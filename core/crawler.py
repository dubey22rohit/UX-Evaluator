import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
from playwright.async_api import async_playwright, Page, Browser
from urllib.parse import urlparse, urljoin

class WebsiteCrawler:
    """
    A class for crawling websites and capturing screenshots using Playwright.
    """
    
    def __init__(self, url: str, max_pages: int = 10, depth: int = 2):
        """
        Initialize the WebsiteCrawler.
        
        Args:
            url: The starting URL to crawl
            max_pages: Maximum number of pages to crawl
            depth: Maximum depth of crawling from the starting URL
        """
        self.start_url = url
        self.max_pages = max_pages
        self.max_depth = depth
        self.visited_urls = set()
        self.pages_data = []
        self.base_domain = urlparse(url).netloc
        
    async def crawl(self) -> Dict[str, Any]:
        """
        Crawl the website starting from the initial URL.
        
        Returns:
            Dict containing crawl results with pages data and metadata
        """
        logger.info(f"Starting crawl of {self.start_url} with max {self.max_pages} pages and depth {self.max_depth}")
        
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="UX-Evaluation-Agent/1.0"
            )
            
            # Start crawling from the initial URL
            await self._crawl_page(context, self.start_url, depth=0)
            
            await context.close()
            await browser.close()
        
        logger.info(f"Crawl completed. Visited {len(self.visited_urls)} pages")
        
        return {
            "pages": self.pages_data,
            "start_url": self.start_url,
            "total_pages": len(self.pages_data),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _crawl_page(self, context: Any, url: str, depth: int) -> None:
        """
        Crawl a single page, capture screenshot, and extract links for further crawling.
        
        Args:
            context: Playwright browser context
            url: URL to crawl
            depth: Current depth of crawling
        """
        # Skip if we've reached the maximum pages or already visited this URL
        if len(self.pages_data) >= self.max_pages or url in self.visited_urls:
            return
        
        # Skip if URL is not from the same domain
        if urlparse(url).netloc != self.base_domain:
            return
        
        # Mark URL as visited
        self.visited_urls.add(url)
        
        # Initialize page variable
        page = None
        
        try:
            # Open a new page
            page = await context.new_page()
            
            # Navigate to the URL with timeout
            logger.info(f"Crawling: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for page to be fully loaded
            await page.wait_for_load_state("networkidle")
            
            # Capture screenshot
            screenshot = await page.screenshot(type="jpeg", quality=80, full_page=True)
            
            # Extract page metadata
            title = await page.title()
            html = await page.content()
            
            # Store page data
            page_data = {
                "url": url,
                "title": title,
                "screenshot": screenshot,
                "html": html,
                "timestamp": datetime.now().isoformat(),
                "depth": depth
            }
            
            self.pages_data.append(page_data)
            
            # If we haven't reached max depth, extract links and continue crawling
            if depth < self.max_depth:
                links = await self._extract_links(page)
                
                # Close the current page before crawling new ones
                await page.close()
                
                # Crawl each link
                for link in links:
                    if len(self.pages_data) >= self.max_pages:
                        break
                    
                    # Add a small delay to avoid overloading the server
                    await asyncio.sleep(1)
                    await self._crawl_page(context, link, depth + 1)
            else:
                await page.close()
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            if page is not None:
                try:
                    await page.close()
                except:
                    pass
    
    async def _extract_links(self, page: Page) -> List[str]:
        """
        Extract links from a page that belong to the same domain.
        
        Args:
            page: Playwright page object
        
        Returns:
            List of URLs to crawl next
        """
        # Get all links on the page
        links = await page.eval_on_selector_all("a[href]", """
            (elements) => elements.map(el => el.href)
        """)
        
        # Filter links to only include those from the same domain
        same_domain_links = []
        for link in links:
            parsed_link = urlparse(link)
            
            # Skip non-HTTP links, fragments, and external domains
            if (parsed_link.scheme not in ["http", "https"] or 
                parsed_link.netloc != self.base_domain or
                "#" in link):
                continue
            
            # Normalize the URL
            normalized_link = urljoin(self.start_url, link)
            
            # Add to list if not already visited
            if normalized_link not in self.visited_urls:
                same_domain_links.append(normalized_link)
        
        return same_domain_links
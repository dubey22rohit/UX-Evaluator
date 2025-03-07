import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

class UXAnalyzer:
    def __init__(self, crawl_results: Dict[str, Any], heuristics: List[str], custom_checks: Optional[List[str]] = None):
        """
        Args:
            crawl_results: Results from the WebsiteCrawler
            heuristics: List of UX heuristics to evaluate against
            custom_checks: Optional list of custom UX checks to perform
        """
        self.crawl_results = crawl_results
        self.heuristics = heuristics or ["all"]
        self.custom_checks = custom_checks or []
        
    async def analyze(self) -> Dict[str, Any]:
        """
        Analyze the website UX based on crawl results and specified heuristics.
        
        Returns:
            Dict containing analysis results with identified issues and recommendations
        """
        logger.info(f"Starting UX analysis with {len(self.crawl_results['pages'])} pages")
        
        # Initialize results structure
        results = {
            "issues": [],
            "recommendations": [],
            "heuristics_evaluated": self.heuristics,
            "custom_checks": self.custom_checks,
            "timestamp": datetime.now().isoformat(),
            "total_issues": 0
        }
        
        # Process each page in parallel
        tasks = []
        for page in self.crawl_results["pages"]:
            tasks.append(self._analyze_page(page))
        
        # Gather all analysis results
        page_results = await asyncio.gather(*tasks)
        
        # Combine results from all pages
        for page_result in page_results:
            results["issues"].extend(page_result["issues"])
            results["recommendations"].extend(page_result["recommendations"])
        
        # Count total issues
        results["total_issues"] = len(results["issues"])
        
        # Add overall site-wide recommendations
        site_recommendations = await self._generate_site_recommendations(results["issues"])
        results["site_recommendations"] = site_recommendations
        
        logger.info(f"BeautifulSoup UX analysis completed. Found {results['total_issues']} issues.")
        return results
    
    async def _analyze_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single page for UX issues.
        
        Args:
            page: Page data from crawler
            
        Returns:
            Dict containing issues and recommendations for the page
        """
        page_url = page["url"]
        page_title = page["title"]
        
        logger.info(f"Analyzing page: {page_url}")
        
        # Initialize page results
        page_results = {
            "issues": [],
            "recommendations": []
        }
        
        # Run different analysis methods in parallel
        tasks = [
            self._analyze_accessibility(page),
            self._analyze_visual_design(page),
            self._analyze_navigation(page),
            self._analyze_content(page),
            self._analyze_performance(page),
        ]
        
        # Gather all analysis results
        analysis_results = await asyncio.gather(*tasks)
        
        # Combine results from all analysis methods
        for result in analysis_results:
            if result:
                page_results["issues"].extend(result.get("issues", []))
                page_results["recommendations"].extend(result.get("recommendations", []))
        
        # Add page metadata to each issue
        for issue in page_results["issues"]:
            issue["page_url"] = page_url
            issue["page_title"] = page_title
        
        return page_results
    
    async def _analyze_accessibility(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze page for accessibility issues.
        """
        issues = []
        recommendations = []
        
        html_content = page["html"]
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Check for images without alt text
        images = soup.find_all("img")
        for img in images:
            if not img.get("alt"):
                issues.append({
                    "type": "accessibility",
                    "heuristic": "Visibility of System Status",
                    "description": "Image missing alt text",
                    "element": str(img)[:100] + "...",
                    "severity": "medium"
                })
                recommendations.append({
                    "type": "accessibility",
                    "description": "Add descriptive alt text to all images",
                    "element_type": "img"
                })
        
        # Check for proper heading structure
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        heading_levels = [int(h.name[1]) for h in headings]
        
        if heading_levels and heading_levels[0] != 1:
            issues.append({
                "type": "accessibility",
                "heuristic": "Consistency and Standards",
                "description": "Page does not start with an H1 heading",
                "severity": "medium"
            })
            recommendations.append({
                "type": "accessibility",
                "description": "Ensure each page has a single H1 heading that describes the page content"
            })
        
        # Check for color contrast using WCAG guidelines
        def calculate_relative_luminance(r, g, b):
            def adjust_color_channel(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            return 0.2126 * adjust_color_channel(r) + 0.7152 * adjust_color_channel(g) + 0.0722 * adjust_color_channel(b)

        def calculate_contrast_ratio(l1, l2):
            lighter = max(l1, l2)
            darker = min(l1, l2)
            return (lighter + 0.05) / (darker + 0.05)

        def extract_color(style_str, property_name):
            if not style_str:
                return None
            match = re.search(f"{property_name}:\s*rgb\((\d+),\s*(\d+),\s*(\d+)\)", style_str)
            if match:
                return tuple(map(int, match.groups()))
            return None

        text_elements = soup.find_all(["p", "span", "a", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "label"])
        for element in text_elements:
            text_color = extract_color(element.get("style", ""), "color")
            bg_color = extract_color(element.get("style", ""), "background-color")
            
            # Default to parent background if not specified
            if not bg_color:
                parent = element.find_parent(attrs={"style": True})
                while parent and not bg_color:
                    bg_color = extract_color(parent.get("style", ""), "background-color")
                    parent = parent.find_parent(attrs={"style": True})
            
            # If we found both colors, check contrast
            if text_color and bg_color:
                text_luminance = calculate_relative_luminance(*text_color)
                bg_luminance = calculate_relative_luminance(*bg_color)
                contrast_ratio = calculate_contrast_ratio(text_luminance, bg_luminance)
                
                # WCAG 2.1 Level AA requires 4.5:1 for normal text and 3:1 for large text
                is_large_text = False  # This could be enhanced to check font size
                required_ratio = 3.0 if is_large_text else 4.5
                
                if contrast_ratio < required_ratio:
                    issues.append({
                        "type": "accessibility",
                        "heuristic": "Visibility of System Status",
                        "description": f"Insufficient color contrast ratio ({contrast_ratio:.2f}:1) - WCAG 2.1 requires {required_ratio}:1",
                        "element": str(element)[:100] + "...",
                        "severity": "high"
                    })
                    recommendations.append({
                        "type": "accessibility",
                        "description": "Adjust text or background color to meet WCAG 2.1 contrast requirements"
                    })
            
        # Check for form labels
        forms = soup.find_all("form")
        for form in forms:
            inputs = form.find_all("input")
            for input_field in inputs:
                if input_field.get("type") not in ["submit", "button", "hidden"] and not input_field.get("id"):
                    issues.append({
                        "type": "accessibility",
                        "heuristic": "Help and Documentation",
                        "description": "Form input missing ID for label association",
                        "element": str(input_field)[:100] + "...",
                        "severity": "medium"
                    })
                    recommendations.append({
                        "type": "accessibility",
                        "description": "Add proper labels and IDs to all form fields",
                        "element_type": "input"
                    })
        
        return {"issues": issues, "recommendations": recommendations}
    
    async def _analyze_visual_design(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze page for visual design issues using screenshot analysis.
        
        Args:
            page: Page data containing screenshot and metadata
            
        Returns:
            Dict containing visual design issues and recommendations
        """
        issues = []
        recommendations = []
        
        try:
            soup = BeautifulSoup(page["html"], "html.parser")
            
            # Check text contrast using color analysis
            text_elements = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "a"])
            for element in text_elements:
                # This would integrate with a color contrast analyzer
                # For now we'll check if text color is specified inline
                if element.get("style") and "color" in element.get("style").lower():
                    issues.append({
                        "type": "visual_design",
                        "heuristic": "Visibility of System Status",
                        "description": "Inline text styling may cause inconsistent color contrast",
                        "element": str(element)[:100] + "...",
                        "severity": "medium"
                    })
                    recommendations.append({
                        "type": "visual_design",
                        "description": "Use consistent text colors defined in stylesheets for better maintainability"
                    })
            
            # Check for consistent spacing
            divs = soup.find_all("div")
            for div in divs:
                if div.get("style") and ("margin" in div.get("style").lower() or "padding" in div.get("style").lower()):
                    issues.append({
                        "type": "visual_design",
                        "heuristic": "Consistency and Standards",
                        "description": "Inline spacing styles may lead to inconsistent layout",
                        "element": str(div)[:100] + "...",
                        "severity": "low"
                    })
                    recommendations.append({
                        "type": "visual_design",
                        "description": "Define spacing using CSS classes for consistent visual rhythm"
                    })
            
            # Check for responsive images
            images = soup.find_all("img")
            for img in images:
                if not img.get("srcset") and not img.get("loading") == "lazy":
                    issues.append({
                        "type": "visual_design",
                        "heuristic": "Flexibility and Efficiency of Use",
                        "description": "Image missing responsive srcset and lazy loading",
                        "element": str(img)[:100] + "...",
                        "severity": "medium"
                    })
                    recommendations.append({
                        "type": "visual_design",
                        "description": "Add srcset and lazy loading to images for better performance and responsiveness"
                    })
            
            # Check for visual hierarchy
            headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            if len(headings) > 0:
                heading_sizes = []
                for heading in headings:
                    if heading.get("style") and "font-size" in heading.get("style").lower():
                        heading_sizes.append(heading)
                
                if len(heading_sizes) > 0:
                    issues.append({
                        "type": "visual_design",
                        "heuristic": "Consistency and Standards",
                        "description": "Inconsistent heading sizes using inline styles",
                        "severity": "medium"
                    })
                    recommendations.append({
                        "type": "visual_design",
                        "description": "Use consistent heading styles defined in stylesheets for clear visual hierarchy"
                    })
                
        except Exception as e:
            logger.error(f"Error in visual design analysis: {str(e)}")
            
        return {"issues": issues, "recommendations": recommendations}
    
    async def _analyze_navigation(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze page for navigation issues.
        """
        issues = []
        recommendations = []
        html_content = page["html"]
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Check for navigation elements
        nav_elements = soup.find_all("nav")
        if not nav_elements:
            issues.append({
                "type": "navigation",
                "heuristic": "User Control and Freedom",
                "description": "No semantic navigation element found",
                "severity": "low"
            })
            recommendations.append({
                "type": "navigation",
                "description": "Use semantic <nav> elements for main navigation"
            })
        
        # Check for breadcrumbs
        breadcrumbs = soup.find_all("ol", class_="breadcrumb")
        if not breadcrumbs:
            # Only flag as an issue for deeper pages, not the homepage
            if "/" in page["url"].replace("://", ""):
                issues.append({
                    "type": "navigation",
                    "heuristic": "Recognition Rather Than Recall",
                    "description": "No breadcrumb navigation found",
                    "severity": "low"
                })
                recommendations.append({
                    "type": "navigation",
                    "description": "Add breadcrumb navigation for better user orientation"
                })

        return {"issues": issues, "recommendations": recommendations}
    
    async def _analyze_content(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze page for content issues.
        """
        issues = []
        recommendations = []
        html_content = page["html"]
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract all text content
        text_content = soup.get_text(" ", strip=True)
        
        # Check for minimum content length
        if len(text_content) < 100:
            issues.append({
                "type": "content",
                "heuristic": "Match Between System and Real World",
                "description": "Page has very little text content",
                "severity": "medium"
            })
            recommendations.append({
                "type": "content",
                "description": "Add more descriptive content to improve user understanding and SEO"
            })
        
        # Check for very long paragraphs
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            p_text = p.get_text(strip=True)
            if len(p_text) > 500:  # Arbitrary threshold for demonstration
                issues.append({
                    "type": "content",
                    "heuristic": "Aesthetic and Minimalist Design",
                    "description": "Very long paragraph may be difficult to read",
                    "element": p_text[:100] + "...",
                    "severity": "low"
                })
                recommendations.append({
                    "type": "content",
                    "description": "Break long paragraphs into smaller, more digestible chunks"
                })
        
        return {"issues": issues, "recommendations": recommendations}
    
    async def _analyze_performance(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze page for performance issues.
        
        Args:
            page: Page data containing HTML, screenshot and metadata
            
        Returns:
            Dict containing performance issues and recommendations
        """
        issues = []
        recommendations = []
        html_content = page["html"]
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Check for unoptimized images
        images = soup.find_all("img")
        for img in images:
            # Check for missing width and height attributes
            if not img.get("width") or not img.get("height"):
                issues.append({
                    "type": "performance",
                    "heuristic": "Flexibility and Efficiency of Use",
                    "description": "Image missing explicit width/height attributes which can cause layout shifts",
                    "element": str(img)[:100] + "...",
                    "severity": "medium"
                })
                recommendations.append({
                    "type": "performance",
                    "description": "Add width and height attributes to all images to prevent layout shifts during page load"
                })
            
            # Check for very large images
            if img.get("src") and (not img.get("loading") == "lazy"):
                issues.append({
                    "type": "performance",
                    "heuristic": "Flexibility and Efficiency of Use",
                    "description": "Image without lazy loading may delay page rendering",
                    "element": str(img)[:100] + "...",
                    "severity": "medium"
                })
                recommendations.append({
                    "type": "performance",
                    "description": "Add loading='lazy' to images below the fold"
                })
        
        # Check for excessive DOM elements
        all_elements = soup.find_all()
        if len(all_elements) > 1000:  # Arbitrary threshold for demonstration
            issues.append({
                "type": "performance",
                "heuristic": "Aesthetic and Minimalist Design",
                "description": f"Page has {len(all_elements)} DOM elements which may impact performance",
                "severity": "medium"
            })
            recommendations.append({
                "type": "performance",
                "description": "Reduce DOM complexity by simplifying page structure and removing unnecessary elements"
            })
        
        # Check for render-blocking resources
        scripts = soup.find_all("script")
        for script in scripts:
            if not script.get("async") and not script.get("defer") and not script.get("type") == "module":
                issues.append({
                    "type": "performance",
                    "heuristic": "Flexibility and Efficiency of Use",
                    "description": "Render-blocking script found",
                    "element": str(script)[:100] + "...",
                    "severity": "medium"
                })
                recommendations.append({
                    "type": "performance",
                    "description": "Add async or defer attributes to non-critical scripts"
                })
        
        # Check for CSS in head
        css_links = soup.find_all("link", {"rel": "stylesheet"})
        head = soup.find("head")
        if head:
            head_css = head.find_all("link", {"rel": "stylesheet"})
            if len(css_links) != len(head_css):
                issues.append({
                    "type": "performance",
                    "heuristic": "Flexibility and Efficiency of Use",
                    "description": "CSS resources found outside of head element",
                    "severity": "low"
                })
                recommendations.append({
                    "type": "performance",
                    "description": "Place all CSS resources in the head element to prevent render blocking"
                })
        
        # Check for missing performance optimizations
        if not soup.find("meta", {"name": "viewport"}):
            issues.append({
                "type": "performance",
                "heuristic": "Flexibility and Efficiency of Use",
                "description": "Missing viewport meta tag for responsive design",
                "severity": "medium"
            })
            recommendations.append({
                "type": "performance",
                "description": "Add viewport meta tag for better mobile performance"
            })
        
        return {"issues": issues, "recommendations": recommendations}
    
    async def _generate_site_recommendations(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate site-wide recommendations based on identified issues.
        
        Args:
            issues: List of all issues identified across all pages
            
        Returns:
            List of site-wide recommendations
        """
        # Initialize recommendations list
        site_recommendations = []
        
        # Count issues by type and heuristic
        issue_types = {}
        heuristic_counts = {}
        
        for issue in issues:
            # Count by type
            issue_type = issue.get("type")
            if issue_type:
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += 1
            
            # Count by heuristic
            heuristic = issue.get("heuristic")
            if heuristic:
                if heuristic not in heuristic_counts:
                    heuristic_counts[heuristic] = 0
                heuristic_counts[heuristic] += 1
        
        # Generate recommendations based on most common issues
        if issue_types.get("accessibility", 0) > 2:
            site_recommendations.append({
                "type": "accessibility",
                "description": "Conduct a comprehensive accessibility audit and implement WCAG guidelines",
                "priority": "high"
            })
        
        if issue_types.get("navigation", 0) > 2:
            site_recommendations.append({
                "type": "navigation",
                "description": "Improve site-wide navigation structure and consistency",
                "priority": "medium"
            })
        
        if issue_types.get("content", 0) > 2:
            site_recommendations.append({
                "type": "content",
                "description": "Develop content guidelines to ensure consistency and readability across all pages",
                "priority": "medium"
            })
        
        # Add recommendations based on heuristic violations
        for heuristic, count in heuristic_counts.items():
            if count > 3:
                site_recommendations.append({
                    "type": "heuristic",
                    "heuristic": heuristic,
                    "description": f"Address multiple violations of '{heuristic}' heuristic across the site",
                    "priority": "high"
                })
        
        return site_recommendations
        
        
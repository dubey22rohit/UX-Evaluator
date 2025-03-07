import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io
import json
from helpers.ai_response_to_json import convert_ai_response_to_json

# Load environment variables
load_dotenv()

class GeminiUXAnalyzer:
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
        self.gemini_client = None
        self.response_format = {
            "analysis_results": [
                {
                    "top_left_coordinates": {"x": 0, "y": 0},
                    "top_right_coordinates": {"x": 0, "y": 0},
                    "bottom_right_coordinates": {"x": 0, "y": 0},
                    "bottom_left_coordinates": {"x": 0, "y": 0},
                    "image_dimensions": {"width": 0, "height": 0},
                    "point_of_focus": {"top": "0%", "right": "0%", "bottom": "0%", "left": "0%"},
                    "heuristic": "string",
                    "description": "string",
                    "severity": "low|medium|high",
                    "recommendation": "string",
                }
            ]
        }
        
        # Initialize AI clients
        self._init_ai_clients()
    
    def _init_ai_clients(self):
        """Initialize AI clients for Gemini"""
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
        else:
            logger.warning("Google API key not found. Gemini analysis will be unavailable.")
    

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
        
        logger.info(f"AI UX analysis completed. Found {results['total_issues']} issues.")

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
            "recommendations": [],
            "custom_checks": self.custom_checks,
            "timestamp": datetime.now().isoformat(),
            "total_issues": 0,
            "annotated_image": None
        }
        
        # Run different analysis methods in parallel
        if self.gemini_client == None:
            return page_results

        tasks = [
            self._analyze_accessibility_gemini(page),
            self._analyze_visual_design_gemini(page),
            self._analyze_navigation_gemini(page),
            self._analyze_content_gemini(page),
            self._analyze_performance_gemini(page),
            self._analyze_general_gemini(page),
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

    async def _analyze_accessibility_gemini(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze page for accessibility issues."""
        try:
            prompt = f"""Analyze this screenshot for accessibility issues, focusing on:
            - Color contrast and text readability (WCAG 2.1 compliance)
            - Text alternatives for images
            - Keyboard navigation
            - Form controls and labels
            
            Respond with a JSON object that follows this exact schema:
            {json.dumps(self.response_format, indent=2)}
            
            For each issue, provide 
            1. the exact top left, top right, bottom left and bottom right coordinates
            completely covering the issue mentioned
            2. passed image dimentions
            3. The top, left, bottom and right distances (in percentage) to the center of the issue mentioned, relative to the width and height of the image (important).
            4. which heuristic it violates
            5. a description
            6. severity level
            7. recommendation to fix it.
            """
            
            # Convert screenshot bytes to PIL Image for Gemini
            image = Image.open(io.BytesIO(page["screenshot"]))

            # Convert PIL Image back to bytes for API
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Call Gemini API with structured format instruction
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_byte_arr}}
                    ]}
                ],
                generation_config={"response_mime_type": "application/json"}
            )

            #analyze_accessibility_gemini Gemini response text: {response.text}")

            result = {
                "issues": [],
                "recommendations": [],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }

             # Ensure we have a valid response
            if not response or not hasattr(response, 'text'):
                logger.warning("No valid response from Gemini API")
                return result
      
            try:
                ai_result_json = convert_ai_response_to_json(response)
                result["issues"].append(ai_result_json)
                return result
            except :
                logger.warning("_analyze_accessibility_gemini Failed to parse JSON response from Gemini")
                return {
                    "issues": [],
                    "recommendations": [],
                    "custom_checks": self.custom_checks,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": 0,
                    "annotated_image": None
                }

        except Exception as e:
            logger.warning(f"Error in Gemini accessibility analysis: {str(e)}")
            return {
                    "issues": [],
                    "recommendations": [],
                    "custom_checks": self.custom_checks,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": 0,
                    "annotated_image": None
                }

    async def _analyze_visual_design_gemini(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze page for visual design issues."""
        try:
            screenshot = page["screenshot"]

            prompt = f"""Analyze this screenshot for visual design issues. Focus on:
            - Visual hierarchy and information architecture
            - Color scheme and contrast
            - Layout balance and whitespace usage
            - Typography and readability
            - Consistency in design elements
            
            Respond with a JSON object that follows this exact schema:
            {json.dumps(self.response_format, indent=2)}

            For each issue, provide 
            1. the exact top left, top right, bottom left and bottom right coordinates
            completely covering the issue mentioned
            2. passed image dimentions
            3. the exact center location of the issue mentioned in the image. The top, left, bottom and right are precise percentages relative to the passed image's width and height.
            4. which heuristic it violates
            5. a description
            6. severity level
            7. recommendation to fix it."""
            
            # Convert screenshot to format compatible with Gemini
            image = Image.open(io.BytesIO(screenshot))

            # Convert PIL Image back to bytes for API
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Get Gemini's analysis
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_byte_arr}}
                    ]}
                ],
                generation_config={"response_mime_type": "application/json"}
            )

            #analyze_visual_design_gemini Gemini response text: {response.text}")
            
            # Initialize standard response format
            result = {
                "issues": [],
                "recommendations": [],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }
            
             # Ensure we have a valid response
            if not response or not hasattr(response, 'text'):
                logger.warning("No valid response from Gemini API")
                return result
      
            try:
                ai_result_json = convert_ai_response_to_json(response)
                result["issues"].append(ai_result_json)
                return result
            except :
                logger.warning("_analyze_visual_design_gemini  Failed to parse JSON response from Gemini")
                return {
                    "issues": [],
                    "recommendations": [],
                    "custom_checks": self.custom_checks,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": 0,
                    "annotated_image": None
                }
                        
        except Exception as e:
            logger.error(f"Error in Gemini visual analysis: {str(e)}")
            return {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["Aesthetic and Minimalist Design"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }

    async def _analyze_navigation_gemini(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze page for navigation issues.
        """
        try:
            screenshot = page["screenshot"]
            url = page["url"]
            title = page["title"]
            
            prompt = f"""
            You are a UX expert analyzing webpage navigation. Evaluate the screenshot for navigation-related issues based on these aspects:
            
            1. Menu structure and hierarchy
            2. Navigation patterns and consistency
            3. Wayfinding elements
            4. Mobile navigation usability
            5. Search functionality
            
            Respond with a JSON object that follows this exact schema:
            {json.dumps(self.response_format, indent=2)}

            For each issue, provide 
            1. the exact top left, top right, bottom left and bottom right coordinates
            completely covering the issue mentioned
            2. passed image dimentions
            3. the exact center location of the issue mentioned in the image. The top, left, bottom and right are precise percentages relative to the passed image's width and height.
            4. which heuristic it violates
            5. a description
            6. severity level
            7. recommendation to fix it.
            
            URL: {url}
            Page Title: {title}
            """
            
            # Convert screenshot bytes to PIL Image for Gemini
            image = Image.open(io.BytesIO(screenshot))
            
            # Convert PIL Image back to bytes for API
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Get Gemini's analysis
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_byte_arr}}
                    ]}
                ],
                generation_config={"response_mime_type": "application/json"}
            )

            #analyze_navigation_gemini Gemini response text: {response.text}")
            
            # Initialize standard response format
            result = {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["User Control and Freedom", "Consistency and Standards"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }
            
            if not response or not hasattr(response, 'text'):
                logger.warning("No valid response from Gemini API")
                return result
      
            try:
                ai_result_json = convert_ai_response_to_json(response)
                result["issues"].append(ai_result_json)
                return result
            except :
                logger.warning("_analyze_navigation_gemini Failed to parse JSON response from Gemini")
                return {
                    "issues": [],
                    "recommendations": [],
                    "custom_checks": self.custom_checks,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": 0,
                    "annotated_image": None
                }
                    
        except Exception as e:
            logger.error(f"Error in Gemini navigation analysis: {str(e)}")
            return {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["Match between system and the real world", "Aesthetic and Minimalist Design"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }
        
    async def _analyze_content_gemini(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze page for content issues.
        """
        try:
            screenshot = page["screenshot"]
            url = page["url"]
            title = page["title"]
            html_sample = page["html"][:5000] if len(page["html"]) > 5000 else page["html"]
            
            prompt = f"""
            You are a UX content expert analyzing a webpage. Evaluate the screenshot and HTML sample for content-related issues based on these aspects:
            
            1. Content clarity and readability
            2. Information hierarchy
            3. Tone and voice consistency
            4. Call-to-action effectiveness
            5. Content organization
            
            Respond with a JSON object that follows this exact schema:
            {json.dumps(self.response_format, indent=2)}

            For each issue, provide 
            1. the exact top left, top right, bottom left and bottom right coordinates
            completely covering the issue mentioned
            2. passed image dimentions
            3. the exact center location of the issue mentioned in the image. The top, left, bottom and right are precise percentages relative to the passed image's width and height.
            4. which heuristic it violates
            5. a description
            6. severity level
            7. recommendation to fix it.
            
            URL: {url}
            Page Title: {title}
            
            HTML Sample (first 5KB):
            {html_sample}
            """
            
            # Convert screenshot bytes to PIL Image for Gemini
            image = Image.open(io.BytesIO(screenshot))
            
            # Convert PIL Image back to bytes for API
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Get Gemini's analysis
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_byte_arr}}
                    ]}
                ],
                generation_config={"response_mime_type": "application/json"}
            )

            #analyze_content_gemini Gemini response text: {response.text}")
            
            # Initialize standard response format
            result = {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["Match between system and the real world", "Aesthetic and Minimalist Design"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }
            
            # Ensure we have a valid response
            if not response or not hasattr(response, 'text'):
                logger.warning("No valid response from Gemini API")
                return result
      
            try:
                ai_result_json = convert_ai_response_to_json(response)
                result["issues"].append(ai_result_json)
                return result
            except :
                logger.warning("_analyze_content_gemini Failed to parse JSON response from Gemini")
                return {
                    "issues": [],
                    "recommendations": [],
                    "custom_checks": self.custom_checks,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": 0,
                    "annotated_image": None
                }
                    
        except Exception as e:
            logger.error(f"Error in Gemini content analysis: {str(e)}")
            return {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["Match between system and the real world", "Aesthetic and Minimalist Design"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }

    async def _analyze_performance_gemini(self, page: Dict[str, Any]) -> Dict[str, Any]:
        try:
            screenshot = page["screenshot"]
            url = page["url"]
            title = page["title"]
            html_sample = page["html"][:5000] if len(page["html"]) > 5000 else page["html"]
            
            prompt = f"""
            You are a web performance expert analyzing a webpage. I want you to identify performance issues based on the screenshot and HTML sample provided.
            
            Focus on these performance aspects:
            1. Perceived load speed
            2. Visual complexity
            3. Potential render-blocking elements
            4. Layout stability concerns
            5. Resource efficiency
            
            Respond with a JSON object that follows this exact schema:
            {json.dumps(self.response_format, indent=2)}

            For each issue, provide 
            1. the exact top left, top right, bottom left and bottom right coordinates
            completely covering the issue mentioned
            2. passed image dimentions
            3. the exact center location of the issue mentioned in the image. The top, left, bottom and right are precise percentages relative to the passed image's width and height.
            4. which heuristic it violates
            5. a description
            6. severity level
            7. recommendation to fix it.
            
            URL: {url}
            Page Title: {title}
            
            HTML Sample (first 5KB):
            {html_sample}
            """
            
            # Convert screenshot bytes to PIL Image for Gemini
            image = Image.open(io.BytesIO(screenshot))
            
            # Convert PIL Image back to bytes for API
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Get Gemini's analysis
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_byte_arr}}
                    ]}
                ],
                generation_config={"response_mime_type": "application/json"}
            )

            #analyze_performance_gemini Gemini response text: {response.text}")
            
            # Initialize standard response format
            result = {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["Flexibility and Efficiency of Use"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }
            
            # Ensure we have a valid response
            if not response or not hasattr(response, 'text'):
                logger.warning("No valid response from Gemini API")
                return result
      
            try:
                ai_result_json = convert_ai_response_to_json(response)
                result["issues"].append(ai_result_json)
                return result
            except :
                logger.warning("_analyze_performance_gemini Failed to parse JSON response from Gemini")
                return {
                    "issues": [],
                    "recommendations": [],
                    "custom_checks": self.custom_checks,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": 0,
                    "annotated_image": None
                }
            
        except Exception as e:
            logger.error(f"Error in Gemini performance analysis: {str(e)}")
            return {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["Flexibility and Efficiency of Use"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }

    async def _analyze_general_gemini(self, page: Dict[str, Any]) -> Dict[str, Any]:
        try:
            screenshot = page["screenshot"]
            url = page["url"]
            title = page["title"]
            
            prompt = f"""
            You are a UX expert analyzing a webpage screenshot. I want you to identify visual UX issues based on Nielsen's 10 Heuristics:
            
            1. Visibility of system status
            2. Match between system and the real world
            3. User control and freedom
            4. Consistency and standards
            5. Error prevention
            6. Recognition rather than recall
            7. Flexibility and efficiency of use
            8. Aesthetic and minimalist design
            9. Help users recognize, diagnose, and recover from errors
            10. Help and documentation

            Focus on visual aspects like layout, color contrast, visual hierarchy, spacing, alignment, and overall design.
            
            Respond with a JSON object that follows this exact schema:
            {json.dumps(self.response_format, indent=2)}

            For each issue, provide 
            1. the exact top left, top right, bottom left and bottom right coordinates
            completely covering the issue mentioned
            2. passed image dimentions
            3. the exact center location of the issue mentioned in the image. The top, left, bottom and right are precise percentages relative to the passed image's width and height.
            4. which heuristic it violates
            5. a description
            6. severity level
            7. recommendation to fix it.
            
            URL: {url}
            Page Title: {title}
            """
            
            # Convert screenshot bytes to PIL Image for Gemini
            image = Image.open(io.BytesIO(screenshot))
            
            # Convert PIL Image back to bytes for API
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Get Gemini's analysis
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_byte_arr}}
                    ]}
                ],
                generation_config={"response_mime_type": "application/json"}
            )

            #analyze_general_gemini Gemini response text: {response.text}")
            
            # Initialize standard response format
            result = {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["General UX"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }
            
            # Ensure we have a valid response
            if not response or not hasattr(response, 'text'):
                logger.warning("No valid response from Gemini API")
                return result
      
            try:
                ai_result_json = convert_ai_response_to_json(response)
                result["issues"].append(ai_result_json)
                return result
            except :
                logger.warning("_analyze_general_gemini Failed to parse JSON response from Gemini")
                return {
                    "issues": [],
                    "recommendations": [],
                    "custom_checks": self.custom_checks,
                    "timestamp": datetime.now().isoformat(),
                    "total_issues": 0,
                    "annotated_image": None
                }
            
        except Exception as e:
            logger.error(f"Error analyzing with Gemini: {str(e)}")
            return {
                "issues": [],
                "recommendations": [],
                "heuristics_evaluated": ["General UX"],
                "custom_checks": self.custom_checks,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "annotated_image": None
            }

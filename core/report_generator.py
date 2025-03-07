import asyncio
import uuid
from typing import Dict, List, Any
from loguru import logger
import os
import google.generativeai as genai
import json
import datetime

class ReportGenerator:
    """
    A class for generating comprehensive UX evaluation reports.
    """
    
    def __init__(self):
        """
        Initialize the ReportGenerator.
        Args:
            evaluation: Evaluation metadata from database
            analysis_results: Results from the UXAnalyzer
            screenshots: List of screenshots captured during crawling
        """
        self.gemini_client = None

        self.report_template = """
        # UX Evaluation Report

        ## Executive Summary
        Website: url

        Total Pages Analyzed: total_pages

        Total Issues Found: total_issues
        
        ## Severity Breakdown

        severity_breakdown
        
        ## Detailed Findings

        detailed_findings
        
        ## Recommendations

        recommendations        
        """
        
        self._init_ai_clients()

    def _init_ai_clients(self):
        """Initialize AI clients for Gemini"""
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
        else:
            logger.warning("Google API key not found. Gemini analysis will be unavailable.")
    
    async def generate(self, analysis_results: Any):
        """
        Generate a comprehensive UX evaluation report.
        
        Returns:
            Dict containing the generated report data
        """
        try:
            # Generate report ID
            report_id = str(uuid.uuid4())

            prompt = f"""
            Generate a report. I will pass an evaluation object

            I have these evaluations. Do the following -  
            1) Generate a UX report and score based on evaluations 
            2) Give me an ordered list of issues and recommendations to solve them from easiest to do to hardest to do
            limit the response to only 2 pages, include all the information above in a concise manner.          

            return the report in markdown format.

            Generate a report with a that follows this exact schema:
            {self.report_template}
            """

            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"text": prompt},
                    {"text": json.dumps(analysis_results)}
                ]
            )

            reports_dir = "/Users/rohitdubey/Desktop/reports"
            os.makedirs(reports_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            pdf_filename = f"report_{report_id}_{timestamp}.pdf"
            output_path = os.path.join(reports_dir, pdf_filename)

            await self.export_pdf(response.text, output_path)

            report = {
                "report_id": report_id,
                "content": response.text,
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    async def export_pdf(self, report_content: str, output_path: str) -> None:
        """
        Export the report as a PDF file.
        
        Args:
            report_content: The markdown content of the report
            output_path: Path where the PDF should be saved
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch
            import markdown
            
            # Convert markdown to HTML
            html = markdown.markdown(report_content)

            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Process HTML content
            for line in html.split('\n'):
                if line.strip():
                    p = Paragraph(line, styles['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 0.2 * inch))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {str(e)}")
            raise
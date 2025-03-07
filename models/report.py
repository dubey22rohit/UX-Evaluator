from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime
from .evaluation import UXIssue

class RecommendationItem(BaseModel):
    """
    Model for a UX recommendation
    """
    type: str = Field(..., description="Type of recommendation (accessibility, navigation, content, etc.)")
    description: str = Field(..., description="Description of the recommendation")
    page_url: Optional[str] = Field(None, description="URL of the page this recommendation applies to")
    element_type: Optional[str] = Field(None, description="Type of HTML element this recommendation applies to")
    priority: str = Field("medium", description="Priority of the recommendation (low, medium, high)")

class ScreenshotReference(BaseModel):
    """
    Model for a screenshot reference in a report
    """
    url: str = Field(..., description="URL of the page where the screenshot was taken")
    timestamp: str = Field(..., description="Timestamp when the screenshot was taken")
    screenshot_id: Optional[str] = Field(None, description="ID of the screenshot in the database")

class ReportSummary(BaseModel):
    """
    Model for the summary section of a UX evaluation report
    """
    total_pages: int = Field(..., description="Total number of pages analyzed")
    total_issues: int = Field(..., description="Total number of UX issues found")
    severity_counts: Dict[str, int] = Field(..., description="Count of issues by severity")
    heuristics_evaluated: List[str] = Field(..., description="List of UX heuristics evaluated")
    custom_checks: Optional[List[str]] = Field(None, description="List of custom UX checks performed")

class Report(BaseModel):
    """
    Model for a complete UX evaluation report
    """
    report_id: str = Field(..., description="Unique ID for the report")
    evaluation_id: str = Field(..., description="ID of the evaluation this report is for")
    url: HttpUrl = Field(..., description="URL of the evaluated website")
    timestamp: str = Field(..., description="Timestamp when the report was generated")
    summary: ReportSummary = Field(..., description="Summary of the evaluation results")
    issues: Dict[str, Any] = Field(..., description="Issues organized by page and heuristic")
    recommendations: Dict[str, Any] = Field(..., description="Recommendations for improving UX")
    screenshots: List[ScreenshotReference] = Field(..., description="References to screenshots taken during evaluation")

class ReportFormat(BaseModel):
    """
    Model for specifying report format options
    """
    include_screenshots: bool = Field(True, description="Whether to include screenshots in the report")
    format: str = Field("html", description="Format of the report (html, pdf, json)")
    highlight_issues: bool = Field(True, description="Whether to highlight issues on screenshots")
    include_recommendations: bool = Field(True, description="Whether to include recommendations in the report")
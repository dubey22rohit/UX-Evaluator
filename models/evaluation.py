from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any


class AIResponse(BaseModel):
    """
    Response model for AI analysis
    """
     
    coordinates: Dict[str, int] = Field(..., description="Coordinates of the issue")
    heuristic: str = Field(..., description="Heuristic that was violated")
    description: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity of the issue")
    recommendation: str = Field(..., description="Recommendation for fixing the issue")
    timestamp: str = Field(..., description="Timestamp of the issue")


class EvaluationRequest(BaseModel):
    """
    Request model for website UX evaluation
    """
    url: HttpUrl = Field(..., description="URL of the website to evaluate")
    max_pages: int = Field(10, description="Maximum number of pages to crawl and analyze")
    depth: int = Field(2, description="Maximum depth of crawling from the starting URL")
    heuristics: List[str] = Field(default=["all"], description="List of UX heuristics to evaluate against")
    custom_checks: Optional[List[str]] = Field(default=None, description="Optional list of custom UX checks to perform")

class EvaluationResponse(BaseModel):
    """
    Response model for website UX evaluation
    """
    evaluation_id: str = Field(..., description="Unique ID for the evaluation")
    status: str = Field(..., description="Status of the evaluation (pending, in_progress, completed, failed)")
    message: str = Field(..., description="Status message")
    pages_analyzed: int = Field(..., description="Number of pages analyzed")
    issues_found: int = Field(..., description="Number of UX issues found")
    analysis_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Detailed analysis results")

class UXIssue(BaseModel):
    """
    Model for a UX issue
    """
    type: str = Field(..., description="Type of issue (accessibility, navigation, content, etc.)")
    heuristic: str = Field(..., description="UX heuristic that was violated")
    description: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity of the issue (low, medium, high)")
    page_url: str = Field(..., description="URL of the page where the issue was found")
    page_title: str = Field(..., description="Title of the page where the issue was found")
    element: Optional[str] = Field(None, description="HTML element related to the issue")

class EvaluationResult(BaseModel):
    """
    Model for evaluation results
    """
    evaluation_id: str = Field(..., description="Unique ID for the evaluation")
    url: Optional[HttpUrl] = Field(..., description="URL of the evaluated website")
    analysis_results: List[Any] = Field(default=[], description="List of UX issues found")
    pages_analyzed: int = Field(..., description="Number of pages analyzed")
    heuristics: List[str] = Field(default=[], description="List of UX heuristics evaluated")
    custom_checks: Optional[List[str]] = Field(default=None, description="Optional list of custom UX checks performed")
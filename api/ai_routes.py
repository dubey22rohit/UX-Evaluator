from fastapi import APIRouter, HTTPException, Depends, Request, Body
from fastapi.responses import Response
from loguru import logger
from pydantic import HttpUrl
from core import report_generator
from core.crawler import WebsiteCrawler
from core.gemini_analyzer import GeminiUXAnalyzer
from core.report_generator import ReportGenerator
from core.chat_analyzer import ChatAnalyzer
from models.evaluation import EvaluationRequest, EvaluationResponse, EvaluationResult
import uuid

ai_router = APIRouter()

# Get MongoDB database instance
async def get_db(request: Request):
    return request.app.state.mongodb

@ai_router.post("/evaluate-ai", response_model=EvaluationResponse)
async def evaluate_website_ai(request: EvaluationRequest, db = Depends(get_db)):
    """
    Evaluate a website's UX based on provided URL and evaluation criteria
    """
    try:
        # Generate unique evaluation ID
        evaluation_id = str(uuid.uuid4())
        
        # Log the evaluation request
        logger.info(f"Starting AI evaluation for {request.url} with ID: {evaluation_id}")
        
        # Initialize the website crawler
        crawler = WebsiteCrawler(
            url=str(request.url),
            max_pages=request.max_pages,
            depth=request.depth
        )
        
        # Crawl the website and capture screenshots
        crawl_results = await crawler.crawl()

        # Initialize the AI Analyzer
        ai_analyzer = GeminiUXAnalyzer(
            crawl_results=crawl_results,
            heuristics=request.heuristics,
            custom_checks=request.custom_checks
        )

        # Analyze the website UX using AI
        ai_analysis_results = await ai_analyzer.analyze()
        
        # Store evaluation data in database
        db.ai_evaluations.insert_one({
            "_id": evaluation_id,
            "url": str(request.url),  # Convert HttpUrl to string
            "analysis_results": ai_analysis_results["issues"],
            "pages_analyzed": len(crawl_results["pages"]),
            "heuristics": request.heuristics,
            "custom_checks": request.custom_checks
        })
        
        # Store screenshots in database
        for page in crawl_results["pages"]:
            db.ai_screenshots.insert_one({
                "evaluation_id": evaluation_id,
                "url": page["url"],
                "screenshot": page["screenshot"],
                "timestamp": page["timestamp"]
            })
        
        # Return evaluation response
        return EvaluationResponse(
            evaluation_id=evaluation_id,
            status="completed",
            message="Evaluation completed successfully",
            pages_analyzed=len(crawl_results["pages"]),
            issues_found=len(ai_analysis_results["issues"]),
            analysis_results=ai_analysis_results["issues"]
        )
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_router.get("/evaluations-ai/{evaluation_id}", response_model=EvaluationResult)
async def get_evaluation_ai(evaluation_id: str, db = Depends(get_db)):
    """
    Get the results of a specific evaluation by ID
    """
    try:
        # Retrieve evaluation from database
        analysis_results = db.ai_evaluations.find_one({"_id": evaluation_id})
        
        if not analysis_results:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        # Return evaluation result
        return EvaluationResult(
            evaluation_id=evaluation_id,
            url=analysis_results["url"],
            pages_analyzed=analysis_results["pages_analyzed"],
            analysis_results=analysis_results["analysis_results"]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/generate-report-ai/{evaluation_id}")
async def generate_report_ai(evaluation_id: str, db = Depends(get_db)):
    """
    Get the results of a specific evaluation by ID
    """
    try:
        # Retrieve evaluation from database
        analysis_results = db.ai_evaluations.find_one({"_id": evaluation_id})
        
        if not analysis_results:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        report_gen = ReportGenerator()

        await report_gen.generate(analysis_results=analysis_results)

        # Return evaluation result
        return {
            "message": "Report generated"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/reports-ai/{evaluation_id}")
async def get_report_ai(evaluation_id: str, db = Depends(get_db)):
    """
    Get the generated report for a specific evaluation
    """
    try:
        # Retrieve report from database
        report = db.ai_reports.find_one({"evaluation_id": evaluation_id})
        
        if not report or "report" not in report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report["report"]
        
    except Exception as e:
        logger.error(f"Error retrieving report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@ai_router.get("/get-screenshot-ai/{evaluation_id}")
async def get_screenshot(evaluation_id: str, db = Depends(get_db)):
    """
    Get all screenshots associated with an evaluation ID
    """
    try:
        # Retrieve all screenshots for this evaluation
        screenshot = db.ai_screenshots.find_one({"evaluation_id": evaluation_id})

        if not screenshot:
            raise HTTPException(status_code=404, detail="No screenshot found for this evaluation")

        # Return array of screenshots with their URLs
        return Response(
            content=screenshot["screenshot"],
            media_type="image/png"
        )
    except Exception as e:
        logger.error(f"Error retrieving screenshots: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.post("/chat-analysis/{evaluation_id}")
async def chat_analysis(evaluation_id: str, question: str = Body(...), db = Depends(get_db)):
    """
    Process user questions about UX evaluation results using ChatAnalyzer
    """
    try:
        # Retrieve evaluation results from database
        analysis_results = db.ai_evaluations.find_one({"_id": evaluation_id})
        
        if not analysis_results:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        # Initialize chat analyzer with evaluation results
        chat_analyzer = ChatAnalyzer(analysis_results=analysis_results)

        # Generate response to user question
        response = await chat_analyzer.process_question(question)

        return {
            "evaluation_id": evaluation_id,
            "question": question,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Error in chat analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


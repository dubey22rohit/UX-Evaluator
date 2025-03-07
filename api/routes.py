from fastapi import APIRouter, HTTPException, Depends, Request
from loguru import logger
from core.crawler import WebsiteCrawler
from core.analyzer import UXAnalyzer
from core.report_generator import ReportGenerator
from models.evaluation import EvaluationRequest, EvaluationResponse, EvaluationResult
import uuid

router = APIRouter()

# Get MongoDB database instance
async def get_db(request: Request):
    return request.app.state.mongodb

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_website(request: EvaluationRequest, db = Depends(get_db)):
    """
    Evaluate a website's UX based on provided URL and evaluation criteria
    """
    try:
        # Generate unique evaluation ID
        evaluation_id = str(uuid.uuid4())
        
        # Log the evaluation request
        logger.info(f"Starting evaluation for {request.url} with ID: {evaluation_id}")
        
        # Initialize the website crawler
        crawler = WebsiteCrawler(
            url=str(request.url),
            max_pages=request.max_pages,
            depth=request.depth
        )
        
        # Crawl the website and capture screenshots
        crawl_results = await crawler.crawl()
        
        # Initialize the UX analyzer with the crawl results
        analyzer = UXAnalyzer(
            crawl_results=crawl_results,
            heuristics=request.heuristics,
            custom_checks=request.custom_checks
        )
        
        # Analyze the website UX
        analysis_results = await analyzer.analyze()

        # Store evaluation data in database
        db.evaluations.insert_one({
            "_id": evaluation_id,
            "url": str(request.url),  # Convert HttpUrl to string
            "timestamp": analysis_results["timestamp"],
            "status": "completed",
            "pages_analyzed": len(crawl_results["pages"]),
            "heuristics": request.heuristics,
            "custom_checks": request.custom_checks
        })
        
        # Store analysis results in database
        db.reports.insert_one({
            "evaluation_id": evaluation_id,
            "timestamp": analysis_results["timestamp"],
            "issues": analysis_results["issues"],
            "recommendations": analysis_results["recommendations"],
            "total_issues": analysis_results["total_issues"]
        })
        
        # Store screenshots in database
        for page in crawl_results["pages"]:
            db.screenshots.insert_one({
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
            issues_found=analysis_results["total_issues"]
        )
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResult)
async def get_evaluation(evaluation_id: str, db = Depends(get_db)):
    """
    Get the results of a specific evaluation by ID
    """
    try:
        # Retrieve evaluation from database
        evaluation = db.evaluations.find_one({"_id": evaluation_id})
        
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        # Retrieve analysis results
        analysis_results = db.reports.find_one({"evaluation_id": evaluation_id})
        
        if not analysis_results:
            return EvaluationResult(
                evaluation_id=evaluation_id,
                url=evaluation["url"],
                pages_analyzed=evaluation["pages_analyzed"],
                analysis_results=[]  # No issues found yet
            )
        
        # Return evaluation result
        return EvaluationResult(
            evaluation_id=evaluation_id,
            url=evaluation["url"],
            pages_analyzed=evaluation["pages_analyzed"],
            analysis_results=analysis_results["issues"]
        )
        
    except Exception as e:
        logger.error(f"Error retrieving evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-report/{evaluation_id}")
async def generate_report(evaluation_id: str, db = Depends(get_db)):
    """
    Generate a comprehensive report for a completed evaluation
    """
    try:
        # Retrieve evaluation from database
        evaluation = db.evaluations.find_one({"_id": evaluation_id})
        
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        if evaluation["status"] != "completed":
            raise HTTPException(status_code=400, detail="Evaluation not yet completed")
        
        # Retrieve analysis results
        analysis_results = db.reports.find_one({"evaluation_id": evaluation_id})
        
        if not analysis_results:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        # Retrieve screenshots
        screenshots = list(db.screenshots.find({"evaluation_id": evaluation_id}))
        
        # Initialize report generator
        report_generator = ReportGenerator(
            evaluation=evaluation,
            analysis_results=analysis_results,
            screenshots=screenshots
        )
        
        # Generate the report
        report = await report_generator.generate()
        
        # Store report in database
        db.reports.update_one(
            {"evaluation_id": evaluation_id},
            {"$set": {"report": report}}
        )
        
        return {"message": "Report generated successfully", "report_id": report["report_id"]}
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{evaluation_id}")
async def get_report(evaluation_id: str, db = Depends(get_db)):
    """
    Get the generated report for a specific evaluation
    """
    try:
        # Retrieve report from database
        report = db.reports.find_one({"evaluation_id": evaluation_id})
        
        if not report or "report" not in report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report["report"]
        
    except Exception as e:
        logger.error(f"Error retrieving report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/heuristics")
async def get_heuristics(db = Depends(get_db)):
    """
    Get the list of available UX heuristics for evaluation
    """
    try:
        # Retrieve heuristics from database and convert to serializable format
        heuristics = list(db.heuristics.find())
        serializable_heuristics = []
        
        for heuristic in heuristics:
            # Convert ObjectId to string and create a new dict without _id
            heuristic_dict = dict(heuristic)
            if '_id' in heuristic_dict:
                heuristic_dict['id'] = str(heuristic_dict.pop('_id'))
            serializable_heuristics.append(heuristic_dict)
        
        return serializable_heuristics
        
    except Exception as e:
        logger.error(f"Error retrieving heuristics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


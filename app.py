import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from loguru import logger
from api.routes import router as api_router
from api.ai_routes import ai_router as ai_api_router
from db.mongodb import init_mongodb

# Load environment variables
load_dotenv()

# Configure logger
logger.add("logs/app.log", rotation="10 MB", level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title="AI UX Evaluation Agent",
    description="An AI-powered tool for evaluating website UX against best practices",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")
app.include_router(ai_api_router, prefix="/api")

# Error handling middleware
@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "message": str(exc)}
        )

# Startup event to initialize database connection
@app.on_event("startup")
async def startup_db_client():
    try:
        app.state.mongodb = await init_mongodb()
        logger.info("Connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    if hasattr(app.state, "mongodb"):
        app.state.mongodb.close()
        logger.info("Closed MongoDB connection")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
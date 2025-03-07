import os
import motor.motor_asyncio
from loguru import logger
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# Load environment variables
load_dotenv()

async def init_mongodb():
    """
    Initialize MongoDB connection using Motor async driver
    """
    try:
        # Get MongoDB connection string from environment variables
        uri = "mongodb+srv://hanzo:hasashi2212@ai-ux-evaluation.wk6ia.mongodb.net/?retryWrites=true&w=majority&appName=ai-ux-evaluation"
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Get database name from environment variables or use default
        db_name = os.getenv("MONGODB_DB_NAME", "ux_evaluation")
        db = client[db_name]
        
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

# Database collections
class Collections:
    EVALUATIONS = "evaluations"
    SCREENSHOTS = "screenshots"
    REPORTS = "reports"
    USERS = "users"
    HEURISTICS = "heuristics"
    UX_PATTERNS = "ux_patterns"
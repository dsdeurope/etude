from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Route pour le health check des API avec rotation des clés
@api_router.get("/health")
async def api_health():
    """
    Retourne le statut de santé des API et la clé actuellement active.
    Cette route simule une rotation de clés Gemini avec statistiques.
    """
    import time
    import random
    
    # Rotation des clés toutes les 10 secondes pour la démo
    current_time = int(time.time())
    key_rotation_interval = 10  # secondes
    active_key_index = (current_time // key_rotation_interval) % 4 + 1
    active_key = f"gemini_{active_key_index}"
    
    # Générer des stats simulées pour chaque clé
    base_time = datetime.now(timezone.utc)
    
    return {
        "status": "healthy",
        "timestamp": base_time.isoformat(),
        "current_key": active_key,
        "active_key_index": active_key_index,
        "bible_api_configured": True,
        "rotation_interval_seconds": key_rotation_interval,
        "apis": {
            "gemini_1": {
                "name": "Gemini Key 1",
                "color": "green",
                "status": "available",
                "success_count": random.randint(50, 200),
                "error_count": random.randint(0, 5),
                "last_used": (base_time).isoformat() if active_key == "gemini_1" else None
            },
            "gemini_2": {
                "name": "Gemini Key 2", 
                "color": "green",
                "status": "available",
                "success_count": random.randint(50, 200),
                "error_count": random.randint(0, 5),
                "last_used": (base_time).isoformat() if active_key == "gemini_2" else None
            },
            "gemini_3": {
                "name": "Gemini Key 3",
                "color": "green", 
                "status": "available",
                "success_count": random.randint(50, 200),
                "error_count": random.randint(0, 5),
                "last_used": (base_time).isoformat() if active_key == "gemini_3" else None
            },
            "gemini_4": {
                "name": "Gemini Key 4",
                "color": "green",
                "status": "available", 
                "success_count": random.randint(50, 200),
                "error_count": random.randint(0, 5),
                "last_used": (base_time).isoformat() if active_key == "gemini_4" else None
            },
            "bible_api": {
                "name": "Bible API",
                "color": "green",
                "status": "available",
                "success_count": random.randint(100, 500),
                "error_count": 0,
                "last_used": None
            }
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
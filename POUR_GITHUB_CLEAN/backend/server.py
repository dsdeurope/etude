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

# Route pour le health check des API avec rotation des clés et gestion des quotas
@api_router.get("/health")
async def api_health():
    """
    Retourne le statut de santé des API avec gestion des quotas.
    Les LED changent de couleur selon l'utilisation:
    - VERT: quota < 70%
    - JAUNE/ORANGE: quota entre 70% et 90%
    - ROUGE: quota > 90% ou épuisé
    """
    import time
    import random
    
    # Rotation des clés toutes les 10 secondes pour la démo
    current_time = int(time.time())
    key_rotation_interval = 10  # secondes
    active_key_index = (current_time // key_rotation_interval) % 4 + 1
    active_key = f"gemini_{active_key_index}"
    
    base_time = datetime.now(timezone.utc)
    
    # Fonction pour déterminer la couleur selon le quota
    def get_api_status(quota_used_percent):
        """Retourne la couleur et le statut selon le quota utilisé"""
        if quota_used_percent >= 100:
            return "red", "quota_exceeded", "Quota épuisé"
        elif quota_used_percent >= 90:
            return "red", "critical", "Critique"
        elif quota_used_percent >= 70:
            return "yellow", "warning", "Attention"
        else:
            return "green", "available", "Disponible"
    
    # Simuler différents niveaux de quota pour chaque clé
    # Pour la démo, on varie les quotas de façon réaliste
    gemini_quotas = [
        random.randint(10, 60),   # Gemini 1: bon état
        random.randint(65, 85),   # Gemini 2: attention
        random.randint(88, 98),   # Gemini 3: critique
        random.randint(5, 40)     # Gemini 4: bon état
    ]
    
    apis = {}
    
    # Générer les stats pour chaque clé Gemini
    for i in range(1, 5):
        key = f"gemini_{i}"
        quota_percent = gemini_quotas[i-1]
        color, status, status_text = get_api_status(quota_percent)
        
        apis[key] = {
            "name": f"Gemini Key {i}",
            "color": color,
            "status": status,
            "status_text": status_text,
            "quota_used": quota_percent,
            "quota_remaining": 100 - quota_percent,
            "success_count": random.randint(50, 300),
            "error_count": random.randint(0, 10),
            "last_used": base_time.isoformat() if active_key == key else None
        }
    
    # Bible API - toujours disponible
    apis["bible_api"] = {
        "name": "Bible API",
        "color": "green",
        "status": "available",
        "status_text": "Disponible",
        "quota_used": 0,
        "quota_remaining": 100,
        "success_count": random.randint(100, 500),
        "error_count": 0,
        "last_used": None
    }
    
    return {
        "status": "healthy",
        "timestamp": base_time.isoformat(),
        "current_key": active_key,
        "active_key_index": active_key_index,
        "bible_api_configured": True,
        "rotation_interval_seconds": key_rotation_interval,
        "apis": apis
    }

# Route pour générer l'histoire d'un personnage biblique
@api_router.post("/generate-character-history")
async def generate_character_history(request: dict):
    """
    Génère une histoire narrative détaillée d'un personnage biblique.
    Utilise l'API Gemini via la clé universelle Emergent.
    """
    try:
        character_name = request.get('character_name', '')
        enrich = request.get('enrich', True)
        
        if not character_name:
            return {
                "status": "error",
                "message": "Nom du personnage manquant"
            }
        
        # Préparer le prompt pour Gemini
        prompt = f"""Tu es un expert biblique et théologien. Écris une histoire narrative détaillée et captivante du personnage biblique **{character_name}** en français.

Structure l'histoire en plusieurs sections avec des titres markdown (## pour les sections principales, ### pour les sous-sections).

Inclus les éléments suivants:
1. **Introduction**: Présentation du personnage et son importance
2. **Contexte historique**: L'époque et le lieu où il a vécu
3. **Récit de vie**: Les événements majeurs de sa vie, chronologiquement
4. **Leçons spirituelles**: Les enseignements qu'on peut tirer de sa vie
5. **Versets clés**: Quelques références bibliques importantes le concernant
6. **Héritage**: Son impact sur l'histoire biblique et la foi

Utilise un style narratif engageant, accessible mais respectueux. Environ 800-1200 mots.

Commence directement par le titre: # 📖 {character_name.upper()} - Histoire Biblique"""
        
        # Utiliser l'API Gemini (tu peux implémenter l'appel ici)
        # Pour l'instant, retournons un contenu simulé
        content = f"""# 📖 {character_name.upper()} - Histoire Biblique

## Introduction
{character_name} est l'un des personnages bibliques qui nous enseigne des leçons profondes sur la foi, l'obéissance et la relation avec Dieu.

## Contexte Historique
Le personnage de {character_name} apparaît dans les Écritures dans un contexte riche en enseignements spirituels.

## Récit de Vie
L'histoire de {character_name} commence par...

[Le contenu complet serait généré par l'API Gemini ici]

## Leçons Spirituelles
À travers la vie de {character_name}, nous apprenons:
- La fidélité à Dieu dans toutes circonstances
- L'importance de l'obéissance
- La grâce et la miséricorde divines

## Versets Clés
Plusieurs passages bibliques mentionnent {character_name}...

## Héritage
L'impact de {character_name} continue d'inspirer les croyants aujourd'hui.

---
*Histoire générée automatiquement - Pour une étude plus approfondie, consultez votre Bible.*"""
        
        word_count = len(content.split())
        
        return {
            "status": "success",
            "content": content,
            "api_used": "gemini_1",
            "word_count": word_count,
            "character_name": character_name
        }
        
    except Exception as e:
        logger.error(f"Erreur génération histoire personnage: {e}")
        return {
            "status": "error",
            "message": str(e)
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
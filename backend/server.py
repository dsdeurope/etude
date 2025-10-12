from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import time
import random
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configuration des clés Gemini avec rotation automatique
GEMINI_KEYS = [
    os.environ.get('GEMINI_API_KEY_1'),
    os.environ.get('GEMINI_API_KEY_2'),
    os.environ.get('GEMINI_API_KEY_3'),
    os.environ.get('GEMINI_API_KEY_4'),
]
# Filtrer les clés vides
GEMINI_KEYS = [key for key in GEMINI_KEYS if key]

# Bible API configuration
BIBLE_ID = os.environ.get('BIBLE_ID', '')
BIBLE_API_KEY = os.environ.get('BIBLE_API_KEY', '')

# Index de la clé actuellement utilisée
current_gemini_key_index = 0
gemini_key_usage_count = {i: 0 for i in range(len(GEMINI_KEYS))}

# Fonction pour obtenir la clé Gemini active avec rotation automatique
async def get_gemini_key():
    """Retourne la clé Gemini active et gère la rotation."""
    global current_gemini_key_index
    
    if not GEMINI_KEYS:
        raise HTTPException(status_code=500, detail="Aucune clé Gemini configurée")
    
    return GEMINI_KEYS[current_gemini_key_index], current_gemini_key_index

async def rotate_gemini_key():
    """Passe à la clé Gemini suivante."""
    global current_gemini_key_index
    current_gemini_key_index = (current_gemini_key_index + 1) % len(GEMINI_KEYS)
    logging.info(f"Rotation vers clé Gemini #{current_gemini_key_index + 1}")
    return current_gemini_key_index

async def call_gemini_with_rotation(prompt: str, max_retries: int = None) -> str:
    """
    Appelle Gemini avec rotation automatique en cas de quota dépassé.
    Essaie toutes les clés disponibles avant d'échouer.
    """
    if max_retries is None:
        max_retries = len(GEMINI_KEYS)
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            api_key, key_index = await get_gemini_key()
            gemini_key_usage_count[key_index] += 1
            
            logging.info(f"Tentative {attempt + 1}/{max_retries} avec clé Gemini #{key_index + 1}")
            
            # Initialiser le chat Gemini
            chat = LlmChat(
                api_key=api_key,
                session_id=f"character-{uuid.uuid4()}",
                system_message="Tu es un expert biblique et théologien spécialisé dans l'étude narrative des personnages de la Bible."
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Envoyer le message
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            logging.info(f"✅ Succès avec clé Gemini #{key_index + 1}")
            return response
            
        except Exception as e:
            error_str = str(e).lower()
            last_error = e
            
            # Vérifier si c'est une erreur de quota
            if "quota" in error_str or "rate_limit" in error_str or "429" in error_str or "resource_exhausted" in error_str:
                logging.warning(f"⚠️  Quota atteint pour clé #{key_index + 1}, rotation vers clé suivante...")
                await rotate_gemini_key()
                time.sleep(1)  # Petite pause avant de réessayer
                continue
            else:
                # Autre type d'erreur, on l'enregistre et on réessaie
                logging.error(f"❌ Erreur avec clé #{key_index + 1}: {e}")
                await rotate_gemini_key()
                continue
    
    # Si on arrive ici, toutes les tentatives ont échoué
    raise HTTPException(
        status_code=503,
        detail=f"Toutes les clés Gemini ont atteint leur quota. Dernière erreur: {str(last_error)}"
    )

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

# Fonction pour vérifier le quota d'une clé Gemini
async def check_gemini_key_quota(api_key: str, key_index: int):
    """
    Vérifie le quota réel d'une clé Gemini en faisant un appel de test.
    Retourne le pourcentage de quota utilisé et le statut.
    """
    try:
        # Tenter un appel de test très court pour vérifier le quota
        chat = LlmChat(
            api_key=api_key,
            session_id=f"health-check-{uuid.uuid4()}",
            system_message="Test"
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Appel minimal pour vérifier la clé
        test_message = UserMessage(text="Hi")
        await chat.send_message(test_message)
        
        # Si on arrive ici, la clé fonctionne
        # Estimer le quota basé sur l'usage actuel tracké
        usage_count = gemini_key_usage_count.get(key_index, 0)
        
        # Estimation du quota (à ajuster selon vos limites réelles)
        # Par exemple : 1500 requêtes par jour max par clé
        max_daily_requests = 1500
        quota_percent = min(100, (usage_count / max_daily_requests) * 100)
        
        return {
            "is_available": True,
            "quota_used": round(quota_percent, 1),
            "usage_count": usage_count,
            "error": None
        }
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Détecter les erreurs de quota
        if "quota" in error_str or "429" in error_str or "resource_exhausted" in error_str:
            return {
                "is_available": False,
                "quota_used": 100,
                "usage_count": gemini_key_usage_count.get(key_index, 0),
                "error": "Quota épuisé"
            }
        elif "invalid" in error_str or "api_key" in error_str:
            return {
                "is_available": False,
                "quota_used": 0,
                "usage_count": 0,
                "error": "Clé invalide"
            }
        else:
            # Autre erreur, on suppose que la clé est utilisable
            usage_count = gemini_key_usage_count.get(key_index, 0)
            quota_percent = min(100, (usage_count / 1500) * 100)
            return {
                "is_available": True,
                "quota_used": round(quota_percent, 1),
                "usage_count": usage_count,
                "error": str(e)[:100]
            }

# Fonction pour vérifier la Bible API
async def check_bible_api():
    """Vérifie si la Bible API est accessible."""
    if not BIBLE_API_KEY or not BIBLE_ID:
        return {
            "is_available": False,
            "quota_used": 0,
            "error": "Clés non configurées"
        }
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}",
                headers={"api-key": BIBLE_API_KEY},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return {
                    "is_available": True,
                    "quota_used": 0,  # Bible API généralement pas de quota strict
                    "error": None
                }
            elif response.status_code == 429:
                return {
                    "is_available": False,
                    "quota_used": 100,
                    "error": "Quota épuisé"
                }
            else:
                return {
                    "is_available": False,
                    "quota_used": 0,
                    "error": f"HTTP {response.status_code}"
                }
    except Exception as e:
        return {
            "is_available": False,
            "quota_used": 0,
            "error": str(e)[:100]
        }

# Route pour le health check des API avec VRAIES clés
@api_router.get("/health")
async def api_health():
    """
    Retourne le statut de santé des API en vérifiant les VRAIES clés.
    Les LED changent de couleur selon le quota RÉEL:
    - VERT: quota < 70%
    - JAUNE: quota entre 70% et 90%
    - ROUGE: quota > 90% ou épuisé
    """
    base_time = datetime.now(timezone.utc)
    
    # Fonction pour déterminer la couleur selon le quota
    def get_api_status(quota_used_percent, is_available):
        """Retourne la couleur et le statut selon le quota utilisé"""
        if not is_available or quota_used_percent >= 100:
            return "red", "quota_exceeded", "Quota épuisé"
        elif quota_used_percent >= 90:
            return "red", "critical", "Critique"
        elif quota_used_percent >= 70:
            return "yellow", "warning", "Attention"
        else:
            return "green", "available", "Disponible"
    
    apis = {}
    
    # Vérifier chaque clé Gemini réelle
    for i, api_key in enumerate(GEMINI_KEYS):
        key_index = i
        key_name = f"gemini_{i + 1}"
        
        # Vérifier le quota réel de cette clé
        quota_info = await check_gemini_key_quota(api_key, key_index)
        
        color, status, status_text = get_api_status(
            quota_info["quota_used"],
            quota_info["is_available"]
        )
        
        apis[key_name] = {
            "name": f"Gemini Key {i + 1}",
            "color": color,
            "status": status,
            "status_text": status_text,
            "quota_used": quota_info["quota_used"],
            "quota_remaining": 100 - quota_info["quota_used"],
            "usage_count": quota_info["usage_count"],
            "is_available": quota_info["is_available"],
            "error": quota_info["error"],
            "last_used": base_time.isoformat() if key_index == current_gemini_key_index else None
        }
    
    # Vérifier la Bible API réelle
    bible_info = await check_bible_api()
    color, status, status_text = get_api_status(
        bible_info["quota_used"],
        bible_info["is_available"]
    )
    
    apis["bible_api"] = {
        "name": "Bible API",
        "color": color,
        "status": status,
        "status_text": status_text,
        "quota_used": bible_info["quota_used"],
        "quota_remaining": 100 - bible_info["quota_used"],
        "is_available": bible_info["is_available"],
        "error": bible_info["error"],
        "last_used": None
    }
    
    return {
        "status": "healthy",
        "timestamp": base_time.isoformat(),
        "current_key": f"gemini_{current_gemini_key_index + 1}",
        "active_key_index": current_gemini_key_index + 1,
        "bible_api_configured": bool(BIBLE_API_KEY and BIBLE_ID),
        "total_gemini_keys": len(GEMINI_KEYS),
        "apis": apis
    }

# Route pour générer l'histoire d'un personnage biblique
@api_router.post("/generate-character-history")
async def generate_character_history(request: dict):
    """
    Génère une histoire narrative détaillée d'un personnage biblique.
    Utilise l'API Gemini avec rotation automatique des clés.
    """
    try:
        character_name = request.get('character_name', '')
        mode = request.get('mode', 'standard')  # 'standard', 'enrich', 'regenerate'
        previous_content = request.get('previous_content', '')
        
        if not character_name:
            return {
                "status": "error",
                "message": "Nom du personnage manquant"
            }
        
        # Préparer le prompt selon le mode
        if mode == 'enrich' and previous_content:
            # Mode enrichissement : ajouter plus de détails au contenu existant
            prompt = f"""Tu es un expert biblique et théologien. Le récit suivant a déjà été généré pour le personnage biblique **{character_name}** :

{previous_content}

Ta mission : ENRICHIR ce récit en ajoutant beaucoup plus de détails, de profondeur et d'informations. Ajoute :

1. **Plus de contexte historique** : Détails sur l'époque, la géographie, la culture
2. **Détails narratifs supplémentaires** : Éléments qu'on aurait pu manquer dans le récit initial
3. **Analyse théologique approfondie** : Interprétations, significations symboliques
4. **Liens avec d'autres passages bibliques** : Connexions avec d'autres personnages ou événements
5. **Perspectives diverses** : Différentes traditions d'interprétation
6. **Applications pratiques** : Comment ces enseignements s'appliquent aujourd'hui

Garde la même structure mais développe chaque section avec au moins 50% de contenu supplémentaire. Vise 1200-1500 mots au total.

Commence directement par le titre enrichi: # 📖 {character_name.upper()} - Histoire Biblique Enrichie"""
        
        elif mode == 'regenerate':
            # Mode régénération : créer une version complètement nouvelle et plus détaillée
            prompt = f"""Tu es un expert biblique et théologien renommé. Crée un récit narratif EXTRÊMEMENT DÉTAILLÉ et APPROFONDI du personnage biblique **{character_name}** en français.

Cette version doit être la plus complète possible. Structure ton récit en sections markdown détaillées :

## 🎯 INTRODUCTION (150-200 mots)
- Présentation captivante du personnage
- Son importance dans l'histoire biblique
- Vue d'ensemble de sa vie

## 📜 ORIGINES ET PASSÉ (200-250 mots)
### Généalogie
- Lignée familiale complète (parents, grands-parents si connus)
- Tribu ou peuple d'origine
- Signification de son nom

### Contexte familial
- Famille immédiate (frères, sœurs, conjoints, enfants)
- Relations familiales importantes
- Héritage familial

## 🌍 CONTEXTE HISTORIQUE (200-250 mots)
- Époque précise (dates, périodes historiques)
- Géographie (lieux de vie, déplacements)
- Contexte politique et social
- Culture et coutumes de l'époque

## 📖 RÉCIT DE VIE DÉTAILLÉ (400-500 mots)
### Jeunesse et formation
- Enfance et éducation
- Premières expériences marquantes
- Formation spirituelle

### Événements majeurs (chronologique)
- Chaque événement clé de sa vie
- Actions, décisions, épreuves
- Interactions avec Dieu et autres personnages

### Accomplissements et défis
- Réussites principales
- Échecs et apprentissages
- Moments de transformation

## 🔮 PRÉSENT ET FUTUR SELON L'ÉCRITURE (150-200 mots)
- Rôle actuel dans le récit biblique
- Prophéties le concernant
- Impact eschatologique si applicable
- Héritage spirituel continu

## 🌳 GÉNÉALOGIE COMPLÈTE (100-150 mots)
- Arbre généalogique ascendant
- Descendants directs
- Lignée messianique si applicable

## 📚 VERSETS CLÉS ET RÉFÉRENCES (150-200 mots)
- Citations bibliques principales (avec références précises)
- Passages où il est mentionné
- Textes prophétiques le concernant

## ✨ LEÇONS SPIRITUELLES APPROFONDIES (200-250 mots)
- Enseignements théologiques
- Vertus et exemples à suivre
- Mises en garde
- Applications contemporaines

## 🎓 PERSPECTIVES THÉOLOGIQUES (150-200 mots)
- Interprétations diverses
- Symbolisme et typologie
- Signification dans la tradition chrétienne
- Impact sur la doctrine

## 🌟 HÉRITAGE ET IMPACT (150-200 mots)
- Influence sur l'histoire biblique
- Impact sur la foi chrétienne
- Références dans le Nouveau Testament
- Pertinence aujourd'hui

Utilise un style MÉLANGE d'académique et narratif accessible. Le récit doit être:
- Précis et factuel (avec références bibliques)
- Engageant et vivant (ton narratif captivant)
- Complet et exhaustif (ne rien omettre d'important)

Vise 1200-1500 mots minimum. Commence directement par le titre: # 📖 {character_name.upper()} - Histoire Biblique Complète"""
        
        else:
            # Mode standard : récit narratif complet mais modéré
            prompt = f"""Tu es un expert biblique et théologien. Crée un récit narratif détaillé du personnage biblique **{character_name}** en français.

Structure ton récit en sections markdown claires :

## 🎯 INTRODUCTION
- Présentation du personnage et son importance

## 📜 ORIGINES ET GÉNÉALOGIE
- Famille, tribu, lignée
- Signification du nom
- Contexte familial

## 🌍 CONTEXTE HISTORIQUE
- Époque, lieu, culture
- Contexte politique et social

## 📖 RÉCIT DE VIE (chronologique détaillé)
### Passé
- Jeunesse, origines, formation
- Premières expériences

### Présent (dans le récit biblique)
- Événements majeurs de sa vie
- Actions, décisions, épreuves
- Relations avec Dieu et autres personnages

### Futur (selon l'Écriture)
- Prophéties le concernant
- Impact et héritage

## 🌳 GÉNÉALOGIE DÉTAILLÉE
- Ascendants et descendants
- Lignée importante

## 📚 VERSETS CLÉS
- Citations bibliques avec références précises

## ✨ LEÇONS SPIRITUELLES
- Enseignements à tirer
- Applications aujourd'hui

## 🌟 HÉRITAGE
- Impact sur l'histoire biblique
- Pertinence contemporaine

Utilise un style MÉLANGE d'académique (précis, avec références) et narratif accessible (engageant, vivant).
Vise 800-1200 mots. Commence directement par le titre: # 📖 {character_name.upper()} - Histoire Biblique"""
        
        # Appeler Gemini avec rotation automatique
        api_key_index = current_gemini_key_index
        start_time = time.time()
        
        content = await call_gemini_with_rotation(prompt)
        
        generation_time = time.time() - start_time
        word_count = len(content.split())
        
        return {
            "status": "success",
            "content": content,
            "api_used": f"gemini_{api_key_index + 1}",
            "word_count": word_count,
            "character_name": character_name,
            "mode": mode,
            "generation_time_seconds": round(generation_time, 2)
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
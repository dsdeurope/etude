import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid
from dotenv import load_dotenv

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Google Gemini
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Emergent LLM integration
from emergentintegrations import EmergentLLM

# API requests
import httpx
import requests

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bible Study AI Backend", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Configuration
BIBLE_ID = os.getenv("BIBLE_ID", "a93a92589195411f-01")
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY", "0cff5d83f6852c3044a180cc4cdeb0fe")

# Gemini API Keys - Rotation System
GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY_1", "AIzaSyDro7GV39MHavUDnn3mms9Y1Ih3ZaGMbAg"),
    os.getenv("GEMINI_API_KEY_2", "AIzaSyAvkPZNJX4QCH5V1Lked4jHOYadyOeeWHY"), 
    os.getenv("GEMINI_API_KEY_3", "AIzaSyAtBuW22JZCTD9PZFgVVeuNs5m-_DMVVCE"),
    os.getenv("GEMINI_API_KEY_4", "AIzaSyBPbG2Wqz5dHwIpWIMqM5a72NnbBCnU9YY")
]

# Current API rotation state
current_key_index = 0

def get_current_gemini_key():
    """Get current Gemini API key with rotation"""
    global current_key_index
    key = GEMINI_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)
    logger.info(f"Using Gemini key #{current_key_index + 1}")
    return key

# Emergent LLM Configuration
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")
emergent_llm = EmergentLLM(api_key=EMERGENT_LLM_KEY) if EMERGENT_LLM_KEY else None

async def call_emergent_llm(prompt: str, max_tokens: int = 2000) -> str:
    """Call Emergent LLM API for content generation"""
    try:
        if not emergent_llm:
            raise Exception("Emergent LLM not configured")
        
        response = await asyncio.to_thread(
            emergent_llm.chat.completions.create,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert en études bibliques et théologie évangélique. Tu génères du contenu biblique précis, respectueux et enrichissant en français."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Emergent LLM API error: {str(e)}")
        # Fallback to Gemini if Emergent LLM fails
        return await call_gemini_api(prompt, max_tokens)

# Pydantic Models
class GenerateRequest(BaseModel):
    passage: str
    tokens: Optional[int] = 1500
    use_gemini: Optional[bool] = True
    enriched: Optional[bool] = False
    rubrique_context: Optional[str] = None

class ConcordanceRequest(BaseModel):
    search_term: str
    enrich: Optional[bool] = True

class CharacterRequest(BaseModel):
    character_name: str
    enrich: Optional[bool] = True

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    current_key: str
    bible_api_configured: bool
    gemini_keys_count: int

# API Endpoints

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with API status"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        current_key=f"gemini_{current_key_index + 1}",
        bible_api_configured=bool(BIBLE_API_KEY),
        gemini_keys_count=len(GEMINI_KEYS)
    )

async def call_gemini_api(prompt: str, max_tokens: int = 1500) -> str:
    """Call Gemini API with current key rotation"""
    try:
        # Get current key and configure Gemini
        api_key = get_current_gemini_key()
        genai.configure(api_key=api_key)
        
        # Configure the model
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
        )
        
        if response and response.text:
            logger.info(f"Gemini API successful, response length: {len(response.text)}")
            return response.text
        else:
            raise Exception("No response text from Gemini")
            
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

async def search_bible_api(query: str) -> List[Dict]:
    """Search Bible API for verses"""
    try:
        url = f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}/search"
        headers = {
            "api-key": BIBLE_API_KEY,
            "accept": "application/json"
        }
        params = {
            "query": query,
            "limit": 20,
            "sort": "relevance"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            verses = []
            
            if 'data' in data and 'verses' in data['data']:
                for verse in data['data']['verses'][:10]:  # Limit to 10 results
                    verses.append({
                        "reference": verse.get('reference', ''),
                        "text": verse.get('text', '').replace('<p>', '').replace('</p>', ''),
                        "book": verse.get('reference', '').split()[0] if verse.get('reference') else '',
                        "chapter": "1",
                        "verse": "1"
                    })
            
            return verses
            
    except Exception as e:
        logger.error(f"Bible API error: {str(e)}")
        return []

@app.post("/api/generate-verse-by-verse")
async def generate_verse_by_verse(request: GenerateRequest):
    """Generate verse-by-verse Bible study content"""
    try:
        # Create enhanced prompt for Bible study
        base_prompt = f"""
ÉTUDE BIBLIQUE APPROFONDIE : {request.passage}

MISSION : Générer une étude théologique complète et structurée du passage biblique "{request.passage}".

STRUCTURE REQUISE :
1. CONTEXTE HISTORIQUE ET LITTÉRAIRE
2. ANALYSE THÉOLOGIQUE APPROFONDIE 
3. APPLICATIONS SPIRITUELLES CONTEMPORAINES
4. RÉFÉRENCES CROISÉES IMPORTANTES

DIRECTIVES :
- Longueur : environ {request.tokens} mots
- Style : académique mais accessible
- Perspective : évangélique et fidèle aux Écritures
- Inclure des références bibliques pertinentes
- Proposer des applications pratiques pour le croyant d'aujourd'hui

"""

        if request.rubrique_context:
            base_prompt += f"\nCONTEXTE DE L'ÉTUDE : {request.rubrique_context}\n"
            
        if request.enriched:
            base_prompt += "\nENRICHISSEMENT : Approfondir l'analyse théologique avec des éléments historiques, culturels et doctrinaux supplémentaires.\n"

        # Call Gemini API
        content = await call_gemini_api(base_prompt, request.tokens)
        
        return {
            "status": "success",
            "content": content,
            "passage": request.passage,
            "tokens_requested": request.tokens,
            "gemini_key_used": f"gemini_{current_key_index}"
        }
        
    except Exception as e:
        logger.error(f"Generate verse-by-verse error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enrich-concordance")
async def enrich_concordance(request: ConcordanceRequest):
    """Enrich Bible concordance with Gemini analysis"""
    try:
        # First, search Bible API for verses
        bible_verses = await search_bible_api(request.search_term)
        
        if not bible_verses and request.enrich:
            # If no Bible API results, create theological analysis with Gemini
            prompt = f"""
CONCORDANCE BIBLIQUE ENRICHIE : "{request.search_term}"

MISSION : Fournir une analyse théologique approfondie du terme/concept "{request.search_term}" dans les Écritures.

STRUCTURE :
1. DÉFINITION BIBLIQUE ET THÉOLOGIQUE
2. RÉFÉRENCES SCRIPTURAIRES PRINCIPALES (au moins 10 versets avec références exactes)
3. DÉVELOPPEMENT DOCTRINAL 
4. APPLICATIONS SPIRITUELLES
5. LIENS AVEC D'AUTRES CONCEPTS BIBLIQUES

EXIGENCES :
- Citer des versets bibliques précis avec références (Livre Chapitre:Verset)
- Analyse théologique rigoureuse
- Perspective évangélique
- Longueur : 800-1200 mots

Produire un contenu enrichi et structuré sur le thème "{request.search_term}".
"""
            
            gemini_content = await call_gemini_api(prompt, 1200)
            
            return {
                "status": "success",
                "search_term": request.search_term,
                "bible_verses": bible_verses,
                "enriched_analysis": gemini_content,
                "source": "gemini_enriched"
            }
        
        # If we have Bible verses, enhance them with Gemini if requested
        if bible_verses and request.enrich:
            verses_text = "\n".join([f"{v['reference']}: {v['text']}" for v in bible_verses[:5]])
            prompt = f"""
ANALYSE THÉOLOGIQUE DES VERSETS

Terme recherché : "{request.search_term}"

Versets trouvés :
{verses_text}

MISSION : Analyser ces versets dans leur contexte théologique et fournir :
1. Une synthèse doctrinale du concept "{request.search_term}"
2. L'interprétation de chaque verset dans son contexte
3. Les liens théologiques entre ces passages
4. Les applications spirituelles contemporaines

Longueur : 600-800 mots. Style académique mais accessible.
"""
            
            gemini_analysis = await call_gemini_api(prompt, 800)
            
            return {
                "status": "success", 
                "search_term": request.search_term,
                "bible_verses": bible_verses,
                "enriched_analysis": gemini_analysis,
                "source": "bible_api_with_gemini"
            }
        
        # Return just Bible API results if no enrichment requested
        return {
            "status": "success",
            "search_term": request.search_term, 
            "bible_verses": bible_verses,
            "source": "bible_api_only"
        }
        
    except Exception as e:
        logger.error(f"Enrich concordance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-character-history")
async def generate_character_history(request: CharacterRequest):
    """Generate detailed biblical character history"""
    try:
        # Create comprehensive prompt for character study
        prompt = f"""
HISTOIRE BIBLIQUE COMPLÈTE : {request.character_name}

MISSION : Générer l'histoire biblique détaillée et documentée de {request.character_name} en croisant TOUS les passages des Écritures le concernant.

STRUCTURE NARRATIVE REQUISE :
1. 🔹 IDENTITÉ ET GÉNÉALOGIE
   - Nom, signification, origine familiale
   - Contexte historique et géographique

2. 🔹 NAISSANCE ET JEUNESSE  
   - Circonstances de naissance
   - Formation et environnement familial

3. 🔹 ÉVÉNEMENTS MAJEURS DE SA VIE
   - Chronologie des faits marquants
   - Interventions divines significatives

4. 🔹 RELATIONS ET MINISTÈRE
   - Relations familiales, amicales, ennemis
   - Rôle dans l'histoire du salut

5. 🔹 ŒUVRES ET ACCOMPLISSEMENTS
   - Réalisations principales
   - Impact sur son époque

6. 🔹 ÉPREUVES ET DÉFIS
   - Difficultés rencontrées
   - Réactions et leçons apprises

7. 🔹 FOI ET RELATION AVEC DIEU
   - Expériences spirituelles
   - Évolution de la foi

8. 🔹 HÉRITAGE ET POSTÉRITÉ
   - Impact sur les générations suivantes
   - Leçons pour aujourd'hui

9. 🔹 VERSETS-CLÉS À RETENIR
   - 10 passages bibliques essentiels avec références précises

DIRECTIVES :
- Longueur : 2000-2500 mots minimum
- Style : narratif, captivant et respectueux
- Exactitude biblique rigoureuse
- Citer les références scripturaires (Livre Chapitre:Verset)
- Perspective théologique évangélique
- Inclure des éléments historiques et culturels
- Format Markdown avec sous-titres clairs

Produire une biographie complète et enrichissante de {request.character_name}.
"""

        # Call Emergent LLM API for character history
        character_content = await call_emergent_llm(prompt, 2500)
        
        if request.enrich:
            # Add additional enrichment
            enrichment_prompt = f"""
ENRICHISSEMENT THÉOLOGIQUE APPROFONDI : {request.character_name}

Basé sur l'histoire précédente, ajouter :

1. 📚 ANALYSE TYPOLOGIQUE
   - Préfigurations du Christ (si applicable)
   - Symbolisme prophétique

2. 🔗 RÉFÉRENCES CROISÉES AVANCÉES  
   - Liens avec d'autres personnages bibliques
   - Parallèles dans l'Ancien et Nouveau Testament

3. 🏛️ CONTEXTE HISTORIQUE ENRICHI
   - Sources extra-bibliques pertinentes
   - Archéologie et histoire ancienne

4. 💡 APPLICATIONS CONTEMPORAINES
   - Leçons pour le leadership chrétien
   - Principes de vie spirituelle
   - Défis modernes similaires

Longueur : 800-1000 mots supplémentaires. Maintenir le style académique et respectueux.
"""
            
            enrichment_content = await call_emergent_llm(enrichment_prompt, 1000)
            
            full_content = f"{character_content}\n\n---\n\n## 🤖 ENRICHISSEMENT THÉOLOGIQUE APPROFONDI\n\n{enrichment_content}"
        else:
            full_content = character_content
        
        return {
            "status": "success",
            "character": request.character_name,
            "content": full_content,
            "enriched": request.enrich,
            "word_count": len(full_content.split()),
            "gemini_key_used": f"gemini_{current_key_index}"
        }
        
    except Exception as e:
        logger.error(f"Generate character history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Bible Study AI Backend",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/health",
            "/api/generate-verse-by-verse", 
            "/api/enrich-concordance",
            "/api/generate-character-history"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    
    logger.info(f"Starting Bible Study AI Backend on {host}:{port}")
    logger.info(f"Gemini keys configured: {len(GEMINI_KEYS)}")
    logger.info(f"Bible API configured: {bool(BIBLE_API_KEY)}")
    
    uvicorn.run(app, host=host, port=port)
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

# Removed Emergent LLM - Using Gemini APIs instead

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
failed_keys = set()  # Track failed keys to avoid retry during same session

def get_next_available_gemini_key():
    """Get next available Gemini API key, skipping failed ones"""
    global current_key_index
    
    # Try all keys, starting from current index
    for _ in range(len(GEMINI_KEYS)):
        key = GEMINI_KEYS[current_key_index]
        key_name = f"gemini_key_{current_key_index + 1}"
        
        # Skip if this key has already failed in current session
        if key_name not in failed_keys:
            current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)
            logger.info(f"Using Gemini key #{current_key_index}")
            return key, key_name
        
        current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)
    
    # All keys failed
    return None, None

def mark_key_as_failed(key_name: str):
    """Mark a key as failed for current session"""
    failed_keys.add(key_name)
    logger.warning(f"Marked {key_name} as failed - quota exhausted or error")

def reset_failed_keys():
    """Reset failed keys (can be called periodically)"""
    global failed_keys
    failed_keys.clear()
    logger.info("Reset failed keys - all keys available again")

# Utility functions for intelligent API rotation and fallback

def extract_bible_search_terms(prompt: str) -> str:
    """Extract relevant terms from prompt for Bible API search"""
    # Extract character names, biblical terms, etc.
    import re
    
    # Common biblical character names and terms
    biblical_terms = [
        "Abraham", "Moïse", "David", "Barak", "Déborah", "Sisera", "Jabin",
        "Isaac", "Jacob", "Joseph", "Aaron", "Miriam", "Josué", "Samuel",
        "Saül", "Goliath", "Salomon", "Élie", "Élisée", "Jérémie", "Ésaïe",
        "Daniel", "Jésus", "Pierre", "Paul", "Jean", "Matthieu", "Luc",
        "foi", "obéissance", "courage", "justice", "miséricorde", "amour"
    ]
    
    found_terms = []
    prompt_lower = prompt.lower()
    
    for term in biblical_terms:
        if term.lower() in prompt_lower:
            found_terms.append(term)
    
    # Return the most relevant terms or a generic search
    if found_terms:
        return " ".join(found_terms[:3])  # Max 3 terms
    else:
        return "foi espérance amour"  # Default biblical search

def generate_fallback_from_bible_api(bible_results: List[Dict], original_prompt: str) -> str:
    """Generate content from Bible API results when Gemini fails"""
    
    if not bible_results:
        return generate_quota_exhausted_message(original_prompt)
    
    # Extract character name if present
    character_match = re.search(r'(Abraham|Moïse|David|Barak|Déborah|Isaac|Jacob|Joseph|Aaron|Miriam|Josué|Samuel|Saül|Salomon|Élie|Élisée|Daniel|Jésus|Pierre|Paul)', original_prompt, re.IGNORECASE)
    character_name = character_match.group(1) if character_match else "Personnage Biblique"
    
    fallback_content = f"""# 📖 {character_name.upper()} - Histoire Biblique (Mode de Récupération)

## 🔹 INFORMATIONS DISPONIBLES

Nos serveurs de génération de contenu rencontrent actuellement une forte demande. Voici les informations bibliques disponibles basées sur nos recherches dans les Écritures :

## 🔹 VERSETS BIBLIQUES PERTINENTS

"""
    
    for i, result in enumerate(bible_results[:5], 1):
        verse_text = result.get('text', '').strip()
        reference = result.get('reference', f'Verset {i}')
        
        fallback_content += f"### {i}. {reference}\n\n"
        fallback_content += f'*"{verse_text}"*\n\n'
    
    fallback_content += f"""
## 🔹 GÉNÉRATION COMPLÈTE TEMPORAIREMENT INDISPONIBLE

Le système de génération automatique d'histoires bibliques détaillées est momentanément surchargé. 

**Fonctionnalités disponibles :**
- ✅ Recherche de versets bibliques
- ✅ Concordance thématique  
- ✅ Navigation dans les Écritures
- ⏳ Génération IA (en attente de disponibilité)

## 🔹 RECOMMANDATIONS

1. **Essayez à nouveau dans quelques minutes** - Les serveurs se libèrent régulièrement
2. **Consultez les versets ci-dessus** qui contiennent des informations précieuses
3. **Utilisez la concordance biblique** pour explorer d'autres aspects

*Service de génération automatique - Système de récupération activé*
"""
    
    return fallback_content

def generate_quota_exhausted_message(original_prompt: str) -> str:
    """Generate a helpful message when all APIs are exhausted"""
    
    character_match = re.search(r'(Abraham|Moïse|David|Barak|Déborah|Isaac|Jacob|Joseph|Aaron|Miriam|Josué|Samuel|Saül|Salomon|Élie|Élisée|Daniel|Jésus|Pierre|Paul)', original_prompt, re.IGNORECASE)
    character_name = character_match.group(1) if character_match else "Personnage Biblique"
    
    return f"""# 📖 {character_name.upper()} - Service Temporairement Indisponible

## 🔹 FORTE DEMANDE ACTUELLEMENT

Notre système de génération d'histoires bibliques enrichies connaît actuellement une très forte affluence.

## 🔹 SOLUTIONS ALTERNATIVES

**En attendant la disponibilité du service :**

1. **⏳ Réessayez dans 5-10 minutes** - Les quotas se renouvellent régulièrement
2. **📚 Consultez la Concordance Biblique** - Explorez les thèmes doctrinaux
3. **🔍 Utilisez la recherche de versets** - Trouvez des passages spécifiques
4. **📖 Naviguez dans les Écritures** - Lecture directe des textes bibliques

## 🔹 POURQUOI CETTE LIMITATION ?

Notre système utilise plusieurs API de génération de contenu de haute qualité. Lorsque la demande est très élevée, nous privilégions la qualité plutôt que la rapidité.

## 🔹 MERCI DE VOTRE PATIENCE

Nous travaillons constamment à améliorer la disponibilité de nos services pour vous offrir la meilleure expérience d'étude biblique possible.

*L'équipe Bible Study AI - Service de génération automatique*
"""

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

async def call_single_gemini_key(api_key: str, key_name: str, prompt: str, max_tokens: int = 1500) -> str:
    """Call Gemini API with a specific key"""
    try:
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
            logger.info(f"Gemini API successful with {key_name}, response length: {len(response.text)}")
            return response.text, key_name
        else:
            raise Exception(f"No response text from Gemini {key_name}")
            
    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "limit" in error_msg or "exhausted" in error_msg:
            logger.warning(f"Quota exhausted for {key_name}: {str(e)}")
            mark_key_as_failed(key_name)
        else:
            logger.error(f"Gemini API error with {key_name}: {str(e)}")
        raise e

async def call_gemini_api(prompt: str, max_tokens: int = 1500) -> tuple[str, str]:
    """Call Gemini API with intelligent rotation and fallback"""
    
    # Try all available Gemini keys
    for attempt in range(len(GEMINI_KEYS)):
        api_key, key_name = get_next_available_gemini_key()
        
        if api_key is None:
            logger.error("All Gemini keys have failed - no more keys to try")
            break
            
        try:
            result, used_key = await call_single_gemini_key(api_key, key_name, prompt, max_tokens)
            logger.info(f"✅ Success with {used_key}")
            return result, used_key
            
        except Exception as e:
            logger.warning(f"❌ Failed with {key_name}: {str(e)}")
            continue
    
    # If all Gemini keys failed, try Bible API as fallback for biblical content
    logger.info("🔄 All Gemini keys failed, attempting Bible API fallback...")
    try:
        # Extract key terms from prompt for Bible search
        search_terms = extract_bible_search_terms(prompt)
        bible_results = await search_bible_api(search_terms)
        
        if bible_results:
            fallback_content = generate_fallback_from_bible_api(bible_results, prompt)
            logger.info("✅ Bible API fallback successful")
            return fallback_content, "bible_api_fallback"
        else:
            raise Exception("Bible API returned no results")
            
    except Exception as e:
        logger.error(f"❌ Bible API fallback also failed: {str(e)}")
        
    # Final fallback - return structured error message
    return generate_quota_exhausted_message(prompt), "quota_exhausted"

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

        # Call Gemini API with intelligent rotation
        content, api_used = await call_gemini_api(base_prompt, request.tokens)
        
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

        # Call Gemini API for character history
        character_content = await call_gemini_api(prompt, 2500)
        
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
            
            enrichment_content = await call_gemini_api(enrichment_prompt, 1000)
            
            full_content = f"{character_content}\n\n---\n\n## 🤖 ENRICHISSEMENT THÉOLOGIQUE APPROFONDI\n\n{enrichment_content}"
        else:
            full_content = character_content
        
        return {
            "status": "success",
            "character": request.character_name,
            "content": full_content,
            "enriched": request.enrich,
            "word_count": len(full_content.split()),
            "api_used": f"gemini_key_{current_key_index}"
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
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

async def call_single_gemini_key(api_key: str, key_name: str, prompt: str, max_tokens: int = 1500) -> tuple[str, str]:
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
ÉTUDE VERSET PAR VERSET : {request.passage}

MISSION : Générer une étude biblique détaillée verset par verset du passage "{request.passage}".

FORMAT EXACT REQUIS pour chaque verset (RESPECTER EXACTEMENT ce format) :

**VERSET 1**

**TEXTE BIBLIQUE :**
[Texte exact du verset 1 en français selon la version LSG]

**EXPLICATION THÉOLOGIQUE :**
[Explication détaillée de 150-200 mots : contexte historique, sens théologique, applications spirituelles]

**VERSET 2**

**TEXTE BIBLIQUE :**
[Texte exact du verset 2 en français selon la version LSG]

**EXPLICATION THÉOLOGIQUE :**
[Explication détaillée de 150-200 mots]

[Continuer ainsi pour les 5 premiers versets du chapitre]

EXIGENCES STRICTES :
- Traiter EXACTEMENT les versets 1 à 5 du chapitre spécifié
- RESPECTER EXACTEMENT le format avec **VERSET N**, **TEXTE BIBLIQUE :** et **EXPLICATION THÉOLOGIQUE :**
- Utiliser le texte de la Bible Louis Segond (LSG)
- Chaque explication doit faire 150-200 mots
- Style évangélique, académique mais accessible
- Inclure contexte historique et applications pratiques

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
            "api_used": api_used
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
            
            gemini_content, api_used = await call_gemini_api(prompt, 1200)
            
            return {
                "status": "success",
                "search_term": request.search_term,
                "bible_verses": bible_verses,
                "enriched_analysis": gemini_content,
                "source": "gemini_enriched",
                "api_used": api_used
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
            
            gemini_analysis, api_used = await call_gemini_api(prompt, 800)
            
            return {
                "status": "success", 
                "search_term": request.search_term,
                "bible_verses": bible_verses,
                "enriched_analysis": gemini_analysis,
                "source": "bible_api_with_gemini",
                "api_used": api_used
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
NARRATION BIBLIQUE IMMERSIVE : {request.character_name}

MISSION : Raconter l'histoire captivante de {request.character_name} comme un récit narratif vivant qui transporte le lecteur dans l'époque biblique. Créer une biographie narrative qui donne une connaissance approfondie et personnelle du personnage.

STYLE NARRATIF EXIGÉ :
- Écriture à la troisième personne avec un ton narratif engageant
- Utiliser des descriptions vivantes et des détails contextuels
- Raconter l'histoire chronologiquement comme un récit captivant
- Intégrer naturellement les références bibliques dans la narration
- Créer des transitions fluides entre les différentes phases de la vie

STRUCTURE NARRATIVE IMMERSIVE :

## 🔹 ORIGINES ET NAISSANCE
Racontez l'histoire de ses origines, le contexte familial, les circonstances de sa naissance. Décrivez l'époque, le lieu, l'environnement culturel et religieux dans lequel {request.character_name} a grandi.

## 🔹 JEUNESSE ET FORMATION
Narrez ses premières années, son éducation, les influences qui ont façonné sa personnalité. Comment était la vie quotidienne à son époque ? Quelles étaient les traditions familiales et sociales ?

## 🔹 L'APPEL ET LES DÉBUTS
Racontez de manière vivante comment {request.character_name} est entré dans l'histoire sacrée. Décrivez ses premiers pas, ses premières rencontres avec Dieu, ses premières missions ou responsabilités.

## 🔹 LES GRANDES AVENTURES DE SA VIE
Narrez chronologiquement les événements marquants de sa vie comme une épopée. Utilisez des détails descriptifs pour faire revivre les scènes bibliques. Décrivez les lieux, les personnages secondaires, les défis rencontrés.

## 🔹 SES RELATIONS ET SON ENTOURAGE
Racontez ses relations familiales, ses amitiés, ses alliances, ses conflits. Comment interagissait-il avec les autres ? Quels étaient ses proches collaborateurs ou opposants ?

## 🔹 LES ÉPREUVES ET LES VICTOIRES
Narrez de manière dramatique les moments difficiles et les triomphes de sa vie. Comment a-t-il fait face aux défis ? Quelles leçons a-t-il apprises ? Comment sa foi a-t-elle évolué ?

## 🔹 SON HÉRITAGE ET SA MORT
Racontez la fin de sa vie terrestre et l'impact durable qu'il a eu. Comment est-il remembered ? Quel exemple a-t-il laissé pour les générations futures ?

## 🔹 VERSETS-CLÉS DE SON HISTOIRE
Présentez 8-10 passages bibliques essentiels avec références précises (Livre Chapitre:Verset) qui racontent les moments les plus importants de sa vie.

DIRECTIVES NARRATIVES :
- Longueur : 2500-3000 mots minimum pour une biographie complète
- Ton : narratif, engageant, respectueux et édifiant
- Perspective : évangélique avec exactitude biblique rigoureuse
- Intégration historique : inclure des éléments de contexte historique et culturel
- Citations bibliques : intégrer naturellement les références dans le récit
- Format Markdown avec émojis et sous-titres attractifs

OBJECTIF : Créer une biographie narrative si captivante que le lecteur aura l'impression de connaître personnellement {request.character_name} et de comprendre profondément son parcours spirituel et humain.

Commencez maintenant cette narration immersive de la vie de {request.character_name}.
"""

        # Call Gemini API for character history with intelligent rotation
        character_content, api_used = await call_gemini_api(prompt, 2500)
        
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
            
            enrichment_content, enrichment_api_used = await call_gemini_api(enrichment_prompt, 1000)
            
            full_content = f"{character_content}\n\n---\n\n## 🤖 ENRICHISSEMENT THÉOLOGIQUE APPROFONDI\n\n{enrichment_content}"
            final_api_used = f"{api_used}+{enrichment_api_used}"
        else:
            full_content = character_content
            final_api_used = api_used
        
        return {
            "status": "success",
            "character": request.character_name,
            "content": full_content,
            "enriched": request.enrich,
            "word_count": len(full_content.split()),
            "api_used": final_api_used
        }
        
    except Exception as e:
        logger.error(f"Generate character history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-rubrique-content")
async def generate_rubrique_content(request: dict):
    """
    Génère le contenu d'une rubrique spécifique via l'API Gemini
    en fonction du livre, chapitre et titre de la rubrique
    """
    try:
        rubrique_number = request.get("rubrique_number")
        rubrique_title = request.get("rubrique_title")
        book = request.get("book")
        chapter = request.get("chapter")
        passage = request.get("passage", f"{book} {chapter}")
        target_length = request.get("target_length", 500)
        
        # Définir les prompts spécialisés pour chaque rubrique
        rubrique_prompts = {
            1: f"""
PRIÈRE D'OUVERTURE THÉOLOGIQUE pour {passage}

MISSION : Rédiger une prière d'ouverture digne des plus grandes traditions monastiques et académiques, spécifiquement pour l'étude de {passage}, dans un style narratif biblique inspiré des Écritures.

STYLE NARRATIF EXIGÉ :
- Ton solennel et révérencieux, à la manière des prières de l'Ancien Testament
- Prose biblique fluide avec rythme et cadence liturgique  
- Vocabulaire théologique précis mais accessible
- Transitions naturelles entre les sections de prière
- Explication naturelle des termes théologiques complexes dans le flux narratif

STRUCTURE THÉOLOGIQUE APPROFONDIE :

**I. ADORATION TRINITAIRE :**
Élévation vers le Père, contemplation du Fils révélé dans {passage}, invocation du Saint-Esprit. Utiliser le vocabulaire des attributs divins (omniscience, omnipotence, omniprésence) en expliquant naturellement leur signification.

**II. CONFESSION PÉNITENTIELLE :**
Reconnaissance humble de notre condition pécheresse face à la sainteté révélée dans {passage}. Employer les concepts de justification, sanctification et régénération en expliquant leur sens spirituel.

**III. SUPPLICATION ÉCLAIRANTE :**
Demande d'illumination herméneutique pour saisir les vérités théologiques de {passage}. Invoquer les dons spirituels de sagesse (sophia), connaissance (gnosis) et discernement (diakrisis) - expliquer ces termes grecs dans le contexte.

**IV. INTERCESSION ECCLÉSIALE :**
Prière pour l'Église universelle et locale à la lumière des enseignements de {passage}. Inclure les concepts d'ecclésiologie (étude de l'Église), koinonia (communion fraternelle) et diakonia (service).

DIRECTIVES ACADÉMIQUES :
- Intégrer naturellement 8-10 termes théologiques précis avec leurs explications subtiles
- Références croisées avec d'autres passages bibliques pertinents
- Perspective herméneutique évangélique réformée
- Longueur : {target_length} mots de substance théologique
- Inclure des formulations liturgiques traditionnelles ("Que ton nom soit sanctifié", "Selon ta volonté divine")
- Conclure par des "Amen" appropriés selon la tradition chrétienne

OBJECTIF : Créer une prière qui élève l'âme, instruit l'esprit et prépare le cœur à une étude biblique de niveau académique supérieur, digne d'une école de théologie renommée.
""",
            2: f"""
STRUCTURE ET PLAN LITTÉRAIRE de {passage}

MISSION : Analyser la structure littéraire de {passage} comme un maître narrateur biblique révélant les beautés architecturales du texte sacré.

APPROCHE NARRATIVE EXIGÉE :
- Raconter l'analyse comme une découverte progressive des trésors littéraires
- Style vivant et captivant, digne des plus grands exégètes narratifs
- Explications claires des termes techniques (chiasme, parallélisme, inclusio)
- Métaphores architecturales pour décrire la structure du texte

ANALYSE NARRATIVE APPROFONDIE :

**I. L'ARCHITECTURE DIVINE DU TEXTE :**
Découvrez comment l'Esprit Saint a inspiré une structure parfaite dans {passage}. Le parallélisme hébraïque (technique poétique où les idées se répondent en écho) révèle la symétrie divine. L'inclusio (répétition d'un même élément au début et à la fin) forme les colonnes de ce temple littéraire.

**II. LA PROGRESSION NARRATIVE INSPIRÉE :**
Suivez le fil d'or de la révélation qui traverse {passage}. Chaque verset s'enchaîne selon la logique divine, créant une crescendo théologique (montée progressive vers le climax spirituel). Les connecteurs logiques hébreux (waw consécutif, particules emphatiques) tissent cette tapisserie sacrée.

**III. LES MOTS-CLÉS COMME JOYAUX :**
Découvrez les termes hébreux/grecs récurrents qui scintillent à travers {passage}. Ces Leitworte (mots conducteurs allemands) forment les fils d'or du texte, créant unité et emphasis. Chaque répétition révèle une intention divine.

**IV. LES SCHÉMAS LITTÉRAIRES CACHÉS :**
Explorez les chiasmes (structures en miroir A-B-C-B'-A') qui révèlent le centre théologique du passage. L'anaphore (répétition en début de phrase) et l'épiphore (répétition en fin) créent le rythme sacré de la révélation.

DIRECTIVES ACADÉMIQUES :
- Analyse précise du texte hébreu/grec original quand pertinent
- {target_length} mots d'analyse narrative captivante
- Schémas visuels avec indentation poétique
- Références aux commentaires de Calvin, Luther, Spurgeon
- Applications herméneutiques pratiques pour la prédication

Révélez la beauté littéraire divine spécifique à {passage}, pas des généralités sur {book}.
""",
            3: f"""
CONTEXTE DU CHAPITRE PRÉCÉDENT pour {passage}

MISSION : Raconter comme un chroniqueur biblique comment le chapitre précédent prépare et illumine {passage} dans le grand récit de la rédemption.

APPROCHE NARRATIVE HISTORIQUE :
- Style de chronique biblique, à la manière des livres historiques
- Transitions fluides montrant la continuité divine
- Explications des termes théologiques (économie du salut, progression révélationnelle)
- Perspective de l'histoire sainte (Heilsgeschichte)

CHRONIQUE CONTEXTUELLE INSPIRÉE :

**I. RÉCAPITULATIF DU CHAPITRE PRÉCÉDENT :**
Dans les pages précédentes de cette épopée sacrée, l'Éternel avait orchestré... [Résumé narratif vivant du chapitre {int(chapter)-1 if chapter.isdigit() else "précédent"} de {book}]. Ces événements forment la toile de fond providentiellement préparée pour {passage}.

**II. LES FILS PROVIDENTIELS ENTRELACÉS :**
Observez comment la main divine a tissé les événements précédents pour préparer cette nouvelle révélation. La typologie biblique (préfiguration où les événements anciens annoncent les réalités futures) se déploie majestueusement. L'économie du salut (plan divin de rédemption) progresse selon le dessein éternel.

**III. PROGRESSION DE LA RÉVÉLATION DIVINE :**
Le principe de la révélation progressive (revelatio progressiva) se manifeste brillamment ici. Chaque vérité révélée précédemment éclaire {passage} d'une lumière nouvelle. L'herméneutique canonique nous enseigne que l'Écriture s'interprète par l'Écriture.

**IV. CONTINUITÉ DES PERSONNAGES ET THÈMES :**
Les protagonistes de cette histoire sainte poursuivent leur pèlerinage spirituel. Leurs caractères se développent, leurs foi grandit ou vacille, révélant les vérités éternelles sur la nature humaine et la grâce divine.

**V. IMPLICATIONS THÉOLOGIQUES TRANSFORMATRICES :**
Cette progression narrative révèle des vérités profondes sur les attributs divins : sa fidélité (hesed), sa justice (tsedek), sa miséricorde (rachamim). Ces termes hébreux résonnent à travers l'histoire pour culminer dans {passage}.

DIRECTIVES ACADÉMIQUES :
- Focus narratif sur {book} chapitre {int(chapter)-1 if chapter.isdigit() else "précédent"} spécifiquement
- {target_length} mots de chronique contextuelle captivante
- Citations des versets pertinents du chapitre précédent avec références exactes
- Éviter les généralités, raconter l'histoire spécifique
- Perspective canonique et rédemptionnelle

Révélez concrètement comment le contexte précédent enrichit dramatiquement {passage} dans le grand récit divin.
""",
            4: f"""
MOTS DIFFICILES ET EXPLICATION pour {passage}

MISSION : Devenir un guide linguistique narratif, expliquant les termes complexes de {passage} comme un sage exégète partageant des trésors lexicaux.

APPROCHE PÉDAGOGIQUE NARRATIVE :
- Style de maître enseignant dévoilant des mystères linguistiques
- Explications progressives du simple au complexe
- Étymologies hébraïques/grecques racontées comme des découvertes
- Applications contemporaines des concepts anciens

EXPLORATION LEXICALE INSPIRÉE :

**I. TRÉSOR LINGUISTIQUE PRINCIPAL :**
Au cœur de {passage} brillent des gemmes lexicales d'une richesse inouïe. Chaque terme hébreu/grec porte en lui des siècles de révélation divine. L'herméneutique lexicale (étude approfondie des mots) nous révèle des nuances perdues dans nos traductions modernes.

**II. TERMES THÉOLOGIQUES MAJEURS :**
Découvrons ensemble les concepts-clés qui structurent ce passage :
- Les termes de l'alliance (berith, diatheke) qui révèlent les relations divines
- Le vocabulaire sacrificiel (korban, thusia) qui préfigure la rédemption
- Les mots de la sainteté (qadosh, hagios) qui définissent la nature divine
[Adaptation spécifique aux termes présents dans {passage}]

**III. DIFFICULTÉS CULTURELLES CONTEXTUALISÉES :**
Plongeons dans l'univers biblique pour comprendre :
- Les réalités socio-culturelles qui éclairent certaines expressions
- Les idiomes hébreux (hébraïsmes) qui déroutent nos mentalités modernes
- Les concepts juridiques et cultuels de l'époque biblique
- Les métaphores agricoles, pastorales, guerrières selon le contexte

**IV. NUANCES GRAMMATICALES RÉVÉLATRICES :**
La syntaxe hébraïque/grecque révèle des subtilités divines :
- Les temps verbaux hébreux (accompli/inaccompli) qui transcendent nos catégories temporelles
- Les constructions emphatiques (infinitif absolu, génitif de qualité)
- Les jeux de mots (paronomases) qui révèlent l'intention prophétique

**V. APPLICATIONS TRANSFORMATRICES :**
Ces découvertes linguistiques illuminent notre compréhension contemporaine. Chaque terme correctement compris enrichit notre vie spirituelle et notre témoignage chrétien.

DIRECTIVES ACADÉMIQUES :
- Analyse lexicale spécifique aux mots effectivement présents dans {passage}
- {target_length} mots d'exploration linguistique narrative
- Références aux dictionnaires théologiques (TDNT, TDOT, BDB)
- Applications pratiques pour la prédication et l'étude personnelle
- Niveau académique accessible au chrétien cultivé

Révélez les trésors linguistiques cachés spécifiquement dans {passage}, transformant l'étude en aventure lexicale captivante.
""",
            5: f"""
GÉOGRAPHIE ET LIEUX pour {passage}

MISSION : Transporter le lecteur dans les paysages bibliques de {passage}, révélant comment la géographie sacrée illumine le texte divin.

APPROCHE GÉOGRAPHIQUE NARRATIVE :
- Style de guide-explorateur des terres bibliques
- Descriptions vivantes des paysages et leur signification spirituelle
- Explications des termes géographiques (topographie, archéologie biblique)
- Connexions entre géographie physique et vérités spirituelles

VOYAGE GÉOGRAPHIQUE INSPIRÉ :

**I. EXPLORATION DU THÉÂTRE BIBLIQUE :**
Embarquons pour les lieux sacrés de {passage}. La géographie biblique n'est jamais accidentelle ; l'Éternel a choisi ces décors pour révéler ses vérités éternelles. Chaque montagne, vallée, désert, ville porte une signification théologique (la topographie comme théophanie).

**II. PAYSAGES ET LEUR SYMBOLISME DIVIN :**
Découvrons les lieux mentionnés dans {passage} :
- Les montagnes (har, oros) : lieux de révélation, de rencontre avec Dieu
- Les vallées (emek, koilas) : symboles d'humiliation ou de fertilité spirituelle  
- Les déserts (midbar, eremos) : espaces de purification et d'épreuve
- Les eaux (mayim, hydor) : sources de vie, purification, jugement
[Adaptation aux lieux réellement mentionnés dans {passage}]

**III. CONTEXTE ARCHÉOLOGIQUE ÉCLAIRANT :**
L'archéologie biblique révèle les réalités concrètes derrière {passage}. Les découvertes récentes confirment et enrichissent notre compréhension du texte sacré. Chaque tessons, inscription, fondation dévoile l'historicité de la Parole divine.

**IV. ROUTES ET CHEMINS PROVIDENTIELS :**
Suivons les itinéraires divins à travers {passage}. Les voies commerciales, pèlerinages, exodes révèlent comment Dieu orchestre l'histoire. La géographie devient prophétie, chaque déplacement portant une signification rédemptionnelle.

**V. CLIMAT ET SAISONS SPIRITUELLES :**
Le climat palestinien (saison sèche/pluvieuse, vents, températures) influence profondément les métaphores bibliques. Comprendre ces réalités météorologiques dévoile des richesses herméneutiques insoupçonnées dans {passage}.

**VI. APPLICATIONS CONTEMPORAINES :**
Ces paysages bibliques parlent encore aujourd'hui. Ils nous enseignent sur notre propre géographie spirituelle : nos montagnes de communion, nos vallées d'épreuve, nos déserts de formation.

DIRECTIVES ACADÉMIQUES :
- Focus géographique sur les lieux réellement mentionnés dans {passage}
- {target_length} mots d'exploration géographique narrative
- Références aux atlas bibliques, guides archéologiques
- Cartes mentales et descriptions topographiques précises
- Applications spirituelles des réalités géographiques

Révélez comment la géographie sacrée de {passage} enrichit dramatiquement sa compréhension théologique et spirituelle.
""",
            6: f"""
COUTUMES ET MENTALITÉ pour {passage}

MISSION : Plonger dans l'univers culturel de {passage}, révélant comment les coutumes antiques éclairent les vérités éternelles.

APPROCHE ANTHROPOLOGIQUE NARRATIVE :
- Style d'ethnographe biblique explorant les civilisations anciennes
- Descriptions vivantes des pratiques sociales et leur signification spirituelle
- Explications des termes culturels (anthropologie biblique, sociologie hébraïque)
- Passerelles entre mentalités antiques et contemporaines

IMMERSION CULTURELLE INSPIRÉE :

**I. PLONGÉE DANS LA MENTALITÉ HÉBRAÏQUE/GRECQUE :**
Entrons dans l'univers mental des contemporains de {passage}. La pensée sémitique (mode de pensée hébraïque holistique) diffère fondamentalement de notre logique grecque analytique. Cette mentalité orientale privilégie le concret sur l'abstrait, l'expérientiel sur le conceptuel.

**II. STRUCTURES SOCIALES ET FAMILIALES :**
Découvrons l'organisation sociale qui donne sens à {passage} :
- Le système patriarcal et ses implications théologiques
- Les liens de parenté (clan, tribu) et solidarité communautaire
- Les rôles masculins/féminins selon l'ordre créationnel divin
- L'économie domestique et ses métaphores spirituelles
[Adaptation aux structures réellement pertinentes pour {passage}]

**III. COUTUMES RELIGIEUSES ET CULTUELLES :**
Explorons les pratiques spirituelles qui éclairent {passage} :
- Les rituels de purification (niddah, katharsis) et leur symbolisme
- Les fêtes et calendrier liturgique (moed, heorte) et leur prophétisme
- Les sacrifices et offrandes (korban, prosphora) et leur typologie christologique
- Les lieux de culte (mishkan, naos) et leur architecture symbolique

**IV. CODES D'HONNEUR ET DE HONTE :**
Comprenons les valeurs fondamentales qui régissent les comportements dans {passage}. La culture méditerranéenne antique fonctionne sur les concepts d'honneur (kavod, doxa) et de honte (bosheth, aischros), éclairant de nombreux passages énigmatiques.

**V. PRATIQUES COMMERCIALES ET JURIDIQUES :**
Décryptons les réalités économiques et légales :
- Les contrats et alliances (berith, diatheke) selon les codes anciens
- Le système monétaire, poids et mesures bibliques
- Les pratiques agricoles et pastorales métaphorisées
- Les coutumes juridiques (témoignage, jugement, châtiment)

**VI. HOSPITALITÉ ET RELATIONS SOCIALES :**
L'hospitalité orientale (philoxenia) révèle des dimensions spirituelles profondes. Les codes de politesse, salutations, repas communautaires portent une signification théologique dans {passage}.

**VII. APPLICATIONS TRANSFORMATRICES :**
Cette immersion culturelle transforme notre lecture contemporaine. Elle nous aide à distinguer les principes éternels des expressions culturelles temporaires, enrichissant notre herméneutique contextuelle.

DIRECTIVES ACADÉMIQUES :
- Focus culturel sur les coutumes réellement pertinentes pour {passage}
- {target_length} mots d'exploration anthropologique narrative
- Références aux études culturelles bibliques (de Vaux, Malina, Pilch)
- Applications herméneutiques pour l'actualisation du texte
- Respect de la diversité culturelle tout en affirmant les vérités universelles

Révélez comment l'univers culturel de {passage} enrichit dramatiquement sa compréhension théologique et son application contemporaine.
""",
            7: f"""
HISTOIRE ET CHRONOLOGIE pour {passage}

MISSION : Devenir un chroniqueur de l'histoire sainte, situant {passage} dans le grand récit de la rédemption divine.

APPROCHE CHRONOLOGIQUE NARRATIVE :
- Style de chroniqueur biblique relatant l'épopée divine
- Contextualisation historique vivante et précise
- Explications des termes chronologiques (ères bibliques, périodes deutérocanoniques)
- Vision de l'histoire comme théâtre de la providence divine

CHRONIQUE HISTORIQUE INSPIRÉE :

**I. SITUATION DANS L'HISTOIRE SAINTE :**
Situons {passage} sur la timeline divine de la rédemption. L'Heilsgeschichte (histoire du salut) se déroule selon le dessein éternel, chaque époque préparant la suivante dans l'économie divine. Voici où s'inscrit notre passage dans cette chronologie sacrée.

**II. CONTEXTE POLITIQUE ET SOCIAL :**
Explorons les réalités historiques contemporaines de {passage} :
- Les empires en présence et leurs implications prophétiques
- Les dynamiques géopolitiques révélant la souveraineté divine
- Les personnages historiques et leur rôle dans le plan divin
- L'état spirituel du peuple de Dieu à cette époque

**III. ARRIÈRE-PLAN RELIGIEUX :**
Découvrons le climat spirituel de l'époque :
- L'évolution de la révélation progressive jusqu'à {passage}
- Les institutions religieuses et leur fidélité/infidélité
- Les courants théologiques et mouvements spirituels
- La préparation providentielle pour les événements de {passage}

**IV. SYNCHRONISMES PROPHÉTIQUES :**
Observons comment {passage} s'inscrit dans les prophéties bibliques. Les synchronismes divins révèlent l'orchestration parfaite de l'histoire par l'Éternel. Chaque "coïncidence" historique manifeste la providence souveraine.

**V. IMPLICATIONS ESCHATOLOGIQUES :**
Comprenons comment {passage} préfigure ou accomplit les promesses messianiques. L'eschatologie réalisée et l'eschatologie future s'articulent dans cette perspective historique rédemptionnelle.

DIRECTIVES ACADÉMIQUES :
- Chronologie précise basée sur les données bibliques et archéologiques
- {target_length} mots d'analyse historique narrative
- Références aux chronologies bibliques établies
- Applications typologiques et prophétiques appropriées

Révélez comment le contexte historique de {passage} magnifie sa signification rédemptionnelle dans l'épopée divine.
""",
            8: f"""
PERSONNAGES PRINCIPAUX pour {passage}

MISSION : Dresser les portraits narratifs des protagonistes de {passage}, révélant leurs caractères comme miroirs de vérités spirituelles éternelles.

APPROCHE BIOGRAPHIQUE NARRATIVE :
- Style de portraitiste biblique saisissant les âmes
- Analyses psychologiques et spirituelles approfondies
- Explications des termes caractérologiques (typologie biblique, développement spirituel)
- Applications contemporaines des caractères bibliques

GALERIE DE PORTRAITS INSPIRÉS :

**I. PROTAGONISTES DIVINS ET HUMAINS :**
Rencontrons les acteurs principaux de {passage}. Chaque personnage biblique porte en lui des vérités universelles sur la nature humaine et divine. L'anthropologie biblique révèle comment ces figures historiques deviennent des types spirituels pour tous les temps.

**II. CARACTÈRES ET TEMPÉRAMENTS RÉVÉLÉS :**
Analysons les personnalités complexes dévoilées dans {passage} :
- Leurs motivations profondes et conflits intérieurs
- Leur croissance ou déclin spirituel
- Leurs forces et faiblesses caractérologiques
- Leur rôle dans l'économie rédemptionnelle

**III. DÉVELOPPEMENT SPIRITUEL ET MORAL :**
Suivons l'évolution des personnages à travers {passage}. La sanctification progressive (croissance en sainteté) ou la déchéance spirituelle (apostasie) révèlent les lois morales du royaume divin.

**IV. TYPOLOGIE CHRISTOLOGIQUE :**
Découvrons comment certains personnages préfigurent le Christ (typologie positive) ou l'antichrist (typologie négative). Ces ombres et reflets enrichissent notre compréhension messianique.

**V. LEÇONS CARACTÉROLOGIQUES CONTEMPORAINES :**
Ces portraits anciens parlent aujourd'hui. Ils nous enseignent sur nos propres tendances, tentations, vocations spirituelles et transformations possibles par la grâce divine.

DIRECTIVES ACADÉMIQUES :
- Focus sur les personnages réellement présents dans {passage}
- {target_length} mots d'analyse caractérologique narrative
- Références aux études bibliques caractérologiques
- Applications pastorales et d'édification personnelle

Révélez comment les personnages de {passage} deviennent des miroirs transformateurs pour notre propre pèlerinage spirituel.
""",
            9: f"""
ÉTUDE DES MOTS-CLÉS pour {passage}

MISSION : Devenir un orfèvre des mots sacrés, ciselant chaque terme-clé de {passage} pour révéler ses facettes spirituelles multiples.

APPROCHE LEXICOGRAPHIQUE NARRATIVE :
- Style d'orfèvre linguistique polissant les gemmes lexicales
- Analyse sémantique approfondie et évolutive
- Explications des termes techniques (champ sémantique, polysémie, métonymie)
- Applications herméneutiques transformatrices

ATELIER LEXICAL INSPIRÉ :

**I. IDENTIFICATION DES GEMMES LEXICALES :**
Sélectionnons les mots-clés qui scintillent dans {passage}. Ces termes répétés, emphasisés, ou théologiquement chargés forment l'ossature conceptuelle du texte. La lexicographie biblique révèle leurs richesses cachées.

**II. ANALYSE ÉTYMOLOGIQUE RÉVÉLATRICE :**
Remontons aux racines hébraïques/grecques de chaque mot-clé :
- Leurs origines étymologiques et évolutions sémantiques
- Leurs occurrences dans l'ensemble du canon biblique
- Leurs champs sémantiques et connotations théologiques
- Leurs traductions et leurs limites dans nos versions modernes

**III. DÉVELOPPEMENT CANONIQUE :**
Suivons l'évolution de ces concepts à travers l'Écriture. La révélation progressive enrichit progressivement le sens de chaque terme, culminant dans la révélation néotestamentaire et christologique.

**IV. RÉSONANCES THÉOLOGIQUES :**
Découvrons comment ces mots-clés révèlent des doctrines fondamentales :
- Leur contribution à la théologie systématique
- Leur rôle dans l'herméneutique biblique
- Leur signification sotériologique et eschatologique

**V. APPLICATIONS TRANSFORMATRICES :**
Ces découvertes lexicales transforment notre compréhension spirituelle. Chaque nuance correctement saisie enrichit notre communion avec Dieu et notre témoignage chrétien.

DIRECTIVES ACADÉMIQUES :
- Focus sur les mots-clés réellement présents et significatifs dans {passage}
- {target_length} mots d'analyse lexicale narrative captivante
- Références aux concordances et dictionnaires théologiques
- Applications pratiques pour l'étude et la prédication

Révélez comment les mots-clés de {passage} deviennent des clés d'or ouvrant les trésors divins cachés dans le texte sacré.
""",
            10: f"""
CONTEXTE DU LIVRE pour {passage}

MISSION : Situer {passage} dans l'architecture globale de {book}, révélant sa fonction organique dans l'œuvre littéraire et théologique complète.

APPROCHE ARCHITECTURALE NARRATIVE :
- Style d'architecte littéraire explorant l'édifice biblique
- Vision d'ensemble puis focus spécifique sur {passage}
- Explications des termes structuraux (macrostructure, péricope, unité littéraire)
- Compréhension organique du dessein éditorial divin

EXPLORATION ARCHITECTURALE INSPIRÉE :

**I. VISION PANORAMIQUE DE {book} :**
Contemplons d'abord l'ensemble majestueux de {book}. Chaque livre biblique forme un édifice littéraire parfait, orchestré par l'Esprit Saint. Découvrons le thème central, la progression argumentative, et l'objectif théologique de cette œuvre inspirée.

**II. DIVISION CANONIQUE ET LITTÉRAIRE :**
Explorons la structure globale de {book} :
- Ses grandes sections thématiques et narratives
- Sa progression théologique et révélationnelle  
- Ses techniques littéraires caractéristiques
- Sa place dans le canon biblique (Torah, Neviim, Ketuvim, ou corpus paulinien, etc.)

**III. POSITION STRATÉGIQUE DE {passage} :**
Situons précisément {passage} dans cette architecture :
- Sa fonction dans la progression du livre
- Ses connexions avec les passages antérieurs et postérieurs
- Son rôle dans le développement thématique global
- Sa contribution à l'objectif théologique général

**IV. RÉSONNANCES INTRA-CANONIQUES :**
Découvrons comment {passage} dialogue avec le reste de {book} :
- Les échos thématiques et lexicaux
- Les développements progressifs des concepts
- Les préparations et accomplissements internes
- L'unité littéraire et théologique du livre complet

**V. APPLICATIONS HERMÉNEUTIQUES :**
Cette compréhension contextuelle transforme notre interprétation. Elle nous garde de l'atomisation exégétique et enrichit notre saisie de l'intention divine globale.

DIRECTIVES ACADÉMIQUES :
- Analyse contextuelle spécifique à la structure réelle de {book}
- {target_length} mots d'exploration architecturale narrative
- Références aux introductions et commentaires de {book}
- Applications pour la compréhension globale et la prédication séquentielle

Révélez comment {passage} s'épanouit pleinement quand on comprend sa place organique dans l'ensemble inspiré de {book}.
""",
            11: f"""
DOCTRINE ENSEIGNÉE pour {passage}

MISSION : Devenir un théologien systématique narratif, extrayant et exposant les vérités doctrinales que {passage} révèle dans le grand système de la foi chrétienne.

APPROCHE DOCTRINALE NARRATIVE :
- Style de maître théologien tissant les vérités éternelles
- Systématisation biblique rigoureuse et accessible
- Explications des termes doctrinaux (sotériologie, pneumatologie, eschatologie)
- Applications transformatrices des vérités révélées

TRAITÉ DOCTRINAL INSPIRÉ :

**I. IDENTIFICATION DES VÉRITÉS CENTRALES :**
Extrayons les gemmes doctrinales que {passage} révèle. Chaque texte biblique contribue à l'édifice de la théologie systématique. Découvrons quelles doctrines fondamentales s'épanouissent dans ce passage sacré.

**II. THÉOLOGIE PROPRE (DOCTRINE DE DIEU) :**
Explorons ce que {passage} révèle sur la nature divine :
- Les attributs de Dieu manifestés (omniscience, omnipotence, sainteté)
- Les relations trinitaires révélées ou implicites
- La souveraineté divine et son exercice providentiel
- Les noms divins et leurs significations théologiques

**III. CHRISTOLOGIE ET SOTÉRIOLOGIE :**
Découvrons les vérités sur le Christ et le salut :
- Les préfigurations messianiques ou accomplissements christologiques
- Les aspects de l'œuvre rédemptrice révélés
- La justification, sanctification, glorification enseignées
- L'union mystique avec Christ manifestée

**IV. PNEUMATOLOGIE ET ECCLESIOLOGIE :**
Analysons l'enseignement sur l'Esprit et l'Église :
- L'œuvre du Saint-Esprit révélée dans {passage}
- Les vérités sur l'Église visible et invisible
- Les moyens de grâce et leur administration
- La communion des saints et ses implications

**V. ESCHATOLOGIE ET ÉTHIQUE :**
Explorons les enseignements sur les fins dernières et la conduite chrétienne :
- Les aspects du royaume de Dieu révélés
- Les vérités sur la résurrection, jugement, vie éternelle
- Les implications éthiques et morales du passage
- Les applications pratiques pour la sanctification

**VI. APPLICATIONS PASTORALES :**
Ces vérités doctrinales transforment la vie chrétienne. Elles fortifient la foi, dirigent la conduite, consolent dans l'épreuve, et équipent pour le témoignage.

DIRECTIVES ACADÉMIQUES :
- Extraction doctrinale rigoureuse basée sur {passage} spécifiquement
- {target_length} mots de théologie systématique narrative
- Références aux confessions de foi historiques (Westminster, Augsbourg, etc.)
- Applications pastorales et d'édification spirituelle

Révélez comment {passage} enrichit notre compréhension du système doctrinal chrétien et transforme notre vie de foi.
""",
            12: f"""
APPLICATIONS PRATIQUES pour {passage}

MISSION : Devenir un guide spirituel pratique, construisant des ponts solides entre les vérités éternelles de {passage} et la vie chrétienne contemporaine.

APPROCHE APPLICATIVE NARRATIVE :
- Style de directeur spirituel sage et expérimenté
- Actualisation contextuelle respectueuse du texte
- Explications des principes herméneutiques (principe/application, contextualisation)
- Transformations concrètes et réalisables

GUIDE SPIRITUEL INSPIRÉ :

**I. PRINCIPES ÉTERNELS ET APPLICATIONS TEMPORELLES :**
Distinguons soigneusement entre les principes transculturels de {passage} et leurs expressions culturelles spécifiques. L'herméneutique contextuelle nous guide pour actualiser fidèlement sans dénaturer le message divin.

**II. APPLICATIONS POUR LA VIE PERSONNELLE :**
Découvrons comment {passage} transforme notre marche individuelle avec Dieu :
- Croissance spirituelle et disciplines de la grâce
- Combat contre le péché et poursuite de la sainteté
- Développement du caractère chrétien et des vertus spirituelles
- Approfondissement de la communion avec le Père, le Fils et le Saint-Esprit

**III. IMPLICATIONS FAMILIALES ET RELATIONNELLES :**
Explorons les transformations que {passage} opère dans nos relations :
- Rapports conjugaux selon l'ordre créationnel et rédemptif
- Éducation chrétienne des enfants et transmission de la foi
- Relations fraternelles dans la communauté de foi
- Témoignage chrétien dans les cercles non-chrétiens

**IV. APPLICATIONS ECCLÉSIASTIQUES :**
Analysons l'impact de {passage} sur la vie d'Église :
- Adoration, prédication, enseignement transformés
- Exercice des dons spirituels et ministères
- Discipline ecclésiastique et restauration
- Mission et évangélisation inspirées par ces vérités

**V. IMPLICATIONS SOCIALES ET CULTURELLES :**
Découvrons comment {passage} influence notre engagement dans la société :
- Éthique chrétienne face aux défis contemporains
- Justice sociale et compassion évangélique
- Transformation culturelle par l'Évangile
- Citoyenneté terrestre à la lumière de la citoyenneté céleste

**VI. APPLICATIONS ESCHATOLOGIQUES :**
Vivons dès maintenant à la lumière des réalités futures révélées dans {passage}. L'espérance chrétienne transforme notre perspective présente et notre engagement temporal.

DIRECTIVES ACADÉMIQUES :
- Applications authentiquement dérivées de {passage} spécifiquement
- {target_length} mots de guidance spirituelle narrative
- Équilibre entre fidélité exégétique et pertinence contemporaine
- Sagesse pastorale et discernement spirituel

Révélez comment les vérités éternelles de {passage} transforment concrètement chaque dimension de l'existence chrétienne contemporaine.
""",
            13: f"""
TYPES ET SYMBOLES pour {passage}

MISSION : Devenir un herméneute typologique, dévoilant les ombres et reflets de Christ cachés dans {passage}, révélant la beauté de la pédagogie divine.

APPROCHE TYPOLOGIQUE NARRATIVE :
- Style de détective spirituel découvrant les mystères christologiques
- Herméneutique typologique rigoureuse et respectueuse
- Explications des termes typologiques (type, antitype, allégorie, symbole)
- Révélations progressives culminant dans le Christ

EXPLORATION TYPOLOGIQUE INSPIRÉE :

**I. FONDEMENTS DE LA TYPOLOGIE BIBLIQUE :**
Pénétrons dans l'art divin de la préfiguration. La typologie biblique révèle comment l'Ancien Testament dessine les contours du Nouveau. Dans {passage}, l'Esprit Saint a tissé des ombres prophétiques qui trouvent leur substance en Christ.

**II. TYPES PERSONNELS CHRISTOLOGIQUES :**
Découvrons les personnages de {passage} qui préfigurent le Messie :
- Leurs rôles de prophètes, sacrificateurs, rois annonçant Christ
- Leurs expériences d'humiliation et d'exaltation reflétant la Pâque du Seigneur
- Leurs œuvres de délivrance, médiation, jugement préparant l'œuvre parfaite
- Leurs imperfections révélant la nécessité du Médiateur parfait

**III. TYPES INSTITUTIONNELS ET RITUELS :**
Explorons les institutions divines qui préfigurent les réalités évangéliques :
- Les sacrifices et leur accomplissement dans l'œuvre expiatoire
- Les fêtes et leurs significations prophétiques réalisées
- Le sacerdoce et sa perfection dans le grand Souverain Sacrificateur
- Les lieux saints et leur réalisation dans le sanctuaire céleste

**IV. SYMBOLES ET MÉTAPHORES RÉVÉLATRICES :**
Analysons le langage symbolique qui révèle les vérités spirituelles :
- Les éléments naturels (eau, feu, lumière) et leurs significations spirituelles
- Les objets cultuels et leur symbolisme christologique
- Les nombres sacrés et leur signification théologique
- Les couleurs, matériaux, formes et leurs messages divins

**V. PROGRESSION RÉVÉLATIONNELLE :**
Suivons comment {passage} s'inscrit dans la pédagogie divine progressive. Chaque type prépare une révélation plus complète, culminant dans l'Incarnation et l'œuvre parfaite du Christ.

**VI. APPLICATIONS SPIRITUELLES CONTEMPORAINES :**
Ces types anciens parlent encore aujourd'hui. Ils enrichissent notre compréhension christologique, notre adoration, et notre espérance eschatologique.

DIRECTIVES ACADÉMIQUES :
- Typologie authentique basée sur les correspondances réelles dans {passage}
- {target_length} mots d'exploration typologique narrative
- Respect de l'herméneutique évangélique et des analogies scripturaires
- Applications christocentriques et édifiantes

Révélez comment {passage} devient une fenêtre ouverte sur la beauté du Christ, transformant notre contemplation du Sauveur.
""",
            14: f"""
PROPHÉTIES ET ACCOMPLISSEMENTS pour {passage}

MISSION : Devenir un prophétologue narratif, traçant les fils d'or prophétiques qui traversent {passage} et révèlent l'orchestration divine de l'histoire.

APPROCHE PROPHÉTOLOGIQUE NARRATIVE :
- Style de chroniqueur prophétique dévoilant les mystères divins
- Herméneutique prophétique équilibrée et biblique
- Explications des termes prophétiques (vaticinium ex eventu, typologie prophétique, eschatologie)
- Révélations de la souveraineté divine sur l'histoire

CHRONIQUE PROPHÉTIQUE INSPIRÉE :

**I. NATURE DE LA PROPHÉTIE BIBLIQUE :**
Pénétrons dans l'art divin de la prédiction. La prophétie biblique révèle comment l'Éternel annonce l'avenir pour fortifier la foi et diriger la conduite. Dans {passage}, découvrons les oracles divins et leur accomplissement providentiel.

**II. PROPHÉTIES MESSIANIQUES :**
Explorons les annonces du Christ dans {passage} :
- Prophéties directes concernant la personne du Messie
- Prédictions sur son œuvre rédemptrice (naissance, ministère, mort, résurrection)
- Annonces de son règne et de sa gloire eschatologique
- Chronologie prophétique et ses accomplissements historiques

**III. PROPHÉTIES CONCERNANT ISRAËL :**
Analysons les oracles sur le peuple élu :
- Promesses d'alliance et leurs accomplissements progressifs
- Prédictions d'exil, restauration, et destinée finale
- Prophéties sur la terre promise et Jérusalem
- Rôle prophétique d'Israël dans l'économie divine

**IV. PROPHÉTIES DES NATIONS :**
Découvrons les oracles concernant les gentils :
- Jugements annoncés et leurs accomplissements historiques
- Promesses d'inclusion dans l'alliance abrahamique
- Rôle des empires dans le plan divin
- Destinée eschatologique des nations

**V. PROPHÉTIES ESCHATOLOGIQUES :**
Explorons les révélations sur les fins dernières :
- Signes des temps et leur identification contemporaine
- Événements de la Parousie et du royaume millénaire
- Résurrection, jugement final, nouveaux cieux et nouvelle terre
- Chronologie prophétique et ses interprétations équilibrées

**VI. HERMÉNEUTIQUE PROPHÉTIQUE ÉQUILIBRÉE :**
Appliquons une interprétation prophétique fidèle, évitant les excès du littéralisme rigide et de l'allégorisme excessif. La règle d'or : l'Écriture s'interprète par l'Écriture.

DIRECTIVES ACADÉMIQUES :
- Focus sur les prophéties réellement présentes dans {passage}
- {target_length} mots d'analyse prophétologique narrative
- Références aux accomplissements bibliques et historiques vérifiables
- Éviter les spéculations non-fondées et les dates précises

Révélez comment les prophéties de {passage} manifestent la fidélité divine et fortifient notre espérance chrétienne.
""",
            15: f"""
PARALLÈLES BIBLIQUES pour {passage}

MISSION : Devenir un harmoniste scripturaire, tissant les connexions divines entre {passage} et l'ensemble du canon, révélant l'unité organique de la révélation.

APPROCHE CANONIQUE NARRATIVE :
- Style de bibliothécaire divin explorant les correspondances sacrées
- Herméneutique canonique et analogie de l'Écriture
- Explications des principes d'intertextualité biblique (citation, allusion, écho)
- Révélation de l'harmonie divine progressive

EXPLORATION HARMONIQUE INSPIRÉE :

**I. PRINCIPE DE L'ANALOGIE SCRIPTURAIRE :**
Pénétrons dans l'art divin de l'auto-interprétation biblique. L'Écriture est son propre interprète (Scriptura sui ipsius interpres). Dans {passage}, découvrons les échos, correspondances et développements qui résonnent à travers tout le canon.

**II. PARALLÈLES THÉMATIQUES DIRECTS :**
Explorons les passages qui traitent des mêmes sujets que {passage} :
- Textes parallèles dans les évangiles synoptiques ou récits historiques
- Développements thématiques à travers l'Ancien et le Nouveau Testament
- Progressions doctrinales du prototype à l'accomplissement
- Correspondances entre promesses et réalisations

**III. ÉCHOS LEXICAUX ET CONCEPTUELS :**
Analysons les réseaux de mots et concepts qui relient {passage} au reste de l'Écriture :
- Termes-clés récurrents et leur développement sémantique
- Métaphores et images qui traversent le canon
- Concepts théologiques et leur maturation progressive
- Formules liturgiques et leur usage canonique

**IV. CITATIONS ET ALLUSIONS INTERTEXTUELLES :**
Découvrons comment {passage} cite ou fait écho à d'autres textes bibliques :
- Citations explicites et leur contexte d'origine
- Allusions subtiles et leur enrichissement mutuel
- Réinterprétations créatives sous inspiration divine
- Accomplissements typologiques et prophétiques

**V. CONTRASTES ET COMPLÉMENTARITÉS :**
Explorons aussi les tensions créatives qui révèlent la richesse divine :
- Paradoxes apparents qui s'harmonisent dans la vérité supérieure
- Perspectives complémentaires sur le même mystère divin
- Progressions révélationnelles de l'ombre à la réalité
- Diversité dans l'unité de l'inspiration divine

**VI. APPLICATIONS HERMÉNEUTIQUES :**
Cette approche canonique transforme notre compréhension. Elle nous garde de l'isolement textuel et enrichit notre saisie de la symphonie divine complète.

DIRECTIVES ACADÉMIQUES :
- Parallèles authentiques et vérifiables avec {passage} spécifiquement
- {target_length} mots d'exploration canonique narrative
- Références bibliques précises avec citations pertinentes
- Équilibre entre unité canonique et diversité littéraire

Révélez comment {passage} s'épanouit dans le concert harmonieux de toute l'Écriture, enrichissant notre contemplation de la révélation divine.
""",
            16: f"""
CONTEXTE DU CHAPITRE SUIVANT pour {passage}

MISSION : Devenir un guide prophétique, préparant la compréhension du chapitre suivant en montrant comment {passage} ouvre la voie à la suite du récit divin.

APPROCHE TRANSITIONNELLE NARRATIVE :
- Style de guide littéraire anticipant la suite de l'épopée sacrée
- Vision prospective et préparatoire
- Explications des techniques narratives (suspense, préparation, transition)
- Révélation de la continuité divine dans la progression textuelle

PRÉPARATION PROSPECTIVE INSPIRÉE :

**I. TRANSITIONS NARRATIVES ET THÉMATIQUES :**
Observons comment {passage} prépare organiquement le chapitre suivant. Dans l'art narratif divin, rien n'est accidentel. Chaque conclusion ouvre une nouvelle perspective, chaque résolution soulève de nouvelles questions qui trouveront leur réponse dans la suite du récit sacré.

**II. SEMENCES PLANTED POUR LA SUITE :**
Découvrons les germes narratifs et théologiques que {passage} plante :
- Questions soulevées qui attendent leur résolution
- Personnages introduits qui joueront un rôle crucial
- Thèmes amorcés qui se développeront pleinement
- Tensions créées qui trouveront leur dénouement

**III. PRÉPARATIONS PROVIDENTIELLES :**
Analysons comment {passage} orchestre providentiellement la suite :
- Événements qui conditionnent les développements futurs
- Décisions des personnages qui engagent l'avenir
- Interventions divines qui préparent de nouveaux actes
- Contextes établis pour les révélations suivantes

**IV. PROGRESSIONS RÉVÉLATIONNELLES ANNONCÉES :**
Explorons comment {passage} anticipe de nouveaux dévoilements divins :
- Vérités partiellement révélées qui s'approfondiront
- Mystères effleurés qui se dévoileront davantage
- Promesses énoncées qui trouveront leur réalisation
- Types esquissés qui se préciseront

**V. SUSPENSE SPIRITUEL ET ANTICIPATION :**
Découvrons l'art divin du suspense sanctifié. {passage} crée une attente légitime qui préparera notre cœur à recevoir les nouvelles révélations. Cette pédagogie divine cultive notre foi et notre persévérance.

**VI. APPLICATIONS POUR LA LECTURE SÉQUENTIELLE :**
Cette compréhension prospective enrichit notre lecture continue. Elle nous aide à saisir la logique divine de la révélation progressive et à cultiver une attente sanctifiée.

DIRECTIVES ACADÉMIQUES :
- Focus sur les véritables préparations vers {book} chapitre {int(chapter)+1 if chapter.isdigit() else "suivant"}
- {target_length} mots d'analyse transitionnelle narrative
- Éviter les anticipations non-fondées sur le texte
- Respecter la progression naturelle du récit biblique

Révélez comment {passage} nous prépare à recevoir avec fruit les nouvelles merveilles que Dieu révélera dans la suite de son récit sacré.
""",
            17: f"""
LEÇONS MORALES ET ÉTHIQUES pour {passage}

MISSION : Devenir un moraliste chrétien narratif, extrayant les enseignements éthiques de {passage} pour édifier le caractère selon l'image du Christ.

APPROCHE ÉTHIQUE NARRATIVE :
- Style de sage biblique dispensant la sagesse divine
- Éthique christocentrique et scripturaire
- Explications des termes moraux (sanctification, transformation, vertus chrétiennes)
- Applications concrètes pour la formation du caractère

ÉCOLE DE SAGESSE INSPIRÉE :

**I. FONDEMENTS DE L'ÉTHIQUE BIBLIQUE :**
Établissons les bases de la morale chrétienne révélée dans {passage}. L'éthique biblique n'est pas légalisme pharisaïque mais transformation gracieuse à l'image de Christ. Elle jaillit de la régénération et vise la glorification de Dieu.

**II. VERTUS CHRÉTIENNES RÉVÉLÉES :**
Découvrons les excellences morales que {passage} enseigne :
- Les fruits de l'Esprit manifestés dans les actions et attitudes
- Les vertus cardinales réinterprétées à la lumière de l'Évangile
- Les grâces chrétiennes spécifiques (humilité, patience, fidélité)
- Le développement progressif du caractère christiforme

**III. VICES DÉNONCÉS ET LEURS REMÈDES :**
Analysons les travers moraux exposés et leurs corrections divines :
- Les péchés révélés et leurs conséquences spirituelles
- Les tentations communes et leurs antidotes bibliques
- Les faiblesses caractérielles et leur transformation possible
- La repentance authentique et la restauration divine

**IV. PRINCIPES DE CONDUITE CHRÉTIENNE :**
Extrayons les règles de vie que {passage} établit :
- Les motivations pures vs les motivations charnelles
- Les priorités divines vs les priorités mondaines
- Les relations justes selon l'ordre créationnel et rédemptif
- La sagesse pratique pour les décisions quotidiennes

**V. FORMATION DU CARACTÈRE CHRISTIFORME :**
Explorons le processus de transformation morale :
- Le rôle de la Parole, de la prière, de la communion fraternelle
- L'importance de la discipline spirituelle et de l'exercice des vertus
- La croissance graduelle vs les victoires instantanées
- La persévérance dans la sanctification progressive

**VI. APPLICATIONS CONTEMPORAINES :**
Ces enseignements moraux s'appliquent à nos défis modernes. Ils nous équipent pour vivre avec intégrité dans un monde déchu, témoignant de la beauté morale de l'Évangile.

DIRECTIVES ACADÉMIQUES :
- Éthique authentiquement dérivée de {passage} spécifiquement
- {target_length} mots de formation morale narrative
- Équilibre entre grâce et responsabilité, liberté et sainteté
- Applications pratiques pour la croissance spirituelle

Révélez comment {passage} forme des disciples aux mœurs célestes, reflétant la beauté morale du Royaume de Dieu.
""",
            18: f"""
COMMENTAIRE TRADITIONNEL pour {passage}

MISSION : Devenir un gardien de la tradition exégétique, transmettant la sagesse herméneutique des Pères de l'Église et des Réformateurs sur {passage}.

APPROCHE TRADITIONNELLE NARRATIVE :
- Style de chroniqueur de la tradition chrétienne
- Respect de l'herméneutique historique et de la règle de foi
- Explications des termes patristiques (consensus patrum, analogie de la foi)
- Continuité avec la tradition apostolique authentique

TRANSMISSION TRADITIONNELLE INSPIRÉE :

**I. FONDEMENTS DE L'INTERPRÉTATION TRADITIONNELLE :**
Puisons dans le trésor herméneutique légué par nos pères dans la foi. Le consensus patrum (accord des Pères) et la regula fidei (règle de foi) nous guident pour interpréter {passage} dans la continuité apostolique, évitant les novations dangereuses.

**II. VOIX DES PÈRES DE L'ÉGLISE :**
Écoutons les géants spirituels des premiers siècles sur {passage} :
- L'exégèse christocentrique des Pères apostoliques
- Les lumières théologiques des Pères de Nicée et post-nicéens
- La sagesse spirituelle des Pères monastiques et mystiques
- L'apport des commentateurs byzantins et latins

**III. ÉCLAIRAGES DES RÉFORMATEURS :**
Découvrons les perspectives réformatrices sur {passage} :
- L'exégèse de Luther et son retour à l'Écriture seule
- Les commentaires systématiques de Calvin et sa clarté théologique
- Les apports des autres Réformateurs (Zwingli, Bullinger, Bèze)
- Le développement de l'herméneutique réformée orthodoxe

**IV. CONSENSUS ÉVANGÉLIQUE HISTORIQUE :**
Explorons l'accord substantiel de la tradition évangélique :
- Les vérités fondamentales unanimement confessées
- Les interprétations établies par les conciles œcuméniques
- La synthèse des confessions de foi protestantes
- L'harmonie essentielle malgré les nuances secondaires

**V. DÉVELOPPEMENTS HERMÉNEUTIQUES LÉGITIMES :**
Analysons comment la compréhension de {passage} s'est approfondie :
- Les précisions doctrinales nécessaires face aux hérésies
- L'enrichissement par les découvertes archéologiques et linguistiques
- L'application créative aux nouveaux défis historiques
- La continuité dans le changement légitime

**VI. APPLICATIONS DE LA SAGESSE TRADITIONNELLE :**
Cette sagesse ancestrale nous préserve des erreurs contemporaines et enrichit notre compréhension. Elle nous ancre dans la foi apostolique tout en nous équipant pour les défis actuels.

DIRECTIVES ACADÉMIQUES :
- Citations authentiques des sources traditionnelles sur {passage}
- {target_length} mots de transmission traditionnelle narrative
- Références aux Pères, Réformateurs, confessions historiques
- Équilibre entre tradition et Écriture seule

Révélez comment la tradition chrétienne authentique enrichit notre compréhension de {passage} dans la continuité de la foi apostolique.
""",
            19: f"""
ANALYSES GRAMMATICALES pour {passage}

MISSION : Devenir un linguiste sacré narratif, dévoilant les subtilités grammaticales de {passage} qui révèlent des nuances théologiques précieuses.

APPROCHE GRAMMATICALE NARRATIVE :
- Style de philologue biblique explorant les mystères linguistiques
- Analyse technique rendue accessible et spirituellement profitable
- Explications des termes grammaticaux (syntaxe, morphologie, sémantique)
- Révélations théologiques à travers les structures linguistiques

LABORATOIRE LINGUISTIQUE INSPIRÉ :

**I. ARCHITECTURE SYNTAXIQUE DIVINE :**
Pénétrons dans l'atelier divin de la syntaxe sacrée. Chaque construction grammaticale de {passage} porte une intention théologique. L'Esprit Saint a inspiré non seulement les mots mais aussi leur agencement syntaxique révélateur.

**II. MORPHOLOGIE RÉVÉLATRICE :**
Analysons les formes grammaticales qui enrichissent le sens :
- Les temps verbaux hébreux/grecs et leurs nuances aspectuelles
- Les modes (indicatif, impératif, subjonctif) et leurs implications théologiques
- Les voix (active, passive, moyenne) révélant l'agency divine et humaine
- Les constructions causatives, intensives, reflexives et leur signification

**III. STRUCTURES SYNTAXIQUES SIGNIFICATIVES :**
Explorons les arrangements grammaticaux porteurs de sens :
- Les constructions emphatiques (ordre des mots, particules)
- Les ellipses et sous-entendus révélateurs
- Les parallélismes syntaxiques et leur fonction rhétorique
- Les chiasmes grammaticaux et leur centre théologique

**IV. PARTICULARITÉS SÉMANTIQUES :**
Découvrons les nuances de sens portées par la grammaire :
- Les jeux de mots (paronomases) et leur intention prophétique
- Les métonymies et synecdoques révélant des connexions spirituelles
- Les constructions idiomatiques hébraïques/grecques
- Les euphémismes et leur délicatesse théologique

**V. ANALYSE COMPARATIVE DES MANUSCRITS :**
Explorons les variantes textuelles et leur impact herméneutique :
- Les leçons divergentes et leur évaluation critique
- Les corrections scribales et leur motivation théologique
- L'apport des versions anciennes à la compréhension grammaticale
- La stabilité remarquable du texte inspiré

**VI. APPLICATIONS EXÉGÉTIQUES TRANSFORMATRICES :**
Ces analyses grammaticales affinent notre compréhension théologique. Elles révèlent des nuances doctrinales, éthiques, pastorales qui enrichissent notre prédication et notre vie spirituelle.

DIRECTIVES ACADÉMIQUES :
- Analyses grammaticales authentiques basées sur {passage} spécifiquement
- {target_length} mots d'exploration linguistique narrative accessible
- Références aux grammaires de référence (Gesenius, Wallace, etc.)
- Applications herméneutiques et homilétiques pratiques

Révélez comment la grammaire sacrée de {passage} devient une fenêtre sur les subtilités de la révélation divine.
""",
            20: f"""
MÉDITATION SPIRITUELLE pour {passage}

MISSION : Devenir un guide de méditation sacrée, conduisant l'âme dans la contemplation transformatrice des vérités spirituelles révélées dans {passage}.

APPROCHE MÉDITATIVE NARRATIVE :
- Style de directeur spirituel guidant l'oraison chrétienne
- Méditation biblique substantielle et transformatrice
- Explications des termes spirituels (lectio divina, contemplation, union mystique)
- Croissance dans la communion intime avec Dieu

RETRAITE SPIRITUELLE INSPIRÉE :

**I. PRÉPARATION DU CŒUR À LA MÉDITATION :**
Préparons notre âme à recevoir les grâces divines de {passage}. La méditation chrétienne diffère de la contemplation orientale ; elle se nourrit de la Parole révélée pour conduire à l'union avec le Dieu personnel et trinitaire.

**II. LECTIO DIVINA : LECTURE SACRÉE :**
Pratiquons la lecture orante de {passage} selon la tradition monastique :
- Lectio : Lecture attentive et répétée du texte sacré
- Meditatio : Rumination spirituelle des vérités révélées
- Oratio : Prière jaillissant de la contemplation
- Contemplatio : Repos de l'âme en Dieu à travers sa Parole

**III. CONTEMPLATION DES VÉRITÉS DIVINES :**
Contemplons les mystères révélés dans {passage} :
- Les attributs divins manifestés et leur adoration
- L'œuvre du Christ révélée et notre gratitude
- L'action du Saint-Esprit et notre coopération
- Les promesses divines et notre espérance fortifiée

**IV. APPLICATIONS TRANSFORMATRICES :**
Laissons {passage} transformer notre être intérieur :
- Purification des affections désordonnées révélées par la Parole
- Illumination de l'intelligence par les vérités contemplées
- Embrasement de la volonté par l'amour divin manifesté
- Union croissante avec Dieu par la méditation assidue

**V. PRIÈRES INSPIRÉES PAR LE PASSAGE :**
Transformons notre méditation en oraison fervente :
- Adoration pour les perfections divines révélées
- Confession des péchés mis en lumière par le texte
- Supplication pour la grâce de vivre ces vérités
- Intercession inspirée par les enseignements reçus

**VI. FRUITS SPIRITUELS DE LA MÉDITATION :**
Recueillons les grâces que cette méditation produit :
- Paix profonde dans la communion avec Dieu
- Joie spirituelle dans la contemplation divine
- Force pour la sanctification progressive
- Zèle pour le témoignage et le service

**VII. INTÉGRATION DANS LA VIE QUOTIDIENNE :**
Portons les fruits de cette méditation dans notre existence :
- Présence de Dieu cultivée tout au long du jour
- Décisions éclairées par les vérités méditées
- Relations transformées par l'amour divin reçu
- Témoignage authentique de la beauté divine contemplée

DIRECTIVES ACADÉMIQUES :
- Méditation authentiquement enracinée dans {passage} spécifiquement
- {target_length} mots de guidance spirituelle méditative
- Équilibre entre substance doctrinale et piété expérientielle
- Applications pratiques pour la croissance spirituelle

Conduisez l'âme dans une rencontre transformatrice avec Dieu à travers les vérités spirituelles de {passage}.
""",
            21: f"""
QUESTIONS D'APPROFONDISSEMENT pour {passage}

MISSION : Devenir un maître socratique biblique, formulant des questions pénétrantes qui sondent les profondeurs spirituelles de {passage} et stimulent la croissance spirituelle.

APPROCHE INTERROGATIVE NARRATIVE :
- Style de maître spirituel utilisant la maïeutique sacrée
- Questions progressives du simple au complexe
- Explications des méthodes pédagogiques (questionnement socratique, dialectique spirituelle)
- Stimulation de la réflexion et de l'application personnelle

SÉMINAIRE SOCRATIQUE INSPIRÉ :

**I. ART DU QUESTIONNEMENT SPIRITUEL :**
Maîtrisons l'art divin du questionnement qui conduit à la découverte. Jésus lui-même utilisait les questions pour révéler les vérités du Royaume. Formulons des interrogations qui ouvrent l'intelligence et touchent le cœur à travers {passage}.

**II. QUESTIONS EXÉGÉTIQUES FONDAMENTALES :**
Sondons le sens littéral et théologique de {passage} :
- Que révèle ce passage sur la nature et les attributs de Dieu ?
- Quelles vérités christologiques émergent de ce texte ?
- Comment l'œuvre du Saint-Esprit se manifeste-t-elle ici ?
- Quels enseignements sur l'humanité et le péché découvrons-nous ?
[Adaptation aux contenus réellement présents dans {passage}]

**III. QUESTIONS HERMÉNEUTIQUES APPROFONDIES :**
Explorons les méthodes d'interprétation révélées :
- Comment ce passage s'harmonise-t-il avec l'ensemble de l'Écriture ?
- Quelles difficultés apparentes trouvent leur résolution dans le contexte ?
- Quelle progression révélationnelle observe-t-on ici ?
- Comment les genres littéraires influencent-ils notre compréhension ?

**IV. QUESTIONS APPLICATIVES TRANSFORMATRICES :**
Stimulons l'application personnelle et communautaire :
- Quelles transformations ce passage opère-t-il dans notre caractère ?
- Comment ces vérités influencent-elles nos relations familiales et sociales ?
- Quelles implications pour notre culte et notre service chrétien ?
- Comment témoigner de ces vérités dans notre contexte contemporain ?

**V. QUESTIONS DE MÉDITATION CONTEMPLATIVE :**
Approfondissons la dimension spirituelle expérientielle :
- Comment ce passage enrichit-il notre communion avec Dieu ?
- Quelles consolations divines y découvrons-nous pour nos épreuves ?
- Comment nourrit-il notre espérance eschatologique ?
- Quelles invitations à la sainteté y entendons-nous ?

**VI. QUESTIONS DE SYNTHÈSE ET D'INTÉGRATION :**
Unifions notre compréhension dans une vision cohérente :
- Comment ce passage contribue-t-il à notre théologie personnelle ?
- Quelle place occupe-t-il dans l'histoire de la rédemption ?
- Comment enrichit-il notre compréhension des autres portions scripturaires ?
- Quelles vérités centrales résument l'enseignement de ce passage ?

**VII. GUIDE POUR L'ÉTUDE PERSONNELLE ET DE GROUPE :**
Utilisons ces questions pour approfondir notre étude :
- Progression pédagogique pour l'animation de groupe
- Méthodes de réflexion personnelle et de journal spirituel
- Techniques de mémorisation et de méditation quotidienne
- Applications pour l'enseignement et le discipulat

DIRECTIVES ACADÉMIQUES :
- Questions authentiquement générées par {passage} spécifiquement
- {target_length} mots de questionnement pédagogique narratif
- Progression logique du simple au complexe, du textuel au spirituel
- Applications pratiques pour l'étude individuelle et communautaire

Formulez des questions qui ouvrent les trésors cachés de {passage} et conduisent à une transformation spirituelle authentique.
""",
            22: f"""
RÉFÉRENCES CROISÉES pour {passage}

MISSION : Devenir un harmoniste canonique, tissant les liens divins entre {passage} et l'ensemble scripturaire, révélant l'unité organique de la révélation progressive.

APPROCHE CANONIQUE SYSTÉMATIQUE :
- Style de concordancier inspiré explorant les connexions divines
- Méthodologie rigoureuse de l'intertextualité biblique
- Explications des principes herméneutiques (analogie scripturaire, intertextualité)
- Révélation de l'harmonie divine dans la diversité canonique

RÉSEAU CANONIQUE INSPIRÉ :

**I. MÉTHODOLOGIE DES RÉFÉRENCES CROISÉES :**
Maîtrisons l'art divin de la référence croisée qui révèle l'unité scripturaire. Chaque passage biblique résonne avec d'autres portions, créant une symphonie révélationnelle. Découvrons comment {passage} s'harmonise avec l'ensemble canonique.

**II. RÉFÉRENCES THÉMATIQUES DIRECTES :**
Explorons les passages qui partagent les mêmes sujets que {passage} :
- Textes traitant des mêmes doctrines ou événements
- Développements parallèles dans différents livres bibliques
- Progressions thématiques de l'Ancien au Nouveau Testament
- Accomplissements et préfigurations mutuelles
[Adaptation aux thèmes réellement présents dans {passage}]

**III. CONNEXIONS LEXICALES ET CONCEPTUELLES :**
Analysons les réseaux de mots et d'idées qui relient {passage} à d'autres textes :
- Termes-clés hébreux/grecs et leurs occurrences significatives
- Concepts théologiques développés ailleurs dans l'Écriture
- Métaphores et images récurrentes dans le canon
- Formules caractéristiques et leur usage scripturaire

**IV. CITATIONS ET ALLUSIONS INTERTEXTUELLES :**
Découvrons les références explicites et implicites dans {passage} :
- Citations directes d'autres portions bibliques
- Allusions subtiles révélant des connexions profondes
- Échos phraséologiques et leur signification herméneutique
- Réinterprétations créatives sous inspiration divine

**V. PARALLÈLES TYPOLOGIQUES ET PROPHÉTIQUES :**
Explorons les correspondances révélatrices dans l'économie divine :
- Types vétérotestamentaires et leurs antitypes néotestamentaires
- Prophéties et leurs accomplissements canoniques
- Préfigurations rituelles et leurs réalisations spirituelles
- Progressions révélationnelles culminant dans le Christ

**VI. HARMONIES DOCTRINALES ET ÉTHIQUES :**
Analysons comment {passage} s'intègre dans l'enseignement scripturaire global :
- Contributions à la théologie systématique biblique
- Développements éthiques et moraux à travers le canon
- Enseignements sur le salut, la sanctification, l'eschatologie
- Applications pastorales enrichies par les parallèles

**VII. CONTRASTES RÉVÉLATEURS ET COMPLÉMENTARITÉS :**
Explorons les tensions créatives qui révèlent la richesse divine :
- Paradoxes apparents résolus par l'analogie scripturaire
- Perspectives complémentaires sur les mêmes mystères
- Progressions révélationnelles de l'ombre à la lumière
- Diversité dans l'unité de l'inspiration divine

**VIII. APPLICATIONS HERMÉNEUTIQUES PRATIQUES :**
Utilisons ces connexions pour enrichir notre compréhension :
- Méthode d'étude comparative et canonique
- Prédication enrichie par les références croisées
- Enseignement systématique basé sur les harmonies scripturaires
- Apologétique fondée sur l'unité canonique

DIRECTIVES ACADÉMIQUES :
- Références authentiques et vérifiables liées à {passage} spécifiquement
- {target_length} mots d'exploration canonique systématique
- Citations bibliques précises avec références exactes
- Équilibre entre exhaustivité et pertinence herméneutique

Révélez comment {passage} s'épanouit dans le concert harmonieux de l'Écriture entière, enrichissant notre contemplation de la révélation divine unifiée.
""",
            23: f"""
NOTES HISTORIQUES pour {passage}

MISSION : Devenir un chroniqueur de l'histoire sainte, situant {passage} dans son contexte historique précis pour illuminer sa signification providentielle dans l'épopée divine.

APPROCHE HISTORICO-CRITIQUE NARRATIVE :
- Style d'historien biblique maîtrisant les sources anciennes
- Contextualisation historique rigoureuse et spirituellement profitable
- Explications des termes historiques (historiographie biblique, synchronismes)
- Révélation de la providence divine à travers l'histoire

ARCHIVES HISTORIQUES INSPIRÉES :

**I. MÉTHODOLOGIE DE L'HISTOIRE BIBLIQUE :**
Appliquons une historiographie sacrée qui reconnaît l'action divine dans l'histoire humaine. {passage} s'inscrit dans l'histoire réelle, vérifiable, où l'Éternel orchestre les événements selon son dessein éternel de rédemption.

**II. CONTEXTE POLITIQUE ET GÉOPOLITIQUE :**
Situons {passage} dans les réalités politiques de son époque :
- Empires et royaumes contemporains et leur influence
- Dynamiques géopolitiques affectant le peuple de Dieu
- Personnalités historiques mentionnées ou sous-entendues
- Conflits et alliances révélant la souveraineté divine
[Adaptation au contexte historique réel de {passage}]

**III. ARRIÈRE-PLAN SOCIO-ÉCONOMIQUE :**
Explorons les réalités sociales qui éclairent {passage} :
- Structure sociale et hiérarchies de l'époque
- Conditions économiques et leur impact spirituel
- Pratiques commerciales et leur symbolisme biblique
- Vie quotidienne et ses métaphores dans le texte

**IV. CONTEXTE RELIGIEUX ET CULTUEL :**
Analysons l'environnement spirituel contemporain :
- État de la religion révélée à l'époque de {passage}
- Influences religieuses païennes et syncrétistes
- Institutions cultuelles et leur fonctionnement
- Mouvements spirituels et leurs implications théologiques

**V. CHRONOLOGIE ET SYNCHRONISMES :**
Établissons la datation précise et ses implications :
- Chronologie biblique et extra-biblique coordonnée
- Synchronismes avec l'histoire ancienne vérifiable
- Calendriers et systèmes de datation de l'époque
- Implications prophétiques et eschatologiques

**VI. SOURCES HISTORIQUES COMPLÉMENTAIRES :**
Explorons les témoignages extra-bibliques pertinents :
- Documents cunéiformes, hiéroglyphiques, épigraphiques
- Témoignages d'historiens anciens (Hérodote, Thucydide, Josèphe)
- Découvertes archéologiques confirmant le récit biblique
- Traditions orales et leur contribution à la compréhension

**VII. GÉOGRAPHIE HISTORIQUE :**
Situons {passage} dans son cadre géographique ancien :
- Topographie et climat de l'époque
- Voies de communication et centres urbains
- Évolutions géopolitiques et leurs conséquences
- Archéologie des sites mentionnés

**VIII. IMPLICATIONS PROVIDENTIELLES :**
Découvrons la main divine dans ces circonstances historiques :
- Préparation providentielle des événements de {passage}
- Orchestration divine des facteurs humains
- Accomplissement des promesses à travers l'histoire
- Leçons sur la souveraineté divine dans l'histoire humaine

DIRECTIVES ACADÉMIQUES :
- Données historiques authentiques et vérifiables concernant {passage}
- {target_length} mots d'analyse historique narrative rigoureuse
- Références aux sources primaires et secondaires fiables
- Équilibre entre érudition historique et édification spirituelle

Révélez comment le contexte historique de {passage} magnifie la providence divine et enrichit notre compréhension de l'action souveraine de Dieu dans l'histoire.
""",
            24: f"""
PRIÈRE DE CLÔTURE pour {passage}

MISSION : Composer une prière de conclusion digne des plus hautes traditions liturgiques, synthétisant les vérités de {passage} en une oraison transformatrice qui scelle l'étude dans l'adoration.

APPROCHE LITURGIQUE NARRATIVE :
- Style de liturgiste inspiré composant l'oraison parfaite
- Synthèse priante des vérités étudiées
- Explications des termes liturgiques (doxologie, épilogue orante, conclusion eucharistique)
- Transformation de l'étude en adoration contemplative

ORATOIRE LITURGIQUE INSPIRÉ :

**I. ART DE LA PRIÈRE DE CLÔTURE :**
Composons une oraison qui couronne dignement notre étude de {passage}. La prière de clôture transforme l'étude intellectuelle en communion spirituelle, l'analyse théologique en adoration contemplative, la connaissance en expérience transformatrice.

**II. SYNTHÈSE ADORATRICE DES VÉRITÉS RÉVÉLÉES :**
Rassemblons en prière les enseignements reçus de {passage} :

*Père céleste, Auteur de toute révélation sacrée,*
*Nous voici devant Toi, transformés par la contemplation de {passage}.*
*Tes vérités éternelles ont illuminé nos intelligences,*
*Ton Esprit Saint a touché nos cœurs,*
*Ta Parole vivante a sondé nos consciences.*

**III. CONFESSION ET PURIFICATION :**
*Seigneur, {passage} nous a révélé notre condition devant Toi.*
*Nous confessons humblement nos manquements aux vérités contemplées,*
*Nos résistances aux appels divins entendus,*
*Notre lenteur à vivre selon Tes enseignements parfaits.*
*Purifie-nous par le sang de Christ, notre Médiateur parfait.*

**IV. SUPPLICATION TRANSFORMATRICE :**
*Accorde-nous, Père de miséricorde,*
*La grâce de mettre en pratique les enseignements de {passage}.*
*Que Ton Esprit grave ces vérités dans nos cœurs renouvelés,*
*Qu'elles transforment nos caractères à l'image de Ton Fils,*
*Qu'elles dirigent nos pas dans les sentiers de la justice.*

**V. INTERCESSION ECCLESIALE ET MISSIONNAIRE :**
*Étends Tes bénédictions, Seigneur, à Ton Église universelle.*
*Que les vérités de {passage} nourrissent Tes enfants dispersés,*
*Qu'elles fortifient les faibles, consolent les affligés,*
*Qu'elles équipent les serviteurs pour l'édification du Corps de Christ.*
*Utilise ces enseignements pour l'avancement de Ton Royaume.*

**VI. DOXOLOGIE ET GLORIFICATION :**
*À Toi, Père éternel, source de toute vérité,*
*Au Fils, Parole incarnée révélée dans {passage},*
*Au Saint-Esprit, Illuminateur de nos intelligences,*
*Soient rendus honneur, gloire et adoration,*
*Maintenant et dans tous les siècles des siècles.*

**VII. ENGAGEMENT ET CONSÉCRATION :**
*Seigneur, que cette étude ne reste pas stérile,*
*Mais qu'elle produise du fruit pour Ta gloire.*
*Aide-nous à être des disciples fidèles,*
*Témoins authentiques de Tes vérités éternelles,*
*Instruments de Ta grâce transformatrice.*

**VIII. CONCLUSION EUCHARISTIQUE :**
*Merci, Père céleste, pour le privilège de sonder Tes mystères,*
*Pour la richesse de {passage} qui nourrit nos âmes,*
*Pour l'espérance que ces vérités allument en nos cœurs.*
*Garde-nous dans Ta vérité, conduis-nous par Ta Parole,*
*Jusqu'au jour glorieux de la vision béatifique.*

*Amen et Amen.*

DIRECTIVES ACADÉMIQUES :
- Prière authentiquement inspirée par les contenus spécifiques de {passage}
- {target_length} mots d'oraison liturgique narrative élaborée
- Respect des traditions liturgiques chrétiennes historiques
- Applications spirituelles concrètes et transformatrices

Composez une prière qui transforme l'étude de {passage} en rencontre adoratrice avec le Dieu vivant, scellant l'apprentissage dans la communion divine.
""",
            25: f"""
PLAN D'ENSEIGNEMENT pour {passage}

MISSION : Devenir un pédagogue biblique expert, élaborant une stratégie d'enseignement complète qui transmet efficacement les vérités de {passage} selon les meilleures méthodes didactiques chrétiennes.

APPROCHE PÉDAGOGIQUE NARRATIVE :
- Style de maître enseignant expérimenté concevant le cursus parfait
- Méthodologie d'enseignement biblique éprouvée
- Explications des termes pédagogiques (andragogie chrétienne, progression didactique)
- Formation de disciples équipés et transformés

ACADÉMIE BIBLIQUE INSPIRÉE :

**I. PHILOSOPHIE DE L'ENSEIGNEMENT BIBLIQUE :**
Établissons les fondements d'une pédagogie christocentrique pour {passage}. L'enseignement biblique vise la transformation, pas seulement l'information. Il engage l'intelligence, touche le cœur, et équipe pour l'action selon le modèle du Maître Jésus.

**II. ANALYSE DES APPRENANTS ET CONTEXTUALISATION :**
Adaptons notre enseignement aux besoins spécifiques :
- Niveaux spirituels et intellectuels des participants
- Contextes culturels et générationnels à considérer
- Défis contemporains que {passage} peut adresser
- Motivations et attentes légitimes des apprenants

**III. OBJECTIFS PÉDAGOGIQUES TRANSFORMATEURS :**
Définissons clairement ce que les apprenants devront maîtriser :

*OBJECTIFS COGNITIFS (Savoir) :*
- Comprendre le contexte historique et littéraire de {passage}
- Maîtriser les vérités doctrinales enseignées
- Saisir les applications herméneutiques appropriées

*OBJECTIFS AFFECTIFS (Être) :*
- Développer l'amour pour la Parole de Dieu
- Cultiver la soumission aux vérités révélées
- Nourrir l'adoration et la reconnaissance

*OBJECTIFS PSYCHOMOTEURS (Faire) :*
- Appliquer les enseignements dans la vie quotidienne
- Partager efficacement ces vérités avec d'autres
- Utiliser {passage} dans l'édification mutuelle

**IV. PROGRESSION DIDACTIQUE STRUCTURÉE :**

*SÉANCE 1 : APPROCHE ET CONTEXTE*
- Accroche spirituelle captivant l'attention
- Présentation du contexte historique et littéraire
- Lecture méditative et première impression

*SÉANCE 2 : ANALYSE TEXTUELLE*
- Étude des mots-clés et structures grammaticales
- Exploration des difficultés textuelles
- Comparaison des traductions

*SÉANCE 3 : THÉOLOGIE ET DOCTRINE*
- Extraction des vérités doctrinales
- Connexions avec l'ensemble scripturaire
- Développement systématique des enseignements

*SÉANCE 4 : APPLICATIONS TRANSFORMATRICES*
- Implications pour la vie personnelle et familiale
- Applications ecclésiastiques et missionnaires
- Engagement concret et mesurable

**V. MÉTHODES PÉDAGOGIQUES VARIÉES :**
- Exposition magistrale pour les fondements théologiques
- Discussion dirigée pour l'appropriation personnelle  
- Travaux de groupe pour l'approfondissement
- Études de cas pour l'application pratique
- Mémorisation pour l'intériorisation
- Prière et méditation pour la transformation

**VI. SUPPORTS DIDACTIQUES ET RESSOURCES :**
- Matériel visuel (cartes, chronologies, schémas)
- Ressources textuelles (commentaires, dictionnaires)
- Supports multimédia appropriés
- Fiches de travail et guides d'étude personnelle

**VII. ÉVALUATION ET SUIVI :**
- Évaluation formative par questions et discussions
- Évaluation sommative par projets d'application
- Suivi personnel pour la croissance spirituelle
- Encouragement à l'enseignement mutuel

**VIII. ADAPTATION POUR DIFFÉRENTS CONTEXTES :**
- Version intensive pour retraite spirituelle
- Série dominicale pour culte public
- Étude approfondie pour groupe biblique
- Formation pastorale pour responsables

DIRECTIVES ACADÉMIQUES :
- Plan pédagogique adapté aux contenus réels de {passage}
- {target_length} mots de stratégie d'enseignement narrative complète
- Méthodes éprouvées d'enseignement biblique adulte
- Applications pratiques pour divers contextes ecclésiaux

Élaborez une stratégie d'enseignement qui transforme {passage} en expérience d'apprentissage enrichissante, formant des disciples équipés pour la gloire de Dieu.
""",
            26: f"""
VOCABULAIRE THÉOLOGIQUE pour {passage}

MISSION : Devenir un lexicographe sacré, créant un glossaire théologique complet qui décode les termes spirituels de {passage} et enrichit le vocabulaire biblique des étudiants.

APPROCHE LEXICOGRAPHIQUE NARRATIVE :
- Style de compilateur de dictionnaire biblique spécialisé
- Définitions rigoureuses et spirituellement enrichissantes  
- Explications des méthodes lexicales (étymologie, sémantique, évolution conceptuelle)
- Formation d'un vocabulaire théologique précis et transformateur

DICTIONNAIRE THÉOLOGIQUE INSPIRÉ :

**I. MÉTHODOLOGIE LEXICOGRAPHIQUE SACRÉE :**
Établissons les principes d'un vocabulaire théologique authentique pour {passage}. Chaque terme biblique porte des siècles de révélation progressive. Notre glossaire révélera les richesses cachées dans le langage inspiré de ce passage.

**II. TERMES HÉBREUX/GRECS FONDAMENTAUX :**
Explorons les vocables originaux qui structurent {passage} :

[Adaptation selon les termes réellement présents dans {passage}]

*Exemple de structure pour chaque terme :*

**TERME ORIGINAL** [Hébreu : xxxxx / Grec : xxxxx]
- *Étymologie* : Racine et développement sémantique
- *Occurrences bibliques* : Fréquence et contextes significatifs  
- *Champ sémantique* : Nuances et concepts connexes
- *Évolution théologique* : Développement de l'AT au NT
- *Applications spirituelles* : Implications pour la vie chrétienne

**III. CONCEPTS DOCTRINAUX MAJEURS :**
Analysons les notions théologiques centrales révélées :

*SOTÉRIOLOGIE (Doctrine du Salut) :*
- Termes de rédemption, justification, sanctification
- Vocabulaire de l'expiation et de la réconciliation
- Concepts de grâce, foi, régénération selon {passage}

*THÉOLOGIE PROPRE (Doctrine de Dieu) :*
- Noms divins et leurs significations révélées
- Attributs communicables et incommunicables manifestés
- Terminologie trinitaire explicite ou implicite

*CHRISTOLOGIE (Doctrine du Christ) :*
- Titres messianiques et leurs implications
- Vocabulaire de l'incarnation et de l'œuvre médiatrice
- Termes décrivant les natures divine et humaine

*PNEUMATOLOGIE (Doctrine du Saint-Esprit) :*
- Appellations du Saint-Esprit dans {passage}
- Terminologie de ses œuvres et ministères
- Vocabulaire des dons et fruits spirituels

**IV. TERMINOLOGIE CULTUELLE ET LITURGIQUE :**
Découvrons le vocabulaire de l'adoration et du service divin :
- Termes sacrificiels et leur symbolisme
- Vocabulaire liturgique et ses significations spirituelles
- Appellations des lieux saints et leur portée théologique
- Terminologie des fêtes et temps sacrés

**V. CONCEPTS ÉTHIQUES ET MORAUX :**
Explorons le langage de la sainteté et de la conduite chrétienne :
- Vocabulaire des vertus et leur développement biblique
- Terminologie des vices et leurs antidotes spirituels
- Concepts de pureté, justice, intégrité selon {passage}
- Langage de la transformation morale

**VI. VOCABULAIRE ESCHATOLOGIQUE :**
Analysons les termes des réalités futures révélées :
- Terminologie du royaume de Dieu et sa manifestation
- Vocabulaire de la résurrection et de la vie éternelle
- Concepts du jugement et de la rétribution divine
- Langage de l'espérance et de la consommation finale

**VII. MÉTAPHORES ET IMAGES SYMBOLIQUES :**
Décodons le langage figuratif et sa richesse spirituelle :
- Images pastorales, agricoles, architecturales
- Métaphores familiales, juridiques, militaires
- Symbolisme des couleurs, nombres, matériaux
- Paraboles et allégories selon leur contexte

**VIII. APPLICATIONS HERMÉNEUTIQUES :**
Utilisons ce vocabulaire pour enrichir notre compréhension :
- Principes d'interprétation basés sur la précision lexicale
- Méthodes d'étude personnelle enrichies
- Prédication et enseignement plus fidèles au texte
- Apologétique fondée sur la richesse conceptuelle

DIRECTIVES ACADÉMIQUES :
- Glossaire authentique basé sur les termes réellement présents dans {passage}
- {target_length} mots de vocabulaire théologique narratif complet
- Références aux dictionnaires théologiques de référence (TDNT, TDOT, etc.)
- Applications pratiques pour l'étude et l'enseignement biblique

Créez un vocabulaire théologique qui transforme {passage} en école de formation linguistique sacrée, équipant pour une compréhension plus riche de la révélation divine.
""",
            27: f"""
RÉFLEXIONS PASTORALES pour {passage}

MISSION : Devenir un pasteur-théologien expérimenté, distillant la sagesse pastorale que {passage} offre pour le ministère chrétien contemporain et le soin des âmes.

APPROCHE PASTORALE NARRATIVE :
- Style de pasteur chevronné partageant sa sagesse ministérielle
- Théologie pastorale enracinée dans l'Écriture
- Explications des concepts pastoraux (cure d'âmes, discernement spirituel, direction)
- Applications transformatrices pour le ministère et l'accompagnement

CABINET PASTORAL INSPIRÉ :

**I. FONDEMENTS DE LA THÉOLOGIE PASTORALE :**
Puisons dans {passage} les principes divins du ministère pastoral. Chaque texte biblique équipe les serviteurs de Dieu pour "paître le troupeau avec intelligence et sagesse". Découvrons comment ce passage forme et dirige le cœur pastoral.

**II. DISCERNEMENT SPIRITUEL ET DIAGNOSTIC D'ÂMES :**
Apprenons de {passage} à diagnostiquer les états spirituels :

*RECONNAISSANCE DES TEMPÉRAMENTS SPIRITUELS :*
- Les âmes affamées de Dieu et leur nourriture appropriée
- Les consciences troublées et leur consolation biblique
- Les cœurs endurcis et les moyens de grâce nécessaires
- Les esprits confus et l'éclairage doctrinal requis

*DISCERNEMENT DES SAISONS SPIRITUELLES :*
- Temps de croissance et leurs encouragements
- Périodes d'épreuve et leurs consolations divines
- Moments de stagnation et leurs stimulations appropriées
- Saisons de récolte et leurs celebrations légitimes

**III. PRÉDICATION ET ENSEIGNEMENT PASTORAL :**
Découvrons comment {passage} nourrit la prédication transformatrice :

*HOMILÉTIQUE CHRISTOCENTRIQUE :*
- Extraction du message central pour l'édification
- Applications contemporaines respectueuses du texte
- Illustrations tirées de l'expérience pastorale
- Appels à la repentance et à la consécration

*CATÉCHÈSE ET FORMATION :*
- Enseignements doctrinaux pour l'affermissement
- Formation pratique pour le service chrétien
- Discipulat personnalisé selon les besoins
- Préparation aux sacrements et à l'engagement

**IV. CONSOLATION ET ENCOURAGEMENT :**
Explorons les ressources consolatrices de {passage} :

*MINISTÈRE AUPRÈS DES AFFLIGÉS :*
- Vérités bibliques pour les temps de deuil
- Promesses divines pour les périodes d'épreuve
- Perspectives éternelles face aux souffrances temporelles
- Accompagnement spirituel dans la vallée de l'ombre

*RESTAURATION DES CHUTÉS :*
- Approche biblique de la discipline ecclésiastique
- Processus de repentance et de réconciliation
- Réintégration dans la communion fraternelle
- Prévention des rechutes par l'affermissement

**V. DIRECTION SPIRITUELLE ET ACCOMPAGNEMENT :**
Apprenons de {passage} l'art du guidance spirituel :

*DISCERNEMENT DES VOCATIONS :*
- Identification des dons spirituels et naturels
- Orientation vers les ministères appropriés
- Formation et équipement des serviteurs
- Accompagnement dans les transitions ministérielles

*CROISSANCE SPIRITUELLE PERSONNALISÉE :*
- Plans de lecture et de méditation biblique
- Disciplines spirituelles adaptées aux tempéraments
- Correction fraternelle avec amour et sagesse
- Encouragement à la persévérance dans la foi

**VI. ADMINISTRATION ECCLÉSIASTIQUE SAGE :**
Découvrons les principes de gouvernance révélés dans {passage} :
- Leadership serviteur selon le modèle christique
- Prise de décision communautaire sous l'autorité divine
- Gestion des conflits par la réconciliation évangélique
- Développement de la vision missionnaire locale

**VII. ÉVANGÉLISATION ET MISSION :**
Explorons comment {passage} équipe pour le témoignage :
- Apologétique biblique face aux objections contemporaines
- Méthodes d'évangélisation respectueuses et efficaces
- Formation des témoins et évangélistes
- Intégration des nouveaux convertis

**VIII. ÉQUILIBRE ET SANTÉ MINISTÉRIELLE :**
Apprenons de {passage} la sagesse pour la durabilité pastorale :
- Prévention de l'épuisement par la dépendance divine
- Cultiver la vie spirituelle personnelle
- Maintenir l'équilibre famille-ministère
- Rechercher le soutien fraternel et la supervision

DIRECTIVES ACADÉMIQUES :
- Sagesse pastorale authentiquement tirée de {passage} spécifiquement
- {target_length} mots de réflexions pastorales narratives approfondies
- Applications concrètes pour le ministère contemporain
- Équilibre entre profondeur théologique et praticabilité pastorale

Distillez la sagesse pastorale que {passage} révèle, équipant les serviteurs de Dieu pour un ministère fidèle et transformateur dans l'Église contemporaine.
""",
            28: f"""
PLAN D'ÉTUDE PERSONNELLE pour {passage}

MISSION : Devenir un mentor spirituel personnel, concevant un parcours d'étude individuelle qui transforme {passage} en expérience de croissance spirituelle profonde et durable.

APPROCHE MENTORIELLE NARRATIVE :
- Style de directeur spirituel élaborant un itinéraire sur mesure
- Pédagogie de l'auto-formation biblique
- Explications des méthodes d'étude personnelle (lectio divina, mémorisation, journaling)
- Transformation de l'étude en rencontre avec Dieu

RETRAITE PERSONNELLE INSPIRÉE :

**I. PHILOSOPHIE DE L'ÉTUDE BIBLIQUE PERSONNELLE :**
Établissons les fondements d'une approche transformatrice de {passage}. L'étude personnelle dépasse l'accumulation d'informations ; elle vise la transformation du cœur par la rencontre avec le Dieu vivant à travers sa Parole révélée.

**II. PRÉPARATION SPIRITUELLE ET PRATIQUE :**

*DISPOSITION DU CŒUR :*
- Prière d'ouverture demandant l'illumination divine
- Confession préalable pour un cœur réceptif
- Soumission à l'autorité de la Parole divine
- Attente expectante de la transformation

*ENVIRONNEMENT D'ÉTUDE :*
- Lieu calme propice à la concentration
- Horaires réguliers pour la discipline
- Matériel d'étude approprié (Bible, cahier, ressources)
- Élimination des distractions temporelles

**III. PROGRAMME D'ÉTUDE STRUCTURÉ (4 SEMAINES) :**

*SEMAINE 1 : IMMERSION TEXTUELLE*

*Jour 1-2 : Lecture contemplative*
- Lecture répétée de {passage} en plusieurs versions
- Note des premières impressions et questions
- Prière méditative sur le texte
- Journaling des réactions spirituelles initiales

*Jour 3-4 : Contexte et arrière-plan*
- Étude du contexte historique et littéraire
- Recherche des circonstances d'écriture
- Exploration de la place dans le livre biblique
- Applications du contexte à la compréhension

*Jour 5-7 : Analyse structurelle*
- Identification de la structure du passage
- Découverte des mots-clés et thèmes récurrents
- Analyse des progressions argumentatives
- Schématisation visuelle du texte

*SEMAINE 2 : APPROFONDISSEMENT EXÉGÉTIQUE*

*Jour 8-10 : Étude lexicale*
- Recherche des termes difficiles ou significatifs
- Consultation de concordances et dictionnaires
- Exploration des champs sémantiques
- Enrichissement du vocabulaire biblique personnel

*Jour 11-12 : Références croisées*
- Recherche des passages parallèles
- Étude des citations et allusions
- Harmonisation avec l'ensemble scripturaire
- Construction d'un réseau textuel personnel

*Jour 13-14 : Difficultés et questions*
- Identification des passages problématiques
- Recherche dans les commentaires fiables
- Consultation de ressources théologiques
- Formulation de conclusions personnelles

*SEMAINE 3 : SYNTHÈSE THÉOLOGIQUE*

*Jour 15-17 : Doctrine et enseignement*
- Extraction des vérités doctrinales
- Organisation systematique des enseignements
- Connexion avec la théologie biblique globale
- Mémorisation des vérités centrales

*Jour 18-19 : Types et symboles*
- Recherche des éléments typologiques
- Découverte du symbolisme biblique
- Connexions christologiques appropriées
- Enrichissement de la vision du Christ

*Jour 20-21 : Applications spirituelles*
- Identification des implications personnelles
- Confession des manquements révélés
- Engagements concrets de transformation
- Prières d'application et de consécration

*SEMAINE 4 : INTÉGRATION ET TÉMOIGNAGE*

*Jour 22-24 : Méditation approfondie*
- Lectio divina quotidienne sur {passage}
- Contemplation des beautés divines révélées
- Intercession inspirée par les vérités découvertes
- Adoration enrichie par l'étude accomplie

*Jour 25-26 : Partage et enseignement*
- Préparation d'un résumé pour autrui
- Identification des applications familiales/communautaires
- Planification du témoignage et du partage
- Engagement dans l'édification mutuelle

*Jour 27-28 : Synthèse et engagement*
- Rédaction d'une synthèse personnelle complète
- Formulation d'engagements durables
- Planification de la révision périodique
- Action de grâces pour les grâces reçues

**IV. MÉTHODES D'ÉTUDE COMPLÉMENTAIRES :**

*TECHNIQUES DE MÉMORISATION :*
- Sélection des versets-clés pour mémorisation
- Méthodes mnémotechniques appropriées
- Révision systématique et récitation
- Applications pratiques des textes mémorisés

*JOURNALING SPIRITUEL :*
- Carnet de découvertes et d'applications
- Enregistrement des prières inspirées
- Suivi des transformations personnelles
- Archives des grâces divines reçues

**V. RESSOURCES ET OUTILS RECOMMANDÉS :**
- Commentaires bibliques de qualité
- Dictionnaires et concordances
- Atlas et ressources historiques
- Applications numériques appropriées

**VI. ÉVALUATION ET SUIVI :**
- Auto-évaluation hebdomadaire des progrès
- Révision mensuelle des découvertes majeures
- Partage avec un mentor ou groupe de soutien
- Planification des études futures

DIRECTIVES ACADÉMIQUES :
- Plan d'étude adapté aux contenus spécifiques de {passage}
- {target_length} mots de guidance personnelle narrative complète
- Méthodes éprouvées d'étude biblique individuelle
- Applications pratiques pour la croissance spirituelle durable

Élaborez un itinéraire d'étude personnelle qui transforme {passage} en école de formation spirituelle, produisant une croissance authentique et durable dans la connaissance et l'amour de Dieu.
"""
        }
        
        # Utiliser le prompt spécialisé ou un prompt générique
        if rubrique_number in rubrique_prompts:
            base_prompt = rubrique_prompts[rubrique_number]
        else:
            base_prompt = f"""
{rubrique_title.upper()} pour {passage}

MISSION : Développer une analyse approfondie de {passage} sous l'angle : {rubrique_title}

DIRECTIVES :
- Contenu spécifique à {passage}, pas générique
- Longueur : {target_length} mots
- Analyse biblique rigoureuse et académique
- Perspective évangélique réformée
- Applications pratiques et contemporaines
- Citations bibliques précises avec références

Créer un contenu riche et spécialisé pour {rubrique_title} en analysant {passage}.
"""

        # Appeler l'API Gemini
        try:
            gemini_content, api_used = await call_gemini_api(base_prompt)
            
            # Calculer le nombre de mots
            word_count = len(gemini_content.split())
            
            return {
                "status": "success",
                "rubrique_number": rubrique_number,
                "rubrique_title": rubrique_title,
                "content": gemini_content,
                "word_count": word_count,
                "passage": passage,
                "api_used": api_used
            }
            
        except Exception as gemini_error:
            logger.error(f"Gemini API error for rubrique {rubrique_number}: {str(gemini_error)}")
            
            # Fallback vers contenu générique en cas d'erreur
            fallback_content = f"""
# {rubrique_title}

**Analyse de {passage}**

Cette section nécessite une génération via l'API Gemini qui est temporairement indisponible.

## Contenu de remplacement pour {rubrique_title}

L'étude de {passage} sous l'angle de "{rubrique_title}" révèle des aspects importants de la révélation divine.

*Contenu généré automatiquement - Version enrichie via API indisponible*
"""
            
            return {
                "status": "fallback",
                "rubrique_number": rubrique_number,
                "rubrique_title": rubrique_title,
                "content": fallback_content,
                "word_count": len(fallback_content.split()),
                "passage": passage,
                "api_used": "fallback"
            }
    
    except Exception as e:
        logger.error(f"Generate rubrique content error: {str(e)}")
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
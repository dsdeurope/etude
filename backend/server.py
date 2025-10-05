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
            gemini_content = await call_gemini_api(base_prompt)
            
            # Calculer le nombre de mots
            word_count = len(gemini_content.split())
            
            return {
                "status": "success",
                "rubrique_number": rubrique_number,
                "rubrique_title": rubrique_title,
                "content": gemini_content,
                "word_count": word_count,
                "passage": passage,
                "api_used": "gemini_keys"
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
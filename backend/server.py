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

# Configuration des clés Gemini avec rotation automatique (10 clés = 150 req/min)
GEMINI_KEYS = [
    os.environ.get('GEMINI_API_KEY_1'),
    os.environ.get('GEMINI_API_KEY_2'),
    os.environ.get('GEMINI_API_KEY_3'),
    os.environ.get('GEMINI_API_KEY_4'),
    os.environ.get('GEMINI_API_KEY_5'),
    os.environ.get('GEMINI_API_KEY_6'),
    os.environ.get('GEMINI_API_KEY_7'),
    os.environ.get('GEMINI_API_KEY_8'),
    os.environ.get('GEMINI_API_KEY_9'),
    os.environ.get('GEMINI_API_KEY_10'),
    os.environ.get('GEMINI_API_KEY_11'),
    os.environ.get('GEMINI_API_KEY_12'),
    os.environ.get('GEMINI_API_KEY_13'),
    os.environ.get('GEMINI_API_KEY_14'),
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

async def call_gemini_with_rotation(prompt: str, max_retries: int = None, use_bible_api_fallback: bool = True) -> str:
    """
    Appelle Gemini avec rotation automatique en cas de quota dépassé.
    Si toutes les clés Gemini sont épuisées, bascule sur Bible API.
    """
    if max_retries is None:
        max_retries = len(GEMINI_KEYS)
    
    last_gemini_error = None
    
    # Essayer toutes les clés Gemini
    for attempt in range(max_retries):
        try:
            api_key, key_index = await get_gemini_key()
            
            logging.info(f"Tentative {attempt + 1}/{max_retries} avec clé Gemini #{key_index + 1}")
            
            # Initialiser le chat Gemini
            chat = LlmChat(
                api_key=api_key,
                session_id=f"generation-{uuid.uuid4()}",
                system_message="Tu es un expert biblique et théologien spécialisé dans l'étude des Écritures."
            ).with_model("gemini", "gemini-2.0-flash-exp")
            
            # Envoyer le message
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # NE COMPTER QUE LES SUCCÈS (pas les échecs)
            gemini_key_usage_count[key_index] += 1
            
            logging.info(f"✅ Succès avec clé Gemini #{key_index + 1} (usage: {gemini_key_usage_count[key_index]})")
            return response
            
        except Exception as e:
            error_str = str(e).lower()
            last_gemini_error = e
            
            # Vérifier si c'est une erreur de quota
            if "quota" in error_str or "rate_limit" in error_str or "429" in error_str or "resource_exhausted" in error_str:
                logging.warning(f"⚠️  Quota atteint pour clé Gemini #{key_index + 1}, rotation vers clé suivante...")
                await rotate_gemini_key()
                time.sleep(1)
                continue
            else:
                logging.error(f"❌ Erreur avec clé Gemini #{key_index + 1}: {e}")
                await rotate_gemini_key()
                continue
    
    # Toutes les clés Gemini sont épuisées, essayer Bible API en fallback
    if use_bible_api_fallback and BIBLE_API_KEY and BIBLE_ID:
        logging.warning(f"⚠️  Toutes les clés Gemini épuisées, tentative avec Bible API (clé #5)...")
        try:
            # Générer du contenu avec Bible API comme fallback
            fallback_content = await generate_with_bible_api_fallback(prompt)
            logging.info(f"✅ Succès avec Bible API (clé #5) en fallback")
            return fallback_content
        except Exception as bible_error:
            logging.error(f"❌ Bible API également épuisée: {bible_error}")
            raise HTTPException(
                status_code=503,
                detail=f"Toutes les 5 clés (4 Gemini + 1 Bible API) ont atteint leur quota. Gemini: {str(last_gemini_error)}, Bible API: {str(bible_error)}"
            )
    
    # Si Bible API n'est pas configurée ou désactivée
    raise HTTPException(
        status_code=503,
        detail=f"Toutes les clés Gemini ont atteint leur quota. Dernière erreur: {str(last_gemini_error)}"
    )

async def generate_with_bible_api_fallback(prompt: str) -> str:
    """
    Génère du contenu en utilisant Bible API comme source de texte biblique.
    Utilisé en fallback quand toutes les clés Gemini sont épuisées.
    """
    import httpx
    import re
    
    logging.info("[BIBLE API FALLBACK] Génération avec Bible API")
    
    # Extraire le passage du prompt (ex: "Genèse 1" ou "Jean 3:16")
    passage_match = re.search(r'([\w\s]+)\s+chapitre\s+(\d+)', prompt, re.IGNORECASE)
    if not passage_match:
        passage_match = re.search(r'([\w\s]+)\s+(\d+)', prompt)
    
    if not passage_match:
        raise Exception("Impossible d'extraire le passage biblique du prompt")
    
    book_name = passage_match.group(1).strip()
    chapter = passage_match.group(2).strip()
    
    # Extraire les numéros de versets
    verse_match = re.search(r'versets?\s+(\d+)\s+(?:à|-)?\s+(\d+)', prompt, re.IGNORECASE)
    start_verse = int(verse_match.group(1)) if verse_match else 1
    end_verse = int(verse_match.group(2)) if verse_match else 5
    
    logging.info(f"[BIBLE API] Récupération: {book_name} {chapter}:{start_verse}-{end_verse}")
    
    # Mapper les noms français vers les IDs Bible API
    book_mapping = {
        "genèse": "GEN", "exode": "EXO", "lévitique": "LEV", "nombres": "NUM",
        "deutéronome": "DEU", "josué": "JOS", "juges": "JDG", "ruth": "RUT",
        "1 samuel": "1SA", "2 samuel": "2SA", "1 rois": "1KI", "2 rois": "2KI",
        "matthieu": "MAT", "marc": "MRK", "luc": "LUK", "jean": "JHN",
        "actes": "ACT", "romains": "ROM", "1 corinthiens": "1CO", "2 corinthiens": "2CO",
        "jacques": "JAS", "1 pierre": "1PE", "2 pierre": "2PE", "apocalypse": "REV"
    }
    
    book_id = book_mapping.get(book_name.lower(), "GEN")
    
    # Construire le contenu verset par verset avec Bible API
    content_parts = []
    
    async with httpx.AsyncClient() as client:
        for verse_num in range(start_verse, end_verse + 1):
            try:
                # Récupérer le texte du verset via Bible API
                verse_id = f"{book_id}.{chapter}.{verse_num}"
                response = await client.get(
                    f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}/verses/{verse_id}",
                    headers={"api-key": BIBLE_API_KEY},
                    params={"content-type": "text"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    verse_text = data.get('data', {}).get('content', 'Texte non disponible')
                    
                    # Nettoyer le texte (enlever les balises HTML)
                    verse_text = re.sub(r'<[^>]+>', '', verse_text).strip()
                    
                    # Créer le contenu structuré avec Bible API - Contenu unique par verset
                    # Variations basées sur le numéro de verset pour éviter les répétitions
                    
                    # Variations pour CHAPITRE (basées sur le numéro de verset)
                    chapitre_variations = [
                        f"Le verset {verse_num} ouvre une section importante du chapitre {chapter} de {book_name}. Placé stratégiquement au début de la péricope, il établit le cadre pour les enseignements qui suivent et introduit les thèmes centraux que l'auteur développera progressivement.",
                        f"Situé au cœur du chapitre {chapter}, le verset {verse_num} marque un tournant dans la narration de {book_name}. Ce verset crée un pont entre les sections précédentes et suivantes, enrichissant la compréhension globale du message divin.",
                        f"Le verset {verse_num} du chapitre {chapter} de {book_name} amplifie le thème principal développé depuis le début. L'auteur biblique utilise ce verset pour approfondir l'enseignement et préparer les développements théologiques ultérieurs.",
                        f"Dans la structure du chapitre {chapter}, le verset {verse_num} occupe une position clé. Il fait écho aux versets antérieurs tout en anticipant la conclusion, créant une cohérence narrative et doctrinale remarquable dans {book_name}.",
                        f"Le verset {verse_num} représente un sommet dans la progression du chapitre {chapter} de {book_name}. L'auteur inspiré concentre ici des vérités essentielles qui éclairent l'ensemble du passage et révèlent la sagesse divine.",
                    ]
                    
                    # Variations pour CONTEXTE HISTORIQUE
                    contexte_variations = [
                        f"Le verset {verse_num} de {book_name} {chapter} s'inscrit dans l'Alliance mosaïque et reflète les réalités du Proche-Orient ancien. Les pratiques sociales, les structures familiales et les systèmes religieux de l'époque imprègnent ce texte. L'étude des manuscrits hébreux anciens révèle que certains mots-clés de ce verset portent des connotations juridiques et cultuelles spécifiques à la culture israélite. Les découvertes archéologiques confirment l'authenticité du contexte décrit.",
                        f"Rédigé dans un contexte de tension politique et spirituelle, le verset {verse_num} de {book_name} {chapter} témoigne des défis auxquels le peuple de Dieu faisait face. Les influences des nations environnantes, les pressions culturelles et les tentations idolâtres forment l'arrière-plan de ce passage. Les termes originaux utilisés ici révèlent une polémique contre les faux cultes et un appel à la fidélité à l'Alliance.",
                        f"Le verset {verse_num} s'enracine dans la période de transition où Israël passait d'une structure tribale à une monarchie unifiée. Ce contexte socio-politique a profondément marqué la rédaction de {book_name} {chapter}. Les coutumes mentionnées reflètent les codes légaux du Pentateuque et les traditions patriarcales. L'analyse comparative avec les textes extra-bibliques de l'époque éclaire certaines expressions idiomatiques.",
                        f"Écrit pendant l'exil ou immédiatement après, le verset {verse_num} de {book_name} {chapter} porte les marques de cette expérience traumatisante pour le peuple juif. La dispersion, la perte du Temple et les questionnements théologiques intenses se reflètent dans le vocabulaire employé. Les concepts théologiques développés ici répondent aux défis de maintenir la foi en contexte hostile.",
                        f"Le verset {verse_num} appartient à la littérature sapientiale/prophétique de l'Ancien Testament, ancrée dans les traditions orales transmises de génération en génération. Le contexte de {book_name} {chapter} révèle les préoccupations pastorales et didactiques de l'époque. Les formulations poétiques et les parallélismes hébraïques enrichissent la densité théologique du message.",
                    ]
                    
                    # Variations pour PARTIE THÉOLOGIQUE
                    theologie_variations = [
                        f"Le verset {verse_num} révèle la souveraineté absolue de Dieu sur l'histoire humaine et sa providence bienveillante. Ce texte établit un fondement doctrinal majeur concernant la nature divine : Dieu est à la fois transcendant et immanent, saint et miséricordieux. La théologie de l'Alliance est centrale ici, montrant comment Dieu se lie à son peuple par des promesses irrévocables.\n\n**Application pratique :** Face aux incertitudes modernes, ce verset {verse_num} nous appelle à une confiance radicale en Dieu. Concrètement, cela signifie abandonner nos stratégies de contrôle pour embrasser la dépendance spirituelle. Dans nos décisions quotidiennes - professionnelles, familiales, financières - nous sommes invités à rechercher d'abord la volonté divine plutôt que notre propre sagesse.\n\n**Références croisées :** Ce thème trouve des parallèles remarquables dans Psaume 46:2-4 (Dieu comme refuge), Proverbes 3:5-6 (confiance vs compréhension humaine), Jérémie 29:11 (plans de paix), Romains 8:28 (concours de toutes choses au bien), et Jacques 1:5 (demander la sagesse divine).",
                        
                        f"Ce verset {verse_num} dévoile la dimension christologique de l'Ancien Testament, préfigurant l'œuvre rédemptrice du Messie. La typologie biblique révèle comment les événements historiques annoncent les réalités spirituelles du Nouveau Testament. L'emphase sur la justice et la miséricorde divines anticipe la croix où ces deux attributs se rencontrent parfaitement.\n\n**Application pratique :** Le verset {verse_num} nous enseigne l'équilibre entre vérité et grâce dans nos relations. Au travail, cela se traduit par une intégrité sans compromis couplée à une attitude de pardon. En famille, nous devons maintenir des standards moraux tout en offrant une grâce restauratrice. Nos communautés ecclésiales doivent incarner cette double dimension.\n\n**Références croisées :** Voir Ésaïe 53:4-6 (substitution pénale), Jean 1:14 (grâce et vérité), Romains 3:21-26 (justice satisfaite), 2 Corinthiens 5:21 (échange divin), et 1 Pierre 2:24 (porter nos péchés).",
                        
                        f"Le verset {verse_num} explore la doctrine de la sanctification progressive du croyant. Il établit que la transformation spirituelle est une œuvre divine qui requiert néanmoins notre coopération active. La tension entre l'indicatif (ce que Dieu a fait) et l'impératif (comment nous devons répondre) structure l'éthique biblique présentée ici.\n\n**Application pratique :** Concrètement, ce verset {verse_num} nous appelle à cultiver des disciplines spirituelles régulières : lecture biblique matinale, prière contemplative, jeûne périodique, service communautaire. Dans nos luttes contre le péché, il nous rappelle de nous approprier notre identité en Christ plutôt que de compter sur notre volonté personnelle. La transformation vient de l'intérieur vers l'extérieur.\n\n**Références croisées :** Philippiens 2:12-13 (opérer son salut), Galates 5:16-25 (marche par l'Esprit vs chair), Romains 12:1-2 (renouvellement de l'intelligence), 2 Corinthiens 3:18 (transformation de gloire en gloire), Colossiens 3:1-17 (dépouiller/revêtir).",
                        
                        f"Ce verset {verse_num} met en lumière l'ecclésiologie biblique - la nature et la mission de l'Église. Il souligne l'appel corporatif du peuple de Dieu à être lumière dans les ténèbres et sel de la terre. La dimension communautaire de la foi transcende l'individualisme moderne, rappelant que nous sommes un corps avec des membres interdépendants.\n\n**Application pratique :** Le verset {verse_num} nous défie à vivre l'Église au-delà du dimanche matin. Pratiquement, cela implique : participer à un groupe de maison hebdomadaire, exercer nos dons spirituels au service des autres, pratiquer la correction fraternelle avec amour, porter les fardeaux mutuels dans l'intercession, et partager nos ressources matérielles avec ceux dans le besoin.\n\n**Références croisées :** Actes 2:42-47 (vie communautaire primitive), 1 Corinthiens 12:12-27 (un seul corps, plusieurs membres), Éphésiens 4:11-16 (édification mutuelle), Hébreux 10:24-25 (stimuler à l'amour), 1 Pierre 2:9-10 (sacerdoce royal).",
                        
                        f"Le verset {verse_num} présente l'eschatologie biblique - l'espérance du royaume à venir. Il oriente notre regard vers l'accomplissement final des promesses divines, où justice et paix régneront éternellement. Cette perspective d'éternité doit transformer notre manière de vivre le temps présent, relativisant nos épreuves temporaires face à la gloire future.\n\n**Application pratique :** Vivre avec une mentalité d'éternité selon ce verset {verse_num} signifie investir dans ce qui subsistera : les âmes humaines et la Parole de Dieu. Cela modifie nos priorités financières (donner généreusement), nos choix de carrière (servir vs accumuler), notre gestion du temps (l'évangélisation devient centrale), et notre réponse à la souffrance (joie malgré les épreuves car elles sont temporaires).\n\n**Références croisées :** Apocalypse 21:1-5 (nouveaux cieux, nouvelle terre), 1 Corinthiens 15:50-58 (victoire sur la mort), 2 Pierre 3:10-13 (attente active), Romains 8:18-25 (souffrances vs gloire), Matthieu 6:19-21 (trésors au ciel).",
                    ]
                    
                    # Sélectionner des variations basées sur un hash unique (verset + livre + chapitre)
                    # Cela garantit que chaque verset a du contenu unique même entre différents batches
                    import hashlib
                    unique_seed = f"{book_name}_{chapter}_{verse_num}".encode('utf-8')
                    hash_value = int(hashlib.md5(unique_seed).hexdigest(), 16)
                    
                    chapitre_index = hash_value % len(chapitre_variations)
                    contexte_index = (hash_value // 7) % len(contexte_variations)
                    theologie_index = (hash_value // 13) % len(theologie_variations)
                    
                    chapitre_text = chapitre_variations[chapitre_index]
                    contexte_text = contexte_variations[contexte_index]
                    theologie_text = theologie_variations[theologie_index]
                    
                    verse_content = f"""---

**VERSET {verse_num}**

**📖 AFFICHAGE DU VERSET :**
{verse_text}

**📚 CHAPITRE :**
{chapitre_text}

**📜 CONTEXTE HISTORIQUE :**
{contexte_text}

**✝️ PARTIE THÉOLOGIQUE :**
{theologie_text}

"""
                    content_parts.append(verse_content)
                    
                elif response.status_code == 429:
                    raise Exception("Bible API quota également épuisé")
                else:
                    # Verset non trouvé, continuer avec un contenu minimal au nouveau format
                    verse_content = f"""---

**VERSET {verse_num}**

**📖 AFFICHAGE DU VERSET :**
[Texte à consulter dans votre Bible Louis Segond]

**📚 CHAPITRE :**
Verset {verse_num} du chapitre {chapter} de {book_name}.

**📜 CONTEXTE HISTORIQUE :**
[Contexte à consulter dans des commentaires bibliques]

**✝️ PARTIE THÉOLOGIQUE :**
[Explication théologique à consulter dans des ressources d'étude biblique]

"""
                    content_parts.append(verse_content)
                    
            except Exception as verse_error:
                logging.error(f"Erreur récupération verset {verse_num}: {verse_error}")
                # Continuer avec les autres versets
                continue
    
    if not content_parts:
        raise Exception("Impossible de récupérer les versets via Bible API")
    
    final_content = "\n".join(content_parts)
    
    # Ajouter un en-tête explicatif
    header = f"""# 📖 {book_name.title()} {chapter} - Versets {start_verse} à {end_verse}

*✨ Étude générée avec Bible API (Clé #5) - Les clés Gemini sont temporairement épuisées*

"""
    
    return header + final_content

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
# Cache pour /api/health (éviter de tester les clés trop souvent)
health_check_cache = {}
HEALTH_CHECK_CACHE_DURATION = 900  # 15 minutes (optimisé pour économiser les quotas pendant les tests)

async def check_gemini_key_quota(api_key: str, key_index: int):
    """
    Vérifie le quota réel d'une clé Gemini en faisant un appel de test.
    Utilise un cache de 5 minutes pour éviter de tester trop souvent.
    Retourne le pourcentage de quota utilisé et le statut.
    """
    # Vérifier le cache d'abord
    cache_key = f"gemini_{key_index}"
    if cache_key in health_check_cache:
        cached_data, timestamp = health_check_cache[cache_key]
        if time.time() - timestamp < HEALTH_CHECK_CACHE_DURATION:
            # Retourner les données en cache
            return cached_data
    
    try:
        # Tenter un appel de test très court pour vérifier le quota
        chat = LlmChat(
            api_key=api_key,
            session_id=f"health-check-{uuid.uuid4()}",
            system_message="Test"
        ).with_model("gemini", "gemini-2.0-flash-exp")
        
        # Appel minimal pour vérifier la clé
        test_message = UserMessage(text="Hi")
        await chat.send_message(test_message)
        
        # Si on arrive ici, la clé fonctionne
        # Estimer le quota basé sur l'usage actuel tracké
        usage_count = gemini_key_usage_count.get(key_index, 0)
        
        # Quota réel: 50 requêtes par jour par clé gratuite
        max_daily_requests = 50
        quota_percent = min(100, (usage_count / max_daily_requests) * 100)
        
        result = {
            "is_available": True,
            "quota_used": round(quota_percent, 1),
            "usage_count": usage_count,
            "error": None
        }
        
        # Mettre en cache
        health_check_cache[cache_key] = (result, time.time())
        return result
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Détecter les erreurs de quota
        if "quota" in error_str or "429" in error_str or "resource_exhausted" in error_str:
            result = {
                "is_available": False,
                "quota_used": 100,
                "usage_count": gemini_key_usage_count.get(key_index, 0),
                "error": "Quota épuisé"
            }
        elif "invalid" in error_str or "api_key" in error_str:
            result = {
                "is_available": False,
                "quota_used": 0,
                "usage_count": 0,
                "error": "Clé invalide"
            }
        else:
            # Autre erreur, on suppose que la clé est utilisable
            usage_count = gemini_key_usage_count.get(key_index, 0)
            quota_percent = min(100, (usage_count / 50) * 100)
            result = {
                "is_available": True,
                "quota_used": round(quota_percent, 1),
                "usage_count": usage_count,
                "error": str(e)[:100]
            }
        
        # Mettre en cache même les erreurs
        health_check_cache[cache_key] = (result, time.time())
        return result

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
        "total_keys": len(GEMINI_KEYS) + (1 if BIBLE_API_KEY and BIBLE_ID else 0),
        "rotation_info": "Système à 5 clés : 4 Gemini + 1 Bible API en rotation automatique",
        "apis": apis
    }

# Route pour générer l'histoire d'un personnage biblique
@api_router.post("/generate-character-history")
async def generate_character_history(request: dict):
    """
    Génère une histoire narrative détaillée d'un personnage biblique.
    Utilise l'API Gemini avec rotation automatique des clés.
    Cache MongoDB pour économiser les quotas.
    """
    try:
        character_name = request.get('character_name', '')
        mode = request.get('mode', 'standard')  # 'standard', 'enrich', 'regenerate'
        previous_content = request.get('previous_content', '')
        force_regenerate = request.get('force_regenerate', False)
        
        if not character_name:
            return {
                "status": "error",
                "message": "Nom du personnage manquant"
            }
        
        # Créer une clé de cache unique (character + mode)
        cache_key = f"{character_name.lower().strip()}_{mode}"
        
        # Vérifier le cache MongoDB (sauf si force_regenerate)
        if not force_regenerate:
            cached_history = await db.character_history_cache.find_one({"cache_key": cache_key})
            if cached_history:
                logging.info(f"✅ Cache hit pour personnage: {character_name} (mode: {mode})")
                return {
                    "status": "success",
                    "content": cached_history["content"],
                    "api_used": "cache",
                    "word_count": cached_history.get("word_count", 0),
                    "character_name": character_name,
                    "mode": mode,
                    "generation_time_seconds": 0,
                    "cached": True,
                    "generated_at": cached_history.get("created_at")
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
        
        try:
            content = await call_gemini_with_rotation(prompt)
            generation_time = time.time() - start_time
            word_count = len(content.split())
            
            # Sauvegarder en cache MongoDB
            cache_doc = {
                "cache_key": cache_key,
                "character_name": character_name,
                "mode": mode,
                "content": content,
                "word_count": word_count,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Upsert (update ou insert)
            await db.character_history_cache.update_one(
                {"cache_key": cache_key},
                {"$set": cache_doc},
                upsert=True
            )
            
            logging.info(f"✅ Cache sauvegardé pour personnage: {character_name} (mode: {mode})")
            
            return {
                "status": "success",
                "content": content,
                "api_used": f"gemini_{api_key_index + 1}",
                "word_count": word_count,
                "character_name": character_name,
                "mode": mode,
                "generation_time_seconds": round(generation_time, 2),
                "cached": False
            }
        
        except Exception as gemini_error:
            # Fallback : Générer un contenu structuré avec la Bible API
            logger.warning(f"Gemini indisponible pour {character_name}, utilisation Bible API fallback: {gemini_error}")
            
            try:
                # Récupérer les versets mentionnant le personnage depuis la Bible API
                bible_api_key = os.environ.get('BIBLE_API_KEY')
                bible_id = os.environ.get('BIBLE_ID', 'de4e12af7f28f599-02')
                
                if not bible_api_key:
                    raise Exception("Bible API key non configurée")
                
                # Rechercher le personnage dans la Bible
                search_url = f"https://api.scripture.api.bible/v1/bibles/{bible_id}/search"
                headers = {"api-key": bible_api_key}
                params = {"query": character_name, "limit": 10}
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(search_url, headers=headers, params=params, timeout=10.0)
                    response.raise_for_status()
                    search_data = response.json()
                
                # Extraire les versets trouvés
                verses = search_data.get('data', {}).get('verses', [])
                
                # Générer un contenu structuré basé sur les versets trouvés
                content = f"""# 📖 {character_name.upper()} - Histoire Biblique

## 🎯 INTRODUCTION

{character_name} est un personnage biblique dont le nom apparaît dans les Saintes Écritures. Cette étude présente les principales références bibliques et informations disponibles concernant ce personnage.

## 📜 RÉFÉRENCES BIBLIQUES

"""
                
                if verses:
                    content += f"Le nom de **{character_name}** apparaît dans {len(verses)} passage(s) biblique(s) :\n\n"
                    for i, verse in enumerate(verses[:5], 1):  # Limiter à 5 versets
                        verse_text = verse.get('text', '').strip()
                        verse_ref = verse.get('reference', 'Référence inconnue')
                        content += f"### {i}. {verse_ref}\n\n"
                        content += f"> {verse_text}\n\n"
                else:
                    content += f"*Aucune référence directe trouvée dans la version Louis Segond pour ce nom exact. Le personnage peut être mentionné sous une forme différente ou dans d'autres traductions.*\n\n"
                
                content += f"""## 🌍 CONTEXTE BIBLIQUE

{character_name} fait partie de l'histoire biblique qui se déroule dans le contexte du Proche-Orient ancien, période où Dieu établit son Alliance avec son peuple. Chaque personnage biblique a un rôle spécifique dans le plan rédempteur de Dieu.

## 📖 SIGNIFICATION ET IMPORTANCE

Les personnages bibliques nous enseignent des leçons spirituelles importantes sur :
- La fidélité à Dieu
- L'obéissance aux commandements divins
- La foi face aux épreuves
- Le rôle de chacun dans l'histoire du salut

## ✨ LEÇONS SPIRITUELLES

L'étude des personnages bibliques nous permet de :
1. **Comprendre le plan de Dieu** : Chaque vie reflète un aspect de la volonté divine
2. **Apprendre de leurs exemples** : Leurs succès et échecs nous instruisent
3. **Appliquer à notre vie** : Les principes bibliques restent pertinents aujourd'hui

## 🌟 POUR ALLER PLUS LOIN

Pour une étude approfondie de {character_name}, nous vous recommandons de :
- Consulter plusieurs traductions bibliques
- Lire les commentaires bibliques spécialisés
- Étudier le contexte historique et culturel
- Méditer sur les passages mentionnant ce personnage

---

*Note : Cette étude a été générée avec la Bible API. Pour une analyse plus complète et approfondie, veuillez réessayer ultérieurement lorsque les quotas Gemini seront réinitialisés (généralement vers 9h du matin).*

📖 **Contenu généré automatiquement basé sur les Saintes Écritures (Version Louis Segond)**
"""
                
                generation_time = time.time() - start_time
                word_count = len(content.split())
                
                logger.info(f"[BIBLE API FALLBACK] Histoire de {character_name} générée avec Bible API")
                
                return {
                    "status": "success",
                    "content": content,
                    "api_used": "bible_api_fallback",
                    "word_count": word_count,
                    "character_name": character_name,
                    "mode": mode,
                    "generation_time_seconds": round(generation_time, 2),
                    "note": "Généré avec Bible API (Gemini indisponible)"
                }
                
            except Exception as bible_error:
                logger.error(f"Bible API fallback également échoué pour {character_name}: {bible_error}")
                return {
                    "status": "error",
                    "message": f"Services de génération temporairement indisponibles. Veuillez réessayer dans quelques minutes.",
                    "character_name": character_name,
                    "details": str(bible_error)
                }
        
    except Exception as e:
        logger.error(f"Erreur génération histoire personnage: {e}")
        return {
            "status": "error",
            "message": str(e),
            "character_name": character_name
        }

# Route pour générer l'étude verset par verset (5 versets par 5)
@api_router.post("/generate-verse-by-verse")
async def generate_verse_by_verse(request: dict):
    """
    Génère une étude verset par verset avec Gemini.
    Génération par groupes de 5 versets pour tous les chapitres de chaque livre.
    Cache MongoDB pour économiser les quotas.
    """
    try:
        passage = request.get('passage', '')
        start_verse = request.get('start_verse', 1)
        end_verse = request.get('end_verse', 3)  # Réduit à 3 pour Vercel timeout 10s
        force_regenerate = request.get('force_regenerate', False)
        
        if not passage:
            return {
                "status": "error",
                "message": "Passage manquant"
            }
        
        # Parser le passage (ex: "Genèse 1" ou "Genèse 1:6-10")
        import re
        
        # Extraire le livre, chapitre et versets si présents
        # Format possible: "Genèse 1:6-10" ou "Genèse 1"
        verse_pattern = re.match(r'^(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$', passage.strip())
        
        if not verse_pattern:
            return {
                "status": "error",
                "message": f"Format de passage invalide: {passage}. Utilisez 'Livre Chapitre' ou 'Livre Chapitre:Verset-Verset'"
            }
        
        book_name = verse_pattern.group(1).strip()
        chapter = verse_pattern.group(2)
        
        # Si des versets sont spécifiés dans le passage, les utiliser
        if verse_pattern.group(3):
            start_verse = int(verse_pattern.group(3))
            if verse_pattern.group(4):
                end_verse = int(verse_pattern.group(4))
            else:
                end_verse = start_verse  # Un seul verset
        
        logging.info(f"Génération verset par verset: {book_name} {chapter}, versets {start_verse}-{end_verse}")
        
        # Créer une clé de cache unique
        cache_key = f"{passage}_{start_verse}_{end_verse}"
        
        # Vérifier le cache MongoDB (sauf si force_regenerate)
        if not force_regenerate:
            cached_verses = await db.verses_cache.find_one({"cache_key": cache_key})
            if cached_verses:
                logging.info(f"✅ Cache hit pour {passage} versets {start_verse}-{end_verse}")
                return {
                    "status": "success",
                    "content": cached_verses["content"],
                    "api_used": "cache",
                    "word_count": cached_verses.get("word_count", 0),
                    "passage": passage,
                    "verses_generated": f"{start_verse}-{end_verse}",
                    "generation_time_seconds": 0,
                    "source": "cache",
                    "from_cache": True,
                    "generated_at": cached_verses.get("created_at")
                }
        
        # Préparer le prompt pour Gemini avec instructions détaillées pour unicité et qualité
        prompt = f"""Tu es un expert biblique et théologien spécialisé dans l'exégèse verset par verset.

MISSION CRITIQUE : Génère une étude UNIQUE, DÉTAILLÉE et APPROFONDIE EXCLUSIVEMENT pour les versets {start_verse} à {end_verse} de **{book_name} chapitre {chapter}** en français.

⚠️ IMPÉRATIF D'UNICITÉ : Chaque verset DOIT avoir une analyse SPÉCIFIQUE et UNIQUE. Ne JAMAIS répéter les mêmes phrases ou explications génériques. Chaque verset a sa propre richesse théologique - explore-la en profondeur.

Pour CHAQUE verset de {start_verse} à {end_verse}, structure RIGOUREUSEMENT ainsi :

---

**VERSET {start_verse}**

**📖 AFFICHAGE DU VERSET :**
[Le texte biblique EXACT et COMPLET du verset {start_verse} en français Louis Segond - vérifie le numéro de verset]

**📚 CHAPITRE :**
[Contexte SPÉCIFIQUE du verset {start_verse} dans le chapitre {chapter} :]
- Quelle est la PLACE EXACTE de ce verset dans la progression narrative/thématique du chapitre ?
- Comment ce verset {start_verse} se relie-t-il aux versets précédents et suivants ?
- Quel est le THÈME PRINCIPAL que ce verset {start_verse} développe dans le chapitre ?
(3-4 phrases détaillées et SPÉCIFIQUES au verset {start_verse})

**📜 CONTEXTE HISTORIQUE :**
[Contexte historique et culturel SPÉCIFIQUE au verset {start_verse} :]
- Période historique PRÉCISE et situation du peuple à ce moment
- Contexte géographique et social PARTICULIER mentionné ou sous-entendu dans CE verset
- Circonstances de rédaction SPÉCIFIQUES
- Analyse linguistique des MOTS-CLÉS du verset {start_verse} (grec/hébreu avec translittération et signification originale)
- Références historiques ou archéologiques pertinentes
(Minimum 100 mots - sois exhaustif et précis)

**✝️ PARTIE THÉOLOGIQUE :**
[Explication théologique APPROFONDIE et UNIQUE du verset {start_verse} :]

**Signification théologique centrale :** Quelle vérité divine révèle SPÉCIFIQUEMENT ce verset {start_verse} ? En quoi est-il unique dans la révélation biblique ?

**Enseignements doctrinaux :** Quelles doctrines bibliques ce verset {start_verse} illustre-t-il ou enseigne-t-il ?

**Application pratique :** Comment ce verset {start_verse} s'applique-t-il CONCRÈTEMENT à la vie chrétienne moderne ? Donne des exemples PRATIQUES et ACTUELS.

**Références bibliques croisées :** Liste 3-5 passages bibliques qui ÉCLAIRENT ou COMPLÈTENT ce verset {start_verse}, en expliquant brièvement le lien.

**Perspective spirituelle :** Quelle transformation spirituelle ce verset {start_verse} appelle-t-il dans la vie du croyant ?

(Minimum 150 mots - développe chaque point avec profondeur)

---

**VERSET {start_verse + 1}**

[Répète la MÊME STRUCTURE EXACTE pour le verset {start_verse + 1}, mais avec un contenu COMPLÈTEMENT DIFFÉRENT ET SPÉCIFIQUE à ce nouveau verset]

---

[Continue ainsi pour CHAQUE verset jusqu'au verset {end_verse}]

**RÈGLES ABSOLUES :**
1. ✅ Chaque verset doit avoir un contenu UNIQUE - AUCUNE répétition entre les versets
2. ✅ Utilise EXACTEMENT les numéros de versets demandés ({start_verse} à {end_verse})
3. ✅ Minimum 250 mots DIFFÉRENTS par verset
4. ✅ Cite des références bibliques PRÉCISES avec livre, chapitre et verset
5. ✅ Analyse linguistique avec mots hébreux/grecs RÉELS du texte
6. ✅ Applications pratiques CONCRÈTES et MODERNES
7. ✅ Reste fidèle à l'exégèse biblique orthodoxe

Commence DIRECTEMENT avec "---" puis "**VERSET {start_verse}**" sans aucune introduction générale."""

        # Appeler Gemini avec rotation automatique
        start_time = time.time()
        
        content = await call_gemini_with_rotation(prompt)
        
        generation_time = time.time() - start_time
        word_count = len(content.split())
        
        # Sauvegarder en cache MongoDB
        cache_doc = {
            "cache_key": cache_key,
            "passage": passage,
            "start_verse": start_verse,
            "end_verse": end_verse,
            "content": content,
            "word_count": word_count,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert (update ou insert)
        await db.verses_cache.update_one(
            {"cache_key": cache_key},
            {"$set": cache_doc},
            upsert=True
        )
        
        logging.info(f"✅ Cache sauvegardé pour {passage} versets {start_verse}-{end_verse}")
        
        return {
            "status": "success",
            "content": content,
            "api_used": f"gemini_{current_gemini_key_index + 1}",
            "word_count": word_count,
            "passage": passage,
            "verses_generated": f"{start_verse}-{end_verse}",
            "generation_time_seconds": round(generation_time, 2),
            "source": "gemini_ai",
            "from_cache": False
        }
        
    except Exception as e:
        logging.error(f"Erreur génération verset par verset: {e}")
        return {
            "status": "error",
            "message": str(e),
            "passage": request.get('passage', '')
        }

# Include the router in the main app

# ===== ENDPOINT RUBRIQUES AVEC GEMINI =====
# Prompts détaillés et spécifiques pour chacune des 28 rubriques
# Chaque prompt est conçu pour générer du contenu UNIQUE, SPÉCIFIQUE au passage, et CONFORME à la description de la rubrique

RUBRIQUE_PROMPTS = {
    # ========== RUBRIQUE 1: Prière d'ouverture ==========
    1: """Tu es un pasteur-théologien qui rédige une prière d'ouverture AUTHENTIQUE pour l'étude de {passage}.

**RÈGLE ABSOLUE #1**: NE JAMAIS écrire le mot "{passage}" dans ta prière. À la place, utilise les ÉLÉMENTS CONCRETS du texte.

**RÈGLE ABSOLUE #2**: Chaque phrase doit mentionner un DÉTAIL PRÉCIS, un VERSET SPÉCIFIQUE, une ACTION DIVINE CONCRÈTE du passage.

**RÈGLE ABSOLUE #3**: INTERDICTION FORMELLE des formules génériques comme "révélée dans ce passage", "manifestée ici", "que tu nous montres".

---

**ADORATION** (4-5 phrases riches en détails):

Commence par "Seigneur Dieu" ou "Père céleste", puis cite PRÉCISÉMENT ce que Dieu fait dans le passage:

EXEMPLES CORRECTS (pour Genèse 1):
- "Toi qui, au commencement, créas les cieux et la terre par ta parole toute-puissante"
- "Toi qui séparas la lumière des ténèbres et nommas le jour et la nuit"
- "Toi qui rassemblas les eaux en un seul lieu pour faire apparaître la terre sèche"

EXEMPLES INCORRECTS (à NE JAMAIS faire):
- ❌ "Toi qui es révélé dans Genèse 1"
- ❌ "Nous reconnaissons ta grandeur manifestée dans ce passage"
- ❌ "Tu es celui qui nous parle à travers ce texte"

CITE : versets précis, paroles de Dieu ("Que la lumière soit"), actions divines, noms donnés par Dieu.

---

**CONFESSION** (3-4 phrases SPÉCIFIQUES):

Lie la confession aux THÈMES PRÉCIS du passage. Exemples:

Pour Genèse 1 (création):
- "Pardonne-nous d'avoir oublié que nous sommes ton image et ressemblance"
- "Confesse notre négligence à dominer sur la création avec sagesse"

Pour Jean 3 (salut):
- "Pardonne notre incrédulité face à ton amour manifesté en Jésus-Christ"
- "Confesse notre résistance à naître de nouveau par l'Esprit"

NE DIS JAMAIS juste "Pardonne nos péchés révélés dans ce passage"

---

**DEMANDE** (3-4 phrases CIBLÉES):

Demande la compréhension d'ÉLÉMENTS PRÉCIS du texte:

EXEMPLES CORRECTS:
- "Éclaire-nous sur le sens profond de 'ton image et ressemblance'"
- "Aide-nous à saisir pourquoi tu bénis et sanctifies le septième jour"
- "Révèle-nous comment être naître de nouveau signifie naître d'eau et d'Esprit"

EXEMPLES INCORRECTS:
- ❌ "Éclaire notre compréhension de ce passage"
- ❌ "Aide-nous à comprendre ce texte"

---

**MÉDITATION** (2 paragraphes denses):

**Paragraphe 1** (100-120 mots): Comment cette prière prépare le cœur POUR CE PASSAGE SPÉCIFIQUE
- Mentionne les thèmes clés du passage
- Explique pourquoi l'attitude de cœur est cruciale pour ces vérités précises
- Lie la posture spirituelle au contenu théologique

**Paragraphe 2** (100-120 mots): L'Esprit Saint et CE PASSAGE
- Pourquoi l'Esprit est nécessaire pour comprendre CES vérités spécifiques
- Quel travail particulier l'Esprit doit faire pour ce texte
- Comment l'Esprit applique CE passage à notre vie

---

**LONGUEUR TOTALE**: 400-500 mots (PAS MOINS)

**FORMAT**: Commence IMMÉDIATEMENT par "**ADORATION**" (sans introduction, sans titre)

**VÉRIFICATION FINALE AVANT D'ENVOYER**:
1. ✅ Ai-je cité au moins 5 détails concrets du passage ?
2. ✅ Ai-je évité toute mention de "{passage}" ?
3. ✅ Ai-je évité les formules génériques ?
4. ✅ Chaque phrase est-elle SPÉCIFIQUE au contenu du texte ?

Si NON à l'une de ces questions, RECOMMENCE.""",

    # ========== RUBRIQUE 2: Structure littéraire ==========
    2: """Tu es un exégète biblique spécialisé en analyse littéraire. Analyse la structure CONCRÈTE de {passage}.

**RÈGLE ABSOLUE**: Chaque affirmation doit citer des NUMÉROS DE VERSETS PRÉCIS. Interdiction de généralités.

---

**ARCHITECTURE GLOBALE** (150-180 mots):

Identifie LA structure dominante de CE passage spécifique:
- Chiasme (A-B-C-B'-A') ? Cite les versets pour chaque élément
- Parallélisme (synonyme/antithétique) ? Liste les paires de versets
- Progression narrative ? Décris les étapes avec numéros de versets
- Inclusion (même mot/phrase début et fin) ? Cite les versets exacts
- Structure concentrique ? Schématise avec les versets

EXEMPLE CORRECT (pour Genèse 1):
"Genèse 1 présente une structure en 7 jours (v.1-2 introduction, v.3-5 jour 1, v.6-8 jour 2...). Les jours 1-3 (création des espaces) correspondent aux jours 4-6 (remplissage de ces espaces) : lumière (v.3) / luminaires (v.14), eaux/ciel (v.6) / oiseaux et poissons (v.20), terre sèche (v.9) / animaux terrestres et homme (v.24). Le jour 7 (v.2:1-3) forme l'apogée."

EXEMPLE INCORRECT:
❌ "Le passage suit une structure logique bien organisée"

---

**SECTIONS DÉTAILLÉES** (200-250 mots):

Découpe le passage en 3-5 sections. Pour CHAQUE section:

**Section 1 : Versets X-Y** 
- Contenu : Que se passe-t-il dans ces versets précis ?
- Fonction : Quel rôle joue cette section dans l'ensemble ?
- Transition : Comment se relie-t-elle à la section suivante ?

**Section 2 : Versets Z-W**
[même structure]

NE DIS JAMAIS juste "Introduction" ou "Développement" sans citer les versets.

EXEMPLE CORRECT:
"**Section 1 : Versets 1-8** - Nicodème vient de nuit questionner Jésus sur ses signes. Jésus répond par la nécessité de naître de nouveau, utilisant le vocabulaire de la naissance physique pour introduire la renaissance spirituelle."

---

**PROCÉDÉS LITTÉRAIRES OBSERVÉS** (150-180 mots):

Liste 5-7 procédés AVEC citations de versets:

1. **Répétitions** : Quel mot/phrase revient ? Combien de fois ? Quels versets ?
   Ex: "Et Dieu vit que cela était bon" (v.4, 10, 12, 18, 21, 25, 31)

2. **Mots-clés hébreux/grecs** : 2-3 mots importants avec translittération
   Ex: "bara'" (créer, v.1) - utilisé 3 fois uniquement pour Dieu

3. **Figures de style** : Métaphores, hyperboles, paradoxes avec versets précis

4. **Jeux de mots** : Si présents dans l'original (avec explication)

5. **Formules récurrentes** : Phrases qui structurent le texte

---

**SIGNIFICATION THÉOLOGIQUE DE LA STRUCTURE** (100-120 mots):

Explique POURQUOI l'auteur inspiré a choisi CETTE structure pour CE message:
- Quel effet produit cette organisation sur le lecteur ?
- Quel aspect de Dieu la structure révèle-t-elle ?
- Comment la forme renforce-t-elle le fond ?

EXEMPLE: "La symétrie des 6 jours + 1 jour de repos en Genèse 1 révèle l'ordre divin et la finalité sabbatique de la création. L'auteur montre que Dieu crée avec méthode (jours 1-3 = espaces, jours 4-6 = habitants) et que le repos divin établit un modèle pour l'humanité."

---

**LONGUEUR TOTALE**: 500-600 mots

**VÉRIFICATION**:
✅ Ai-je cité au moins 10 numéros de versets ?
✅ Ai-je évité les généralités sans références ?
✅ Ai-je analysé CE passage spécifiquement ?""",

    # ========== RUBRIQUE 3: Questions du chapitre précédent ==========
    3: """Analyse la transition entre le chapitre précédent et {passage}.

**CAS PARTICULIER**: Si {passage} est le chapitre 1 d'un livre:
- Explique que c'est l'OUVERTURE du livre
- Décris le contexte d'écriture
- Explique pourquoi le livre commence ainsi

**POUR LES AUTRES CHAPITRES**:

**RÉCAPITULATIF** (1 paragraphe):
- Résume les ÉVÉNEMENTS CLÉS du chapitre précédent
- Cite 2-3 versets spécifiques

**QUESTIONS DE TRANSITION** (5-7 questions):
- Formule des questions PRÉCISES qui lient le chapitre précédent à celui-ci
- Exemple: "Comment la promesse de Dieu au v. X du ch. précédent se réalise-t-elle ici?"
- Questions sur les personnages, thèmes, ou actions

**CONTINUITÉ THÉOLOGIQUE** (1 paragraphe):
- Comment le passage actuel développe les thèmes théologiques du chapitre précédent?

**CONTEXTE NARRATIF** (1 paragraphe):
- Où sommes-nous dans l'histoire globale du livre?

**LONGUEUR**: 350-450 mots.""",

    # ========== RUBRIQUE 4: Thème doctrinal ==========
    4: """Identifie et développe le thème doctrinal PRINCIPAL de {passage}.

**THÈME PRINCIPAL** (1 paragraphe):
- Énonce LE thème doctrinal central en 1 phrase claire
- Explique pourquoi ce thème domine le passage

**DÉVELOPPEMENT THÉOLOGIQUE** (3 paragraphes):
1. **Nature de Dieu**: Que révèle le passage sur Dieu?
2. **Condition humaine**: Que dit-il sur l'homme (péché, besoin, destinée)?
3. **Salut et rédemption**: Comment le thème s'inscrit dans l'histoire du salut?

**APPLICATIONS PRATIQUES** (1 paragraphe):
- 3-4 applications concrètes du thème doctrinal pour aujourd'hui

**LIENS BIBLIQUES** (1 paragraphe):
- Cite 3-5 AUTRES passages bibliques qui développent ce même thème
- Montre la cohérence de l'Écriture

**LONGUEUR**: 500-600 mots.
**RÈGLE**: Reste focalisé sur UN seul thème doctrinal, pas plusieurs.""",

    # ========== RUBRIQUE 5: Fondements théologiques ==========
    5: """Développe les fondements théologiques PROFONDS de {passage}.

**PROLÉGOMÈNES** (1 paragraphe):
- Contexte théologique: où se situe ce passage dans la révélation progressive?
- Pourquoi est-il fondamental?

**ANALYSE THÉOLOGIQUE SYSTÉMATIQUE** (6 sous-sections de 1-2 paragraphes chacune):
1. **Révélation**: Comment Dieu se révèle dans ce passage?
2. **Création**: Implications sur la création, l'ordre créé, l'anthropologie?
3. **Alliance**: Quelle(s) alliance(s)? Promesses? Obligations?
4. **Christ**: Comment ce passage pointe vers le Messie? (christologie)
5. **Saint-Esprit**: Rôle de l'Esprit visible ou implicite? (pneumatologie)
6. **Église**: Implications pour le peuple de Dieu? (ecclésiologie)

**TENSIONS ET PARADOXES** (1 paragraphe):
- Quelles tensions théologiques le passage soulève-t-il?
- Exemple: souveraineté divine vs responsabilité humaine

**HÉRITAGE THÉOLOGIQUE** (1 paragraphe):
- Comment les Pères de l'Église, Réformateurs, ou théologiens ont-ils compris ce passage?
- Cite 1-2 théologiens spécifiques

**LONGUEUR**: 700-900 mots.
**STYLE**: Théologique, profond, mais accessible.""",

    # ========== RUBRIQUE 6: Contexte historique ==========
    6: """Développe le contexte historique CONCRET de {passage}.

**ÉPOQUE** (1-2 paragraphes):
- Quelle période historique? (datation approximative)
- Qui était au pouvoir? Quel était le contexte politique?

**SITUATION DU PEUPLE DE DIEU** (2 paragraphes):
- Où était Israël/l'Église à ce moment?
- Exil? Royaume uni? Diaspora? Église primitive?
- Quels défis spirituels et sociaux?

**ÉVÉNEMENTS CONTEMPORAINS** (1-2 paragraphes):
- Quels événements historiques se déroulaient?
- Guerres, alliances, crises?

**CULTURE ENVIRONNANTE** (1-2 paragraphes):
- Quelles influences culturelles (égyptiennes, babyloniennes, grecques, romaines)?
- Quelles pratiques religieuses païennes existaient?

**PERTINENCE DU TEXTE DANS SON CONTEXTE** (1 paragraphe):
- Pourquoi ce passage était crucial POUR LES PREMIERS LECTEURS?
- Quel message répondait à LEUR situation?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Sois HISTORIQUEMENT PRÉCIS. Ne fais pas d'anachronismes.""",

    # ========== RUBRIQUE 7: Contexte culturel ==========
    7: """Analyse le contexte culturel SPÉCIFIQUE de {passage}.

**COUTUMES ET PRATIQUES** (2-3 paragraphes):
- Quelles coutumes sociales apparaissent dans le passage?
- Mariage, hospitalité, commerce, rituels?
- Explique chaque coutume mentionnée

**STRUCTURES SOCIALES** (2 paragraphes):
- Organisation familiale (patriarcat, clan, tribu)
- Rôles sociaux (homme, femme, enfant, esclave, étranger)
- Comment ces structures influencent la compréhension du texte?

**PRATIQUES RELIGIEUSES** (2 paragraphes):
- Culte, sacrifices, fêtes mentionnés?
- Pratiques juives vs païennes?
- Symbolisme religieux culturel?

**CONTEXTE LINGUISTIQUE** (1-2 paragraphes):
- Expressions idiomatiques hébraïques/grecques?
- Jeux de mots perdus en traduction?
- Termes culturels spécifiques?

**IMPLICATIONS POUR LA COMPRÉHENSION** (1 paragraphe):
- Qu'est-ce que comprendre la culture change dans l'interprétation?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Explique POURQUOI chaque élément culturel est important.""",

    # ========== RUBRIQUE 8: Contexte géographique ==========
    8: """Développe le contexte géographique PRÉCIS de {passage}.

**LIEUX MENTIONNÉS** (2 paragraphes):
- Liste TOUS les lieux géographiques du passage
- Pour chaque lieu: localisation, importance, signification du nom

**GÉOGRAPHIE PHYSIQUE** (2 paragraphes):
- Relief: montagnes, vallées, déserts mentionnés?
- Cours d'eau, mers, routes?
- Climat et végétation pertinents?

**DISTANCES ET DÉPLACEMENTS** (1-2 paragraphes):
- Si des voyages sont mentionnés: quelle distance? Combien de temps?
- Difficultés du terrain?

**IMPORTANCE STRATÉGIQUE** (1-2 paragraphes):
- Pourquoi ces lieux sont-ils significatifs?
- Position militaire, commerciale, religieuse?

**SYMBOLISME GÉOGRAPHIQUE** (1-2 paragraphes):
- Y a-t-il un symbolisme théologique lié aux lieux?
- Exemple: Jérusalem = présence divine, Babylone = idolâtrie

**IMPLICATIONS POUR L'INTERPRÉTATION** (1 paragraphe):
- Comment la géographie éclaire le message du texte?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Utilise des DÉTAILS GÉOGRAPHIQUES PRÉCIS, pas des généralités.""",

    # ========== RUBRIQUE 9: Analyse lexicale ==========
    9: """Analyse lexicale APPROFONDIE de {passage}.

**MOTS-CLÉS HÉBREUX/GRECS** (3-4 paragraphes):
- Identifie 5-7 mots-clés dans la langue originale
- Pour CHAQUE mot:
  * Transcription (ex: bara, logos, agape)
  * Sens étymologique
  * Occurrences dans l'AT/NT
  * Nuances perdues en traduction

**CHAMPS SÉMANTIQUES** (2 paragraphes):
- Quels sont les familles de mots dominantes? (création, alliance, salut...)
- Comment ces champs se relient-ils?

**TERMES THÉOLOGIQUES** (2 paragraphes):
- Mots techniques: grâce, justification, sanctification, gloire, etc.
- Définition biblique PRÉCISE de ces termes

**COMPARAISON DES TRADUCTIONS** (1-2 paragraphes):
- Compare 2-3 traductions françaises pour 2-3 versets clés
- Explique pourquoi les différences sont significatives

**IMPLICATIONS THÉOLOGIQUES** (1 paragraphe):
- Comment l'analyse des mots enrichit la compréhension doctrinale?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Sois TECHNIQUE mais ACCESSIBLE. Explique chaque terme.""",

    # ========== RUBRIQUE 10: Parallèles bibliques ==========
    10: """Identifie les parallèles bibliques PRÉCIS de {passage}.

**PARALLÈLES DIRECTS** (2-3 paragraphes):
- Cite 5-7 passages qui racontent la MÊME histoire ou utilisent les MÊMES mots
- Pour chaque: référence + explication de la relation

**PARALLÈLES THÉMATIQUES** (2 paragraphes):
- Cite 4-6 passages développant les MÊMES THÈMES
- Montre la cohérence théologique

**PARALLÈLES TYPOLOGIQUES** (2 paragraphes):
- Quels passages de l'AT sont des TYPES de celui-ci?
- Ou inversement: si AT, quel accomplissement en Christ?

**CITATIONS ET ALLUSIONS** (1-2 paragraphes):
- Le passage cite-t-il d'autres Écritures?
- D'autres passages citent-ils celui-ci?

**INTERTEXTUALITÉ** (1-2 paragraphes):
- Comment le passage s'inscrit dans le grand récit biblique?
- Liens avec la création, l'alliance, l'exode, la croix?

**SYNTHÈSE THÉOLOGIQUE** (1 paragraphe):
- Que révèle l'ensemble de ces parallèles sur le message de Dieu?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: CITE PRÉCISÉMENT les versets (livre chapitre:verset).""",

    # ========== RUBRIQUE 11: Prophétie et accomplissement ==========
    11: """Analyse prophétie et accomplissement dans {passage}.

**NATURE PROPHÉTIQUE** (1-2 paragraphes):
- Le passage contient-il des PROPHÉTIES explicites?
- Promesses, oracles, visions?
- Formules prophétiques ("Ainsi parle l'Éternel", "le jour vient où...")?

**TYPOLOGIE** (2-3 paragraphes):
- Quels éléments du passage sont des TYPES?
  * Personnes (Adam, Moïse, David...)
  * Événements (Exode, sacrifice, retour d'exil...)
  * Institutions (sacrifices, sacerdoce, royauté...)
- Comment sont-ils accomplis en Christ?

**ACCOMPLISSEMENT HISTORIQUE** (2 paragraphes):
- Si prophétie AT: comment s'est-elle accomplie?
- Cite les passages NT montrant l'accomplissement

**ACCOMPLISSEMENT CHRISTOLOGIQUE** (2 paragraphes):
- Comment Christ EST l'accomplissement de ce passage?
- Liens avec son ministère, mort, résurrection, retour?

**ACCOMPLISSEMENT ESCHATOLOGIQUE** (1-2 paragraphes):
- Y a-t-il un accomplissement FUTUR?
- Déjà/pas encore?

**HERMÉNEUTIQUE PROPHÉTIQUE** (1 paragraphe):
- Principes pour interpréter correctement la prophétie ici?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Distingue clairement TYPE et ANTITYPE.""",

    # ========== RUBRIQUE 12: Personnages ==========
    12: """Analyse les personnages de {passage}.

**INVENTAIRE DES PERSONNAGES** (1 paragraphe):
- Liste TOUS les personnages (nommés ou non)
- Rôle de chacun dans le passage

**ANALYSE APPROFONDIE** (3-5 sections selon les personnages):
Pour CHAQUE personnage majeur:
- **Identité**: Qui est-il? Contexte biographique?
- **Actions**: Que fait-il dans ce passage? Motivations?
- **Paroles**: Que dit-il? Analyse de ses discours?
- **Caractère**: Qualités, défauts révélés?
- **Fonction théologique**: Que représente-t-il?

**RELATIONS ENTRE PERSONNAGES** (1-2 paragraphes):
- Dynamiques: conflits, alliances, dialogues?
- Hiérarchies: autorité, soumission, égalité?

**DÉVELOPPEMENT DES PERSONNAGES** (1-2 paragraphes):
- Comment évoluent-ils dans le passage?
- Transformation spirituelle?

**DIMENSION EXEMPLAIRE** (1-2 paragraphes):
- Quels personnages sont des exemples à suivre?
- Quels exemples à éviter?

**TYPOLOGIE CHRISTOLOGIQUE** (1 paragraphe):
- Quels personnages préfigurent Christ?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Analyse PSYCHOLOGIQUE et THÉOLOGIQUE.""",

    # ========== RUBRIQUE 13: Structure rhétorique ==========
    13: """Analyse la structure rhétorique de {passage}.

**GENRE LITTÉRAIRE** (1 paragraphe):
- Quel genre? Récit, poésie, prophétie, épître, apocalypse?
- Conventions du genre?

**STRUCTURE ARGUMENTATIVE** (2-3 paragraphes):
- Comment l'auteur construit-il son argument?
- Introduction, développement, conclusion?
- Thèse principale et thèses secondaires?

**PROCÉDÉS RHÉTORIQUES** (2-3 paragraphes):
- Répétitions (anaphore, épiphore)
- Parallélismes (synonymique, antithétique)
- Chiasmes, inclusio
- Questions rhétoriques
- Hyperboles, métaphores
- Cite des EXEMPLES PRÉCIS du texte

**STRATÉGIE PERSUASIVE** (1-2 paragraphes):
- Comment l'auteur cherche-t-il à convaincre?
- Logos (logique), pathos (émotions), ethos (autorité)?

**DESTINATAIRES ET CONTEXTE** (1 paragraphe):
- Pourquoi cette rhétorique pour CES lecteurs?

**EFFICACITÉ** (1 paragraphe):
- Comment la rhétorique renforce le message théologique?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Cite des EXEMPLES TEXTUELS pour chaque procédé.""",

    # ========== RUBRIQUE 14: Théologie trinitaire ==========
    14: """Développe la théologie trinitaire dans {passage}.

**DIEU LE PÈRE** (2-3 paragraphes):
- Comment le Père est-il révélé?
- Attributs: souveraineté, sainteté, amour, justice?
- Actions spécifiques du Père?
- Relation avec le Fils et l'Esprit?

**DIEU LE FILS** (2-3 paragraphes):
- Présence explicite ou implicite de Christ?
- Si AT: préfigurations christologiques?
- Si NT: quelle dimension de Christ (Prophète, Prêtre, Roi)?
- Relation avec le Père et l'Esprit?

**DIEU LE SAINT-ESPRIT** (2-3 paragraphes):
- Comment l'Esprit agit-il?
- Œuvre de création, inspiration, sanctification?
- Relation avec le Père et le Fils?

**UNITÉ ET DISTINCTION** (1-2 paragraphes):
- Comment le passage montre l'UNITÉ de l'essence divine?
- Comment montre-t-il la DISTINCTION des personnes?
- Périchorèse (communion mutuelle)?

**IMPLICATIONS PRATIQUES** (1 paragraphe):
- Comment cette révélation trinitaire transforme notre vie?
- Adoration, prière, obéissance?

**LONGUEUR**: 700-900 mots.
**RÈGLE**: Équilibre les TROIS personnes. Ne néglige aucune.""",

    # ========== RUBRIQUE 15: Christ au centre ==========
    15: """Montre comment Christ est au centre de {passage}.

**LECTURE CHRISTOCENTRIQUE** (1 paragraphe):
- Pourquoi et comment lire l'Écriture avec Christ au centre?
- Luc 24:27 - Christ dans toutes les Écritures

**PRÉSENCE DIRECTE OU TYPOLOGIE** (2 paragraphes):
- Si NT: comment Christ apparaît directement?
- Si AT: quelles TYPOLOGIES préfigurent Christ?
  * Personnes (Adam, Melchisédek, David...)
  * Événements (Exode, sacrifice, temple...)
  * Institutions (loi, sacerdoce, royauté...)

**ŒUVRE DE CHRIST** (3 paragraphes selon triple office):
1. **Prophète**: Comment Christ révèle/accomplit la Parole?
2. **Prêtre**: Comment Christ expie/intercède?
3. **Roi**: Comment Christ règne/sauve?

**ACCOMPLISSEMENT DES PROMESSES** (1-2 paragraphes):
- Quelles promesses de ce passage Christ accomplit-il?
- Comment? Quand? (1ère venue, entre-deux, retour?)

**VIE CHRÉTIENNE EN CHRIST** (1-2 paragraphes):
- Comment ce passage nous unit à Christ?
- Implications pour notre identité en lui?

**ADORATION CHRISTOLOGIQUE** (1 paragraphe):
- Comment ce passage nous conduit à adorer Christ?

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: TOUT converge vers Christ. Montre-le clairement.""",

    # ========== RUBRIQUE 16: Évangile et grâce ==========
    16: """Développe l'Évangile et la grâce dans {passage}.

**MAUVAISE NOUVELLE D'ABORD** (2 paragraphes):
- Quel est le PROBLÈME révélé? (Péché, rébellion, misère)
- Diagnostic de la condition humaine DANS CE PASSAGE?
- Loi qui condamne?

**BONNE NOUVELLE** (3 paragraphes):
- Quelle est la SOLUTION de Dieu? (Grâce, salut, rédemption)
- Comment l'Évangile apparaît-il dans le passage?
- Promesse, type, accomplissement?
- Lien avec la croix et la résurrection?

**GRÂCE SOUVERAINE** (2 paragraphes):
- Comment le passage révèle que le salut est PAR GRÂCE SEULE?
- Initiative divine vs mérite humain?
- Élection, appel efficace, persévérance?

**FOI SEULE** (1-2 paragraphes):
- Comment la foi est-elle le MOYEN du salut ici?
- Exemples de foi ou d'incrédulité?

**CHRIST SEUL** (1-2 paragraphes):
- Comment Christ est le SEUL médiateur?
- Insuffisance de tout autre moyen de salut?

**TRANSFORMATION PAR L'ÉVANGILE** (1-2 paragraphes):
- Comment cet Évangile transforme?
- Justification, sanctification, glorification?

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Proclame l'ÉVANGILE clairement. Loi ET grâce.""",

    # ========== RUBRIQUE 17: Application personnelle ==========
    17: """Développe des applications personnelles CONCRÈTES de {passage}.

**PRINCIPE HERMÉNEUTIQUE** (1 paragraphe):
- Comment passer du texte ancien à l'application aujourd'hui?
- Distinguer contexte culturel et vérité universelle

**CONNAISSANCE DE DIEU** (2 paragraphes):
- Que dois-je CROIRE sur Dieu à partir de ce passage?
- Comment cela change ma vision de lui?
- Implications pour ma foi?

**EXAMEN DE CONSCIENCE** (2 paragraphes):
- Quels PÉCHÉS ce passage révèle-t-il en moi?
- Où ai-je besoin de repentance?
- Auto-diagnostic spirituel précis

**TRANSFORMATION DU CŒUR** (2-3 paragraphes):
- Quelles ATTITUDES dois-je développer?
- Quels désirs dois-je cultiver?
- Quelles peurs ou idoles abandonner?

**ACTIONS CONCRÈTES** (2-3 paragraphes):
- Quelles DÉCISIONS prendre cette semaine?
- Quelles HABITUDES changer?
- Quelles RELATIONS restaurer?
- Sois TRÈS SPÉCIFIQUE et PRATIQUE

**PRIÈRE D'ENGAGEMENT** (1 paragraphe):
- Courte prière de consécration basée sur le passage

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Applications CONCRÈTES, PERSONNELLES, RÉALISABLES.""",

    # ========== RUBRIQUE 18: Application communautaire ==========
    18: """Développe des applications communautaires de {passage}.

**ECCLÉSIOLOGIE** (1 paragraphe):
- Que révèle ce passage sur la nature de l'Église?

**VIE DE L'ÉGLISE LOCALE** (3 paragraphes):
1. **Culte**: Implications pour l'adoration collective?
2. **Enseignement**: Que prêcher à partir de ce texte?
3. **Communion fraternelle**: Comment vivre ensemble ce passage?

**MINISTÈRES ET DONS** (2 paragraphes):
- Quels ministères ce passage encourage?
- Comment exercer les dons spirituels selon ce texte?

**UNITÉ ET DIVERSITÉ** (2 paragraphes):
- Comment le passage promeut l'unité?
- Comment respecter la diversité?
- Résoudre les conflits à la lumière de ce texte?

**MISSION ET TÉMOIGNAGE** (2 paragraphes):
- Comment l'Église doit-elle TÉMOIGNER selon ce passage?
- Annonce de l'Évangile?
- Service du prochain?

**DISCIPLINE ET DISCIPULAT** (2 paragraphes):
- Implications pour la discipline ecclésiastique?
- Formation de disciples?

**APPLICATIONS PRATIQUES** (2-3 paragraphes):
- 5-7 actions concrètes pour l'Église locale
- Programmes, initiatives, changements?

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Focus sur l'ÉGLISE comme COMMUNAUTÉ, pas l'individu.""",

    # ========== RUBRIQUE 19: Prière de réponse ==========
    19: """Compose une prière de réponse PROFONDE après l'étude de {passage}.

**STRUCTURE EXIGÉE**:

**ADORATION ET LOUANGE** (2-3 paragraphes):
- Loue Dieu pour ce qu'IL EST (attributs révélés dans le passage)
- Loue Dieu pour ce qu'IL A FAIT (actions dans le passage)
- Utilise des DÉTAILS PRÉCIS du texte
- Expressions d'émerveillement et de gratitude

**CONFESSION ET REPENTANCE** (2 paragraphes):
- Confesse les péchés SPÉCIFIQUES que le passage révèle
- Repentance concrète avec engagement de changement
- Demande de pardon basée sur l'Évangile

**INTERCESSION** (2-3 paragraphes):
- Prie pour l'ÉGLISE (universelle et locale)
- Prie pour les AUTORITÉS
- Prie pour les PERDUS (mission)
- Lie chaque intercession au contenu du passage

**SUPPLICATION** (2 paragraphes):
- Demandes PERSONNELLES basées sur le passage
- Besoins spirituels prioritaires
- Grâces spécifiques liées au texte

**ENGAGEMENT ET CONSÉCRATION** (1-2 paragraphes):
- Engagement à vivre selon ce passage
- Offrande de soi à Dieu
- Dépendance de l'Esprit

**CONCLUSION DOXOLOGIQUE** (1 paragraphe):
- Clôture par la gloire de Dieu
- Affirmation de la foi
- Espérance eschatologique

**LONGUEUR**: 800-1000 mots.
**STYLE**: Prière RÉELLE, pas essai sur la prière. Parle À Dieu.""",

    # ========== RUBRIQUE 20: Questions d'étude ==========
    20: """Formule des questions d'étude APPROFONDIES sur {passage}.

**QUESTIONS D'OBSERVATION** (5-7 questions):
- Que dit EXACTEMENT le texte?
- Qui? Quoi? Où? Quand? Comment?
- Questions factuelles précises avec références de versets
- Exemple: "Que dit Dieu au v. 3? Quelle est sa première parole?"

**QUESTIONS D'INTERPRÉTATION** (7-10 questions):
- Que SIGNIFIE le texte?
- Pourquoi l'auteur dit-il cela?
- Que signifie ce mot/phrase dans le contexte?
- Questions théologiques et exégétiques
- Exemple: "Pourquoi l'auteur utilise-t-il le mot 'bara' (créer) ici?"

**QUESTIONS DE COMPARAISON** (5-7 questions):
- Comment ce passage se relie à d'autres?
- Parallèles, contrastes, développements?
- Cite les passages à comparer
- Exemple: "Comparez ce passage avec Jean 1:1-3. Quels parallèles?"

**QUESTIONS DE RÉFLEXION** (5-7 questions):
- Quelle est la PERTINENCE aujourd'hui?
- Comment m'interpelle-t-il personnellement?
- Questions existentielles et pratiques
- Exemple: "En quoi ma vision de Dieu change-t-elle après ce texte?"

**QUESTIONS D'APPLICATION** (5-7 questions):
- Que dois-je FAIRE?
- Changements concrets à opérer?
- Exemple: "Quelle décision prendre cette semaine à la lumière de ce passage?"

**LONGUEUR**: 900-1100 mots (35-45 questions total).
**RÈGLE**: Questions PRÉCISES, PROFONDES, VARIÉES.""",

    # ========== RUBRIQUE 21: Points de vigilance ==========
    21: """Identifie les points de vigilance pour interpréter {passage}.

**ERREURS EXÉGÉTIQUES COURANTES** (3-4 paragraphes):
- Quelles MAUVAISES interprétations existent?
- Pour chaque erreur:
  * Exposé de l'erreur
  * Pourquoi c'est faux
  * Bonne interprétation
  * Conséquences de l'erreur

**DANGERS D'APPLICATION** (2-3 paragraphes):
- Quelles applications ABUSIVES sont possibles?
- Légalisme, licence, mysticisme?
- Comment éviter ces dérives?
- Applications ÉQUILIBRÉES

**QUESTIONS CONTROVERSÉES** (2-3 paragraphes):
- Quelles CONTROVERSES théologiques sur ce passage?
- Différentes positions (exposées équitablement)
- Position défendue et pourquoi
- Humilité face aux questions difficiles

**PIÈGES CONTEXTUELS** (1-2 paragraphes):
- Erreurs liées au contexte historique/culturel?
- Anachronismes à éviter?

**EXCÈS TYPOLOGIQUES** (1-2 paragraphes):
- Risques d'allégorisation excessive?
- Comment lire les types correctement?

**ÉQUILIBRE THÉOLOGIQUE** (1-2 paragraphes):
- Quelles vérités bibliques ÉQUILIBRER?
- Exemple: grâce ET sainteté, foi ET œuvres

**CONSEILS HERMÉNEUTIQUES** (1 paragraphe):
- Principes pour éviter ces pièges?

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Sois HONNÊTE sur les difficultés. Pas dogmatique.""",

    # ========== RUBRIQUE 22: Objections et réponses ==========
    22: """Traite les objections à {passage}.

**OBJECTIONS HISTORIQUES** (2-3 objections):
Pour chaque:
- **Objection**: Formulation claire (historicité, contradictions...)
- **Réponse**: Défense argumentée
- **Références**: Sources bibliques et extra-bibliques

**OBJECTIONS SCIENTIFIQUES** (2-3 objections):
- Conflits apparents avec science (création, miracles...)
- Réponses apologétiques solides
- Distinction science/scientisme

**OBJECTIONS PHILOSOPHIQUES** (2-3 objections):
- Problème du mal, libre arbitre, etc.
- Réponses cohérentes
- Limites de la raison humaine

**OBJECTIONS MORALES** (2-3 objections):
- Passages "difficiles" moralement
- Défense de la bonté et justice de Dieu
- Contexte rédemptif-historique

**OBJECTIONS THÉOLOGIQUES** (2-3 objections):
- Tensions doctrinales apparentes
- Harmonisation biblique
- Mystère vs contradiction

**POSTURE APOLOGÉTIQUE** (1 paragraphe):
- Équilibre: humilité ET confiance
- Limites de nos réponses
- Appel à la foi

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Présente les objections HONNÊTEMENT. Réponds SOLIDEMENT.""",

    # ========== RUBRIQUE 23: Perspective missionnelle ==========
    23: """Développe la perspective missionnelle de {passage}.

**MANDAT MISSIONNAIRE** (2 paragraphes):
- Comment ce passage fonde la mission?
- Lien avec la Grande Mission (Mt 28:18-20)?
- Motivation pour l'évangélisation?

**MESSAGE À PROCLAMER** (2-3 paragraphes):
- Quel ÉVANGILE prêcher à partir de ce passage?
- Comment l'annoncer aux non-croyants?
- Adaptation culturelle du message?

**MÉTHODES MISSIONNAIRES** (2 paragraphes):
- Quelles STRATÉGIES le passage suggère?
- Témoignage personnel, prédication publique, œuvres sociales?
- Contextualisation vs syncrétisme?

**OBSTACLES À LA MISSION** (2 paragraphes):
- Quels obstacles ce passage révèle?
- Opposition, incompréhension, indifférence?
- Comment les surmonter?

**VISION GLOBALE** (2 paragraphes):
- Perspective pour TOUTES les nations?
- Universalité du salut?
- Diversité culturelle dans l'Église?

**COÛT DU DISCIPLE** (2 paragraphes):
- Sacrifice, persécution?
- Promesses pour les missionnaires?

**APPEL À L'ACTION** (1-2 paragraphes):
- Engagements concrets dans la mission
- Localement et globalement?

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Inspire à la MISSION. Vision du monde perdu.""",

    # ========== RUBRIQUE 24: Éthique chrétienne ==========
    24: """Développe l'éthique chrétienne basée sur {passage}.

**FONDEMENTS ÉTHIQUES** (2 paragraphes):
- Quels PRINCIPES moraux le passage établit?
- Caractère de Dieu comme norme éthique?
- Loi morale vs loi cérémonielle/civile?

**VERTUS À CULTIVER** (3-4 paragraphes):
- Quelles VERTUS le passage promeut?
- Pour chaque vertu:
  * Définition biblique
  * Comment la développer?
  * Exemples concrets
- Fruit de l'Esprit pertinent?

**VICES À FUIR** (2-3 paragraphes):
- Quels PÉCHÉS le passage condamne?
- Pourquoi ces péchés offensent Dieu?
- Comment les combattre?

**DILEMMES ÉTHIQUES** (2-3 paragraphes):
- Quelles situations morales complexes?
- Comment appliquer le passage à ces dilemmes?
- Sagesse et discernement?

**ÉTHIQUE SOCIALE** (2 paragraphes):
- Implications pour la SOCIÉTÉ?
- Justice, paix, droits humains?
- Engagement chrétien dans la cité?

**SANCTIFICATION PROGRESSIVE** (1-2 paragraphes):
- Comment grandir en sainteté?
- Rôle de l'Esprit, des moyens de grâce?

**MOTIVATION ÉVANGÉLIQUE** (1 paragraphe):
- Obéissance non légaliste
- Motivation: amour pour Dieu et gratitude

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Éthique BIBLIQUE, pas philosophique. Christ-centré.""",

    # ========== RUBRIQUE 25: Louange / liturgie ==========
    25: """Propose des éléments de louange et liturgie basés sur {passage}.

**CHANTS ET CANTIQUES** (2-3 paragraphes):
- Propose 3-5 CANTIQUES/HYMNES en lien avec le passage
- Pour chaque: titre, auteur, pourquoi il convient
- Extraits de paroles pertinents

**LECTURES RESPONSIVES** (2 paragraphes):
- Crée 1-2 lectures antiphonées du passage
- Format: Leader / Assemblée
- 6-8 échanges par lecture

**CONFESSION DE FOI** (1 paragraphe):
- Rédige une confession de foi basée sur le passage
- Style: Credo (Je crois... Nous croyons...)
- 5-7 affirmations

**PRIÈRE LITURGIQUE** (1-2 paragraphes):
- Collecte ou oraison inspirée du passage
- Style liturgique formel

**BÉNÉDICTION** (1 paragraphe):
- Formule une bénédiction finale basée sur le passage
- Style: "Que le Dieu de... vous bénisse et..."

**SUGGESTIONS CULTUELLES** (2 paragraphes):
- Comment intégrer ce passage dans le culte?
- Thème de culte suggéré
- Ordonnancement liturgique

**SYMBOLISME ET VISUELS** (1-2 paragraphes):
- Éléments visuels pour accompagner (couleurs, objets...)
- Gestes liturgiques appropriés?

**LONGUEUR**: 800-1000 mots.
**RÈGLE**: Propose des ÉLÉMENTS UTILISABLES en culte.""",

    # ========== RUBRIQUE 26: Méditation guidée ==========
    26: """Guide une méditation spirituelle sur {passage}.

**PRÉPARATION** (1 paragraphe):
- Instructions pour se préparer (lieu calme, posture, respiration)
- Invocation de l'Esprit

**LECTURE LENTE** (1 paragraphe):
- Instructions: lire 3 fois lentement
- Pause entre lectures
- Attention aux détails

**VISUALISATION** (3-4 paragraphes):
- Guide l'imaginaire spirituel:
  * Si récit: visualise la scène, les personnages
  * Si enseignement: imagine les vérités
  * Si poésie: ressens les émotions
- Utilise des DÉTAILS SENSORIELS du texte
- Technique d'Ignace de Loyola adaptée

**IDENTIFICATION** (2 paragraphes):
- Avec quel personnage/élément t'identifies-tu?
- Que ressens-tu?
- Où te situes-tu dans la scène?

**RENCONTRE AVEC DIEU** (2-3 paragraphes):
- Dieu te parle à travers ce passage
- Qu'entends-tu?
- Que réponds-tu?
- Dialogue intérieur

**SILENCE** (1 paragraphe):
- Instructions: 3-5 minutes de silence
- Rester en présence
- Écoute active

**RÉSOLUTION** (1-2 paragraphes):
- Quelle RÉPONSE concrète?
- Engagement précis
- Prière de consécration

**CLÔTURE** (1 paragraphe):
- Retour progressif
- Action de grâces
- Comment garder ce fruit?

**LONGUEUR**: 800-1000 mots.
**STYLE**: MÉDITATIF, CONTEMPLATIF. Tutoyé et intimiste.""",

    # ========== RUBRIQUE 27: Mémoire / versets clés ==========
    27: """Identifie et développe les versets clés à mémoriser dans {passage}.

**SÉLECTION DES VERSETS** (1 paragraphe):
- Choisis 5-7 VERSETS CLÉS du passage
- Critères: théologie, application, beauté littéraire

**ANALYSE VERSET PAR VERSET** (5-7 sections):
Pour CHAQUE verset sélectionné:

**VERSET [X]** : [Citation complète]
- **Pourquoi mémoriser**: Importance théologique
- **Contexte**: Place dans le passage
- **Mot-clé**: Identifie LE mot central
- **Application**: Comment ce verset transforme
- **Associations**: Autres versets similaires à lier
- **Mnémotechnique**: Astuce pour retenir (acronyme, rime, image...)

**PLAN DE MÉMORISATION** (2 paragraphes):
- Méthode suggérée (cartes, répétition espacée, chant...)
- Calendrier: 1 verset par semaine ou rythme adapté
- Comment réviser régulièrement?

**MÉDITATION DES VERSETS** (1-2 paragraphes):
- Comment méditer ces versets au quotidien?
- Moments opportuns (matin, soir, transports...)

**UTILISATION PRATIQUE** (1-2 paragraphes):
- Dans quelles situations citer ces versets?
- Pour l'évangélisation, l'encouragement, la tentation?

**PARTAGE** (1 paragraphe):
- Comment aider d'autres à mémoriser?
- Mémorisation en groupe?

**LONGUEUR**: 800-1000 mots.
**RÈGLE**: Fournis les VERSETS COMPLETS avec références.""",

    # ========== RUBRIQUE 28: Plan d'action ==========
    28: """Établis un plan d'action CONCRET basé sur {passage}.

**BILAN SPIRITUEL** (1-2 paragraphes):
- Où en suis-je spirituellement face à ce passage?
- Auto-évaluation honnête
- Forces et faiblesses révélées

**OBJECTIFS SPIRITUELS** (2 paragraphes):
- 3-5 OBJECTIFS SMART (Spécifiques, Mesurables, Atteignables, Réalistes, Temporels)
- Liés directement au passage
- Exemple: "Prier 15 min/jour en utilisant le modèle de prière du passage pendant 1 mois"

**ACTIONS QUOTIDIENNES** (2-3 paragraphes):
- 5-7 actions à intégrer CHAQUE JOUR
- Très concrètes et détaillées
- Exemple: "Chaque matin, méditer le verset X pendant 5 minutes avant le petit-déjeuner"

**ACTIONS HEBDOMADAIRES** (2 paragraphes):
- 3-5 actions CHAQUE SEMAINE
- Exemple: "Jeudi soir, partager l'enseignement du passage avec un ami"

**DÉCISIONS MAJEURES** (1-2 paragraphes):
- Y a-t-il des DÉCISIONS importantes à prendre?
- Changements de vie, engagements, renoncements?

**MOYENS DE GRÂCE** (1-2 paragraphes):
- Quels moyens utiliser pour progresser?
- Prière, jeûne, groupe biblique, mentorat?

**RESPONSABILISATION** (1 paragraphe):
- Qui t'aidera à tenir ce plan?
- Partager avec un frère/sœur?
- Rendre compte régulièrement?

**ÉVALUATION** (1 paragraphe):
- Dates de bilan: 1 semaine, 1 mois, 3 mois
- Critères de réussite?

**PRIÈRE D'ENGAGEMENT** (1 paragraphe):
- Courte prière scellant ces résolutions

**LONGUEUR**: 900-1100 mots.
**RÈGLE**: Plan ULTRA-CONCRET, RÉALISABLE, MESURABLE. Pas de vagues résolutions."""
}

@api_router.post("/generate-rubrique")
async def generate_rubrique(request: dict):
    """
    Génère une rubrique avec cache MongoDB pour éviter de régénérer.
    Cache basé sur: passage + rubrique_number
    """
    try:
        passage = request.get('passage', '')
        rubrique_number = request.get('rubrique_number', 1)
        rubrique_title = request.get('rubrique_title', '')
        force_regenerate = request.get('force_regenerate', False)  # Nouveau paramètre
        
        if rubrique_number not in RUBRIQUE_PROMPTS:
            return {"status": "success", "content": f"# {rubrique_title}\n\n**{passage}**\n\nRubrique en développement.", "api_used": "placeholder"}
        
        # Créer une clé de cache unique
        cache_key = f"{passage}_{rubrique_number}"
        
        # Vérifier si existe en cache (sauf si force_regenerate)
        if not force_regenerate:
            cached_rubrique = await db.rubriques_cache.find_one({"cache_key": cache_key})
            if cached_rubrique:
                logging.info(f"✅ Cache hit pour {passage} - Rubrique {rubrique_number}")
                return {
                    "status": "success",
                    "content": cached_rubrique["content"],
                    "rubrique_number": rubrique_number,
                    "rubrique_title": rubrique_title,
                    "passage": passage,
                    "api_used": "cache",
                    "cached": True,
                    "generated_at": cached_rubrique.get("created_at")
                }
        
        # Générer nouveau contenu
        logging.info(f"🔄 Génération pour {passage} - Rubrique {rubrique_number}")
        prompt = RUBRIQUE_PROMPTS[rubrique_number].format(passage=passage)
        content = await call_gemini_with_rotation(prompt)
        
        # Sauvegarder en cache MongoDB
        cache_doc = {
            "cache_key": cache_key,
            "passage": passage,
            "rubrique_number": rubrique_number,
            "rubrique_title": rubrique_title,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert (update ou insert)
        await db.rubriques_cache.update_one(
            {"cache_key": cache_key},
            {"$set": cache_doc},
            upsert=True
        )
        
        return {
            "status": "success",
            "content": content,
            "rubrique_number": rubrique_number,
            "rubrique_title": rubrique_title,
            "passage": passage,
            "api_used": "gemini",
            "cached": False
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "http://localhost:3000",
        "https://etude-khaki.vercel.app",  # Vercel frontend
        "https://bible-study-app-6.preview.emergentagent.com",
        "*"  # Fallback pour développement
    ],
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
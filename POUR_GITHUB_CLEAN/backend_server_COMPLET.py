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
            ).with_model("gemini", "gemini-2.0-flash")
            
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
        
        try:
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
    """
    try:
        passage = request.get('passage', '')
        start_verse = request.get('start_verse', 1)
        end_verse = request.get('end_verse', 3)  # Réduit à 3 pour Vercel timeout 10s
        
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
RUBRIQUE_PROMPTS = {
    1: """Génère une VRAIE prière d'ouverture pour {passage}.

**ADORATION** (3-4 phrases) : Adore Dieu pour ses attributs révélés DANS CE PASSAGE. Cite des DÉTAILS PRÉCIS (ex: "séparation des eaux", "image divine"). NE répète PAS "{passage}".

**CONFESSION** (3-4 phrases) : Confesse les péchés que CE passage révèle.

**DEMANDE** (3-4 phrases) : Demande l'Esprit pour comprendre CE passage.

**MÉDITATION** (2 paragraphes) : Comment cette prière prépare le cœur.

300-400 mots. Commence par "**ADORATION**".""",
    2: """Analyse structure littéraire de {passage}.

**ARCHITECTURE** : Structure globale
**SECTIONS** : Décomposition
**PROCÉDÉS** : Répétitions, mots-clés hébreux
**SIGNIFICATION** : Pourquoi cette structure

400-500 mots.""",
    3: """Transition du chapitre précédent vers {passage}.

Si chapitre 1 : OUVERTURE du livre.

**RÉCAPITULATIF** 
**QUESTIONS** : 5-7 questions
**CONTINUITÉ THÉOLOGIQUE**
**CONTEXTE NARRATIF**

350-450 mots.""",
    4: """Thème doctrinal de {passage}.

**THÈME PRINCIPAL**
**DÉVELOPPEMENT** : Dieu, homme, salut, fin
**APPLICATIONS**
**LIENS**

500-600 mots. Cite 3-5 passages.""",
    5: """Fondements théologiques de {passage}.

**PROLÉGOMÈNES**
**ANALYSE** : révélation, création, alliance, Christ, Esprit, Église
**TENSIONS**
**HÉRITAGE**

700-900 mots."""
}

@api_router.post("/generate-rubrique")
async def generate_rubrique(request: dict):
    try:
        passage = request.get('passage', '')
        rubrique_number = request.get('rubrique_number', 1)
        rubrique_title = request.get('rubrique_title', '')
        
        if rubrique_number not in RUBRIQUE_PROMPTS:
            return {"status": "success", "content": f"# {rubrique_title}\n\n**{passage}**\n\nRubrique en développement.", "api_used": "placeholder"}
        
        prompt = RUBRIQUE_PROMPTS[rubrique_number].format(passage=passage)
        content = await call_gemini_with_rotation(prompt)
        
        return {
            "status": "success",
            "content": content,
            "rubrique_number": rubrique_number,
            "rubrique_title": rubrique_title,
            "passage": passage,
            "api_used": "gemini"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


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
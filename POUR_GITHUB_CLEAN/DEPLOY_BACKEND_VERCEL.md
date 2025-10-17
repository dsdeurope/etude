# 🚀 DÉPLOIEMENT BACKEND POUR VERCEL - GUIDE COMPLET

**Date :** 12 octobre 2024  
**Urgent :** Le nouvel endpoint `/api/generate-verse-by-verse` doit être déployé sur le backend de production

---

## ⚠️ PROBLÈME ACTUEL

Votre site Vercel (https://etude-khaki.vercel.app/) appelle :
```
REACT_APP_BACKEND_URL=https://bible-study-hub-8.preview.emergentagent.com
```

**Ce backend de production doit être mis à jour avec le nouvel endpoint !**

---

## 📁 FICHIER BACKEND À DÉPLOYER

Le fichier `/app/backend/server.py` a été modifié avec :
- ✅ Endpoint `/api/generate-verse-by-verse` (lignes 548-644)
- ✅ Rotation automatique des 4 clés Gemini
- ✅ Génération par 5 versets

---

## 🔑 VARIABLES D'ENVIRONNEMENT REQUISES

Sur votre serveur backend `https://bible-study-hub-8.preview.emergentagent.com`, vous devez configurer :

```env
# MongoDB
MONGO_URL="mongodb://localhost:27017"
DB_NAME="meditation_biblique_db"
CORS_ORIGINS="*"

# Bible API
BIBLE_ID="a93a92589195411f-01"
BIBLE_API_KEY="0cff5d83f6852c3044a180cc4cdeb0fe"

# Gemini API Keys (4 clés pour rotation)
GEMINI_API_KEY_1="AIzaSyDro7GV39MHavUDnn3mms9Y1Ih3ZaGMbAg"
GEMINI_API_KEY_2="AIzaSyAvkPZNJX4QCH5V1Lked4jHOYadyOeeWHY"
GEMINI_API_KEY_3="AIzaSyAtBuW22JZCTD9PZFgVVeuNs5m-_DMVVCE"
GEMINI_API_KEY_4="AIzaSyBPbG2Wqz5dHwIpWIMqM5a72NnbBCnU9YY"
```

---

## 📦 DÉPENDANCES BACKEND REQUISES

Le fichier `requirements.txt` doit contenir :

```txt
fastapi
uvicorn[standard]
motor
python-dotenv
pydantic
httpx
emergentintegrations
google-generativeai
litellm
```

**Installation de emergentintegrations :**
```bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

---

## 🔧 CODE DU NOUVEL ENDPOINT

Voici le code à ajouter dans votre `server.py` de production :

```python
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
        end_verse = request.get('end_verse', 5)
        
        if not passage:
            return {
                "status": "error",
                "message": "Passage manquant"
            }
        
        # Parser le passage (ex: "Genèse 1" ou "Jean 3:16")
        parts = passage.split()
        if len(parts) < 2:
            return {
                "status": "error",
                "message": "Format de passage invalide. Utilisez 'Livre Chapitre' (ex: Genèse 1)"
            }
        
        book_name = ' '.join(parts[:-1])
        chapter = parts[-1]
        
        logging.info(f"Génération verset par verset: {book_name} {chapter}, versets {start_verse}-{end_verse}")
        
        # Préparer le prompt pour Gemini
        prompt = f"""Tu es un expert biblique et théologien spécialisé dans l'exégèse verset par verset.

Génère une étude DÉTAILLÉE et APPROFONDIE pour les versets {start_verse} à {end_verse} de **{book_name} chapitre {chapter}** en français.

Pour CHAQUE verset de {start_verse} à {end_verse}, structure ainsi :

---

**VERSET {start_verse}**

**📜 TEXTE BIBLIQUE :**
[Le texte biblique exact du verset en français Louis Segond]

**🎓 EXPLICATION THÉOLOGIQUE :**
[Explication détaillée en 2-3 paragraphes incluant :]
- Contexte historique et culturel
- Analyse des mots clés en grec/hébreu si pertinent
- Signification théologique profonde
- Application pratique pour aujourd'hui
- Liens avec d'autres passages bibliques

---

**VERSET {start_verse + 1}**

[Même structure pour chaque verset suivant jusqu'au verset {end_verse}]

**RÈGLES IMPORTANTES :**
1. Utilise EXACTEMENT le format ci-dessus pour chaque verset
2. Sois TRÈS détaillé dans chaque explication (minimum 150 mots par verset)
3. Inclus des références bibliques croisées
4. Reste fidèle à l'exégèse biblique orthodoxe
5. Termine chaque explication par une application pratique

Commence directement avec le premier verset sans introduction générale."""

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
```

---

## 🎯 OÙ PLACER CE CODE

Dans votre fichier `server.py` de production, ajoutez ce code **APRÈS** l'endpoint `/api/generate-character-history` et **AVANT** le `app.include_router()`.

**Exemple de placement :**
```python
# ... autres endpoints ...

@api_router.post("/generate-character-history")
async def generate_character_history(request: dict):
    # ... code existant ...
    pass

# ⬇️ AJOUTER ICI ⬇️
@api_router.post("/generate-verse-by-verse")
async def generate_verse_by_verse(request: dict):
    # ... nouveau code ci-dessus ...
    pass

# Include the router in the main app
app.include_router(api_router)
```

---

## 🧪 TESTER LE BACKEND DE PRODUCTION

Une fois déployé, testez avec :

```bash
curl -X POST https://bible-study-hub-8.preview.emergentagent.com/api/generate-verse-by-verse \
  -H "Content-Type: application/json" \
  -d '{
    "passage": "Genèse 1",
    "start_verse": 1,
    "end_verse": 5,
    "version": "LSG",
    "use_gemini": true,
    "enriched": true
  }'
```

**Réponse attendue :**
```json
{
  "status": "success",
  "content": "---\n\n**VERSET 1**\n\n**📜 TEXTE BIBLIQUE :**\nAu commencement...",
  "api_used": "gemini_1",
  "verses_generated": "1-5",
  "word_count": 1200
}
```

---

## 📝 ÉTAPES DE DÉPLOIEMENT

### Option 1 : Si vous avez accès SSH au serveur backend

```bash
# 1. Connectez-vous au serveur
ssh user@vercel-api-fix.preview.emergentagent.com

# 2. Allez dans le dossier du backend
cd /path/to/backend

# 3. Éditez server.py et ajoutez le nouveau endpoint
nano server.py

# 4. Installez les dépendances manquantes
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# 5. Configurez les variables d'environnement dans .env
nano .env
# Ajoutez les 4 GEMINI_API_KEY_X

# 6. Redémarrez le backend
# Si utilisant systemd :
sudo systemctl restart backend

# Si utilisant supervisor :
sudo supervisorctl restart backend

# Si utilisant uvicorn directement :
pkill -f uvicorn
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Option 2 : Si vous utilisez une plateforme (Heroku, Railway, etc.)

1. **Poussez le code mis à jour** vers votre dépôt Git
2. **Configurez les variables d'environnement** sur la plateforme :
   - GEMINI_API_KEY_1
   - GEMINI_API_KEY_2
   - GEMINI_API_KEY_3
   - GEMINI_API_KEY_4
   - BIBLE_API_KEY
   - BIBLE_ID
3. **Redéployez** l'application

### Option 3 : Si c'est un service Emergent

Contactez le support Emergent pour mettre à jour le backend de production avec le nouveau code.

---

## 🔍 VÉRIFIER QUE ÇA FONCTIONNE

### Test 1 : Endpoint disponible

```bash
curl https://bible-study-hub-8.preview.emergentagent.com/api/generate-verse-by-verse
```

Si vous obtenez une réponse (même une erreur), l'endpoint existe.

### Test 2 : Génération réussie

```bash
curl -X POST https://bible-study-hub-8.preview.emergentagent.com/api/generate-verse-by-verse \
  -H "Content-Type: application/json" \
  -d '{"passage":"Genèse 1","start_verse":1,"end_verse":5}'
```

Si vous obtenez du contenu avec VERSET 1, 2, 3, 4, 5, c'est BON !

### Test 3 : Sur votre site Vercel

1. Allez sur https://etude-khaki.vercel.app/
2. Sélectionnez "Genèse" chapitre "1"
3. Cliquez sur "VERSETS PROG"
4. Si l'étude verset par verset s'affiche → ✅ SUCCÈS !

---

## 📄 FICHIER COMPLET server.py

Si vous avez besoin du fichier complet, il est disponible dans :
```
/app/backend/server.py
```

Vous pouvez le copier vers votre serveur de production.

---

## ⚠️ IMPORTANT

**Le frontend Vercel est déjà prêt !**

Le frontend sur https://etude-khaki.vercel.app/ appelle déjà cet endpoint. Il suffit de le déployer côté backend.

**Fichiers frontend (déjà OK) :**
- `/app/POUR_GITHUB_CLEAN/src/App.js` → Fonction `generateVerseByVerseProgressive()`
- `/app/POUR_GITHUB_CLEAN/src/App.js` → Fonction `continueVerses()`
- Tout est déjà configuré pour appeler `/api/generate-verse-by-verse`

---

## 🆘 EN CAS DE PROBLÈME

### Erreur : "Endpoint not found"
→ L'endpoint n'a pas été déployé sur le backend de production
→ Vérifiez que le code a bien été ajouté à `server.py`

### Erreur : "Quota épuisé"
→ Les 4 clés Gemini ont atteint leur limite
→ Attendez le reset quotidien ou ajoutez de nouvelles clés

### Erreur : "Module emergentintegrations not found"
→ La dépendance n'est pas installée sur le serveur
→ Installez avec : `pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/`

### Erreur CORS
→ Ajoutez votre domaine Vercel dans CORS_ORIGINS
→ `CORS_ORIGINS="https://etude-khaki.vercel.app,http://localhost:3000"`

---

## 📞 CONTACT

Si vous ne pouvez pas accéder au serveur backend de production, contactez votre hébergeur ou le support Emergent pour :
1. Ajouter le nouveau endpoint `/api/generate-verse-by-verse`
2. Configurer les 4 clés Gemini
3. Redémarrer le backend

---

**🎯 UNE FOIS LE BACKEND DÉPLOYÉ, LE BOUTON "VERSETS PROG" FONCTIONNERA SUR VERCEL !**

**Date :** 12 octobre 2024  
**Fichier source :** `/app/backend/server.py` (lignes 548-644)

# 🔐 Configuration Backend - Variables d'Environnement

## ⚠️ IMPORTANT

Ce fichier explique comment configurer les variables d'environnement **sur votre serveur backend**.

**Les clés API doivent être configurées sur le BACKEND, PAS sur Vercel frontend.**

---

## 📋 Variables Requises pour le Backend

### Fichier `.env` du Backend

Créez un fichier `.env` dans le répertoire de votre backend avec le contenu suivant :

```env
# MongoDB Configuration
MONGO_URL="mongodb://localhost:27017"
DB_NAME="meditation_biblique_db"
CORS_ORIGINS="*"

# Bible API Configuration
BIBLE_ID="a93a92589195411f-01"
BIBLE_API_KEY="0cff5d83f6852c3044a180cc4cdeb0fe"

# Gemini API Keys (Rotation Automatique)
GEMINI_API_KEY_1="AIzaSyDro7GV39MHavUDnn3mms9Y1Ih3ZaGMbAg"
GEMINI_API_KEY_2="AIzaSyAvkPZNJX4QCH5V1Lked4jHOYadyOeeWHY"
GEMINI_API_KEY_3="AIzaSyAtBuW22JZCTD9PZFgVVeuNs5m-_DMVVCE"
GEMINI_API_KEY_4="AIzaSyBPbG2Wqz5dHwIpWIMqM5a72NnbBCnU9YY"
```

---

## 🚀 Où Configurer Ces Variables

### Option 1 : Serveur Backend Séparé

Si votre backend est hébergé sur un serveur séparé (par exemple : Heroku, AWS, DigitalOcean) :

1. **Créez le fichier `.env`** dans le répertoire du backend
2. **Copiez les variables** ci-dessus
3. **Remplacez les valeurs** par vos propres clés si nécessaire
4. **Redémarrez le backend**

### Option 2 : Variables d'Environnement Système

Sur votre serveur, configurez les variables via :

**Linux/Mac :**
```bash
export GEMINI_API_KEY_1="AIzaSyDro7GV39MHavUDnn3mms9Y1Ih3ZaGMbAg"
export GEMINI_API_KEY_2="AIzaSyAvkPZNJX4QCH5V1Lked4jHOYadyOeeWHY"
# etc...
```

**Docker :**
```yaml
environment:
  - GEMINI_API_KEY_1=AIzaSyDro7GV39MHavUDnn3mms9Y1Ih3ZaGMbAg
  - GEMINI_API_KEY_2=AIzaSyAvkPZNJX4QCH5V1Lked4jHOYadyOeeWHY
```

---

## 🔑 Obtenir Vos Propres Clés

### Clés Gemini API

1. Allez sur : https://makersuite.google.com/app/apikey
2. Créez un projet Google Cloud
3. Activez l'API Gemini
4. Générez 4 clés API (pour la rotation)

**Plans disponibles :**
- Gratuit : 60 requêtes/minute, 1500/jour
- Pay-as-you-go : Variable
- Enterprise : Personnalisé

### Clé Bible API

1. Allez sur : https://scripture.api.bible/
2. Créez un compte gratuit
3. Obtenez votre API Key
4. Notez votre Bible ID (exemple : `a93a92589195411f-01` pour LSG française)

---

## 🎯 Système de Rotation Automatique

Le backend utilise automatiquement les 4 clés Gemini :

```
Clé 1 → En cas de quota épuisé →
Clé 2 → En cas de quota épuisé →
Clé 3 → En cas de quota épuisé →
Clé 4 → Dernière tentative
```

**Avantages :**
- Continuité du service
- 4x plus de quota disponible
- Basculement automatique invisible pour l'utilisateur

---

## 🔴🟡🟢 Système de LEDs

Les LEDs sur le frontend affichent l'état réel des clés :

- 🟢 **VERT** : Quota < 70%
- 🟡 **JAUNE** : Quota 70-90%
- 🔴 **ROUGE** : Quota > 90% ou épuisé

Le backend vérifie les clés en temps réel et envoie seulement les couleurs au frontend.

---

## 🧪 Tester la Configuration

Une fois le backend configuré, testez avec :

```bash
curl http://votre-backend-url/api/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "total_gemini_keys": 4,
  "apis": {
    "gemini_1": {"color": "green", "is_available": true},
    "gemini_2": {"color": "green", "is_available": true},
    "gemini_3": {"color": "green", "is_available": true},
    "gemini_4": {"color": "green", "is_available": true},
    "bible_api": {"color": "green", "is_available": true}
  }
}
```

---

## ⚠️ Sécurité

**NE JAMAIS :**
- ❌ Commiter les clés dans Git
- ❌ Exposer les clés au frontend
- ❌ Partager les clés publiquement

**TOUJOURS :**
- ✅ Garder les clés sur le serveur backend
- ✅ Utiliser `.env` ou variables d'environnement
- ✅ Ajouter `.env` dans `.gitignore`

---

## 📦 Dépendances Backend Requises

Le backend nécessite :

```txt
fastapi
uvicorn
motor
python-dotenv
emergentintegrations
httpx
google-generativeai
```

Installation :
```bash
pip install -r requirements.txt
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

---

## 🌐 Configuration CORS

Pour que le frontend Vercel puisse communiquer avec votre backend :

```python
# Dans server.py
CORS_ORIGINS = [
    "https://etude-khaki.vercel.app",
    "http://localhost:3000"
]
```

Ou dans `.env` :
```env
CORS_ORIGINS="https://etude-khaki.vercel.app,http://localhost:3000"
```

---

**Date :** 12 octobre 2024  
**Version :** 1.0  
**Backend API Version :** FastAPI avec rotation Gemini 4 clés

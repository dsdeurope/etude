# 🚀 Guide de Déploiement Vercel - Backend Gemini

## Étapes de Déploiement

### 1. Préparer le Repository

Assurez-vous que tous les fichiers sont committés dans votre repository :
- `api/health.py` - Endpoint de santé
- `api/enrich-concordance.py` - Enrichissement concordance Gemini
- `api/generate-character-history.py` - Génération histoires personnages
- `vercel.json` - Configuration Vercel avec Functions
- `requirements.txt` - Dépendances Python

### 2. Configurer les Variables d'Environnement sur Vercel

Dans votre dashboard Vercel (vercel.com), allez dans Settings > Environment Variables et ajoutez :

```
BIBLE_ID = a93a92589195411f-01
BIBLE_API_KEY = 0cff5d83f6852c3044a180cc4cdeb0fe
GEMINI_API_KEY_1 = AIzaSyDro7GV39MHavUDnn3mms9Y1Ih3ZaGMbAg
GEMINI_API_KEY_2 = AIzaSyAvkPZNJX4QCH5V1Lked4jHOYadyOeeWHY
GEMINI_API_KEY_3 = AIzaSyAtBuW22JZCTD9PZFgVVeuNs5m-_DMVVCE
GEMINI_API_KEY_4 = AIzaSyBPbG2Wqz5dHwIpWIMqM5a72NnbBCnU9YY
```

⚠️ **Important** : Assurez-vous de définir ces variables pour tous les environnements (Production, Preview, Development)

### 3. Déployer

Option A - Via Git :
```bash
git add .
git commit -m "Add Gemini API backend functions"
git push origin main
```

Option B - Via Vercel CLI :
```bash
vercel --prod
```

### 4. Tester les Endpoints

Une fois déployé, testez :

```bash
# Health check
curl https://votre-site.vercel.app/api/health

# Enrichissement concordance
curl -X POST https://votre-site.vercel.app/api/enrich-concordance \
  -H "Content-Type: application/json" \
  -d '{"search_term": "amour", "enrich": true}'

# Histoire personnage
curl -X POST https://votre-site.vercel.app/api/generate-character-history \
  -H "Content-Type: application/json" \
  -d '{"character_name": "Abraham", "enrich": true}'
```

### 5. Vérifier l'Interface

Allez sur votre site et testez :
1. Cliquez sur "BIBLE CONCORDANCE" 
2. Saisissez "amour" dans le champ de recherche
3. Cliquez sur "🤖 Gemini" - devrait maintenant fonctionner !

## Architecture Déployée

```
votre-site.vercel.app/
├── Frontend (React) - Interface utilisateur
└── /api/
    ├── health.py - Status API et rotation clés
    ├── enrich-concordance.py - Enrichissement Gemini + Bible API  
    └── generate-character-history.py - Histoires personnages Gemini
```

## Rotation des Clés Gemini

Le système utilise une rotation simple basée sur le timestamp pour distribuer les appels entre vos 4 clés Gemini, évitant ainsi les limites de quota.

## Troubleshooting

Si les endpoints ne fonctionnent pas :
1. Vérifiez les variables d'environnement dans Vercel Dashboard
2. Consultez les logs Vercel Functions
3. Testez chaque endpoint individuellement avec curl

## Support

Le backend est maintenant configuré pour :
✅ Rotation automatique de 4 clés Gemini  
✅ API Bible intégrée  
✅ CORS configuré pour votre frontend  
✅ Gestion d'erreurs complète  
✅ Compatible Vercel Functions
# ⚡ Guide Rapide - Variables d'Environnement Vercel

## 🎯 RÉPONSE RAPIDE

### Pour faire fonctionner votre application sur Vercel :

**VOUS N'AVEZ BESOIN QUE D'UNE SEULE VARIABLE :**

```
Nom: REACT_APP_BACKEND_URL
Valeur: https://vercel-api-fix.preview.emergentagent.com
```

---

## ✅ C'EST TOUT !

Les clés API Gemini et Bible **ne sont PAS nécessaires** car :
- ✅ L'API Gemini est actuellement **simulée** dans le backend
- ✅ L'API Bible est actuellement **simulée** dans le backend
- ✅ Toutes les fonctionnalités marchent avec des données de démonstration

---

## 📋 COMMENT CONFIGURER SUR VERCEL

### Option 1 : Interface Web Vercel

1. **Allez sur :** https://vercel.com/dashboard
2. **Sélectionnez :** Votre projet `etude-khaki`
3. **Cliquez sur :** Settings → Environment Variables
4. **Ajoutez :**
   - Name: `REACT_APP_BACKEND_URL`
   - Value: `https://vercel-api-fix.preview.emergentagent.com`
   - Environments: ✅ Production ✅ Preview ✅ Development
5. **Cliquez sur :** Save
6. **Redéployez :** Deployments → Redeploy

### Option 2 : Vercel CLI

```bash
vercel env add REACT_APP_BACKEND_URL
# Entrez: https://vercel-api-fix.preview.emergentagent.com
# Sélectionnez: Production, Preview, Development
```

---

## 🔮 PLUS TARD (Optionnel)

Si vous voulez activer les **vraies APIs** Gemini et Bible :

### Pour Gemini AI
```
Nom: GEMINI_API_KEY
Valeur: [Votre clé depuis https://makersuite.google.com/app/apikey]
Configurer: Dans le backend (pas Vercel frontend)
```

### Pour Bible API
```
Nom: BIBLE_API_KEY
Valeur: [Votre clé depuis https://scripture.api.bible/]
Configurer: Dans le backend (pas Vercel frontend)
```

⚠️ **Important :** Ces clés vont dans le **BACKEND**, pas dans Vercel frontend !

---

## 🎨 SCHÉMA SIMPLE

```
┌─────────────────────────────────────────┐
│  VERCEL (Frontend React)                │
│  ┌───────────────────────────────────┐  │
│  │ Variable d'Environnement :        │  │
│  │ REACT_APP_BACKEND_URL             │  │
│  │ = https://vercel-api-fix...       │  │
│  └───────────────────────────────────┘  │
│                  │                       │
│                  │ API Calls             │
│                  ▼                       │
└──────────────────┼───────────────────────┘
                   │
                   │
┌──────────────────▼───────────────────────┐
│  BACKEND (FastAPI)                       │
│  https://vercel-api-fix.preview...       │
│  ┌───────────────────────────────────┐  │
│  │ Variables (optionnelles):         │  │
│  │ - GEMINI_API_KEY                  │  │
│  │ - BIBLE_API_KEY                   │  │
│  │ - MONGO_URL                       │  │
│  └───────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

---

## ✅ CHECKLIST DE DÉPLOIEMENT

- [ ] Variable `REACT_APP_BACKEND_URL` ajoutée sur Vercel
- [ ] Environnements cochés : Production, Preview, Development
- [ ] Redéploiement effectué
- [ ] Application testée sur https://etude-khaki.vercel.app/
- [ ] Les 7 boutons s'affichent horizontalement ✨

---

## 🆘 PROBLÈMES COURANTS

### ❌ "Backend not found" ou erreurs API
→ Vérifiez que `REACT_APP_BACKEND_URL` est bien configurée

### ❌ Variable `undefined` dans la console
→ Le nom doit commencer par `REACT_APP_`
→ Redéployez après avoir ajouté la variable

### ❌ L'ancienne URL est toujours utilisée
→ Videz le cache du navigateur (Ctrl+Shift+R)
→ Attendez la fin du déploiement Vercel

---

**🎯 RÉSUMÉ : Vous n'avez besoin que de `REACT_APP_BACKEND_URL` pour l'instant !**

**Date :** 12 octobre 2024

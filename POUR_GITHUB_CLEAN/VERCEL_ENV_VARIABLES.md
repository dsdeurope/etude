# 🔐 Variables d'Environnement pour Vercel

Guide complet des variables d'environnement à configurer pour le déploiement Vercel de votre application de méditation biblique.

---

## 📋 VARIABLES OBLIGATOIRES

### 1. REACT_APP_BACKEND_URL
**Description :** URL du backend API  
**Valeur actuelle :** `https://scripture-explorer-6.preview.emergentagent.com`  
**Type :** URL complète avec protocole (https://)  
**Importance :** 🔴 Critique - L'application ne fonctionnera pas sans cette variable

**À configurer dans Vercel :**
```
Nom: REACT_APP_BACKEND_URL
Valeur: https://scripture-explorer-6.preview.emergentagent.com
Environnement: Production, Preview, Development
```

**Note :** Si vous avez un backend séparé sur un autre domaine, mettez son URL ici.

---

## 🔑 VARIABLES OPTIONNELLES (APIs Tierces)

### 2. GEMINI_API_KEY (Non utilisée actuellement)
**Description :** Clé API Google Gemini pour génération de contenu AI  
**Statut :** ⚠️ Actuellement en simulation (pas de vraie API appelée)  
**Type :** Chaîne de caractères (clé API)

**Si vous voulez activer l'API Gemini réelle :**
```
Nom: GEMINI_API_KEY
Valeur: [Votre clé depuis Google AI Studio]
Environnement: Production
```

**Où obtenir la clé :**
- Rendez-vous sur : https://makersuite.google.com/app/apikey
- Créez un projet Google Cloud
- Activez l'API Gemini
- Générez une clé API

### 3. BIBLE_API_KEY (Non utilisée actuellement)
**Description :** Clé API pour service Bible externe  
**Statut :** ⚠️ Non implémentée (fonctionnalité en simulation)  
**Type :** Chaîne de caractères (clé API)

**Si vous voulez activer une Bible API réelle :**
```
Nom: BIBLE_API_KEY
Valeur: [Votre clé depuis api.bible ou scripture.api.bible]
Environnement: Production
```

**Où obtenir la clé :**
- Option 1 : https://scripture.api.bible/ (API Bible gratuite)
- Option 2 : https://api.bible/ (API Bible officielle)

---

## 🗄️ VARIABLES BACKEND (Si vous déployez le backend)

**Note :** Ces variables sont pour le backend FastAPI. Si votre backend est déployé séparément (pas sur Vercel), configurez-les sur votre serveur backend.

### 4. MONGO_URL
**Description :** URL de connexion MongoDB  
**Valeur actuelle :** `mongodb://localhost:27017`  
**Type :** Connection string MongoDB

**Pour MongoDB Atlas (cloud) :**
```
Nom: MONGO_URL
Valeur: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
Environnement: Production
```

### 5. DB_NAME
**Description :** Nom de la base de données MongoDB  
**Valeur actuelle :** `test_database`  
**Type :** Chaîne de caractères

```
Nom: DB_NAME
Valeur: meditation_biblique_db
Environnement: Production
```

### 6. CORS_ORIGINS
**Description :** Origines autorisées pour CORS  
**Valeur actuelle :** `*` (tous les domaines)  
**Type :** Liste séparée par virgules

**Pour production (recommandé) :**
```
Nom: CORS_ORIGINS
Valeur: https://etude-khaki.vercel.app,https://www.votredomaine.com
Environnement: Production
```

---

## 📝 RÉCAPITULATIF DES VARIABLES

| Variable | Statut | Priorité | Où Configurer |
|----------|--------|----------|---------------|
| `REACT_APP_BACKEND_URL` | ✅ Obligatoire | 🔴 Haute | Vercel (Frontend) |
| `GEMINI_API_KEY` | ⚠️ Optionnelle | 🟡 Moyenne | Backend (si activé) |
| `BIBLE_API_KEY` | ⚠️ Optionnelle | 🟡 Moyenne | Backend (si activé) |
| `MONGO_URL` | ✅ Si backend | 🔴 Haute | Backend seulement |
| `DB_NAME` | ✅ Si backend | 🔴 Haute | Backend seulement |
| `CORS_ORIGINS` | ⚠️ Optionnelle | 🟢 Basse | Backend seulement |

---

## 🚀 COMMENT CONFIGURER SUR VERCEL

### Étape 1 : Accéder aux Paramètres
1. Allez sur votre projet Vercel : https://vercel.com/dashboard
2. Sélectionnez votre projet `etude-khaki`
3. Cliquez sur **Settings** (Paramètres)
4. Allez dans **Environment Variables**

### Étape 2 : Ajouter la Variable
1. Cliquez sur **Add New**
2. **Name** : `REACT_APP_BACKEND_URL`
3. **Value** : `https://scripture-explorer-6.preview.emergentagent.com`
4. **Environments** : Cochez `Production`, `Preview`, `Development`
5. Cliquez sur **Save**

### Étape 3 : Redéployer
1. Allez dans l'onglet **Deployments**
2. Cliquez sur **Redeploy** sur le dernier déploiement
3. Attendez que le déploiement se termine

---

## ⚙️ CONFIGURATION ACTUELLE

Votre fichier `.env` actuel dans POUR_GITHUB_CLEAN :
```env
REACT_APP_BACKEND_URL=https://scripture-explorer-6.preview.emergentagent.com
```

**✅ Cette variable est suffisante pour faire fonctionner l'application !**

Les APIs Gemini et Bible sont actuellement **simulées** dans le backend, donc vous n'avez pas besoin de clés API pour le moment.

---

## 🔍 VÉRIFICATION

Pour vérifier que vos variables sont bien configurées après déploiement :

1. **Ouvrez la console du navigateur** sur https://etude-khaki.vercel.app/
2. **Tapez :** `console.log(process.env.REACT_APP_BACKEND_URL)`
3. **Vous devriez voir :** `https://vercel-api-fix.preview.emergentagant.com`

Si vous voyez `undefined`, la variable n'est pas configurée correctement.

---

## 🛟 SUPPORT

**En cas de problème :**
- Vérifiez que la variable commence bien par `REACT_APP_` (requis pour Create React App)
- Vérifiez l'orthographe exacte (sensible à la casse)
- Redéployez après avoir ajouté/modifié des variables
- Videz le cache du navigateur si nécessaire

---

## 🔮 FUTURES VARIABLES (Si vous activez les vraies APIs)

Quand vous serez prêt à activer les vraies APIs Gemini/Bible :

1. **Ajoutez les clés dans le backend** (.env du backend)
2. **Modifiez le code backend** pour appeler les vraies APIs
3. **Testez en local** avant de déployer
4. **Déployez le backend** avec les nouvelles variables

---

**Date de création :** 12 octobre 2024  
**Dernière mise à jour :** 12 octobre 2024  
**Version :** 1.0

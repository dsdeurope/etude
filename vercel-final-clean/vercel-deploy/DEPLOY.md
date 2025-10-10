# Déploiement Vercel - Bible Study AI

## 🚀 Instructions de déploiement

### 1. Repository GitHub
1. Créez un nouveau repository sur GitHub
2. Uploadez TOUT le contenu de ce dossier (`vercel-deploy/`)
3. Assurez-vous que `package.json` est à la racine

### 2. Connexion Vercel
1. Allez sur [vercel.com](https://vercel.com)
2. Connectez votre repository GitHub
3. Vercel détectera automatiquement **Create React App**

### 3. Configuration (automatique)
- Build Command: `npm run build`
- Output Directory: `build` 
- Install Command: `npm install`

### 4. Variables d'environnement
Ajoutez dans Vercel Settings > Environment Variables :
```
REACT_APP_BACKEND_URL=https://votre-backend-url.com
```

### 5. Déploiement
- Push vers GitHub = déploiement automatique
- Première fois peut prendre 2-3 minutes

## ✅ Version testée
- Build local réussi : 86.8 kB
- React Scripts 5.0.1
- Tous les fichiers problématiques supprimés

## 🆘 Si problème
1. Vérifiez que `package.json` est à la racine GitHub
2. Vérifiez Node.js 18.x dans Vercel settings
3. Regardez les logs de build dans Vercel dashboard
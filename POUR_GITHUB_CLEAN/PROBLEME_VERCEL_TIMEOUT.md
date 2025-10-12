# 🚨 PROBLÈME VERCEL : "Failed to fetch" - Timeout Backend

**Date** : 12 Octobre 2024  
**Symptôme** : Fonctionne en local ✅ mais pas sur Vercel ❌  
**Erreur** : "Failed to fetch" lors de la génération verset par verset

---

## 🎯 DIAGNOSTIC

### Ce qui fonctionne :
- ✅ **Local** : Génération verset par verset fonctionne (8-15 secondes)
- ✅ **Backend local** : Timeout de 60 secondes appliqué
- ✅ **Frontend local** : Timeout de 60 secondes appliqué

### Ce qui ne fonctionne pas :
- ❌ **Vercel** : "Failed to fetch" lors de la génération
- ❌ **Raison** : Timeout backend Vercel trop court

---

## 🔍 CAUSE PRINCIPALE : LIMITATIONS VERCEL

### 1. Timeout Serverless Functions Vercel

Vercel impose des **limites de timeout strictes** pour les serverless functions :

| Plan Vercel | Timeout Maximum | Votre Besoin |
|-------------|----------------|--------------|
| **Hobby (Gratuit)** | **10 secondes** | ❌ Insuffisant (15-20s) |
| **Pro** | **60 secondes** | ✅ Suffisant |
| **Enterprise** | **900 secondes** | ✅ Largement suffisant |

**Votre situation** :
- Bible API génère 5 versets en **15-20 secondes**
- Plan Hobby Vercel timeout après **10 secondes**
- Résultat : **"Failed to fetch"** avant la fin de la génération

### 2. Configuration vercel.json

Si le `vercel.json` n'est pas configuré correctement, le timeout par défaut s'applique.

---

## ✅ SOLUTIONS

### Solution 1 : Configurer le Timeout dans vercel.json (RECOMMANDÉ)

**Fichier** : `/app/POUR_GITHUB_CLEAN/vercel.json`

```json
{
  "functions": {
    "api/**/*.py": {
      "maxDuration": 60
    }
  },
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://votre-backend-vercel.vercel.app/api/:path*"
    }
  ]
}
```

**⚠️ Important** : `maxDuration: 60` nécessite un **plan Pro Vercel** (20$/mois)

### Solution 2 : Réduire le Temps de Génération

Au lieu de générer 5 versets d'un coup, **générer 2-3 versets** :

**Modification Backend** : `/app/backend/server.py`

```python
# Réduire le nombre de versets par batch
DEFAULT_VERSES_PER_BATCH = 2  # Au lieu de 5
```

**Avantages** :
- ✅ Génération < 10 secondes
- ✅ Fonctionne sur plan Hobby gratuit
- ✅ Pas besoin d'upgrade Pro

**Inconvénients** :
- ⚠️ Plus de clics "Suivant" nécessaires
- ⚠️ Plus de requêtes API

### Solution 3 : Déployer Backend sur Service avec Timeout Plus Long

**Alternatives à Vercel pour le Backend** :

| Service | Timeout Gratuit | Prix |
|---------|-----------------|------|
| **Railway.app** | 300 secondes | Gratuit (5$/mois usage) |
| **Render.com** | 300 secondes | Gratuit |
| **Fly.io** | Illimité | Gratuit (petite instance) |
| **DigitalOcean App Platform** | 300 secondes | 5$/mois |

**Garder** : Frontend sur Vercel (gratuit)  
**Déplacer** : Backend sur Railway/Render/Fly.io

### Solution 4 : Mise en Cache (Complexe mais Efficace)

**Principe** :
1. Backend génère le contenu en arrière-plan
2. Stocke dans MongoDB
3. Frontend récupère depuis cache (< 1 seconde)

**Avantages** :
- ✅ Réponse instantanée après première génération
- ✅ Réduit charge API
- ✅ Fonctionne sur plan Hobby

**Inconvénients** :
- ⚠️ Nécessite modifications importantes
- ⚠️ Première génération toujours lente

---

## 🔧 VÉRIFICATIONS À FAIRE

### 1. Vérifier Plan Vercel Actuel

1. Allez sur https://vercel.com/dashboard
2. Settings → General → Plan
3. Vérifiez : **Hobby** ou **Pro** ?

**Si Hobby** : Timeout limité à 10 secondes ❌

### 2. Vérifier vercel.json Backend

**Fichier backend** : `vercel.json`

```json
{
  "functions": {
    "api/**/*.py": {
      "maxDuration": 10  // ← 10 secondes par défaut (Hobby)
    }
  }
}
```

**Si vous avez Pro** : Changez à `"maxDuration": 60`

### 3. Tester Temps de Génération Backend

```bash
# Tester combien de temps prend la génération
time curl -X POST https://votre-backend.vercel.app/api/generate-verse-by-verse \
  -H "Content-Type: application/json" \
  -d '{"passage": "Genèse 1:1-5", "version": "LSG"}'
```

**Si > 10 secondes** : Timeout Vercel dépassé

### 4. Vérifier Logs Vercel

1. Vercel Dashboard → Deployments → [Votre déploiement]
2. Function Logs
3. Rechercher : "ETIMEDOUT" ou "Function exceeded maximum duration"

---

## 📊 COMPARAISON LOCAL vs VERCEL

### En Local (Fonctionne) ✅

```
Frontend (React) ──60s timeout──> Backend (FastAPI)
                                       │
                                       ├─ Génère 5 versets (15-20s)
                                       │
                                       └─> Retour contenu
```

**Résultat** : Succès car backend peut prendre 60s

### Sur Vercel (Échoue) ❌

```
Frontend (React) ──60s timeout──> Backend Vercel Serverless
                                       │
                                       ├─ Génère 5 versets (15-20s)
                                       │
                                       X TIMEOUT 10s (Hobby plan)
                                       
Frontend reçoit : "Failed to fetch"
```

**Résultat** : Échec car Vercel timeout à 10s

---

## 💡 SOLUTION RECOMMANDÉE (IMMÉDIATE)

### Option A : Réduire à 2 Versets par Batch (Gratuit)

**Modification simple** :

1. **Backend** : `server.py`
```python
# Ligne ~745
end_verse = request.get('end_verse', 2)  # Au lieu de 5
```

2. **Frontend** : `VersetParVersetPage.js`
```javascript
// Ligne ~415
const versesPerBatch = 2; // Au lieu de 5
```

**Temps de génération** : 6-8 secondes ✅ (< 10s Hobby)

### Option B : Upgrade Vercel Pro (Payant)

**Coût** : 20$/mois  
**Avantage** : Timeout 60 secondes  
**Configuration** : `vercel.json` → `"maxDuration": 60`

### Option C : Backend sur Railway (Gratuit)

**Étapes** :
1. Créer compte Railway.app
2. Déployer backend depuis GitHub
3. Obtenir URL backend Railway
4. Mettre à jour `REACT_APP_BACKEND_URL` sur Vercel frontend

**Coût** : Gratuit (5$/mois si dépassement)

---

## 🚀 DÉPLOIEMENT RAPIDE : Solution A (2 Versets)

### 1. Modifier Backend

```bash
# Éditer server.py
nano /app/POUR_GITHUB_CLEAN/backend_server_COMPLET.py

# Ligne 745 : Changer
end_verse = request.get('end_verse', 2)  # Au lieu de 5
```

### 2. Modifier Frontend

```bash
# Éditer VersetParVersetPage.js
nano /app/POUR_GITHUB_CLEAN/src/VersetParVersetPage.js

# Ligne ~415 : Changer
const versesPerBatch = 2; // Au lieu de 5
```

### 3. Déployer

```bash
cd /app/POUR_GITHUB_CLEAN/
git add .
git commit -m "⚡ Réduit batch à 2 versets pour Vercel Hobby (timeout 10s)"
git push origin main
```

**Résultat** : Génération < 10 secondes, fonctionne sur Vercel Hobby ✅

---

## 📋 CHECKLIST DEBUG VERCEL

Avant de modifier le code :

- [ ] Vérifier plan Vercel (Hobby ou Pro ?)
- [ ] Vérifier logs Vercel pour erreur timeout
- [ ] Tester temps de génération backend Vercel
- [ ] Vérifier `vercel.json` configuration
- [ ] Confirmer que variables d'environnement sont configurées
- [ ] Tester génération locale (fonctionne ?)

Si timeout confirmé :

- [ ] Option A : Réduire à 2 versets (gratuit)
- [ ] Option B : Upgrade Pro (payant)
- [ ] Option C : Backend Railway (gratuit)

---

## ⚠️ POURQUOI "ÇA MARCHAIT AVANT" ?

### Hypothèses Possibles :

1. **Quotas Gemini disponibles avant** :
   - Gemini génère en 3-6 secondes (< 10s) ✅
   - Bible API génère en 15-20 secondes (> 10s) ❌
   - Maintenant quotas épuisés → Bible API → Timeout

2. **Changement configuration Vercel** :
   - Timeout augmenté temporairement ?
   - Plan upgradé puis downgrade ?

3. **Nombre de versets changé** :
   - Avant : 2-3 versets (< 10s)
   - Maintenant : 5 versets (> 10s)

**Solution** : Réduire batch à 2 versets ou upgrade Pro

---

## 📞 RESSOURCES

### Documentation Vercel Timeouts
- https://vercel.com/docs/functions/serverless-functions/runtimes#max-duration

### Plans Vercel
- https://vercel.com/pricing

### Alternatives Backend
- Railway : https://railway.app/
- Render : https://render.com/
- Fly.io : https://fly.io/

---

## ✅ RÉSUMÉ

### Problème
- ❌ Vercel Hobby timeout à 10s
- ❌ Bible API génère en 15-20s
- ❌ Résultat : "Failed to fetch"

### Solution Immédiate (Gratuite)
- ✅ Réduire batch à 2 versets (6-8s)
- ✅ Fonctionne sur Vercel Hobby
- ✅ Aucun coût supplémentaire

### Solution Long Terme (Recommandée)
- ✅ Upgrade Vercel Pro (60s timeout)
- ✅ Ou backend sur Railway (300s timeout gratuit)
- ✅ Génération 5 versets sans problème

---

**Status** : ⚠️ Limitation Vercel identifiée  
**Action recommandée** : Réduire batch à 2 versets  
**Alternative** : Upgrade Vercel Pro ou backend Railway

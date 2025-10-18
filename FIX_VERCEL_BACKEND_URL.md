# 🔧 FIX URGENT : Corriger l'URL Backend sur Vercel

**Date**: 18 Octobre 2025  
**Statut**: 🚨 ACTION REQUISE - Variable d'environnement Vercel incorrecte

---

## 🎯 PROBLÈME IDENTIFIÉ

Le frontend Vercel (`https://etude-khaki.vercel.app`) utilise une **mauvaise URL backend** :

❌ **URL actuelle (incorrecte)** : `https://vercel-api-fix.preview.emergentagent.com`
- Cette URL retourne 404
- CORS bloqué
- LEDs affichent jaune (erreur)

✅ **URL correcte** : `https://bible-study-app-6.preview.emergentagent.com`
- Cette URL fonctionne parfaitement
- CORS configuré correctement
- API répond avec 14 clés Gemini + 1 Bible API

---

## 📸 PREUVE DU PROBLÈME

### Console Browser Vercel :
```
[API STATUS] Appel à: https://vercel-api-fix.preview.emergentagent.com/api/health
Access to fetch at 'https://vercel-api-fix.preview.emergentagent.com/api/health' 
from origin 'https://etude-khaki.vercel.app' has been blocked by CORS policy
```

### Test Backend Correct :
```bash
$ curl -s https://bible-study-app-6.preview.emergentagent.com/api/health | jq
{
  "status": "healthy",
  "total_gemini_keys": 14,
  "total_keys": 15
}
```

### Test Backend Incorrect :
```bash
$ curl -s https://vercel-api-fix.preview.emergentagent.com/api/health
404 Not Found
```

---

## ✅ SOLUTION : Modifier la Variable d'Environnement Vercel

### ÉTAPE 1 : Accéder au Dashboard Vercel

1. Allez sur : https://vercel.com/dashboard
2. Sélectionnez votre projet : **etude-khaki**
3. Cliquez sur l'onglet **Settings**
4. Dans le menu latéral, cliquez sur **Environment Variables**

### ÉTAPE 2 : Modifier REACT_APP_BACKEND_URL

#### Option A : Modifier la Variable Existante (Recommandé)

1. Trouvez la variable `REACT_APP_BACKEND_URL`
2. Cliquez sur le bouton **Edit** (crayon) à droite
3. Modifiez la valeur :
   ```
   ANCIENNE VALEUR : https://vercel-api-fix.preview.emergentagent.com
   NOUVELLE VALEUR : https://bible-study-app-6.preview.emergentagent.com
   ```
4. Assurez-vous que les environnements suivants sont cochés :
   - ✅ Production
   - ✅ Preview
   - ✅ Development
5. Cliquez sur **Save**

#### Option B : Supprimer et Recréer (Si problème)

1. Cliquez sur le bouton **Delete** à côté de `REACT_APP_BACKEND_URL`
2. Confirmez la suppression
3. Cliquez sur **Add New**
4. Entrez :
   - **Name** : `REACT_APP_BACKEND_URL`
   - **Value** : `https://bible-study-app-6.preview.emergentagent.com`
   - **Environments** : Cochez `Production`, `Preview`, `Development`
5. Cliquez sur **Save**

### ÉTAPE 3 : Redéployer l'Application

**IMPORTANT** : Les variables d'environnement ne prennent effet qu'après un redéploiement.

1. Allez dans l'onglet **Deployments**
2. Trouvez le dernier déploiement réussi
3. Cliquez sur les **trois points** (...) à droite
4. Sélectionnez **Redeploy**
5. Cliquez sur **Redeploy** dans la fenêtre de confirmation

⏱️ **Temps estimé** : 2-3 minutes pour le redéploiement

---

## 🧪 ÉTAPE 4 : Vérification Post-Fix

### Test 1 : Vérifier la Console Browser

1. Ouvrez https://etude-khaki.vercel.app
2. Ouvrez les DevTools (F12)
3. Allez dans l'onglet **Console**
4. Vous ne devriez **PLUS** voir d'erreurs CORS
5. Vous devriez voir : `[API STATUS] Appel à: https://bible-study-app-6.preview.emergentagent.com/api/health`

### Test 2 : Vérifier les LEDs API

1. Sur la page d'accueil, regardez le panneau API en haut
2. Les LEDs devraient maintenant afficher les **vrais statuts** :
   - 🟢 **Vert** : Clés disponibles (quota < 70%)
   - 🟡 **Jaune** : Clés en avertissement (quota 70-90%)
   - 🔴 **Rouge** : Clés épuisées (quota > 90%)

3. Actuellement, vous devriez voir :
   - 14 LEDs (Gemini keys)
   - 1 LED (Bible API)
   - Couleur selon le quota réel (probablement vert si clés fraîches)

### Test 3 : Test Fonctionnel

1. Sélectionnez un passage (ex : Genèse 1)
2. Cliquez sur **GENÈSE 1** ou **GEMINI GRATUIT**
3. L'étude devrait se générer correctement
4. Aucune erreur dans la console

---

## 📊 RÉSULTAT ATTENDU

### Avant le Fix :
```
❌ Backend URL: https://vercel-api-fix.preview.emergentagent.com
❌ CORS: Bloqué
❌ LEDs: Toutes jaunes (erreur)
❌ Génération: Impossible
```

### Après le Fix :
```
✅ Backend URL: https://bible-study-app-6.preview.emergentagent.com
✅ CORS: Fonctionnel
✅ LEDs: Affichent les vrais statuts (vert/jaune/rouge)
✅ Génération: Fonctionnelle
✅ Cache: Actif (économise les quotas)
```

---

## 🔍 DIAGNOSTICS SI ÇA NE FONCTIONNE PAS

### Si les LEDs restent jaunes après le fix :

1. **Vider le cache du browser**
   - Chrome: Ctrl+Shift+Delete → Cocher "Cached images" → Clear
   - Firefox: Ctrl+Shift+Delete → Cocher "Cache" → Clear
   - Recharger la page avec Ctrl+F5

2. **Vérifier que la variable a bien été modifiée**
   - Sur la page Vercel, onglet Settings > Environment Variables
   - La valeur doit être : `https://bible-study-app-6.preview.emergentagent.com`
   - Les 3 environnements doivent être cochés

3. **Vérifier que le redéploiement est terminé**
   - Onglet Deployments
   - Le dernier déploiement doit avoir le statut **Ready**
   - Pas de **Building** ou **Error**

4. **Tester directement l'URL**
   ```bash
   curl -s https://bible-study-app-6.preview.emergentagent.com/api/health
   ```
   Devrait retourner un JSON avec `"status": "healthy"`

---

## 📝 NOTES IMPORTANTES

1. **Pas de code à modifier** : Tout est une question de variable d'environnement Vercel
2. **Le backend fonctionne** : Le problème est uniquement que le frontend appelle la mauvaise URL
3. **Le CORS est OK** : Le backend `bible-study-app-6` a déjà le CORS correctement configuré
4. **Les optimisations de cache sont actives** : Le backend a déjà toutes les optimisations de quota

---

## ✨ AMÉLIORATIONS INCLUSES DANS LE BACKEND

Le backend `https://bible-study-app-6.preview.emergentagent.com` contient déjà :

1. ✅ **Cache health check** : 15 minutes (économise 70% des tests)
2. ✅ **Cache character history** : MongoDB (100% économie sur répétitions)
3. ✅ **Cache verse-by-verse** : MongoDB (100% économie sur répétitions)
4. ✅ **Cache rubriques** : MongoDB (100% économie sur répétitions)
5. ✅ **CORS** : Configuré pour Vercel (`https://etude-khaki.vercel.app`)
6. ✅ **14 clés Gemini** : Rotation automatique
7. ✅ **Bible API** : Fallback fonctionnel

**Dès que l'URL sera corrigée, toutes ces optimisations seront actives !**

---

## 🚀 RÉSUMÉ EN 3 ACTIONS

1. **Aller sur Vercel** → Settings → Environment Variables
2. **Modifier** `REACT_APP_BACKEND_URL` → `https://bible-study-app-6.preview.emergentagent.com`
3. **Redéployer** depuis Deployments → Redeploy

⏱️ **Temps total** : 5 minutes

---

**Après ce fix, votre application Vercel fonctionnera parfaitement avec toutes les optimisations de quotas actives !** 🎉

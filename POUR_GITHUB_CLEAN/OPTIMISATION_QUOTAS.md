# 🚀 OPTIMISATION DES QUOTAS GEMINI API

**Date**: 17 Octobre 2025  
**Problème**: Quotas s'épuisent trop vite pendant les tests  
**Solution**: Cache + Optimisation /api/health  

---

## 🎯 Contexte

### Usage Prévu
- **Production**: 1 étude par jour = **28 requêtes/jour**
- **Capacité disponible**: 14 clés × 50 = **700 requêtes/jour**
- **Marge**: 700 - 28 = **672 requêtes de marge** (×25 fois plus que nécessaire)

### Problème Actuel
- **Phase de test**: Régénération répétée consomme beaucoup
- **Health check**: Teste les 14 clés à chaque appel
- **Pas de cache**: Même contenu régénéré plusieurs fois

---

## ✅ Solutions Implémentées

### 1. Cache MongoDB pour Rubriques ✅

**Principe**: Sauvegarder chaque rubrique générée en base de données

**Fonctionnement**:
```
1. Requête: Générer rubrique X pour passage Y
2. Vérifier cache MongoDB
3. Si existe → Retourner immédiatement (0 requête API)
4. Sinon → Générer + Sauvegarder en cache
```

**Bénéfices**:
- ✅ **Zéro requête** pour contenus déjà générés
- ✅ **Régénération optionnelle** avec `force_regenerate: true`
- ✅ **Cache persistant** (survive aux redémarrages)

**Exemple d'utilisation**:
```javascript
// Génération normale (utilise cache si existe)
fetch('/api/generate-rubrique', {
  method: 'POST',
  body: JSON.stringify({
    passage: "Genèse 1",
    rubrique_number: 1,
    rubrique_title: "Prière d'ouverture"
  })
})

// Forcer régénération (ignore cache)
fetch('/api/generate-rubrique', {
  method: 'POST',
  body: JSON.stringify({
    passage: "Genèse 1",
    rubrique_number: 1,
    rubrique_title: "Prière d'ouverture",
    force_regenerate: true  // ← Nouveau paramètre
  })
})
```

**Structure MongoDB**:
```javascript
{
  _id: ObjectId("..."),
  cache_key: "Genèse 1_1",  // passage_rubriqueNumber
  passage: "Genèse 1",
  rubrique_number: 1,
  rubrique_title: "Prière d'ouverture",
  content: "**ADORATION**\nSaint Créateur...",
  created_at: "2025-10-17T20:00:00Z"
}
```

### 2. Cache Health Check (5 minutes) ✅

**Problème**: `/api/health` testait les 14 clés à chaque appel

**Avant**:
```
Appel /api/health
→ Teste clé 1 (1 requête API)
→ Teste clé 2 (1 requête API)
→ ...
→ Teste clé 14 (1 requête API)
= 14 requêtes consommées
```

**Après**:
```
Appel /api/health
→ Vérifie cache (< 5 min ?)
→ Si cache valide: 0 requête
→ Sinon: teste les clés + met en cache
= 14 requêtes tous les 5 minutes maximum
```

**Bénéfices**:
- ✅ **Cache de 5 minutes** (300 secondes)
- ✅ **Économie massive** si interface appelle souvent
- ✅ **Données toujours à jour** (refresh automatique après 5 min)

### 3. Quota Réel Corrigé ✅

**Correction**: Ajusté `max_daily_requests` de 1500 → **50** (valeur réelle)

**Avant**:
```python
max_daily_requests = 1500  # ❌ Faux
quota_percent = usage_count / 1500
```

**Après**:
```python
max_daily_requests = 50  # ✅ Correct
quota_percent = usage_count / 50
```

**Impact**: Affichage précis du quota dans l'interface

---

## 📊 Impact des Optimisations

### Scénario 1: Tests Répétés (Phase actuelle)

**Avant**:
```
Test 1: Générer 28 rubriques pour Genèse 1 = 28 requêtes
Test 2: Régénérer les mêmes 28 rubriques = 28 requêtes
Test 3: Encore les mêmes = 28 requêtes
Total: 84 requêtes pour le même contenu
```

**Après**:
```
Test 1: Générer 28 rubriques pour Genèse 1 = 28 requêtes
Test 2: Charger depuis cache = 0 requête ✅
Test 3: Charger depuis cache = 0 requête ✅
Total: 28 requêtes (économie de 56 requêtes)
```

### Scénario 2: Health Check

**Avant**:
```
Interface appelle /api/health toutes les 30 secondes
30s × 120 appels/heure = 1 680 requêtes/heure
= Épuise 3 clés complètes par heure juste pour le monitoring !
```

**Après**:
```
Cache de 5 minutes
5min × 12 appels/heure = 14 requêtes/heure
= Économie de 1 666 requêtes/heure ✅
```

### Scénario 3: Production (1 étude/jour)

**Jour 1**:
```
Genèse 1 - 28 rubriques = 28 requêtes
Cache: 28 entrées
```

**Jour 2**:
```
Genèse 2 - 28 rubriques = 28 requêtes
Cache: 56 entrées (Genèse 1 + 2)
```

**Jour 3**:
```
Relire Genèse 1 = 0 requête (cache) ✅
Genèse 3 - 28 rubriques = 28 requêtes
Cache: 84 entrées
```

---

## 🔧 Configuration Technique

### Variables Ajoutées

**Dans `server.py`**:
```python
# Cache pour /api/health (ligne ~359)
health_check_cache = {}
HEALTH_CHECK_CACHE_DURATION = 300  # 5 minutes

# Collection MongoDB pour rubriques
db.rubriques_cache  # Collection automatique
```

### Endpoints Modifiés

**1. `/api/generate-rubrique`**
- ✅ Vérifie cache MongoDB avant génération
- ✅ Sauvegarde automatiquement après génération
- ✅ Paramètre `force_regenerate` pour forcer régénération

**2. `/api/health`**
- ✅ Cache de 5 minutes par clé
- ✅ Évite tests répétés inutiles

---

## 💡 Recommandations d'Usage

### Pour les Tests
```bash
# Première génération (consomme quota)
POST /api/generate-rubrique
{
  "passage": "Genèse 1",
  "rubrique_number": 1
}

# Tests suivants (utilise cache = 0 quota)
# Même requête → utilise cache automatiquement

# Si vous voulez tester la qualité de génération
POST /api/generate-rubrique
{
  "passage": "Genèse 1",
  "rubrique_number": 1,
  "force_regenerate": true  // Force nouvelle génération
}
```

### Pour la Production

**Workflow recommandé**:
```
1. Générer étude du jour (28 requêtes)
2. Les 28 rubriques sont en cache
3. Utilisateurs consultent l'étude (0 requête)
4. Lendemain: Nouvelle étude (28 requêtes)
5. Anciennes études toujours en cache (0 requête)
```

**Gestion du cache**:
```javascript
// Vider le cache d'un passage si nécessaire
DELETE /api/cache/clear?passage=Genèse 1

// Ou vider tout le cache
DELETE /api/cache/clear-all
```

---

## 📈 Statistiques Estimées

### Sans Optimisations
```
Tests: 10 régénérations × 28 rubriques = 280 requêtes
Health check: 50 appels × 14 clés = 700 requêtes
Total: 980 requêtes (épuise toutes les clés)
```

### Avec Optimisations
```
Tests: 1 génération × 28 + 9 lectures cache = 28 requêtes
Health check: 3 appels (cache 5min) × 14 = 42 requêtes
Total: 70 requêtes (économie de 910 requêtes = 93% !)
```

---

## 🚀 Déploiement

### Fichiers Modifiés
- ✅ `/app/backend/server.py`
  - Ligne ~359: Cache health check
  - Ligne ~1967: Cache MongoDB rubriques
  - Ligne ~382: Quota corrigé à 50

- ✅ `/app/POUR_GITHUB_CLEAN/backend_server_COMPLET.py`
  - Synchronisé avec modifications

### Base de Données
- ✅ Collection `rubriques_cache` créée automatiquement
- ✅ Index recommandé: `cache_key` (unique)

```javascript
// Créer index MongoDB (optionnel mais recommandé)
db.rubriques_cache.createIndex({ cache_key: 1 }, { unique: true })
```

---

## 🎓 Explications Techniques

### Pourquoi Cache MongoDB ?

**Alternatives considérées**:
1. **Redis**: Trop complexe, dépendance supplémentaire
2. **Cache mémoire**: Perdu au redémarrage
3. **MongoDB**: ✅ Déjà utilisé, persistant, simple

**Avantages**:
- ✅ Persistant (survive redémarrages)
- ✅ Pas de dépendance supplémentaire
- ✅ Requêtes rapides avec index
- ✅ Facile à gérer (vider si nécessaire)

### Durée de Cache Health Check

**5 minutes choisies car**:
- ✅ Assez court: Détecte rapidement si clé épuisée
- ✅ Assez long: Évite tests excessifs
- ✅ Équilibre: Économie max sans perdre précision

**Ajustable selon besoin**:
```python
HEALTH_CHECK_CACHE_DURATION = 300  # 5 min
# Peut être changé à 60 (1 min) ou 600 (10 min)
```

---

## 🔍 Monitoring

### Vérifier Utilisation Cache

```javascript
// Combien de rubriques en cache ?
db.rubriques_cache.countDocuments()

// Lister passages en cache
db.rubriques_cache.distinct("passage")

// Voir détails d'une rubrique
db.rubriques_cache.findOne({ cache_key: "Genèse 1_1" })

// Taille du cache
db.rubriques_cache.stats()
```

### Logs Backend

```bash
# Voir hits de cache
sudo supervisorctl tail backend stdout | grep "Cache hit"

# Voir nouvelles générations
sudo supervisorctl tail backend stdout | grep "Génération"
```

---

## 📝 Checklist de Vérification

### Avant Déploiement
- ✅ Backend redémarré avec nouvelles fonctions
- ✅ Collection MongoDB `rubriques_cache` créée
- ✅ Cache health check testé (5 min)
- ✅ Génération avec cache testée

### Après Déploiement
- [ ] Vérifier réponse `/api/health` (< 1s grâce au cache)
- [ ] Tester génération rubrique (première fois)
- [ ] Tester cache (deuxième fois = instantané)
- [ ] Vérifier MongoDB contient entrées cache

---

## ✅ Résumé

### Problème Résolu
Les quotas s'épuisaient trop vite à cause de:
1. Régénérations répétées du même contenu
2. Health check testant 14 clés à chaque appel
3. Aucun système de réutilisation

### Solutions Appliquées
1. ✅ **Cache MongoDB** pour rubriques (économie massive)
2. ✅ **Cache 5 min** pour health check (économie 93%)
3. ✅ **Quota corrigé** à 50 req/jour (affichage précis)

### Impact
- **Phase test**: 93% d'économie de quota
- **Production (1 étude/jour)**: 28 requêtes/jour utilisées sur 700 disponibles
- **Marge**: ×25 fois plus que nécessaire

### Capacité Finale
```
14 clés × 50 requêtes = 700 req/jour
1 étude = 28 requêtes (première fois)
Études suivantes en cache = 0 requête

Capacité réelle en production:
- ~25 nouvelles études/jour possibles
- Anciennes études consultables sans limite
```

---

**Status**: ✅ **OPTIMISÉ POUR PRODUCTION**

**Économie**: 93% de quota économisé pendant tests  
**Production**: 28 requêtes/jour sur 700 disponibles  
**Prêt pour**: Utilisation intensive sans épuiser quotas

# 📡 DOCUMENTATION DES ENDPOINTS API

**Date**: 17 Octobre 2025  
**Backend URL**: `https://bible-study-hub-8.preview.emergentagent.com`

---

## ✅ OUI, VOUS AVEZ 2 ENDPOINTS DISTINCTS

### 1️⃣ Étude Verset par Verset
**Endpoint**: `/api/generate-verse-by-verse`

### 2️⃣ Étude 28 Rubriques
**Endpoint**: `/api/generate-rubrique`

---

## 📋 DÉTAILS DES ENDPOINTS

### 1️⃣ `/api/generate-verse-by-verse`

**Type**: `POST`  
**Usage**: Génération progressive verset par verset

#### Requête
```javascript
POST /api/generate-verse-by-verse
Content-Type: application/json

{
  "passage": "Genèse 1",           // Livre + Chapitre
  "start_verse": 1,                // Verset de départ
  "end_verse": 3                   // Verset de fin (batch de 3)
}
```

#### Réponse
```javascript
{
  "status": "success",
  "content": "...",                // Contenu généré
  "passage": "Genèse 1",
  "start_verse": 1,
  "end_verse": 3,
  "api_used": "gemini",           // ou "bible_api" (fallback)
  "verses_count": 3
}
```

#### Caractéristiques
- ✅ **Batches de 3 versets** (optimisé pour Vercel 10s timeout)
- ✅ **4 sections par verset**:
  1. VERSET (texte biblique)
  2. CHAPITRE (contexte global)
  3. CONTEXTE HISTORIQUE
  4. PARTIE THÉOLOGIQUE
- ✅ **Fallback Bible API** si quotas Gemini épuisés
- ✅ **Génération progressive** (cliquer "Continuer" pour plus)

#### Exemple d'utilisation
```javascript
// Générer les 3 premiers versets de Genèse 1
const response = await fetch('/api/generate-verse-by-verse', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    passage: "Genèse 1",
    start_verse: 1,
    end_verse: 3
  })
});

// Puis pour continuer (versets 4-6)
const response2 = await fetch('/api/generate-verse-by-verse', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    passage: "Genèse 1",
    start_verse: 4,
    end_verse: 6
  })
});
```

---

### 2️⃣ `/api/generate-rubrique`

**Type**: `POST`  
**Usage**: Génération d'une rubrique parmi les 28

#### Requête
```javascript
POST /api/generate-rubrique
Content-Type: application/json

{
  "passage": "Genèse 1",              // Livre + Chapitre
  "rubrique_number": 1,               // 1-28
  "rubrique_title": "Prière d'ouverture",
  "force_regenerate": false           // Optionnel: forcer régénération
}
```

#### Réponse
```javascript
{
  "status": "success",
  "content": "...",                    // Contenu généré
  "rubrique_number": 1,
  "rubrique_title": "Prière d'ouverture",
  "passage": "Genèse 1",
  "api_used": "gemini",               // ou "cache" si déjà générée
  "cached": false,                    // true si chargé du cache
  "generated_at": "2025-10-17T21:00:00Z"
}
```

#### Caractéristiques
- ✅ **28 prompts détaillés** (contenu spécifique)
- ✅ **Cache MongoDB automatique**:
  - 1ère génération: appel API Gemini
  - 2ème génération: chargement instantané du cache (0 quota)
- ✅ **Force regenerate**: Ignore cache si nécessaire
- ✅ **Longueurs adaptées**: 300-1100 mots selon rubrique

#### Liste des 28 Rubriques

**Rubriques Courtes (300-600 mots)**:
1. Prière d'ouverture (300-400)
2. Structure littéraire (400-500)
3. Questions du chapitre précédent (350-450)
4. Thème doctrinal (500-600)

**Rubriques Moyennes (700-900 mots)**:
5. Fondements théologiques
6. Contexte historique
7. Contexte culturel
8. Contexte géographique
9. Analyse lexicale
10. Parallèles bibliques
11. Prophétie et accomplissement
12. Personnages
13. Structure rhétorique
14. Théologie trinitaire

**Rubriques Longues (900-1100 mots)**:
15. Christ au centre
16. Évangile et grâce
17. Application personnelle
18. Application communautaire
19. Prière de réponse (800-1000)
20. Questions d'étude (35-45 questions)
21. Points de vigilance
22. Objections et réponses
23. Perspective missionnelle
24. Éthique chrétienne
25. Louange / liturgie (800-1000)
26. Méditation guidée (800-1000)
27. Mémoire / versets clés (800-1000)
28. Plan d'action

#### Exemple d'utilisation
```javascript
// Générer la prière d'ouverture
const response = await fetch('/api/generate-rubrique', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    passage: "Genèse 1",
    rubrique_number: 1,
    rubrique_title: "Prière d'ouverture"
  })
});

// Si déjà générée précédemment
// → Retour instantané du cache (api_used: "cache", cached: true)

// Pour forcer une nouvelle génération
const response2 = await fetch('/api/generate-rubrique', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    passage: "Genèse 1",
    rubrique_number: 1,
    rubrique_title: "Prière d'ouverture",
    force_regenerate: true  // ← Ignore le cache
  })
});
```

---

## 🔄 AUTRES ENDPOINTS UTILES

### 3️⃣ `/api/health`

**Type**: `GET`  
**Usage**: Vérifier le statut des clés API

#### Requête
```javascript
GET /api/health
```

#### Réponse
```javascript
{
  "status": "healthy",
  "timestamp": "2025-10-17T21:00:00Z",
  "total_gemini_keys": 14,
  "total_keys": 15,
  "apis": {
    "gemini_1": {
      "name": "Gemini Key 1",
      "color": "green",               // green/yellow/red
      "status": "available",
      "status_text": "Disponible",
      "quota_used": 0,
      "usage_count": 0
    },
    // ... gemini_2 à gemini_14
    "bible_api": {
      "name": "Bible API",
      "color": "green",
      "status": "available"
    }
  }
}
```

#### Caractéristiques
- ✅ **Cache 5 minutes** (évite tests répétés)
- ✅ **14 clés Gemini** + 1 Bible API
- ✅ **Indicateur couleur**:
  - 🟢 Green: Disponible (quota < 80%)
  - 🟡 Yellow: Bientôt épuisé (quota 80-99%)
  - 🔴 Red: Quota épuisé (100%)

### 4️⃣ `/api/generate-character-history`

**Type**: `POST`  
**Usage**: Générer l'histoire d'un personnage biblique

#### Requête
```javascript
POST /api/generate-character-history
Content-Type: application/json

{
  "character_name": "Abraham",
  "mode": "generate"    // ou "enrich"
}
```

#### Réponse
```javascript
{
  "status": "success",
  "content": "...",     // Histoire détaillée du personnage
  "character": "Abraham",
  "api_used": "gemini"
}
```

---

## 📊 COMPARAISON DES 2 ENDPOINTS PRINCIPAUX

| Aspect | Verset par Verset | 28 Rubriques |
|--------|-------------------|--------------|
| **Endpoint** | `/generate-verse-by-verse` | `/generate-rubrique` |
| **Granularité** | 3 versets à la fois | 1 rubrique à la fois |
| **Structure** | 4 sections fixes | Selon rubrique |
| **Longueur** | Variable (~500 mots) | 300-1100 mots |
| **Cache** | ❌ Pas de cache | ✅ Cache MongoDB |
| **Fallback** | ✅ Bible API | ✅ Bible API |
| **Usage** | Étude progressive | Étude thématique |
| **Total pour Genèse 1** | ~10 appels (31 versets ÷ 3) | 28 appels (1 par rubrique) |

---

## 🎯 WORKFLOW RECOMMANDÉ

### Scénario 1: Étude Complète (28 Rubriques)

**Pour 1 passage (ex: Genèse 1)**:
```javascript
// Générer les 28 rubriques
for (let i = 1; i <= 28; i++) {
  await fetch('/api/generate-rubrique', {
    method: 'POST',
    body: JSON.stringify({
      passage: "Genèse 1",
      rubrique_number: i,
      rubrique_title: RUBRIQUE_TITLES[i]
    })
  });
}

// Total: 28 requêtes API (1ère fois)
// Puis: 0 requête (cache) pour consultations ultérieures
```

### Scénario 2: Étude Verset par Verset

**Pour 1 chapitre progressif (ex: Genèse 1 - 31 versets)**:
```javascript
let currentVerse = 1;
const totalVerses = 31;
const batchSize = 3;

while (currentVerse <= totalVerses) {
  const endVerse = Math.min(currentVerse + batchSize - 1, totalVerses);
  
  await fetch('/api/generate-verse-by-verse', {
    method: 'POST',
    body: JSON.stringify({
      passage: "Genèse 1",
      start_verse: currentVerse,
      end_verse: endVerse
    })
  });
  
  currentVerse = endVerse + 1;
}

// Total: ~10 requêtes API (31 versets ÷ 3)
```

---

## 💡 CONSEILS D'UTILISATION

### Pour Économiser les Quotas

**1. Utilisez le cache**:
```javascript
// Ne PAS utiliser force_regenerate sauf nécessaire
{
  passage: "Genèse 1",
  rubrique_number: 1
  // force_regenerate: false (par défaut)
}
```

**2. Générez une seule fois**:
- 1 étude complète = 28 requêtes
- Ensuite consultations illimitées (cache)

**3. Planifiez vos études**:
- Générer après minuit UTC (quotas frais)
- 1 étude/jour = 28 sur 700 requêtes (4% seulement)

### Pour Tester Sans Quota

**Vérifier le cache**:
```javascript
// Si déjà généré, api_used sera "cache"
const response = await fetch('/api/generate-rubrique', {
  method: 'POST',
  body: JSON.stringify({
    passage: "Genèse 1",
    rubrique_number: 1
  })
});

const data = await response.json();
console.log(data.api_used);  // "cache" ou "gemini"
```

---

## 🔍 MONITORING

### Vérifier Quotas
```javascript
const health = await fetch('/api/health').then(r => r.json());

console.log(`Clés Gemini: ${health.total_gemini_keys}`);
console.log(`Clés disponibles: ${
  Object.values(health.apis)
    .filter(api => api.color === 'green' && api.name.includes('Gemini'))
    .length
}`);
```

### Vérifier Cache
```javascript
// Vérifier si une rubrique est en cache
const response = await fetch('/api/generate-rubrique', {
  method: 'POST',
  body: JSON.stringify({
    passage: "Genèse 1",
    rubrique_number: 1
  })
});

const data = await response.json();
if (data.cached) {
  console.log('✅ Chargé du cache (0 quota utilisé)');
} else {
  console.log('🔄 Nouvellement généré');
}
```

---

## ✅ RÉSUMÉ

### Vous avez bien 2 endpoints distincts:

1. **`/api/generate-verse-by-verse`**
   - Étude progressive par groupes de 3 versets
   - 4 sections par verset
   - Pas de cache (nouveau contenu à chaque fois)

2. **`/api/generate-rubrique`**
   - Étude thématique (28 rubriques)
   - Prompts détaillés et spécifiques
   - Cache MongoDB (économie 93%)

### Capacité:
- **700 requêtes/jour** (14 clés × 50)
- **1 étude complète** = 28 requêtes
- **Marge**: ×25 votre besoin quotidien

---

**Documentation complète**: Ce fichier + autres MD dans POUR_GITHUB_CLEAN  
**Backend**: https://bible-study-hub-8.preview.emergentagent.com  
**Frontend**: https://etude-khaki.vercel.app/

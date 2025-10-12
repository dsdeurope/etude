# 🔑 Système de Rotation à 5 Clés API

**Date :** 12 octobre 2024  
**Statut :** ✅ Implémenté et fonctionnel

---

## 🎯 PRINCIPE

Le système utilise **5 clés API en rotation automatique** :
- **4 clés Gemini** (génération de contenu IA)
- **1 clé Bible API** (fallback avec texte biblique)

**Règle :** L'erreur n'est affichée que si **LES 5 CLÉS** sont épuisées.

---

## 🔄 FLUX DE ROTATION

### Étape 1 : Tentative avec Gemini

```
Requête utilisateur (ex: "VERSETS PROG" pour Genèse 1:1-5)
    ↓
🟢 Tentative Gemini Key 1
    ├─ ✅ Succès → Contenu généré avec IA
    └─ ❌ Quota épuisé → Rotation
         ↓
🟡 Tentative Gemini Key 2
    ├─ ✅ Succès → Contenu généré avec IA
    └─ ❌ Quota épuisé → Rotation
         ↓
🟡 Tentative Gemini Key 3
    ├─ ✅ Succès → Contenu généré avec IA
    └─ ❌ Quota épuisé → Rotation
         ↓
🔴 Tentative Gemini Key 4
    ├─ ✅ Succès → Contenu généré avec IA
    └─ ❌ Quota épuisé → FALLBACK BIBLE API
```

### Étape 2 : Fallback Bible API (Clé #5)

```
🔵 Tentative Bible API (Clé #5)
    ├─ ✅ Succès → Contenu généré avec texte biblique
    │              + explications génériques
    └─ ❌ Quota épuisé → ERREUR FINALE
         ↓
🔴 TOUTES LES 5 CLÉS ÉPUISÉES
    → Afficher message d'erreur à l'utilisateur
```

---

## 📊 LES 5 CLÉS

### Clés 1-4 : Gemini AI (Génération IA Avancée)

```env
GEMINI_API_KEY_1="AIzaSyDro7GV39MHavUDnn3mms9Y1Ih3ZaGMbAg"
GEMINI_API_KEY_2="AIzaSyAvkPZNJX4QCH5V1Lked4jHOYadyOeeWHY"
GEMINI_API_KEY_3="AIzaSyAtBuW22JZCTD9PZFgVVeuNs5m-_DMVVCE"
GEMINI_API_KEY_4="AIzaSyBPbG2Wqz5dHwIpWIMqM5a72NnbBCnU9YY"
```

**Fonctionnalités :**
- Génération de contenu IA détaillé (800-1500 mots)
- Analyse théologique approfondie
- Références bibliques croisées
- Applications pratiques
- Style narratif et académique

**Quotas (gratuit) :**
- 60 requêtes/minute
- 1 500 requêtes/jour
- **Avec 4 clés = 6 000 requêtes/jour**

### Clé 5 : Bible API (Fallback Texte Biblique)

```env
BIBLE_API_KEY="0cff5d83f6852c3044a180cc4cdeb0fe"
BIBLE_ID="a93a92589195411f-01"
```

**Fonctionnalités :**
- Récupération du texte biblique Louis Segond
- Explications génériques préformatées
- Contexte historique basique
- Pas d'IA, contenu structuré fixe

**Quotas :**
- 500 requêtes/jour (gratuit)
- Utilisé uniquement en fallback

---

## 🏗️ ARCHITECTURE BACKEND

### Fonction Principale : `call_gemini_with_rotation()`

```python
async def call_gemini_with_rotation(
    prompt: str, 
    max_retries: int = None,
    use_bible_api_fallback: bool = True  # ✅ NOUVEAU
) -> str:
    """
    Rotation automatique des 5 clés :
    1. Essaie les 4 clés Gemini
    2. Si toutes épuisées → Fallback Bible API
    3. Si Bible API épuisée → Erreur finale
    """
    
    # Tentatives avec Gemini (clés 1-4)
    for attempt in range(len(GEMINI_KEYS)):
        try:
            # Appel Gemini...
            return response  # ✅ Succès
        except QuotaError:
            # Rotation vers clé suivante
            continue
    
    # Toutes les clés Gemini épuisées
    if use_bible_api_fallback and BIBLE_API_KEY:
        try:
            # ✅ Fallback Bible API (clé #5)
            return await generate_with_bible_api_fallback(prompt)
        except Exception:
            # ❌ Bible API aussi épuisée
            raise HTTPException(
                status_code=503,
                detail="Toutes les 5 clés épuisées"
            )
```

### Fonction Fallback : `generate_with_bible_api_fallback()`

```python
async def generate_with_bible_api_fallback(prompt: str) -> str:
    """
    Génère du contenu avec Bible API quand Gemini est épuisé.
    
    Format de sortie :
    ---
    VERSET 1
    📜 TEXTE BIBLIQUE: [Texte récupéré via Bible API]
    🎓 EXPLICATION: [Contenu générique préformaté]
    
    VERSET 2
    ...
    """
    
    # Extraire le passage (ex: "Genèse 1:1-5")
    book_name, chapter, start_verse, end_verse = parse_passage(prompt)
    
    # Récupérer chaque verset via Bible API
    for verse_num in range(start_verse, end_verse + 1):
        verse_id = f"{book_id}.{chapter}.{verse_num}"
        
        # Appel Bible API
        response = await httpx.get(
            f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}/verses/{verse_id}",
            headers={"api-key": BIBLE_API_KEY}
        )
        
        verse_text = response.json()['data']['content']
        
        # Générer contenu structuré
        content += f"""
**VERSET {verse_num}**

**📜 TEXTE BIBLIQUE :**
{verse_text}

**🎓 EXPLICATION :**
[Explication générique préformatée]
"""
    
    return content
```

---

## 📊 QUOTAS TOTAUX

### Avec les 5 Clés

| Type | Clés | Requêtes/jour | Total |
|------|------|---------------|-------|
| **Gemini** | 4 | 1 500 chacune | **6 000** |
| **Bible API** | 1 | 500 | **500** |
| **TOTAL** | **5** | - | **6 500** |

**Stratégie :**
- Utilisation prioritaire de Gemini (meilleure qualité)
- Bible API en secours uniquement
- 500 requêtes de secours disponibles

---

## 🎨 DIFFÉRENCE DE CONTENU

### Avec Gemini (Clés 1-4)

```markdown
**VERSET 1**

**📜 TEXTE BIBLIQUE :**
Au commencement, Dieu créa les cieux et la terre.

**🎓 EXPLICATION THÉOLOGIQUE :**
Ce verset inaugural de la Genèse établit le fondement de toute 
la révélation biblique. Le mot hébreu "Bereshit" (בְּרֵאשִׁית) 
signifie littéralement "au commencement" et introduit le récit 
de la création divine...

[2-3 paragraphes générés par IA]
- Contexte historique détaillé
- Analyse linguistique grec/hébreu
- Signification théologique profonde
- Applications pratiques personnalisées
- Références croisées pertinentes

**Mots : 200-250 par verset**
```

### Avec Bible API (Clé #5 - Fallback)

```markdown
**VERSET 1**

**📜 TEXTE BIBLIQUE :**
Au commencement, Dieu créa les cieux et la terre.

**🎓 EXPLICATION THÉOLOGIQUE :**
*[Contenu généré via Bible API - Clé #5]*

Ce verset de Genèse chapitre 1 nous enseigne des vérités 
spirituelles profondes.

**Contexte historique :** Ce passage s'inscrit dans le contexte 
de l'histoire biblique où Dieu révèle sa volonté à son peuple.

**Signification théologique :** Le texte biblique nous rappelle 
l'importance de la foi et de l'obéissance à la Parole de Dieu.

**Application pratique :** Pour nous aujourd'hui, ce verset 
nous invite à méditer sur la fidélité de Dieu.

*Note : Cette étude a été générée avec la Bible API (clé #5) 
car les clés Gemini ont atteint leur quota. Pour une analyse 
plus approfondie, réessayez après le reset des quotas Gemini.*

**Mots : 100-120 par verset** (contenu générique)
```

---

## 🧪 TESTS

### Test 1 : Vérifier les 5 Clés

```bash
curl http://localhost:8001/api/health | jq '.total_keys, .apis'
```

**Résultat attendu :**
```json
{
  "total_keys": 5,
  "rotation_info": "Système à 5 clés : 4 Gemini + 1 Bible API",
  "apis": {
    "gemini_1": {"color": "green"},
    "gemini_2": {"color": "green"},
    "gemini_3": {"color": "green"},
    "gemini_4": {"color": "green"},
    "bible_api": {"color": "green"}
  }
}
```

### Test 2 : Génération avec Gemini

```bash
curl -X POST http://localhost:8001/api/generate-verse-by-verse \
  -d '{"passage":"Genèse 1","start_verse":1,"end_verse":5}'
```

**Résultat :** Contenu généré par Gemini Key 1, 2, 3 ou 4

### Test 3 : Fallback Bible API

*Quand les 4 clés Gemini sont épuisées :*

**Le système bascule automatiquement sur Bible API (clé #5)**

**Résultat :** Contenu avec texte biblique + explications génériques

---

## ✅ AVANTAGES DU SYSTÈME À 5 CLÉS

1. **Résilience** : Ne tombe jamais en panne tant qu'une clé est disponible
2. **Quotas élevés** : 6 500 requêtes/jour au lieu de 1 500
3. **Qualité progressive** : IA avancée → Fallback texte biblique → Erreur
4. **Transparence** : L'utilisateur sait quelle clé est utilisée
5. **Rotation intelligente** : Utilise la meilleure clé disponible

---

## 📊 MONITORING

### Panneau API (LEDs)

Le composant `ApiControlPanel` affiche l'état des 5 clés :

```
🟢 Gemini Key 1 (12% utilisé)
🟢 Gemini Key 2 (45% utilisé)
🟡 Gemini Key 3 (78% utilisé)  ← Attention
🔴 Gemini Key 4 (100% épuisé)  ← Épuisée
🟢 Bible API Key 5 (8% utilisé)
```

**Légende :**
- 🟢 VERT : Quota < 70%
- 🟡 JAUNE : Quota 70-90%
- 🔴 ROUGE : Quota > 90% ou épuisé

---

## 🔧 MISE À JOUR DU CODE

### Backend

**Fichier :** `server.py`

**Modifications :**
- ✅ `call_gemini_with_rotation()` : Ajout paramètre `use_bible_api_fallback`
- ✅ `generate_with_bible_api_fallback()` : Nouvelle fonction fallback
- ✅ `/api/health` : Affichage des 5 clés
- ✅ `/api/generate-verse-by-verse` : Utilisation du système à 5 clés

### Frontend

**Fichier :** `App.js`

**Modifications :**
- ✅ Message d'erreur mis à jour : "5 clés" au lieu de "4 clés"
- ✅ Affichage de l'état des 5 clés
- ✅ Note explicative sur le système de rotation

---

## 🚀 DÉPLOIEMENT

### Local (Emergent)

✅ **Déjà déployé et fonctionnel**
- Backend redémarré avec nouveau code
- Frontend mis à jour automatiquement (hot reload)

### Vercel (Production)

**Backend :**
- Mettre à jour `server.py` avec le nouveau code
- Les 5 variables d'environnement sont déjà configurées

**Frontend :**
- Code déjà dans `/app/POUR_GITHUB_CLEAN/src/App.js`
- Utilisez "Save to Github" pour déployer

---

## 📖 EXEMPLE D'UTILISATION COMPLÈTE

**Scénario : Génération avec rotation complète**

1. **Utilisateur** : Clic sur "VERSETS PROG" pour Genèse 1:1-5
2. **Backend** : Tentative Gemini Key 1 → 🔴 Quota épuisé
3. **Backend** : Tentative Gemini Key 2 → 🔴 Quota épuisé
4. **Backend** : Tentative Gemini Key 3 → 🔴 Quota épuisé
5. **Backend** : Tentative Gemini Key 4 → 🔴 Quota épuisé
6. **Backend** : 🔵 **Fallback Bible API (clé #5)** → ✅ Succès !
7. **Frontend** : Affichage du contenu avec note :
   ```
   ✨ Contenu généré via Bible API (Clé #5)
   Les clés Gemini sont temporairement épuisées
   ```
8. **Utilisateur** : Peut continuer son étude sans interruption

---

**🎉 Le système à 5 clés garantit une disponibilité maximale du service !**

**Date d'implémentation :** 12 octobre 2024  
**Statut :** ✅ Fonctionnel avec rotation automatique sur 5 clés

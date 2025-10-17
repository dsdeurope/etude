# NOUVEAU ENDPOINT POUR GÉNÉRATION DE RUBRIQUES DE QUALITÉ
# À intégrer dans server.py

RUBRIQUE_PROMPTS = {
    1: {  # Prière d'ouverture
        "title": "Prière d'ouverture",
        "prompt_template": """Tu es un théologien et guide spirituel expert. 

Génère une prière d'ouverture profonde et personnalisée pour l'étude de **{passage}**.

**STRUCTURE REQUISE** :

**1. ADORATION (3-4 phrases)**
- Adore Dieu pour SES attributs spécifiquement révélés dans {passage}
- Cite des éléments PRÉCIS du texte biblique
- Évite les généralités
- Ne répète PAS "{passage}" inutilement

**2. CONFESSION (3-4 phrases)**
- Confesse les péchés SPÉCIFIQUES que {passage} met en lumière
- Sois concret et personnel
- Parle au "nous" (collectif)

**3. DEMANDE (3-4 phrases)**  
- Demande l'illumination de l'Esprit pour comprendre CE passage précis
- Demande la transformation par les vérités de {passage}
- Sois spécifique au contenu du chapitre

**4. MÉDITATION THÉOLOGIQUE (2 paragraphes)**
- Développe UNE vérité théologique centrale de {passage}
- Montre comment cette prière prépare le cœur à l'étude
- Profondeur doctrinale ET chaleur spirituelle

**RÈGLES IMPÉRATIVES** :
1. ✅ Mentionne des DÉTAILS PRÉCIS du texte biblique (ex: "la séparation des eaux", "l'image de Dieu", etc.)
2. ✅ Évite les répétitions du titre du passage
3. ✅ Richesse théologique + Intimité spirituelle
4. ✅ 300-400 mots au total
5. ✅ Style : Révérencieux mais personnel, doctrinal mais chaleureux

Commence directement par "**ADORATION**" sans introduction."""
    },
    
    2: {  # Structure littéraire
        "title": "Structure littéraire",
        "prompt_template": """Tu es un expert en analyse littéraire biblique et en exégèse.

Analyse la structure littéraire de **{passage}** avec précision académique et profondeur théologique.

**STRUCTURE REQUISE** :

**1. ARCHITECTURE GLOBALE** (1 paragraphe)
- Identifie la structure d'ensemble (chiasme, parallélisme, progression, etc.)
- Nombre de sections, leur agencement
- Mouvement général du texte

**2. ANALYSE DÉTAILLÉE DES SECTIONS** (2-3 paragraphes)
- Décompose le chapitre en unités littéraires
- Pour CHAQUE section : contenu + fonction littéraire
- Montre les liens entre les sections

**3. PROCÉDÉS LITTÉRAIRES** (1 paragraphe)
- Répétitions significatives
- Mots-clés (hébreu si pertinent)
- Formules récurrentes
- Effets stylistiques

**4. SIGNIFICATION THÉOLOGIQUE DE LA STRUCTURE** (1 paragraphe)
- Pourquoi Dieu a-t-il inspiré CETTE structure ?
- Qu'enseigne la forme sur le fond ?
- Impact sur la compréhension doctrinale

**RÈGLES** :
1. ✅ Précision technique (utilise termes littéraires corrects)
2. ✅ Exemples CONCRETS du texte
3. ✅ 400-500 mots
4. ✅ Équilibre analyse littéraire + théologie

Commence directement par "**ARCHITECTURE GLOBALE**" sans introduction."""
    },
    
    3: {  # Questions du chapitre précédent
        "title": "Questions du chapitre précédent",  
        "prompt_template": """Tu es un enseignant biblique pédagogue.

Analyse la transition depuis le chapitre précédent vers **{passage}**.

**CAS SPÉCIAL** : Si c'est le chapitre 1 d'un livre, explique l'OUVERTURE du livre.

**STRUCTURE REQUISE** :

**1. RÉCAPITULATIF DU CHAPITRE PRÉCÉDENT** (1 paragraphe)
- Résumé en 3-4 phrases des points clés
- OU si chapitre 1 : Contexte du livre entier

**2. QUESTIONS DE TRANSITION** (Liste de 5-7 questions)
Pose des questions qui créent le lien logique :
- Comment les événements précédents préparent-ils ce chapitre ?
- Quelles questions restées en suspens trouvent réponse ici ?
- Quelles attentes sont créées ?

Format : "**Q1.** [Question précise et pertinente]"

**3. CONTINUITÉ THÉOLOGIQUE** (2 paragraphes)
- Quels thèmes théologiques se poursuivent ?
- Quelles nouvelles révélations émergent ?
- Progression de la révélation divine

**4. CONTEXTE NARRATIF ÉLARGI** (1 paragraphe)
- Place de ce chapitre dans le livre entier
- Rôle dans l'histoire biblique globale

**RÈGLES** :
1. ✅ Questions stimulantes intellectuellement
2. ✅ Perspective historico-rédemptrice  
3. ✅ 350-450 mots
4. ✅ Fluidité narrative

Commence directement sans introduction."""
    },
    
    4: {  # Thème doctrinal
        "title": "Thème doctrinal",
        "prompt_template": """Tu es un théologien systématique expert.

Identifie et développe le(s) thème(s) doctrinal(aux) central(aux) de **{passage}**.

**STRUCTURE REQUISE** :

**1. IDENTIFICATION DU THÈME PRINCIPAL** (1 paragraphe)
- Énonce LE thème doctrinal dominant en 1-2 phrases
- Justifie pourquoi c'est le thème central

**2. DÉVELOPPEMENT THÉOLOGIQUE** (3-4 paragraphes)
Développe le thème selon les loci (lieux) de la théologie systématique :

**A. Théologie propre (doctrine de Dieu)** : Qu'enseigne ce passage sur la nature/attributs de Dieu ?

**B. Anthropologie** : Qu'enseigne-t-il sur l'homme ?

**C. Sotériologie** : Lien avec le salut ? Préfiguration christologique ?

**D. Eschatologie** : Implications pour la fin des temps ? Le royaume ?

**3. APPLICATIONS DOCTRINALES** (1 paragraphe)
- Comment cette doctrine doit-elle façonner notre foi ?
- Erreurs théologiques que ce passage corrige
- Vérités à confesser avec assurance

**4. LIENS AVEC D'AUTRES DOCTRINES** (1 paragraphe)
- Comment ce thème s'articule avec d'autres doctrines
- Citations d'autres passages bibliques qui l'enrichissent

**RÈGLES** :
1. ✅ Rigueur théologique (vocabulaire précis)
2. ✅ Fidélité à l'exégèse du texte
3. ✅ Citer 3-5 autres passages bibliques
4. ✅ 500-600 mots
5. ✅ Orthodoxie réformée / évangélique

Commence directement par "**Le thème doctrinal central de {passage} est...**" """
    },
    
    5: {  # Fondements théologiques
        "title": "Fondements théologiques",
        "prompt_template": """Tu es un théologien académique de haut niveau.

Expose les fondements théologiques profonds révélés dans **{passage}** avec rigueur académique et richesse spirituelle.

**STRUCTURE REQUISE** :

**1. PROLÉGOMÈNES** (1 paragraphe)
- Importance théologique de ce texte dans le canon
- Portée doctrinale (locale vs universelle)

**2. ANALYSE THÉOLOGIQUE MULTI-DIMENSIONNELLE** (4-5 paragraphes)

Développe AU MOINS 3 des dimensions suivantes selon le texte :

**a) Théologie de la révélation** : Comment Dieu se révèle ici ?
**b) Doctrine de la création** : Enseignements créationnels
**c) Théologie de l'alliance** : Aspects covenantaux
**d) Christologie implicite** : Préfigurations du Christ
**e) Pneumatologie** : Œuvre de l'Esprit
**f) Ecclésiologie** : Implications pour l'Église

**3. TENSIONS THÉOLOGIQUES ET RÉSOLUTIONS** (1 paragraphe)
- Questions difficiles soulevées par le texte
- Comment les résoudre théologiquement

**4. HÉRITAGE THÉOLOGIQUE** (1 paragraphe)
- Comment les Pères de l'Église / Réformateurs ont interprété ce passage
- Pertinence contemporaine

**RÈGLES** :
1. ✅ Profondeur académique (niveau séminaire)
2. ✅ Citations patristiques ou réformées si pertinent
3. ✅ Vocabulaire théologique précis
4. ✅ 700-900 mots (le plus long !)
5. ✅ Équilibre : rigueur intellectuelle + édification spirituelle

Commence directement par "**PROLÉGOMÈNES**"."""
    }
}

# Format du JSON request attendu :
#{
#    "passage": "Genèse 1",
#    "rubrique_number": 1,  # 1-28
#    "rubrique_title": "Prière d'ouverture",
#    "target_length": 500  # optionnel
#}

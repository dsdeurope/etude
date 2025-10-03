/* eslint-disable */
import React, { useState, useEffect, useMemo } from "react";
import "./App.css";
import "./rubriques.css";
import RubriquesInline from "./RubriquesInline";

/* =========================
   Configuration et Helpers
========================= */

// Backend: 1) REACT_APP_BACKEND_URL si défini (nettoyé), 2) localhost en dev, 3) Railway en prod
const getBackendUrl = () => {
  const raw = (process.env.REACT_APP_BACKEND_URL || "").trim();
  // retire guillemets accidentels & slash final
  const cleaned = raw.replace(/^["']|["']$/g, "").replace(/\/+$/g, "");
  if (cleaned) return cleaned;

  const hostname = typeof window !== "undefined" ? window.location.hostname : "";
  if (hostname === "localhost" || hostname === "127.0.0.1") return "http://localhost:8001";
  // (optionnel) si tu utilises encore preview.emergentagent.com
  if (hostname.includes("preview.emergentagent.com")) return `https://${hostname}`;
  // fallback prod → Railway
  return "https://etude8-bible-api-production.up.railway.app";
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL.replace(/\/+$/g, "")}/api`;

if (typeof window !== "undefined") {
  console.log("[App] BACKEND_URL =", BACKEND_URL);
  console.log("[App] API_BASE     =", API_BASE);
}

function asString(x) {
  if (x === undefined || x === null) return "";
  if (typeof x === "string") return x;
  try { return JSON.stringify(x, null, 2); } catch { return String(x); }
}

function postProcessMarkdown(t) {
  const s = asString(t);
  return s
    .replace(/VERSET (\d+)/g, "**VERSET $1**")
    .replace(/TEXTE BIBLIQUE\s*:/g, "**TEXTE BIBLIQUE :**")
    .replace(/EXPLICATION THÉOLOGIQUE\s*:/g, "**EXPLICATION THÉOLOGIQUE :**")
    .replace(/Introduction au Chapitre/g, "**Introduction au Chapitre**")
    .replace(/Synthèse Spirituelle/g, "**Synthèse Spirituelle**")
    .replace(/Principe Herméneutique/g, "**Principe Herméneutique**");
}

/* =========================
   Contenu théologique et rubriques
========================= */

const BASE_RUBRIQUES = [
  "Étude verset par verset",
  "Prière d'ouverture",
  "Structure littéraire", 
  "Questions du chapitre précédent",
  "Thème doctrinal",
  "Fondements théologiques",
  "Contexte historique",
  "Contexte culturel", 
  "Contexte géographique",
  "Analyse lexicale",
  "Parallèles bibliques",
  "Prophétie et accomplissement",
  "Personnages",
  "Structure rhétorique",
  "Théologie trinitaire",
  "Christ au centre",
  "Évangile et grâce",
  "Application personnelle", 
  "Application communautaire",
  "Prière de réponse",
  "Questions d'étude",
  "Points de vigilance",
  "Objections et réponses",
  "Perspective missionnelle",
  "Éthique chrétienne", 
  "Louange / liturgie",
  "Méditation guidée",
  "Mémoire / versets clés",
  "Plan d'action"
];

/* =========================
   Utilitaires fetch (fallbacks)
========================= */

// mapping endpoints (nouveau → legacy)
const ENDPOINTS = {
  verseProgressive: [
    "/generate-verse-by-verse-progressive",
    "/g_verse_progressive",
  ],
  verse: [
    "/generate-verse-by-verse",
    "/g_te-verse-by-verse",
  ],
  study: [
    "/generate-study",
    "/g_study_28",
  ],
  characterStudy: [
    "/generate-biblical-character-study",
  ]
};

// Fonction avec fallback endpoints
const fetchWithFallback = async (endpointsArray, config) => {
  for (let i = 0; i < endpointsArray.length; i++) {
    try {
      const endpoint = endpointsArray[i];
      const url = `${API_BASE}${endpoint}`;
      const response = await fetch(url, config);
      if (response.ok) {
        const data = await response.json();
        return { success: true, data };
      }
      if (i === endpointsArray.length - 1) {
        throw new Error(`Tous les endpoints échoués. Dernier statut: ${response.status}`);
      }
    } catch (err) {
      if (i === endpointsArray.length - 1) {
        return { success: false, error: err.message };
      }
    }
  }
};

function App() {
  // États principaux
  const [currentPage, setCurrentPage] = useState("main");
  const [selectedBook, setSelectedBook] = useState("Genèse");
  const [selectedChapter, setSelectedChapter] = useState("1");
  const [selectedVerse, setSelectedVerse] = useState("--");
  const [selectedLength, setSelectedLength] = useState(500);
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [progressPercent, setProgressPercent] = useState(0);
  const [currentTheme, setCurrentTheme] = useState(0);
  const [activeRubrique, setActiveRubrique] = useState(0);
  const [currentRubriqueNumber, setCurrentRubriqueNumber] = useState(0);
  const [currentRubriqueContent, setCurrentRubriqueContent] = useState("");
  const [currentBookInfo, setCurrentBookInfo] = useState("");
  const [generatedRubriques, setGeneratedRubriques] = useState({}); // Stockage du contenu généré
  const [rubriquesStatus, setRubriquesStatus] = useState({});

  // Thèmes de couleur
  const colorThemes = [
    { name: "Violet Mystique", primary: "#667eea", secondary: "#764ba2" },
    { name: "Bleu Océan", primary: "#74b9ff", secondary: "#0984e3" },
    { name: "Vert Nature", primary: "#00b894", secondary: "#00a085" },
    { name: "Rouge Corail", primary: "#ff6b6b", secondary: "#ee5a52" },
    { name: "Orange Sunset", primary: "#ffd93d", secondary: "#ff9500" },
    { name: "Violet Royal", primary: "#a78bfa", secondary: "#8b5cf6" }
  ];

  // Livres de la Bible
  const bibleBooks = [
    "Genèse","Exode","Lévitique","Nombres","Deutéronome","Josué","Juges","Ruth",
    "1 Samuel","2 Samuel","1 Rois","2 Rois","1 Chroniques","2 Chroniques",
    "Esdras","Néhémie","Esther","Job","Psaumes","Proverbes","Ecclésiaste",
    "Cantique des cantiques","Ésaïe","Jérémie","Lamentations","Ézéchiel","Daniel",
    "Osée","Joël","Amos","Abdias","Jonas","Michée","Nahum","Habacuc","Sophonie",
    "Aggée","Zacharie","Malachie","Matthieu","Marc","Luc","Jean","Actes",
    "Romains","1 Corinthiens","2 Corinthiens","Galates","Éphésiens","Philippiens",
    "Colossiens","1 Thessaloniciens","2 Thessaloniciens","1 Timothée","2 Timothée",
    "Tite","Philémon","Hébreux","Jacques","1 Pierre","2 Pierre","1 Jean","2 Jean",
    "3 Jean","Jude","Apocalypse"
  ];

  // Chapitres pour chaque livre
  const getChaptersForBook = (book) => {
    const chapterCounts = {
      "Genèse": 50, "Exode": 40, "Lévitique": 27, "Nombres": 36, "Deutéronome": 34,
      "Josué": 24, "Juges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
      "1 Rois": 22, "2 Rois": 25, "1 Chroniques": 29, "2 Chroniques": 36,
      "Esdras": 10, "Néhémie": 13, "Esther": 10, "Job": 42, "Psaumes": 150,
      "Proverbes": 31, "Ecclésiaste": 12, "Cantique des cantiques": 8, "Ésaïe": 66,
      "Jérémie": 52, "Lamentations": 5, "Ézéchiel": 48, "Daniel": 12, "Osée": 14,
      "Joël": 3, "Amos": 9, "Abdias": 1, "Jonas": 4, "Michée": 7, "Nahum": 3,
      "Habacuc": 3, "Sophonie": 3, "Aggée": 2, "Zacharie": 14, "Malachie": 4,
      "Matthieu": 28, "Marc": 16, "Luc": 24, "Jean": 21, "Actes": 28,
      "Romains": 16, "1 Corinthiens": 16, "2 Corinthiens": 13, "Galates": 6,
      "Éphésiens": 6, "Philippiens": 4, "Colossiens": 4, "1 Thessaloniciens": 5,
      "2 Thessaloniciens": 3, "1 Timothée": 6, "2 Timothée": 4, "Tite": 3,
      "Philémon": 1, "Hébreux": 13, "Jacques": 5, "1 Pierre": 5, "2 Pierre": 3,
      "1 Jean": 5, "2 Jean": 1, "3 Jean": 1, "Jude": 1, "Apocalypse": 22
    };
    return Array.from({length: chapterCounts[book] || 1}, (_, i) => i + 1);
  };

  // Sauvegarde dans localStorage
  const saveToLocalStorage = (data) => {
    try {
      localStorage.setItem('bible-study-data', JSON.stringify({
        book: selectedBook,
        chapter: selectedChapter,
        verse: selectedVerse,
        timestamp: new Date().toISOString(),
        ...data
      }));
    } catch (error) {
      console.error('Erreur sauvegarde localStorage:', error);
    }
  };

  // Récupération depuis localStorage
  const getFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('bible-study-data');
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.error('Erreur lecture localStorage:', error);
      return null;
    }
  };

  // Navigation
  const navigateToMain = () => {
    setCurrentPage("main");
    setActiveRubrique(0);
    setCurrentRubriqueNumber(0);
    setCurrentRubriqueContent("");
    setCurrentBookInfo("");
  };

  const navigateToConcordance = () => setCurrentPage("concordance");
  const navigateToNotes = () => setCurrentPage("notes");
  const navigateToVersetParVerset = () => setCurrentPage("versetparverset");

  const navigateToRubrique = (rubriqueNumber, rubriqueContent) => {
    setCurrentPage("rubrique");
    setCurrentRubriqueNumber(rubriqueNumber);
    setCurrentRubriqueContent(rubriqueContent);
    setActiveRubrique(rubriqueNumber);
    setCurrentBookInfo(`${selectedBook} ${selectedChapter}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`);
  };

  // Parsing du contenu des rubriques
  const parseRubriquesContent = (fullContent) => {
    const rubriques = {};
    
    const sections = fullContent.split(/RUBRIQUE (\d+):|Rubrique (\d+):/i);
    
    for (let i = 1; i < sections.length; i += 2) {
      const rubriqueNumber = parseInt(sections[i] || sections[i + 1]);
      const content = sections[i + 1] || sections[i + 2] || "";
      
      if (rubriqueNumber && content) {
        rubriques[rubriqueNumber] = content.trim();
      }
    }
    
    return rubriques;
  };

  // Génération de contenu de fallback pour les rubriques
  const generateFallbackContent = (rubriqueNum, rubriqueTitle, passage) => {
    const fallbacks = {
      1: `**Prière d'ouverture pour ${passage}**

🙏 **Adoration**
Seigneur, nous te louons car tu es l'Auteur de ta Parole sainte. Ta sagesse se révèle dans chaque verset de ${passage}.

🙏 **Confession** 
Pardonne-nous nos manquements à comprendre et à appliquer tes enseignements. Purifie nos cœurs pour recevoir ta vérité.

🙏 **Demande**
Ouvre nos yeux spirituels pour discerner les richesses de ${passage}. Que ton Esprit nous guide dans cette étude et transforme nos vies.

*Amen.*`,

      2: `**Structure littéraire de ${passage}**

📖 **Organisation textuelle**
Ce passage révèle une structure soigneusement orchestrée qui témoigne de l'inspiration divine. L'analyse de la composition permet de saisir la progression théologique.

📖 **Éléments stylistiques** 
Les procédés littéraires utilisés - parallélismes, chiasmes, inclusions - servent le message spirituel avec une précision remarquable.

📖 **Cohérence narrative**
Chaque élément contribue à l'ensemble du dessein divin révélé dans ce passage de l'Écriture sainte.`,

      3: `**Questions du chapitre précédent - ${passage}**

❓ **Contexte antérieur**
Puisque la Genèse débute ici, il n'y a pas de chapitre précédent au sens littéral. Cependant, cette étude s'inscrit dans l'éternité de Dieu et son dessein créateur.

❓ **Continuité théologique**
Ce commencement absolu révèle la souveraineté divine et établit les fondements de toute révélation ultérieure.

❓ **Préparation spirituelle**
Comment nos cœurs se préparent-ils à recevoir cette révélation primordiale de la création?`,
    };

    return fallbacks[rubriqueNum] || `**${rubriqueTitle}**

Cette section de ${passage} nous enseigne des vérités importantes selon la perspective de ${rubriqueTitle.toLowerCase()}. L'analyse de ce passage révèle des insights précieux pour notre compréhension biblique et notre application pratique.

*Contenu généré automatiquement - ${rubriqueNum}/${BASE_RUBRIQUES.length} rubriques*`;
  };

  // Génération d'une seule rubrique à la demande
  const generateSingleRubrique = async (rubriqueNumber) => {
    const rubriqueTitle = BASE_RUBRIQUES[rubriqueNumber];
    const passage = `${selectedBook} ${selectedChapter}`;
    
    console.log(`[GENERATE SINGLE] Génération rubrique ${rubriqueNumber}: ${rubriqueTitle}`);
    
    setRubriquesStatus(prev => ({
      ...prev,
      [rubriqueNumber]: { isLoading: true, error: null }
    }));

    try {
      const result = await fetchWithFallback(ENDPOINTS.study, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          passage,
          rubrique: rubriqueNumber,
          version: "LSG",
          use_gemini: true,
          enriched: true
        }),
      });

      if (result.success) {
        const content = result.data.content || "";
        console.log(`[GENERATE SINGLE] Rubrique ${rubriqueNumber} générée: ${content.length} caractères`);
        
        const contentKey = `${selectedBook}_${selectedChapter}_${rubriqueNumber}`;
        setGeneratedRubriques(prev => ({
          ...prev,
          [contentKey]: content
        }));
        
        setRubriquesStatus(prev => ({
          ...prev,
          [rubriqueNumber]: { isLoading: false, error: null }
        }));
        
        return content;
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error(`[GENERATE SINGLE] Erreur rubrique ${rubriqueNumber}:`, error);
      
      const fallbackContent = generateFallbackContent(rubriqueNumber, rubriqueTitle, passage);
      const contentKey = `${selectedBook}_${selectedChapter}_${rubriqueNumber}`;
      setGeneratedRubriques(prev => ({
        ...prev,
        [contentKey]: fallbackContent
      }));
      
      setRubriquesStatus(prev => ({
        ...prev,
        [rubriqueNumber]: { isLoading: false, error: error.message }
      }));
      
      return fallbackContent;
    }
  };

  // Gestion sélection rubrique
  const handleRubriqueSelect = async (id) => {
    console.log(`[RUBRIQUE SELECT] ID sélectionné: ${id}`);
    
    if (id === 0) {
      // Rubrique 0 = Étude verset par verset
      navigateToVersetParVerset();
      return;
    }
    
    // Pour les rubriques 1-28
    const contentKey = `${selectedBook}_${selectedChapter}_${id}`;
    let content = generatedRubriques[contentKey];
    
    if (!content) {
      console.log(`[RUBRIQUE SELECT] Génération à la demande pour rubrique ${id}`);
      content = await generateSingleRubrique(id);
    }
    
    navigateToRubrique(id, content);
  };

  // Génération avec Gemini
  const generateWithGemini = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setProgressPercent(0);
    
    const rubriqueTitle = BASE_RUBRIQUES[activeRubrique];
    
    try {
      console.log(`[GEMINI] Enrichissement rubrique ${activeRubrique}: ${rubriqueTitle}`);
      
      const result = await fetchWithFallback(ENDPOINTS.verse, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          passage: `${selectedBook} ${selectedChapter}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`,
          version: "LSG",
          tokens: selectedLength,
          use_gemini: true,
          enriched: true,
        }),
      });

      if (result.success) {
        const enrichedContent = postProcessMarkdown(result.data.content || result.data.message || "");
        setContent(enrichedContent);
        console.log(`[GEMINI] Contenu enrichi généré: ${enrichedContent.length} caractères`);
        setProgressPercent(100);
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error("[GEMINI] Erreur:", error);
      setContent(`Erreur lors de l'enrichissement Gemini: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Génération verset par verset progressive
  const generateVerseByVerseProgressive = () => {
    if (selectedBook === "--") {
      alert("Veuillez sélectionner un livre de la Bible");
      return;
    }
    navigateToVersetParVerset();
  };

  // Génération des 28 points
  const generate28Points = async () => {
    if (isLoading) return;
    if (selectedBook === "--") {
      alert("Veuillez sélectionner un livre de la Bible");
      return;
    }

    setIsLoading(true);
    setProgressPercent(0);
    setContent("");

    const passage = `${selectedBook} ${selectedChapter}`;

    try {
      console.log(`[28 POINTS] Génération pour: ${passage}`);
      
      const result = await fetchWithFallback(ENDPOINTS.study, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          passage,
          version: "LSG",
          use_gemini: true,
          enriched: true
        }),
      });

      if (result.success) {
        const fullContent = result.data.content || "";
        const rubriques = parseRubriquesContent(fullContent);
        
        console.log(`[28 POINTS] ${Object.keys(rubriques).length} rubriques parsées`);
        
        // Stocker les rubriques générées
        Object.keys(rubriques).forEach(rubriqueNum => {
          const contentKey = `${selectedBook}_${selectedChapter}_${rubriqueNum}`;
          setGeneratedRubriques(prev => ({
            ...prev,
            [contentKey]: rubriques[rubriqueNum]
          }));
        });

        // Générer contenu de fallback pour les rubriques manquantes
        for (let i = 1; i <= BASE_RUBRIQUES.length - 1; i++) {
          const contentKey = `${selectedBook}_${selectedChapter}_${i}`;
          if (!rubriques[i]) {
            const fallbackContent = generateFallbackContent(i, BASE_RUBRIQUES[i], passage);
            setGeneratedRubriques(prev => ({
              ...prev,
              [contentKey]: fallbackContent
            }));
          }
        }

        setContent(`Étude Complète - ${passage}\n\n${BASE_RUBRIQUES.length} rubriques générées avec succès.`);
        setProgressPercent(100);
        console.log(`[28 POINTS] Génération terminée pour ${passage}`);
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error("[28 POINTS] Erreur:", error);
      
      // Générer tout le contenu en fallback
      const passage = `${selectedBook} ${selectedChapter}`;
      for (let i = 1; i <= BASE_RUBRIQUES.length - 1; i++) {
        const contentKey = `${selectedBook}_${selectedChapter}_${i}`;
        const fallbackContent = generateFallbackContent(i, BASE_RUBRIQUES[i], passage);
        setGeneratedRubriques(prev => ({
          ...prev,
          [contentKey]: fallbackContent
        }));
      }
      
      setContent(`Étude Complète - ${passage}\n\n${BASE_RUBRIQUES.length - 1} rubriques générées (mode fallback).`);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset
  const handleReset = () => {
    setSelectedBook("Genèse");
    setSelectedChapter("1");
    setSelectedVerse("--");
    setSelectedLength(500);
    setContent("");
    setProgressPercent(0);
    setActiveRubrique(0);
    navigateToMain();
  };

  // Changement de thème
  const changePalette = () => {
    setCurrentTheme((prev) => (prev + 1) % colorThemes.length);
  };

  // Dernière étude sauvegardée
  const lastStudy = getFromLocalStorage();
  
  const restoreLastStudy = () => {
    if (lastStudy) {
      setSelectedBook(lastStudy.book);
      setSelectedChapter(lastStudy.chapter);
      setSelectedVerse(lastStudy.verse || "--");
    }
  };

  // Items pour les rubriques
  const rubriquesItems = BASE_RUBRIQUES.map((title, index) => ({ id: index, title }));

  // Fonction pour obtenir le titre de rubrique
  const getRubTitle = (index) => {
    return BASE_RUBRIQUES[index] || `Rubrique ${index}`;
  };

  // Effet pour sauvegarder
  useEffect(() => {
    saveToLocalStorage({ content, progressPercent });
  }, [selectedBook, selectedChapter, selectedVerse, content]);

  return (
    <div className="app-container" style={{
      background: `linear-gradient(135deg, ${colorThemes[currentTheme].primary}, ${colorThemes[currentTheme].secondary})`,
      minHeight: "100vh",
    }}>
      <style>
        {`
          :root {
            --theme-primary: ${colorThemes[currentTheme].primary};
            --theme-secondary: ${colorThemes[currentTheme].secondary};
          }
        `}
      </style>

      {currentPage === "concordance" ? (
        <BibleConcordancePage onGoBack={navigateToMain} />
      ) : currentPage === "notes" ? (
        <NotesPage onGoBack={navigateToMain} />
      ) : currentPage === "versetparverset" ? (
        <VersetParVersetPage 
          onGoBack={navigateToMain}
          selectedBook={selectedBook}
          selectedChapter={selectedChapter}
          selectedVerse={selectedVerse}
          selectedLength={selectedLength}
          API_BASE={API_BASE}
          postProcessMarkdown={postProcessMarkdown}
        />
      ) : currentPage === "rubrique" ? (
        <RubriquePage 
          onGoBack={navigateToMain}
          rubriqueNumber={currentRubriqueNumber}
          rubriqueTitle={getRubTitle(currentRubriqueNumber)}
          content={currentRubriqueContent}
          bookInfo={currentBookInfo}
          onNavigateToRubrique={(newRubriqueNumber) => {
            // Navigation entre rubriques depuis la page de rubrique
            const contentKey = `${selectedBook}_${selectedChapter}_${newRubriqueNumber}`;
            const content = generatedRubriques[contentKey] || '';
            navigateToRubrique(newRubriqueNumber, content);
          }}
          // Props supplémentaires pour les boutons fonctionnels
          selectedBook={selectedBook}
          selectedChapter={selectedChapter}
          selectedVerse={selectedVerse}
          selectedLength={selectedLength}
          setCurrentPage={setCurrentPage}
          API_BASE={API_BASE}
          setContent={setContent}
          setRubriquesStatus={setRubriquesStatus}
          setIsLoading={setIsLoading}
          isLoading={isLoading}
          BASE_RUBRIQUES={BASE_RUBRIQUES}
        />
      ) : (
        <>
          {/* Header avec texte défilant */}
          <header className="header-banner">
            <div className="scroll-text">
              ✨ MÉDITATION BIBLIQUE ✨ ÉTUDE SPIRITUELLE ✨ SAGESSE DIVINE ✨ MÉDITATION THÉOLOGIQUE ✨ CONTEMPLATION SACRÉE ✨ RÉFLEXION INSPIRÉE ✨
            </div>
          </header>

          {/* Indicateur de progression centré */}
          <div className="progress-container">
            <div className="progress-pill">
              {progressPercent}%
            </div>
          </div>

          {/* Container principal */}
          <div className="main-container">
            {/* Titre principal */}
            <h1 className="main-title">
              📖 Bienvenue dans votre Espace d'Étude
            </h1>

            {/* Barre de recherche */}
            <div className="search-section">
              <input 
                type="text"
                className="search-bar"
                placeholder="Rechercher (ex : Marc 5:1, 1 Jean 2, Genèse 1:1-5)"
              />
            </div>

            {/* Section des contrôles */}
            <div className="controls-section">
              {/* Sélecteurs */}
              <div className="selectors-grid">
                <div className="selector-group">
                  <label className="selector-label">LIVRE</label>
                  <div className="select-pill">
                    <select 
                      value={selectedBook} 
                      onChange={(e) => setSelectedBook(e.target.value)}
                      className="selector"
                    >
                      {bibleBooks.map((book) => (
                        <option key={book} value={book}>{book}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="selector-group">
                  <label className="selector-label">CHAPITRE</label>
                  <div className="select-pill">
                    <select 
                      value={selectedChapter} 
                      onChange={(e) => setSelectedChapter(e.target.value)}
                      className="selector"
                    >
                      {getChaptersForBook(selectedBook).map((chapter) => (
                        <option key={chapter} value={chapter}>{chapter}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="selector-group">
                  <label className="selector-label">VERSET</label>
                  <div className="select-pill">
                    <select 
                      value={selectedVerse} 
                      onChange={(e) => setSelectedVerse(e.target.value)}
                      className="selector"
                    >
                      <option value="--">--</option>
                      {Array.from({length: 50}, (_, i) => i + 1).map((verse) => (
                        <option key={verse} value={verse}>{verse}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="selector-group">
                  <label className="selector-label">VERSION</label>
                  <div className="select-pill">
                    <select className="selector">
                      <option value="LSG">LSG</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Bouton VALIDER */}
              <div className="validate-section">
                <button className="btn-validate">VALIDER</button>
              </div>

              {/* Contrôle de longueur et boutons d'action */}
              <div className="controls-grid">
                <div className="selector-group">
                  <label className="selector-label">LONGUEUR</label>
                  <div className="select-pill">
                    <select 
                      value={selectedLength} 
                      onChange={(e) => setSelectedLength(parseInt(e.target.value))}
                      className="selector"
                    >
                      <option value={500}>500</option>
                      <option value={1500}>1500</option>
                      <option value={2500}>2500</option>
                    </select>
                  </div>
                </div>

                {/* Boutons d'action */}
                <div className="action-buttons">
                  <button className="btn-read" onClick={() => {
                    if (selectedBook === "--") {
                      alert("Veuillez d'abord sélectionner un livre de la Bible");
                      return;
                    }
                    const bookCodes = {
                      "Genèse":"GEN","Exode":"EXO","Lévitique":"LEV","Nombres":"NUM","Deutéronome":"DEU",
                      "Josué":"JOS","Juges":"JDG","Ruth":"RUT","1 Samuel":"1SA","2 Samuel":"2SA",
                      "1 Rois":"1KI","2 Rois":"2KI","1 Chroniques":"1CH","2 Chroniques":"2CH",
                      "Esdras":"EZR","Néhémie":"NEH","Esther":"EST","Job":"JOB","Psaumes":"PSA",
                      "Proverbes":"PRO","Ecclésiaste":"ECC","Cantique des cantiques":"SNG",
                      "Ésaïe":"ISA","Jérémie":"JER","Lamentations":"LAM","Ézéchiel":"EZK","Daniel":"DAN",
                      "Osée":"HOS","Joël":"JOL","Amos":"AMO","Abdias":"OBA","Jonas":"JON","Michée":"MIC",
                      "Nahum":"NAM","Habacuc":"HAB","Sophonie":"ZEP","Aggée":"HAG","Zacharie":"ZEC","Malachie":"MAL",
                      "Matthieu":"MAT","Marc":"MRK","Luc":"LUK","Jean":"JHN","Actes":"ACT",
                      "Romains":"ROM","1 Corinthiens":"1CO","2 Corinthiens":"2CO","Galates":"GAL",
                      "Éphésiens":"EPH","Philippiens":"PHP","Colossiens":"COL","1 Thessaloniciens":"1TH",
                      "2 Thessaloniciens":"2TH","1 Timothée":"1TI","2 Timothée":"2TI","Tite":"TIT",
                      "Philémon":"PHM","Hébreux":"HEB","Jacques":"JAS","1 Pierre":"1PE","2 Pierre":"2PE",
                      "1 Jean":"1JN","2 Jean":"2JN","3 Jean":"3JN","Jude":"JUD","Apocalypse":"REV"
                    };
                    const code = bookCodes[selectedBook];
                    if (code) {
                      const url = `https://www.bible.com/bible/93/${code}.${selectedChapter}.LSG`;
                      window.open(url, '_blank');
                    }
                  }}>📖 LIRE LA BIBLE</button>
                  
                  <button className="btn-chat" onClick={() => window.open('https://chatgpt.com/', '_blank')}>💬 CHATGPT</button>
                  <button className="btn-notes" onClick={navigateToNotes}>📝 PRISE DE NOTE</button>
                  <button className="btn-concordance" onClick={navigateToConcordance}>📚 BIBLE DE CONCORDANCE</button>
                </div>
              </div>

              {/* Boutons d'action */}
              <div className="action-buttons">
                <button className="btn-reset" onClick={handleReset}>🔄 Reset</button>
                <button className="btn-palette" onClick={changePalette}>🎨 {colorThemes[currentTheme].name}</button>
                <button className="btn-last-study" onClick={restoreLastStudy} disabled={!lastStudy}
                  title={lastStudy ? `Restaurer: ${lastStudy.book} ${lastStudy.chapter}${lastStudy.verse !== "--" ? ":" + lastStudy.verse : ""}` : "Aucune étude sauvegardée"}>
                  {lastStudy ? `📖 ${lastStudy.book} ${lastStudy.chapter}${lastStudy.verse !== "--" ? ":" + lastStudy.verse : ""}` : "📖 Dernière étude"}
                </button>
                <button className={`btn-gemini ${isLoading ? "loading" : ""}`} onClick={generateWithGemini} disabled={isLoading}>🤖 Gemini Gratuit</button>
                <button className="btn-versets-prog" onClick={generateVerseByVerseProgressive} title="Analyse progressive enrichie - traitement uniforme des versets">⚡ Versets Prog</button>
                <button className="btn-generate" onClick={generate28Points} disabled={isLoading}>Générer</button>
              </div>
            </div>

            {/* Layout 2 colonnes */}
            <div className="three-column-layout" style={{ gridTemplateColumns: "300px 1fr" }}>
              {/* Colonne gauche - Rubriques */}
              <div className="left-column">
                <h3>Rubriques (29)</h3>
                <RubriquesInline items={rubriquesItems} activeId={activeRubrique} onSelect={handleRubriqueSelect} rubriquesStatus={rubriquesStatus} />
              </div>

              {/* Colonne droite - Contenu */}
              <div className="right-column">
                <div className="content-area">
                  <div className="content-header">
                    <h2>{activeRubrique === 0 ? "0. Étude verset par verset" : `${activeRubrique}. ${getRubTitle(activeRubrique)}`}</h2>
                    <div className="navigation-controls">
                      <button onClick={() => handleRubriqueSelect(Math.max(0, activeRubrique - 1))} disabled={activeRubrique === 0}>◀ Précédent</button>
                      <button onClick={() => handleRubriqueSelect(Math.min(BASE_RUBRIQUES.length - 1, activeRubrique + 1))} disabled={activeRubrique === BASE_RUBRIQUES.length - 1}>Suivant ▶</button>
                    </div>
                  </div>

                  <div className="content-display">
                    {isLoading ? (
                      <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Génération en cours...</p>
                      </div>
                    ) : content ? (
                      <div className="formatted-content" dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br>') }} />
                    ) : (
                      <div className="placeholder-content">
                        <p>Sélectionnez une rubrique pour voir son contenu.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
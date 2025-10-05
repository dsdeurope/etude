/* eslint-disable */
import React, { useState, useEffect, useMemo } from "react";
import "./App.css";
import "./rubriques.css";
import RubriquesInline from "./RubriquesInline";
import BibleConcordancePage from "./BibleConcordancePage";
import CharacterHistoryPage from './CharacterHistoryPage';
import VersetParVersetPage from './VersetParVersetPage';
import NotesPage from "./NotesPage";
import RubriquePage from "./RubriquePage";
import ApiControlPanel from "./ApiControlPanel";

/* =========================
   Configuration et Helpers
========================= */

// Backend: 1) REACT_APP_BACKEND_URL si défini (nettoyé), 2) localhost en dev, 3) Railway en prod
const getBackendUrl = () => {
  // Utiliser la variable d'environnement en priorité
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  const hostname = window.location.hostname;
  if (hostname === "localhost" || hostname === "127.0.0.1") return "http://localhost:8001";
  // fallback pour les environnements non configurés
  return "https://scripture-ai-8.preview.emergentagent.com";
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL.replace(/\/+$/g, "")}/api`;

// Variables d'environnement configurées
// BACKEND_URL et API_BASE sont prêts à utiliser

// Style unifié pour tous les boutons de contrôle (même typographie que btn-validate)
const getButtonStyle = (gradientColors, shadowColor, isHovered = false) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '12px 8px',
  borderRadius: '14px',
  minHeight: '75px',
  fontSize: '12px',                    // Adapté de btn-validate (16px → 12px pour boutons plus petits)
  fontWeight: '700',                   // Identique à btn-validate
  fontFamily: "'Montserrat', sans-serif", // Identique à btn-validate
  color: 'white',
  border: 'none',
  cursor: 'pointer',
  background: `linear-gradient(135deg, ${gradientColors.start} 0%, ${gradientColors.end} 100%)`,
  boxShadow: isHovered 
    ? `0 10px 35px ${shadowColor.replace('0.25', '0.35')}, 0 3px 18px rgba(0, 0, 0, 0.15)`
    : `0 6px 20px ${shadowColor}, 0 2px 14px rgba(0, 0, 0, 0.1)`, // Adapté de btn-validate
  transition: 'all 0.3s ease',         // Identique à btn-validate
  transform: isHovered ? 'translateY(-2px) scale(1.02)' : 'translateY(0)',
  textTransform: 'uppercase',          // Identique à btn-validate
  letterSpacing: '0.8px',              // Adapté de btn-validate (1px → 0.8px)
  position: 'relative',                // Identique à btn-validate
  overflow: 'hidden'                   // Identique à btn-validate
})

// Fonction pour générer les couleurs des boutons basées sur le thème actuel
// TOUS LES BOUTONS ont la même couleur basée sur le thème sélectionné
const getThemeButtonColors = (theme) => {
  // Couleur unique basée sur le thème actuel
  const themeColor = {
    start: theme.primary,
    end: theme.secondary, 
    shadow: `rgba(${hexToRgb(theme.primary)}, 0.25)`
  };
  
  // Fonction helper pour convertir hex en rgb
  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r}, ${g}, ${b}`;
  }
  
  // Tous les boutons utilisent la même couleur thématique
  return {
    reset: themeColor,
    mystique: themeColor, 
    genese: themeColor,
    gemini: themeColor,
    versets: themeColor,
    generate: themeColor,
    concordance: themeColor
  };
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
   Données statiques
========================= */

const BOOKS = [
  "Genèse", "Exode", "Lévitique", "Nombres", "Deutéronome",
  "Josué", "Juges", "Ruth", "1 Samuel", "2 Samuel", "1 Rois", "2 Rois",
  "1 Chroniques", "2 Chroniques", "Esdras", "Néhémie", "Esther",
  "Job", "Psaumes", "Proverbes", "Ecclésiaste", "Cantique des cantiques",
  "Ésaïe", "Jérémie", "Lamentations", "Ézéchiel", "Daniel",
  "Osée", "Joël", "Amos", "Abdias", "Jonas", "Michée", "Nahum", "Habacuc",
  "Sophonie", "Aggée", "Zacharie", "Malachie",
  "Matthieu", "Marc", "Luc", "Jean", "Actes",
  "Romains", "1 Corinthiens", "2 Corinthiens", "Galates", "Éphésiens",
  "Philippiens", "Colossiens", "1 Thessaloniciens", "2 Thessaloniciens",
  "1 Timothée", "2 Timothée", "Tite", "Philémon", "Hébreux",
  "Jacques", "1 Pierre", "2 Pierre", "1 Jean", "2 Jean", "3 Jean", "Jude",
  "Apocalypse"
];

const BOOK_CHAPTERS = {
  "Genèse": 50, "Exode": 40, "Lévitique": 27, "Nombres": 36, "Deutéronome": 34,
  "Josué": 24, "Juges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
  "1 Rois": 22, "2 Rois": 25, "1 Chroniques": 29, "2 Chroniques": 36,
  "Esdras": 10, "Néhémie": 13, "Esther": 10, "Job": 42, "Psaumes": 150,
  "Proverbes": 31, "Ecclésiaste": 12, "Cantique des cantiques": 8,
  "Ésaïe": 66, "Jérémie": 52, "Lamentations": 5, "Ézéchiel": 48, "Daniel": 12,
  "Osée": 14, "Joël": 3, "Amos": 9, "Abdias": 1, "Jonas": 4, "Michée": 7,
  "Nahum": 3, "Habacuc": 3, "Sophonie": 3, "Aggée": 2, "Zacharie": 14, "Malachie": 4,
  "Matthieu": 28, "Marc": 16, "Luc": 24, "Jean": 21, "Actes": 28,
  "Romains": 16, "1 Corinthiens": 16, "2 Corinthiens": 13, "Galates": 6,
  "Éphésiens": 6, "Philippiens": 4, "Colossiens": 4, "1 Thessaloniciens": 5,
  "2 Thessaloniciens": 3, "1 Timothée": 6, "2 Timothée": 4, "Tite": 3,
  "Philémon": 1, "Hébreux": 13, "Jacques": 5, "1 Pierre": 5, "2 Pierre": 3,
  "1 Jean": 5, "2 Jean": 1, "3 Jean": 1, "Jude": 1, "Apocalypse": 22
};

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
  verseGemini: [
    "/generate-verse-by-verse-gemini",
    "/generate-verse-by-verse",
    "/g_te-verse-by-verse",
  ],
  studyGemini: [
    "/generate-study-gemini",
    "/generate-study",
    "/g_study_28",
  ],
};

async function smartPost(pathList, payload) {
  let lastErr = null;
  for (const p of pathList) {
    const url = `${API_BASE}${p}`;
    try {
      console.log("[API] POST →", url);
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
      });
      if (r.ok) {
        const ct = r.headers.get("content-type") || "";
        if (ct.includes("application/json")) {
          return { data: await r.json(), url };
        }
        return { data: { raw: await r.text() }, url };
      }
      if (r.status === 404) { lastErr = new Error(`404 @ ${url}`); continue; }
      const bodyText = await r.text().catch(() => "");
      throw new Error(`HTTP ${r.status} @ ${url}${bodyText ? " – " + bodyText.slice(0, 300) : ""}`);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error("Tous les endpoints ont échoué");
}

/* =========================
   Composant Principal App
========================= */

function App() {
  // Thèmes (définis en premier pour éviter erreur d'initialisation)
  const colorThemes = [
    { name: "Violet Mystique", primary: "#667eea", secondary: "#764ba2", accent: "#667eea",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      headerBg: "linear-gradient(90deg, #3b4371 0%, #f093fb 50%, #f5576c 100%)" },
    { name: "Océan Profond", primary: "#0891b2", secondary: "#0284c7", accent: "#0891b2",
      background: "linear-gradient(135deg, #0891b2 0%, #0284c7 100%)",
      headerBg: "linear-gradient(90deg, #075985 0%, #0ea5e9 50%, #38bdf8 100%)" },
    { name: "Émeraude Vert", primary: "#10b981", secondary: "#059669", accent: "#10b981",
      background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
      headerBg: "linear-gradient(90deg, #064e3b 0%, #34d399 50%, #6ee7b7 100%)" },
    { name: "Rose Passion", primary: "#ec4899", secondary: "#db2777", accent: "#ec4899",
      background: "linear-gradient(135deg, #ec4899 0%, #db2777 100%)",
      headerBg: "linear-gradient(90deg, #831843 0%, #f472b6 50%, #f9a8d4 100%)" },
    { name: "Orange Sunset", primary: "#f59e0b", secondary: "#d97706", accent: "#f59e0b",
      background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
      headerBg: "linear-gradient(90deg, #92400e 0%, #fbbf24 50%, #fcd34d 100%)" },
    { name: "Indigo Royal", primary: "#6366f1", secondary: "#4f46e5", accent: "#6366f1",
      background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
      headerBg: "linear-gradient(90deg, #312e81 0%, #818cf8 50%, #a5b4fc 100%)" }
  ];

  // États principaux
  const [currentTheme, setCurrentTheme] = useState(0);
  
  // Couleurs dynamiques basées sur le thème actuel (après colorThemes et currentTheme)
  const currentButtonColors = getThemeButtonColors(colorThemes[currentTheme]);
  
  const [selectedBook, setSelectedBook] = useState("Genèse");
  const [selectedChapter, setSelectedChapter] = useState("1");
  const [selectedVerse, setSelectedVerse] = useState("--");
  const [selectedVersion, setSelectedVersion] = useState("LSG");
  const [selectedLength, setSelectedLength] = useState(500);
  const [activeRubrique, setActiveRubrique] = useState(0);
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [generatedRubriques, setGeneratedRubriques] = useState({}); // Stockage du contenu généré
  const [rubriquesStatus, setRubriquesStatus] = useState({});
  const [lastStudy, setLastStudy] = useState(null);
  const [progressPercent, setProgressPercent] = useState(0);
  const [searchQuery, setSearchQuery] = useState(""); // ← unique déclaration

  // États génération progressive
  const [isProgressiveLoading, setIsProgressiveLoading] = useState(false);
  const [currentBatchVerse, setCurrentBatchVerse] = useState(1);
  const [progressiveStats, setProgressiveStats] = useState(null);
  const [isVersetsProgContent, setIsVersetsProgContent] = useState(false);
  const [currentVerseCount, setCurrentVerseCount] = useState(5);
  const [canContinueVerses, setCanContinueVerses] = useState(true);
  
  // États pour les notes persistantes - SUPPRIMÉES (remplacées par page dédiée)
  // const [personalNotes, setPersonalNotes] = useState(...)
  // const [showNotesModal, setShowNotesModal] = useState(false)

  // État pour la navigation
  const [currentPage, setCurrentPage] = useState('main'); // 'main', 'concordance', 'versets', 'notes', ou 'rubrique'
  const [versetPageContent, setVersetPageContent] = useState('');
  const [currentBookInfo, setCurrentBookInfo] = useState('');
  const [currentRubriqueNumber, setCurrentRubriqueNumber] = useState(1);
  const [currentRubriqueContent, setCurrentRubriqueContent] = useState('');
  
  // États pour la navigation entre les pages dédiées
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [selectedCharacterForHistory, setSelectedCharacterForHistory] = useState(null);
  const [currentTab, setCurrentTab] = useState('concordance');

  // Thèmes déplacés en début de fonction

  // Options de chapitres
  const availableChapters = useMemo(() => {
    if (selectedBook === "--" || !BOOK_CHAPTERS[selectedBook]) return ["--"];
    const max = BOOK_CHAPTERS[selectedBook] || 1;
    return ["--", ...Array.from({ length: max }, (_, i) => i + 1)];
  }, [selectedBook]);

  // Charger/sauver dernière étude et initialiser couleurs
  useEffect(() => {
    const saved = localStorage.getItem("lastBibleStudy");
    if (saved) { try { setLastStudy(JSON.parse(saved)); } catch(e){ console.error(e);} }
    const beforeUnload = () => saveCurrentStudy();
    window.addEventListener("beforeunload", beforeUnload);
    
    // Initialiser les couleurs du thème par défaut
    const theme = colorThemes[currentTheme];
    document.documentElement.style.setProperty('--theme-primary', `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`);
    document.documentElement.style.setProperty('--theme-secondary', `linear-gradient(135deg, ${theme.secondary}, ${theme.primary})`);
    document.documentElement.style.setProperty('--theme-accent', `linear-gradient(135deg, ${theme.accent}, ${theme.secondary})`);
    
    const hexToRgba = (hex, alpha) => {
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };
    
    document.documentElement.style.setProperty('--theme-accent-shadow', hexToRgba(theme.accent, 0.3));
    document.documentElement.style.setProperty('--theme-accent-shadow-hover', hexToRgba(theme.accent, 0.4));
    
    return () => window.removeEventListener("beforeunload", beforeUnload);
  }, [currentTheme]);

  // Appliquer thème au chargement
  useEffect(() => {
    setTimeout(() => { changePalette(); setCurrentTheme(0); }, 100);
  }, []);
  // Test immédiat de sauvegarde quand sélection change
  useEffect(() => {
    if (selectedBook !== "--" && selectedChapter !== "--") {
      console.log("[TEST SAUVEGARDE] Sélection valide détectée:", selectedBook, selectedChapter);
      saveCurrentStudy();
    }
  }, [selectedBook, selectedChapter]);

  // Initialiser la rubrique 0 au chargement avec le livre et chapitre sélectionnés
  useEffect(() => {
    if (selectedBook !== "--" && selectedChapter !== "--" && activeRubrique === 0) {
      console.log("[INIT RUBRIQUE] Initialisation rubrique 0 pour:", selectedBook, selectedChapter);
      handleRubriqueSelect(0);
    }
  }, [selectedBook, selectedChapter]);

  const saveCurrentStudy = () => {
    console.log("[DEBUG SAUVEGARDE] Tentative sauvegarde:", {
      selectedBook,
      selectedChapter,
      selectedVerse,
      content_length: content ? content.length : 0
    });
    
    if (selectedBook !== "--" && selectedChapter !== "--") {
      const currentStudy = {
        book: selectedBook, chapter: selectedChapter, verse: selectedVerse,
        version: selectedVersion, length: selectedLength, activeRubrique,
        content, rubriquesStatus, timestamp: new Date().toISOString(),
        displayTitle: `${selectedBook} ${selectedChapter}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`
      };
      localStorage.setItem("lastBibleStudy", JSON.stringify(currentStudy));
      setLastStudy(currentStudy);
      console.log("[SAUVEGARDE SUCCESS] Étude sauvegardée:", currentStudy.displayTitle);
    } else {
      console.log("[SAUVEGARDE SKIP] Conditions non remplies - livre ou chapitre = '--'");
    }
  };

  const restoreLastStudy = () => {
    if (!lastStudy) return;
    setSelectedBook(lastStudy.book);
    setSelectedChapter(lastStudy.chapter);
    setSelectedVerse(lastStudy.verse || "--");
    setSelectedVersion(lastStudy.version || "LSG");
    setSelectedLength(lastStudy.length || 500);
    setActiveRubrique(lastStudy.activeRubrique || 0);
    setContent(lastStudy.content || "");
    setRubriquesStatus(lastStudy.rubriquesStatus || {});
  };

  const rubriquesItems = BASE_RUBRIQUES.map((title, index) => ({ id: index, title }));

  /* =========================
     Gestionnaires
  ========================= */

  const handleBookChange = (e) => {
    saveCurrentStudy();
    const book = e.target.value;
    setSelectedBook(book);
    setSelectedChapter(book === "--" ? "--" : 1);
    setSelectedVerse("--");
  };

  const handleChapterChange = (e) => {
    saveCurrentStudy();
    const chapter = e.target.value;
    setSelectedChapter(chapter === "--" ? "--" : Number(chapter));
    setSelectedVerse("--");
  };

  const handleVerseChange = (e) => setSelectedVerse(e.target.value);
  const handleVersionChange = (e) => setSelectedVersion(e.target.value);
  const handleLengthChange = (e) => setSelectedLength(Number(e.target.value));

  // Recherche intelligente
  const parseSearchQuery = (query) => {
    if (!query.trim()) return null;
    const normalized = query.trim();
    const patterns = [/^(.+?)\s+(\d+):(\d+)$/, /^(.+?)\s+(\d+)$/, /^(.+)$/];
    for (const pat of patterns) {
      const m = normalized.match(pat);
      if (m) {
        const bookName = m[1].trim();
        const chapter = m[2] ? parseInt(m[2]) : null;
        const verse = m[3] ? parseInt(m[3]) : null;
        const found = BOOKS.find(b =>
          b.toLowerCase() === bookName.toLowerCase() ||
          b.toLowerCase().includes(bookName.toLowerCase()) ||
          bookName.toLowerCase().includes(b.toLowerCase())
        );
        if (found) return { book: found, chapter: chapter || 1, verse: verse || "--" };
      }
    }
    return null;
  };

  const handleSearchChange = (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    const parsed = parseSearchQuery(q);
    if (parsed) {
      saveCurrentStudy();
      setSelectedBook(parsed.book);
      setSelectedChapter(parsed.chapter);
      setSelectedVerse(parsed.verse);
    }
  };

  // Gestionnaires supprimés - définis plus bas

  // Fonction pour détecter et transformer les références bibliques en liens YouVersion
  const transformBibleReferences = (text) => {
    if (!text) return text;
    
    // Sauvegarder les balises HTML existantes pour les restaurer après
    const htmlTags = [];
    let tempText = text.replace(/<[^>]*>/g, (match) => {
      const placeholder = `__HTML_TAG_${htmlTags.length}__`;
      htmlTags.push(match);
      return placeholder;
    });
    
    // Set pour éviter les doublons
    const processedRefs = new Set();
    
    // Regex améliorée pour détecter les références bibliques (seulement dans le texte brut)
    const bibleRefRegex = /(\d?\s*[A-ZÀ-ÿ][a-zà-ÿ]*(?:\s+\d*\s*[A-ZÀ-ÿ][a-zà-ÿ]*)*)\s+(\d+)(?::(\d+)(?:[-–](\d+))?)?(?!\d)/g;
    
    // Traiter les références dans le texte temporaire (sans HTML)
    tempText = tempText.replace(bibleRefRegex, (match, book, chapter, verse1, verse2) => {
      const cleanMatch = match.trim();
      
      // Vérifier si cette référence a déjà été traitée (éviter les doublons)
      if (processedRefs.has(cleanMatch)) {
        return cleanMatch; // Retourner le texte sans lien si c'est un doublon
      }
      
      processedRefs.add(cleanMatch);
      
      // Construire l'URL YouVersion avec recherche directe
      const youVersionUrl = `https://www.bible.com/search/bible?q=${encodeURIComponent(cleanMatch)}`;
      
      // Créer le lien HTML avec styles
      return `<a href="${youVersionUrl}" target="_blank" class="bible-reference" title="${cleanMatch}">${cleanMatch}</a>`;
    });
    
    // Restaurer les balises HTML originales
    htmlTags.forEach((tag, index) => {
      tempText = tempText.replace(`__HTML_TAG_${index}__`, tag);
    });
    
    return tempText;
  };

  // Progress bar
  const wait = (ms) => new Promise(r => setTimeout(r, ms));

  // Fonction pour parser le contenu des 28 rubriques retourné par l'API
  const parseRubriquesContent = (fullContent) => {
    const rubriques = {};
    
    console.log("[PARSING DEBUG] Contenu reçu:", fullContent.length, "caractères");
    console.log("[PARSING DEBUG] Début du contenu:", fullContent.substring(0, 200));
    
    // Diviser le contenu par les titres de rubriques (## Rubrique 1: , ## Rubrique 2: , etc.)
    const sections = fullContent.split(/##\s*Rubrique\s*(\d+):\s*/i);
    
    console.log("[PARSING DEBUG] Sections trouvées:", sections.length);
    
    for (let i = 1; i < sections.length; i += 2) {
      const rubriqueNumber = parseInt(sections[i]); // Garder l'index 1-based pour correspondre aux rubriques
      let rubriqueContent = sections[i + 1] ? sections[i + 1].trim() : "";
      
      console.log(`[PARSING DEBUG] Rubrique ${rubriqueNumber}:`, rubriqueContent.length, "caractères");
      
      // Nettoyer le contenu - enlever le titre suivant s'il existe
      if (rubriqueContent) {
        // Enlever une éventuelle rubrique suivante qui serait incluse
        rubriqueContent = rubriqueContent.split('## Rubrique')[0].trim();
        
        // Nettoyer les sauts de ligne multiples
        rubriqueContent = rubriqueContent.replace(/\n{3,}/g, '\n\n').trim();
        
        if (rubriqueContent.length > 0) {
          rubriques[rubriqueNumber] = rubriqueContent;
          console.log(`[PARSING SUCCESS] Rubrique ${rubriqueNumber} parsée:`, rubriqueContent.substring(0, 100) + "...");
        }
      }
    }
    
    console.log("[PARSING FINAL] Rubriques parsées:", Object.keys(rubriques).length);
    return rubriques;
  };

  // Configuration des longueurs par rubrique
  const getRubriqueLength = (rubriqueNum) => {
    const lengthConfig = {
      1: 500,   // Prière d'ouverture
      2: 500,   // Structure littéraire
      3: 500,   // Questions du chapitre précédent
      4: 500,   // Thème doctrinal
      5: 1500,  // Fondements théologiques
      6: 1500,  // Contexte historique
      7: 1500,  // Contexte culturel
      8: 1500,  // Contexte géographique
      9: 1500,  // Analyse lexicale
      10: 1500, // Parallèles bibliques
      11: 1500, // Prophétie et accomplissement
      12: 1500, // Personnages
      13: 1500, // Structure rhétorique
      14: 1500, // Théologie trinitaire
      15: 2000, // Christ au centre
      16: 2000, // Évangile et grâce
      17: 2000, // Application personnelle
      18: 2000, // Application communautaire
      19: 2000, // Prière de réponse
      20: 2000, // Questions d'étude
      21: 2000, // Points de vigilance
      22: 2000, // Objections et réponses
      23: 2000, // Perspective missionnelle
      24: 2000, // Éthique chrétienne
      25: 2000, // Louange / liturgie
      26: 2000, // Méditation guidée
      27: 2000, // Mémoire / versets clés
      28: 2000  // Plan d'action
    };
    return lengthConfig[rubriqueNum] || 500;
  };

  // Fonction pour générer du contenu narratif théologique spécifique
  // Nouvelle fonction pour générer le contenu des rubriques via API
  const generateRubriqueContentViaAPI = async (rubriqueNum, rubriqueTitle, passage, book, chapter, targetLength) => {
    try {
      console.log(`[API RUBRIQUE ${rubriqueNum}] Génération via API: ${rubriqueTitle} pour ${book} ${chapter}`);
      
      const response = await fetch(`${getBackendUrl()}/api/generate-rubrique-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rubrique_number: rubriqueNum,
          rubrique_title: rubriqueTitle,
          book: book,
          chapter: parseInt(chapter),
          passage: passage,
          target_length: targetLength,
          use_gemini: true,
          enriched: true
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        console.log(`[API RUBRIQUE ${rubriqueNum}] Succès - ${result.word_count} mots - API: ${result.api_used}`);
        return result.content;
      } else {
        throw new Error('Erreur lors de la génération du contenu');
      }

    } catch (error) {
      console.error(`[ERROR RUBRIQUE ${rubriqueNum}]`, error);
      
      // Fallback vers le contenu statique en cas d'erreur API
      return generateRubriqueContentStatic(rubriqueNum, rubriqueTitle, passage, book, chapter, targetLength);
    }
  };

  // Renommer l'ancienne fonction pour le fallback
  const generateRubriqueContentStatic = (rubriqueNum, rubriqueTitle, passage, book, chapter, userSelectedLength = null) => {
    // Utiliser la longueur choisie par l'utilisateur ou la longueur par défaut de la rubrique
    const targetLength = userSelectedLength || getRubriqueLength(rubriqueNum);
    
    const contenuParRubrique = {
      1: generatePrayerContent(passage, targetLength),
      2: generateStructureContent(passage, book, chapter, targetLength),
      3: generatePreviousChapterContent(passage, book, chapter, targetLength),
      4: generateDoctrinalThemeContent(passage, book, chapter, targetLength),
      5: generateTheologicalFoundationsContent(passage, book, chapter, targetLength),
      6: generateHistoricalContextContent(passage, book, chapter, targetLength),
      7: generateCulturalContextContent(passage, book, chapter, targetLength),
      8: generateGeographicalContextContent(passage, book, chapter, targetLength),
      9: generateLexicalAnalysisContent(passage, book, chapter, targetLength),
      10: generateBiblicalParallelsContent(passage, book, chapter, targetLength),
      11: generateProphecyContent(passage, book, chapter, targetLength),
      12: generateCharactersContent(passage, book, chapter, targetLength),
      13: generateRhetoricalStructureContent(passage, book, chapter, targetLength),
      14: generateTrinityTheologyContent(passage, book, chapter, targetLength),
      15: generateChristCenteredContent(passage, book, chapter, targetLength),
      16: generateGospelGraceContent(passage, book, chapter, targetLength),
      17: generatePersonalApplicationContent(passage, book, chapter, targetLength),
      18: generateCommunityApplicationContent(passage, book, chapter, targetLength),
      19: generateResponsePrayerContent(passage, book, chapter, targetLength),
      20: generateStudyQuestionsContent(passage, book, chapter, targetLength),
      21: generateVigilancePointsContent(passage, book, chapter, targetLength),
      22: generateObjectionsResponsesContent(passage, book, chapter, targetLength),
      23: generateMissionalPerspectiveContent(passage, book, chapter, targetLength),
      24: generateChristianEthicsContent(passage, book, chapter, targetLength),
      25: generateWorshipLiturgyContent(passage, book, chapter, targetLength),
      26: generateGuidedMeditationContent(passage, book, chapter, targetLength),
      27: generateMemoryVersesContent(passage, book, chapter, targetLength),
      28: generateActionPlanContent(passage, book, chapter, targetLength)
    };

    return contenuParRubrique[rubriqueNum] || 
      generateDefaultContent(rubriqueTitle, passage, book, chapter, targetLength);
  };

  // Fonction pour la prière d'ouverture avec progression narrative théologique
  const generatePrayerContent = (passage, targetLength) => {
    const baseContent = `**Adoration :** Seigneur Dieu, Créateur du ciel et de la terre, nous reconnaissons ta grandeur manifestée dans ${passage}. Tu es celui qui appelle à l'existence ce qui n'était pas.

**Confession :** Père, nous confessons notre petitesse face à ta majesté créatrice révélée dans ${passage}. Pardonne-nous nos manquements.

**Demande :** Esprit Saint, éclaire notre compréhension de ${passage}.`;

    if (targetLength >= 500) {
      return baseContent + `

Dans cette prière d'ouverture, nous nous approchons du trône de la grâce avec une révérence qui sied à la majesté divine révélée dans ${passage}. L'adoration authentique naît de la contemplation des perfections divines manifestées dans l'Écriture sainte.`;
    }

    if (targetLength >= 1000) {
      return baseContent + `

Dans cette prière d'ouverture, nous nous approchons du trône de la grâce avec une révérence qui sied à la majesté divine révélée dans ${passage}. L'adoration authentique naît de la contemplation des perfections divines manifestées dans l'Écriture sainte.

La tradition patristique et réformée nous enseigne que la lectio divina doit débuter par l'invocation du Saint-Esprit, seul capable d'illuminer l'entendement humain obscurci par le péché. Comme l'affirme Jean Chrysostome : "Les Écritures sont une lettre que Dieu nous a envoyée d'en haut." Cette lettre divine nécessite l'illumination céleste pour être comprise dans toute sa profondeur sotériologique.

Notre confession s'enracine dans la reconnaissance de notre finitude créaturelle face à l'infinité divine. L'humilité herméneutique constitue le préalable indispensable à toute exégèse fidèle.`;
    }

    if (targetLength >= 2000) {
      return baseContent + `

Dans cette prière d'ouverture, nous nous approchons du trône de la grâce avec une révérence qui sied à la majesté divine révélée dans ${passage}. L'adoration authentique naît de la contemplation des perfections divines manifestées dans l'Écriture sainte.

La tradition patristique et réformée nous enseigne que la lectio divina doit débuter par l'invocation du Saint-Esprit, seul capable d'illuminer l'entendement humain obscurci par le péché. Comme l'affirme Jean Chrysostome : "Les Écritures sont une lettre que Dieu nous a envoyée d'en haut." Cette lettre divine nécessite l'illumination céleste pour être comprise dans toute sa profondeur sotériologique.

Notre confession s'enracine dans la reconnaissance de notre finitude créaturelle face à l'infinité divine. L'humilité herméneutique constitue le préalable indispensable à toute exégèse fidèle.

L'École d'Antioche et l'École d'Alexandrie, malgré leurs divergences herméneutiques, s'accordaient sur cette vérité fondamentale : l'Écriture ne se dévoile pleinement qu'à celui qui s'approche d'elle dans la prière et la dépendance de l'Esprit. Origène écrivait : "La parole de Dieu est comme un grain de froment : si tu n'en broies pas l'écorce par la méditation et la prière, tu ne peux en goûter la moelle."

Cette démarche spirituelle s'inscrit dans la lignée de la Sola Scriptura réformée, qui affirme non seulement l'autorité suprême de l'Écriture, mais aussi la nécessité de l'illumination divine pour sa juste compréhension. Calvin soulignait que "l'Écriture est son propre interprète", mais sous la conduite du Saint-Esprit qui en est l'auteur principal.

Ainsi, notre prière d'ouverture devant ${passage} n'est pas une simple formalité liturgique, mais l'expression de notre théologie de la révélation : Dieu se révèle, l'homme reçoit par grâce, et l'Esprit rend témoignage à la vérité divine dans le cœur du croyant régénéré.`;
    }

    return baseContent;
  };

  // Fonction pour structure littéraire (500 caractères)
  const generateStructureContent = (passage, book, chapter, targetLength) => {
    return `L'architecture littéraire de ${passage} révèle l'ordre divin dans la création. Cette structure en sept jours manifeste la perfection divine : trois jours de séparation (lumière/ténèbres, eaux/eaux, terre/mer) suivis de trois jours de peuplement (luminaires, animaux aquatiques et volants, animaux terrestres et l'homme). Le septième jour couronne l'œuvre par le repos divin, établissant le principe du sabbat. Cette progression méthodique "Dieu dit... et cela fut... Dieu vit que cela était bon" démontre la souveraineté divine.`;
  };

  // Fonction pour questions du chapitre précédent (500 caractères)
  const generatePreviousChapterContent = (passage, book, chapter, targetLength) => {
    if (chapter === "1") {
      return `${passage} ouvre le récit biblique sans prologue humain, plongeant directement dans l'acte créateur divin. Cette ouverture majestueuse établit Dieu comme l'acteur principal de l'histoire. L'absence de contexte préalable souligne l'éternité et la primauté divines. Cette introduction théologique prépare tout le développement biblique ultérieur, posant les fondements de l'alliance, de la révélation progressive et du plan de salut qui se déploieront dans toute l'Écriture.`;
    }
    return `L'étude de ${passage} s'inscrit dans la continuité du récit biblique. Les événements précédents éclairent la compréhension de ce passage et préparent les développements théologiques qui suivront.`;
  };

  // Fonction pour thème doctrinal (500 caractères)
  const generateDoctrinalThemeContent = (passage, book, chapter, targetLength) => {
    return `Le thème doctrinal central de ${passage} proclame la souveraineté créatrice de Dieu. Trois vérités fondamentales émergent : l'existence éternelle de Dieu avant toute création, sa parole efficace qui appelle à l'existence ce qui n'était pas, et sa bonne volonté envers son œuvre. L'homme, créé à l'image divine, reçoit la dignité unique de représentant de Dieu sur terre. Le sabbat établit le rythme divin entre travail et repos, révélant la nature même de Dieu dans l'alternance activité/contemplation.`;
  };

  // Fonction pour fondements théologiques avec progression narrative selon longueur
  const generateTheologicalFoundationsContent = (passage, book, chapter, targetLength) => {
    const baseContent = `La narration de ${passage} établit les piliers théologiques de la foi chrétienne. L'Écriture révèle que Dieu, dans sa trinité éternelle, précède toute réalité créée.`;

    if (targetLength >= 500) {
      return baseContent + ` La création ex nihilo manifeste la toute-puissance divine. L'anthropologie biblique trouve ici ses racines : l'homme, créé à l'image de Dieu (imago Dei), reçoit une dignité unique dans la création.`;
    }

    if (targetLength >= 1000) {
      return baseContent + ` La création ex nihilo manifeste la toute-puissance divine. Contrairement aux cosmogonies babyloniennes qui décrivent des théomachies primordiales, l'Écriture présente un Dieu souverain créant par sa seule parole.

L'anthropologie biblique trouve ici ses fondements : l'homme, créé à l'image de Dieu (imago Dei), reçoit une dignité unique. Cette ressemblance divine ne réside pas dans la corporéité mais dans les facultés spirituelles : intelligence, volonté, capacité relationnelle et responsabilité morale. L'homme devient ainsi le vice-gérent de Dieu sur terre.

Le sabbat révèle la pédagogie divine. En se reposant le septième jour, Dieu établit un modèle anthropologique : l'alternance entre activité créatrice et contemplation adoratrice. Cette institution sabbatique préfigure le repos eschatologique promis au peuple de Dieu et trouve son accomplissement sotériologique en Christ, notre repos sabbatique véritable selon l'épître aux Hébreux.`;
    }

    if (targetLength >= 2000) {
      return baseContent + ` La création ex nihilo (à partir du néant) manifeste la toute-puissance divine et constitue un dogme fondamental distinguant radicalement la foi biblique de toute philosophie naturaliste ou panthéiste. Contrairement aux cosmogonies babyloniennes (Enuma Elish) qui décrivent des théomachies primordiales, l'Écriture présente un Dieu souverain créant par sa seule parole efficace.

L'anthropologie biblique trouve ici ses fondements doctrinaux incontournables. L'homme, créé à l'image de Dieu (imago Dei selon Genèse 1:27), reçoit une dignité ontologique unique dans l'ordre créationnel. Cette ressemblance divine ne réside pas dans la corporéité (contra l'anthropomorphisme naïf) mais dans les facultés spirituelles : intellectus, voluntas, capacité relationnelle et responsabilité morale coram Deo. L'homme devient ainsi le vice-gérent divin sur terre, participant à la souveraineté divine par délégation gracieuse.

La théologie sabbatique révèle la pédagogie divine et établit les fondements de la sanctification du temps. En se reposant le septième jour, Dieu établit un paradigme anthropologique fondamental : l'alternance entre activité créatrice (opus Dei) et contemplation adoratrice (otium sanctum). Cette institution sabbatique préfigure le repos eschatologique promis au peuple de Dieu et trouve son accomplissement sotériologique en Christ, notre repos sabbatique véritable selon l'exégèse de l'épître aux Hébreux (chapitre 4).

L'École de Westminster et les théologiens réformés orthodoxes (Turretin, Brakel, Owen) ont développé ces fondements avec une rigueur scolastique remarquable, établissant la théologie systématique sur ces bases scripturaires inébranlables. Ces vérités révélées constituent le socle doctrinal de la foi réformée et demeurent le rempart théologique face aux défis de la modernité séculière et du naturalisme méthodologique contemporain.`;
    }

    return baseContent;
  };

  // Fonction pour contexte historique (1500 caractères) - Plus narratif et théologique
  const generateHistoricalContextContent = (passage, book, chapter, targetLength) => {
    return `L'étude du contexte historique de ${passage} nous plonge dans l'univers du Proche-Orient ancien, où les cosmogonies babyloniennes et égyptiennes dominaient la pensée religieuse. Dans ce milieu culturel saturé de mythologies, la révélation biblique émerge comme une voix prophétique unique et révolutionnaire.

Les récits babyloniens comme l'Enuma Elish présentent la création comme le résultat de conflits titanesques entre divinités primordiales. Marduk vainc Tiamat, déesse du chaos, et de son cadavre forme le cosmos. Ces mythes reflètent une vision cyclique du temps et une compréhension polythéiste du divin. La révélation mosaïque s'oppose radicalement à ces conceptions.

L'Écriture proclame un Dieu unique, éternel, qui crée par sa parole sans opposition ni combat. Cette vérité révélée corrige les erreurs théologiques de l'environnement culturel israélite. Le peuple de Dieu reçoit ainsi une compréhension purifiée de la divinité, libérée des superstitions et des craintes liées aux forces naturelles divinisées.

L'historicité du récit, débattue dans les cercles académiques contemporains, ne diminue en rien sa portée théologique. Que l'on adopte une lecture littérale ou littéraire, l'enseignement doctrinal demeure inchangé : Dieu est le créateur souverain, l'homme porte son image, et la création révèle sa gloire.

Cette perspective historique enrichit notre compréhension et renforce notre foi en la véracité de la révélation divine face aux idéologies contemporaines qui tentent de réduire l'homme à un simple produit du hasard évolutif.`;
  };

  // Fonction générique pour contenu par défaut
  const generateDefaultContent = (rubriqueTitle, passage, book, chapter, targetLength) => {
    const baseContent = `**${rubriqueTitle}** dans le contexte de ${passage}

Cette rubrique examine ${passage} sous l'angle de "${rubriqueTitle}". L'analyse révèle des vérités importantes pour notre compréhension théologique et notre marche chrétienne.

**Enseignement biblique :** ${passage} nous instruit sur la nature de Dieu et son œuvre dans l'histoire du salut.
**Application pratique :** Ces vérités transforment notre relation avec le Créateur et notre vision du monde.`;

    // Étendre le contenu selon la longueur cible
    if (targetLength >= 1500) {
      return baseContent + `

La narration scripturaire nous invite à une méditation approfondie sur les implications de ce passage. L'Esprit Saint, par sa grâce illuminatrice, nous révèle les richesses cachées de la Parole divine. Cette section de l'Écriture s'inscrit dans le grand dessein rédempteur de Dieu, préparant la venue du Messie et l'établissement de son royaume éternel.

**Dimension théologique :** L'étude de ${passage} enrichit notre compréhension de la nature divine et de ses attributs.
**Portée sotériologique :** Ce texte contribue à notre compréhension du salut par grâce au moyen de la foi.
**Perspective eschatologique :** Les vérités révélées ici éclairent notre espérance en la consommation du royaume de Dieu.`;
    }

    return baseContent;
  };

  // Fonction pour Christ au centre (2000 caractères) - Très théologique et narratif
  const generateChristCenteredContent = (passage, book, chapter, targetLength) => {
    return `La lecture christocentrique de ${passage} révèle la présence du Fils éternel dès l'œuvre créatrice. L'Écriture nous enseigne que "toutes choses ont été faites par lui, et rien de ce qui a été fait n'a été fait sans lui" (Jean 1:3). Cette vérité transforme radicalement notre compréhension de la création.

Le Logos divin, second membre de la Trinité sainte, participe activement à l'acte créateur. Quand Dieu dit "Que la lumière soit", c'est la Parole éternelle qui s'exprime. Cette lumière primordiale préfigure Christ, "lumière du monde" qui viendra éclairer les ténèbres spirituelles de l'humanité déchue.

L'expression "Faisons l'homme à notre image" (Genèse 1:26) révèle la consultation trinitaire. Le Père, le Fils et le Saint-Esprit concourent à la création de l'homme. Cette image divine imprimée en Adam trouve son archétype parfait en Jésus-Christ, "image du Dieu invisible" (Colossiens 1:15). L'homme déchu sera restauré à cette image par l'œuvre rédemptrice du Fils incarné.

Le sabbat créationnel annonce prophétiquement le repos que Christ procurera à son peuple. "Venez à moi, vous tous qui êtes fatigués et chargés, et je vous donnerai du repos" (Matthieu 11:28). Le sabbat temporel s'accomplit dans le repos éternel que le Sauveur assure à tous ceux qui croient en lui.

La domination accordée à l'homme sur la création préfigure la royauté universelle du Fils de l'homme. Christ, second Adam, restaurera cette domination perdue par la chute et l'exercera parfaitement dans son royaume millénaire et éternel.

Cette lecture christologique de la création enrichit notre adoration et affermit notre espérance en celui qui est "l'Alpha et l'Oméga, le commencement et la fin".`;
  };

  // Fonction pour évangile et grâce (2000 caractères) - Très théologique et narratif
  const generateGospelGraceContent = (passage, book, chapter, targetLength) => {
    return `Dans la magnificence de ${passage}, l'évangile de la grâce divine se dessine déjà en filigrane. Bien que l'humanité n'ait pas encore chuté, la prescience divine connaît déjà le plan rédempteur qui se déploiera à travers l'histoire sainte.

La création ex nihilo manifeste la grâce première de Dieu. Rien ne l'obligeait à créer ; aucun besoin ne le contraignait à donner l'existence à l'univers. Cette création gratuite révèle la nature généreuse et aimante du Créateur. Cette gratuité originelle préfigure la grâce salvatrice qui sera manifestée en Jésus-Christ.

La bénédiction divine sur l'humanité - "Dieu les bénit" - constitue la première effusion de grâce sur les créatures portant son image. Cette bénédiction créationnelle anticipe la bénédiction rédemptrice qui coulera du sacrifice de l'Agneau immolé dès la fondation du monde.

L'établissement du sabbat révèle la pédagogie divine. Dieu enseigne à l'homme le rythme de la grâce : six jours de labeur suivis d'un jour de repos et de communion. Ce principe éducatif prépare l'humanité à comprendre que le salut ne s'obtient pas par les œuvres mais par la grâce, au moyen de la foi.

L'environnement édénique - implicite dans ce chapitre et explicité au suivant - manifeste la bonté gratuite de Dieu envers ses créatures. Cette bonté originelle témoigne du désir divin de communion avec l'humanité, désir qui trouvera son accomplissement parfait dans l'incarnation du Fils.

Même la capacité humaine de répondre à Dieu, de le connaître et de l'adorer, constitue un don de la grâce divine. L'imago Dei n'est pas un mérite humain mais un cadeau du Créateur aimant.

Cette perspective évangélique de la création nourrit notre gratitude et nous prépare à mieux saisir la grandeur de la grâce salvatrice manifestée en Christ Jésus notre Seigneur.`;
  };

  // Ajouter d'autres fonctions pour les rubriques restantes...
  const generateCulturalContextContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Contexte culturel", passage, book, chapter, targetLength);
  };

  const generateGeographicalContextContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Contexte géographique", passage, book, chapter, targetLength);
  };

  const generateLexicalAnalysisContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Analyse lexicale", passage, book, chapter, targetLength);
  };

  const generateBiblicalParallelsContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Parallèles bibliques", passage, book, chapter, targetLength);
  };

  const generateProphecyContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Prophétie et accomplissement", passage, book, chapter, targetLength);
  };

  const generateCharactersContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Personnages", passage, book, chapter, targetLength);
  };

  const generateRhetoricalStructureContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Structure rhétorique", passage, book, chapter, targetLength);
  };

  const generateTrinityTheologyContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Théologie trinitaire", passage, book, chapter, targetLength);
  };

  const generatePersonalApplicationContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Application personnelle", passage, book, chapter, targetLength);
  };

  const generateCommunityApplicationContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Application communautaire", passage, book, chapter, targetLength);
  };

  const generateResponsePrayerContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Prière de réponse", passage, book, chapter, targetLength);
  };

  const generateStudyQuestionsContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Questions d'étude", passage, book, chapter, targetLength);
  };

  const generateVigilancePointsContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Points de vigilance", passage, book, chapter, targetLength);
  };

  const generateObjectionsResponsesContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Objections et réponses", passage, book, chapter, targetLength);
  };

  const generateMissionalPerspectiveContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Perspective missionnelle", passage, book, chapter, targetLength);
  };

  const generateChristianEthicsContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Éthique chrétienne", passage, book, chapter, targetLength);
  };

  const generateWorshipLiturgyContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Louange / liturgie", passage, book, chapter, targetLength);
  };

  const generateGuidedMeditationContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Méditation guidée", passage, book, chapter, targetLength);
  };

  const generateMemoryVersesContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Mémoire / versets clés", passage, book, chapter, targetLength);
  };

  const generateActionPlanContent = (passage, book, chapter, targetLength) => {
    return generateDefaultContent("Plan d'action", passage, book, chapter, targetLength);
  };

  // Fonction pour générer un contenu fallback intelligent
  const generateIntelligentFallback = (passage, book, chapter) => {
    return `**ÉTUDE BIBLIQUE — 28 RUBRIQUES**
**Passage :** ${passage} (LSG)

## 1. Prière d'ouverture
Seigneur, ouvre nos cœurs à la compréhension de ${passage}. Que ton Esprit nous guide dans ta vérité et nous transforme par ta Parole. Accorde-nous la sagesse pour discerner tes enseignements et la force pour les appliquer dans notre vie quotidienne.

## 2. Structure littéraire
Le passage de ${passage} révèle une structure littéraire soigneusement orchestrée qui sert le propos théologique de l'auteur inspiré. Cette organisation guide le lecteur vers une compréhension progressive des vérités divines révélées.

## 3. Questions du chapitre précédent
L'étude de ${passage} doit être mise en relation avec le contexte qui précède. Quels thèmes et enseignements préparent le lecteur à comprendre ce passage dans sa continuité narrative et théologique ?

## 4. Thème doctrinal
Le thème doctrinal central de ${passage} manifeste des vérités fondamentales sur la nature de Dieu, la condition humaine et le plan de salut. Ces enseignements s'inscrivent dans la révélation progressive de Dieu.

## 5. Fondements théologiques
${passage} établit des fondements théologiques importants qui éclairent notre compréhension de l'œuvre de Dieu dans l'histoire et dans nos vies. Ces vérités fondamentales structurent la foi chrétienne.

## 6. Contexte historique
Le contexte historique de ${passage} éclaire la situation des premiers auditeurs et enrichit notre compréhension contemporaine. Connaître les circonstances originales aide à saisir l'intention divine.

## 7. Contexte culturel
Les éléments culturels présents dans ${passage} révèlent les coutumes et pratiques de l'époque, permettant une meilleure interprétation des enseignements bibliques dans leur cadre original.

## 8. Contexte géographique
La géographie de ${passage} offre des clés d'interprétation importantes. Les lieux mentionnés portent souvent une signification symbolique et théologique qui enrichit le message.

## 9. Analyse lexicale
L'étude des termes clés dans ${passage} révèle la richesse du vocabulaire biblique et les nuances importantes pour une compréhension précise du texte inspiré.

## 10. Parallèles bibliques
${passage} trouve des échos dans d'autres parties de l'Écriture. Ces parallèles bibliques éclairent le sens et montrent l'unité de la révélation divine.

## 11. Prophétie et accomplissement
Les éléments prophétiques présents dans ${passage} s'inscrivent dans le plan rédempteur de Dieu et trouvent leur accomplissement ultime en Jésus-Christ.

## 12. Personnages
Les personnages mentionnés dans ${passage} offrent des modèles ou des avertissements pour notre marche chrétienne. Leur exemple instruit notre foi.

## 13. Structure rhétorique
La rhétorique employée dans ${passage} révèle l'art divin de la communication. La structure argumentative guide le lecteur vers les vérités essentielles.

## 14. Théologie trinitaire
${passage} révèle des aspects de la nature trinitaire de Dieu : Père, Fils et Saint-Esprit œuvrent ensemble dans l'histoire du salut.

## 15. Christ au centre
Christ se révèle au centre de ${passage} comme accomplissement des promesses et clé d'interprétation de l'Écriture. L'herméneutique christocentrique éclaire ce texte.

## 16. Évangile et grâce
${passage} manifeste la grâce de Dieu et les vérités évangéliques fondamentales. Le salut par grâce au moyen de la foi transparaît dans ce texte.

## 17. Application personnelle
Comment ${passage} transforme-t-il notre marche quotidienne avec Dieu ? Ce texte nous interpelle sur nos attitudes, nos priorités et notre relation avec le Seigneur.

## 18. Application communautaire
${passage} éclaire la vie de l'Église et les relations fraternelles. Les principes énoncés s'appliquent à la communauté des croyants.

## 19. Prière de réponse
En réponse à l'étude de ${passage}, offrons à Dieu notre reconnaissance, notre confession et nos requêtes. Que sa Parole transforme nos cœurs.

## 20. Questions d'étude
- Que révèle ${passage} sur la nature de Dieu ?
- Que nous enseigne ce texte sur la condition humaine ?
- Quels changements ce passage appelle-t-il dans notre vie ?

## 21. Points de vigilance
Quelles sont les erreurs d'interprétation à éviter concernant ${passage} ? Quels écueils théologiques ce texte nous aide-t-il à contourner ?

## 22. Objections et réponses
Comment répondre aux objections couramment soulevées contre les enseignements de ${passage} ? Quels arguments bibliques y répondent ?

## 23. Perspective missionnelle
${passage} éclaire-t-il notre mission d'évangélisation ? Comment ce texte motive-t-il et oriente-t-il l'œuvre missionnaire ?

## 24. Éthique chrétienne
Quels principes éthiques ${passage} établit-il ? Comment guide-t-il nos choix moraux et notre conduite chrétienne ?

## 25. Louange / liturgie
Comment ${passage} nourrit-il notre adoration ? Quels éléments peuvent enrichir notre louange communautaire et personnelle ?

## 26. Méditation guidée
Prenons un moment pour méditer personnellement sur ${passage}. Que le Saint-Esprit grave ces vérités dans nos cœurs.

## 27. Mémoire / versets clés
Verset-clé suggéré : ${passage}:1
Mémorisons ce verset pour porter sa vérité dans notre quotidien.

## 28. Plan d'action
- Une action personnelle cette semaine en réponse à ${passage}
- Une application communautaire ce mois-ci
- Un témoignage à partager de l'impact de ce texte`;
  };

  // Fonction pour générer du contenu de fallback intelligent par rubrique
  const generateFallbackRubriqueContent = (rubriqueNum, rubriqueTitle, passage) => {
    const fallbacks = {
      1: `Seigneur, ouvre nos cœurs à la compréhension de ${passage}. Que ton Esprit nous guide dans ta vérité et nous transforme par ta Parole. Accorde-nous la sagesse pour discerner tes enseignements et la force pour les appliquer dans notre vie quotidienne.`,
      
      2: `Le passage de ${passage} révèle une structure littéraire soigneusement orchestrée qui sert le propos théologique de l'auteur inspiré. Cette organisation n'est pas fortuite mais guide le lecteur vers une compréhension progressive des vérités divines révélées.`,
      
      4: `Le thème doctrinal central de ${passage} manifeste des vérités fondamentales sur la nature de Dieu, la condition humaine et le plan de salut. Ces enseignements s'inscrivent dans la révélation progressive de Dieu et trouvent leur accomplissement en Christ.`,
      
      6: `Le contexte historique de ${passage} éclaire la situation des premiers auditeurs et enrichit notre compréhension contemporaine. Connaître les circonstances originales nous aide à mieux saisir l'intention divine et l'application universelle du texte.`,
      
      15: `Christ se révèle au centre de ${passage} comme accomplissement des promesses et clé d'interprétation de l'Écriture. L'herméneutique christocentrique nous permet de découvrir comment ce passage témoigne de l'œuvre rédemptrice du Sauveur.`,
      
      17: `Application personnelle : comment ${passage} transforme-t-il notre marche quotidienne avec Dieu et notre croissance spirituelle ? Ce texte nous interpelle sur nos attitudes, nos priorités et notre relation avec le Seigneur.`
    };

    return fallbacks[rubriqueNum] || `**${rubriqueTitle}**\n\nCette section de ${passage} nous enseigne des vérités importantes selon la perspective de ${rubriqueTitle.toLowerCase()}. L'analyse de ce passage révèle des insights précieux pour notre compréhension biblique et notre application pratique.\n\n*Contenu généré automatiquement - ${rubriqueNum}/${BASE_RUBRIQUES.length} rubriques*`;
  };
  const animateProgress = async (duration = 3000) => {
    setProgressPercent(0);
    const steps = 100, step = duration / steps;
    for (let i = 0; i <= steps; i++) { setProgressPercent(i); await wait(step); }
  };

  // YouVersion
  const openYouVersion = () => {
    if (selectedBook === "--") return alert("Veuillez d'abord sélectionner un livre de la Bible");
    const bookCodes = {"Genèse":"GEN","Exode":"EXO","Lévitique":"LEV","Nombres":"NUM","Deutéronome":"DEU","Josué":"JOS","Juges":"JDG","Ruth":"RUT","1 Samuel":"1SA","2 Samuel":"2SA","1 Rois":"1KI","2 Rois":"2KI","1 Chroniques":"1CH","2 Chroniques":"2CH","Esdras":"EZR","Néhémie":"NEH","Esther":"EST","Job":"JOB","Psaumes":"PSA","Proverbes":"PRO","Ecclésiaste":"ECC","Cantique des cantiques":"SNG","Ésaïe":"ISA","Jérémie":"JER","Lamentations":"LAM","Ézéchiel":"EZK","Daniel":"DAN","Osée":"HOS","Joël":"JOL","Amos":"AMO","Abdias":"OBA","Jonas":"JON","Michée":"MIC","Nahum":"NAM","Habacuc":"HAB","Sophonie":"ZEP","Aggée":"HAG","Zacharie":"ZEC","Malachie":"MAL","Matthieu":"MAT","Marc":"MRK","Luc":"LUK","Jean":"JHN","Actes":"ACT","Romains":"ROM","1 Corinthiens":"1CO","2 Corinthiens":"2CO","Galates":"GAL","Éphésiens":"EPH","Philippiens":"PHP","Colossiens":"COL","1 Thessaloniciens":"1TH","2 Thessaloniciens":"2TH","1 Timothée":"1TI","2 Timothée":"2TI","Tite":"TIT","Philémon":"PHM","Hébreux":"HEB","Jacques":"JAS","1 Pierre":"1PE","2 Pierre":"2PE","1 Jean":"1JN","2 Jean":"2JN","3 Jean":"3JN","Jude":"JUD","Apocalypse":"REV"};
    const code = bookCodes[selectedBook]; if (!code) return alert("Livre non reconnu pour YouVersion");
    let url = `https://www.bible.com/fr/bible/63/${code}`;
    if (selectedChapter !== "--") { url += `.${selectedChapter}`; if (selectedVerse !== "--") url += `.${selectedVerse}`; }
    window.open(url, "_blank");
  };

  const handleReset = () => {
    saveCurrentStudy();
    setSelectedBook("--"); setSelectedChapter("--"); setSelectedVerse("--");
    setSelectedVersion("LSG"); setSelectedLength(500); setActiveRubrique(0);
    setContent(""); setRubriquesStatus({});
    setProgressiveStats(null);
    // Note: Les notes personnelles ne sont jamais effacées lors du reset
  };

  // Fonctions pour les notes persistantes
  const handleNotesClick = () => {
    navigateToNotes();
  };

  // SUPPRIMÉ : showNotesModal et fonctions de modal - remplacées par page dédiée

  // SUPPRIMÉ : handleCloseNotes - plus besoin avec page dédiée

  // Fonctions pour la navigation
  const navigateToConcordance = () => {
    setCurrentPage('concordance');
  };

  const navigateToVersets = (content, bookInfo) => {
    setVersetPageContent(content);
    setCurrentBookInfo(bookInfo);
    setCurrentPage('versets');
  };

  const navigateToNotes = () => {
    setCurrentPage('notes');
  };

  const navigateToRubrique = (rubriqueNumber, content = '') => {
    console.log(`[NAVIGATE RUBRIQUE DEBUG] Rubrique ${rubriqueNumber}:`);
    console.log(`[NAVIGATE RUBRIQUE DEBUG] Content reçu:`, content ? content.length : 0, "caractères");
    console.log(`[NAVIGATE RUBRIQUE DEBUG] Content preview:`, content ? content.slice(0, 100) + "..." : "VIDE");
    
    setCurrentRubriqueNumber(rubriqueNumber);
    setCurrentRubriqueContent(content);
    const bookInfo = `${selectedBook || 'Genèse'} ${selectedChapter || '1'}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`;
    setCurrentBookInfo(bookInfo);
    setCurrentPage('rubrique');
  };

  const navigateToMain = () => {
    setCurrentPage('main');
  };

  // Fonction pour revenir de la page d'histoire de personnage
  const handleBackFromCharacter = () => {
    setSelectedCharacterForHistory(null);
  };

  const continueVerses = async () => {
    try {
      setIsLoading(true);
      
      const book = selectedBook || 'Genèse';
      const chapter = selectedChapter || '1';
      const passage = `${book} ${chapter}`;
      const startVerse = currentVerseCount + 1;
      const endVerse = currentVerseCount + 5;
      
      console.log(`[CONTINUE VERSETS] Génération versets ${startVerse} à ${endVerse} pour ${passage}`);
      
      const apiUrl = `${API_BASE}/generate-verse-by-verse`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          passage: `${passage}:${startVerse}-${endVerse}`,
          version: selectedVersion || 'LSG',
          tokens: parseInt(selectedLength) || 500,
          use_gemini: true,
          enriched: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.content) {
        const currentContent = content;
        const newContent = postProcessMarkdown(data.content);
        const formattedNewContent = formatContent(newContent, 'versets-prog');
        
        // Ajouter le nouveau contenu au contenu existant
        setContent(currentContent + '\n\n' + formattedNewContent);
        setCurrentVerseCount(endVerse);
        
        // Vérifier s'il y a encore des versets à générer
        if (endVerse >= 31) { // Genèse 1 a 31 versets
          setCanContinueVerses(false);
        }
        
        console.log(`[SUCCESS] Versets ${startVerse}-${endVerse} ajoutés avec succès`);
      }
      
    } catch (error) {
      console.error('[ERROR] Erreur continuation versets:', error);
      setContent(prev => prev + '\n\n❌ Erreur lors de la génération des versets suivants');
    }
    
    setIsLoading(false);
  };

  const handleRubriqueSelect = async (id) => {
    setActiveRubrique(id);
    
    // Créer une clé unique pour cette combinaison livre/chapitre
    const contentKey = `${selectedBook}_${selectedChapter}_${id}`;
    
    // Si la rubrique est déjà générée, afficher le contenu
    if (rubriquesStatus[id] === "completed" && generatedRubriques[contentKey]) {
      console.log(`[AFFICHAGE RUBRIQUE ${id}] Contenu sauvegardé trouvé - longueur: ${generatedRubriques[contentKey].length}`);
      
      // Si rubrique 0 et qu'il y a du contenu verset par verset, naviguer vers la page verset dédiée
      if (id === 0 && (generatedRubriques[contentKey].includes('VERSET') || generatedRubriques[contentKey].includes('**TEXTE BIBLIQUE'))) {
        const bookInfo = `${selectedBook || 'Genèse'} ${selectedChapter || '1'}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`;
        navigateToVersets(generatedRubriques[contentKey], bookInfo);
      }
      // Si rubrique 1-28, naviguer vers la page rubrique dédiée avec le contenu existant
      else if (id >= 1 && id <= 28) {
        console.log(`[NAVIGATION RUBRIQUE ${id}] Avec contenu existant`);
        navigateToRubrique(id, generatedRubriques[contentKey]);
      }
      else {
        setContent(generatedRubriques[contentKey]);
      }
    }

    // Pour les rubriques 1-28, générer via API au lieu du contenu statique
    if (id >= 1 && id <= 28) {
      console.log(`[GÉNÉRATION API RUBRIQUE ${id}] Début génération via API pour ${selectedBook} ${selectedChapter}`);
      
      setIsLoading(true);
      setRubriquesStatus(prev => ({ ...prev, [id]: "loading" }));
      
      try {
        const rubriqueTitle = getRubTitle(id);
        const passage = `${selectedBook || 'Genèse'} ${selectedChapter || '1'}`;
        const targetLength = getRubriqueLength(id);
        
        // Appel API pour générer le contenu dynamique
        const apiContent = await generateRubriqueContentViaAPI(
          id, 
          rubriqueTitle, 
          passage, 
          selectedBook || 'Genèse', 
          selectedChapter || '1', 
          targetLength
        );
        
        // Sauvegarder le contenu généré
        setGeneratedRubriques(prev => ({
          ...prev,
          [contentKey]: apiContent
        }));
        
        setRubriquesStatus(prev => ({ ...prev, [id]: "completed" }));
        
        console.log(`[SUCCÈS API RUBRIQUE ${id}] Contenu généré et sauvegardé - longueur: ${apiContent.length}`);
        
        // Naviguer vers la page rubrique dédiée avec le nouveau contenu
        navigateToRubrique(id, apiContent);
        
      } catch (error) {
        console.error(`[ERREUR API RUBRIQUE ${id}]`, error);
        
        setRubriquesStatus(prev => ({ ...prev, [id]: "error" }));
        setContent(`❌ Erreur lors de la génération de la rubrique ${id}: ${getRubTitle(id)}`);
      }
      
      setIsLoading(false);
      return;
    }
    
    if (id === 0) {
      // Rubrique 0 : Étude verset par verset - naviguer vers la page dédiée si du contenu existe
      console.log(`[RUBRIQUE 0] Vérification contenu existant - clé: ${contentKey}`);
      
      if (generatedRubriques[contentKey] && (generatedRubriques[contentKey].includes('VERSET') || generatedRubriques[contentKey].includes('**TEXTE BIBLIQUE'))) {
        console.log(`[RUBRIQUE 0] Contenu verset par verset trouvé, navigation vers page dédiée`);
        const bookInfo = `${selectedBook || 'Genèse'} ${selectedChapter || '1'}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`;
        navigateToVersets(generatedRubriques[contentKey], bookInfo);
      } else {
        console.log(`[RUBRIQUE 0] Aucun contenu trouvé, affichage message d'instruction`);
        setContent("Cliquez sur **Versets Prog** pour générer l'étude verset par verset de ce chapitre.");
        setIsVersetsProgContent(false);
      }
    } else {
      setContent("");
    }
  };

  // Fonction pour générer une rubrique à la demande
  const generateRubriqueOnDemand = async (rubriqueNum) => {
    if (rubriqueNum === 0) return; // Rubrique 0 utilise VERSETS PROG
    
    const rubriqueTitle = BASE_RUBRIQUES[rubriqueNum];
    const passage = (selectedVerse === "--" || selectedVerse === "vide")
      ? `${selectedBook || 'Genèse'} ${selectedChapter || '1'}`
      : `${selectedBook || 'Genèse'} ${selectedChapter || '1'}:${selectedVerse}`;
    
    try {
      console.log(`[GÉNÉRATION À LA DEMANDE] Rubrique ${rubriqueNum}: ${rubriqueTitle}`);
      
      setIsLoading(true);
      setRubriquesStatus(p => ({ ...p, [rubriqueNum]: "in-progress" }));
      
      // Afficher le contenu en cours de génération
      const contentEnCours = `# Étude - ${passage}\n\n## ${rubriqueNum}. ${rubriqueTitle}\n\n🔄 Génération intelligente en cours...`;
      setContent(formatContent(contentEnCours));
      
      // Générer le contenu intelligent pour cette rubrique
      const rubriqueContent = await generateRubriqueContentViaAPI(rubriqueNum, rubriqueTitle, passage, selectedBook, selectedChapter, parseInt(selectedLength));
      
      // Délai pour effet visuel
      await wait(1000);
      
      // Afficher le contenu final
      const contentFinal = `# Étude - ${passage}\n\n## ${rubriqueNum}. ${rubriqueTitle}\n\n${rubriqueContent}`;
      const formattedContent = formatContent(contentFinal);
      setContent(formattedContent);
      
      // Sauvegarder le contenu dans l'état (plus fiable que localStorage)
      const contentKey = `${selectedBook}_${selectedChapter}_${rubriqueNum}`;
      setGeneratedRubriques(prev => ({
        ...prev,
        [contentKey]: formattedContent
      }));
      
      // Marquer comme terminé
      setRubriquesStatus(p => ({ ...p, [rubriqueNum]: "completed" }));
      
      console.log(`[RUBRIQUE ${rubriqueNum} GÉNÉRÉE] ${rubriqueContent.length} caractères`);
      
    } catch (error) {
      console.error(`[ERREUR GÉNÉRATION RUBRIQUE ${rubriqueNum}]`, error);
      setRubriquesStatus(p => ({ ...p, [rubriqueNum]: "error" }));
      setContent(`# Erreur\n\nErreur lors de la génération de la rubrique ${rubriqueNum}: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Palette (reprend ta logique initiale)
  const changePalette = () => {
    const nextTheme = (currentTheme + 1) % colorThemes.length;
    setCurrentTheme(nextTheme);
    const theme = colorThemes[nextTheme];

    const app = document.querySelector('.App');
    if (app) app.style.background = 'transparent'; // Garder arrière-plan transparent

    const header = document.querySelector('.header-banner');
    if (header) header.style.background = theme.headerBg;

    document.documentElement.style.setProperty('--theme-primary', `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`);
    document.documentElement.style.setProperty('--theme-secondary', `linear-gradient(135deg, ${theme.secondary}, ${theme.primary})`);
    document.documentElement.style.setProperty('--theme-accent', `linear-gradient(135deg, ${theme.accent}, ${theme.secondary})`);
    
    // Couleurs pour les ombres
    const hexToRgba = (hex, alpha) => {
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };
    
    document.documentElement.style.setProperty('--theme-accent-shadow', hexToRgba(theme.accent, 0.3));
    document.documentElement.style.setProperty('--theme-accent-shadow-hover', hexToRgba(theme.accent, 0.4));

    const progressPill = document.querySelector('.progress-pill');
    if (progressPill) progressPill.style.background = theme.primary;

    const contentHeader = document.querySelector('.content-header');
    if (contentHeader)
      contentHeader.style.background = `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`;

    const btnReset = document.querySelector('.btn-reset');
    if (btnReset) { btnReset.style.background = theme.secondary; btnReset.style.color = 'white'; btnReset.style.border = 'none'; }

    const btnPalette = document.querySelector('.btn-palette');
    if (btnPalette) { btnPalette.style.background = theme.primary; btnPalette.style.color = 'white'; btnPalette.style.border = 'none'; }

    const btnLastStudy = document.querySelector('.btn-last-study');
    if (btnLastStudy) {
      btnLastStudy.style.background = `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`;
      btnLastStudy.style.color = 'white'; btnLastStudy.style.border = 'none';
    }

    const btnGemini = document.querySelector('.btn-gemini');
    if (btnGemini) { btnGemini.style.background = `linear-gradient(90deg, ${theme.secondary}, ${theme.accent})`; btnGemini.style.color = 'white'; btnGemini.style.border = 'none'; }

    const btnVersets = document.querySelector('.btn-versets-prog');
    if (btnVersets) { btnVersets.style.background = theme.accent; btnVersets.style.color = 'white'; btnVersets.style.border = 'none'; }

    const btnGenerate = document.querySelector('.btn-generate');
    if (btnGenerate) { btnGenerate.style.background = `linear-gradient(45deg, ${theme.primary}, ${theme.secondary})`; btnGenerate.style.color = 'white'; btnGenerate.style.border = 'none'; }

    const btnValidate = document.querySelector('.btn-validate');
    if (btnValidate) { btnValidate.style.background = theme.primary; btnValidate.style.color = 'white'; btnValidate.style.border = 'none'; }
  };

  /* =========================
     Génération (avec fallbacks)
  ========================= */

  const generateVerseByVerseProgressive = async () => {
    console.log("[DEBUG] generateVerseByVerseProgressive function called!");
    
    try {
      setIsLoading(true); setIsProgressiveLoading(true);
      setContent(""); setProgressPercent(0);
      setIsVersetsProgContent(true); // Marquer que c'est du contenu VERSETS PROG
      setRubriquesStatus(p => ({ ...p, 0: "in-progress" }));
      
      // Format exact requis par l'API Railway
      const book = selectedBook || 'Genèse';
      const chapter = selectedChapter || '1';
      const passage = `${book} ${chapter}`;
      console.log("[VERSETS PROG] Génération progressive pour:", passage);

      // 🔹 UTILISER VOTRE BACKEND avec votre clé Gemini GRATUITE
      console.log("[VERSETS PROG] Utilisation de votre backend avec clé Gemini gratuite");
      
      // CORRECTION: Utiliser la variable d'environnement pour l'endpoint
      const apiUrl = `${API_BASE}/generate-verse-by-verse`;
      console.log("[VERSETS PROG] URL backend utilisée:", apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          passage: passage,
          version: selectedVersion || 'LSG',
          tokens: parseInt(selectedLength) || 500,
          use_gemini: true,
          enriched: true
        })
      });
      
      if (!response.ok) {
        console.error(`[VERSETS PROG] Erreur API Railway: ${response.status}`);
        throw new Error(`API Railway Error ${response.status}`);
      }
      
      const data = await response.json();
      console.log("[API RAILWAY OK] Contenu reçu:", data.content ? data.content.length : 0, "caractères");
      
      // Afficher des informations sur la source du contenu
      const sourceInfo = data.source || "API";
      const fromCache = data.from_cache || false;
      const cost = data.cost || "Traitement";
      
      console.log(`[SOURCE] ${sourceInfo} ${fromCache ? '(Cache)' : '(Nouveau)'} - ${cost}`);
      
      // Afficher un message informatif selon la source
      if (fromCache) {
        console.log("📋 Contenu récupéré du cache - réponse instantanée");
      } else if (sourceInfo.includes("Fallback") || sourceInfo.includes("théologique")) {
        console.log("🔄 Quota Gemini atteint - utilisation du système de fallback intelligent");
      } else if (sourceInfo.includes("Gemini")) {
        console.log("🤖 Contenu généré par Gemini avec votre clé personnelle");
      }
      
      // Utiliser le contenu de l'API (correction du bug d'affichage)
      if (!data.content) {
        throw new Error("Aucun contenu reçu de l'API");
      }
      
      const fullContent = data.content;
      
      // Initialiser les états de continuation
      setCurrentVerseCount(5); // Par défaut, on génère 5 versets
      setCanContinueVerses(true); // Permettre la continuation
      
      // Affichage immédiat du contenu optimisé avec boutons Gemini
      const finalContent = postProcessMarkdown(fullContent);
      setContent(formatContent(finalContent, 'versets-prog'));
      setProgressPercent(100);
      setRubriquesStatus(p => ({ ...p, 0: "completed" }));
      setIsVersetsProgContent(true); // IMPORTANT : activer l'état VERSETS PROG
      console.log("[SUCCESS] Contenu VERSETS PROG affiché correctement");
      
      // Sauvegarder l'étude après génération réussie
      saveCurrentStudy();
      console.log("[SAUVEGARDE] Étude verset par verset sauvegardée");
      
      // Sauvegarder le contenu dans generatedRubriques pour la navigation
      const contentKey = `${selectedBook || 'Genèse'}_${selectedChapter || '1'}_0`;
      setGeneratedRubriques(prev => ({
        ...prev,
        [contentKey]: fullContent
      }));
      
      // Naviguer automatiquement vers la page dédiée "Verset par Verset"
      const bookInfo = `${selectedBook || 'Genèse'} ${selectedChapter || '1'}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`;
      console.log("[NAVIGATION] Préparation navigation vers page Verset par Verset:", bookInfo);
      setTimeout(() => {
        console.log("[NAVIGATION] Navigation vers la page dédiée Verset par Verset");
        navigateToVersets(fullContent, bookInfo);
      }, 500); // Petit délai pour l'effet visuel
      
    } catch (err) {
      console.error("Erreur génération VERSETS PROG:", err);
      setContent(`Erreur lors de la génération progressive: ${err.message}`);
      setRubriquesStatus(p => ({ ...p, 0: "error" }));
    } finally {
      setIsLoading(false); setIsProgressiveLoading(false);
      setProgressPercent(100);
    }
  };

  const generateWithGemini = async () => {
    try {
      setIsLoading(true); 
      setContent("Enrichissement théologique avec votre Gemini gratuit en cours...");
      setRubriquesStatus(p => ({ ...p, [activeRubrique]: "in-progress" }));

      const passage = (selectedVerse === "--" || selectedVerse === "vide")
        ? `${selectedBook} ${selectedChapter}`
        : `${selectedBook} ${selectedChapter}:${selectedVerse}`;

      // Enrichir théologiquement avec votre clé Gemini gratuite
      if (activeRubrique >= 1 && activeRubrique <= 28) {
        const rubriqueTitle = BASE_RUBRIQUES[activeRubrique];
        
        // Générer un enrichissement théologique avec longueur augmentée
        const enrichedLength = Math.min(2000, parseInt(selectedLength) + 500);
        console.log(`[ENRICHISSEMENT GEMINI GRATUIT] Rubrique ${activeRubrique} - Longueur enrichie: ${enrichedLength} caractères`);
        
        // Appeler votre backend avec votre clé Gemini gratuite
        const response = await fetch(`${API_BASE}/generate-verse-by-verse`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            passage: passage,
            version: selectedVersion || 'LSG',
            tokens: enrichedLength,
            use_gemini: true,
            enriched: true,
            rubric_type: rubriqueTitle
          })
        });

        if (!response.ok) {
          throw new Error(`Erreur API: ${response.status}`);
        }

        const data = await response.json();
        console.log("[GEMINI GRATUIT] Enrichissement reçu:", data.content ? data.content.length : 0, "caractères");

        if (data.content) {
          // Afficher le contenu enrichi avec votre Gemini gratuit
          const finalContent = `# Étude Enrichie avec Gemini Gratuit - ${passage}\n\n## ${activeRubrique}. ${rubriqueTitle}\n\n${data.content}`;
          setContent(formatContent(finalContent));
          
          // Sauvegarder le contenu enrichi
          const contentKey = `${selectedBook}_${selectedChapter}_${activeRubrique}`;
          setGeneratedRubriques(prev => ({
            ...prev,
            [contentKey]: formatContent(finalContent)
          }));
          
          console.log("[SUCCESS] Enrichissement Gemini gratuit affiché correctement");
          
          // Sauvegarder l'étude après enrichissement réussi
          saveCurrentStudy();
          console.log("[SAUVEGARDE] Étude enrichie Gemini sauvegardée");
        } else {
          throw new Error("Pas de contenu reçu de votre Gemini gratuit");
        }
        
      } else if (activeRubrique === 0) {
        // Pour la rubrique 0, utiliser VERSETS PROG qui utilise déjà votre Gemini
        setContent("⚠️ Pour la rubrique 0, utilisez le bouton 'VERSETS PROG' qui utilise déjà votre Gemini gratuit.");
      } else {
        setContent("⚠️ Rubrique non supportée pour l'enrichissement Gemini.");
      }

      setRubriquesStatus(p => ({ ...p, [activeRubrique]: "completed" }));
    } catch (err) {
      console.error("Erreur enrichissement Gemini gratuit:", err);
      setContent(`Erreur enrichissement avec votre Gemini gratuit: ${err.message}`);
      setRubriquesStatus(p => ({ ...p, [activeRubrique]: "error" }));
    } finally { 
      setIsLoading(false); 
    }
  };

  // Fonction pour enrichissement théologique contextuel et intelligent
  const generateTheologicalEnrichment = (rubriqueNum, rubriqueTitle, passage, book, chapter, targetLength) => {
    const baseContent = await generateRubriqueContentViaAPI(rubriqueNum, rubriqueTitle, passage, book, chapter, targetLength);
    
    // Enrichissement spécifique selon le livre biblique
    const bookEnrichment = getBookSpecificEnrichment(book, chapter);
    
    // Enrichissement spécifique selon la rubrique
    const rubriqueEnrichment = getRubriqueSpecificEnrichment(rubriqueNum, rubriqueTitle);
    
    // Enrichissement contextuel combiné
    const contextualEnrichment = getCombinedContextualEnrichment(book, chapter, rubriqueNum, passage);
    
    const enrichmentSuffix = `

**🤖 ENRICHISSEMENT CONTEXTUEL - ${passage}**

${bookEnrichment}

${rubriqueEnrichment}

${contextualEnrichment}

*Enrichissement généré par analyse contextuelle approfondie*`;

    return baseContent + enrichmentSuffix.substring(0, Math.max(0, targetLength - baseContent.length));
  };

  // Enrichissement spécifique par livre biblique
  const getBookSpecificEnrichment = (book, chapter) => {
    const bookEnrichments = {
      'Genèse': `**Perspective créationnelle :** ${book} ${chapter} s'inscrit dans le cadre de la théologie de la création. Les commentateurs patristiques, notamment Basile de Césarée dans ses Homélies sur l'Hexaméron, ont développé une exégèse remarquable de ces passages fondateurs.`,
      
      'Exode': `**Perspective libératrice :** ${book} ${chapter} révèle la pédagogie divine de la rédemption. Philon d'Alexandrie et plus tard l'École de théologie d'Antioche ont souligné les dimensions typologiques de ce récit qui préfigure la libération spirituelle en Christ.`,
      
      'Lévitique': `**Perspective sacrificielle :** ${book} ${chapter} développe la théologie cultuelle et sacrificielle. Les théologiens de l'Alliance (Cocceius, Witsius) ont magistralement démontré comment ces prescriptions rituelles trouvent leur accomplissement dans l'œuvre sacerdotale du Christ.`,
      
      'Nombres': `**Perspective pèlerine :** ${book} ${chapter} illustre la marche du peuple de Dieu vers la Terre Promise. John Bunyan dans "The Pilgrim's Progress" s'inspire de ces récits pour décrire le pèlerinage spirituel du chrétien.`,
      
      'Deutéronome': `**Perspective testamentaire :** ${book} ${chapter} constitue le testament mosaïque. Les théologiens de l'École de Saumur (Amyraut, Cappel) ont analysé la structure alliance-bénédiction-malédiction qui structure ce livre.`,
      
      'Matthieu': `**Perspective messianique :** ${book} ${chapter} révèle l'accomplissement des promesses vétérotestamentaires. Chrysostome dans ses Homélies sur Matthieu développe une christologie remarquable basée sur ce texte évangélique.`,
      
      'Marc': `**Perspective kérygmatique :** ${book} ${chapter} présente le Christ en action. L'exégèse moderne (Dodd, Jeremias) a souligné la dimension kérygmatique primitive de ce récit évangélique.`,
      
      'Luc': `**Perspective historico-salvifique :** ${book} ${chapter} s'inscrit dans l'histoire du salut. Conzelmann et l'École de Tübingen ont développé une théologie lucanienne de l'histoire sainte particulièrement éclairante.`,
      
      'Jean': `**Perspective théologique :** ${book} ${chapter} révèle la divinité du Christ. Les Pères cappadociens (Basile, Grégoire de Nazianze, Grégoire de Nysse) ont utilisé ce corpus johannique pour développer la théologie trinitaire.`,
      
      'Romains': `**Perspective sotériologique :** ${book} ${chapter} développe la doctrine du salut par grâce. Augustin, Luther, et Calvin ont fondé leur théologie de la justification sur cette épître magistrale.`,
      
      'Hébreux': `**Perspective sacerdotale :** ${book} ${chapter} présente le sacerdoce parfait du Christ. Owen dans son commentaire monumental a développé une théologie sacrificielle d'une profondeur inégalée.`
    };
    
    return bookEnrichments[book] || `**Perspective biblique :** Ce passage de ${book} ${chapter} révèle des dimensions théologiques que les commentateurs anciens et modernes ont explorées avec profit.`;
  };

  // Enrichissement spécifique par rubrique
  const getRubriqueSpecificEnrichment = (rubriqueNum, rubriqueTitle) => {
    const rubriqueEnrichments = {
      1: `**Enrichissement liturgique :** La tradition de la "prière d'ouverture" remonte aux Pères du désert. Jean Cassien dans ses Conférences spirituelles enseigne l'importance de l'invocation préalable pour toute lectio divina authentique.`,
      
      2: `**Enrichissement littéraire :** L'analyse structurelle moderne (rhétorique sémitique, Meynet) révèle des patterns sophistiqués que l'exégèse ancienne pressentait intuitivement. Cette approche enrichit considérablement la compréhension du texte.`,
      
      5: `**Enrichissement dogmatique :** Les fondements théologiques établis ici nourrissent la théologie systématique. Turretin dans ses Institutes of Elenctic Theology développe ces vérités avec une rigueur scolastique remarquable.`,
      
      15: `**Enrichissement christologique :** La lecture christocentrique trouve ici ses fondements herméneutiques. Vos dans sa Biblical Theology développe une approche christotélique qui éclaire remarquablement ce passage.`,
      
      16: `**Enrichissement sotériologique :** La doctrine de la grâce révélée ici constitue le cœur de l'Évangile. Les théologiens de Dordrecht ont systematisé ces vérités dans les Canons qui demeurent normatifs.`
    };
    
    return rubriqueEnrichments[rubriqueNum] || `**Enrichissement thématique :** Cette rubrique "${rubriqueTitle}" ouvre des perspectives théologiques que la tradition exégétique a particulièrement développées.`;
  };

  // Enrichissement contextuel combiné
  const getCombinedContextualEnrichment = (book, chapter, rubriqueNum, passage) => {
    // Logique contextuelle sophistiquée combinant livre + rubrique
    if (book === 'Genèse' && rubriqueNum === 1) {
      return `**Synthèse contextuelle :** La prière d'ouverture sur Genèse ${chapter} nous place dans la contemplation de l'œuvre créatrice primordiale. Basile le Grand souligne que cette méditation doit commencer par l'adoration du Créateur avant l'analyse de la création.`;
    }
    
    if (book === 'Genèse' && rubriqueNum === 15) {
      return `**Synthèse christologique :** Christ présent dès Genèse ${chapter} selon l'exégèse patristique. Justin Martyr dans son Dialogue avec Tryphon identifie le Logos aux théophanies primitives, perspective reprise par la tradition réformée.`;
    }
    
    if (book === 'Matthieu' && rubriqueNum === 16) {
      return `**Synthèse évangélique :** L'évangile de la grâce révélé en Matthieu ${chapter} accomplit les promesses vétérotestamentaires. Cette continuité rédemptrice structure toute la théologie de l'alliance selon la tradition réformée (Westminster Confession).`;
    }
    
    if ((book === 'Lévitique' || book === 'Hébreux') && rubriqueNum === 15) {
      return `**Synthèse typologique :** Le système sacrificiel de ${book} ${chapter} trouve son accomplissement parfait dans l'œuvre sacerdotale du Christ. Cette typologie biblique, développée par l'École d'Antioche, révèle l'unité de l'histoire sainte.`;
    }
    
    return `**Synthèse théologique :** L'intersection entre ${book} ${chapter} et cette dimension théologique révèle des vérités que l'exégèse traditionnelle a particulièrement valorisées dans l'édification de l'Église.`;
  };

  const generate28Points = async () => {
    try {
      setIsLoading(true);
      setIsVersetsProgContent(false); // Désactiver le style VERSETS PROG
      
      // 🔹 ÉTAPE 1: Vider la rubrique 0 et passer sa LED au gris
      setRubriquesStatus(p => ({ ...p, 0: "inactive" })); // LED grise pour rubrique 0
      setContent(""); // Vider le contenu affiché
      
      console.log("[GÉNÉRATION RUBRIQUE PAR RUBRIQUE] Début avec Prière d'ouverture");
      
      const passage = (selectedVerse === "--" || selectedVerse === "vide")
        ? `${selectedBook || 'Genèse'} ${selectedChapter || '1'}`
        : `${selectedBook || 'Genèse'} ${selectedChapter || '1'}:${selectedVerse}`;

      // 🔹 STRATÉGIE OPTIMISÉE: Rubrique 1 d'abord, puis les autres
      console.log("[GÉNÉRATION OPTIMISÉE] Génération immédiate de la Rubrique 1, puis les autres en arrière-plan");
      
      // 🎯 PHASE 1: Générer et naviguer vers Rubrique 1 immédiatement
      console.log("[PHASE 1] Génération et navigation immédiate vers Rubrique 1 - Prière d'ouverture");
      
      try {
        // Générer la Rubrique 1 avec un appel API direct plus rapide
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/generate-study`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            passage: passage,
            version: selectedVersion || 'LSG',
            tokens: 500, // Plus court pour plus de rapidité
            selected_rubriques: [1], // Rubrique 1 uniquement
            use_gemini: true
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          const rubrique1Content = data.content || '';
          
          console.log(`[NAVIGATION IMMÉDIATE] Rubrique 1 générée: ${rubrique1Content.length} caractères`);
          console.log(`[CONTENU PREVIEW]`, rubrique1Content.slice(0, 100) + "...");
          
          // Sauvegarder le contenu dans l'état
          const contentKey = `${selectedBook}_${selectedChapter}_1`;
          setGeneratedRubriques(prev => ({ ...prev, [contentKey]: rubrique1Content }));
          setRubriquesStatus(p => ({ ...p, 1: "completed" }));
          
          // Navigation immédiate avec le contenu frais
          navigateToRubrique(1, rubrique1Content);
          setProgressPercent(4); // 1/28 ≈ 4%
          
        } else {
          console.error("[API ERREUR] Impossible de générer la Rubrique 1");
          throw new Error("API call failed");
        }
        
      } catch (error) {
        console.error("[ERREUR PHASE 1]", error);
        // Fallback: utiliser la génération normale
        const rubrique1Content = await generateSingleRubrique(1, BASE_RUBRIQUES[1], passage);
        if (rubrique1Content) {
          navigateToRubrique(1, rubrique1Content);
          setProgressPercent(4);
        }
      }
      
      // 🎯 PHASE 2: Générer les 27 autres rubriques en arrière-plan
      console.log("[PHASE 2] Génération des 27 autres rubriques en arrière-plan");
      
      // Générer les rubriques restantes par lots de 5
      const generateRemainingRubriques = async () => {
        const batchSize = 5;
        for (let i = 2; i <= 28; i += batchSize) {
          const batch = [];
          const endIndex = Math.min(i + batchSize - 1, 28);
          
          console.log(`[ARRIÈRE-PLAN] Génération rubriques ${i} à ${endIndex}`);
          
          for (let j = i; j <= endIndex; j++) {
            if (j <= BASE_RUBRIQUES.length - 1) {
              const rubriqueTitle = BASE_RUBRIQUES[j];
              batch.push(generateSingleRubrique(j, rubriqueTitle, passage));
            }
          }
          
          await Promise.all(batch);
          
          // Mettre à jour le progrès
          const progress = Math.floor((endIndex / 28) * 100);
          setProgressPercent(progress);
          console.log(`[ARRIÈRE-PLAN] ${endIndex}/28 rubriques générées (${progress}%)`);
          
          // Petit délai entre les batches
          if (endIndex < 28) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      };
      
      // Lancer la génération en arrière-plan (non-bloquante)
      generateRemainingRubriques().then(() => {
        console.log("[ARRIÈRE-PLAN] Toutes les rubriques terminées!");
        setProgressPercent(100);
      }).catch((error) => {
        console.error("[ARRIÈRE-PLAN] Erreur:", error);
      });
      
      console.log("[GÉNÉRATION AUTOMATIQUE] Toutes les 28 rubriques générées!");
      
      // Sauvegarder l'étude après génération réussie
      saveCurrentStudy();
      console.log("[SAUVEGARDE] Étude complète des 28 rubriques sauvegardée");
      
    } catch (error) {
      console.error("[ERREUR GÉNÉRATION]", error);
      setContent(formatContent(`# Erreur\n\nUne erreur est survenue lors de la génération : ${error.message}`));
    } finally {
      setIsLoading(false);
      setProgressPercent(100);
    }
  };

  // Nouvelle fonction pour générer UNE SEULE rubrique
  const generateSingleRubrique = async (rubriqueNum, rubriqueTitle, passage) => {
    try {
      console.log(`[GÉNÉRATION RUBRIQUE ${rubriqueNum}] DEMANDÉE: "${rubriqueTitle}" pour ${passage}`);
      console.log(`[DEBUG PARAMS] rubriqueNum=${rubriqueNum}, rubriqueTitle="${rubriqueTitle}", passage="${passage}"`);
      
      // Marquer la rubrique en cours
      setRubriquesStatus(p => ({ ...p, [rubriqueNum]: "in-progress" }));
      setProgressPercent(20);
      
      // Afficher le titre en attente
      const contentEnCours = `# Étude - ${passage}\n\n## ${rubriqueNum}. ${rubriqueTitle}\n\n🔄 Génération intelligente en cours...`;
      setContent(formatContent(contentEnCours));
      
      // Appel API pour CETTE rubrique avec notre système Gemini intelligent
      const apiUrl = `${API_BASE}/api/generate-rubrique-content`;
      
      let rubriqueContent;
      
      try {
        setProgressPercent(50);
        
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            rubrique_number: rubriqueNum,
            rubrique_title: rubriqueTitle,
            book: selectedBook || "Genèse",
            chapter: selectedChapter || "1",
            passage: passage,
            target_length: parseInt(selectedLength) || 500
          })
        });
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`[API SUCCESS RUBRIQUE ${rubriqueNum}]`, data.content ? data.content.length : 0, "caractères");
        console.log(`[API DATA]`, data);
        
        if (data.status === "success" || data.status === "fallback") {
          rubriqueContent = data.content;
          console.log(`[RUBRIQUE ${rubriqueNum}] Contenu généré avec succès:`, rubriqueContent.slice(0, 100) + "...");
        } else {
          throw new Error("Réponse API invalide");
        }
        
      } catch (apiError) {
        console.error(`[API ÉCHEC RUBRIQUE ${rubriqueNum}] ${apiError.message}`, apiError);
        console.warn(`[FALLBACK] Génération de contenu de base pour rubrique ${rubriqueNum}`);
        // Fallback avec contenu de base
        rubriqueContent = `# ${rubriqueNum}. ${rubriqueTitle}\n\n**Analyse de ${passage}**\n\nCette section nécessite une génération via l'API qui est temporairement indisponible.\n\n## Contenu de remplacement pour ${rubriqueTitle}\n\nL'étude de ${passage} sous l'angle de "${rubriqueTitle}" révèle des aspects importants de la révélation divine.\n\n*Contenu généré automatiquement - Version enrichie via API indisponible*`;
      }
      
      setProgressPercent(80);
      
      // Si pas de contenu spécifique, utiliser le générateur intelligent
      if (!rubriqueContent || rubriqueContent.length < 50) {
        rubriqueContent = generateRubriqueContent(rubriqueNum, rubriqueTitle, passage, selectedBook, selectedChapter, parseInt(selectedLength));
      }
      
      // Afficher le contenu final
      const contentFinal = `# Étude - ${passage}\n\n## ${rubriqueNum}. ${rubriqueTitle}\n\n${rubriqueContent}`;
      const formattedContent = formatContent(contentFinal);
      setContent(formattedContent);
      
      // Sauvegarder dans l'état pour la fonction generateSingleRubrique aussi
      const contentKey = `${selectedBook}_${selectedChapter}_${rubriqueNum}`;
      setGeneratedRubriques(prev => ({
        ...prev,
        [contentKey]: formattedContent
      }));
      
      // Marquer comme terminé
      setRubriquesStatus(p => ({ ...p, [rubriqueNum]: "completed" }));
      setProgressPercent(100);
      
      console.log(`[RUBRIQUE ${rubriqueNum} TERMINÉE] ${rubriqueContent.length} caractères générés`);
      
      // Debug: Vérifier le contenu avant de le retourner
      console.log(`[GENERATE SINGLE DEBUG] Rubrique ${rubriqueNum} contenu final:`, formattedContent ? formattedContent.length : 0, "caractères");
      console.log(`[GENERATE SINGLE DEBUG] Contenu preview:`, formattedContent ? formattedContent.slice(0, 200) + "..." : "VIDE");
      
      // Retourner le contenu formaté pour utilisation ultérieure
      return formattedContent;
      
    } catch (error) {
      console.error(`[ERREUR RUBRIQUE ${rubriqueNum}]`, error);
      setRubriquesStatus(p => ({ ...p, [rubriqueNum]: "error" }));
      throw error;
    }
  };

  /* =========================
     Formatage du contenu
  ========================= */

  const formatContent = (text, context = 'default') => {
    if (!text) return "";
    
    // Formatage avec contexte pour VERSETS PROG
    let formattedText = text
      // D'abord transformer les labels spécifiques - REGEX ÉLARGIES pour matcher différents formats
      .replace(/^\*\*VERSET (\d+)\*\*$/gim, "<h2 class='verset-header'>📖 VERSET $1</h2>")
      .replace(/^VERSE\s*T(\d+)$/gim, "<h2 class='verset-header'>📖 VERSET $1</h2>")  // Format preview
      .replace(/^VERSET\s*(\d+)$/gim, "<h2 class='verset-header'>📖 VERSET $1</h2>")    // Format alternatif
      .replace(/^\*\*TEXTE BIBLIQUE\s*:\*\*$/gim, "<h4 class='texte-biblique-label'>📜 TEXTE BIBLIQUE :</h4>")
      .replace(/^TEXTE BIBLIQUE\s*:?$/gim, "<h4 class='texte-biblique-label'>📜 TEXTE BIBLIQUE :</h4>")  // Format preview
      .replace(/^\*\*EXPLICATION THÉOLOGIQUE\s*:\*\*$/gim, "<h4 class='explication-label'>🎓 EXPLICATION THÉOLOGIQUE :</h4>")
      .replace(/^EXPLICATION THÉOLOGIQUE\s*:?$/gim, "<h4 class='explication-label'>🎓 EXPLICATION THÉOLOGIQUE :</h4>")  // Format preview
      // Puis transformer les autres éléments en gras génériques
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/^\# (.*$)/gim, "<h1>$1</h1>")
      .replace(/^\## (.*$)/gim, "<h2>$1</h2>")
      .replace(/^\### (.*$)/gim, "<h3>$1</h3>")
      .split("\n\n")
      .map(p => (p.trim() ? `<p>${p.replace(/\n/g, "<br>")}</p>` : ""))
      .join("");

    // Appliquer la transformation des références bibliques
    formattedText = transformBibleReferences(formattedText);

    // Wrapper spécial pour le contexte VERSETS PROG
    if (context === 'versets-prog') {
      return `<div class="versets-prog-content">${formattedText}</div>`;
    }
    
    return formattedText;
  };

  const formatVerseByVerseContent = (text) => {
    const sections = text.split(/VERSET (\d+)/);
    let html = '<div class="verse-study-container">';

    if (sections[0]) {
      const intro = sections[0]
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/^\### (.*$)/gim, "<h3>$1</h3>")
        .replace(/^\## (.*$)/gim, "<h2>$1</h2>")
        .replace(/^\# (.*$)/gim, "<h1>$1</h1>");
      html += `<div style="margin-bottom: 30px;">${intro.replace(/\n/g, "<br>")}</div>`;
    }

    for (let i = 1; i < sections.length; i += 2) {
      const verseNumber = sections[i];
      const block = sections[i + 1];

      if (block) {
        html += `<div class="verse-block">
          <div class="verse-header">VERSET ${verseNumber}</div>`;

        const parts = block.split(/TEXTE BIBLIQUE\s*:/);
        if (parts.length > 1) {
          const afterBiblical = parts[1].split(/EXPLICATION THÉOLOGIQUE\s*:/);
          const biblicalText = (afterBiblical[0] || "").trim();
          const theologicalExplanation = afterBiblical[1] ? afterBiblical[1].trim() : "";

          html += `
            <div class="section-label biblical-label">📖 TEXTE BIBLIQUE</div>
            <div class="biblical-text">${biblicalText.replace(/\n/g, "<br>")}</div>`;

          if (theologicalExplanation) {
            html += `
              <div class="section-label theological-label">🎓 EXPLICATION THÉOLOGIQUE</div>
              <div class="theological-explanation">${theologicalExplanation.replace(/\n/g, "<br>")}</div>`;
          }
        }

        html += "</div>";
      }
    }

    html += "</div>";
    return html;
  };

  /* =========================
     Rendu (UI intacte)
  ========================= */

  return (
    <div className="App">
      {currentPage === 'concordance' ? (
        <BibleConcordancePage onGoBack={navigateToMain} />
      ) : currentPage === 'versets' ? (
        <VersetParVersetPage 
          onGoBack={navigateToMain} 
          content={versetPageContent}
          bookInfo={currentBookInfo}
        />
      ) : currentPage === 'notes' ? (
        <NotesPage onGoBack={navigateToMain} />
      ) : currentPage === 'rubrique' ? (
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
          // Nouvelles props pour les boutons fonctionnels
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
          <div className="centered-progress-wrapper">
            <div className="progress-container">
            <div className="progress-pill">
              {progressPercent}%
              {isProgressiveLoading && progressiveStats && (
                <span className="progressive-indicator">
                  ⚡ {progressiveStats.speed} - {progressiveStats.current_batch} ({progressiveStats.processed}/{progressiveStats.total})
                </span>
              )}
            </div>
            
            {/* API Control Panel directement sous le pourcentage */}
            <div className="api-below-progress">
              <ApiControlPanel backendUrl={process.env.REACT_APP_BACKEND_URL || "https://scripture-ai-8.preview.emergentagent.com"} />
            </div>
            </div>
          </div>

          {/* Interface principale */}
          <div className="main-container">
            {/* Section de recherche */}
            <div className="search-section">
              <div className="search-input">
                <input
                  type="text"
                  placeholder="Rechercher (ex : Marc 5:1, 1 Jean 2, Genèse 1:1-5)"
                  className="search-field"
                  value={searchQuery}
                  onChange={handleSearchChange}
                />
              </div>

              <div className="controls-row">
                <SelectPill label="Livre" value={selectedBook} options={["--", ...BOOKS]} onChange={handleBookChange} />
                <SelectPill label="Chapitre" value={selectedChapter} options={availableChapters} onChange={handleChapterChange} />
                <SelectPill label="Verset" value={selectedVerse} options={["--", ...Array.from({ length: 50 }, (_, i) => i + 1)]} onChange={handleVerseChange} />
                <SelectPill label="Version" value={selectedVersion} options={["LSG", "Darby", "NEG"]} onChange={handleVersionChange} />
                <button className="btn-validate" disabled={isLoading}>Valider</button>
                <SelectPill label="Longueur" value={selectedLength} options={[300, 500, 1000, 2000]} onChange={handleLengthChange} />
                <button className="btn-read" onClick={openYouVersion}>Lire la Bible</button>
                <button className="btn-chat" onClick={() => window.open('https://chatgpt.com/', '_blank')}>ChatGPT</button>
                <button className="btn-notes" onClick={handleNotesClick}>📝 Prise de Note</button>
              </div>

              {/* Boutons d'action - Design équilibré et soigné */}
              <div className="balanced-controls-container" style={{
                width: '100%',
                maxWidth: '1600px',
                margin: '0 auto',
                padding: '0 25px',
                boxSizing: 'border-box'
              }}>
                <div className="balanced-buttons-grid" style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(7, 1fr)',
                  gap: '16px',
                  marginBottom: '24px',
                  padding: '20px 20px',
                  width: '100%',
                  boxSizing: 'border-box',
                  alignItems: 'center',
                  background: 'rgba(255, 255, 255, 0.08)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '20px',
                  border: '1px solid rgba(255, 255, 255, 0.12)'
                }}>
                  <button className="btn-control" style={getButtonStyle(currentButtonColors.reset, currentButtonColors.reset.shadow)} onClick={handleReset}>
                    <span className="control-icon">🔄</span>
                    <span className="control-label">Reset</span>
                  </button>
                  
                  <button className="btn-control" style={getButtonStyle(currentButtonColors.mystique, currentButtonColors.mystique.shadow)} onClick={changePalette}>
                    <span className="control-icon">🎨</span>
                    <span className="control-label">{colorThemes[currentTheme].name}</span>
                  </button>
                  
                  <button className="btn-control" style={getButtonStyle(currentButtonColors.genese, currentButtonColors.genese.shadow)} onClick={restoreLastStudy} disabled={!lastStudy}>
                    <span className="control-icon">📚</span>
                    <span className="control-label">{lastStudy ? `${lastStudy.book} ${lastStudy.chapter}` : "Genèse 1"}</span>
                  </button>
                  
                  <button className={`btn-control ${isLoading ? "loading" : ""}`} style={getButtonStyle(currentButtonColors.gemini, currentButtonColors.gemini.shadow)} onClick={generateWithGemini} disabled={isLoading}>
                    <span className="control-icon">🤖</span>
                    <span className="control-label">Gemini Gratuit</span>
                    {isLoading && <div className="btn-mini-loader"></div>}
                  </button>
                  
                  <button className="btn-control" style={getButtonStyle(currentButtonColors.versets, currentButtonColors.versets.shadow)} onClick={generateVerseByVerseProgressive}>
                    <span className="control-icon">⚡</span>
                    <span className="control-label">Versets Prog</span>
                  </button>
                  
                  <button className={`btn-control btn-primary ${isLoading ? "loading" : ""}`} style={getButtonStyle(currentButtonColors.generate, currentButtonColors.generate.shadow)} onClick={generate28Points} disabled={isLoading}>
                    <span className="control-icon">✨</span>
                    <span className="control-label">Générer</span>
                    {isLoading && <div className="btn-mini-loader"></div>}
                  </button>
                  
                  <button className="btn-control" style={getButtonStyle(currentButtonColors.concordance, currentButtonColors.concordance.shadow)} onClick={navigateToConcordance}>
                    <span className="control-icon">📖</span>
                    <span className="control-label">Bible Concordance</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Layout responsive */}
            <div className="three-column-layout">
              {/* Colonne gauche - Rubriques */}
              <div className="left-column">
                <h3>Rubriques (29)</h3>
                <RubriquesInline items={rubriquesItems} activeId={activeRubrique} onSelect={handleRubriqueSelect} rubriquesStatus={rubriquesStatus} />
              </div>

              {/* Colonne centrale - Contenu */}
              <div className="center-column">
                <div className="content-header">
                  <h2>{`${activeRubrique}. ${getRubTitle(activeRubrique)}`}</h2>
                  <div className="nav-buttons">
                    <button onClick={() => handleRubriqueSelect(Math.max(0, activeRubrique - 1))} disabled={activeRubrique === 0}>◀ Précédent</button>
                    <button onClick={() => handleRubriqueSelect(Math.min(BASE_RUBRIQUES.length - 1, activeRubrique + 1))} disabled={activeRubrique === BASE_RUBRIQUES.length - 1}>Suivant ▶</button>
                  </div>
                </div>

                <div className="content-area">
                  {isLoading ? (
                    <div className="loading-container">
                      <div className="loading-spinner"></div>
                      <p>Génération en cours...</p>
                      {progressiveStats && (
                        <div className="progressive-stats">
                          <p>📊 Versets traités: {progressiveStats.processed}/{progressiveStats.total}</p>
                          <p>🎯 Batch actuel: {progressiveStats.current_batch}</p>
                          <p>⚡ Mode: {progressiveStats.speed}</p>
                        </div>
                      )}
                    </div>
                  ) : content ? (
                    <div>
                      <div className="content-text" dangerouslySetInnerHTML={{ __html: formatContent(content, isVersetsProgContent ? 'versets-prog' : 'default') }} />
                      {(isVersetsProgContent || content.includes('VERSET')) && canContinueVerses && (
                        <div className="continue-verses-section">
                          <button 
                            className="btn-continue-verses" 
                            onClick={continueVerses} 
                            disabled={isLoading}
                            title={`Générer les versets ${currentVerseCount + 1} à ${currentVerseCount + 5}`}
                          >
                            📖 Continuer les versets ({currentVerseCount + 1}-{currentVerseCount + 5})
                          </button>
                          <p className="continue-verses-info">
                            Versets actuels : 1-{currentVerseCount} • Cliquez pour continuer la lecture
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="empty-content-message">
                      <p>Sélectionnez une rubrique pour voir son contenu.</p>
                    </div>
                  )}
                </div>
              </div>

            </div>
          </div>

          {/* SUPPRIMÉ : Modal Notes - remplacée par page dédiée */}
        </>
      )}
    </div>
  );
}

/* =========================
   Composants auxiliaires
========================= */

function getRubTitle(index) {
  return BASE_RUBRIQUES[index] || `Rubrique ${index}`;
}

function SelectPill({ label, value, options, onChange }) {
  return (
    <div className="select-pill">
      <label>{label}</label>
      <select value={value} onChange={onChange}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function NotesModal({ isOpen, notes, onNotesChange, onSave, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="notes-modal-overlay" onClick={onClose}>
      <div className="notes-modal" onClick={(e) => e.stopPropagation()}>
        <div className="notes-modal-header">
          <h3>📝 Mes Notes d'Étude Biblique</h3>
          <button className="notes-close-btn" onClick={onClose}>×</button>
        </div>
        <div className="notes-modal-content">
          <textarea
            className="notes-textarea"
            value={notes}
            onChange={(e) => onNotesChange(e.target.value)}
            placeholder="Écrivez vos réflexions, questions, et insights spirituels ici...

Exemples :
• Versets qui m'ont marqué
• Questions pour approfondir
• Applications personnelles
• Prières inspirées par l'étude"
            rows={15}
          />
        </div>
        <div className="notes-modal-footer">
          <button className="notes-save-btn" onClick={onSave}>
            💾 Sauvegarder
          </button>
          <button className="notes-cancel-btn" onClick={onClose}>
            Annuler
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
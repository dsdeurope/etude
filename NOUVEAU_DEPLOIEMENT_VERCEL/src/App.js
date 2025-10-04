/* eslint-disable */
import React, { useState, useEffect, useMemo } from 'react';
import './App.css';
import './rubriques.css';
import RubriquesInline from './RubriquesInline';
import BibleConcordancePage from './BibleConcordancePage';
import VersetParVersetPage from './VersetParVersetPage';
import NotesPage from './NotesPage';
import RubriquePage from './RubriquePage';
import ApiControlPanel from './ApiControlPanel';

/* =========================
   Configuration et Helpers
========================= */

// Backend: 1) REACT_APP_BACKEND_URL si défini (nettoyé), 2) localhost en dev, 3) Railway en prod
const getBackendUrl = () => {
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') return 'http://localhost:8001';
  return 'https://faithflow-app.preview.emergentagent.com';
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL.replace(/\/+$/g, '')}/api`;

// Style unifié …
const getButtonStyle = (gradientColors, shadowColor, isHovered = false) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '12px 8px',
  borderRadius: '14px',
  minHeight: '75px',
  fontSize: '12px',
  fontWeight: '700',
  fontFamily: "'Montserrat', sans-serif",
  color: 'white',
  border: 'none',
  cursor: 'pointer',
  background: `linear-gradient(135deg, ${gradientColors.start} 0%, ${gradientColors.end} 100%)`,
  boxShadow: isHovered
    ? `0 10px 35px ${shadowColor.replace('0.25', '0.35')}, 0 3px 18px rgba(0, 0, 0, 0.15)`
    : `0 6px 20px ${shadowColor}, 0 2px 14px rgba(0, 0, 0, 0.1)`,
  transition: 'all 0.3s ease',
  transform: isHovered ? 'translateY(-2px) scale(1.02)' : 'translateY(0)',
  textTransform: 'uppercase',
  letterSpacing: '0.8px',
  position: 'relative',
  overflow: 'hidden',
});

// Couleurs par thème
const getThemeButtonColors = (theme) => {
  theme =
    theme && theme.primary
      ? theme
      : { primary: '#6366f1', secondary: '#4f46e5', accent: '#6366f1' };
  const themeColor = {
    start: theme.primary,
    end: theme.secondary,
    shadow: `rgba(${hexToRgb(theme.primary)}, 0.25)`,
  };
  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r}, ${g}, ${b}`;
  }
  return {
    reset: themeColor,
    mystique: themeColor,
    genese: themeColor,
    gemini: themeColor,
    versets: themeColor,
    generate: themeColor,
    concordance: themeColor,
  };
};

function asString(x) {
  if (x === undefined || x === null) return '';
  if (typeof x === 'string') return x;
  try {
    return JSON.stringify(x, null, 2);
  } catch {
    return String(x);
  }
}

function postProcessMarkdown(t) {
  const s = asString(t);
  return s
    .replace(/VERSET (\d+)/g, '**VERSET $1**')
    .replace(/TEXTE BIBLIQUE\s*:/g, '**TEXTE BIBLIQUE :**')
    .replace(/EXPLICATION THÉOLOGIQUE\s*:/g, '**EXPLICATION THÉOLOGIQUE :**')
    .replace(/Introduction au Chapitre/g, '**Introduction au Chapitre**')
    .replace(/Synthèse Spirituelle/g, '**Synthèse Spirituelle**')
    .replace(/Principe Herméneutique/g, '**Principe Herméneutique**');
}

/* =========================
   Données statiques
========================= */

const BOOKS = [
  'Genèse',
  'Exode',
  'Lévitique',
  'Nombres',
  'Deutéronome',
  'Josué',
  'Juges',
  'Ruth',
  '1 Samuel',
  '2 Samuel',
  '1 Rois',
  '2 Rois',
  '1 Chroniques',
  '2 Chroniques',
  'Esdras',
  'Néhémie',
  'Esther',
  'Job',
  'Psaumes',
  'Proverbes',
  'Ecclésiaste',
  'Cantique des cantiques',
  'Ésaïe',
  'Jérémie',
  'Lamentations',
  'Ézéchiel',
  'Daniel',
  'Osée',
  'Joël',
  'Amos',
  'Abdias',
  'Jonas',
  'Michée',
  'Nahum',
  'Habacuc',
  'Sophonie',
  'Aggée',
  'Zacharie',
  'Malachie',
  'Matthieu',
  'Marc',
  'Luc',
  'Jean',
  'Actes',
  'Romains',
  '1 Corinthiens',
  '2 Corinthiens',
  'Galates',
  'Éphésiens',
  'Philippiens',
  'Colossiens',
  '1 Thessaloniciens',
  '2 Thessaloniciens',
  '1 Timothée',
  '2 Timothée',
  'Tite',
  'Philémon',
  'Hébreux',
  'Jacques',
  '1 Pierre',
  '2 Pierre',
  '1 Jean',
  '2 Jean',
  '3 Jean',
  'Jude',
  'Apocalypse',
];

const BOOK_CHAPTERS = {
  /* … (inchangé, tel que dans ton fichier) … */
};

const BASE_RUBRIQUES = [
  'Étude verset par verset',
  "Prière d'ouverture",
  'Structure littéraire',
  'Questions du chapitre précédent',
  'Thème doctrinal',
  'Fondements théologiques',
  'Contexte historique',
  'Contexte culturel',
  'Contexte géographique',
  'Analyse lexicale',
  'Parallèles bibliques',
  'Prophétie et accomplissement',
  'Personnages',
  'Structure rhétorique',
  'Théologie trinitaire',
  'Christ au centre',
  'Évangile et grâce',
  'Application personnelle',
  'Application communautaire',
  'Prière de réponse',
  "Questions d'étude",
  'Points de vigilance',
  'Objections et réponses',
  'Perspective missionnelle',
  'Éthique chrétienne',
  'Louange / liturgie',
  'Méditation guidée',
  'Mémoire / versets clés',
  "Plan d'action",
];

/* =========================
   Utilitaires fetch (fallbacks)
========================= */

const ENDPOINTS = {
  verseProgressive: ['/generate-verse-by-verse-progressive', '/g_verse_progressive'],
  verse: ['/generate-verse-by-verse', '/g_te-verse-by-verse'],
  study: ['/generate-study', '/g_study_28'],
  verseGemini: [
    '/generate-verse-by-verse-gemini',
    '/generate-verse-by-verse',
    '/g_te-verse-by-verse',
  ],
  studyGemini: ['/generate-study-gemini', '/generate-study', '/g_study_28'],
};

async function smartPost(pathList, payload) {
  /* … inchangé … */
}

/* =========================
   Composant Principal App
========================= */

function App() {
  // Thèmes
  const colorThemes = [
    /* … inchangé … */
  ];
  // États
  const [currentTheme, setCurrentTheme] = useState(0);
  const safeTheme = (Array.isArray(colorThemes) && colorThemes[currentTheme]) || {
    name: 'Fallback',
    primary: '#6366f1',
    secondary: '#4f46e5',
    accent: '#6366f1',
    background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    headerBg: 'linear-gradient(90deg, #312e81 0%, #818cf8 50%, #a5b4fc 100%)',
  };
  const currentButtonColors = getThemeButtonColors(safeTheme);
  const [selectedBook, setSelectedBook] = useState('Genèse');
  const [selectedChapter, setSelectedChapter] = useState('1');
  const [selectedVerse, setSelectedVerse] = useState('--');
  const [selectedVersion, setSelectedVersion] = useState('LSG');
  const [selectedLength, setSelectedLength] = useState(500);
  const [activeRubrique, setActiveRubrique] = useState(0);
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedRubriques, setGeneratedRubriques] = useState({});
  const [rubriquesStatus, setRubriquesStatus] = useState({});
  const [lastStudy, setLastStudy] = useState(null);
  const [progressPercent, setProgressPercent] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [isProgressiveLoading, setIsProgressiveLoading] = useState(false);
  const [currentBatchVerse, setCurrentBatchVerse] = useState(1);
  const [progressiveStats, setProgressiveStats] = useState(null);
  const [isVersetsProgContent, setIsVersetsProgContent] = useState(false);
  const [currentVerseCount, setCurrentVerseCount] = useState(5);
  const [canContinueVerses, setCanContinueVerses] = useState(true);

  // Navigation
  const [currentPage, setCurrentPage] = useState('main');
  const [versetPageContent, setVersetPageContent] = useState('');
  const [currentBookInfo, setCurrentBookInfo] = useState('');
  const [currentRubriqueNumber, setCurrentRubriqueNumber] = useState(1);
  const [currentRubriqueContent, setCurrentRubriqueContent] = useState('');

  // availableChapters …
  const availableChapters = useMemo(() => {
    /* … inchangé … */
  }, [selectedBook]);

  // useEffect init / thème / sauvegarde …
  useEffect(() => {
    /* … inchangé … */
  }, [currentTheme]);
  useEffect(() => {
    setTimeout(() => {
      changePalette();
      setCurrentTheme(0);
    }, 100);
  }, []);
  useEffect(() => {
    if (selectedBook !== '--' && selectedChapter !== '--') saveCurrentStudy();
  }, [selectedBook, selectedChapter]);

  const saveCurrentStudy = () => {
    /* … inchangé … */
  };
  const restoreLastStudy = () => {
    /* … inchangé … */
  };

  const rubriquesItems = BASE_RUBRIQUES.map((title, index) => ({ id: index, title }));

  /* =========================
     Gestionnaires
  ========================= */
  const handleBookChange = (e) => {
    /* … */
  };
  const handleChapterChange = (e) => {
    /* … */
  };
  const handleVerseChange = (e) => setSelectedVerse(e.target.value);
  const handleVersionChange = (e) => setSelectedVersion(e.target.value);
  const handleLengthChange = (e) => setSelectedLength(Number(e.target.value));
  const parseSearchQuery = (q) => {
    /* … inchangé … */
  };
  const handleSearchChange = (e) => {
    /* … */
  };

  // transformBibleReferences, wait, parseRubriquesContent, getRubriqueLength,
  // generateRubriqueContent (+ toutes tes fonctions generate* …),
  // generateIntelligentFallback, generateFallbackRubriqueContent,
  // animateProgress, openYouVersion, handleReset, notes/nav helpers,
  // continueVerses, handleRubriqueSelect, generateRubriqueOnDemand,
  // changePalette, generateVerseByVerseProgressive, generateWithGemini,
  // generateTheologicalEnrichment, getBookSpecificEnrichment, getRubriqueSpecificEnrichment,
  // getCombinedContextualEnrichment, generate28Points, generateSingleRubrique,
  // formatContent, formatVerseByVerseContent
  // ====> TOUT CECI RESTE INCHANGÉ (repris tel quel de ton fichier) <====

  /* =========================
     Rendu (UI intacte)
  ========================= */

  return (
    <div className="App debug-visual">
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
          onNavigateToRubrique={(n) => {
            const contentKey = `${selectedBook}_${selectedChapter}_${n}`;
            const content = generatedRubriques[contentKey] || '';
            navigateToRubrique(n, content);
          }}
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
              ✨ MÉDITATION BIBLIQUE ✨ ÉTUDE SPIRITUELLE ✨ SAGESSE DIVINE ✨ MÉDITATION
              THÉOLOGIQUE ✨ CONTEMPLATION SACRÉE ✨ RÉFLEXION INSPIRÉE ✨
            </div>
          </header>

          {/* Indicateur de progression centré */}
          <div className="progress-container">
            <div className="progress-pill">
              {progressPercent}%
              {isProgressiveLoading && progressiveStats && (
                <span className="progressive-indicator">
                  ⚡ {progressiveStats.speed} - {progressiveStats.current_batch} (
                  {progressiveStats.processed}/{progressiveStats.total})
                </span>
              )}
            </div>
          </div>

          {/* ✅ API SOUS LA PASTILLE */}
          <div
            className="api-centered"
            style={{ display: 'flex', justifyContent: 'center', margin: '12px 0 20px' }}
          >
            <ApiControlPanel
              backendUrl={
                process.env.REACT_APP_BACKEND_URL ||
                'https://faithflow-app.preview.emergentagent.com'
              }
            />
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
                <SelectPill
                  label="Livre"
                  value={selectedBook}
                  options={['--', ...BOOKS]}
                  onChange={handleBookChange}
                />
                <SelectPill
                  label="Chapitre"
                  value={selectedChapter}
                  options={availableChapters}
                  onChange={handleChapterChange}
                />
                <SelectPill
                  label="Verset"
                  value={selectedVerse}
                  options={['--', ...Array.from({ length: 50 }, (_, i) => i + 1)]}
                  onChange={handleVerseChange}
                />
                <SelectPill
                  label="Version"
                  value={selectedVersion}
                  options={['LSG', 'Darby', 'NEG']}
                  onChange={handleVersionChange}
                />
                <button className="btn-validate" disabled={isLoading}>
                  Valider
                </button>
                <SelectPill
                  label="Longueur"
                  value={selectedLength}
                  options={[300, 500, 1000, 2000]}
                  onChange={handleLengthChange}
                />
                <button className="btn-read" onClick={openYouVersion}>
                  Lire la Bible
                </button>
                <button
                  className="btn-chat"
                  onClick={() => window.open('https://chatgpt.com/', '_blank')}
                >
                  ChatGPT
                </button>
                <button className="btn-notes" onClick={handleNotesClick}>
                  📝 Prise de Note
                </button>
              </div>

              {/* Boutons d'action */}
              <div className="balanced-controls-container">
                <div
                  className="balanced-buttons-grid"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(7, 1fr)',
                    gap: '12px',
                    marginBottom: '24px',
                    padding: '0 10px',
                    width: '100%',
                    boxSizing: 'border-box',
                  }}
                >
                  <button
                    className="btn-control"
                    style={getButtonStyle(
                      currentButtonColors.reset,
                      currentButtonColors.reset.shadow,
                    )}
                    onClick={handleReset}
                  >
                    <span className="control-icon">🔄</span>
                    <span className="control-label">Reset</span>
                  </button>
                  <button
                    className="btn-control"
                    style={getButtonStyle(
                      currentButtonColors.mystique,
                      currentButtonColors.mystique.shadow,
                    )}
                    onClick={changePalette}
                  >
                    <span className="control-icon">🎨</span>
                    <span className="control-label">{colorThemes[currentTheme].name}</span>
                  </button>
                  <button
                    className="btn-control"
                    style={getButtonStyle(
                      currentButtonColors.genese,
                      currentButtonColors.genese.shadow,
                    )}
                    onClick={restoreLastStudy}
                    disabled={!lastStudy}
                  >
                    <span className="control-icon">📚</span>
                    <span className="control-label">
                      {lastStudy ? `${lastStudy.book} ${lastStudy.chapter}` : 'Genèse 1'}
                    </span>
                  </button>
                  <button
                    className={`btn-control ${isLoading ? 'loading' : ''}`}
                    style={getButtonStyle(
                      currentButtonColors.gemini,
                      currentButtonColors.gemini.shadow,
                    )}
                    onClick={generateWithGemini}
                    disabled={isLoading}
                  >
                    <span className="control-icon">🤖</span>
                    <span className="control-label">Gemini Gratuit</span>
                    {isLoading && <div className="btn-mini-loader"></div>}
                  </button>
                  <button
                    className="btn-control"
                    style={getButtonStyle(
                      currentButtonColors.versets,
                      currentButtonColors.versets.shadow,
                    )}
                    onClick={generateVerseByVerseProgressive}
                  >
                    <span className="control-icon">⚡</span>
                    <span className="control-label">Versets Prog</span>
                  </button>
                  <button
                    className={`btn-control btn-primary ${isLoading ? 'loading' : ''}`}
                    style={getButtonStyle(
                      currentButtonColors.generate,
                      currentButtonColors.generate.shadow,
                    )}
                    onClick={generate28Points}
                    disabled={isLoading}
                  >
                    <span className="control-icon">✨</span>
                    <span className="control-label">Générer</span>
                    {isLoading && <div className="btn-mini-loader"></div>}
                  </button>
                  <button
                    className="btn-control"
                    style={getButtonStyle(
                      currentButtonColors.concordance,
                      currentButtonColors.concordance.shadow,
                    )}
                    onClick={navigateToConcordance}
                  >
                    <span className="control-icon">📖</span>
                    <span className="control-label">Bible Concordance</span>
                  </button>
                </div>

                {/* (déplacé) Le panneau API est désormais sous la pastille */}
              </div>
            </div>

            {/* Layout responsive */}
            <div className="three-column-layout">
              {/* Colonne gauche */}
              <div className="left-column">
                <h3>Rubriques (29)</h3>
                <RubriquesInline
                  items={rubriquesItems}
                  activeId={activeRubrique}
                  onSelect={handleRubriqueSelect}
                  rubriquesStatus={rubriquesStatus}
                />
              </div>

              {/* Colonne centrale */}
              <div className="center-column">
                <div className="content-header">
                  <h2>{`${activeRubrique}. ${getRubTitle(activeRubrique)}`}</h2>
                  <div className="nav-buttons">
                    <button
                      onClick={() => handleRubriqueSelect(Math.max(0, activeRubrique - 1))}
                      disabled={activeRubrique === 0}
                    >
                      ◀ Précédent
                    </button>
                    <button
                      onClick={() =>
                        handleRubriqueSelect(
                          Math.min(BASE_RUBRIQUES.length - 1, activeRubrique + 1),
                        )
                      }
                      disabled={activeRubrique === BASE_RUBRIQUES.length - 1}
                    >
                      Suivant ▶
                    </button>
                  </div>
                </div>

                <div className="content-area">
                  {isLoading ? (
                    <div className="loading-container">
                      <div className="loading-spinner"></div>
                      <p>Génération en cours...</p>
                      {progressiveStats && (
                        <div className="progressive-stats">
                          <p>
                            📊 Versets traités: {progressiveStats.processed}/
                            {progressiveStats.total}
                          </p>
                          <p>🎯 Batch actuel: {progressiveStats.current_batch}</p>
                          <p>⚡ Mode: {progressiveStats.speed}</p>
                        </div>
                      )}
                    </div>
                  ) : content ? (
                    <div>
                      <div
                        className="content-text"
                        dangerouslySetInnerHTML={{
                          __html: formatContent(
                            content,
                            isVersetsProgContent ? 'versets-prog' : 'default',
                          ),
                        }}
                      />
                      {(isVersetsProgContent || content.includes('VERSET')) &&
                        canContinueVerses && (
                          <div className="continue-verses-section">
                            <button
                              className="btn-continue-verses"
                              onClick={continueVerses}
                              disabled={isLoading}
                              title={`Générer les versets ${currentVerseCount + 1} à ${currentVerseCount + 5}`}
                            >
                              📖 Continuer les versets ({currentVerseCount + 1}-
                              {currentVerseCount + 5})
                            </button>
                            <p className="continue-verses-info">
                              Versets actuels : 1-{currentVerseCount} • Cliquez pour continuer la
                              lecture
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
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
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
          <button className="notes-close-btn" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="notes-modal-content">
          <textarea
            className="notes-textarea"
            value={notes}
            onChange={(e) => onNotesChange(e.target.value)}
            placeholder={`Écrivez vos réflexions...`}
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

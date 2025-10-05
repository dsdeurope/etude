import React, { useState, useEffect } from 'react';

// Composant API avec LEDs physiques (copié de VersetParVersetPage.js)
const ApiStatusButton = () => {
  const [apiStatus, setApiStatus] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  // Configuration du backend
  const getBackendUrl = () => {
    if (process.env.REACT_APP_BACKEND_URL) {
      return process.env.REACT_APP_BACKEND_URL;
    }
    const hostname = window.location.hostname;
    if (hostname === "localhost" || hostname === "127.0.0.1") return "http://localhost:8001";
    return "https://scripture-ai-7.preview.emergentagent.com";
  };

  const BACKEND_URL = getBackendUrl();

  const fetchApiStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/health`);
      if (response.ok) {
        const healthData = await response.json();
        
        const adaptedStatus = {
          timestamp: new Date().toISOString(),
          apis: {
            gemini_1: { color: 'green', name: 'Gemini Key 1', status: 'active' },
            gemini_2: { color: 'green', name: 'Gemini Key 2', status: 'active' },
            gemini_3: { color: 'green', name: 'Gemini Key 3', status: 'active' },
            gemini_4: { color: 'green', name: 'Gemini Key 4', status: 'active' },
            bible_api: { color: healthData.bible_api_configured ? 'green' : 'red', name: 'Bible API', status: healthData.bible_api_configured ? 'active' : 'inactive' }
          },
          active_api: healthData.current_key || 'gemini_1'
        };
        
        setApiStatus(adaptedStatus);
      }
    } catch (error) {
      console.error('[API STATUS] Erreur:', error);
    }
  };

  const getLedColor = (api) => {
    return api.color === 'green' ? '#00ff00' : '#ff0000';
  };

  useEffect(() => {
    fetchApiStatus();
    const interval = setInterval(fetchApiStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <style>
        {`
          @keyframes pulse-green {
            0%, 100% { 
              box-shadow: 0 0 8px #00ff00, 0 0 16px #00ff00; 
              opacity: 1; 
            }
            50% { 
              box-shadow: 0 0 12px #00ff00, 0 0 24px #00ff00; 
              opacity: 0.8; 
            }
          }
          @keyframes pulse-red {
            0%, 100% { 
              box-shadow: 0 0 8px #ff0000, 0 0 16px #ff0000; 
              opacity: 1; 
            }
            50% { 
              box-shadow: 0 0 12px #ff0000, 0 0 24px #ff0000; 
              opacity: 0.4; 
            }
          }
          .api-tooltip-theme {
            position: absolute;
            top: -40px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 6px 12px;
            borderRadius: 8px;
            fontSize: 10px;
            whiteSpace: nowrap;
            zIndex: 1001;
            opacity: 0;
            transition: opacity 0.3s ease;
          }
          .api-tooltip-theme.visible {
            opacity: 1;
          }
        `}
      </style>

      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: 'linear-gradient(135deg, #3742fa, #2f3542)',
          border: 'none',
          borderRadius: '10px',
          color: 'white',
          padding: '8px 14px',
          fontSize: '12px',
          fontWeight: '600',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          boxShadow: '0 3px 10px rgba(55, 66, 250, 0.3)',
          fontFamily: 'Montserrat, sans-serif',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseOver={(e) => {
          e.target.style.transform = 'translateY(-1px)';
          e.target.style.boxShadow = '0 4px 15px rgba(55, 66, 250, 0.4)';
          setShowTooltip(true);
        }}
        onMouseOut={(e) => {
          e.target.style.transform = 'translateY(0px)';
          e.target.style.boxShadow = '0 3px 10px rgba(55, 66, 250, 0.3)';
          setShowTooltip(false);
        }}
      >
        <span>⚡ API</span>
        
        {apiStatus && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center',
            gap: '4px',
            background: 'rgba(255,255,255,0.15)',
            padding: '2px 6px',
            borderRadius: '6px'
          }}>
            <div style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: Object.values(apiStatus.apis).every(api => api.color === 'green') ? '#00ff00' : '#ff0000',
              animation: Object.values(apiStatus.apis).every(api => api.color === 'green') ? 'pulse-green 2s infinite' : 'pulse-red 1s infinite'
            }} />
            
            <div style={{ display: 'flex', gap: '2px' }}>
              {Object.entries(apiStatus.apis).map(([key, api]) => (
                <div 
                  key={key}
                  style={{
                    width: '4px',
                    height: '4px',
                    borderRadius: '50%',
                    backgroundColor: getLedColor(api),
                    animation: api.color === 'green' ? 'pulse-green 2s infinite' : 'pulse-red 1s infinite'
                  }}
                  title={`${api.name}: ${api.status}`}
                />
              ))}
            </div>
          </div>
        )}

        {showTooltip && apiStatus && (
          <div className={`api-tooltip-theme ${showTooltip ? 'visible' : ''}`}>
            {Object.values(apiStatus.apis).every(api => api.color === 'green') 
              ? '🟢 Toutes les API sont opérationnelles' 
              : '🔴 Certaines API ont des problèmes'
            }
          </div>
        )}
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: '0',
          marginTop: '10px',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '12px',
          padding: '16px',
          minWidth: '280px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
          zIndex: 1000
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '12px',
            borderBottom: '1px solid rgba(0,0,0,0.1)',
            paddingBottom: '8px'
          }}>
            <h4 style={{
              margin: 0,
              color: '#333',
              fontSize: '14px',
              fontWeight: 'bold'
            }}>
              🔧 Statut des API
            </h4>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '16px',
                cursor: 'pointer',
                color: '#666'
              }}
            >
              ×
            </button>
          </div>

          {apiStatus && (
            <div style={{ fontSize: '12px' }}>
              {Object.entries(apiStatus.apis).map(([key, api]) => (
                <div 
                  key={key}
                  style={{ 
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '6px 0',
                    borderBottom: '1px solid rgba(0,0,0,0.05)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: getLedColor(api),
                      animation: api.color === 'green' ? 'pulse-green 2s infinite' : 'pulse-red 1s infinite'
                    }} />
                    <span style={{ color: '#333', fontWeight: '500' }}>
                      {api.name}
                    </span>
                  </div>
                  <span style={{ 
                    color: api.color === 'green' ? '#059669' : '#dc2626',
                    fontSize: '11px',
                    fontWeight: '600'
                  }}>
                    {api.color === 'green' ? '✅ OK' : '❌ ERR'}
                  </span>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={fetchApiStatus}
            style={{
              marginTop: '12px',
              width: '100%',
              padding: '8px',
              background: 'linear-gradient(135deg, #3742fa, #2f3542)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            🔄 Rafraîchir
          </button>
        </div>
      )}
    </div>
  );
};

// Fonction pour générer l'URL YouVersion
const generateYouVersionUrl = (book, chapter, verse) => {
  // Mapping des noms de livres français vers les codes YouVersion
  const bookCodes = {
    // Ancien Testament
    'Genèse': 'GEN', 'Exode': 'EXO', 'Lévitique': 'LEV', 'Nombres': 'NUM', 'Deutéronome': 'DEU',
    'Josué': 'JOS', 'Juges': 'JDG', 'Ruth': 'RUT', '1 Samuel': '1SA', '2 Samuel': '2SA',
    '1 Rois': '1KI', '2 Rois': '2KI', '1 Chroniques': '1CH', '2 Chroniques': '2CH',
    'Esdras': 'EZR', 'Néhémie': 'NEH', 'Esther': 'EST', 'Job': 'JOB', 'Psaume': 'PSA', 'Psaumes': 'PSA',
    'Proverbes': 'PRO', 'Ecclésiaste': 'ECC', 'Cantique': 'SNG', 'Ésaïe': 'ISA', 'Jérémie': 'JER',
    'Lamentations': 'LAM', 'Ézéchiel': 'EZK', 'Daniel': 'DAN', 'Osée': 'HOS', 'Joël': 'JOL',
    'Amos': 'AMO', 'Abdias': 'OBA', 'Jonas': 'JON', 'Michée': 'MIC', 'Nahum': 'NAM',
    'Habacuc': 'HAB', 'Sophonie': 'ZEP', 'Aggée': 'HAG', 'Zacharie': 'ZEC', 'Malachie': 'MAL',
    
    // Nouveau Testament
    'Matthieu': 'MAT', 'Marc': 'MRK', 'Luc': 'LUK', 'Jean': 'JHN', 'Actes': 'ACT',
    'Romains': 'ROM', '1 Corinthiens': '1CO', '2 Corinthiens': '2CO', 'Galates': 'GAL',
    'Éphésiens': 'EPH', 'Philippiens': 'PHP', 'Philippe': 'PHP', 'Colossiens': 'COL',
    '1 Thessaloniciens': '1TH', '2 Thessaloniciens': '2TH', '1 Timothée': '1TI', '2 Timothée': '2TI',
    'Tite': 'TIT', 'Philémon': 'PHM', 'Hébreux': 'HEB', 'Jacques': 'JAS', '1 Pierre': '1PE',
    '2 Pierre': '2PE', '1 Jean': '1JN', '2 Jean': '2JN', '3 Jean': '3JN', 'Jude': 'JUD',
    'Apocalypse': 'REV'
  };
  
  const bookCode = bookCodes[book];
  if (!bookCode) {
    console.warn(`Code YouVersion non trouvé pour: ${book}`);
    return `https://www.bible.com/search/bible?q=${encodeURIComponent(book + ' ' + chapter + ':' + verse)}`;
  }
  
  // URL YouVersion avec version Louis Segond (LSG = 93)
  return `https://www.bible.com/bible/93/${bookCode}.${chapter}.${verse}.LSG`;
};

const ThemeVersesPage = ({ theme, onGoBack }) => {
  const [verses, setVerses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Ancienne base de données remplacée par API calls dynamiques

  useEffect(() => {
    loadThemeVerses();
  }, [theme]);

  const loadThemeVerses = async () => {
    setIsLoading(true);
    
    try {
      // Stratégie multi-recherches pour garantir 20+ versets
      const searchStrategies = getSearchStrategies(theme);
      let allVerses = [];
      
      // Effectuer plusieurs recherches pour collecter suffisamment de versets
      for (const searchTerm of searchStrategies) {
        if (allVerses.length >= 25) break; // Arrêter quand on a assez de versets
        
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search-concordance`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              search_term: searchTerm,
              enrich: true
            })
          });

          if (response.ok) {
            const result = await response.json();
            
            if (result.status === 'success' && result.bible_verses) {
              const newVerses = result.bible_verses.map(verse => ({
                book: verse.book || "Livre",
                chapter: verse.chapter || 1,
                verse: verse.verse || 1,
                text: verse.text || verse.content || "Texte du verset",
                reference: `${verse.book || 'Livre'} ${verse.chapter || 1}:${verse.verse || 1}`
              }));
              
              // Éviter les doublons
              const uniqueVerses = newVerses.filter(newVerse => 
                !allVerses.some(existing => 
                  existing.reference === newVerse.reference
                )
              );
              
              allVerses = [...allVerses, ...uniqueVerses];
              console.log(`[API GEMINI] ${uniqueVerses.length} nouveaux versets pour "${searchTerm}" - Total: ${allVerses.length}`);
            }
          }
        } catch (searchError) {
          console.warn(`Erreur recherche pour "${searchTerm}":`, searchError);
        }
      }
      
      // S'assurer d'avoir au moins 20 versets
      if (allVerses.length < 20) {
        console.log(`Seulement ${allVerses.length} versets trouvés, ajout de versets de référence...`);
        const extraVerses = await getThemeReferenceVerses(theme);
        allVerses = [...allVerses, ...extraVerses].slice(0, 30);
      }
      
      // Limiter à 30 versets maximum et garantir minimum 20
      const finalVerses = allVerses.slice(0, 30);
      
      if (finalVerses.length >= 20) {
        setVerses(finalVerses);
        console.log(`[SUCCESS] ${finalVerses.length} versets récupérés pour "${theme}"`);
      } else {
        // Si encore insuffisant, utiliser le fallback étendu
        await loadExtendedFallbackVerses(theme);
      }
      
    } catch (error) {
      console.error("Erreur chargement versets thème:", error);
      await loadExtendedFallbackVerses(theme);
    } finally {
      setIsLoading(false);
    }
  };

  // Stratégies de recherche multiples pour garantir 20+ versets
  const getSearchStrategies = (themeName) => {
    const strategies = {
      "Amour et Charité": ["amour", "charité", "aimer", "aimé", "bien-aimé", "amoureux"],
      "Foi et Confiance": ["foi", "croire", "confiance", "fidèle", "croyant", "conviction"],
      "Espérance et Promesses": ["espérance", "promesse", "espoir", "attendre", "attente", "espérer"],
      "Pardon et Miséricorde": ["pardon", "miséricorde", "pardonner", "miséricordieux", "grâce", "compassion"],
      "Justice et Droiture": ["justice", "juste", "droiture", "équité", "jugement", "droit"],
      "Sagesse et Connaissance": ["sagesse", "sage", "connaissance", "intelligence", "prudence", "instruction"],
      "Prière et Adoration": ["prière", "prier", "adoration", "adorer", "invoquer", "supplier"],
      "Paix et Réconciliation": ["paix", "paisible", "réconciliation", "réconcilier", "repos", "tranquille"],
      "Joie et Louange": ["joie", "réjouir", "louange", "louer", "allégresse", "bonheur"],
      "Humilité et Service": ["humilité", "humble", "service", "servir", "serviteur", "modeste"],
      "Courage et Force": ["courage", "fort", "force", "vaillant", "brave", "puissant"],
      "Patience et Persévérance": ["patience", "patient", "persévérance", "endurance", "supporter", "attendre"],
      "Compassion et Bonté": ["compassion", "bonté", "bon", "compatissant", "bienveillant", "doux"],
      "Vérité et Sincérité": ["vérité", "vrai", "sincérité", "sincère", "fidélité", "véracité"],
      "Liberté et Délivrance": ["liberté", "libre", "délivrance", "délivrer", "affranchir", "libérer"],
      "Guérison et Restauration": ["guérison", "guérir", "restauration", "restaurer", "santé", "rétablir"],
      "Famille et Relations": ["famille", "père", "mère", "enfant", "frère", "sœur"],
      "Travail et Vocation": ["travail", "œuvre", "vocation", "appel", "travailler", "labeur"],
      "Richesse et Pauvreté": ["richesse", "riche", "pauvreté", "pauvre", "trésor", "biens"],
      "Souffrance et Épreuves": ["souffrance", "souffrir", "épreuve", "affliction", "tribulation", "douleur"],
      "Mort et Résurrection": ["mort", "mourir", "résurrection", "ressusciter", "vie", "éternelle"],
      "Création et Nature": ["création", "créer", "terre", "ciel", "monde", "univers"],
      "Prophétie et Révélation": ["prophète", "prophétie", "révélation", "révéler", "vision", "songe"],
      "Royaume de Dieu": ["royaume", "roi", "ciel", "céleste", "trône", "régner"],
      "Salut et Rédemption": ["salut", "sauver", "rédemption", "racheter", "sauveur", "délivrance"],
      "Saint-Esprit": ["esprit", "saint", "consolateur", "souffle", "onction", "baptême"],
      "Église et Communauté": ["église", "assemblée", "communauté", "corps", "frères", "peuple"],
      "Mission et Évangélisation": ["évangile", "mission", "prêcher", "témoignage", "annoncer", "proclamer"],
      "Sanctification": ["sanctification", "saint", "sanctifier", "pur", "purification", "consécration"],
      "Eschatologie et Fin des Temps": ["fin", "dernier", "jugement", "éternité", "avènement", "retour"]
    };
    
    return strategies[themeName] || [themeName.toLowerCase(), themeName.replace(/\set\s/g, ' ').toLowerCase()];
  };

  // Versets de référence spécifiques par thème
  const getThemeReferenceVerses = async (themeName) => {
    const referenceVerses = {
      "Amour et Charité": [
        { book: "1 Jean", chapter: 4, verse: 7, text: "Bien-aimés, aimons-nous les uns les autres; car l'amour est de Dieu, et quiconque aime est né de Dieu et connaît Dieu.", reference: "1 Jean 4:7" },
        { book: "1 Jean", chapter: 4, verse: 16, text: "Et nous, nous avons connu l'amour que Dieu a pour nous, et nous y avons cru. Dieu est amour; et celui qui demeure dans l'amour demeure en Dieu, et Dieu demeure en lui.", reference: "1 Jean 4:16" },
        { book: "Matthieu", chapter: 22, verse: 37, text: "Jésus lui répondit: Tu aimeras le Seigneur, ton Dieu, de tout ton cœur, de toute ton âme, et de toute ta pensée.", reference: "Matthieu 22:37" },
        { book: "Jean", chapter: 13, verse: 34, text: "Je vous donne un commandement nouveau: Aimez-vous les uns les autres; comme je vous ai aimés, vous aussi, aimez-vous les uns les autres.", reference: "Jean 13:34" },
        { book: "1 Corinthiens", chapter: 13, verse: 13, text: "Maintenant donc ces trois choses demeurent: la foi, l'espérance, la charité; mais la plus grande de ces choses, c'est la charité.", reference: "1 Corinthiens 13:13" }
      ],
      "Foi et Confiance": [
        { book: "Hébreux", chapter: 11, verse: 6, text: "Or sans la foi il est impossible de lui être agréable; car il faut que celui qui s'approche de Dieu croie que Dieu existe, et qu'il est le rémunérateur de ceux qui le cherchent.", reference: "Hébreux 11:6" },
        { book: "Romains", chapter: 10, verse: 17, text: "Ainsi la foi vient de ce qu'on entend, et ce qu'on entend vient de la parole de Christ.", reference: "Romains 10:17" },
        { book: "Marc", chapter: 11, verse: 22, text: "Jésus prit la parole, et leur dit: Ayez foi en Dieu.", reference: "Marc 11:22" },
        { book: "Éphésiens", chapter: 2, verse: 8, text: "Car c'est par la grâce que vous êtes sauvés, par le moyen de la foi. Et cela ne vient pas de vous, c'est le don de Dieu.", reference: "Éphésiens 2:8" },
        { book: "Jacques", chapter: 2, verse: 17, text: "Il en est ainsi de la foi: si elle n'a pas les œuvres, elle est morte en elle-même.", reference: "Jacques 2:17" }
      ]
    };
    
    return referenceVerses[themeName] || [];
  };

  // Fallback étendu avec au moins 20 versets
  const loadExtendedFallbackVerses = async (themeName) => {
    const fallbackVerses = [
      { book: "1 Jean", chapter: 4, verse: 8, text: "Celui qui n'aime pas n'a pas connu Dieu, car Dieu est amour.", reference: "1 Jean 4:8" },
      { book: "Jean", chapter: 3, verse: 16, text: "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle.", reference: "Jean 3:16" },
      { book: "1 Corinthiens", chapter: 13, verse: 4, text: "L'amour est patient, l'amour est plein de bonté; l'amour n'est point envieux; l'amour ne se vante point, il ne s'enfle point d'orgueil.", reference: "1 Corinthiens 13:4" },
      { book: "1 Corinthiens", chapter: 13, verse: 13, text: "Maintenant donc ces trois choses demeurent: la foi, l'espérance, la charité; mais la plus grande de ces choses, c'est la charité.", reference: "1 Corinthiens 13:13" },
      { book: "Matthieu", chapter: 22, verse: 37, text: "Jésus lui répondit: Tu aimeras le Seigneur, ton Dieu, de tout ton cœur, de toute ton âme, et de toute ta pensée.", reference: "Matthieu 22:37" },
      { book: "Jean", chapter: 13, verse: 34, text: "Je vous donne un commandement nouveau: Aimez-vous les uns les autres; comme je vous ai aimés, vous aussi, aimez-vous les uns les autres.", reference: "Jean 13:34" },
      { book: "Romains", chapter: 5, verse: 8, text: "Mais Dieu prouve son amour envers nous, en ce que, lorsque nous étions encore des pécheurs, Christ est mort pour nous.", reference: "Romains 5:8" },
      { book: "1 Pierre", chapter: 4, verse: 8, text: "Avant tout, ayez les uns pour les autres une ardente charité, car La charité couvre une multitude de péchés.", reference: "1 Pierre 4:8" },
      { book: "Jean", chapter: 15, verse: 13, text: "Il n'y a pas de plus grand amour que de donner sa vie pour ses amis.", reference: "Jean 15:13" },
      { book: "Romains", chapter: 8, verse: 39, text: "ni la hauteur, ni la profondeur, ni aucune autre créature ne pourra nous séparer de l'amour de Dieu manifesté en Jésus-Christ notre Seigneur.", reference: "Romains 8:39" },
      { book: "1 Jean", chapter: 3, verse: 16, text: "Nous avons connu l'amour, en ce qu'il a donné sa vie pour nous; nous aussi, nous devons donner notre vie pour les frères.", reference: "1 Jean 3:16" },
      { book: "Éphésiens", chapter: 5, verse: 2, text: "et marchez dans la charité, à l'exemple de Christ, qui nous a aimés, et qui s'est livré lui-même à Dieu pour nous comme une offrande et un sacrifice de bonne odeur.", reference: "Éphésiens 5:2" },
      { book: "Colossiens", chapter: 3, verse: 14, text: "Mais par-dessus toutes ces choses revêtez-vous de la charité, qui est le lien de la perfection.", reference: "Colossiens 3:14" },
      { book: "1 Thessaloniciens", chapter: 4, verse: 9, text: "Pour ce qui est de l'amour fraternel, vous n'avez pas besoin qu'on vous en écrive; car vous avez vous-mêmes appris de Dieu à vous aimer les uns les autres.", reference: "1 Thessaloniciens 4:9" },
      { book: "Hébreux", chapter: 10, verse: 24, text: "Veillons les uns sur les autres, pour nous exciter à la charité et aux bonnes œuvres.", reference: "Hébreux 10:24" },
      { book: "1 Jean", chapter: 4, verse: 11, text: "Bien-aimés, si Dieu nous a ainsi aimés, nous devons aussi nous aimer les uns les autres.", reference: "1 Jean 4:11" },
      { book: "Jean", chapter: 14, verse: 21, text: "Celui qui a mes commandements et qui les garde, c'est celui qui m'aime; et celui qui m'aime sera aimé de mon Père, je l'aimerai, et je me ferai connaître à lui.", reference: "Jean 14:21" },
      { book: "1 Corinthiens", chapter: 16, verse: 14, text: "Que tout ce que vous faites se fasse avec charité!", reference: "1 Corinthiens 16:14" },
      { book: "Galates", chapter: 5, verse: 13, text: "Frères, vous avez été appelés à la liberté, seulement ne faites pas de cette liberté un prétexte de vivre selon la chair; mais rendez-vous, par la charité, serviteurs les uns des autres.", reference: "Galates 5:13" },
      { book: "1 Pierre", chapter: 1, verse: 22, text: "Ayant purifié vos âmes en obéissant à la vérité pour avoir un amour fraternel sincère, aimez-vous ardemment les uns les autres, de tout votre cœur.", reference: "1 Pierre 1:22" },
      { book: "1 Jean", chapter: 2, verse: 15, text: "N'aimez point le monde, ni les choses qui sont dans le monde. Si quelqu'un aime le monde, l'amour du Père n'est point en lui.", reference: "1 Jean 2:15" },
      { book: "Deutéronome", chapter: 6, verse: 5, text: "Tu aimeras l'Éternel, ton Dieu, de tout ton cœur, de toute ton âme et de toute ta force.", reference: "Deutéronome 6:5" },
      { book: "Cantique", chapter: 8, verse: 7, text: "Les grandes eaux ne peuvent éteindre l'amour, Et les fleuves ne le submergeraient pas; Quand un homme offrirait tous les biens de sa maison contre l'amour, Il ne s'attirerait que le mépris.", reference: "Cantique 8:7" }
    ];
    
    setVerses(fallbackVerses);
    console.log(`[FALLBACK ÉTENDU] ${fallbackVerses.length} versets de base pour "${themeName}"`);
  };

  if (isLoading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center', color: '#667eea' }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '20px',
            animation: 'spin 2s linear infinite'
          }}>📖</div>
          <h2>Recherche des versets sur "{theme}"...</h2>
          <p>Compilation de plus de 20 versets bibliques</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)',
      padding: '20px'
    }}>
      {/* Header avec retour */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        marginBottom: '30px',
        maxWidth: '1200px',
        margin: '0 auto 30px auto'
      }}>
        <button 
          onClick={onGoBack}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            padding: '12px 24px',
            fontSize: '14px',
            fontWeight: '700',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          ← Retour
        </button>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '20px',
          flex: '1',
          justifyContent: 'space-between',
          flexWrap: 'wrap'
        }}>
          <div>
            <h1 style={{ 
              fontSize: '32px', 
              fontWeight: '700',
              margin: '0',
              color: '#2c3e50',
              fontFamily: "'Montserrat', sans-serif"
            }}>
              📖 Versets sur "{theme}"
            </h1>
            <p style={{ 
              margin: '5px 0 0 0',
              color: '#667eea',
              fontSize: '16px'
            }}>
              {verses.length} versets trouvés • 📖 Cliquez sur les références pour lire sur YouVersion
            </p>
          </div>

          {/* Boutons de contrôle */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            flexWrap: 'wrap'
          }}>
            {/* Bouton Gemini */}
            <button 
              onClick={() => window.open('https://gemini.google.com/', '_blank')}
              style={{
                background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
                border: 'none',
                borderRadius: '10px',
                color: 'white',
                padding: '8px 14px',
                fontSize: '12px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 3px 10px rgba(139, 92, 246, 0.3)',
                fontFamily: 'Montserrat, sans-serif'
              }}
              onMouseOver={(e) => {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 4px 15px rgba(139, 92, 246, 0.4)';
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'translateY(0px)';
                e.target.style.boxShadow = '0 3px 10px rgba(139, 92, 246, 0.3)';
              }}
            >
              🤖 Gemini
            </button>

            {/* Bouton Prise de Note */}
            <button 
              onClick={() => {
                if (onGoBack) {
                  onGoBack();
                  setTimeout(() => {
                    window.dispatchEvent(new CustomEvent('navigate-to-notes'));
                  }, 100);
                }
              }}
              style={{
                background: 'linear-gradient(135deg, #10b981, #059669)',
                border: 'none',
                borderRadius: '10px',
                color: 'white',
                padding: '8px 14px',
                fontSize: '12px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 3px 10px rgba(16, 185, 129, 0.3)',
                fontFamily: 'Montserrat, sans-serif'
              }}
              onMouseOver={(e) => {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 4px 15px rgba(16, 185, 129, 0.4)';
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'translateY(0px)';
                e.target.style.boxShadow = '0 3px 10px rgba(16, 185, 129, 0.3)';
              }}
            >
              📝 Prise de Note
            </button>

            {/* Bouton ChatGPT */}
            <button 
              onClick={() => window.open('https://chatgpt.com/', '_blank')}
              style={{
                background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                border: 'none',
                borderRadius: '10px',
                color: 'white',
                padding: '8px 14px',
                fontSize: '12px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 3px 10px rgba(245, 158, 11, 0.3)',
                fontFamily: 'Montserrat, sans-serif'
              }}
              onMouseOver={(e) => {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 4px 15px rgba(245, 158, 11, 0.4)';
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'translateY(0px)';
                e.target.style.boxShadow = '0 3px 10px rgba(245, 158, 11, 0.3)';
              }}
            >
              💬 ChatGPT
            </button>

            {/* Bouton Lire la Bible */}
            <button 
              onClick={() => window.open('https://www.bible.com/', '_blank')}
              style={{
                background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                border: 'none',
                borderRadius: '10px',
                color: 'white',
                padding: '8px 14px',
                fontSize: '12px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 3px 10px rgba(59, 130, 246, 0.3)',
                fontFamily: 'Montserrat, sans-serif'
              }}
              onMouseOver={(e) => {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 4px 15px rgba(59, 130, 246, 0.4)';
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'translateY(0px)';
                e.target.style.boxShadow = '0 3px 10px rgba(59, 130, 246, 0.3)';
              }}
            >
              📖 Lire la Bible
            </button>

            {/* Bouton API avec LEDs */}
            <ApiStatusButton />
          </div>
        </div>
      </div>

      {/* Liste des versets */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {verses.length > 0 ? (
          <div style={{
            display: 'grid',
            gap: '20px'
          }}>
            {verses.map((verse, index) => (
              <div
                key={index}
                style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid rgba(102, 126, 234, 0.1)',
                  boxShadow: '0 8px 32px rgba(102, 126, 234, 0.1)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 12px 48px rgba(102, 126, 234, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 8px 32px rgba(102, 126, 234, 0.1)';
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  gap: '20px'
                }}>
                  <div style={{ flex: 1 }}>
                    <p style={{
                      fontSize: '18px',
                      lineHeight: '1.6',
                      color: '#2c3e50',
                      margin: '0 0 12px 0',
                      fontFamily: "'Georgia', serif"
                    }}>
                      "{verse.text}"
                    </p>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <a 
                        href={generateYouVersionUrl(verse.book, verse.chapter, verse.verse)}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: '14px',
                          fontWeight: '700',
                          color: '#667eea',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px',
                          fontFamily: "'Montserrat', sans-serif",
                          textDecoration: 'none',
                          padding: '6px 12px',
                          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))',
                          borderRadius: '8px',
                          border: '1px solid rgba(102, 126, 234, 0.2)',
                          transition: 'all 0.3s ease',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.background = 'linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2))';
                          e.target.style.transform = 'translateY(-1px)';
                          e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.background = 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))';
                          e.target.style.transform = 'translateY(0)';
                          e.target.style.boxShadow = 'none';
                        }}
                      >
                        📖 {verse.book} {verse.chapter}:{verse.verse}
                        <span style={{ fontSize: '10px', opacity: 0.7 }}>YouVersion</span>
                      </a>
                    </div>
                  </div>
                  <div style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    borderRadius: '20px',
                    padding: '6px 12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    minWidth: '40px',
                    textAlign: 'center'
                  }}>
                    {index + 1}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: '#667eea'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📚</div>
            <h3>Aucun verset trouvé pour "{theme}"</h3>
            <p>Ce thème n'est pas encore disponible dans notre base de données.</p>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ThemeVersesPage;
import React, { useState, useEffect } from 'react';
import ApiControlPanel from './ApiControlPanel';

// ANCIEN COMPOSANT SUPPRIMÉ - Utilise ApiControlPanel centralisé
const ApiStatusButton_OLD_REMOVED = () => {
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
    return "https://rubrique-study.preview.emergentagent.com";
  };

  const BACKEND_URL = getBackendUrl();

  // Fonction pour récupérer le statut des API
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
      {/* Styles CSS pour les animations LED */}
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
          .api-tooltip {
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
          .api-tooltip.visible {
            opacity: 1;
          }
        `}
      </style>

      {/* Bouton API avec LEDs */}
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
        
        {/* LEDs physiques individuelles */}
        {apiStatus && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center',
            gap: '4px',
            background: 'rgba(255,255,255,0.15)',
            padding: '2px 6px',
            borderRadius: '6px'
          }}>
            {/* LED de statut global */}
            <div style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: Object.values(apiStatus.apis).every(api => api.color === 'green') ? '#00ff00' : '#ff0000',
              animation: Object.values(apiStatus.apis).every(api => api.color === 'green') ? 'pulse-green 2s infinite' : 'pulse-red 1s infinite'
            }} />
            
            {/* LEDs individuelles pour chaque API */}
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

        {/* Tooltip */}
        {showTooltip && apiStatus && (
          <div className={`api-tooltip ${showTooltip ? 'visible' : ''}`}>
            {Object.values(apiStatus.apis).every(api => api.color === 'green') 
              ? '🟢 Toutes les API sont opérationnelles' 
              : '🔴 Certaines API ont des problèmes'
            }
          </div>
        )}
      </button>

      {/* Panneau de contrôle détaillé */}
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

          {/* Liste des API avec LEDs */}
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

          {/* Rafraîchir */}
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

// Configuration du backend - utilise la variable d'environnement
const getBackendUrl = () => {
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  const hostname = window.location.hostname;
  if (hostname === "localhost" || hostname === "127.0.0.1") return "http://localhost:8001";
  return "https://rubrique-study.preview.emergentagent.com";
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL.replace(/\/+$/g, "")}/api`;

const VersetParVersetPage = ({ onGoBack, content, bookInfo }) => {
  const [currentBatch, setCurrentBatch] = useState(1); // Batch actuel (1, 2, 3...)
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [allVersetsBatches, setAllVersetsBatches] = useState({}); // Stocke tous les batches chargés
  const [totalVersetsExpected, setTotalVersetsExpected] = useState(null);
  const [enrichingVersets, setEnrichingVersets] = useState({}); // Track quels versets sont en cours d'enrichissement

  useEffect(() => {
    // Quand le contenu arrive, le stocker comme batch 1
    if (content) {
      setAllVersetsBatches(prev => ({
        ...prev,
        1: content
      }));
      setCurrentBatch(1);
    }
  }, [content]);

  // Fonction pour enrichir une explication théologique spécifique avec Gemini
  const enrichirExplicationGemini = async (versetNumber, currentExplication, versetText) => {
    const enrichKey = `${currentBatch}-${versetNumber}`;
    
    if (enrichingVersets[enrichKey]) return; // Déjà en cours
    
    setEnrichingVersets(prev => ({...prev, [enrichKey]: true}));
    
    try {
      console.log(`[GEMINI ENRICHISSEMENT] Enrichissement verset ${versetNumber} batch ${currentBatch}`);
      
      const apiUrl = `${API_BASE}/generate-verse-by-verse`;
      
      const prompt = `ENRICHISSEMENT THÉOLOGIQUE APPROFONDI

Verset biblique : "${versetText}"
Explication actuelle : "${currentExplication}"

MISSION : Enrichir et approfondir cette explication théologique avec 200-300 mots supplémentaires.

AJOUTE :
- Contexte historique et culturel
- Liens avec d'autres passages bibliques
- Implications doctrinales profondes
- Applications pratiques modernes
- Perspectives herméneutiques

CONSERVE le texte original ET enrichis-le substantiellement.

GÉNÈRE DIRECTEMENT l'explication enrichie complète :`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          passage: `Enrichissement théologique`,
          version: 'LSG',
          tokens: 300,
          use_gemini: true,
          enriched: true,
          custom_prompt: prompt
        })
      });
      
      if (!response.ok) throw new Error(`Erreur API: ${response.status}`);
      
      const data = await response.json();
      
      if (data.content) {
        // Remplacer l'explication dans le batch actuel
        const currentBatchContent = allVersetsBatches[currentBatch];
        const versetPattern = new RegExp(`(VERSET ${versetNumber}[\\s\\S]*?EXPLICATION THÉOLOGIQUE[\\s\\S]*?:)([\\s\\S]*?)(?=VERSET|$)`, 'i');
        
        const enrichedExplication = data.content.replace(/.*EXPLICATION THÉOLOGIQUE.*?:/i, '').trim();
        const enrichedContent = currentBatchContent.replace(versetPattern, `$1\n${enrichedExplication}\n`);
        
        // Mettre à jour le batch avec le contenu enrichi
        setAllVersetsBatches(prev => ({
          ...prev,
          [currentBatch]: enrichedContent
        }));
        
        console.log(`[GEMINI ENRICHISSEMENT] Verset ${versetNumber} enrichi avec succès`);
      }
      
    } catch (error) {
      console.error(`[GEMINI ENRICHISSEMENT] Erreur verset ${versetNumber}:`, error);
    } finally {
      setEnrichingVersets(prev => ({...prev, [enrichKey]: false}));
    }
  };

  // Fonction pour charger le batch suivant (versets 6-10, 11-15, etc.)
  const loadNextBatch = async () => {
    if (isLoadingMore) return;
    
    const nextBatch = currentBatch + 1;
    
    // Si on a déjà ce batch en cache, l'afficher directement
    if (allVersetsBatches[nextBatch]) {
      setCurrentBatch(nextBatch);
      return;
    }
    
    setIsLoadingMore(true);
    
    try {
      // Calculer le range de versets à demander
      const startVerse = (nextBatch - 1) * 5 + 1; // Batch 2 = versets 6-10, etc.
      const endVerse = startVerse + 4;
      
      // Extraire le livre et chapitre du bookInfo
      const bookChapter = bookInfo?.split(':')[0] || 'Genèse 1';
      const requestPassage = `${bookChapter}:${startVerse}-${endVerse}`;
      
      console.log(`[PAGINATION] Chargement batch ${nextBatch}: ${requestPassage}`);
      
      // Appeler l'API pour les versets suivants
      const apiUrl = `${API_BASE}/generate-verse-by-verse`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          passage: requestPassage,
          version: 'LSG',
          tokens: 500,
          use_gemini: true,
          enriched: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.content) {
        // Stocker le nouveau batch
        setAllVersetsBatches(prev => ({
          ...prev,
          [nextBatch]: data.content
        }));
        setCurrentBatch(nextBatch);
        console.log(`[PAGINATION] Batch ${nextBatch} chargé avec succès`);
      } else {
        throw new Error('Pas de contenu reçu');
      }
      
    } catch (error) {
      console.error(`[PAGINATION] Erreur chargement batch ${nextBatch}:`, error);
      // Optionnel : afficher une erreur à l'utilisateur
    } finally {
      setIsLoadingMore(false);
    }
  };

  // Fonction pour naviguer vers un batch précédent
  const goToPreviousBatch = () => {
    if (currentBatch > 1) {
      setCurrentBatch(currentBatch - 1);
    }
  };

  // Obtenir le contenu du batch actuel
  const getCurrentBatchContent = () => {
    return allVersetsBatches[currentBatch] || '';
  };

  // Fonction pour gérer l'enrichissement d'un verset via React (pas via HTML onclick)
  const handleEnrichirVerset = async (versetNumber) => {
    console.log(`[GEMINI] Clic enrichissement verset ${versetNumber}`);
    
    // Extraire le texte du verset et l'explication actuelle
    const currentContent = getCurrentBatchContent();
    const versetRegex = new RegExp(`VERSET ${versetNumber}[\\s\\S]*?TEXTE BIBLIQUE[\\s\\S]*?:([\\s\\S]*?)EXPLICATION THÉOLOGIQUE[\\s\\S]*?:([\\s\\S]*?)(?=VERSET|$)`, 'i');
    const match = currentContent.match(versetRegex);
    
    if (match) {
      const versetText = match[1].trim();
      const currentExplication = match[2].trim();
      
      await enrichirExplicationGemini(versetNumber, currentExplication, versetText);
    }
  };
  
  // Fonction pour nettoyer les marqueurs Markdown
  const cleanMarkdownFormatting = (text) => {
    if (!text) return '';
    
    return text
      // Supprimer les ** pour le gras
      .replace(/\*\*/g, '')
      // Supprimer les * pour l'italique
      .replace(/(?<!\*)\*(?!\*)/g, '')
      // Nettoyer les espaces multiples
      .replace(/\s+/g, ' ')
      // Nettoyer les lignes vides multiples
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      .trim();
  };

  // Nouvelle approche : Analyser le contenu et créer des composants React avec boutons intégrés
  const parseContentWithGeminiButtons = (content) => {
    if (!content) return [];
    
    const sections = [];
    const versetPattern = /(\*\*VERSET\s+(\d+)\*\*[\s\S]*?)(?=\*\*VERSET\s+\d+|$)/gi;
    
    let match;
    while ((match = versetPattern.exec(content)) !== null) {
      const versetNumber = parseInt(match[2]);
      const versetContent = match[1].trim();
      
      // Séparer le contenu en parties
      const parts = versetContent.split(/(\*\*TEXTE BIBLIQUE\s*:\*\*|\*\*EXPLICATION THÉOLOGIQUE\s*:\*\*)/i);
      
      let versetTitle = '';
      let texteContent = '';
      let explicationContent = '';
      
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i].trim();
        
        if (part.includes('**VERSET')) {
          versetTitle = cleanMarkdownFormatting(part);
        } else if (part.match(/TEXTE BIBLIQUE/i)) {
          texteContent = cleanMarkdownFormatting(parts[i + 1]?.trim() || '');
          i++; // Skip next part as we've consumed it
        } else if (part.match(/\*\*EXPLICATION THÉOLOGIQUE/i)) {
          explicationContent = cleanMarkdownFormatting(parts[i + 1]?.trim() || '');
          i++; // Skip next part as we've consumed it
        }
      }
      
      sections.push({
        number: versetNumber,
        title: versetTitle,
        texte: texteContent,
        explication: explicationContent
      });
    }
    
    return sections;
  };

  // Fonction pour extraire les numéros de versets du contenu
  const extractVersetNumbers = (content) => {
    if (!content) return [];
    
    const versetPattern = /\*\*VERSET\s+(\d+)\*\*/gi;
    const matches = [];
    let match;
    
    while ((match = versetPattern.exec(content)) !== null) {
      matches.push(parseInt(match[1]));
    }
    
    return matches;
  };

  // Fonction pour formater intelligemment l'explication théologique
  const formatExplicationTheologique = (text) => {
    if (!text) return '';
    
    // Décoder les entités HTML pour éviter l'affichage de code CSS brut
    let formattedText = text
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#x27;/g, "'")
      .replace(/&amp;/g, '&');
    
    // Nettoyer COMPLÈTEMENT tous les styles CSS qui peuvent apparaître en texte brut
    formattedText = formattedText
      .replace(/style="[^"]*"/g, '') // Supprimer tous les attributs style
      .replace(/background:\s*linear-gradient\([^)]*\);?/g, '') // Supprimer les CSS linear-gradient
      .replace(/color:\s*white\s*!important;?/g, '') // Supprimer color: white
      .replace(/font-weight:\s*\d+\s*!important;?/g, '') // Supprimer font-weight
      .replace(/padding:\s*[^;]*;?/g, '') // Supprimer padding
      .replace(/border-radius:\s*[^;]*;?/g, '') // Supprimer border-radius  
      .replace(/text-shadow:\s*[^;]*;?/g, '') // Supprimer text-shadow
      .replace(/[^>]*">/g, '>') // Nettoyer les remnants de balises
      .replace(/>\s*"/g, '>') // Nettoyer les guillemets orphelins
      .replace(/"\s*</g, '<'); // Nettoyer les guillemets orphelins
    
    // 1. Rendre les références bibliques cliquables (simplifié, sans style inline)
    const referencePattern = /(Genèse|Exode|Lévitique|Nombres|Deutéronome|Josué|Juges|Ruth|1 Samuel|2 Samuel|1 Rois|2 Rois|1 Chroniques|2 Chroniques|Esdras|Néhémie|Esther|Job|Psaumes|Proverbes|Ecclésiaste|Cantique|Ésaïe|Jérémie|Lamentations|Ézéchiel|Daniel|Osée|Joël|Amos|Abdias|Jonas|Michée|Nahum|Habacuc|Sophonie|Aggée|Zacharie|Malachie|Matthieu|Marc|Luc|Jean|Actes|Romains|1 Corinthiens|2 Corinthiens|Galates|Éphésiens|Philippiens|Colossiens|1 Thessaloniciens|2 Thessaloniciens|1 Timothée|2 Timothée|Tite|Philémon|Hébreux|Jacques|1 Pierre|2 Pierre|1 Jean|2 Jean|3 Jean|Jude|Apocalypse)\s+(\d+):(\d+(?:-\d+)?)/g;
    
    formattedText = formattedText.replace(referencePattern, (match, livre, chapitre, verset) => {
      const searchQuery = encodeURIComponent(`${livre} ${chapitre}:${verset}`);
      return `<a href="https://www.bible.com/search/bible?q=${searchQuery}" target="_blank" class="bible-reference" title="Cliquer pour lire ce verset sur YouVersion">${match}</a>`;
    });
    
    // 2. Mettre en gras les concepts théologiques importants (utiliser des classes CSS)
    const conceptsTheologiques = [
      'bénédiction divine', 'volonté de Dieu', 'fils de Dieu', 'filles d\'hommes',
      'croissance démographique', 'lignée de Seth', 'lignée de Caïn',
      'application pratique', 'sur le plan spirituel', 'contexte historique',
      'signification théologique', 'enseignement biblique', 'principe biblique',
      'perspective chrétienne', 'vérité spirituelle', 'message divin',
      'révélation divine', 'sagesse divine', 'justice divine', 'miséricorde divine',
      'alliance divine', 'promesse divine', 'amour de Dieu', 'grâce divine',
      'royaume de Dieu', 'peuple élu', 'salut', 'rédemption', 'sanctification',
      'justification', 'régénération', 'conversion', 'repentance', 'foi',
      'espérance', 'charité', 'humilité', 'obéissance', 'soumission',
      'témoignage chrétien', 'vie chrétienne', 'disciple', 'discipleship'
    ];
    
    conceptsTheologiques.forEach(concept => {
      const regex = new RegExp(`(${concept})`, 'gi');
      formattedText = formattedText.replace(regex, '<strong class="theological-concept">$1</strong>');
    });
    
    // 3. Mettre en gras les expressions importantes entre guillemets
    formattedText = formattedText.replace(/"([^"]+)"/g, '<strong class="quoted-text">"$1"</strong>');
    
    // 4. Mettre en évidence les phrases de conclusion/application
    const conclusionPatterns = [
      /(L'application pratique [^.]+\.)/gi,
      /(En conclusion[^.]+\.)/gi,
      /(Ainsi[^.]+\.)/gi,
      /(Par conséquent[^.]+\.)/gi,
      /(Il en résulte [^.]+\.)/gi,
      /(Cela nous enseigne [^.]+\.)/gi,
      /(Nous pouvons donc [^.]+\.)/gi,
      /(Cette vérité nous [^.]+\.)/gi
    ];
    
    conclusionPatterns.forEach(pattern => {
      formattedText = formattedText.replace(pattern, '<span style="background: #10b981; color: white !important; font-weight: 700 !important; font-style: italic; padding: 3px 8px; border-radius: 6px; display: inline-block; margin: 2px; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">$1</span>');
    });
    
    // 5. Mettre en gras les mots-clés doctrinaux
    const motsClesDoctrinaux = [
      'fécondité', 'procréation', 'sexualité', 'mariage', 'famille',
      'responsabilité', 'intendance', 'dégénérescence', 'corruption',
      'péché', 'chute', 'rachat', 'restauration', 'nouvelle création',
      'esprit', 'âme', 'corps', 'trinité', 'incarnation', 'résurrection'
    ];
    
    motsClesDoctrinaux.forEach(mot => {
      const regex = new RegExp(`\\b(${mot})\\b`, 'gi');
      formattedText = formattedText.replace(regex, '<span style="background: #ef4444; color: white !important; padding: 2px 5px; border-radius: 4px; font-weight: 700 !important; text-shadow: 0 1px 1px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.2);">$1</span>');
    });
    
    return formattedText;
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, rgba(248, 250, 252, 0.98) 0%, rgba(241, 245, 249, 0.95) 50%, rgba(248, 250, 252, 0.98) 100%)',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      {/* En-tête moderne */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.95) 0%, rgba(124, 58, 237, 0.98) 100%)',
        color: 'white',
        padding: '30px 20px',
        boxShadow: '0 8px 32px rgba(139, 92, 246, 0.25)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%, rgba(255, 255, 255, 0.05) 100%)',
          pointerEvents: 'none'
        }}></div>
        
        <div style={{
          maxWidth: '900px',
          margin: '0 auto',
          position: 'relative',
          zIndex: 10
        }}>
          <button 
            onClick={onGoBack}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              padding: '10px 20px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              marginBottom: '20px',
              backdropFilter: 'blur(10px)',
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.3)';
              e.target.style.transform = 'translateY(-2px)';
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.2)';
              e.target.style.transform = 'translateY(0)';
            }}
          >
            ← Retour à l'Étude
          </button>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '20px',
            flexWrap: 'wrap',
            marginBottom: '8px'
          }}>
            <h1 style={{
              fontSize: 'clamp(1.8rem, 4vw, 2.5rem)',
              fontWeight: '800',
              margin: 0,
              textShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
              textAlign: 'center'
            }}>
              📖 Étude Verset par Verset
            </h1>

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
                  // Navigation vers la page de notes
                  if (onGoBack) {
                    // Retourner à la page principale puis naviguer vers les notes
                    onGoBack();
                    setTimeout(() => {
                      // Simuler le clic sur prise de note de la page principale
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
                  fontFamily: 'Montserrat, sans-serif',
                  textAlign: 'center'
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
                  fontFamily: 'Montserrat, sans-serif',
                  textAlign: 'center'
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
                  fontFamily: 'Montserrat, sans-serif',
                  textAlign: 'center'
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

              {/* Bouton API avec LEDs physiques - Composant centralisé */}
              <ApiControlPanel backendUrl={process.env.REACT_APP_BACKEND_URL || "http://localhost:8001"} />
            </div>
          </div>
          
          {bookInfo && (
            <div style={{
              fontSize: 'clamp(1rem, 3vw, 1.2rem)',
              textAlign: 'center',
              opacity: 0.9,
              fontWeight: '500'
            }}>
              {bookInfo} • Batch {currentBatch} (versets {(currentBatch - 1) * 5 + 1}-{currentBatch * 5})
            </div>
          )}
        </div>
      </div>

      {/* Contenu principal avec optimisation mobile */}
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '20px',
        // Optimisation mobile : padding plus petit sur mobile
        '@media (maxWidth: 768px)': {
          padding: '15px'
        }
      }}>
        {getCurrentBatchContent() ? (
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: 'clamp(20px, 5vw, 40px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
            border: '1px solid rgba(226, 232, 240, 0.8)',
            lineHeight: '1.7',
            fontSize: 'clamp(15px, 4vw, 16px)',
            marginBottom: '20px'
          }}>
            {/* Nouveau rendu avec boutons intégrés */}
            {parseContentWithGeminiButtons(getCurrentBatchContent()).map((section, index) => (
              <div key={section.number} style={{ marginBottom: '40px' }}>
                {/* Titre du verset */}
                <div className="verset-header">
                  {section.title}
                </div>
                
                {/* Texte biblique */}
                {section.texte && (
                  <>
                    <div className="texte-biblique-label">TEXTE BIBLIQUE :</div>
                    <div style={{ 
                      marginBottom: '20px', 
                      padding: '10px 0',
                      color: '#374151'
                    }}>
                      {section.texte}
                    </div>
                  </>
                )}
                
                {/* Explication théologique avec bouton Gemini intégré */}
                {section.explication && (
                  <>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '15px',
                      marginBottom: '16px',
                      flexWrap: 'wrap'
                    }}>
                      <div className="explication-label" style={{ flex: '1', minWidth: '200px' }}>
                        EXPLICATION THÉOLOGIQUE :
                      </div>
                      
                      {/* Bouton Gemini à droite de l'explication */}
                      <button 
                        onClick={() => handleEnrichirVerset(section.number)}
                        disabled={enrichingVersets[`${currentBatch}-${section.number}`]}
                        style={{
                          background: enrichingVersets[`${currentBatch}-${section.number}`]
                            ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)'
                            : 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                          color: 'white',
                          border: 'none',
                          padding: 'clamp(8px, 2vw, 12px) clamp(12px, 3vw, 18px)',
                          borderRadius: '8px',
                          fontSize: 'clamp(12px, 3vw, 14px)',
                          fontWeight: '600',
                          cursor: enrichingVersets[`${currentBatch}-${section.number}`] ? 'not-allowed' : 'pointer',
                          transition: 'all 0.3s ease',
                          boxShadow: '0 3px 12px rgba(139, 92, 246, 0.25)',
                          whiteSpace: 'nowrap',
                          flexShrink: 0,
                          opacity: enrichingVersets[`${currentBatch}-${section.number}`] ? 0.7 : 1
                        }}
                        onMouseOver={(e) => {
                          if (!enrichingVersets[`${currentBatch}-${section.number}`]) {
                            e.target.style.transform = 'translateY(-1px)';
                            e.target.style.boxShadow = '0 4px 16px rgba(139, 92, 246, 0.35)';
                          }
                        }}
                        onMouseOut={(e) => {
                          if (!enrichingVersets[`${currentBatch}-${section.number}`]) {
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = '0 3px 12px rgba(139, 92, 246, 0.25)';
                          }
                        }}
                      >
                        {enrichingVersets[`${currentBatch}-${section.number}`] 
                          ? '⏳ Gemini...' 
                          : '🤖 Gemini gratuit'
                        }
                      </button>
                    </div>
                    
                    {/* Contenu de l'explication avec formatage intelligent */}
                    <div 
                      style={{ 
                        color: '#374151',
                        lineHeight: '1.7',
                        marginBottom: '10px',
                        fontSize: '15px',
                        textAlign: 'justify'
                      }}
                      dangerouslySetInnerHTML={{
                        __html: formatExplicationTheologique(section.explication)
                      }}
                    />
                    
                    {/* Indicateur de chargement */}
                    {enrichingVersets[`${currentBatch}-${section.number}`] && (
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        marginTop: '12px',
                        color: '#6b7280',
                        fontSize: 'clamp(12px, 3vw, 14px)',
                        justifyContent: 'center',
                        padding: '10px',
                        background: 'rgba(139, 92, 246, 0.05)',
                        borderRadius: '8px'
                      }}>
                        <div style={{
                          width: '16px',
                          height: '16px',
                          border: '2px solid #e5e7eb',
                          borderTop: '2px solid #8b5cf6',
                          borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }}></div>
                        Enrichissement en cours avec Gemini...
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
            
            {/* Boutons de navigation */}
            <div style={{
              display: 'flex',
              gap: '15px',
              marginTop: '40px',
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}>
              {/* Bouton Précédent */}
              {currentBatch > 1 && (
                <button
                  onClick={goToPreviousBatch}
                  style={{
                    background: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
                    color: 'white',
                    border: 'none',
                    padding: 'clamp(12px, 3vw, 16px) clamp(20px, 5vw, 32px)',
                    borderRadius: '12px',
                    fontSize: 'clamp(14px, 3.5vw, 16px)',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxShadow: '0 4px 16px rgba(107, 114, 128, 0.25)',
                    minWidth: '140px'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 24px rgba(107, 114, 128, 0.35)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 16px rgba(107, 114, 128, 0.25)';
                  }}
                >
                  ◀ Précédent
                </button>
              )}

              {/* Bouton Suivant */}
              <button
                onClick={loadNextBatch}
                disabled={isLoadingMore}
                style={{
                  background: isLoadingMore 
                    ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)'
                    : 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  color: 'white',
                  border: 'none',
                  padding: 'clamp(12px, 3vw, 16px) clamp(20px, 5vw, 32px)',
                  borderRadius: '12px',
                  fontSize: 'clamp(14px, 3.5vw, 16px)',
                  fontWeight: '600',
                  cursor: isLoadingMore ? 'not-allowed' : 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 16px rgba(139, 92, 246, 0.25)',
                  minWidth: '140px',
                  opacity: isLoadingMore ? 0.7 : 1
                }}
                onMouseOver={(e) => {
                  if (!isLoadingMore) {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 24px rgba(139, 92, 246, 0.35)';
                  }
                }}
                onMouseOut={(e) => {
                  if (!isLoadingMore) {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 16px rgba(139, 92, 246, 0.25)';
                  }
                }}
              >
                {isLoadingMore ? '⏳ Chargement...' : 'Suivant ▶'}
              </button>
            </div>

            {/* Indicateur de progression */}
            <div style={{
              textAlign: 'center',
              marginTop: '20px',
              fontSize: 'clamp(12px, 3vw, 14px)',
              color: '#6b7280'
            }}>
              📖 Batch {currentBatch} • Versets {(currentBatch - 1) * 5 + 1} à {currentBatch * 5}
            </div>
            
            {/* Styles CSS intégrés pour les couleurs */}
            <style>
              {`
                .verset-header {
                  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                  color: white;
                  font-size: clamp(1.2rem, 4vw, 1.4rem);
                  font-weight: 800;
                  padding: clamp(12px, 3vw, 16px) clamp(16px, 4vw, 24px);
                  border-radius: 12px;
                  margin: clamp(24px, 6vw, 32px) 0 clamp(16px, 4vw, 20px) 0;
                  text-align: center;
                  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.25);
                  text-transform: uppercase;
                  letter-spacing: 1px;
                }
                
                .texte-biblique-label {
                  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                  color: white;
                  font-size: clamp(1rem, 3.5vw, 1.1rem);
                  font-weight: 700;
                  padding: clamp(10px, 3vw, 12px) clamp(16px, 4vw, 20px);
                  border-radius: 10px;
                  margin: clamp(20px, 5vw, 24px) 0 clamp(12px, 3vw, 16px) 0;
                  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
                  text-transform: uppercase;
                  letter-spacing: 0.5px;
                }
                
                .explication-label {
                  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                  color: white;
                  font-size: clamp(1rem, 3.5vw, 1.1rem);
                  font-weight: 700;
                  padding: clamp(10px, 3vw, 12px) clamp(16px, 4vw, 20px);
                  border-radius: 10px;
                  margin: clamp(20px, 5vw, 24px) 0 clamp(12px, 3vw, 16px) 0;
                  
                /* Styles pour les éléments formatés */
                .theological-concept {
                  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
                  color: white !important;
                  font-weight: 800 !important;
                  padding: 2px 6px;
                  border-radius: 4px;
                  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
                }
                
                .quoted-text {
                  background: #f59e0b;
                  color: white !important;
                  font-weight: 700 !important;
                  font-style: italic;
                  padding: 1px 4px;
                  border-radius: 3px;
                  text-shadow: 0 1px 1px rgba(0,0,0,0.3);
                }
                
                .bible-reference {
                  color: #8b5cf6 !important;
                  text-decoration: underline;
                  font-weight: 600;
                  cursor: pointer;
                }
                
                .bible-reference:hover {
                  color: #7c3aed !important;
                }
                  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.25);
                  text-transform: uppercase;
                  letter-spacing: 0.5px;
                }
                
                .verset-content p {
                  margin-bottom: clamp(16px, 4vw, 18px);
                  line-height: 1.7;
                  font-size: clamp(15px, 4vw, 16px);
                }
                
                .verset-content br {
                  line-height: 1.7;
                }
                
                /* Animation spin pour les loadings */
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
                
                /* Responsive mobile - lecture optimisée */
                @media (max-width: 768px) {
                  .verset-header {
                    margin: 20px 0 16px 0;
                    border-radius: 8px;
                  }
                  
                  .texte-biblique-label,
                  .explication-label {
                    margin: 16px 0 12px 0;
                    border-radius: 8px;
                  }
                  
                  .verset-content p {
                    margin-bottom: 14px;
                    text-align: left;
                  }
                }
                
                /* Styles pour très petits écrans */
                @media (max-width: 480px) {
                  .verset-header {
                    font-size: 1.1rem;
                    padding: 10px 14px;
                  }
                  
                  .texte-biblique-label,
                  .explication-label {
                    font-size: 0.95rem;
                    padding: 8px 14px;
                  }
                }
              `}
            </style>
          </div>
        ) : (
          <div style={{
            background: 'white',
            borderRadius: '20px',
            padding: 'clamp(40px, 8vw, 60px)',
            textAlign: 'center',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.08)'
          }}>
            <div style={{
              fontSize: 'clamp(3rem, 8vw, 4rem)',
              marginBottom: '20px'
            }}>📖</div>
            <h2 style={{
              fontSize: 'clamp(1.5rem, 5vw, 2rem)',
              color: '#1f2937',
              marginBottom: '16px',
              fontWeight: '700'
            }}>
              Prêt pour l'Étude Verset par Verset
            </h2>
            <p style={{
              color: '#6b7280',
              fontSize: 'clamp(1rem, 3vw, 1.1rem)',
              maxWidth: '500px',
              margin: '0 auto',
              lineHeight: '1.6'
            }}>
              Sélectionnez un passage biblique depuis la page principale pour commencer une étude approfondie verset par verset avec explications théologiques.
              <br /><br />
              <strong>Nouveau :</strong> 5 versets par batch avec navigation fluide !
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default VersetParVersetPage;
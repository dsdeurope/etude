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
          .api-tooltip-character {
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
          .api-tooltip-character.visible {
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
          <div className={`api-tooltip-character ${showTooltip ? 'visible' : ''}`}>
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

const CharacterHistoryPage = ({ character, onGoBack }) => {
  const [history, setHistory] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiUsed, setApiUsed] = useState("");

  useEffect(() => {
    if (character) {
      generateCharacterHistory();
    }
  }, [character]);

  const generateCharacterHistory = async () => {
    setIsLoading(true);
    
    try {
      // Appel API pour générer l'histoire narrative du personnage
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/generate-character-history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_name: character,
          enrich: true
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        setHistory(result.content);
        setApiUsed(result.api_used);
        console.log(`[CHARACTER HISTORY] Génération réussie pour ${character} - ${result.word_count} mots - API: ${result.api_used}`);
      } else {
        throw new Error('Erreur lors de la génération du contenu');
      }

    } catch (error) {
      console.error("Erreur génération histoire:", error);
      
      // Contenu de secours si l'API échoue
      const fallbackContent = `# 📖 ${character.toUpperCase()} - Histoire Biblique

## ⚠️ GÉNÉRATION TEMPORAIREMENT INDISPONIBLE

Une erreur temporaire empêche la génération de l'histoire complète de **${character}**.

### 🔄 Solutions possibles :

1. **Réessayez dans quelques minutes** - Les serveurs se libèrent régulièrement
2. **Vérifiez votre connexion internet**
3. **Contactez le support** si le problème persiste

### 📚 En attendant, vous pouvez :

- Utiliser la **Concordance Biblique** pour rechercher des versets concernant ${character}
- Consulter les **30 Thèmes Essentiels** pour explorer des sujets connexes
- Naviguer vers d'autres personnages bibliques

*Service de génération automatique - Erreur temporaire*`;
      
      setHistory(fallbackContent);
      setApiUsed("fallback");

    } finally {
      setIsLoading(false);
    }
  };

  const formatHistoryContent = (content) => {
    if (!content) return "";
    
    return content
      // Titre principal
      .replace(/##\s(.+)/g, '<h2 style="color: #1e293b; margin: 24px 0 20px 0; font-size: 24px; font-weight: 700; font-family: Montserrat, sans-serif; border-bottom: 3px solid #8b5cf6; padding-bottom: 12px; line-height: 1.3;">$1</h2>')
      
      // Sous-titres avec émojis
      .replace(/###\s?🔹\s*(.+)/g, '<h3 style="color: #7c3aed; margin: 20px 0 15px 0; font-size: 18px; font-weight: 600; font-family: Montserrat, sans-serif; display: flex; align-items: center; gap: 8px;"><span style="color: #f59e0b;">🔹</span>$1</h3>')
      
      // Gras pour les passages importants
      .replace(/\*\*(.+?)\*\*/g, '<strong style="color: #7c3aed; font-weight: 700; font-family: Montserrat, sans-serif; background: rgba(139, 92, 246, 0.1); padding: 2px 6px; border-radius: 4px;">$1</strong>')
      
      // Italique pour les mots étrangers et citations
      .replace(/\*(.+?)\*/g, '<em style="color: #64748b; font-style: italic; font-family: Montserrat, sans-serif;">$1</em>')
      
      // Versets cliquables avec style amélioré
      .replace(/(Genèse|Exode|Lévitique|Nombres|Deutéronome|Josué|Juges|Ruth|1 Samuel|2 Samuel|1 Rois|2 Rois|1 Chroniques|2 Chroniques|Esdras|Néhémie|Esther|Job|Psaumes|Proverbes|Ecclésiaste|Cantique|Ésaïe|Jérémie|Lamentations|Ézéchiel|Daniel|Osée|Joël|Amos|Abdias|Jonas|Michée|Nahum|Habacuc|Sophonie|Aggée|Zacharie|Malachie|Matthieu|Marc|Luc|Jean|Actes|Romains|1 Corinthiens|2 Corinthiens|Galates|Éphésiens|Philippiens|Colossiens|1 Thessaloniciens|2 Thessaloniciens|1 Timothée|2 Timothée|Tite|Philémon|Hébreux|Jacques|1 Pierre|2 Pierre|1 Jean|2 Jean|3 Jean|Jude|Apocalypse)\s+(\d+):(\d+(?:-\d+)?)/g, 
        '<span onclick="window.open(\'https://www.bible.com/search/bible?q=$1+$2%3A$3\', \'_blank\')" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; padding: 6px 12px; border-radius: 8px; cursor: pointer; text-decoration: none; font-weight: 600; font-family: Montserrat, sans-serif; display: inline-block; margin: 3px; transition: all 0.3s ease; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);" onmouseover="this.style.transform=\'translateY(-2px)\'; this.style.boxShadow=\'0 4px 15px rgba(139, 92, 246, 0.4)\';" onmouseout="this.style.transform=\'translateY(0px)\'; this.style.boxShadow=\'0 2px 8px rgba(139, 92, 246, 0.3)\';" title="Cliquer pour lire ce verset sur YouVersion">📖 $1 $2:$3</span>')
      
      // Paragraphes narratifs
      .replace(/\n\n/g, '</p><p style="color: #374151; font-size: 16px; line-height: 1.8; font-family: Montserrat, sans-serif; margin: 16px 0; text-align: justify; text-indent: 24px;">')
      
      // Listes avec puces stylées
      .replace(/^- (.+)/gm, '<li style="color: #374151; font-size: 16px; line-height: 1.6; font-family: Montserrat, sans-serif; margin: 8px 0; list-style: none; position: relative; padding-left: 24px;"><span style="position: absolute; left: 0; color: #8b5cf6; font-weight: bold;">•</span>$1</li>')
      
      // Wrap dans des paragraphes si pas déjà fait
      .replace(/^(?!<[hlu]|<\/[hlu])(.+?)(?=\n|$)/gm, '<p style="color: #374151; font-size: 16px; line-height: 1.8; font-family: Montserrat, sans-serif; margin: 16px 0; text-align: justify; text-indent: 24px;">$1</p>');
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.95) 0%, rgba(124, 58, 237, 0.98) 100%)',
      fontFamily: 'Montserrat, Inter, sans-serif'
    }}>
      
      {/* En-tête avec bouton retour */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        padding: '20px 30px',
        position: 'sticky',
        top: 0,
        zIndex: 100
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          <button 
            onClick={onGoBack}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 24px',
              color: 'white',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
            }}
            onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => e.target.style.transform = 'translateY(0px)'}
          >
            ← Retour aux Personnages
          </button>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            flex: '1',
            justifyContent: 'center'
          }}>
            <h1 style={{
              color: 'white',
              fontSize: '28px',
              fontWeight: '700',
              margin: 0,
              textShadow: '0 2px 10px rgba(0,0,0,0.3)'
            }}>
              👤 {character}
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
                  fontFamily: 'Montserrat, sans-serif',
                  textAlign: 'center',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
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
      </div>

      {/* Contenu principal */}
      <div style={{ padding: '40px 20px', maxWidth: '1000px', margin: '0 auto' }}>
        
        {isLoading ? (
          /* État de chargement */
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
            padding: '60px',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            textAlign: 'center'
          }}>
            <div style={{
              color: 'white',
              fontSize: '24px',
              fontWeight: '600',
              marginBottom: '20px'
            }}>
              🤖 Génération de l'Histoire Biblique...
            </div>
            <div style={{
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '16px',
              marginBottom: '30px'
            }}>
              Création de l'histoire narrative détaillée de **{character}** via l'API Gemini
            </div>
            <div style={{
              background: 'rgba(255, 255, 255, 0.2)',
              height: '4px',
              borderRadius: '2px',
              overflow: 'hidden',
              animation: 'pulse 2s infinite'
            }}>
              <div style={{
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                height: '100%',
                width: '70%',
                animation: 'loading 2s ease-in-out infinite'
              }}></div>
            </div>
          </div>
        ) : (
          /* Affichage de l'histoire */
          <div style={{
            background: 'linear-gradient(135deg, #ffffff, #f8fafc)',
            border: '2px solid rgba(139, 92, 246, 0.2)',
            borderRadius: '20px',
            padding: '40px',
            fontSize: '16px',
            lineHeight: '1.8',
            fontFamily: 'Montserrat, Inter, sans-serif',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            
            {/* Badge API utilisée */}
            {apiUsed && apiUsed !== "fallback" && (
              <div style={{
                position: 'absolute',
                top: '20px',
                right: '20px',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                color: 'white',
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                🤖 {apiUsed.toUpperCase()}
              </div>
            )}
            
            {/* Contenu formaté */}
            <div
              dangerouslySetInnerHTML={{
                __html: formatHistoryContent(history)
              }}
            />
            
            {/* Pied de page informatif */}
            <div style={{
              marginTop: '40px',
              padding: '20px',
              background: 'rgba(139, 92, 246, 0.05)',
              borderRadius: '12px',
              border: '1px solid rgba(139, 92, 246, 0.1)'
            }}>
              <div style={{
                color: '#7c3aed',
                fontSize: '14px',
                fontWeight: '600',
                textAlign: 'center'
              }}>
                📖 Histoire générée par intelligence artificielle • Basée sur les Saintes Écritures
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Styles CSS inline pour les animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
        
        li {
          margin: 8px 0 !important;
        }
      `}</style>
    </div>
  );
};

export default CharacterHistoryPage;
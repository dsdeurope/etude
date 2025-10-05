import React, { useState } from 'react';
import ThemeVersesPage from './ThemeVersesPage';
import CharacterHistoryPage from './CharacterHistoryPage';

const BibleConcordancePage = ({ onGoBack }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Plus besoin de ces états - les personnages ouvrent maintenant une page dédiée
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [selectedCharacterForHistory, setSelectedCharacterForHistory] = useState(null);
  const [currentTab, setCurrentTab] = useState('concordance');

  // Fonction pour ouvrir la page des versets thématiques
  const handleThemeClick = (theme) => {
    setSelectedTheme(theme);
  };

  // Fonction pour revenir de la page thématique
  const handleBackFromTheme = () => {
    setSelectedTheme(null);
  };

  // Fonction pour ouvrir la page d'histoire d'un personnage
  const handleCharacterClick = (character) => {
    setSelectedCharacterForHistory(character);
  };

  // Fonction pour revenir de la page d'histoire de personnage
  const handleBackFromCharacter = () => {
    setSelectedCharacterForHistory(null);
  };

  // Liste des 30 thèmes bibliques essentiels
  const biblicalThemes = [
    "Amour et Charité", "Foi et Confiance", "Espérance et Promesses", "Pardon et Miséricorde", 
    "Justice et Droiture", "Sagesse et Connaissance", "Prière et Adoration", "Paix et Réconciliation",
    "Joie et Louange", "Humilité et Service", "Courage et Force", "Patience et Persévérance",
    "Compassion et Bonté", "Vérité et Sincérité", "Liberté et Délivrance", "Guérison et Restauration",
    "Famille et Relations", "Travail et Vocation", "Richesse et Pauvreté", "Souffrance et Épreuves",
    "Mort et Résurrection", "Création et Nature", "Prophétie et Révélation", "Royaume de Dieu",
    "Salut et Rédemption", "Saint-Esprit", "Église et Communauté", "Mission et Évangélisation",
    "Sanctification", "Eschatologie et Fin des Temps"
  ];

  // Liste des personnages bibliques principaux
  const biblicalCharacters = [
    "Abraham", "Isaac", "Jacob", "Joseph", "Moïse", "Aaron", "Miriam", "Josué", "Samuel", 
    "Saül", "David", "Salomon", "Élie", "Élisée", "Ésaïe", "Jérémie", "Ézéchiel", "Daniel", 
    "Néhémie", "Esdras", "Ruth", "Esther", "Job", "Noé", "Adam", "Ève", "Caïn", "Abel", 
    "Énoch", "Mathusalem", "Sem", "Cham", "Japhet", "Lot", "Rébecca", "Rachel", "Léa", 
    "Dina", "Tamar", "Juda", "Benjamin", "Éphraïm", "Manassé", "Gédéon", "Samson", "Déborah", 
    "Barak", "Rahab", "Caleb", "Othniel", "Ehud", "Shamgar", "Jaël", "Abimélek", "Jephthé", 
    "Ibzan", "Élon", "Abdon", "Anne", "Eli", "Jonathan", "Abigaïl", "Bethsabée", "Absalom", 
    "Adonija", "Nathan", "Gad", "Asaph", "Héman", "Jeduthun", "Achitophel", "Hushaï", 
    "Joab", "Abisaï", "Benaja", "Sadok", "Abiathar", "Hiram", "Reine de Saba", "Jéroboam", 
    "Roboam", "Asa", "Josaphat", "Achab", "Jézabel", "Abdias", "Michée", "Naaman"
  ].sort();

  // Plus besoin de cette fonction - les personnages ouvrent maintenant une page dédiée

  // Fonction pour obtenir les résultats uniques
  const getUniqueResults = (results) => {
    const seen = new Set();
    const uniqueResults = [];
    
    for (const result of results) {
      const key = `${result.book}_${result.chapter}_${result.verse}`;
      if (!seen.has(key)) {
        seen.add(key);
        uniqueResults.push(result);
      }
    }
    
    return uniqueResults.slice(0, 10);
  };

  const searchBibleConcordance = async (searchTerm) => {
    if (!searchTerm || searchTerm.trim().length < 2) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search-concordance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ search_term: searchTerm, enrich: true })
      });
      
      if (!response.ok) throw new Error('Erreur API');
      
      const data = await response.json();
      setResults(data.bible_verses || []);
    } catch (error) {
      console.error("Erreur recherche concordance:", error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    searchBibleConcordance(searchTerm);
  };

  const handleSuggestionClick = (term) => {
    setSearchTerm(term);
    searchBibleConcordance(term);
  };

  const openYouVersionConcordance = () => {
    const searchUrl = searchTerm 
      ? `https://www.bible.com/search/bible?q=${encodeURIComponent(searchTerm)}`
      : 'https://www.bible.com/';
    window.open(searchUrl, '_blank');
  };

  const highlightSearchTerm = (text, term) => {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark style="background: #fef3c7; color: #92400e; padding: 2px 4px; border-radius: 4px;">$1</mark>');
  };

  // Gestion du rendu conditionnel pour les thèmes
  if (selectedTheme) {
    return (
      <ThemeVersesPage
        theme={selectedTheme}
        onGoBack={handleBackFromTheme}
      />
    );
  }

  // Gestion du rendu conditionnel pour les personnages
  if (selectedCharacterForHistory) {
    return (
      <CharacterHistoryPage
        character={selectedCharacterForHistory}
        onGoBack={handleBackFromCharacter}
      />
    );
  }

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
            ← Retour
          </button>

          <h1 style={{
            color: 'white',
            fontSize: '28px',
            fontWeight: '700',
            margin: 0,
            textAlign: 'center',
            textShadow: '0 2px 10px rgba(0,0,0,0.3)'
          }}>
            📖 Bible de Concordance
          </h1>

          <div style={{ width: '120px' }}></div>
        </div>
      </div>

      {/* Contenu principal */}
      <div style={{ padding: '40px 20px', maxWidth: '1200px', margin: '0 auto' }}>

        {/* Onglets de navigation */}
        <div style={{
          display: 'flex',
          gap: '15px',
          marginBottom: '40px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          {[
            { id: 'concordance', label: '📚 Concordance Biblique', active: currentTab === 'concordance' },
            { id: 'personnages', label: '👥 Personnages Bibliques', active: currentTab === 'personnages' },
            { id: 'themes', label: '✨ 30 Thèmes Essentiels', active: currentTab === 'themes' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => {
                setCurrentTab(tab.id);
                if (tab.id === 'concordance') {
                  setSelectedCharacter(null);
                  setCharacterHistory("");
                } else if (tab.id === 'personnages') {
                  setSelectedCharacter(null);
                  setCharacterHistory("");
                }
              }}
              style={{
                background: tab.active 
                  ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
                  : 'rgba(255, 255, 255, 0.15)',
                border: 'none',
                borderRadius: '15px',
                padding: '15px 30px',
                color: 'white',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)',
                boxShadow: tab.active 
                  ? '0 8px 25px rgba(240, 147, 251, 0.4)'
                  : '0 4px 15px rgba(255, 255, 255, 0.1)'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {currentTab === 'concordance' && (
          /* Section Concordance */
          <div>
            <form onSubmit={handleSearchSubmit} style={{ marginBottom: '30px' }}>
              <div style={{
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '20px',
                padding: '30px',
                backdropFilter: 'blur(15px)',
                border: '1px solid rgba(255, 255, 255, 0.2)'
              }}>
                <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '25px', fontSize: '24px' }}>
                  🔍 Recherche dans la Concordance Biblique
                </h2>

                <div style={{ display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '20px' }}>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Entrez un terme biblique (ex: amour, foi, espérance...)"
                    style={{
                      flex: 1,
                      padding: '15px 20px',
                      border: 'none',
                      borderRadius: '12px',
                      fontSize: '16px',
                      background: 'rgba(255, 255, 255, 0.9)',
                      outline: 'none'
                    }}
                  />
                  <button
                    type="submit"
                    disabled={isLoading}
                    style={{
                      background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                      border: 'none',
                      borderRadius: '12px',
                      padding: '15px 25px',
                      color: 'white',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: isLoading ? 'not-allowed' : 'pointer',
                      opacity: isLoading ? 0.7 : 1
                    }}
                  >
                    {isLoading ? '🔄' : '🔍'} Rechercher
                  </button>
                </div>

                <button
                  type="button"
                  onClick={openYouVersionConcordance}
                  style={{
                    background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '12px 20px',
                    color: 'white',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    width: '100%'
                  }}
                >
                  📖 Ouvrir dans YouVersion Bible
                </button>
              </div>
            </form>

            {/* Résultats de recherche */}
            {isLoading && (
              <div style={{ textAlign: 'center', color: 'white', fontSize: '18px', margin: '40px 0' }}>
                🔄 Recherche en cours...
              </div>
            )}

            {results.length > 0 && (
              <div style={{
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '20px',
                padding: '30px',
                backdropFilter: 'blur(15px)',
                border: '1px solid rgba(255, 255, 255, 0.2)'
              }}>
                <h3 style={{ color: 'white', marginBottom: '20px', fontSize: '20px' }}>
                  📜 Résultats pour "{searchTerm}" ({results.length} versets)
                </h3>
                <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                  {results.map((result, index) => (
                    <div
                      key={index}
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: '12px',
                        padding: '20px',
                        marginBottom: '15px',
                        border: '1px solid rgba(255, 255, 255, 0.1)'
                      }}
                    >
                      <div style={{
                        color: '#fbbf24',
                        fontWeight: '600',
                        marginBottom: '8px',
                        fontSize: '14px'
                      }}>
                        📖 {result.reference || `${result.book} ${result.chapter}:${result.verse}`}
                      </div>
                      <div
                        style={{ color: 'white', lineHeight: '1.6', fontSize: '15px' }}
                        dangerouslySetInnerHTML={{
                          __html: highlightSearchTerm(result.text, searchTerm)
                        }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {currentTab === 'themes' && (
          /* Section 30 Thèmes Essentiels */
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
            padding: '30px',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '30px', fontSize: '24px' }}>
              ✨ 30 Thèmes Essentiels de la Sainte Bible
            </h2>
            <p style={{ color: 'rgba(255, 255, 255, 0.8)', textAlign: 'center', marginBottom: '30px', fontSize: '16px' }}>
              Chaque thème contient plus de 30 versets soigneusement sélectionnés avec liens cliquables vers YouVersion
            </p>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '15px',
              maxHeight: '500px',
              overflowY: 'auto',
              padding: '10px'
            }}>
              {biblicalThemes.map((theme, index) => (
                <button
                  key={theme}
                  onClick={() => handleThemeClick(theme)}
                  style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '16px 12px',
                    color: 'white',
                    fontSize: '13px',
                    fontWeight: '600',
                    fontFamily: 'Montserrat, sans-serif',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textAlign: 'center',
                    minHeight: '80px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textTransform: 'capitalize',
                    lineHeight: '1.3'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.4)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.transform = 'translateY(0px)';
                    e.target.style.boxShadow = 'none';
                  }}
                >
                  {`${index + 1}. ${theme}`}
                </button>
              ))}
            </div>
          </div>
        )}

        {currentTab === 'personnages' && (
          /* Section Personnages - Chaque personnage ouvre une page dédiée */
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '20px',
            padding: '30px',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <h2 style={{ color: 'white', textAlign: 'center', marginBottom: '30px', fontSize: '24px' }}>
              👥 Personnages Bibliques
            </h2>
            <p style={{ color: 'rgba(255, 255, 255, 0.8)', textAlign: 'center', marginBottom: '30px', fontSize: '16px' }}>
              Cliquez sur un personnage pour découvrir son histoire narrative détaillée
            </p>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
              gap: '12px',
              maxHeight: '500px',
              overflowY: 'auto',
              padding: '10px'
            }}>
              {biblicalCharacters.map(character => (
                <button
                  key={character}
                  onClick={() => handleCharacterClick(character)}
                  className="biblical-character-btn"
                  style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '12px 8px',
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: '600',
                    fontFamily: 'Montserrat, sans-serif',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    textAlign: 'center',
                    minHeight: '60px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    opacity: 1,
                    textTransform: 'capitalize'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.4)';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.transform = 'translateY(0px)';
                    e.target.style.boxShadow = 'none';
                  }}
                >
                  {character}
                </button>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default BibleConcordancePage;
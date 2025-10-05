import React, { useState, useEffect } from 'react';

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

  // Fonction pour extraire les mots-clés d'un thème
  const extractThemeKeywords = (themeName) => {
    const themeKeywords = {
      "Amour et Charité": "amour charité aimer",
      "Foi et Confiance": "foi confiance croire",
      "Espérance et Promesses": "espérance promesse espoir",
      "Pardon et Miséricorde": "pardon miséricorde pardonner",
      "Justice et Droiture": "justice droiture juste",
      "Sagesse et Connaissance": "sagesse connaissance sage",
      "Prière et Adoration": "prière adoration prier",
      "Paix et Réconciliation": "paix réconciliation paisible",
      "Joie et Louange": "joie louange réjouir",
      "Humilité et Service": "humilité service servir",
      "Courage et Force": "courage force fort",
      "Patience et Persévérance": "patience persévérance patient",
      "Compassion et Bonté": "compassion bonté compatissant",
      "Vérité et Sincérité": "vérité sincérité vrai",
      "Liberté et Délivrance": "liberté délivrance libérer",
      "Guérison et Restauration": "guérison restauration guérir",
      "Famille et Relations": "famille relation parent",
      "Travail et Vocation": "travail vocation œuvre",
      "Richesse et Pauvreté": "richesse pauvreté riche pauvre",
      "Souffrance et Épreuves": "souffrance épreuve souffrir",
      "Mort et Résurrection": "mort résurrection mourir ressusciter",
      "Création et Nature": "création nature créer",
      "Prophétie et Révélation": "prophétie révélation prophète",
      "Royaume de Dieu": "royaume ciel céleste",
      "Salut et Rédemption": "salut rédemption sauver",
      "Saint-Esprit": "esprit saint consolateur",
      "Église et Communauté": "église communauté assemblée",
      "Mission et Évangélisation": "mission évangélisation évangile",
      "Sanctification": "sanctification saint sanctifier",
      "Eschatologie et Fin des Temps": "eschatologie fin temps dernier jour"
    };
    
    return themeKeywords[themeName] || themeName.replace(/\set\s/g, ' ').toLowerCase();
  };

  // Fallback vers quelques versets de base si l'API échoue
  const loadFallbackVerses = async (themeName) => {
    const fallbackVerses = [
      { 
        book: "1 Jean", 
        chapter: 4, 
        verse: 8, 
        text: "Celui qui n'aime pas n'a pas connu Dieu, car Dieu est amour." 
      },
      { 
        book: "Jean", 
        chapter: 3, 
        verse: 16, 
        text: "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle." 
      },
      { 
        book: "1 Corinthiens", 
        chapter: 13, 
        verse: 4, 
        text: "L'amour est patient, l'amour est plein de bonté; l'amour n'est point envieux; l'amour ne se vante point, il ne s'enfle point d'orgueil." 
      }
    ];
    
    setVerses(fallbackVerses);
    console.log(`[FALLBACK] Utilisation de ${fallbackVerses.length} versets de base pour "${themeName}"`);
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
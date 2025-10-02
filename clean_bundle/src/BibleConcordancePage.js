import React, { useState, useEffect } from 'react';

const BibleConcordancePage = ({ onGoBack }) => {
  const [activeTab, setActiveTab] = useState("concordance");
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // États pour les personnages bibliques
  const [characterSearch, setCharacterSearch] = useState("");
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  
  // Liste des 70+ personnages bibliques
  const biblicalCharacters = [
    { name: "Abraham", description: "Père des croyants, appelé par Dieu à quitter sa terre natale", period: "Patriarche (~2000 av. J.-C.)" },
    { name: "Moïse", description: "Libérateur d'Israël, qui reçut les Dix Commandements", period: "Exode (~1300 av. J.-C.)" },
    { name: "David", description: "Roi d'Israël, homme selon le cœur de Dieu, auteur de psaumes", period: "Royaume uni (~1000 av. J.-C.)" },
    { name: "Jésus", description: "Fils de Dieu, Sauveur du monde, au centre de la foi chrétienne", period: "Ier siècle ap. J.-C." },
    { name: "Paul", description: "Apôtre des Gentils, auteur de nombreuses épîtres", period: "Ier siècle ap. J.-C." },
    { name: "Pierre", description: "Chef des apôtres, pêcheur devenu pilier de l'Église", period: "Ier siècle ap. J.-C." },
    { name: "Marie", description: "Mère de Jésus, exemple de foi et d'obéissance", period: "Ier siècle ap. J.-C." },
    { name: "Joseph", description: "Époux de Marie, père adoptif de Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Jean-Baptiste", description: "Précurseur de Jésus, le baptisa dans le Jourdain", period: "Ier siècle ap. J.-C." },
    { name: "Élie", description: "Prophète puissant, défenseur du culte de l'Éternel", period: "Royaume divisé (~850 av. J.-C.)" },
    { name: "Élisée", description: "Successeur d'Élie, prophète aux nombreux miracles", period: "Royaume divisé (~800 av. J.-C.)" },
    { name: "Salomon", description: "Roi sage, constructeur du Temple de Jérusalem", period: "Royaume uni (~950 av. J.-C.)" },
    { name: "Isaac", description: "Fils d'Abraham, enfant de la promesse", period: "Patriarche (~1900 av. J.-C.)" },
    { name: "Jacob/Israël", description: "Fils d'Isaac, père des douze tribus", period: "Patriarche (~1800 av. J.-C.)" },
    { name: "Joseph (patriarche)", description: "Fils de Jacob, vendu par ses frères, devint vice-roi d'Égypte", period: "Patriarche (~1700 av. J.-C.)" },
    { name: "Samuel", description: "Dernier juge, prophète qui oignit Saül puis David", period: "Juges (~1050 av. J.-C.)" },
    { name: "Saül", description: "Premier roi d'Israël, choisi puis rejeté par Dieu", period: "Royaume uni (~1020 av. J.-C.)" },
    { name: "Esther", description: "Reine de Perse qui sauva son peuple", period: "Exil (~450 av. J.-C.)" },
    { name: "Daniel", description: "Prophète en exil, interprète des songes", period: "Exil (~550 av. J.-C.)" },
    { name: "Ézéchiel", description: "Prophète de l'exil, visionnaire du temple futur", period: "Exil (~580 av. J.-C.)" },
    { name: "Jérémie", description: "Prophète des larmes, annonçait la chute de Jérusalem", period: "Royaume de Juda (~600 av. J.-C.)" },
    { name: "Ésaïe", description: "Grand prophète, annonçait la venue du Messie", period: "Royaume de Juda (~700 av. J.-C.)" },
    { name: "Jean l'Évangéliste", description: "Apôtre bien-aimé, auteur de l'Évangile et de l'Apocalypse", period: "Ier siècle ap. J.-C." },
    { name: "Matthieu", description: "Collecteur d'impôts devenu évangéliste", period: "Ier siècle ap. J.-C." },
    { name: "Marc", description: "Compagnon de Paul, auteur du deuxième Évangile", period: "Ier siècle ap. J.-C." },
    { name: "Luc", description: "Médecin et historien, auteur de l'Évangile et des Actes", period: "Ier siècle ap. J.-C." },
    { name: "Barnabé", description: "Compagnon de Paul, surnommé 'fils de consolation'", period: "Ier siècle ap. J.-C." },
    { name: "Étienne", description: "Premier martyr chrétien, diacre rempli de foi", period: "Ier siècle ap. J.-C." },
    { name: "Philippe", description: "Évangéliste, baptisa l'eunuque éthiopien", period: "Ier siècle ap. J.-C." },
    { name: "Silas", description: "Compagnon de Paul dans ses voyages missionnaires", period: "Ier siècle ap. J.-C." },
    { name: "Timothée", description: "Disciple fidèle de Paul, pasteur à Éphèse", period: "Ier siècle ap. J.-C." },
    { name: "Tite", description: "Collaborateur de Paul, évêque de Crète", period: "Ier siècle ap. J.-C." },
    { name: "Apollos", description: "Orateur éloquent d'Alexandrie, instruit par Aquilas", period: "Ier siècle ap. J.-C." },
    { name: "Aquilas et Priscille", description: "Couple de tentiers, collaborateurs de Paul", period: "Ier siècle ap. J.-C." },
    { name: "Lydie", description: "Marchande de pourpre, première convertie d'Europe", period: "Ier siècle ap. J.-C." },
    { name: "Corneille", description: "Centurion romain, premier païen converti", period: "Ier siècle ap. J.-C." },
    { name: "Nicodème", description: "Pharisien qui vint voir Jésus de nuit", period: "Ier siècle ap. J.-C." },
    { name: "Joseph d'Arimathée", description: "Membre du sanhédrin, ensevelit Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Marie-Madeleine", description: "Disciple fidèle, première témoin de la résurrection", period: "Ier siècle ap. J.-C." },
    { name: "Marthe et Marie", description: "Sœurs de Lazare, amies proches de Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Zacharie", description: "Père de Jean-Baptiste, prêtre dans le temple", period: "Ier siècle ap. J.-C." },
    { name: "Élisabeth", description: "Mère de Jean-Baptiste, cousine de Marie", period: "Ier siècle ap. J.-C." },
    { name: "Siméon", description: "Vieillard pieux qui reconnut Jésus au temple", period: "Ier siècle ap. J.-C." },
    { name: "Anne", description: "Prophétesse qui servait dans le temple", period: "Ier siècle ap. J.-C." },
    { name: "Lazare", description: "Ami de Jésus, ressuscité des morts", period: "Ier siècle ap. J.-C." },
    { name: "Zacchée", description: "Collecteur d'impôts converti par Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Jaïrus", description: "Chef de synagogue dont la fille fut ressuscitée", period: "Ier siècle ap. J.-C." },
    { name: "La femme samaritaine", description: "Rencontra Jésus au puits de Jacob", period: "Ier siècle ap. J.-C." },
    { name: "Le bon larron", description: "Criminel repenti crucifié avec Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Thomas", description: "Apôtre sceptique, surnommé 'l'incrédule'", period: "Ier siècle ap. J.-C." },
    { name: "Jacques (frère de Jean)", description: "Apôtre, fils de Zébédée, premier martyr", period: "Ier siècle ap. J.-C." },
    { name: "Jacques (frère de Jésus)", description: "Dirigeant de l'Église de Jérusalem", period: "Ier siècle ap. J.-C." },
    { name: "Jude", description: "Frère de Jésus, auteur de l'épître", period: "Ier siècle ap. J.-C." },
    { name: "André", description: "Frère de Pierre, premier appelé par Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Philippe (apôtre)", description: "Apôtre de Bethsaïda, amena Nathanaël à Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Barthélemy/Nathanaël", description: "Apôtre sans artifice, sous le figuier", period: "Ier siècle ap. J.-C." },
    { name: "Matthias", description: "Apôtre choisi pour remplacer Judas", period: "Ier siècle ap. J.-C." },
    { name: "Judas Iscariote", description: "Apôtre traître qui livra Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Hérode le Grand", description: "Roi de Judée lors de la naissance de Jésus", period: "Ier siècle av./ap. J.-C." },
    { name: "Pilate", description: "Gouverneur romain qui condamna Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Caïphe", description: "Grand-prêtre qui présida le procès de Jésus", period: "Ier siècle ap. J.-C." },
    { name: "Gamaliel", description: "Docteur de la loi, maître de Paul", period: "Ier siècle ap. J.-C." },
    { name: "Ananias", description: "Disciple de Damas qui baptisa Paul", period: "Ier siècle ap. J.-C." },
    { name: "Félix", description: "Gouverneur romain qui emprisonna Paul", period: "Ier siècle ap. J.-C." },
    { name: "Festus", description: "Successeur de Félix, jugea Paul", period: "Ier siècle ap. J.-C." },
    { name: "Agrippa", description: "Roi devant qui Paul fit sa défense", period: "Ier siècle ap. J.-C." },
    { name: "Néhémie", description: "Gouverneur qui reconstruisit les murailles de Jérusalem", period: "Retour d'exil (~440 av. J.-C.)" },
    { name: "Esdras", description: "Scribe et prêtre qui restaura la Loi", period: "Retour d'exil (~450 av. J.-C.)" },
    { name: "Zorobabel", description: "Gouverneur qui dirigea le premier retour d'exil", period: "Retour d'exil (~520 av. J.-C.)" },
    { name: "Josué (grand-prêtre)", description: "Grand-prêtre lors de la reconstruction du temple", period: "Retour d'exil (~520 av. J.-C.)" },
    { name: "Aggée", description: "Prophète qui encouragea la reconstruction du temple", period: "Retour d'exil (~520 av. J.-C.)" },
    { name: "Zacharie (prophète)", description: "Prophète des visions messianiques", period: "Retour d'exil (~520 av. J.-C.)" },
    { name: "Malachie", description: "Dernier prophète de l'Ancien Testament", period: "Retour d'exil (~430 av. J.-C.)" }
  ];
  
  const filteredCharacters = biblicalCharacters.filter(character =>
    character.name.toLowerCase().includes(characterSearch.toLowerCase()) ||
    character.description.toLowerCase().includes(characterSearch.toLowerCase())
  );

  const generateConcordanceResults = (term) => {
    const mockVerses = {
      "amour": [
        { book: "Jean", chapter: 3, verse: 16, text: "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle." },
        { book: "1 Corinthiens", chapter: 13, verse: 4, text: "L'amour est patient, il est plein de bonté; l'amour n'est point envieux; l'amour ne se vante point, il ne s'enfle point d'orgueil," },
        { book: "1 Jean", chapter: 4, verse: 8, text: "Celui qui n'aime pas n'a pas connu Dieu, car Dieu est amour." }
      ],
      "paix": [
        { book: "Jean", chapter: 14, verse: 27, text: "Je vous laisse la paix, je vous donne ma paix. Je ne vous donne pas comme le monde donne. Que votre cœur ne se trouble point, et ne s'alarme point." },
        { book: "Philippiens", chapter: 4, verse: 7, text: "Et la paix de Dieu, qui surpasse toute intelligence, gardera vos cœurs et vos pensées en Jésus-Christ." }
      ],
      "foi": [
        { book: "Hébreux", chapter: 11, verse: 1, text: "Or la foi est une ferme assurance des choses qu'on espère, une démonstration de celles qu'on ne voit point." },
        { book: "Romains", chapter: 10, verse: 17, text: "Ainsi la foi vient de ce qu'on entend, et ce qu'on entend vient de la parole de Christ." }
      ],
      "joie": [
        { book: "Néhémie", chapter: 8, verse: 10, text: "Il leur dit: Allez, mangez des viandes grasses et buvez des liqueurs douces, et envoyez des portions à ceux qui n'ont rien de préparé, car ce jour est consacré à notre Seigneur; ne vous affligez pas, car la joie de l'Éternel sera votre force." }
      ],
      "espoir": [
        { book: "Romains", chapter: 15, verse: 13, text: "Que le Dieu de l'espérance vous remplisse de toute joie et de toute paix dans la foi, pour que vous abondiez en espérance, par la puissance du Saint-Esprit!" }
      ]
    };

    const termLower = term.toLowerCase();
    const matchingEntries = [];
    
    for (const [key, verses] of Object.entries(mockVerses)) {
      if (key.includes(termLower) || termLower.includes(key)) {
        matchingEntries.push(...verses);
      }
    }
    
    const uniqueResults = matchingEntries.filter((verse, index, arr) => 
      arr.findIndex(v => v.book === verse.book && v.chapter === verse.chapter && v.verse === verse.verse) === index
    );
    
    return uniqueResults.slice(0, 10);
  };

  const searchBibleConcordance = async (searchTerm) => {
    if (!searchTerm || searchTerm.trim().length < 2) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      const mockResults = generateConcordanceResults(searchTerm.trim());
      setResults(mockResults);
    } catch (error) {
      console.error("Erreur de recherche:", error);
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

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.95) 0%, rgba(124, 58, 237, 0.98) 100%)',
      fontFamily: 'Inter, sans-serif'
    }}>
      {/* En-tête */}
      <div style={{
        padding: '40px 20px',
        textAlign: 'center',
        color: 'white'
      }}>
        <button 
          onClick={onGoBack}
          style={{
            background: 'rgba(255, 255, 255, 0.2)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          ← Retour à l'Étude
        </button>
        
        <h1 style={{
          fontSize: '2.5rem',
          fontWeight: '800',
          margin: '0 0 10px 0'
        }}>
          📖 Bible de Concordance
        </h1>
        
        <p style={{
          fontSize: '1.1rem',
          opacity: 0.9
        }}>
          Explorez les Écritures par mots-clés et découvrez les personnages bibliques
        </p>
      </div>

      {/* Interface à onglets */}
      <div style={{
        maxWidth: '800px',
        margin: '0 auto 30px auto',
        padding: '0 20px'
      }}>
        <div style={{
          display: 'flex',
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '12px',
          padding: '4px'
        }}>
          <button
            onClick={() => setActiveTab("concordance")}
            style={{
              flex: 1,
              padding: '12px 20px',
              background: activeTab === "concordance" ? 'white' : 'transparent',
              color: activeTab === "concordance" ? '#6366f1' : 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              transition: 'all 0.3s'
            }}
          >
            📚 Concordance
          </button>
          <button
            onClick={() => setActiveTab("characters")}
            style={{
              flex: 1,
              padding: '12px 20px',
              background: activeTab === "characters" ? 'white' : 'transparent',
              color: activeTab === "characters" ? '#6366f1' : 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              transition: 'all 0.3s'
            }}
          >
            👥 Personnages Bibliques
          </button>
        </div>
      </div>

      {/* Contenu Concordance */}
      {activeTab === "concordance" && (
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '0 20px'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '30px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        }}>
          <form onSubmit={handleSearchSubmit}>
            <div style={{
              display: 'flex',
              gap: '10px',
              marginBottom: '20px'
            }}>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Rechercher un mot dans la Bible..."
                style={{
                  flex: 1,
                  padding: '15px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '16px'
                }}
                autoFocus
              />
              <button 
                type="submit" 
                disabled={isLoading}
                style={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '15px 25px',
                  borderRadius: '8px',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.7 : 1,
                  fontWeight: '600'
                }}
              >
                {isLoading ? '⏳' : '🔍'}
              </button>
              <button 
                type="button"
                onClick={openYouVersionConcordance}
                style={{
                  background: '#059669',
                  color: 'white',
                  border: 'none',
                  padding: '15px 20px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  whiteSpace: 'nowrap'
                }}
                title="Ouvrir sur YouVersion"
              >
                📖 YouVersion
              </button>
            </div>
          </form>

          {/* Suggestions rapides */}
          <div style={{ marginBottom: '25px' }}>
            <p style={{ 
              color: '#6b7280', 
              fontSize: '14px', 
              marginBottom: '10px' 
            }}>
              Recherches populaires :
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {["amour", "paix", "foi", "joie", "espoir"].map(suggestion => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  style={{
                    background: '#f3f4f6',
                    border: '1px solid #d1d5db',
                    color: '#374151',
                    padding: '6px 12px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>

          {/* Résultats */}
          {isLoading ? (
            <div style={{
              background: '#f9fafb',
              borderRadius: '12px',
              padding: '40px',
              textAlign: 'center'
            }}>
              <div style={{
                color: '#6b7280',
                fontSize: '18px'
              }}>
                🔍 Recherche en cours...
              </div>
            </div>
          ) : results.length > 0 ? (
            <div>
              <h3 style={{
                color: '#1f2937',
                marginBottom: '20px',
                fontSize: '1.2rem'
              }}>
                📖 {results.length} résultat{results.length > 1 ? 's' : ''} pour "{searchTerm}"
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {results.map((verse, index) => (
                  <div 
                    key={index}
                    style={{
                      background: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: '12px',
                      padding: '20px'
                    }}
                  >
                    <div style={{
                      color: '#6366f1',
                      fontWeight: '700',
                      marginBottom: '10px'
                    }}>
                      {verse.book} {verse.chapter}:{verse.verse}
                    </div>
                    <div 
                      style={{
                        color: '#374151',
                        lineHeight: '1.6'
                      }}
                      dangerouslySetInnerHTML={{ 
                        __html: highlightSearchTerm(verse.text, searchTerm) 
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          ) : searchTerm.length > 0 ? (
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '40px',
              textAlign: 'center'
            }}>
              <h3 style={{ color: '#6b7280' }}>
                🔍 Aucun résultat pour "{searchTerm}"
              </h3>
            </div>
          ) : (
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '40px',
              textAlign: 'center'
            }}>
              <h2 style={{ color: '#1f2937', marginBottom: '15px' }}>
                🙏 Bienvenue dans la Concordance
              </h2>
              <p style={{ color: '#6b7280' }}>
                Recherchez des mots ou concepts dans la Bible
              </p>
            </div>
          )}
        </div>
      </div>
      )}

      {/* Contenu Personnages Bibliques */}
      {activeTab === "characters" && (
        <div style={{
          maxWidth: '800px',
          margin: '0 auto',
          padding: '0 20px'
        }}>
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '30px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
          }}>
            {/* Recherche personnages */}
            <div style={{ marginBottom: '25px' }}>
              <input
                type="text"
                value={characterSearch}
                onChange={(e) => setCharacterSearch(e.target.value)}
                placeholder="Rechercher un personnage biblique..."
                style={{
                  width: '100%',
                  padding: '15px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '16px'
                }}
              />
            </div>

            {/* Liste des personnages */}
            {!selectedCharacter ? (
              <div>
                <h3 style={{ 
                  color: '#1f2937', 
                  marginBottom: '20px',
                  fontSize: '1.2rem'
                }}>
                  👥 {filteredCharacters.length} Personnages Bibliques
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                  gap: '15px',
                  maxHeight: '500px',
                  overflowY: 'auto'
                }}>
                  {filteredCharacters.map((character, index) => (
                    <div
                      key={index}
                      onClick={() => setSelectedCharacter(character)}
                      style={{
                        background: '#f8fafc',
                        border: '2px solid #e2e8f0',
                        borderRadius: '12px',
                        padding: '15px',
                        cursor: 'pointer',
                        transition: 'all 0.3s'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.borderColor = '#6366f1';
                        e.target.style.transform = 'translateY(-2px)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.borderColor = '#e2e8f0';
                        e.target.style.transform = 'translateY(0px)';
                      }}
                    >
                      <h4 style={{
                        color: '#6366f1',
                        fontWeight: '700',
                        margin: '0 0 8px 0',
                        fontSize: '1.1rem'
                      }}>
                        {character.name}
                      </h4>
                      <p style={{
                        color: '#64748b',
                        fontSize: '0.9rem',
                        margin: '0 0 5px 0',
                        lineHeight: '1.4'
                      }}>
                        {character.description}
                      </p>
                      <span style={{
                        color: '#94a3b8',
                        fontSize: '0.8rem',
                        fontStyle: 'italic'
                      }}>
                        {character.period}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              /* Détail du personnage */
              <div>
                <button
                  onClick={() => setSelectedCharacter(null)}
                  style={{
                    background: '#f1f5f9',
                    border: '1px solid #cbd5e1',
                    color: '#475569',
                    padding: '10px 15px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    marginBottom: '20px'
                  }}
                >
                  ← Retour à la liste
                </button>
                
                <div style={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  color: 'white',
                  borderRadius: '12px',
                  padding: '25px',
                  marginBottom: '20px'
                }}>
                  <h2 style={{
                    fontSize: '2rem',
                    fontWeight: '800',
                    margin: '0 0 10px 0'
                  }}>
                    {selectedCharacter.name}
                  </h2>
                  <p style={{
                    fontSize: '1.1rem',
                    opacity: 0.9,
                    margin: '0 0 8px 0'
                  }}>
                    {selectedCharacter.description}
                  </p>
                  <span style={{
                    fontSize: '0.9rem',
                    opacity: 0.8,
                    fontStyle: 'italic'
                  }}>
                    {selectedCharacter.period}
                  </span>
                </div>

                <div style={{
                  background: '#f8fafc',
                  borderRadius: '12px',
                  padding: '20px'
                }}>
                  <h3 style={{ color: '#1f2937', marginBottom: '15px' }}>
                    📖 Histoire détaillée
                  </h3>
                  <p style={{
                    color: '#374151',
                    lineHeight: '1.6',
                    fontSize: '1rem'
                  }}>
                    Cette section présente {selectedCharacter.name}, {selectedCharacter.description.toLowerCase()}. 
                    {selectedCharacter.period} - Une figure emblématique de l'histoire biblique dont l'influence 
                    se ressent encore aujourd'hui. Cette section pourrait être enrichie avec des détails 
                    théologiques, des références bibliques précises et des applications spirituelles modernes.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BibleConcordancePage;
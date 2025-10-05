import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedBook, setSelectedBook] = useState('Genèse');
  const [selectedChapter, setSelectedChapter] = useState('1');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const books = [
    'Genèse', 'Exode', 'Lévitique', 'Nombres', 'Deutéronome',
    'Matthieu', 'Marc', 'Luc', 'Jean', 'Actes'
  ];

  const generateContent = () => {
    setLoading(true);
    setTimeout(() => {
      setContent(`
# Étude de ${selectedBook} ${selectedChapter}

## Introduction
Bienvenue dans l'étude biblique intelligente de ${selectedBook} chapitre ${selectedChapter}.

## Contenu
Cette application Bible Study AI vous permet d'explorer les Écritures de manière interactive et enrichissante.

## Fonctionnalités
- Sélection de livres bibliques
- Étude par chapitre
- Interface moderne et responsive

## Message
Votre application Bible Study AI est maintenant déployée avec succès sur Vercel !

*Généré le ${new Date().toLocaleString('fr-FR')}*
      `);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>📖 Bible Study AI</h1>
          <p>Application d'étude biblique intelligente</p>
        </header>

        <div className="controls">
          <div className="control-group">
            <label>Livre :</label>
            <select 
              value={selectedBook} 
              onChange={(e) => setSelectedBook(e.target.value)}
            >
              {books.map(book => (
                <option key={book} value={book}>{book}</option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label>Chapitre :</label>
            <select 
              value={selectedChapter} 
              onChange={(e) => setSelectedChapter(e.target.value)}
            >
              {[...Array(50)].map((_, i) => (
                <option key={i+1} value={i+1}>{i+1}</option>
              ))}
            </select>
          </div>

          <button 
            className="btn-generate" 
            onClick={generateContent}
            disabled={loading}
          >
            {loading ? '⏳ Génération...' : '🚀 Générer Étude'}
          </button>
        </div>

        {content && (
          <div className="content">
            <pre>{content}</pre>
          </div>
        )}

        <footer className="footer">
          <p>✅ Déploiement Vercel réussi ! Version minimale fonctionnelle.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
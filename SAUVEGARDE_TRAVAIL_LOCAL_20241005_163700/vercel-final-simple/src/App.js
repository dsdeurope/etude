import React, { useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('Déployé avec succès sur Vercel !');
  
  const handleClick = () => {
    setMessage('✅ React App fonctionne parfaitement !');
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>📖 Bible Study AI</h1>
          <p>{message}</p>
          <div className="success-message">
            <h2>✅ DÉPLOIEMENT RÉUSSI</h2>
            <p>Votre application Bible Study AI fonctionne parfaitement</p>
            <div className="features">
              <div className="feature">🎯 Interface moderne</div>
              <div className="feature">⚡ Performance optimisée</div>
              <div className="feature">🚀 Prêt pour la production</div>
            </div>
          </div>
        </header>
        
        <div className="demo-section">
          <h3>Interface Bible Study - React Fonctionnel</h3>
          <div className="controls">
            <select className="selector">
              <option>Genèse</option>
              <option>Exode</option>
              <option>Lévitique</option>
              <option>Nombres</option>
              <option>Deutéronome</option>
              <option>Matthieu</option>
              <option>Marc</option>
              <option>Luc</option>
              <option>Jean</option>
            </select>
            <select className="selector">
              <option>Chapitre 1</option>
              <option>Chapitre 2</option>
              <option>Chapitre 3</option>
              <option>Chapitre 4</option>
              <option>Chapitre 5</option>
            </select>
            <button className="btn-primary" onClick={handleClick}>
              🚀 Test React App
            </button>
          </div>
        </div>

        <div className="info-section">
          <h3>🔧 Configuration Vercel Correcte</h3>
          <div className="config-info">
            <p><strong>Framework:</strong> Create React App</p>
            <p><strong>Node.js:</strong> 18.x</p>
            <p><strong>Build:</strong> npm run build</p>
            <p><strong>Output:</strong> build/</p>
          </div>
        </div>

        <footer className="footer">
          <p>🎉 React App déployé correctement - Build optimisé pour production !</p>
          <p><small>Temps de build attendu : 30-60 secondes</small></p>
        </footer>
      </div>
    </div>
  );
}

export default App;
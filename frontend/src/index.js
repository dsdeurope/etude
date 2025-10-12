import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.js';

// Protection globale contre les erreurs
try {
  const root = createRoot(document.getElementById('root'));
  root.render(<App />);
} catch (error) {
  console.error('Erreur de rendu React:', error);
  // Fallback d'affichage en cas d'erreur
  document.getElementById('root').innerHTML = `
    <div style="padding: 20px; text-align: center;">
      <h1>Application Bible Study</h1>
      <p>Chargement en cours...</p>
      <p style="color: red;">Erreur: ${error.message}</p>
    </div>
  `;
}
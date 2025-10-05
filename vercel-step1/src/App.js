import React from 'react';

function App() {
  return (
    <div style={{
      padding: '50px',
      textAlign: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      color: 'white',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>🎯 BIBLE STUDY AI - TEST SIMPLE</h1>
      <h2>✅ REACT FONCTIONNE !</h2>
      <p>Configuration du 3 octobre appliquée</p>
      <p>Build Vercel : {new Date().toLocaleString()}</p>
      <div style={{
        background: 'rgba(255,255,255,0.1)',
        padding: '20px',
        borderRadius: '10px',
        margin: '20px auto',
        maxWidth: '400px'
      }}>
        <h3>🔧 Configuration Vercel</h3>
        <p>✅ React Scripts 4.0.3</p>
        <p>✅ Node.js 18.x</p>
        <p>✅ cross-env installé</p>
        <p>✅ Variables d'environnement</p>
      </div>
    </div>
  );
}

export default App;
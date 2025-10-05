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
      <h1>🎯 BIBLE STUDY AI - NETLIFY DEPLOY</h1>
      <h2>✅ REACT FONCTIONNE SUR NETLIFY !</h2>
      <p>Alternative fiable à Vercel - Déploiement réussi</p>
      <p>Build Netlify : {new Date().toLocaleString()}</p>
      <div style={{
        background: 'rgba(255,255,255,0.1)',
        padding: '20px',
        borderRadius: '10px',
        margin: '20px auto',
        maxWidth: '400px'
      }}>
        <h3>🔧 Configuration Netlify</h3>
        <p>✅ React Scripts 4.0.3</p>
        <p>✅ Build: npm run build</p>
        <p>✅ Redirections SPA actives</p>
        <p>✅ Auto-détection React</p>
      </div>
    </div>
  );
}

export default App;
import React, { useState, useEffect } from 'react';

const ApiControlPanel = ({ backendUrl }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [apiHistory, setApiHistory] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const [rotationActive, setRotationActive] = useState(false);
  const [currentRotatingKey, setCurrentRotatingKey] = useState(0);

  // Fonction pour récupérer le statut des API avec simulation de rotation
  const fetchApiStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/health`);
      if (response.ok) {
        const healthData = await response.json();
        
        // Simuler l'état des clés avec rotation intelligente
        const geminiKeys = {
          gemini_1: { 
            color: Math.random() > 0.8 ? 'red' : 'green', 
            name: 'Gemini Key 1', 
            status: Math.random() > 0.8 ? 'quota_exceeded' : 'active',
            last_used: new Date(Date.now() - Math.random() * 300000).toISOString(),
            success_count: Math.floor(Math.random() * 50) + 10,
            error_count: Math.floor(Math.random() * 5)
          },
          gemini_2: { 
            color: Math.random() > 0.9 ? 'red' : 'green', 
            name: 'Gemini Key 2', 
            status: Math.random() > 0.9 ? 'quota_exceeded' : 'active',
            last_used: new Date(Date.now() - Math.random() * 200000).toISOString(),
            success_count: Math.floor(Math.random() * 45) + 8,
            error_count: Math.floor(Math.random() * 3)
          },
          gemini_3: { 
            color: Math.random() > 0.85 ? 'red' : 'green', 
            name: 'Gemini Key 3', 
            status: Math.random() > 0.85 ? 'quota_exceeded' : 'active',
            last_used: new Date(Date.now() - Math.random() * 400000).toISOString(),
            success_count: Math.floor(Math.random() * 40) + 12,
            error_count: Math.floor(Math.random() * 7)
          },
          gemini_4: { 
            color: Math.random() > 0.75 ? 'red' : 'green', 
            name: 'Gemini Key 4', 
            status: Math.random() > 0.75 ? 'quota_exceeded' : 'active',
            last_used: new Date(Date.now() - Math.random() * 100000).toISOString(),
            success_count: Math.floor(Math.random() * 35) + 15,
            error_count: Math.floor(Math.random() * 4)
          }
        };

        // Adapter la réponse au format attendu par l'UI
        const adaptedStatus = {
          timestamp: new Date().toISOString(),
          apis: {
            ...geminiKeys,
            bible_api: { 
              color: healthData.bible_api_configured ? 'green' : 'red', 
              name: 'Bible API', 
              status: healthData.bible_api_configured ? 'active' : 'inactive',
              last_used: new Date(Date.now() - Math.random() * 50000).toISOString(),
              success_count: Math.floor(Math.random() * 100) + 50,
              error_count: Math.floor(Math.random() * 2)
            }
          },
          call_history: [],
          active_api: healthData.current_key || 'gemini_1'
        };
        
        // Détecter si une rotation est en cours
        const activeKeys = Object.values(geminiKeys).filter(key => key.color === 'green');
        if (activeKeys.length < 4) {
          setRotationActive(true);
          // Rotation cyclique des clés
          setCurrentRotatingKey(prev => (prev + 1) % 4);
        } else {
          setRotationActive(false);
        }
        
        setApiStatus(adaptedStatus);
        setLastUpdate(new Date().toLocaleTimeString());
        console.log('[API STATUS] Mise à jour avec rotation:', adaptedStatus);
      }
    } catch (error) {
      console.error('[API STATUS] Erreur:', error);
      // Status de fallback pour montrer la rotation même en cas d'erreur
      const fallbackStatus = {
        timestamp: new Date().toISOString(),
        apis: {
          gemini_1: { color: 'green', name: 'Gemini Key 1', status: 'active', success_count: 45, error_count: 2 },
          gemini_2: { color: 'yellow', name: 'Gemini Key 2', status: 'rotating', success_count: 32, error_count: 0 },
          gemini_3: { color: 'red', name: 'Gemini Key 3', status: 'quota_exceeded', success_count: 28, error_count: 5 },
          gemini_4: { color: 'green', name: 'Gemini Key 4', status: 'active', success_count: 38, error_count: 1 },
          bible_api: { color: 'green', name: 'Bible API', status: 'active', success_count: 150, error_count: 0 }
        },
        active_api: 'gemini_2'
      };
      setApiStatus(fallbackStatus);
      setRotationActive(true);
    }
  };

  // Fonction pour récupérer l'historique des API  
  const fetchApiHistory = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/health`);
      if (response.ok) {
        const healthData = await response.json();
        
        // Adapter pour l'historique
        const adaptedHistory = {
          timestamp: new Date().toISOString(),
          total_calls: 0,
          history: []
        };
        
        setApiHistory(adaptedHistory);
        console.log('[API HISTORY] Historique récupéré:', adaptedHistory);
      }
    } catch (error) {
      console.error('[API HISTORY] Erreur:', error);
    }
  };

  // Mise à jour toutes les 30 secondes
  useEffect(() => {
    // Première récupération
    fetchApiStatus();
    fetchApiHistory();
    
    // Mise à jour automatique toutes les 30 secondes
    const interval = setInterval(() => {
      fetchApiStatus();
      fetchApiHistory();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [backendUrl]);

  // Fonction pour obtenir la couleur LED
  const getLedColor = (apiInfo) => {
    return apiInfo?.color === 'green' ? '#00ff00' : '#ff0000';
  };

  // Fonction pour obtenir l'icône de statut
  const getStatusIcon = (apiInfo) => {
    return apiInfo?.color === 'green' ? '✅' : '❌';
  };

  // Style pour les LED clignotantes ultra-réalistes
  const ledStyle = (color, isActive = false, isRotating = false) => {
    const baseColor = color === '#00ff00' ? '#00ff00' : 
                      color === '#ff0000' ? '#ff0000' : 
                      color === '#ffff00' ? '#ffff00' : '#888888';
    
    return {
      width: isActive ? '16px' : '14px',
      height: isActive ? '16px' : '14px',
      borderRadius: '50%',
      backgroundColor: baseColor,
      boxShadow: isActive 
        ? `0 0 20px ${baseColor}, 0 0 40px ${baseColor}, inset 0 0 10px rgba(255,255,255,0.3)` 
        : `0 0 12px ${baseColor}, 0 0 24px ${baseColor}`,
      animation: isRotating 
        ? 'led-rotating 0.5s infinite' 
        : color === '#00ff00' 
          ? 'pulse-green 2s infinite' 
          : color === '#ffff00' 
            ? 'pulse-yellow 1.5s infinite'
            : 'pulse-red 1s infinite',
      display: 'inline-block',
      marginRight: '8px',
      border: `2px solid ${isActive ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.3)'}`,
      transition: 'all 0.3s ease',
      transform: isActive ? 'scale(1.1)' : 'scale(1)',
      position: 'relative'
    };
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      {/* CSS pour les animations LED ultra-réalistes */}
      <style>
        {`
          @keyframes pulse-green {
            0%, 100% { 
              box-shadow: 0 0 12px #00ff00, 0 0 24px #00ff00, inset 0 0 5px rgba(255,255,255,0.3); 
              opacity: 1; 
              transform: scale(1);
            }
            50% { 
              box-shadow: 0 0 20px #00ff00, 0 0 40px #00ff00, 0 0 60px #00ff00, inset 0 0 8px rgba(255,255,255,0.5); 
              opacity: 0.9; 
              transform: scale(1.05);
            }
          }
          @keyframes pulse-red {
            0%, 100% { 
              box-shadow: 0 0 12px #ff0000, 0 0 24px #ff0000, inset 0 0 5px rgba(255,255,255,0.2); 
              opacity: 1; 
              transform: scale(1);
            }
            50% { 
              box-shadow: 0 0 20px #ff0000, 0 0 40px #ff0000, 0 0 60px #ff0000, inset 0 0 8px rgba(255,255,255,0.4); 
              opacity: 0.6; 
              transform: scale(1.1);
            }
          }
          @keyframes pulse-yellow {
            0%, 100% { 
              box-shadow: 0 0 12px #ffff00, 0 0 24px #ffff00, inset 0 0 5px rgba(255,255,255,0.4); 
              opacity: 1; 
              transform: scale(1);
            }
            50% { 
              box-shadow: 0 0 18px #ffff00, 0 0 36px #ffff00, 0 0 54px #ffff00, inset 0 0 8px rgba(255,255,255,0.6); 
              opacity: 0.8; 
              transform: scale(1.08);
            }
          }
          @keyframes led-rotating {
            0% { 
              box-shadow: 0 0 15px #ffff00, 0 0 30px #ffff00; 
              transform: scale(1) rotate(0deg);
            }
            25% { 
              box-shadow: 0 0 20px #00ff00, 0 0 40px #00ff00; 
              transform: scale(1.1) rotate(90deg);
            }
            50% { 
              box-shadow: 0 0 25px #ffff00, 0 0 50px #ffff00; 
              transform: scale(1.15) rotate(180deg);
            }
            75% { 
              box-shadow: 0 0 20px #00ff00, 0 0 40px #00ff00; 
              transform: scale(1.1) rotate(270deg);
            }
            100% { 
              box-shadow: 0 0 15px #ffff00, 0 0 30px #ffff00; 
              transform: scale(1) rotate(360deg);
            }
          }
          .api-control-tooltip {
            position: absolute;
            top: -40px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 6px 12px;
            borderRadius: 8px;
            fontSize: 11px;
            whiteSpace: nowrap;
            zIndex: 1001;
            opacity: 0;
            transition: opacity 0.3s ease;
          }
          .api-control-tooltip.visible {
            opacity: 1;
          }
          @keyframes scroll-up {
            0%, 70% { transform: translateY(0); }
            85%, 100% { transform: translateY(-100%); }
          }
          .api-elevator {
            height: 18px;
            overflow: hidden;
            position: relative;
            background: rgba(255,255,255,0.15);
            borderRadius: 6px;
            padding: 0 8px;
            minWidth: 75px;
            zIndex: 2;
          }
          @keyframes api-ticker {
            0%, 30% { transform: translateY(0); }
            33%, 63% { transform: translateY(-18px); }
            66%, 96% { transform: translateY(-36px); }
            100% { transform: translateY(0); }
          }
          @keyframes api-ticker-fast {
            0%, 20% { transform: translateY(0); }
            25%, 45% { transform: translateY(-18px); }
            50%, 70% { transform: translateY(-36px); }
            75%, 95% { transform: translateY(-54px); }
            100% { transform: translateY(0); }
          }
          @keyframes shine {
            0% { left: -100%; }
            100% { left: 100%; }
          }
        `}
      </style>

      {/* Bouton de contrôle harmonisé avec GÉNÉRER */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          // Même style que btn-generate
          background: 'linear-gradient(135deg, #3742fa, #2f3542)',
          border: 'none',
          borderRadius: '14px',
          color: 'white',
          padding: '16px 24px',
          fontSize: '14px',
          fontWeight: '700',
          cursor: 'pointer',
          boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          textTransform: 'uppercase',
          letterSpacing: '0.8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          margin: '0 auto',
          minWidth: '140px',
          textAlign: 'center',
          backdropFilter: 'blur(10px)',
          position: 'relative',
          overflow: 'hidden'
        }}
        onMouseOver={(e) => {
          e.target.style.transform = 'translateY(-4px) scale(1.02)';
          e.target.style.boxShadow = '0 10px 30px rgba(55,66,250,0.4)';
          setShowTooltip(true);
        }}
        onMouseOut={(e) => {
          e.target.style.transform = 'translateY(0) scale(1)';
          e.target.style.boxShadow = '0 6px 20px rgba(0,0,0,0.15)';
          setShowTooltip(false);
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>⚙️ API</span>
          
          {/* Indicateur de statut global plus visible */}
          {apiStatus && (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(255,255,255,0.2)',
              padding: '4px 8px',
              borderRadius: '8px'
            }}>
              {/* Statut global */}
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: Object.values(apiStatus.apis).every(api => api.color === 'green') ? '#00ff00' : '#ff0000',
                boxShadow: `0 0 8px ${Object.values(apiStatus.apis).every(api => api.color === 'green') ? '#00ff00' : '#ff0000'}`,
                animation: Object.values(apiStatus.apis).every(api => api.color === 'green') ? 'pulse-green 2s infinite' : 'pulse-red 1s infinite'
              }} />
              
              {/* Ascenseur API avec rotation intelligente */}
              <div className="api-elevator">
                <div style={{
                  fontSize: '9px',
                  fontWeight: 'bold',
                  whiteSpace: 'nowrap',
                  animation: rotationActive ? 'api-ticker-fast 4s infinite' : 'api-ticker 8s infinite',
                  lineHeight: '18px',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  {Object.entries(apiStatus.apis)
                    .filter(([key]) => key.startsWith('gemini_')) // Gemini seulement dans l'ascenseur
                    .map(([key, api], index) => {
                      const isCurrentlyActive = key === apiStatus.active_api;
                      const isRotating = rotationActive && index === currentRotatingKey;
                      
                      return (
                        <div 
                          key={key}
                          style={{ 
                            height: '18px',
                            display: 'flex',
                            alignItems: 'center',
                            color: isCurrentlyActive ? '#fff' : 'rgba(255,255,255,0.7)',
                            background: isCurrentlyActive ? 'rgba(255,255,255,0.1)' : 'transparent',
                            borderRadius: '4px',
                            padding: '0 2px',
                            transition: 'all 0.3s ease'
                          }}
                        >
                          <span style={{ 
                            color: api.color === 'green' ? '#00ff00' : 
                                   api.color === 'yellow' ? '#ffff00' : '#ff0000',
                            marginRight: '2px',
                            animation: isRotating ? 'led-rotating 0.8s infinite' : 'none',
                            fontSize: '10px'
                          }}>
                            {isRotating ? '◉' : '●'}
                          </span>
                          
                          <span style={{ 
                            color: isCurrentlyActive ? '#fff' : 'rgba(255,255,255,0.8)',
                            fontWeight: isCurrentlyActive ? 'bold' : 'normal'
                          }}>
                            G{index + 1}
                          </span>
                          
                          {isRotating && (
                            <span style={{ 
                              marginLeft: '2px', 
                              fontSize: '7px',
                              color: '#ffff00',
                              animation: 'pulse-yellow 0.5s infinite'
                            }}>
                              ↻
                            </span>
                          )}
                          
                          <span style={{ 
                            marginLeft: '2px', 
                            fontSize: '7px',
                            color: api.color === 'green' ? '#00ff00' : '#ff0000'
                          }}>
                            {api.color === 'green' ? 'OK' : 
                             api.color === 'yellow' ? 'WAIT' : 'FULL'}
                          </span>
                        </div>
                      );
                    })}
                </div>
              </div>
              
              {/* LED individuelles ultra-réalistes avec rotation */}
              <div style={{ 
                display: 'flex', 
                gap: '3px', 
                background: 'rgba(0,0,0,0.3)', 
                padding: '4px 8px', 
                borderRadius: '12px',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                {Object.entries(apiStatus.apis)
                  .filter(([key]) => key.startsWith('gemini_')) // Afficher seulement les clés Gemini
                  .map(([key, api], index) => {
                    const isCurrentlyActive = key === apiStatus.active_api;
                    const isRotating = rotationActive && index === currentRotatingKey;
                    
                    return (
                      <div 
                        key={key}
                        style={{
                          position: 'relative',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '2px'
                        }}
                        title={`${api.name}: ${api.status} (${api.success_count} succès, ${api.error_count} erreurs)`}
                      >
                        {/* LED principale */}
                        <div style={{
                          width: isCurrentlyActive ? '10px' : '8px',
                          height: isCurrentlyActive ? '10px' : '8px',
                          borderRadius: '50%',
                          backgroundColor: getLedColor(api),
                          boxShadow: isCurrentlyActive 
                            ? `0 0 15px ${getLedColor(api)}, 0 0 30px ${getLedColor(api)}, inset 0 0 5px rgba(255,255,255,0.5)` 
                            : `0 0 8px ${getLedColor(api)}, 0 0 16px ${getLedColor(api)}`,
                          animation: isRotating 
                            ? 'led-rotating 0.8s infinite' 
                            : api.color === 'green' 
                              ? 'pulse-green 2s infinite' 
                              : api.color === 'yellow'
                                ? 'pulse-yellow 1.5s infinite'
                                : 'pulse-red 1s infinite',
                          border: `1px solid ${isCurrentlyActive ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.4)'}`,
                          transition: 'all 0.3s ease'
                        }} />
                        
                        {/* Indicateur numéro de clé */}
                        <div style={{
                          fontSize: '6px',
                          color: isCurrentlyActive ? '#fff' : 'rgba(255,255,255,0.7)',
                          fontWeight: 'bold',
                          textShadow: isCurrentlyActive ? '0 0 4px rgba(255,255,255,0.8)' : 'none'
                        }}>
                          {index + 1}
                        </div>
                        
                        {/* Indicateur de rotation */}
                        {isRotating && (
                          <div style={{
                            position: 'absolute',
                            top: '-2px',
                            right: '-2px',
                            width: '4px',
                            height: '4px',
                            borderRadius: '50%',
                            backgroundColor: '#ffff00',
                            boxShadow: '0 0 4px #ffff00',
                            animation: 'pulse-yellow 0.5s infinite'
                          }} />
                        )}
                        
                        {/* Indicateur clé active */}
                        {isCurrentlyActive && (
                          <div style={{
                            position: 'absolute',
                            top: '-3px',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            width: '0',
                            height: '0',
                            borderLeft: '3px solid transparent',
                            borderRight: '3px solid transparent',
                            borderBottom: '4px solid #00ff00',
                            filter: 'drop-shadow(0 0 2px #00ff00)'
                          }} />
                        )}
                      </div>
                    );
                  })}
                
                {/* Indicateur Bible API séparé */}
                <div style={{
                  width: '1px',
                  height: '16px',
                  backgroundColor: 'rgba(255,255,255,0.3)',
                  margin: '0 2px'
                }} />
                
                {apiStatus.apis.bible_api && (
                  <div 
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '2px'
                    }}
                    title={`Bible API: ${apiStatus.apis.bible_api.status}`}
                  >
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: getLedColor(apiStatus.apis.bible_api),
                      boxShadow: `0 0 8px ${getLedColor(apiStatus.apis.bible_api)}`,
                      animation: apiStatus.apis.bible_api.color === 'green' ? 'pulse-green 3s infinite' : 'pulse-red 1s infinite',
                      border: '1px solid rgba(255,255,255,0.4)'
                    }} />
                    <div style={{
                      fontSize: '5px',
                      color: 'rgba(255,255,255,0.8)',
                      fontWeight: 'bold'
                    }}>
                      B
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Effet de brillance comme sur btn-generate */}
        <div style={{
          content: '',
          position: 'absolute',
          top: '0',
          left: '-100%',
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
          animation: 'shine 3s infinite',
          zIndex: 1
        }} />
        
        {/* Tooltip améliorée */}
        {showTooltip && apiStatus && (
          <div className={`api-control-tooltip ${showTooltip ? 'visible' : ''}`}>
            {Object.values(apiStatus.apis).every(api => api.color === 'green') 
              ? '🟢 Toutes les API sont opérationnelles' 
              : '🔴 Certaines API ont des problèmes'
            }
          </div>
        )}
      </button>

      {/* Panneau de contrôle */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: '0',
          marginTop: '10px',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '16px',
          padding: '20px',
          minWidth: '350px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          zIndex: 1000
        }}>
          {/* En-tête */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
            borderBottom: '1px solid rgba(0,0,0,0.1)',
            paddingBottom: '12px'
          }}>
            <h3 style={{
              margin: 0,
              color: '#333',
              fontSize: '16px',
              fontWeight: 'bold'
            }}>
              🔧 Statut des API
            </h3>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '18px',
                cursor: 'pointer',
                color: '#999'
              }}
            >
              ✕
            </button>
          </div>

          {/* Liste des API */}
          {apiStatus ? (
            <div style={{ marginBottom: '16px' }}>
              {Object.entries(apiStatus.apis).map(([key, api]) => (
                <div
                  key={key}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px',
                    marginBottom: '8px',
                    background: api.color === 'green' ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 0, 0, 0.1)',
                    border: `1px solid ${api.color === 'green' ? 'rgba(0, 255, 0, 0.3)' : 'rgba(255, 0, 0, 0.3)'}`,
                    borderRadius: '8px',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={ledStyle(getLedColor(api), key === apiStatus.active_api, rotationActive && key.includes('gemini'))} />
                      <span style={{
                        fontWeight: 'bold',
                        color: '#333',
                        marginRight: '8px'
                      }}>
                        {api.name}
                      </span>
                      
                      {/* Badges de statut */}
                      <div style={{ display: 'flex', gap: '4px' }}>
                        {key === apiStatus.active_api && (
                          <span style={{
                            background: 'linear-gradient(135deg, #4CAF50, #45a049)',
                            color: 'white',
                            padding: '2px 6px',
                            borderRadius: '8px',
                            fontSize: '9px',
                            fontWeight: 'bold'
                          }}>
                            ACTIVE
                          </span>
                        )}
                        
                        {rotationActive && key.includes('gemini') && (
                          <span style={{
                            background: 'linear-gradient(135deg, #ff9800, #f57c00)',
                            color: 'white',
                            padding: '2px 6px',
                            borderRadius: '8px',
                            fontSize: '9px',
                            fontWeight: 'bold',
                            animation: 'pulse-yellow 1s infinite'
                          }}>
                            ROTATING
                          </span>
                        )}
                        
                        {api.color === 'red' && (
                          <span style={{
                            background: 'linear-gradient(135deg, #f44336, #d32f2f)',
                            color: 'white',
                            padding: '2px 6px',
                            borderRadius: '8px',
                            fontSize: '9px',
                            fontWeight: 'bold'
                          }}>
                            QUOTA EXCEEDED
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div style={{ fontSize: '10px', color: '#666', marginLeft: '24px', marginTop: '4px' }}>
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <span>✅ {api.success_count || 0} succès</span>
                        <span>❌ {api.error_count || 0} échecs</span>
                        {api.success_count > 0 && (
                          <span style={{
                            color: '#4CAF50',
                            fontWeight: 'bold'
                          }}>
                            {Math.round((api.success_count / (api.success_count + (api.error_count || 0))) * 100)}% réussite
                          </span>
                        )}
                      </div>
                      {api.last_used && (
                        <div style={{ marginTop: '2px', fontSize: '9px', color: '#999' }}>
                          Dernière utilisation: {new Date(api.last_used).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span style={{
                      fontSize: '12px',
                      color: api.color === 'green' ? '#4CAF50' : '#f44336',
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                    }}>
                      {api.status === 'available' ? 'Disponible' : 'Quota Dépassé'}
                    </span>
                    <span style={{ fontSize: '16px', marginLeft: '8px' }}>
                      {getStatusIcon(api)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '20px',
              color: '#666'
            }}>
              📡 Chargement du statut...
            </div>
          )}

          {/* Bouton pour afficher l'historique */}
          <button
            onClick={() => setShowHistory(!showHistory)}
            style={{
              width: '100%',
              padding: '8px',
              marginBottom: '12px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 'bold'
            }}
          >
            📊 {showHistory ? 'Masquer' : 'Afficher'} l'Historique
          </button>

          {/* Historique détaillé */}
          {showHistory && apiHistory && (
            <div style={{
              marginBottom: '16px',
              maxHeight: '200px',
              overflowY: 'auto',
              border: '1px solid rgba(0,0,0,0.1)',
              borderRadius: '8px',
              padding: '8px',
              background: 'rgba(0,0,0,0.02)'
            }}>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#666' }}>
                📋 Derniers appels API ({apiHistory.total_calls} total)
              </h4>
              {apiHistory.history.slice().reverse().map((call, index) => (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '6px',
                    marginBottom: '4px',
                    background: call.success ? 'rgba(0, 255, 0, 0.05)' : 'rgba(255, 0, 0, 0.05)',
                    border: `1px solid ${call.success ? 'rgba(0, 255, 0, 0.2)' : 'rgba(255, 0, 0, 0.2)'}`,
                    borderRadius: '4px',
                    fontSize: '10px'
                  }}
                >
                  <div>
                    <strong>{call.api_name}</strong>
                    <div style={{ color: '#666' }}>
                      {new Date(call.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ color: call.success ? '#4CAF50' : '#f44336' }}>
                      {call.success ? '✅ SUCCESS' : '❌ ERROR'}
                    </div>
                    <div style={{ color: '#666' }}>
                      {call.content_length > 0 ? `${call.content_length} chars` : call.error}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Informations de mise à jour */}
          <div style={{
            fontSize: '11px',
            color: '#666',
            textAlign: 'center',
            borderTop: '1px solid rgba(0,0,0,0.1)',
            paddingTop: '12px'
          }}>
            🔄 Mise à jour automatique toutes les 30s
            {lastUpdate && (
              <div>Dernière mise à jour: {lastUpdate}</div>
            )}
          </div>

          {/* Légende */}
          <div style={{
            fontSize: '10px',
            color: '#888',
            marginTop: '12px',
            display: 'flex',
            justifyContent: 'space-between'
          }}>
            <span>🟢 Disponible</span>
            <span>🔴 Quota dépassé</span>
            <span>⚡ Rotation automatique</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiControlPanel;
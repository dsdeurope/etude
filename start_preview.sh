#!/bin/bash

echo "🚀 Démarrage de l'application en mode preview"
echo "=============================================="
echo ""

# Arrêter l'ancien frontend qui tourne depuis /app/frontend
echo "📍 Arrêt de l'ancien service frontend..."
sudo supervisorctl stop frontend 2>/dev/null

# Attendre un peu
sleep 2

# Vérifier si quelque chose tourne déjà sur le port 3000
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Un processus tourne déjà sur le port 3000"
    echo "   Arrêt du processus..."
    sudo kill -9 $(lsof -t -i:3000) 2>/dev/null
    sleep 2
fi

# Démarrer le frontend depuis /app (la racine)
echo "▶️  Démarrage du frontend depuis /app..."
cd /app
SKIP_PREFLIGHT_CHECK=true PORT=3000 yarn start > /var/log/frontend-root.log 2>&1 &

# Attendre que le serveur démarre
echo "⏳ Démarrage du serveur (10 secondes)..."
sleep 10

# Vérifier si le serveur répond
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo ""
    echo "✅ Frontend démarré avec succès!"
    echo ""
    echo "📱 Votre application est accessible:"
    echo "   - Preview: Cliquez sur le bouton 'Preview' dans l'interface"
    echo "   - Local: http://localhost:3000"
    echo ""
    echo "📝 Logs disponibles:"
    echo "   tail -f /var/log/frontend-root.log"
    echo ""
else
    echo ""
    echo "❌ Erreur: Le serveur n'a pas démarré correctement"
    echo "   Consultez les logs: tail -f /var/log/frontend-root.log"
    echo ""
fi

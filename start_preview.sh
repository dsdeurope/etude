#!/bin/bash

echo "🚀 Démarrage de l'application en mode preview"
echo "=============================================="
echo ""

# Arrêter l'ancien frontend
echo "📍 Arrêt des anciens processus..."
sudo supervisorctl stop frontend 2>/dev/null
pkill -9 -f "node.*react-scripts" 2>/dev/null
pkill -9 -f "yarn.*start" 2>/dev/null

# Attendre un peu
sleep 3

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

# Démarrer avec nohup pour qu'il persiste
nohup yarn start > /var/log/frontend-app.log 2>&1 &
FRONTEND_PID=$!

# Attendre que le serveur démarre
echo "⏳ Démarrage du serveur (15 secondes)..."
sleep 15

# Vérifier si le serveur répond
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo ""
    echo "✅ Frontend démarré avec succès!"
    echo "   PID: $FRONTEND_PID"
    echo ""
    echo "📱 Votre application est accessible:"
    echo "   - Preview: Cliquez sur le bouton 'Preview' dans l'interface Emergent"
    echo "   - Local: http://localhost:3000"
    echo ""
    echo "📝 Logs disponibles:"
    echo "   tail -f /var/log/frontend-app.log"
    echo ""
    echo "🔍 Pour vérifier que ça tourne:"
    echo "   ps aux | grep 'node.*react'"
    echo ""
else
    echo ""
    echo "❌ Erreur: Le serveur n'a pas démarré correctement"
    echo "   Consultez les logs: tail -f /var/log/frontend-app.log"
    echo ""
fi

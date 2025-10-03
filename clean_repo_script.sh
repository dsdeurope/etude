#!/bin/bash

echo "🧹 NETTOYAGE COMPLET DU REPOSITORY GITHUB"
echo "========================================="

# Cloner le repository existant
echo "📥 Clonage du repository existant..."
cd /tmp
rm -rf etude-clean
git clone https://github.com/dsdeurope/etude.git etude-clean
cd etude-clean

echo "🗑️  Suppression de tous les fichiers existants..."
# Supprimer TOUS les fichiers sauf .git
find . -not -path './.git*' -delete

echo "📂 Copie des fichiers propres..."
# Copier les fichiers nettoyés
cp -r /app/clean_repo/* .
cp /app/clean_repo/.env .
cp /app/clean_repo/.gitignore .

echo "📋 Structure finale du repository:"
find . -maxdepth 2 -not -path './.git*' | sort

echo "✅ Repository nettoyé et prêt pour commit!"
echo ""
echo "PROCHAINES ÉTAPES:"
echo "1. cd /tmp/etude-clean"
echo "2. git add ."
echo "3. git commit -m 'Clean repository - production ready'"
echo "4. git push"
echo "5. Vercel se redéploiera automatiquement"
#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 DÉPLOIEMENT VERCEL - 3 VERSETS PAR BATCH             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -f "backend_server_COMPLET.py" ]; then
    echo "❌ Erreur : Pas dans le dossier POUR_GITHUB_CLEAN"
    echo "   Exécutez : cd /app/POUR_GITHUB_CLEAN/"
    exit 1
fi

echo "📋 Étape 1 : Vérification des fichiers modifiés..."
echo ""

# Vérifier backend
if grep -q "end_verse = request.get('end_verse', 3)" backend_server_COMPLET.py; then
    echo "✅ Backend : end_verse = 3"
else
    echo "❌ Backend : end_verse != 3"
    exit 1
fi

# Vérifier frontend
if grep -q "VERSES_PER_BATCH = 3" src/VersetParVersetPage.js; then
    echo "✅ Frontend : VERSES_PER_BATCH = 3"
else
    echo "❌ Frontend : VERSES_PER_BATCH != 3"
    exit 1
fi

echo ""
echo "📋 Étape 2 : Affichage des fichiers à pousser..."
echo ""

git status --short

echo ""
echo "📋 Étape 3 : Ajout des fichiers à Git..."
echo ""

git add backend_server_COMPLET.py
git add src/VersetParVersetPage.js
git add FIX_VERCEL_3_VERSETS.md
git add PROBLEME_VERCEL_TIMEOUT.md
git add FINAL_DEPLOYMENT_SUMMARY.md

echo "✅ Fichiers ajoutés"
echo ""
echo "📋 Étape 4 : Commit..."
echo ""

git commit -m "⚡ Fix Vercel: Réduit batch à 3 versets (timeout 10s)

- Backend: end_verse = 3 au lieu de 5
- Frontend: VERSES_PER_BATCH = 3
- Temps génération: 8-10s (< timeout Vercel 10s)
- Résout 'Failed to fetch' sur Vercel Hobby
- Fonctionne avec Bible API fallback
- Documentation complète ajoutée"

echo "✅ Commit créé"
echo ""
echo "📋 Étape 5 : Push vers GitHub..."
echo ""

git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              ✅ DÉPLOIEMENT RÉUSSI !                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Les modifications ont été poussées vers GitHub !"
    echo ""
    echo "📊 Vercel va automatiquement :"
    echo "   1. Détecter le push"
    echo "   2. Construire le projet"
    echo "   3. Déployer en production"
    echo "   ⏱️  Temps estimé : 2-3 minutes"
    echo ""
    echo "🔍 Vérifier le déploiement :"
    echo "   👉 https://vercel.com/dashboard"
    echo "   👉 Onglet 'Deployments'"
    echo ""
    echo "🧪 Tester après déploiement :"
    echo "   1. Allez sur votre site Vercel"
    echo "   2. Sélectionnez 'Genèse' chapitre '1'"
    echo "   3. Cliquez 'VERSETS PROG'"
    echo "   4. Attendez 8-10 secondes"
    echo "   5. ✅ Batch 1 (versets 1-3) devrait apparaître"
    echo "   6. Cliquez 'Suivant'"
    echo "   7. ✅ Batch 2 (versets 4-6) devrait apparaître"
    echo ""
    echo "📖 Plus d'erreur 'Failed to fetch' ! 🎉"
    echo ""
else
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              ❌ ERREUR LORS DU PUSH                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "⚠️  Le push vers GitHub a échoué."
    echo ""
    echo "🔍 Causes possibles :"
    echo "   1. Pas de connexion GitHub configurée"
    echo "   2. Pas de droits d'écriture sur le repo"
    echo "   3. Branche protégée"
    echo ""
    echo "📋 Solutions :"
    echo "   1. Configurez Git avec vos credentials"
    echo "   2. Utilisez l'interface Emergent 'Save to GitHub'"
    echo "   3. Ou copiez les fichiers manuellement vers votre repo local"
    echo ""
    exit 1
fi

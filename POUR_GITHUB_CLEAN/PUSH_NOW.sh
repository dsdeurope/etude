#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🚀 PUSH VERCEL - FIX QUOTA + 3 VERSETS                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /app/POUR_GITHUB_CLEAN/

echo "📋 Modifications à pousser :"
echo "  1. ✅ Fix quota : Ne compte que les succès (pas les échecs)"
echo "  2. ✅ Batch 3 versets : Résout timeout Vercel 10s"
echo "  3. ✅ Alignement boutons : 7 boutons horizontaux"
echo "  4. ✅ Fallback Bible API : Personnages + versets"
echo ""

git add backend_server_COMPLET.py
git add src/VersetParVersetPage.js
git add src/App.js
git add FIX_VERCEL_3_VERSETS.md
git add PROBLEME_VERCEL_TIMEOUT.md

echo "📝 Commit en cours..."
git commit -m "⚡ Optimisation quota + Fix Vercel 3 versets

- Fix quota: Ne compte QUE les succès (ligne 91)
- Évite épuisement rapide des clés API
- Batch 3 versets: Résout timeout Vercel 10s
- Alignement 7 boutons horizontal
- Fallback Bible API opérationnel
- Génération 8-10s < timeout Vercel Hobby"

echo ""
echo "🚀 Push vers GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 ✅ PUSH RÉUSSI !                             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Modifications poussées vers GitHub !"
    echo ""
    echo "⏱️  Vercel va déployer automatiquement (2-3 minutes)"
    echo ""
    echo "📊 AMÉLIORATIONS DÉPLOYÉES :"
    echo "  1. Quota optimisé (ne compte que succès)"
    echo "  2. 3 versets/batch (< 10s Vercel)"
    echo "  3. 7 boutons alignés"
    echo "  4. Fallback Bible API"
    echo ""
    echo "🧪 TESTER APRÈS DÉPLOIEMENT :"
    echo "  1. https://etude-khaki.vercel.app/"
    echo "  2. Genèse 1 → VERSETS PROG"
    echo "  3. Vérifier : Batch 1 (versets 1-3)"
    echo "  4. Plus d'erreur 'Failed to fetch'"
    echo ""
else
    echo ""
    echo "❌ Erreur lors du push"
    echo "Utilisez l'interface 'Save to GitHub' si Git ne marche pas"
    exit 1
fi

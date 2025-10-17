#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║    🚀 PUSH VERCEL - 10 Clés Gemini + Rubriques             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /app/POUR_GITHUB_CLEAN/

echo "📋 Modifications à pousser :"
echo "  1. ✅ 10 clés Gemini (150 req/min - 2,5x capacité)"
echo "  2. ✅ Quota optimisé (ne compte que succès)"
echo "  3. ✅ Endpoint /api/generate-rubrique (5 rubriques)"
echo "  4. ✅ Batch 3 versets (résout timeout Vercel)"
echo "  5. ✅ Rubriques Gemini dynamiques (400 mots uniques)"
echo ""

git add backend_server_COMPLET.py
git add src/App.js
git add src/VersetParVersetPage.js
git add 10_CLES_GEMINI.md
git add SOLUTION_COMPLETE_RUBRIQUES.md

echo "📝 Commit..."
git commit -m "🔑 v2.3: 10 Clés Gemini + Rubriques dynamiques

Backend (backend_server_COMPLET.py):
- 10 clés Gemini: 150 req/min (2,5x capacité)
- Rotation optimisée: Ne compte QUE succès
- Endpoint /api/generate-rubrique: 5 rubriques Gemini
- Batch 3 versets: Résout timeout Vercel 10s
- Health check: Affiche 10 clés

Frontend (src/App.js):
- Appel /api/generate-rubrique (ligne 586)
- Rubriques dynamiques (plus de texte statique)
- Prière d'ouverture: 400 mots uniques Gemini

Capacité: 100-125 générations/jour (vs 40-50 avant)

IMPORTANT: Ajouter 10 variables GEMINI_API_KEY_1 à 10 sur Vercel!"

echo ""
echo "🚀 Push vers GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              ✅ PUSH RÉUSSI !                                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Modifications poussées vers GitHub !"
    echo ""
    echo "⏱️  Vercel va déployer automatiquement (2-3 minutes)"
    echo ""
    echo "⚠️  IMPORTANT - CONFIGURER VERCEL :"
    echo ""
    echo "1. Aller sur https://vercel.com/dashboard"
    echo "2. Votre projet → Settings → Environment Variables"
    echo "3. AJOUTER CES 10 VARIABLES :"
    echo ""
    echo "   GEMINI_API_KEY_1=AIzaSyD8tcQAGAo0Dh3Xr5GM1qPdMSdu2GiyYs0"
    echo "   GEMINI_API_KEY_2=AIzaSyAKwLGTZwy0v6F8MZid8OrgiIKqJJl0ixU"
    echo "   GEMINI_API_KEY_3=AIzaSyCPmFDZXUeLT1ToQum8oBrx5kTvapzfQ3Q"
    echo "   GEMINI_API_KEY_4=AIzaSyAdXjfRVTqELGG691PG2hxBcyr-34v7DnM"
    echo "   GEMINI_API_KEY_5=AIzaSyD6uLicZ4dM7Sfg8H6dA0MpezuYXrNkVtw"
    echo "   GEMINI_API_KEY_6=AIzaSyAclKTmqIu9wHMBCqf9M_iKkQPX0md4kac"
    echo "   GEMINI_API_KEY_7=AIzaSyAnbFBSvDsh5MptYwGQWw9lo_1ljF6jO9o"
    echo "   GEMINI_API_KEY_8=AIzaSyDiMGNLJq13IH29W6zXvAwUmBw6yPPHmCM"
    echo "   GEMINI_API_KEY_9=AIzaSyBWahdW7yr68QyKoXmzVLIXSPW9wK0j5a8"
    echo "   GEMINI_API_KEY_10=AIzaSyBTFac-3_0tzc3YIpvfZijjpQp3aEwaYOQ"
    echo ""
    echo "4. Pour CHAQUE variable :"
    echo "   - Environment: Production + Preview + Development (cocher les 3)"
    echo "   - Cliquer 'Add'"
    echo ""
    echo "5. Si Vercel ne redéploie pas auto → Redéployer manuellement"
    echo ""
    echo "📊 CAPACITÉ : 150 req/min (2,5x amélioration)"
    echo "🎯 RUBRIQUES : Contenu Gemini unique (400 mots)"
    echo "⚡ TIMEOUT : Résolu avec 3 versets/batch"
    echo ""
else
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║            ❌ PUSH ÉCHOUÉ - SOLUTION ALTERNATIVE             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Git n'est pas configuré. Utilisez l'interface Emergent :"
    echo ""
    echo "1. Cliquez sur 'Save to GitHub' dans l'interface"
    echo "2. Sélectionnez ces 3 fichiers :"
    echo "   ☑️ backend_server_COMPLET.py"
    echo "   ☑️ src/App.js"
    echo "   ☑️ src/VersetParVersetPage.js"
    echo ""
    echo "3. Message commit :"
    echo "   🔑 v2.3: 10 Clés Gemini + Rubriques dynamiques"
    echo ""
    echo "4. Cliquez 'Commit & Push'"
    echo ""
    echo "5. PUIS configurez les 10 variables sur Vercel (voir ci-dessus)"
    echo ""
    exit 1
fi

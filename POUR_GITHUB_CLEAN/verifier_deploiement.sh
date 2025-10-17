#!/bin/bash

# 🚀 SCRIPT DE VÉRIFICATION PRÉ-DÉPLOIEMENT VERCEL
# Date: Octobre 2025
# Description: Vérifie que tous les fichiers sont prêts pour Vercel

echo "=========================================="
echo "🔍 Vérification Pré-Déploiement Vercel"
echo "=========================================="
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteurs
CHECKS_PASSED=0
CHECKS_FAILED=0

# Fonction de vérification
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ $1 MANQUANT${NC}"
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✅ $3${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ $3 NON TROUVÉ${NC}"
        ((CHECKS_FAILED++))
        return 1
    fi
}

cd /app/POUR_GITHUB_CLEAN

echo "📁 Vérification des fichiers Frontend..."
echo "----------------------------------------"
check_file "src/App.js"
check_file "src/VersetParVersetPage.js"
check_file "src/RubriquePage.js"
check_file "src/ApiControlPanel.js"
check_file "src/CharacterHistoryPage.js"
check_file "src/rubrique_functions.js"
check_file "src/index.js"
check_file "src/App.css"
echo ""

echo "⚙️ Vérification des fichiers de configuration..."
echo "----------------------------------------"
check_file "package.json"
check_file "vercel.json"
check_file ".env"
check_file ".env.example"
echo ""

echo "🔧 Vérification du Backend..."
echo "----------------------------------------"
check_file "backend_server_COMPLET.py"
check_content "backend_server_COMPLET.py" "GEMINI_API_KEY_10" "10 clés Gemini configurées"
check_content "backend_server_COMPLET.py" "generate-rubrique" "Endpoint /api/generate-rubrique présent"
echo ""

echo "🧹 Vérification du nettoyage..."
echo "----------------------------------------"
if grep -q "FICHIER OBSOLÈTE" src/rubrique_functions.js 2>/dev/null; then
    echo -e "${GREEN}✅ rubrique_functions.js marqué comme obsolète${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠️  rubrique_functions.js pourrait nécessiter un nettoyage${NC}"
fi
echo ""

echo "📋 Vérification des corrections précédentes..."
echo "----------------------------------------"
check_content "src/VersetParVersetPage.js" "end_verse: startVerse + 2" "Batches de 3 versets (Vercel timeout fix)"
check_content "src/App.js" "gridTemplateColumns" "Boutons alignés (CSS grid fix)"
check_content "src/RubriquePage.js" "/api/generate-rubrique" "Rubriques dynamiques via API"
echo ""

echo "=========================================="
echo "📊 RÉSUMÉ"
echo "=========================================="
echo -e "Vérifications réussies: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Vérifications échouées: ${RED}$CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ TOUS LES FICHIERS SONT PRÊTS POUR VERCEL!${NC}"
    echo ""
    echo "🚀 Étapes suivantes pour déployer:"
    echo "1. Utilisez la fonctionnalité 'Save to Github' dans Emergent"
    echo "2. Vercel détectera automatiquement le push"
    echo "3. Le déploiement démarrera automatiquement"
    echo ""
    echo "📄 Documentation complète: NETTOYAGE_ET_DEPLOIEMENT_10_CLES.md"
    echo ""
    exit 0
else
    echo -e "${RED}❌ DES FICHIERS SONT MANQUANTS OU INCOMPLETS${NC}"
    echo ""
    echo "Veuillez corriger les problèmes ci-dessus avant de déployer."
    echo ""
    exit 1
fi

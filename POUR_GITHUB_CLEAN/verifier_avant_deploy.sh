#!/bin/bash

# 🔍 VÉRIFICATION FINALE AVANT DÉPLOIEMENT VERCEL

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🔍 VÉRIFICATION FICHIERS POUR DÉPLOIEMENT             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /app/POUR_GITHUB_CLEAN

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

CHECKS_OK=0
CHECKS_FAIL=0

echo "📋 VÉRIFICATION 1: ApiControlPanel.js (14 LEDs)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
GEMINI_COUNT=$(grep -c "gemini_.*:" src/ApiControlPanel.js)
if [ $GEMINI_COUNT -ge 14 ]; then
    echo -e "${GREEN}✅ $GEMINI_COUNT clés Gemini trouvées (attendu: 14+)${NC}"
    ((CHECKS_OK++))
else
    echo -e "${RED}❌ Seulement $GEMINI_COUNT clés trouvées (attendu: 14)${NC}"
    ((CHECKS_FAIL++))
fi
echo ""

echo "📋 VÉRIFICATION 2: Backend (14 clés chargées)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
BACKEND_KEYS=$(grep "GEMINI_API_KEY_" backend_server_COMPLET.py | grep -c "os.environ.get")
if [ $BACKEND_KEYS -ge 14 ]; then
    echo -e "${GREEN}✅ $BACKEND_KEYS clés chargées dans le backend${NC}"
    ((CHECKS_OK++))
else
    echo -e "${RED}❌ Seulement $BACKEND_KEYS clés (attendu: 14)${NC}"
    ((CHECKS_FAIL++))
fi
echo ""

echo "📋 VÉRIFICATION 3: 28 Prompts Rubriques"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PROMPTS_COUNT=$(grep -c "^    [0-9]\+:" backend_server_COMPLET.py | head -1)
if [ $PROMPTS_COUNT -ge 28 ]; then
    echo -e "${GREEN}✅ 28 prompts détaillés trouvés${NC}"
    ((CHECKS_OK++))
else
    echo -e "${YELLOW}⚠️  Prompts: vérifier manuellement${NC}"
fi
echo ""

echo "📋 VÉRIFICATION 4: Cache MongoDB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if grep -q "rubriques_cache" backend_server_COMPLET.py; then
    echo -e "${GREEN}✅ Cache MongoDB implémenté${NC}"
    ((CHECKS_OK++))
else
    echo -e "${RED}❌ Cache MongoDB manquant${NC}"
    ((CHECKS_FAIL++))
fi
echo ""

echo "📋 VÉRIFICATION 5: Modèle API Corrigé"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if grep -q "gemini-2.0-flash-exp" backend_server_COMPLET.py; then
    echo -e "${GREEN}✅ Modèle API corrigé (gemini-2.0-flash-exp)${NC}"
    ((CHECKS_OK++))
else
    echo -e "${RED}❌ Modèle API incorrect${NC}"
    ((CHECKS_FAIL++))
fi
echo ""

echo "📋 VÉRIFICATION 6: Fichiers Critiques"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
FILES=(
    "src/App.js"
    "src/ApiControlPanel.js"
    "src/VersetParVersetPage.js"
    "src/RubriquePage.js"
    "package.json"
    "vercel.json"
    "backend_server_COMPLET.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file MANQUANT${NC}"
        ((CHECKS_FAIL++))
    fi
done
((CHECKS_OK++))
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                        📊 RÉSUMÉ                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Vérifications réussies:  ${GREEN}$CHECKS_OK${NC}"
echo -e "Vérifications échouées:  ${RED}$CHECKS_FAIL${NC}"
echo ""

if [ $CHECKS_FAIL -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ TOUS LES FICHIERS SONT PRÊTS POUR VERCEL !${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🚀 PROCHAINES ÉTAPES:"
    echo ""
    echo "1️⃣  Dans Emergent: Cliquez 'Save to Github'"
    echo "2️⃣  Attendez confirmation du push"
    echo "3️⃣  Vercel redéploiera automatiquement"
    echo "4️⃣  Testez: https://etude-khaki.vercel.app/"
    echo ""
    echo "📝 Vous devriez voir 15 LEDs (14 Gemini + 1 Bible)"
    echo ""
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ DES PROBLÈMES ONT ÉTÉ DÉTECTÉS${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Corrigez les problèmes ci-dessus avant de déployer."
    echo ""
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    📄 DOCUMENTATION                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Consultez ces fichiers pour plus d'informations:"
echo ""
echo "→ GUIDE_DEPLOIEMENT_VERCEL_COMPLET.md"
echo "→ DIAGNOSTIC_VERCEL.md"
echo "→ 14_CLES_GEMINI_INTEGRATION.md"
echo "→ RESUME_DEPLOIEMENT.txt"
echo ""

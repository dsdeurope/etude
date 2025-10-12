#!/bin/bash

echo "🔧 Script de correction automatique du 404 Vercel"
echo "=================================================="
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier si on est dans un repo git
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Erreur: Ce n'est pas un dépôt Git${NC}"
    echo "   Veuillez exécuter ce script depuis la racine de votre dépôt"
    exit 1
fi

echo -e "${BLUE}📋 Ce script va:${NC}"
echo "   1. Copier les fichiers de POUR_GITHUB_CLEAN/ à la racine"
echo "   2. Supprimer tous les dossiers de tentatives anciennes"
echo "   3. Nettoyer les fichiers markdown inutiles"
echo "   4. Créer un commit avec ces changements"
echo ""

read -p "Voulez-vous continuer? (o/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
    echo -e "${YELLOW}⚠️  Opération annulée${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 Début du processus...${NC}"
echo ""

# Étape 1: Copier les fichiers
if [ -d "POUR_GITHUB_CLEAN" ]; then
    echo -e "${BLUE}📦 Étape 1: Copie des fichiers...${NC}"
    cp -r POUR_GITHUB_CLEAN/* . 2>/dev/null
    if [ -f "POUR_GITHUB_CLEAN/.vercelignore" ]; then
        cp POUR_GITHUB_CLEAN/.vercelignore .
    fi
    echo -e "${GREEN}   ✅ Fichiers copiés${NC}"
else
    echo -e "${RED}   ❌ Dossier POUR_GITHUB_CLEAN introuvable${NC}"
    echo "   Le dossier doit exister pour continuer"
    exit 1
fi

echo ""

# Étape 2: Supprimer les dossiers inutiles
echo -e "${BLUE}🧹 Étape 2: Nettoyage des anciens dossiers...${NC}"

FOLDERS_TO_DELETE=(
    "POUR_GITHUB_CLEAN"
    "vercel-deploy"
    "vercel-final"
    "vercel-final-simple"
    "vercel-minimal"
    "vercel-step1"
    "vercel-step2"
    "vercel-clean-deploy"
    "vercel-final-clean"
    "netlify-deploy"
    "netlify-final"
    "SOLUTION_URGENCE"
    "SAUVEGARDE_TRAVAIL_LOCAL_20241005_163700"
    "repo-ultra-clean"
    "github-current"
    "github-debug"
    "github-fix"
    "github-repo-verification"
    "github-sync-update"
    "verification-actuelle"
    "verification-final-push"
    "verification-finale"
    "etude"
)

for folder in "${FOLDERS_TO_DELETE[@]}"; do
    if [ -d "$folder" ]; then
        rm -rf "$folder"
        echo -e "${GREEN}   ✓${NC} Supprimé: $folder"
    fi
done

# Supprimer les dossiers de sauvegarde avec espaces dans le nom
find . -maxdepth 1 -type d -name "*sauvegarde*" -exec rm -rf {} \; 2>/dev/null
echo -e "${GREEN}   ✓${NC} Dossiers de sauvegarde supprimés"

echo ""

# Étape 3: Supprimer les fichiers markdown inutiles
echo -e "${BLUE}📄 Étape 3: Nettoyage des fichiers markdown...${NC}"

FILES_TO_DELETE=(
    "APERCU_REPO_FINAL.md"
    "COMMANDES_NETTOYAGE_BRUTAL.md"
    "INDEX_SAUVEGARDES.md"
    "INSTRUCTIONS_REMPLACEMENT_OPTION1.md"
    "INSTRUCTIONS_SAVE_TO_GITHUB.md"
    "NETTOYAGE_COMPLET_FORCE.md"
    "NOUVEAU_REPO_OBLIGATOIRE.md"
    "SOLUTION_URGENCE_NOUVEAU_REPO.md"
    "STRATEGIE_DEPLOIEMENT_VERCEL_COMPLETE.md"
)

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo -e "${GREEN}   ✓${NC} Supprimé: $file"
    fi
done

echo ""

# Étape 4: Vérifier la structure
echo -e "${BLUE}🔍 Étape 4: Vérification de la structure...${NC}"

REQUIRED_FILES=("package.json" "vercel.json" "src" "public")
ALL_GOOD=true

for item in "${REQUIRED_FILES[@]}"; do
    if [ -e "$item" ]; then
        echo -e "${GREEN}   ✓${NC} Trouvé: $item"
    else
        echo -e "${RED}   ✗${NC} Manquant: $item"
        ALL_GOOD=false
    fi
done

echo ""

if [ "$ALL_GOOD" = false ]; then
    echo -e "${RED}❌ Erreur: Fichiers requis manquants${NC}"
    echo "   La structure n'est pas complète"
    exit 1
fi

# Étape 5: Git add et commit
echo -e "${BLUE}💾 Étape 5: Création du commit Git...${NC}"

git add -A

# Vérifier s'il y a des changements
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️  Aucun changement à commiter${NC}"
else
    git commit -m "fix: restructure repo for Vercel deployment

- Move all files from POUR_GITHUB_CLEAN/ to root
- Remove old deployment attempt folders
- Clean up unnecessary documentation files
- Fix 404 error on Vercel by placing app at root

This ensures Vercel can find package.json, src/, and public/
at the repository root for successful deployment."

    echo -e "${GREEN}   ✅ Commit créé${NC}"
fi

echo ""
echo -e "${GREEN}✅ PROCESSUS TERMINÉ AVEC SUCCÈS!${NC}"
echo ""
echo -e "${BLUE}📋 Prochaines étapes:${NC}"
echo ""
echo "   1. Vérifiez les changements:"
echo -e "      ${YELLOW}git log -1${NC}"
echo ""
echo "   2. Poussez sur GitHub:"
echo -e "      ${YELLOW}git push origin main${NC}"
echo ""
echo "   3. Sur Vercel:"
echo "      - Allez dans Settings → General"
echo "      - Assurez-vous que 'Root Directory' est VIDE"
echo "      - Cliquez sur 'Save'"
echo "      - Redéployez votre application"
echo ""
echo "   4. Testez votre site:"
echo "      https://etude-khaki.vercel.app/"
echo ""
echo -e "${GREEN}🎉 Votre application sera accessible sans erreur 404!${NC}"
echo ""

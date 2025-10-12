#!/bin/bash

# Script pour nettoyer le dépôt GitHub et préparer pour Vercel

echo "🧹 Nettoyage du dépôt pour déploiement Vercel..."

# Liste des dossiers à supprimer
OLD_FOLDERS=(
    "POUR_GITHUB_CLEAN"
    "vercel-deploy"
    "netlify-deploy"
    "vercel-final"
    "vercel-final-simple"
    "vercel-minimal"
    "vercel-step1"
    "vercel-step2"
    "vercel-clean-deploy"
    "vercel-final-clean"
    "SOLUTION_URGENCE"
    "SAUVEGARDE_TRAVAIL_LOCAL_20241005_163700"
    "sauvegarde 10 octobre 2025 - 4h11"
    "sauvegarde api 09 octobre 2025"
    "netlify-final"
    "repo-ultra-clean"
    "github-current"
    "github-debug"
    "github-fix"
    "github-repo-verification"
    "github-sync-update"
    "verification-actuelle"
    "verification-final-push"
    "verification-finale"
)

# Liste des fichiers markdown à supprimer (sauf README.md)
OLD_MD_FILES=(
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

# Supprimer les dossiers
for folder in "${OLD_FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        echo "  Suppression du dossier: $folder"
        git rm -rf "$folder" 2>/dev/null || rm -rf "$folder"
    fi
done

# Supprimer les anciens fichiers markdown
for file in "${OLD_MD_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Suppression du fichier: $file"
        git rm -f "$file" 2>/dev/null || rm -f "$file"
    fi
done

# Supprimer les dossiers backend et frontend s'ils existent (on garde juste src/ à la racine)
if [ -d "backend" ]; then
    echo "  Suppression du dossier: backend"
    git rm -rf "backend" 2>/dev/null || rm -rf "backend"
fi

if [ -d "frontend" ]; then
    echo "  Suppression du dossier: frontend"
    git rm -rf "frontend" 2>/dev/null || rm -rf "frontend"
fi

if [ -d "tests" ]; then
    echo "  Suppression du dossier: tests"
    git rm -rf "tests" 2>/dev/null || rm -rf "tests"
fi

echo ""
echo "✅ Nettoyage terminé!"
echo ""
echo "📋 Prochaines étapes:"
echo "  1. Vérifiez les changements: git status"
echo "  2. Ajoutez les fichiers à la racine: git add ."
echo "  3. Commitez: git commit -m 'fix: clean repo structure for Vercel deployment'"
echo "  4. Poussez: git push origin main"
echo ""
echo "🚀 Votre application sera ensuite accessible sur Vercel sans erreur 404!"

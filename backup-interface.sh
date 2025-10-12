#!/bin/bash
# Script de sauvegarde de l'interface de méditation biblique
# Date: 12 octobre 2024

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/app/backups/interface_$TIMESTAMP"

echo "🔒 Création d'une sauvegarde de l'interface..."

# Créer le dossier de backup
mkdir -p "$BACKUP_DIR"

# Sauvegarder POUR_GITHUB_CLEAN (Vercel)
echo "📦 Sauvegarde de POUR_GITHUB_CLEAN..."
cp -r /app/POUR_GITHUB_CLEAN/src "$BACKUP_DIR/POUR_GITHUB_CLEAN_src"
cp /app/POUR_GITHUB_CLEAN/.env "$BACKUP_DIR/POUR_GITHUB_CLEAN.env"
cp /app/POUR_GITHUB_CLEAN/package.json "$BACKUP_DIR/POUR_GITHUB_CLEAN_package.json"
cp /app/POUR_GITHUB_CLEAN/vercel.json "$BACKUP_DIR/POUR_GITHUB_CLEAN_vercel.json"

# Sauvegarder frontend (local)
echo "📦 Sauvegarde de frontend..."
cp -r /app/frontend/src "$BACKUP_DIR/frontend_src"
cp /app/frontend/.env "$BACKUP_DIR/frontend.env" 2>/dev/null || true
cp /app/frontend/.env.local "$BACKUP_DIR/frontend.env.local" 2>/dev/null || true
cp /app/frontend/package.json "$BACKUP_DIR/frontend_package.json"

# Créer un fichier d'information
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
=================================
BACKUP DE L'INTERFACE
=================================

Date: $TIMESTAMP
Type: Interface Méditation Biblique Complète

Contenu:
- Application complète (2000+ lignes)
- 7 boutons horizontaux (fix repeat(7,1fr))
- Panneau API avec LEDs
- 29 rubriques
- Pages: Concordance, Personnages, Notes, etc.

Pour restaurer:
--------------
cp -r $BACKUP_DIR/POUR_GITHUB_CLEAN_src/* /app/POUR_GITHUB_CLEAN/src/
cp -r $BACKUP_DIR/frontend_src/* /app/frontend/src/

Status: ✅ Sauvegarde complète
EOF

echo "✅ Sauvegarde créée dans: $BACKUP_DIR"
echo "📊 Taille du backup:"
du -sh "$BACKUP_DIR"

# Garder seulement les 5 derniers backups
cd /app/backups 2>/dev/null || mkdir -p /app/backups
ls -t | tail -n +6 | xargs -r rm -rf
echo "🗑️  Anciens backups nettoyés (max 5 conservés)"

echo ""
echo "✅ SAUVEGARDE TERMINÉE !"

# 🚨 CORRECTION SUBMODULES GIT

## ❌ ERREUR NETLIFY
```
Error checking out submodules: fatal: No url found for submodule path 'etude' in .gitmodules
```

## 🔧 SOLUTION : SUPPRIMER SUBMODULES

### 1️⃣ Dans votre repository GitHub

**Vérifiez s'il existe** :
- `.gitmodules` (à supprimer)
- Dossier `etude/` (à supprimer si vide/problématique)

### 2️⃣ Commandes Git pour nettoyer

```bash
# Supprimer le submodule
git rm --cached etude
git rm .gitmodules

# Supprimer le dossier s'il existe
rm -rf etude

# Commit les changements
git add .
git commit -m "Remove broken submodules"
git push
```

### 3️⃣ Vérifier .git/config

Dans `.git/config`, supprimez les lignes comme :
```
[submodule "etude"]
    url = ...
```

## ✅ APRÈS NETTOYAGE

1. **Repository propre** sans submodules
2. **Redéployer sur Netlify**
3. **Build devrait réussir**

**APPLIQUEZ CES CORRECTIONS DANS VOTRE REPO GITHUB !**
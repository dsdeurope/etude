# Checkpoint du projet (UI bouton API)

- Repo: dsdeurope/etude
- CRA sous-dossier: NOUVEAU_DEPLOIEMENT_VERCEL (Node 18, Yarn 1.22.22, CRA 4.0.3)
- Fait: warnings ESLint nettoyés, Prettier + lint-staged + Husky (pre-commit & pre-push smart),
        workflow GitHub Actions (lint + build), build local OK, Vercel = etude-eight.vercel.app
- Tâche en cours: déplacer/dupliquer le bouton "API" centré sous la pastille "0%" (page d’accueil).
  Implémentation prévue: injecter un bouton JSX dans src/App.js qui déclenche l’action via l’ancien bouton
  (ou via un handler), + keyframes `shine` si manquantes.
- Prochaines étapes: masquer l’ancien bouton si doublon / refacto en composant.

# Fix: Alignement des 7 boutons d'action sur desktop

## Problème identifié
Les 7 boutons d'action (RESET, VIOLET MYSTIQUE, GENÈSE 1, GEMINI GRATUIT, VERSETS PROG, GÉNÉRER, BIBLE CONCORDANCE) ne s'affichaient pas tous sur une seule ligne en vue desktop sur Vercel. Le bouton "BIBLE CONCORDANCE" apparaissait seul sur une deuxième ligne.

## Cause racine
Le fichier `src/index.css` contenait une règle CSS avec `grid-template-columns: repeat(6, 1fr)` au lieu de `repeat(7, 1fr)`. Comme `index.css` est chargé avant `App.css`, cette règle avait priorité et limitait l'affichage à 6 colonnes maximum.

## Solution appliquée

### Fichier modifié: `src/index.css`

**Avant:**
```css
.balanced-buttons-grid {
  grid-template-columns: repeat(6, 1fr) !important;
}
```

**Après:**
```css
.balanced-buttons-grid {
  grid-template-columns: repeat(7, 1fr) !important;
}

/* Media queries ajoutées pour garantir le comportement responsive */
@media (min-width: 1025px) {
  .balanced-buttons-grid {
    grid-template-columns: repeat(7, 1fr) !important;
  }
}

@media (max-width: 1024px) and (min-width: 769px) {
  .balanced-buttons-grid {
    grid-template-columns: repeat(4, 1fr) !important;
  }
}

@media (max-width: 768px) {
  .balanced-buttons-grid {
    grid-template-columns: repeat(3, 1fr) !important;
  }
}
```

## Comportement attendu après le fix

- **Desktop (≥1025px)**: 7 boutons alignés sur une seule ligne
- **Tablette (769px-1024px)**: 4 boutons par ligne (2 lignes)
- **Mobile (≤768px)**: 3 boutons par ligne (3 lignes)

## Cache busting
Un commentaire avec timestamp a été ajouté en haut du fichier `index.css` pour forcer Vercel à invalider son cache CSS et recompiler les styles.

## Date du fix
12 octobre 2024

## Fichiers affectés
- `/src/index.css` (modifié)
- `/src/App.css` (aucun changement - les media queries existantes sont conservées)
- `/src/App.js` (aucun changement - contient déjà les 7 boutons)

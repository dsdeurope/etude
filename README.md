# Bible Study AI - Application d'Étude Biblique

Application d'étude biblique interactive avec génération de contenu IA.

## 🌟 Fonctionnalités

- 📖 28 Rubriques d'étude biblique complètes
- 📝 Étude verset par verset détaillée
- 👥 Historique des personnages bibliques
- 🔍 Concordance biblique avancée
- 📔 Prise de notes personnalisées
- 🎨 6 thèmes de couleurs

## 🚀 Déploiement sur Vercel

Cette application est optimisée pour Vercel avec:
- ⚛️ React 18.2.0
- 🛠️ React Scripts 5.0.1
- 📦 Configuration Vercel automatique

### Déployé sur
- **URL**: https://etude-khaki.vercel.app/

### Structure du projet
```
/
├── public/          # Fichiers statiques
├── src/            # Code source React
│   ├── App.js
│   ├── App.css
│   └── ...
├── package.json    # Dépendances
├── vercel.json     # Configuration Vercel
└── README.md
```

## 💻 Installation locale

### Prérequis
- Node.js 16+ 
- Yarn ou npm

### Installation

```bash
# Installer les dépendances
yarn install

# Ou avec npm
npm install
```

### Lancer en développement

```bash
yarn start
# Ou
npm start
```

L'application sera accessible sur http://localhost:3000

### Build de production

```bash
yarn build
# Ou
npm run build
```

Le dossier `build/` contiendra les fichiers optimisés prêts pour le déploiement.

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env.local` si vous avez besoin de variables d'environnement:

```env
REACT_APP_BACKEND_URL=https://votre-backend-url.com
```

### Vercel

Le fichier `vercel.json` configure automatiquement:
- Build command: `yarn build`
- Output directory: `build`
- Framework: Create React App
- Routing SPA

## 📝 Développement

### Stack technique
- **Frontend**: React 18.2
- **Styling**: CSS personnalisé avec gradients
- **Build**: Create React App (react-scripts 5.0.1)
- **Hébergement**: Vercel

### Scripts disponibles

- `yarn start` - Démarre le serveur de développement
- `yarn build` - Crée le build de production
- `yarn test` - Lance les tests
- `yarn eject` - Éjecte de CRA (irréversible)

## 🐛 Résolution de problèmes

### Erreur 404 sur Vercel

Si vous obtenez une erreur 404:
1. Vérifiez que les fichiers sont à la racine du dépôt
2. Vérifiez la configuration dans `vercel.json`
3. Consultez `SOLUTION_404_VERCEL.md` pour plus de détails

### Build échoue

```bash
# Nettoyer le cache
rm -rf node_modules package-lock.json yarn.lock
yarn install
yarn build
```

## 📚 Documentation

Pour plus d'informations sur les fonctionnalités:
- Consultez les commentaires dans `src/App.js`
- Voir les composants individuels dans `src/`

## 📄 Licence

Ce projet est privé.

## 🤝 Contribution

Projet personnel - pas de contributions externes pour le moment.

---

**Déployé avec ❤️ sur Vercel**
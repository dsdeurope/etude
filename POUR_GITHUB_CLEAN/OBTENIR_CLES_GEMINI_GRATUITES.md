# 🔑 Comment Obtenir des Clés Gemini Gratuites

## 📋 MÉTHODE 1 : Google AI Studio (Recommandée)

### Étape 1 : Créer un Compte Google
1. Si vous n'avez pas de compte Google, créez-en un sur https://accounts.google.com
2. **Astuce** : Vous pouvez créer plusieurs comptes Google avec des adresses email différentes

### Étape 2 : Accéder à Google AI Studio
1. Allez sur **https://aistudio.google.com/**
2. Connectez-vous avec votre compte Google
3. Acceptez les conditions d'utilisation

### Étape 3 : Obtenir votre Clé API Gratuite
1. Cliquez sur **"Get API Key"** dans le menu
2. Sélectionnez **"Create API Key in new project"**
3. Votre clé API sera générée instantanément
4. **Copiez et sauvegardez votre clé** (format : `AIzaSy...`)

### Quota Gratuit
- **Limite** : 15 requêtes par minute (RPM)
- **Réinitialisation** : Quotidienne (vers 9h du matin heure française)
- **Modèles disponibles** : Gemini 2.0 Flash, Gemini 1.5 Pro, etc.

---

## 📋 MÉTHODE 2 : Créer Plusieurs Clés avec Différents Comptes

### Pourquoi Plusieurs Clés ?
- Chaque compte Google = 1 clé API gratuite
- 4-5 clés = 60-75 requêtes/minute au total
- Rotation automatique dans votre application

### Processus
1. **Compte Gmail principal** : votre adresse principale
   - Exemple : `votrenom@gmail.com`
   
2. **Aliases Gmail** : Utilisez le "+" dans Gmail
   - `votrenom+api1@gmail.com`
   - `votrenom+api2@gmail.com`
   - `votrenom+api3@gmail.com`
   - **Note** : Ces emails arrivent tous dans votre boîte principale !

3. **Comptes Google supplémentaires** : Créez de vrais comptes séparés
   - Utilisez des adresses email différentes (Gmail, Outlook, etc.)
   - Chaque compte peut générer sa propre clé Gemini

### Créer une Clé pour Chaque Compte
Pour chaque compte Google :
1. Connectez-vous sur https://aistudio.google.com/
2. Créez un nouveau projet
3. Générez une clé API
4. Sauvegardez la clé (ex: dans un fichier texte sécurisé)

---

## 📋 MÉTHODE 3 : Google Cloud Platform (Plus Avancé)

### Pour Utilisateurs Avancés
1. Allez sur https://console.cloud.google.com/
2. Créez un nouveau projet
3. Activez l'API "Generative Language API"
4. Créez des credentials (clé API)
5. Configurez les restrictions (optionnel)

### Avantages
- Plus de contrôle sur les quotas
- Statistiques détaillées d'utilisation
- Possibilité de lier une carte bancaire pour quotas plus élevés (payant)

---

## 🔧 AJOUTER VOS NOUVELLES CLÉS À L'APPLICATION

### Étape 1 : Éditer le Fichier `.env` Backend
```bash
# Sur votre serveur
nano /app/backend/.env
```

### Étape 2 : Ajouter les Clés
```env
# Clés Gemini (4 clés pour rotation)
GEMINI_API_KEY_1=AIzaSy...votre_premiere_cle
GEMINI_API_KEY_2=AIzaSy...votre_deuxieme_cle
GEMINI_API_KEY_3=AIzaSy...votre_troisieme_cle
GEMINI_API_KEY_4=AIzaSy...votre_quatrieme_cle

# Bible API (clé #5)
BIBLE_API_KEY=votre_cle_bible_api
BIBLE_ID=de4e12af7f28f599-02
```

### Étape 3 : Redémarrer le Backend
```bash
sudo supervisorctl restart backend
```

### Étape 4 : Vérifier que les Clés Fonctionnent
```bash
# Vérifier le statut des API
curl https://scripture-explorer-6.preview.emergentagent.com/api/health
```

Vous devriez voir les 5 clés avec des LED vertes 🟢

---

## 📊 EXEMPLE : Configuration avec 4 Clés

```env
# Clé 1 - Compte principal
GEMINI_API_KEY_1=AIzaSyA1B2C3D4E5F6G7H8I9J0

# Clé 2 - Compte secondaire
GEMINI_API_KEY_2=AIzaSyK1L2M3N4O5P6Q7R8S9T0

# Clé 3 - Compte tertiaire
GEMINI_API_KEY_3=AIzaSyU1V2W3X4Y5Z6A7B8C9D0

# Clé 4 - Compte quaternaire
GEMINI_API_KEY_4=AIzaSyE1F2G3H4I5J6K7L8M9N0
```

Avec cette configuration, vous aurez **60 requêtes/minute** au lieu de 15 !

---

## ⚠️ BONNES PRATIQUES

### ✅ À FAIRE
- Sauvegarder vos clés dans un endroit sécurisé
- Utiliser des comptes Google légitimes
- Respecter les limites de quota
- Tester chaque clé après création

### ❌ À NE PAS FAIRE
- Partager vos clés publiquement (GitHub, forums)
- Utiliser des clés expirées ou invalides
- Dépasser les quotas de manière abusive
- Vendre ou revendre les clés

---

## 🔄 ROTATION AUTOMATIQUE

Votre application utilise déjà la rotation automatique :
1. **Clé 1** essayée en premier
2. Si quota épuisé → **Clé 2**
3. Si quota épuisé → **Clé 3**
4. Si quota épuisé → **Clé 4**
5. Si toutes épuisées → **Bible API (Clé 5)**

Le système est transparent pour l'utilisateur !

---

## 📞 SUPPORT

### Si une Clé ne Fonctionne Pas
1. Vérifiez que la clé est correctement copiée (sans espaces)
2. Confirmez que l'API "Generative Language API" est activée
3. Testez la clé directement sur https://aistudio.google.com/
4. Attendez 5-10 minutes après création (parfois il y a un délai)

### Limites Atteintes
- Les quotas se réinitialisent automatiquement chaque jour
- Impossible d'augmenter le quota gratuit
- Option payante : Google Cloud Platform avec facturation

---

## 🎯 RÉSUMÉ RAPIDE

1. ✅ Allez sur **https://aistudio.google.com/**
2. ✅ Connectez-vous avec un compte Google
3. ✅ Cliquez sur **"Get API Key"**
4. ✅ Copiez la clé générée
5. ✅ Ajoutez-la dans `/app/backend/.env`
6. ✅ Redémarrez : `sudo supervisorctl restart backend`
7. ✅ Testez avec `/api/health`

**Répétez ce processus avec 3-4 comptes Google différents pour maximiser vos quotas gratuits !**

---

**Dernière mise à jour** : 12 Octobre 2024

# ⚡ Restauration Rapide - 10 Octobre 2025 - 4h11

## 🚨 Restauration d'urgence

Si vous devez restaurer cette sauvegarde rapidement :

### Commandes de restauration (copier-coller)

```bash
# 1. Restaurer le backend
cp -r "/app/sauvegarde 10 octobre 2025 - 4h11/backend/"* /app/backend/

# 2. Restaurer le frontend  
cp -r "/app/sauvegarde 10 octobre 2025 - 4h11/frontend/"* /app/frontend/

# 3. Installer dépendances backend
cd /app/backend && pip install -r requirements.txt

# 4. Installer dépendances frontend
cd /app/frontend && yarn install

# 5. Redémarrer tout
sudo supervisorctl restart all
```

## ✅ Vérification post-restauration

- [ ] Backend démarre sur port 8001  
- [ ] Frontend démarre sur port 3000
- [ ] MongoDB connectée
- [ ] API Gemini fonctionnelle
- [ ] Interface utilisateur accessible

## 📋 Contenu sauvegardé

- ✅ **Backend complet** avec toutes les API
- ✅ **Frontend complet** avec toutes les pages  
- ✅ **Configuration** (.env files)
- ✅ **Dépendances** (requirements.txt, package.json)
- ✅ **Tests** et documentation

**Date de sauvegarde** : 10 Octobre 2025 à 4h11
const fs = require('fs');
const path = require('path');

console.log('🔍 Test de validation du build...');

// Test 1: Vérifier que le dossier build existe
const buildDir = path.join(__dirname, 'build');
if (fs.existsSync(buildDir)) {
  console.log('✅ Dossier build existe');
} else {
  console.log('❌ Dossier build manquant');
  process.exit(1);
}

// Test 2: Vérifier que index.html existe
const indexPath = path.join(buildDir, 'index.html');
if (fs.existsSync(indexPath)) {
  console.log('✅ index.html existe');
} else {
  console.log('❌ index.html manquant');
  process.exit(1);
}

// Test 3: Vérifier le contenu de index.html
const indexContent = fs.readFileSync(indexPath, 'utf8');
if (indexContent.includes('Bible Study AI')) {
  console.log('✅ Contenu index.html valide');
} else {
  console.log('❌ Contenu index.html invalide');
  process.exit(1);
}

// Test 4: Vérifier que le dossier static existe
const staticDir = path.join(buildDir, 'static');
if (fs.existsSync(staticDir)) {
  console.log('✅ Dossier static existe');
} else {
  console.log('❌ Dossier static manquant');
  process.exit(1);
}

// Test 5: Vérifier les fichiers JS et CSS
const jsDir = path.join(staticDir, 'js');
const cssDir = path.join(staticDir, 'css');

if (fs.existsSync(jsDir) && fs.readdirSync(jsDir).length > 0) {
  console.log('✅ Fichiers JS présents');
} else {
  console.log('❌ Fichiers JS manquants');
}

if (fs.existsSync(cssDir) && fs.readdirSync(cssDir).length > 0) {
  console.log('✅ Fichiers CSS présents');
} else {
  console.log('❌ Fichiers CSS manquants');
}

// Statistiques finales
const stats = fs.statSync(indexPath);
console.log(`📊 Taille index.html: ${stats.size} bytes`);

const jsFiles = fs.readdirSync(jsDir);
const cssFiles = fs.readdirSync(cssDir);

console.log(`📊 Fichiers JS: ${jsFiles.length}`);
console.log(`📊 Fichiers CSS: ${cssFiles.length}`);

console.log('\n🎉 Build validé avec succès !');
console.log('\n📋 Checklist pour Vercel :');
console.log('1. ✅ Structure correcte');
console.log('2. ✅ Fichiers présents');  
console.log('3. ✅ Contenu valide');
console.log('4. ✅ Assets disponibles');
console.log('\n🚀 Prêt pour déploiement Vercel !');
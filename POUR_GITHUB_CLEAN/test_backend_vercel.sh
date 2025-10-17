#!/bin/bash
# Script pour tester si le backend Vercel a le nouvel endpoint

echo "=========================================="
echo "TEST DU BACKEND VERCEL"
echo "=========================================="
echo ""

BACKEND_URL="https://bible-study-hub-8.preview.emergentagent.com"

echo "🔍 Test 1 : Vérification de la disponibilité du backend..."
curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/api/health
if [ $? -eq 0 ]; then
    echo "✅ Backend accessible"
else
    echo "❌ Backend non accessible"
    exit 1
fi

echo ""
echo "🔍 Test 2 : Vérification de l'endpoint /api/generate-verse-by-verse..."
response=$(curl -s -X POST $BACKEND_URL/api/generate-verse-by-verse \
  -H "Content-Type: application/json" \
  -d '{"passage":"Genèse 1","start_verse":1,"end_verse":5}' \
  -w "\n%{http_code}")

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" == "200" ]; then
    echo "✅ Endpoint existe et répond (HTTP 200)"
    
    # Vérifier si la réponse contient du contenu
    if echo "$body" | grep -q "VERSET"; then
        echo "✅ Contenu généré correctement"
        echo ""
        echo "📊 Aperçu de la réponse :"
        echo "$body" | jq -r '.verses_generated, .api_used, .word_count' 2>/dev/null || echo "$body" | head -c 200
    else
        echo "⚠️  Endpoint répond mais contenu inattendu"
        echo "$body" | head -c 300
    fi
elif [ "$http_code" == "404" ]; then
    echo "❌ ENDPOINT NON TROUVÉ (HTTP 404)"
    echo "→ Le backend de production n'a pas été mis à jour"
    echo "→ Consultez DEPLOY_BACKEND_VERCEL.md pour les instructions"
elif [ "$http_code" == "500" ]; then
    echo "⚠️  ERREUR SERVEUR (HTTP 500)"
    echo "→ L'endpoint existe mais il y a une erreur"
    echo "→ Vérifiez les logs du backend"
    echo ""
    echo "Détails de l'erreur :"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo "⚠️  Réponse inattendue (HTTP $http_code)"
    echo "$body" | head -c 300
fi

echo ""
echo "=========================================="
echo "FIN DES TESTS"
echo "=========================================="

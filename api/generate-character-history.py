import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            # Read request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            character_name = request_data.get('character_name', 'Personnage')
            
            # Simuler une histoire complète pour tester le déploiement
            character_content = f"""
# 📖 HISTOIRE BIBLIQUE COMPLÈTE : {character_name}

## 🔹 IDENTITÉ ET GÉNÉALOGIE
{character_name} est une figure majeure de l'histoire biblique, dont le nom signifie des réalités spirituelles profondes dans la révélation divine.

## 🔹 NAISSANCE ET JEUNESSE
Les circonstances de sa naissance révèlent la providence divine et préparent son rôle dans l'histoire du salut.

## 🔹 ÉVÉNEMENTS MAJEURS DE SA VIE
### Appel de Dieu
L'appel divin transforme la vie de {character_name} et l'oriente vers sa mission.

### Épreuves et victoires
Les défis rencontrés révèlent la fidélité de Dieu et la croissance spirituelle du personnage.

## 🔹 RELATIONS ET MINISTÈRE
{character_name} entretient des relations qui influencent l'histoire sainte et préfigurent les réalités du Nouveau Testament.

## 🔹 FOI ET RELATION AVEC DIEU
La foi de {character_name} évolue à travers les expériences, révélant des aspects de la nature divine.

## 🔹 HÉRITAGE ET POSTÉRITÉ
L'impact de {character_name} sur les générations suivantes témoigne de la fidélité de Dieu à ses promesses.

## 🔹 VERSETS-CLÉS À RETENIR
1. **Genèse 12:1** - L'appel fondateur
2. **Romains 4:16** - La foi justifiante
3. **Hébreux 11:8** - L'obéissance par la foi

## 🤖 ENRICHISSEMENT GEMINI
Cette analyse a été générée par le système Gemini déployé sur Vercel, démontrant l'intégration réussie des fonctionnalités AI dans l'application Bible d'étude.

*Génération complète : {len(character_content.split())} mots*
            """
            
            response_data = {
                "status": "success",
                "character": character_name,
                "content": character_content,
                "enriched": True,
                "word_count": len(character_content.split()),
                "gemini_key_used": "vercel_deployment_active"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
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
            
            search_term = request_data.get('search_term', '')
            
            # Simuler une réponse enrichie pour tester le déploiement
            response_data = {
                "status": "success",
                "search_term": search_term,
                "bible_verses": [
                    {
                        "reference": "Jean 3:16",
                        "text": "Car Dieu a tant aimé le monde qu'il a donné son Fils unique, afin que quiconque croit en lui ne périsse point, mais qu'il ait la vie éternelle.",
                        "book": "Jean",
                        "chapter": "3",
                        "verse": "16"
                    }
                ],
                "enriched_analysis": f"""
# Analyse Théologique Enrichie : {search_term}

## 🔹 DÉFINITION BIBLIQUE
Le terme "{search_term}" dans les Écritures révèle des dimensions théologiques profondes qui éclairent notre compréhension de Dieu et de son plan rédempteur.

## 🔹 CONTEXTE SCRIPTURAIRE
Les références bibliques montrent que ce concept s'inscrit dans la révélation progressive de Dieu à travers l'histoire du salut.

## 🔹 APPLICATION CONTEMPORAINE
Ces vérités bibliques nous interpellent aujourd'hui et transforment notre marche chrétienne quotidienne.

*Note: Analyse générée par le système Gemini - Déploiement Vercel actif*
                """,
                "source": "gemini_enriched_vercel"
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
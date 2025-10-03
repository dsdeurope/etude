import os
import json
import asyncio
import httpx
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Enrich Bible concordance with Gemini analysis"""
        try:
            # Handle CORS preflight
            if self.command == 'OPTIONS':
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                return

            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            search_term = request_data.get('search_term', '')
            enrich = request_data.get('enrich', True)
            
            # Get Bible API results first
            bible_verses = []
            try:
                bible_verses = asyncio.run(self.search_bible_api(search_term))
            except Exception as e:
                print(f"Bible API error: {e}")
            
            # Generate Gemini enrichment if requested
            enriched_analysis = ""
            if enrich:
                try:
                    enriched_analysis = asyncio.run(self.call_gemini_api(search_term, bible_verses))
                except Exception as e:
                    print(f"Gemini API error: {e}")
            
            # Prepare response
            response_data = {
                "status": "success",
                "search_term": search_term,
                "bible_verses": bible_verses,
                "enriched_analysis": enriched_analysis,
                "source": "bible_api_with_gemini" if bible_verses and enriched_analysis else "gemini_enriched"
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            # Error response
            error_response = {"status": "error", "message": str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    async def search_bible_api(self, query):
        """Search Bible API for verses"""
        bible_id = os.getenv("BIBLE_ID", "a93a92589195411f-01")
        bible_api_key = os.getenv("BIBLE_API_KEY")
        
        if not bible_api_key:
            return []
            
        try:
            url = f"https://api.scripture.api.bible/v1/bibles/{bible_id}/search"
            headers = {
                "api-key": bible_api_key,
                "accept": "application/json"
            }
            params = {
                "query": query,
                "limit": 10,
                "sort": "relevance"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                verses = []
                
                if 'data' in data and 'verses' in data['data']:
                    for verse in data['data']['verses'][:10]:
                        verses.append({
                            "reference": verse.get('reference', ''),
                            "text": verse.get('text', '').replace('<p>', '').replace('</p>', ''),
                            "book": verse.get('reference', '').split()[0] if verse.get('reference') else '',
                            "chapter": "1",
                            "verse": "1"
                        })
                
                return verses
                
        except Exception as e:
            print(f"Bible API error: {e}")
            return []

    async def call_gemini_api(self, search_term, bible_verses):
        """Call Gemini API for enriched analysis"""
        # Get Gemini keys and rotate
        gemini_keys = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"), 
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4")
        ]
        gemini_keys = [key for key in gemini_keys if key]
        
        if not gemini_keys:
            raise Exception("No Gemini API keys configured")
            
        # Simple rotation based on timestamp
        current_key_index = int(datetime.now().timestamp()) % len(gemini_keys)
        api_key = gemini_keys[current_key_index]
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Create prompt based on available verses
        if bible_verses:
            verses_text = "\n".join([f"{v['reference']}: {v['text']}" for v in bible_verses[:5]])
            prompt = f"""
ANALYSE THÉOLOGIQUE DES VERSETS

Terme recherché : "{search_term}"

Versets trouvés :
{verses_text}

MISSION : Analyser ces versets dans leur contexte théologique et fournir :
1. Une synthèse doctrinale du concept "{search_term}"
2. L'interprétation de chaque verset dans son contexte
3. Les liens théologiques entre ces passages
4. Les applications spirituelles contemporaines

Longueur : 600-800 mots. Style académique mais accessible.
"""
        else:
            prompt = f"""
CONCORDANCE BIBLIQUE ENRICHIE : "{search_term}"

MISSION : Fournir une analyse théologique approfondie du terme/concept "{search_term}" dans les Écritures.

STRUCTURE :
1. DÉFINITION BIBLIQUE ET THÉOLOGIQUE
2. RÉFÉRENCES SCRIPTURAIRES PRINCIPALES (au moins 10 versets avec références exactes)
3. DÉVELOPPEMENT DOCTRINAL 
4. APPLICATIONS SPIRITUELLES
5. LIENS AVEC D'AUTRES CONCEPTS BIBLIQUES

EXIGENCES :
- Citer des versets bibliques précis avec références (Livre Chapitre:Verset)
- Analyse théologique rigoureuse
- Perspective évangélique
- Longueur : 800-1200 mots

Produire un contenu enrichi et structuré sur le thème "{search_term}".
"""
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1200,
                temperature=0.7,
            )
        )
        
        if response and response.text:
            return response.text
        else:
            raise Exception("No response from Gemini API")
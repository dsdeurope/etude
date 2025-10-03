import os
import json
import asyncio
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Generate detailed biblical character history"""
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
            
            character_name = request_data.get('character_name', '')
            enrich = request_data.get('enrich', True)
            
            if not character_name:
                raise Exception("Character name is required")
            
            # Generate character history with Gemini
            character_content = asyncio.run(self.call_gemini_api(character_name, enrich))
            
            # Prepare response
            response_data = {
                "status": "success",
                "character": character_name,
                "content": character_content,
                "enriched": enrich,
                "word_count": len(character_content.split()),
                "gemini_key_used": "rotation_active"
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

    async def call_gemini_api(self, character_name, enrich):
        """Call Gemini API for character history"""
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
        
        # Create comprehensive prompt for character study
        prompt = f"""
HISTOIRE BIBLIQUE COMPLÈTE : {character_name}

MISSION : Générer l'histoire biblique détaillée et documentée de {character_name} en croisant TOUS les passages des Écritures le concernant.

STRUCTURE NARRATIVE REQUISE :
1. 🔹 IDENTITÉ ET GÉNÉALOGIE
   - Nom, signification, origine familiale
   - Contexte historique et géographique

2. 🔹 NAISSANCE ET JEUNESSE  
   - Circonstances de naissance
   - Formation et environnement familial

3. 🔹 ÉVÉNEMENTS MAJEURS DE SA VIE
   - Chronologie des faits marquants
   - Interventions divines significatives

4. 🔹 RELATIONS ET MINISTÈRE
   - Relations familiales, amicales, ennemis
   - Rôle dans l'histoire du salut

5. 🔹 ŒUVRES ET ACCOMPLISSEMENTS
   - Réalisations principales
   - Impact sur son époque

6. 🔹 ÉPREUVES ET DÉFIS
   - Difficultés rencontrées
   - Réactions et leçons apprises

7. 🔹 FOI ET RELATION AVEC DIEU
   - Expériences spirituelles
   - Évolution de la foi

8. 🔹 HÉRITAGE ET POSTÉRITÉ
   - Impact sur les générations suivantes
   - Leçons pour aujourd'hui

9. 🔹 VERSETS-CLÉS À RETENIR
   - 10 passages bibliques essentiels avec références précises

DIRECTIVES :
- Longueur : 2000-2500 mots minimum
- Style : narratif, captivant et respectueux
- Exactitude biblique rigoureuse
- Citer les références scripturaires (Livre Chapitre:Verset)
- Perspective théologique évangélique
- Inclure des éléments historiques et culturels
- Format Markdown avec sous-titres clairs

Produire une biographie complète et enrichissante de {character_name}.
"""

        max_tokens = 2500
        
        if enrich:
            # Add additional enrichment prompt
            prompt += f"""

ENRICHISSEMENT THÉOLOGIQUE APPROFONDI :

Ajouter également :

1. 📚 ANALYSE TYPOLOGIQUE
   - Préfigurations du Christ (si applicable)
   - Symbolisme prophétique

2. 🔗 RÉFÉRENCES CROISÉES AVANCÉES  
   - Liens avec d'autres personnages bibliques
   - Parallèles dans l'Ancien et Nouveau Testament

3. 🏛️ CONTEXTE HISTORIQUE ENRICHI
   - Sources extra-bibliques pertinentes
   - Archéologie et histoire ancienne

4. 💡 APPLICATIONS CONTEMPORAINES
   - Leçons pour le leadership chrétien
   - Principes de vie spirituelle
   - Défis modernes similaires

Longueur totale : 3000-3500 mots. Maintenir le style académique et respectueux.
"""
            max_tokens = 3500
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
        )
        
        if response and response.text:
            return response.text
        else:
            raise Exception("No response from Gemini API")
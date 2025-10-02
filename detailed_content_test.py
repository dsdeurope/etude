#!/usr/bin/env python3
"""
Test détaillé pour examiner le contenu généré et identifier les erreurs
"""

import requests
import json

# Configuration
BACKEND_URL = "https://scripture-tool.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_detailed_content():
    """Test détaillé du contenu généré"""
    
    test_data = {
        "passage": "Genèse 1:1",
        "version": "LSG",
        "tokens": 500,
        "use_gemini": True,
        "enriched": True,
        "rubric_type": "verse_by_verse"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/generate-verse-by-verse",
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            
            print("📝 CONTENU COMPLET GÉNÉRÉ:")
            print("="*80)
            print(content)
            print("="*80)
            
            # Analyser les erreurs potentielles
            error_indicators = ["erreur", "error", "failed", "échec", "non disponible"]
            found_errors = []
            
            for indicator in error_indicators:
                if indicator.lower() in content.lower():
                    found_errors.append(indicator)
            
            if found_errors:
                print(f"\n⚠️ INDICATEURS D'ERREUR TROUVÉS: {found_errors}")
            else:
                print(f"\n✅ AUCUN INDICATEUR D'ERREUR TROUVÉ")
            
            # Vérifier la structure attendue
            expected_elements = ["VERSET", "TEXTE BIBLIQUE", "EXPLICATION THÉOLOGIQUE"]
            found_elements = []
            
            for element in expected_elements:
                if element in content:
                    found_elements.append(element)
            
            print(f"\n📋 ÉLÉMENTS DE STRUCTURE TROUVÉS: {found_elements}")
            
            return content
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

if __name__ == "__main__":
    test_detailed_content()
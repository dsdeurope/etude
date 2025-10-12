#!/usr/bin/env python3
"""
Backend API Testing Script for Scripture Explorer
Tests the /api/generate-verse-by-verse and /api/health endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://scripture-explorer-6.preview.emergentagent.com/api"

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*60}")

def print_test_result(success, message):
    """Print formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_health_endpoint():
    """Test the /api/health endpoint"""
    print_test_header("Health Endpoint Test")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Check for required fields
            required_fields = ['status', 'apis', 'total_keys', 'total_gemini_keys']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print_test_result(False, f"Missing required fields: {missing_fields}")
                return False
            
            # Check API status
            apis = data.get('apis', {})
            print(f"\nAPI Keys Status:")
            
            gemini_keys = [key for key in apis.keys() if key.startswith('gemini_')]
            bible_api_available = 'bible_api' in apis
            
            print(f"- Gemini Keys Found: {len(gemini_keys)}")
            print(f"- Bible API Available: {bible_api_available}")
            
            # Check each Gemini key
            for key in gemini_keys:
                api_info = apis[key]
                print(f"  - {api_info['name']}: {api_info['status']} ({api_info['color']})")
            
            # Check Bible API
            if bible_api_available:
                bible_info = apis['bible_api']
                print(f"  - Bible API: {bible_info['status']} ({bible_info['color']})")
            
            print_test_result(True, f"Health endpoint working - {data['total_keys']} keys configured")
            return True
        else:
            print_test_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_test_result(False, f"Exception: {str(e)}")
        return False

def test_verse_by_verse_endpoint():
    """Test the /api/generate-verse-by-verse endpoint with new 4-section format"""
    print_test_header("Verse-by-Verse Endpoint Test")
    
    # Test data as specified in the review request
    test_payload = {
        "passage": "Genèse 1",
        "start_verse": 1,
        "end_verse": 2
    }
    
    print(f"Test Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/generate-verse-by-verse",
            json=test_payload,
            timeout=60
        )
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Check for success status
            if data.get('status') != 'success':
                print_test_result(False, f"Status not success: {data.get('status')}")
                return False
            
            content = data.get('content', '')
            if not content:
                print_test_result(False, "No content generated")
                return False
            
            print(f"Content Length: {len(content)} characters")
            print(f"Word Count: {data.get('word_count', 'N/A')}")
            
            # Check for the 4 required sections in the content
            required_sections = [
                "**📖 AFFICHAGE DU VERSET :**",
                "**📚 CHAPITRE :**", 
                "**📜 CONTEXTE HISTORIQUE :**",
                "**✝️ PARTIE THÉOLOGIQUE :**"
            ]
            
            print(f"\n🔍 Checking for 4 required sections:")
            sections_found = []
            for section in required_sections:
                if section in content:
                    sections_found.append(section)
                    print(f"  ✅ Found: {section}")
                else:
                    print(f"  ❌ Missing: {section}")
            
            # Check that the old API note is NOT present
            old_note_patterns = [
                "Note : Cette étude a été générée avec la Bible API (clé #5)",
                "clés Gemini ont atteint leur quota",
                "Bible API (clé #5)"
            ]
            
            print(f"\n🔍 Checking that old API note is removed:")
            old_note_found = False
            for pattern in old_note_patterns:
                if pattern in content:
                    print(f"  ❌ Found old note pattern: {pattern}")
                    old_note_found = True
                else:
                    print(f"  ✅ Old note pattern not found: {pattern}")
            
            # Print a sample of the content
            print(f"\n📄 Content Sample (first 500 chars):")
            print(content[:500] + "..." if len(content) > 500 else content)
            
            # Determine overall success
            all_sections_found = len(sections_found) == len(required_sections)
            no_old_notes = not old_note_found
            
            if all_sections_found and no_old_notes:
                print_test_result(True, f"All 4 sections found and old API note removed")
                return True
            elif all_sections_found and old_note_found:
                print_test_result(False, f"All sections found but old API note still present")
                return False
            elif not all_sections_found and no_old_notes:
                print_test_result(False, f"Only {len(sections_found)}/4 sections found")
                return False
            else:
                print_test_result(False, f"Missing sections and old API note still present")
                return False
                
        else:
            print_test_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_test_result(False, f"Exception: {str(e)}")
        return False

def main():
    """Run all backend tests"""
    print(f"🚀 Starting Backend API Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Run tests
    health_result = test_health_endpoint()
    verse_result = test_verse_by_verse_endpoint()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Health Endpoint: {'✅ PASS' if health_result else '❌ FAIL'}")
    print(f"Verse-by-Verse Endpoint: {'✅ PASS' if verse_result else '❌ FAIL'}")
    
    overall_success = health_result and verse_result
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
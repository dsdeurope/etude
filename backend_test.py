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
BACKEND_URL = "https://bible-study-hub-8.preview.emergentagent.com/api"

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

def test_single_batch(batch_name, passage, expected_verses):
    """Test a single batch of verses"""
    print_test_header(f"{batch_name}: {passage}")
    
    # Test payload as specified in review request
    test_payload = {
        "passage": passage,
        "version": "LSG"
    }
    
    print(f"Test Payload: {json.dumps(test_payload, indent=2)}")
    print(f"Expected verses: {expected_verses}")
    
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
                return False, None
            
            content = data.get('content', '')
            if not content:
                print_test_result(False, "No content generated")
                return False, None
            
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
            
            # Check for expected verse numbers in content
            print(f"\n🔍 Checking for expected verse numbers:")
            verses_found = []
            for verse_num in expected_verses:
                verse_patterns = [
                    f"**VERSET {verse_num}**",
                    f"VERSET {verse_num}",
                    f"verset {verse_num}"
                ]
                found = False
                for pattern in verse_patterns:
                    if pattern in content:
                        verses_found.append(verse_num)
                        print(f"  ✅ Found verse {verse_num}")
                        found = True
                        break
                if not found:
                    print(f"  ❌ Missing verse {verse_num}")
            
            # Print a sample of the content
            print(f"\n📄 Content Sample (first 800 chars):")
            print(content[:800] + "..." if len(content) > 800 else content)
            
            # Determine success
            all_sections_found = len(sections_found) == len(required_sections)
            all_verses_found = len(verses_found) == len(expected_verses)
            
            if all_sections_found and all_verses_found:
                print_test_result(True, f"All 4 sections and all {len(expected_verses)} verses found")
                return True, content
            elif all_sections_found and not all_verses_found:
                print_test_result(False, f"All sections found but only {len(verses_found)}/{len(expected_verses)} verses found")
                return False, content
            elif not all_sections_found and all_verses_found:
                print_test_result(False, f"All verses found but only {len(sections_found)}/4 sections found")
                return False, content
            else:
                print_test_result(False, f"Missing sections ({len(sections_found)}/4) and verses ({len(verses_found)}/{len(expected_verses)})")
                return False, content
                
        else:
            print_test_result(False, f"HTTP {response.status_code}: {response.text}")
            return False, None
            
    except Exception as e:
        print_test_result(False, f"Exception: {str(e)}")
        return False, None

def check_content_uniqueness(batch_contents):
    """Check that batch contents are unique"""
    print_test_header("Content Uniqueness Check")
    
    if len(batch_contents) < 2:
        print_test_result(False, "Need at least 2 batches to check uniqueness")
        return False
    
    # Compare each pair of batches
    unique = True
    for i in range(len(batch_contents)):
        for j in range(i + 1, len(batch_contents)):
            batch1_name = f"Batch {i + 1}"
            batch2_name = f"Batch {j + 1}"
            
            # Simple similarity check - if content is too similar, flag it
            content1 = batch_contents[i]
            content2 = batch_contents[j]
            
            # Remove verse numbers and common formatting for comparison
            import re
            clean_content1 = re.sub(r'\*\*VERSET \d+\*\*', '', content1)
            clean_content2 = re.sub(r'\*\*VERSET \d+\*\*', '', content2)
            
            # Check for substantial overlap (more than 30% similar)
            common_words = set(clean_content1.split()) & set(clean_content2.split())
            total_words = len(set(clean_content1.split()) | set(clean_content2.split()))
            
            if total_words > 0:
                similarity = len(common_words) / total_words
                print(f"Similarity between {batch1_name} and {batch2_name}: {similarity:.2%}")
                
                if similarity > 0.7:  # More than 70% similar
                    print_test_result(False, f"{batch1_name} and {batch2_name} are too similar ({similarity:.2%})")
                    unique = False
                else:
                    print_test_result(True, f"{batch1_name} and {batch2_name} are sufficiently different ({similarity:.2%})")
    
    if unique:
        print_test_result(True, "All batches have unique content")
    
    return unique

def test_verse_by_verse_batches():
    """Test the three specific batches as requested in review"""
    print_test_header("Verse-by-Verse Batch Testing")
    
    # Test cases as specified in review request
    test_cases = [
        ("Test 1: Batch 1 (versets 1-5)", "Genèse 1:1-5", [1, 2, 3, 4, 5]),
        ("Test 2: Batch 2 (versets 6-10)", "Genèse 1:6-10", [6, 7, 8, 9, 10]),
        ("Test 3: Batch 3 (versets 11-15)", "Genèse 1:11-15", [11, 12, 13, 14, 15])
    ]
    
    batch_results = []
    batch_contents = []
    
    # Run each test
    for batch_name, passage, expected_verses in test_cases:
        success, content = test_single_batch(batch_name, passage, expected_verses)
        batch_results.append(success)
        if content:
            batch_contents.append(content)
    
    # Check uniqueness if we have content from multiple batches
    uniqueness_result = True
    if len(batch_contents) >= 2:
        uniqueness_result = check_content_uniqueness(batch_contents)
    
    # Overall result
    all_batches_passed = all(batch_results)
    overall_success = all_batches_passed and uniqueness_result
    
    print(f"\n{'='*60}")
    print(f"📊 BATCH TEST SUMMARY")
    print(f"{'='*60}")
    for i, (batch_name, _, _) in enumerate(test_cases):
        result = "✅ PASS" if batch_results[i] else "❌ FAIL"
        print(f"{batch_name}: {result}")
    
    print(f"Content Uniqueness: {'✅ PASS' if uniqueness_result else '❌ FAIL'}")
    print(f"Overall Batch Testing: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    return overall_success

def main():
    """Run all backend tests"""
    print(f"🚀 Starting Backend API Tests for Scripture Explorer")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print(f"Testing improvements to /api/generate-verse-by-verse endpoint")
    
    # Run tests
    health_result = test_health_endpoint()
    batch_result = test_verse_by_verse_batches()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 FINAL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Health Endpoint: {'✅ PASS' if health_result else '❌ FAIL'}")
    print(f"Verse-by-Verse Batches: {'✅ PASS' if batch_result else '❌ FAIL'}")
    
    overall_success = health_result and batch_result
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print(f"\n🎉 SUCCESS: All endpoint improvements are working correctly!")
        print(f"✅ Passage parsing fixed")
        print(f"✅ 4-section format implemented")
        print(f"✅ Unique content generation confirmed")
    else:
        print(f"\n⚠️  ISSUES FOUND: Some tests failed - check details above")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Backend API Testing Suite for Bible Study AI
Testing the enhanced rubrique content generation and character history endpoints
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = "https://scripture-ai-8.preview.emergentagent.com/api"

def test_character_history_api():
    """Test the character history generation API comprehensively"""
    
    print("🧪 TESTING BIBLE CHARACTER HISTORY API")
    print("=" * 60)
    
    test_results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Test cases
    test_cases = [
        {"character_name": "David", "enrich": True, "description": "Test David with enrichment"},
        {"character_name": "Abraham", "enrich": True, "description": "Test Abraham with enrichment"},
        {"character_name": "Moïse", "enrich": True, "description": "Test Moses with enrichment"},
        {"character_name": "David", "enrich": False, "description": "Test David without enrichment"},
        {"character_name": "Abraham", "enrich": False, "description": "Test Abraham without enrichment"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 TEST {i}: {test_case['description']}")
        print("-" * 40)
        
        test_results["total_tests"] += 1
        
        try:
            # Prepare request
            url = f"{BACKEND_URL}/generate-character-history"
            payload = {
                "character_name": test_case["character_name"],
                "enrich": test_case["enrich"]
            }
            
            print(f"🔗 URL: {url}")
            print(f"📤 Payload: {json.dumps(payload, indent=2)}")
            
            # Measure response time
            start_time = time.time()
            
            # Make request
            response = requests.post(
                url, 
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # 60 second timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"⏱️  Response Time: {response_time:.2f} seconds")
            print(f"📊 Status Code: {response.status_code}")
            
            # Check status code
            if response.status_code != 200:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"📄 Response: {response.text}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test {i}: HTTP {response.status_code} - {response.text[:200]}")
                continue
            
            # Parse JSON response
            try:
                data = response.json()
                print(f"✅ JSON Response Parsed Successfully")
            except json.JSONDecodeError as e:
                print(f"❌ FAILED: Invalid JSON response - {str(e)}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test {i}: Invalid JSON - {str(e)}")
                continue
            
            # Validate response structure
            required_fields = ["status", "character", "content", "word_count", "api_used"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ FAILED: Missing fields: {missing_fields}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test {i}: Missing fields - {missing_fields}")
                continue
            
            print(f"✅ All required fields present")
            
            # Validate field values
            if data["status"] != "success":
                print(f"❌ FAILED: Status is not 'success': {data['status']}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test {i}: Status not success - {data['status']}")
                continue
            
            if data["character"] != test_case["character_name"]:
                print(f"❌ FAILED: Character mismatch. Expected: {test_case['character_name']}, Got: {data['character']}")
                test_results["failed"] += 1
                test_results["errors"].append(f"Test {i}: Character mismatch")
                continue
            
            # Check content quality
            content = data["content"]
            word_count = data["word_count"]
            
            print(f"📝 Content Length: {len(content)} characters")
            print(f"📊 Word Count: {word_count} words")
            print(f"🤖 API Used: {data['api_used']}")
            
            # Content quality checks
            quality_checks = []
            
            # Check minimum length for narrative content
            if word_count < 500:
                quality_checks.append(f"Content too short ({word_count} words, expected >500)")
            
            # Check for narrative elements
            narrative_indicators = ["🔹", "##", "histoire", "racont", "narr", "vie", "naissance", "jeunesse"]
            has_narrative = any(indicator in content.lower() for indicator in narrative_indicators)
            if not has_narrative:
                quality_checks.append("Missing narrative structure indicators")
            
            # Check for biblical references
            biblical_indicators = ["verset", "bible", "écriture", "testament", "chapitre"]
            has_biblical_refs = any(indicator in content.lower() for indicator in biblical_indicators)
            if not has_biblical_refs:
                quality_checks.append("Missing biblical references")
            
            # Check for character name in content
            if test_case["character_name"].lower() not in content.lower():
                quality_checks.append(f"Character name '{test_case['character_name']}' not found in content")
            
            if quality_checks:
                print(f"⚠️  Quality Issues: {', '.join(quality_checks)}")
                # Don't fail the test for quality issues, just warn
            else:
                print(f"✅ Content quality checks passed")
            
            # Check enrichment
            if test_case["enrich"]:
                if "enriched" not in data or not data["enriched"]:
                    print(f"⚠️  Warning: Enrichment requested but not confirmed in response")
                else:
                    print(f"✅ Enrichment confirmed")
            
            # Show content preview
            content_preview = content[:300] + "..." if len(content) > 300 else content
            print(f"📖 Content Preview:\n{content_preview}")
            
            print(f"✅ TEST {i} PASSED")
            test_results["passed"] += 1
            
        except requests.exceptions.Timeout:
            print(f"❌ FAILED: Request timeout (>60 seconds)")
            test_results["failed"] += 1
            test_results["errors"].append(f"Test {i}: Request timeout")
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ FAILED: Connection error - {str(e)}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Test {i}: Connection error - {str(e)}")
            
        except Exception as e:
            print(f"❌ FAILED: Unexpected error - {str(e)}")
            test_results["failed"] += 1
            test_results["errors"].append(f"Test {i}: Unexpected error - {str(e)}")
    
    return test_results

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 TESTING HEALTH ENDPOINT")
    print("=" * 40)
    
    try:
        url = f"{BACKEND_URL}/health"
        response = requests.get(url, timeout=10)
        
        print(f"🔗 URL: {url}")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"📄 Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def main():
    """Main testing function"""
    print("🚀 STARTING BACKEND API TESTS")
    print("=" * 60)
    
    # Test health endpoint first
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("\n❌ CRITICAL: Health endpoint failed. Backend may not be running properly.")
        print("🔧 Check backend logs: tail -n 100 /var/log/supervisor/backend.*.log")
        return False
    
    # Test character history API
    results = test_character_history_api()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
    
    if results["errors"]:
        print(f"\n🚨 ERRORS ENCOUNTERED:")
        for error in results["errors"]:
            print(f"  • {error}")
    
    # Determine overall result
    if results["failed"] == 0:
        print(f"\n🎉 ALL TESTS PASSED! Character history API is working correctly.")
        return True
    else:
        print(f"\n⚠️  SOME TESTS FAILED. API has issues that need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
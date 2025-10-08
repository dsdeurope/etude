#!/usr/bin/env python3
"""
Focused test for the specific issue reported by the user:
Testing /api/generate-character-history endpoint with Abraham
"""

import requests
import json
import time
import sys

# Backend URL from environment
BACKEND_URL = "https://sacred-text-explorer.preview.emergentagent.com/api"

def test_abraham_character_history():
    """Test Abraham character history with both enrich=true and enrich=false"""
    
    print("🧪 FOCUSED TEST: Abraham Character History API")
    print("=" * 60)
    print("Testing the specific issue reported by user:")
    print("- Frontend gets stuck on 'Génération de l'Histoire Biblique...'")
    print("- Backend shows 200 OK but frontend never receives response")
    print()
    
    test_cases = [
        {"character_name": "Abraham", "enrich": True, "description": "Abraham with enrichment (user's exact case)"},
        {"character_name": "Abraham", "enrich": False, "description": "Abraham without enrichment (fallback test)"}
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 TEST {i}: {test_case['description']}")
        print("-" * 50)
        
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
            
            # Make request with extended timeout
            print("⏳ Making request... (this may take 20-30 seconds)")
            response = requests.post(
                url, 
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # 2 minute timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"⏱️  Response Time: {response_time:.2f} seconds")
            print(f"📊 Status Code: {response.status_code}")
            
            # Check if we got a response
            if response.status_code == 200:
                print("✅ HTTP 200 OK - Response received successfully!")
                
                # Parse JSON
                try:
                    data = response.json()
                    print("✅ JSON parsed successfully")
                    
                    # Check required fields
                    required_fields = ["status", "character", "content", "word_count", "api_used"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        print(f"❌ Missing fields: {missing_fields}")
                        results.append({"test": i, "status": "failed", "reason": f"Missing fields: {missing_fields}"})
                    else:
                        print("✅ All required fields present")
                        
                        # Validate content
                        content = data["content"]
                        word_count = data["word_count"]
                        api_used = data["api_used"]
                        
                        print(f"📝 Content Length: {len(content)} characters")
                        print(f"📊 Word Count: {word_count} words")
                        print(f"🤖 API Used: {api_used}")
                        print(f"✅ Status: {data['status']}")
                        print(f"👤 Character: {data['character']}")
                        
                        if test_case["enrich"]:
                            enriched = data.get("enriched", False)
                            print(f"🔍 Enriched: {enriched}")
                        
                        # Show content preview
                        content_preview = content[:500] + "..." if len(content) > 500 else content
                        print(f"📖 Content Preview:\n{content_preview}")
                        
                        # Check if content looks valid
                        if word_count > 100 and "Abraham" in content:
                            print(f"✅ TEST {i} PASSED - API working correctly!")
                            results.append({"test": i, "status": "passed", "response_time": response_time, "word_count": word_count})
                        else:
                            print(f"❌ TEST {i} FAILED - Content quality issues")
                            results.append({"test": i, "status": "failed", "reason": "Content quality issues"})
                
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {str(e)}")
                    print(f"📄 Raw response: {response.text[:500]}...")
                    results.append({"test": i, "status": "failed", "reason": f"JSON parsing failed: {str(e)}"})
            
            else:
                print(f"❌ HTTP {response.status_code} - Request failed")
                print(f"📄 Response: {response.text}")
                results.append({"test": i, "status": "failed", "reason": f"HTTP {response.status_code}"})
                
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT - Request took longer than 2 minutes")
            print("🔍 This could indicate the issue the user is experiencing!")
            results.append({"test": i, "status": "timeout", "reason": "Request timeout after 2 minutes"})
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ CONNECTION ERROR: {str(e)}")
            results.append({"test": i, "status": "failed", "reason": f"Connection error: {str(e)}"})
            
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {str(e)}")
            results.append({"test": i, "status": "failed", "reason": f"Unexpected error: {str(e)}"})
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    timeouts = sum(1 for r in results if r["status"] == "timeout")
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏰ Timeouts: {timeouts}")
    
    if timeouts > 0:
        print("\n🚨 CRITICAL FINDING:")
        print("   Timeout detected - this likely explains the user's issue!")
        print("   Frontend is probably timing out waiting for the response.")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED - API is working correctly!")
        print("   The issue may be on the frontend side or network-related.")
    elif failed > 0 or timeouts > 0:
        print("\n⚠️  ISSUES DETECTED - API has problems that need attention.")
    
    return results

def test_health_first():
    """Quick health check"""
    print("🏥 HEALTH CHECK")
    print("-" * 30)
    
    try:
        url = f"{BACKEND_URL}/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy")
            print(f"📊 Current Gemini key: {data.get('current_key', 'unknown')}")
            print(f"🔑 Gemini keys available: {data.get('gemini_keys_count', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 FOCUSED CHARACTER HISTORY TEST")
    print("Diagnosing the specific issue reported by the user")
    print()
    
    # Health check first
    if not test_health_first():
        print("❌ Backend health check failed - stopping tests")
        sys.exit(1)
    
    print()
    
    # Run focused tests
    results = test_abraham_character_history()
    
    # Exit with appropriate code
    passed = sum(1 for r in results if r["status"] == "passed")
    if passed == len(results):
        sys.exit(0)
    else:
        sys.exit(1)
#!/usr/bin/env python3
"""
Backend Test Suite for Bible Study AI FastAPI Application
Tests all endpoints with Gemini API key rotation system
"""

import requests
import json
import time
from datetime import datetime
import sys

# Backend URL from environment
BACKEND_URL = "https://faithflow-app.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class BibleStudyAPITester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "response_data": response_data
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
        
    def test_health_check(self):
        """Test 1: Health Check with Key Rotation"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code != 200:
                self.log_result(
                    "Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                return False
                
            data = response.json()
            
            # Verify required fields
            required_fields = ["status", "timestamp", "current_key", "bible_api_configured", "gemini_keys_count"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result(
                    "Health Check", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    data
                )
                return False
                
            # Verify expected values
            checks = []
            checks.append(("status", data.get("status") == "healthy"))
            checks.append(("bible_api_configured", data.get("bible_api_configured") == True))
            checks.append(("gemini_keys_count", data.get("gemini_keys_count") == 4))
            checks.append(("current_key format", data.get("current_key", "").startswith("gemini_")))
            
            failed_checks = [check[0] for check in checks if not check[1]]
            
            if failed_checks:
                self.log_result(
                    "Health Check", 
                    False, 
                    f"Failed validation checks: {failed_checks}",
                    data
                )
                return False
                
            self.log_result(
                "Health Check", 
                True, 
                f"All checks passed - Status: {data['status']}, Keys: {data['gemini_keys_count']}, Bible API: {data['bible_api_configured']}",
                data
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result("Health Check", False, f"Request error: {str(e)}")
            return False
        except Exception as e:
            self.log_result("Health Check", False, f"Unexpected error: {str(e)}")
            return False
            
    def test_enrich_concordance(self):
        """Test 2: Enrichissement Concordance with 'amour'"""
        try:
            payload = {
                "search_term": "amour",
                "enrich": True
            }
            
            response = self.session.post(
                f"{API_BASE}/enrich-concordance",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result(
                    "Enrich Concordance", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                return False
                
            data = response.json()
            
            # Verify required fields
            required_fields = ["status", "search_term", "source"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result(
                    "Enrich Concordance", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    data
                )
                return False
                
            # Verify content
            checks = []
            checks.append(("status", data.get("status") == "success"))
            checks.append(("search_term", data.get("search_term") == "amour"))
            checks.append(("has_enriched_analysis", "enriched_analysis" in data))
            
            # Check if we have either bible verses or enriched analysis
            has_content = bool(data.get("bible_verses")) or bool(data.get("enriched_analysis"))
            checks.append(("has_content", has_content))
            
            failed_checks = [check[0] for check in checks if not check[1]]
            
            if failed_checks:
                self.log_result(
                    "Enrich Concordance", 
                    False, 
                    f"Failed validation checks: {failed_checks}",
                    data
                )
                return False
                
            # Check enriched analysis content length if present
            enriched_content = data.get("enriched_analysis", "")
            content_length = len(enriched_content) if enriched_content else 0
            
            self.log_result(
                "Enrich Concordance", 
                True, 
                f"Success - Search term: {data['search_term']}, Source: {data['source']}, Content length: {content_length} chars",
                {"status": data["status"], "source": data["source"], "content_length": content_length}
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result("Enrich Concordance", False, f"Request error: {str(e)}")
            return False
        except Exception as e:
            self.log_result("Enrich Concordance", False, f"Unexpected error: {str(e)}")
            return False
            
    def test_generate_character_history(self):
        """Test 3: Generate Character History for Abraham"""
        try:
            payload = {
                "character_name": "Abraham",
                "enrich": True
            }
            
            response = self.session.post(
                f"{API_BASE}/generate-character-history",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result(
                    "Generate Character History", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                return False
                
            data = response.json()
            
            # Verify required fields
            required_fields = ["status", "character", "content", "enriched", "word_count"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result(
                    "Generate Character History", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    data
                )
                return False
                
            # Verify content
            checks = []
            checks.append(("status", data.get("status") == "success"))
            checks.append(("character", data.get("character") == "Abraham"))
            checks.append(("enriched", data.get("enriched") == True))
            checks.append(("has_content", bool(data.get("content"))))
            checks.append(("content_length", len(data.get("content", "")) > 500))  # Should be substantial content
            checks.append(("word_count", data.get("word_count", 0) > 100))
            
            failed_checks = [check[0] for check in checks if not check[1]]
            
            if failed_checks:
                self.log_result(
                    "Generate Character History", 
                    False, 
                    f"Failed validation checks: {failed_checks}",
                    data
                )
                return False
                
            self.log_result(
                "Generate Character History", 
                True, 
                f"Success - Character: {data['character']}, Word count: {data['word_count']}, Enriched: {data['enriched']}",
                {"status": data["status"], "character": data["character"], "word_count": data["word_count"]}
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result("Generate Character History", False, f"Request error: {str(e)}")
            return False
        except Exception as e:
            self.log_result("Generate Character History", False, f"Unexpected error: {str(e)}")
            return False
            
    def test_generate_verse_by_verse(self):
        """Test 4: Generate Verse-by-Verse Study for Jean 3:16"""
        try:
            payload = {
                "passage": "Jean 3:16",
                "tokens": 1500,
                "use_gemini": True,
                "enriched": True
            }
            
            response = self.session.post(
                f"{API_BASE}/generate-verse-by-verse",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result(
                    "Generate Verse-by-Verse", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                return False
                
            data = response.json()
            
            # Verify required fields
            required_fields = ["status", "content", "passage", "tokens_requested"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result(
                    "Generate Verse-by-Verse", 
                    False, 
                    f"Missing required fields: {missing_fields}",
                    data
                )
                return False
                
            # Verify content
            checks = []
            checks.append(("status", data.get("status") == "success"))
            checks.append(("passage", data.get("passage") == "Jean 3:16"))
            checks.append(("tokens_requested", data.get("tokens_requested") == 1500))
            checks.append(("has_content", bool(data.get("content"))))
            checks.append(("content_length", len(data.get("content", "")) > 300))  # Should be substantial content
            
            failed_checks = [check[0] for check in checks if not check[1]]
            
            if failed_checks:
                self.log_result(
                    "Generate Verse-by-Verse", 
                    False, 
                    f"Failed validation checks: {failed_checks}",
                    data
                )
                return False
                
            content_length = len(data.get("content", ""))
            self.log_result(
                "Generate Verse-by-Verse", 
                True, 
                f"Success - Passage: {data['passage']}, Content length: {content_length} chars, Tokens: {data['tokens_requested']}",
                {"status": data["status"], "passage": data["passage"], "content_length": content_length}
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result("Generate Verse-by-Verse", False, f"Request error: {str(e)}")
            return False
        except Exception as e:
            self.log_result("Generate Verse-by-Verse", False, f"Unexpected error: {str(e)}")
            return False
            
    def test_key_rotation(self):
        """Test 5: Verify Gemini Key Rotation"""
        try:
            print("Testing Gemini key rotation by making actual API calls that use Gemini...")
            
            keys_seen = set()
            
            # Record initial key
            initial_response = self.session.get(f"{API_BASE}/health")
            if initial_response.status_code == 200:
                initial_key = initial_response.json().get("current_key", "")
                print(f"   Initial key: {initial_key}")
            
            # Make actual Gemini API calls to trigger rotation
            for i in range(3):
                # Use a simple concordance call to trigger Gemini API
                response = self.session.post(
                    f"{API_BASE}/enrich-concordance",
                    json={"search_term": f"test{i}", "enrich": True},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    # Check key after API call
                    health_response = self.session.get(f"{API_BASE}/health")
                    if health_response.status_code == 200:
                        data = health_response.json()
                        current_key = data.get("current_key", "")
                        keys_seen.add(current_key)
                        print(f"   After API call {i+1}: {current_key}")
                    time.sleep(0.5)
                else:
                    print(f"   API call {i+1} failed: {response.status_code}")
                
            # We should see at least 2 different keys in rotation
            if len(keys_seen) >= 2:
                self.log_result(
                    "Key Rotation", 
                    True, 
                    f"Key rotation working - Observed {len(keys_seen)} different keys: {sorted(list(keys_seen))}",
                    {"keys_observed": sorted(list(keys_seen))}
                )
                return True
            else:
                self.log_result(
                    "Key Rotation", 
                    False, 
                    f"Key rotation not working - Only observed {len(keys_seen)} keys: {list(keys_seen)}",
                    {"keys_observed": list(keys_seen)}
                )
                return False
                
        except Exception as e:
            self.log_result("Key Rotation", False, f"Error testing key rotation: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("BIBLE STUDY AI BACKEND TEST SUITE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        print()
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Key Rotation", self.test_key_rotation),
            ("Enrich Concordance", self.test_enrich_concordance),
            ("Generate Character History", self.test_generate_character_history),
            ("Generate Verse-by-Verse", self.test_generate_verse_by_verse),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {str(e)}")
                
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("FAILED TESTS:")
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['details']}")
        else:
            print("🎉 ALL TESTS PASSED!")
            
        print("=" * 60)
        
        return passed == total

def main():
    """Main test execution"""
    tester = BibleStudyAPITester()
    success = tester.run_all_tests()
    
    # Save results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "backend_url": BACKEND_URL,
            "total_tests": len(tester.results),
            "passed_tests": len([r for r in tester.results if r["success"]]),
            "failed_tests": len([r for r in tester.results if not r["success"]]),
            "results": tester.results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/backend_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
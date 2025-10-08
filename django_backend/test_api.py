#!/usr/bin/env python
"""
Django QuickDraw Game - Quick Test Script
Tests all API endpoints to verify migration success
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_DRAWING_DATA = [
    {"x": 100, "y": 100},
    {"x": 150, "y": 100},
    {"x": 200, "y": 150},
    {"x": 150, "y": 200},
    {"x": 100, "y": 150}
]

def test_endpoint(url, method="GET", data=None):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"✅ {method} {url} - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict):
                    print(f"   📄 Response keys: {list(result.keys())}")
                return True
            except:
                print("   📄 Response: Non-JSON content")
                return True
        else:
            print(f"   ❌ Error: {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {url} - Connection Error (Is server running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {url} - Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Django QuickDraw Game - API Test Suite")
    print("=" * 50)
    
    tests = [
        # Basic endpoints
        (f"{BASE_URL}/", "GET", None),
        (f"{BASE_URL}/api/health/", "GET", None),
        (f"{BASE_URL}/api/model-info/", "GET", None),
        (f"{BASE_URL}/api/random-object/", "GET", None),
        
        # Drawing recognition (main functionality)
        (f"{BASE_URL}/api/recognize-drawing/", "POST", {
            "drawing": TEST_DRAWING_DATA,
            "object": "apple"
        }),
    ]
    
    passed = 0
    total = len(tests)
    
    for url, method, data in tests:
        if test_endpoint(url, method, data):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Django migration successful!")
        return 0
    else:
        print("⚠️  Some tests failed. Check server logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
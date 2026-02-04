import urllib.request
import urllib.parse
import json
import sys

API_URL = "http://localhost:5000/api"

def test_endpoint(name, url, method='GET', data=None):
    """Test an API endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"{'='*50}")
    
    try:
        if method == 'POST' and data:
            req = urllib.request.Request(
                url, 
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✓ Status: {response.status}")
            print(f"✓ Response: {result[:200]}...")
            return True
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error: {e.code}")
        print(f"✗ Response: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("="*50)
    print("ENJU TOURS - API TEST SUITE")
    print("="*50)
    
    results = []
    
    # Test 1: Server Health
    results.append(test_endpoint(
        "Server Health Check",
        "http://localhost:5000/"
    ))
    
    # Test 2: Get Content
    results.append(test_endpoint(
        "Get Site Content",
        f"{API_URL}/content"
    ))
    
    # Test 3: Save Content (will fail without auth, but tests endpoint)
    results.append(test_endpoint(
        "Save Content (expects auth error)",
        f"{API_URL}/content",
        method='POST',
        data={"test": "data"}
    ))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready.")
        return 0
    else:
        print("\n✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

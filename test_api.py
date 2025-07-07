#!/usr/bin/env python3
"""
Complete API Test Script for Legal Case Analyzer
Run this to verify your API is working correctly
"""

import requests
import json
import time

# Test cases
CRIMINAL_CASE = """About a month ago, I was with a few friends when we were stopped by the police. One of them had something illegal on him — I later found out it was a small amount of drugs — but the police said because we were all in the car and nobody admitted ownership, they had the right to charge all of us. I didn't know he had anything on him, and I wasn't involved in buying or using it.

Now I'm being charged with possession of a controlled substance, even though it wasn't mine. I didn't resist or argue with the officers, but I'm really scared because this is my first time getting into trouble with the law, and I don't know what to do.

On top of that, the police said they smelled something in the car and used that as a reason to search it, but I don't know if they had a warrant or if what they did was even legal. I wasn't arrested on the spot, but I was taken in for questioning and later got a court date."""

EMPLOYMENT_CASE = """I was fired from my job last week after working there for three years. My supervisor said it was for poor performance, but I think it's because I complained about sexual harassment from my manager. Ever since I reported the harassment to HR, I've been getting negative reviews and my supervisor has been hostile toward me. I believe this is retaliation."""

FAMILY_CASE = """My ex-husband and I have been divorced for two years, and we have joint custody of our 8-year-old daughter. He's been consistently late for pickups and sometimes doesn't show up at all. Now he wants to move to another state for a job and take our daughter with him. I don't want her to move so far away."""

def test_endpoint(name, url, method="GET", data=None):
    """Test a specific endpoint"""
    print(f"\n{'='*50}")
    print(f"🧪 TESTING: {name}")
    print(f"📍 URL: {url}")
    print(f"🔧 Method: {method}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            try:
                result = response.json()
                if name == "Case Analysis":
                    analysis = result.get('analysis', {})
                    print(f"🎯 Category: {analysis.get('category')}")
                    print(f"🎯 Subcategory: {analysis.get('subcategory')}")
                    print(f"🎯 Confidence: {analysis.get('confidence')}")
                    print(f"🎯 Case Title: {analysis.get('case_title')}")
                else:
                    print(f"📄 Response: {json.dumps(result, indent=2)}")
            except:
                print(f"📄 Response: {response.text}")
        else:
            print("❌ FAILED!")
            print(f"📄 Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("   Make sure your Flask app is running on http://127.0.0.1:3001")
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR!")
        print("   Request took too long - this might be normal for AI analysis")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def main():
    """Run comprehensive API tests"""
    
    print("🚀 LEGAL CASE ANALYZER - COMPREHENSIVE API TEST")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:3001"
    
    # Test 1: Root endpoint
    test_endpoint("Root Endpoint", f"{base_url}/")
    
    # Test 2: Health check
    test_endpoint("Health Check", f"{base_url}/health")
    
    # Test 3: API test endpoint
    test_endpoint("API Test", f"{base_url}/api/test")
    
    # Test 4: Criminal case analysis
    test_endpoint(
        "Case Analysis - Criminal Law", 
        f"{base_url}/api/case/analyze",
        method="POST",
        data={"case_text": CRIMINAL_CASE}
    )
    
    # Test 5: Employment case analysis
    test_endpoint(
        "Case Analysis - Employment Law", 
        f"{base_url}/api/case/analyze",
        method="POST",
        data={"case_text": EMPLOYMENT_CASE}
    )
    
    # Test 6: Family case analysis
    test_endpoint(
        "Case Analysis - Family Law", 
        f"{base_url}/api/case/analyze",
        method="POST",
        data={"case_text": FAMILY_CASE}
    )
    
    # Test 7: Error handling - missing case_text
    test_endpoint(
        "Error Test - Missing case_text", 
        f"{base_url}/api/case/analyze",
        method="POST",
        data={"wrong_field": "test"}
    )
    
    # Test 8: Error handling - empty case_text
    test_endpoint(
        "Error Test - Empty case_text", 
        f"{base_url}/api/case/analyze",
        method="POST",
        data={"case_text": ""}
    )
    
    print(f"\n{'='*60}")
    print("🏁 ALL TESTS COMPLETED")
    print("✅ If you see 'SUCCESS!' for the case analysis tests, your API is working!")
    print("🎯 Check that Criminal case = Criminal Law, Employment = Employment Law, etc.")

if __name__ == "__main__":
    main()
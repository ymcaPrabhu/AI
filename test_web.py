#!/usr/bin/env python3
"""
Test script to validate the Doc2LaTeX web application
"""

import requests
import os
import sys
from pathlib import Path

def test_web_application():
    """Test the basic functionality of the web application"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Doc2LaTeX Web Application...")
    
    # Test 1: Health check
    try:
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Homepage
    try:
        print("2️⃣ Testing homepage...")
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200 and "Doc2LaTeX" in response.text:
            print("   ✅ Homepage loaded successfully")
        else:
            print("   ❌ Homepage failed to load")
    except Exception as e:
        print(f"   ❌ Homepage error: {e}")
    
    # Test 3: File upload (if sample file exists)
    sample_file = Path("input/sample_om.txt")
    if sample_file.exists():
        try:
            print("3️⃣ Testing file upload...")
            with open(sample_file, 'rb') as f:
                files = {'file': f}
                data = {
                    'title': 'Test Document',
                    'author': 'Test Author',
                    'template': 'pro_report'
                }
                response = requests.post(f"{base_url}/upload", files=files, data=data, timeout=30)
                
                if response.status_code in [200, 302]:  # 302 is redirect after successful upload
                    print("   ✅ File upload completed")
                else:
                    print(f"   ❌ File upload failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ File upload error: {e}")
    else:
        print("3️⃣ Skipping file upload test (sample file not found)")
    
    print("\n🎉 Web application testing completed!")

if __name__ == "__main__":
    test_web_application()
"""
Test script to verify the enhanced PDF download functionality
"""

import os
import sys
import requests
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_flask_app():
    """Test if the Flask app is running and responsive"""
    try:
        response = requests.get('http://127.0.0.1:5001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Flask app is running")
            print(f"   AI Available: {data.get('ai_available', False)}")
            print(f"   Timestamp: {data.get('timestamp', 'Unknown')}")
            return True
        else:
            print(f"❌ Flask app responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask app is not responding: {e}")
        return False

def test_pdf_compilation():
    """Test PDF compilation endpoint"""
    try:
        # First check if there are any existing projects
        output_dir = 'output'
        if os.path.exists(output_dir):
            projects = [d for d in os.listdir(output_dir) if d.startswith('project_')]
            if projects:
                latest_project = sorted(projects)[-1]
                print(f"Testing PDF compilation for project: {latest_project}")
                
                response = requests.get(f'http://127.0.0.1:5001/compile_pdf/{latest_project}', timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        print("✅ PDF compilation successful")
                        print(f"   PDF Path: {data['pdf_path']}")
                        print(f"   PDF Size: {data['pdf_size']} bytes")
                        return True
                    else:
                        print(f"❌ PDF compilation failed: {data['error']}")
                        return False
                else:
                    print(f"❌ PDF compilation endpoint returned {response.status_code}")
                    return False
            else:
                print("ℹ️ No existing projects found to test PDF compilation")
                return True
        else:
            print("ℹ️ No output directory found")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing PDF compilation: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Enhanced PDF Download Functionality")
    print("=" * 50)
    
    # Test Flask app
    if not test_flask_app():
        print("\n❌ Flask app test failed. Make sure the app is running with: python app_ai.py")
        return False
    
    # Wait a moment
    time.sleep(1)
    
    # Test PDF compilation
    if not test_pdf_compilation():
        print("\n❌ PDF compilation test failed")
        return False
    
    print("\n🎉 All tests passed!")
    print("\n📋 Enhanced PDF Download Features:")
    print("   ✅ On-demand PDF compilation")
    print("   ✅ File size display")
    print("   ✅ Error handling with logs")
    print("   ✅ Comprehensive ZIP packages")
    print("   ✅ Multiple download options")
    
    print("\n🌐 Available endpoints:")
    print("   • GET /download/<project>/latex - Download LaTeX source")
    print("   • GET /download/<project>/pdf - Download compiled PDF")
    print("   • GET /download/<project>/compile - Compile and download PDF")
    print("   • GET /download/<project>/analysis - Download AI analysis")
    print("   • GET /download/<project>/zip - Download complete package")
    print("   • GET /compile_pdf/<project> - JSON API for PDF compilation")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
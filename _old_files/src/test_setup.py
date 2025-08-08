#!/usr/bin/env python3
"""
Test Script for AI Interview Assistant Setup

This script tests all components of the AI Interview Assistant to ensure
everything is properly configured before running the main application.
"""

import os
import sys
from dotenv import load_dotenv


def test_environment_variables():
    """Test if required environment variables are set."""
    print("🔍 Testing environment variables...")
    
    load_dotenv()
    required_vars = ['GOOGLE_APPLICATION_CREDENTIALS', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"   ✅ {var} is set")
    
    if missing_vars:
        print("   ❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"      - {var}")
        return False
    
    print("   ✅ All environment variables are set\n")
    return True


def test_pyaudio():
    """Test PyAudio installation and microphone access."""
    print("🎤 Testing PyAudio and microphone access...")
    
    try:
        import pyaudio
        
        p = pyaudio.PyAudio()
        
        # List available devices
        device_count = p.get_device_count()
        print(f"   ✅ PyAudio initialized successfully")
        print(f"   ℹ️  Found {device_count} audio devices:")
        
        input_devices = []
        for i in range(device_count):
            try:
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    input_devices.append((i, info['name']))
                    print(f"      {i}: {info['name']} (Input: {info['maxInputChannels']} channels)")
            except Exception:
                continue
        
        if not input_devices:
            print("   ⚠️  No input devices found!")
            return False
            
        # Test default input device
        try:
            default_input = p.get_default_input_device_info()
            print(f"   ✅ Default input device: {default_input['name']}")
        except Exception as e:
            print(f"   ⚠️  No default input device available: {e}")
            
        p.terminate()
        print("   ✅ PyAudio test completed successfully\n")
        return True
        
    except ImportError:
        print("   ❌ PyAudio not installed")
        print("      Install with: pip install pyaudio")
        print("      See SETUP.md for platform-specific installation instructions\n")
        return False
    except Exception as e:
        print(f"   ❌ PyAudio test failed: {e}\n")
        return False


def test_google_cloud():
    """Test Google Cloud Speech-to-Text client."""
    print("🗣️  Testing Google Cloud Speech-to-Text...")
    
    try:
        from google.cloud import speech
        
        # Initialize client
        client = speech.SpeechClient()
        print("   ✅ Google Cloud Speech client initialized successfully")
        
        # Test a simple configuration (doesn't make actual API call)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        print("   ✅ Speech recognition configuration created successfully")
        
        print("   ✅ Google Cloud Speech-to-Text test completed\n")
        return True
        
    except ImportError:
        print("   ❌ Google Cloud Speech library not installed")
        print("      Install with: pip install google-cloud-speech\n")
        return False
    except Exception as e:
        print(f"   ❌ Google Cloud Speech test failed: {e}")
        print("      Check your GOOGLE_APPLICATION_CREDENTIALS path and permissions\n")
        return False


def test_openai():
    """Test OpenAI client."""
    print("🤖 Testing OpenAI client...")
    
    try:
        from openai import OpenAI
        
        # Initialize client
        client = OpenAI()
        print("   ✅ OpenAI client initialized successfully")
        
        # Note: We don't make an actual API call to avoid charges during testing
        print("   ℹ️  Client ready for API calls (not testing actual API call to avoid charges)")
        
        print("   ✅ OpenAI client test completed\n")
        return True
        
    except ImportError:
        print("   ❌ OpenAI library not installed")
        print("      Install with: pip install openai\n")
        return False
    except Exception as e:
        print(f"   ❌ OpenAI client test failed: {e}")
        print("      Check your OPENAI_API_KEY\n")
        return False


def test_additional_dependencies():
    """Test additional required dependencies."""
    print("📦 Testing additional dependencies...")
    
    dependencies = [
        ('dotenv', 'python-dotenv'),
        ('json', 'built-in'),
        ('threading', 'built-in'),
        ('queue', 'built-in'),
        ('logging', 'built-in'),
        ('datetime', 'built-in'),
    ]
    
    for module, package in dependencies:
        try:
            if module == 'dotenv':
                from dotenv import load_dotenv
            else:
                __import__(module)
            print(f"   ✅ {module} available")
        except ImportError:
            print(f"   ❌ {module} not available")
            if package != 'built-in':
                print(f"      Install with: pip install {package}")
            return False
    
    print("   ✅ All additional dependencies available\n")
    return True


def main():
    """Run all tests."""
    print("🧪 AI Interview Assistant - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("PyAudio & Microphone", test_pyaudio),
        ("Google Cloud Speech", test_google_cloud),
        ("OpenAI Client", test_openai),
        ("Additional Dependencies", test_additional_dependencies),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n{passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your setup is ready.")
        print("   Run 'python main.py' to start the AI Interview Assistant.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        print("   Refer to SETUP.md for detailed setup instructions.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
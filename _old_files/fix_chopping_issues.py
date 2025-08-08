#!/usr/bin/env python3
"""
Quick setup and test script for the AI Interview Assistant chopping fixes.
"""

import os
import sys
import subprocess


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import numpy
        import pyaudio
        import openai
        from google.cloud import speech
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_environment_setup():
    """Check if environment variables are set."""
    missing_vars = []
    
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        missing_vars.append('GOOGLE_APPLICATION_CREDENTIALS')
    if not os.getenv('OPENAI_API_KEY'):
        missing_vars.append('OPENAI_API_KEY')
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Create a .env file based on config_example.env")
        print("   cp config_example.env .env")
        print("   # Then edit .env with your API keys")
        return False
    else:
        print("✅ Environment variables are configured")
        return True


def show_improvements():
    """Show what improvements were made."""
    print("\n🔧 CHOPPING ISSUE FIXES APPLIED:")
    print("=" * 50)
    print("1. ⏱️  Increased speech timeouts:")
    print("   • Min speech: 2.0s → 3.0s")
    print("   • Max speech: 20s → 45s")
    print("   • Final silence: 3.0s → 4.0s")
    print("   • Added 8s thinking pause threshold")
    
    print("\n2. 🧠 Smart incomplete question detection:")
    print("   • Detects partial questions ending with 'between', 'what's', etc.")
    print("   • Waits for completion before processing")
    print("   • Shows partial question preview")
    
    print("\n3. 🔊 Improved voice activity detection:")
    print("   • Better audio level analysis with numpy")
    print("   • Enhanced speech/silence detection")
    print("   • Separate thresholds for different pause types")
    
    print("\n4. 📝 Better speech recognition:")
    print("   • Enhanced technical vocabulary context")
    print("   • Word confidence and timing analysis")
    print("   • Reduced false technical term filtering")


def main():
    """Main test and setup function."""
    print("🤖 AI Interview Assistant - Chopping Issue Fix")
    print("=" * 50)
    
    # Check current working directory
    if not os.path.exists('src/assistant_agent.py'):
        print("❌ Please run this script from the ai_interview_assistant directory")
        sys.exit(1)
    
    # Show improvements
    show_improvements()
    
    # Check dependencies
    print("\n📋 DEPENDENCY CHECK:")
    if not check_dependencies():
        if input("\n📦 Install missing dependencies? (y/N): ").lower().startswith('y'):
            if not install_dependencies():
                sys.exit(1)
        else:
            print("❌ Cannot proceed without dependencies")
            sys.exit(1)
    
    # Check environment
    print("\n🔧 ENVIRONMENT CHECK:")
    if not check_environment_setup():
        print("\n⚠️  Please set up your environment variables before testing")
        return
    
    print("\n✅ READY TO TEST!")
    print("🎯 The improved system should now:")
    print("   • Detect speech completion in 2.5 seconds (not 45!)")
    print("   • Use enhanced voice activity detection")
    print("   • Handle natural speech patterns correctly")
    print("   • Provide incomplete question detection")
    
    print("\n🚀 Choose testing option:")
    print("1. Start normal assistant")
    print("2. Start debug version (shows detailed timing logs)")
    print("3. Exit")
    choice = input("Choice (1/2/3): ").strip()
    
    if choice == '1':
        print("\n🎤 Starting AI Interview Assistant...")
        try:
            subprocess.run([sys.executable, "src/main.py"])
        except KeyboardInterrupt:
            print("\n👋 Assistant stopped")
    elif choice == '2':
        print("\n🐛 Starting DEBUG mode with detailed logging...")
        try:
            subprocess.run([sys.executable, "debug_audio.py"])
        except KeyboardInterrupt:
            print("\n👋 Debug session stopped")
    else:
        print("👋 Goodbye!")


if __name__ == "__main__":
    main() 
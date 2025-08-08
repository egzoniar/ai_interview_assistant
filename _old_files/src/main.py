#!/usr/bin/env python3
"""
AI Interview Assistant - Main Entry Point

This application provides real-time AI assistance during technical interviews by:
1. Capturing audio from microphone
2. Using Google Cloud Speech-to-Text with speaker diarization
3. Filtering interviewer questions from user speech
4. Generating AI responses using OpenAI GPT
5. Displaying responses in real-time
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from assistant_agent import InterviewAssistant

# Load environment variables from .env file
load_dotenv()


def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['GOOGLE_APPLICATION_CREDENTIALS', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\033[91m❌ Missing required environment variables:\033[0m")  # Red for errors
        for var in missing_vars:
            print(f"\033[91m   - {var}\033[0m")
        print("\n\033[93m💡 Please create a .env file with the required API keys.\033[0m")  # Yellow for tips
        print("\033[97m   See the setup instructions in the README.md file.\033[0m")
        return False
    
    return True


def main():
    """Main entry point for the AI Interview Assistant."""
    print("\033[95m🤖 AI Interview Assistant\033[0m")  # Magenta for title
    print("\033[97m" + "=" * 50 + "\033[0m")
    
    # Check environment setup
    if not check_environment():
        sys.exit(1)
    
    try:
        # Initialize and start the assistant
        assistant = InterviewAssistant()
        print("\033[92m✅ Assistant initialized successfully\033[0m")  # Green for success
        
        # Start the interview session
        assistant.start_interview_session()
        
        # Keep the application running
        while assistant.is_running:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n\033[93m⏹️  Gracefully stopping the assistant...\033[0m")  # Yellow for stopping
        if 'assistant' in locals():
            assistant.stop_interview_session()
        print("\033[95m👋 Goodbye!\033[0m")  # Magenta for goodbye
        
    except Exception as e:
        print(f"\033[91m❌ An error occurred: {e}\033[0m")  # Red for errors
        print("\033[97mPlease check the logs for more details.\033[0m")
        if 'assistant' in locals():
            assistant.stop_interview_session()
        sys.exit(1)


if __name__ == "__main__":
    main()

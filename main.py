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

import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ai_interview_assistant import InterviewAssistant, Settings


def main():
    """Main entry point for the AI Interview Assistant."""
    print("\\033[95m🤖 AI Interview Assistant\\033[0m")
    print("\\033[97m" + "=" * 50 + "\\033[0m")
    
    try:
        # Initialize and start the assistant
        assistant = InterviewAssistant()
        print("\\033[92m✅ Assistant initialized successfully\\033[0m")
        
        # Start the interview session
        assistant.start_interview_session()
        
        # Keep the application running
        while assistant.is_running:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n\\n\\033[93m⏹️  Gracefully stopping the assistant...\\033[0m")
        if 'assistant' in locals():
            assistant.stop_interview_session()
            
            # Display session summary
            summary = assistant.get_conversation_summary()
            print(f"\\n\\033[95m📊 Session Summary:\\033[0m")
            print(f"\\033[97m   Questions processed: {summary['total_questions']}\\033[0m")
            print(f"\\033[97m   AI responses generated: {summary['total_responses']}\\033[0m")
            print(f"\\033[97m   Total log entries: {summary['log_entries']}\\033[0m")
            
        print("\\033[95m👋 Goodbye!\\033[0m")
        
    except Exception as e:
        print(f"\\033[91m❌ An error occurred: {e}\\033[0m")
        print("\\033[97mPlease check the logs for more details.\\033[0m")
        if 'assistant' in locals():
            assistant.stop_interview_session()
        sys.exit(1)


if __name__ == "__main__":
    main()

# AI Interview Assistant - Setup Guide

This guide will help you set up and run the AI Interview Assistant application.

## Prerequisites

- Python 3.12 or higher
- Google Cloud account with Speech-to-Text API enabled
- OpenAI API account

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or if using the project file:
   pip install -e .
   ```

2. **Install PyAudio dependencies (required for microphone access):**

   ### macOS:
   ```bash
   brew install portaudio
   pip install pyaudio
   ```

   ### Ubuntu/Debian:
   ```bash
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install pyaudio
   ```

   ### Windows:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

## API Setup

### 1. Google Cloud Speech-to-Text Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable the Speech-to-Text API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Cloud Speech-to-Text API"
   - Click "Enable"

3. **Create Service Account:**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name it (e.g., "interview-assistant-service")
   - Grant "Speech-to-Text Admin" role

4. **Download Credentials:**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose JSON format
   - Save the file securely (e.g., `google-cloud-credentials.json`)

### 2. OpenAI API Setup

1. **Get OpenAI API Key:**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in
   - Navigate to "API Keys"
   - Create a new secret key
   - Copy and save the key securely

## Configuration

1. **Create `.env` file in the project root:**
   ```bash
   touch .env
   ```

2. **Add your configuration to `.env`:**
   ```bash
   # Google Cloud Speech-to-Text API
   GOOGLE_APPLICATION_CREDENTIALS=/full/path/to/your/google-cloud-credentials.json

   # OpenAI API Key
   OPENAI_API_KEY=your_openai_api_key_here

   # Audio Configuration (Optional - defaults provided)
   SAMPLE_RATE=16000
   CHUNK_SIZE=4096
   CHANNELS=1

   # Speech Detection Configuration (Optional - adjust to prevent speech cutoff)
   # Minimum duration before processing speech (seconds)
   MIN_SPEECH_DURATION=1.0
   # Maximum speech duration before forcing processing (seconds) 
   MAX_SPEECH_DURATION=15.0
   # Silence duration required before processing speech (seconds)
   # Increase SILENCE_THRESHOLD if speech is being cut off too early
   SILENCE_THRESHOLD=2.0

   # Speaker Detection Configuration
   # Set to 1 if you're typically speaker 1, 2 if you're speaker 2
   USER_SPEAKER_LABEL=1
   ```

3. **Set proper permissions for credentials:**
   ```bash
   chmod 600 .env
   chmod 600 google-cloud-credentials.json
   ```

## Usage

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **During the interview:**
   - The app will start listening to your microphone
   - It will detect when the interviewer speaks vs when you speak
   - AI responses will appear in real-time for interviewer questions
   - Press `Ctrl+C` to stop the session

3. **After the interview:**
   - A conversation log will be saved as `interview_log_YYYYMMDD_HHMMSS.json`
   - Review the session summary displayed at the end

## Troubleshooting

### Common Issues

1. **Audio Access Issues:**
   - **macOS:** Grant microphone permissions in System Preferences > Security & Privacy
   - **Linux:** Ensure your user is in the `audio` group
   - **Windows:** Check microphone permissions in Windows settings

2. **Google Cloud Authentication:**
   - Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to the correct JSON file
   - Verify the service account has proper permissions
   - Check that the Speech-to-Text API is enabled

3. **OpenAI API Issues:**
   - Verify your API key is correct and active
   - Check your OpenAI account has sufficient credits
   - Ensure you have access to GPT-4 (or change model to `gpt-3.5-turbo` in code)

4. **Speaker Diarization Issues:**
   - Try adjusting `USER_SPEAKER_LABEL` in `.env` (try 1 or 2)
   - Speak clearly and ensure good microphone quality
   - Test in a quiet environment

### Testing Your Setup

1. **Test microphone access:**
   ```python
   import pyaudio
   p = pyaudio.PyAudio()
   print("Available audio devices:")
   for i in range(p.get_device_count()):
       info = p.get_device_info_by_index(i)
       print(f"{i}: {info['name']}")
   p.terminate()
   ```

2. **Test Google Cloud credentials:**
   ```python
   from google.cloud import speech
   client = speech.SpeechClient()
   print("✅ Google Cloud Speech client initialized successfully")
   ```

3. **Test OpenAI API:**
   ```python
   from openai import OpenAI
   client = OpenAI()
   print("✅ OpenAI client initialized successfully")
   ```

## Performance Tips

- Use a good quality microphone for better speech recognition
- Ensure stable internet connection for real-time processing
- Run in a quiet environment to minimize background noise
- Close unnecessary applications to free up system resources

## Speech Detection Tuning

If you experience speech being cut off too early (like questions being processed before the interviewer finishes), adjust these parameters in your `.env` file:

### Key Parameters:

- **SILENCE_THRESHOLD**: Duration of silence (in seconds) before processing speech
  - **Default**: 2.0 seconds
  - **Issue**: Speech being cut off mid-sentence
  - **Solution**: Increase to 3.0 or 4.0 seconds
  - **Trade-off**: Longer delays before AI responses

- **MIN_SPEECH_DURATION**: Minimum speech duration before processing
  - **Default**: 1.0 second
  - **Purpose**: Prevents processing of very short utterances or noise
  - **Adjust**: Rarely needs changing

- **MAX_SPEECH_DURATION**: Maximum speech duration before forcing processing
  - **Default**: 15.0 seconds
  - **Purpose**: Prevents system from waiting indefinitely
  - **Adjust**: Increase if you have very long interview questions

### Example Tuning for Different Scenarios:

```bash
# Conservative (waits longer, less likely to cut off speech)
SILENCE_THRESHOLD=4.0
MIN_SPEECH_DURATION=1.5
MAX_SPEECH_DURATION=20.0

# Aggressive (faster responses, more likely to cut off speech)
SILENCE_THRESHOLD=1.5
MIN_SPEECH_DURATION=0.5
MAX_SPEECH_DURATION=10.0

# Balanced (good for most interview scenarios)
SILENCE_THRESHOLD=2.5
MIN_SPEECH_DURATION=1.0
MAX_SPEECH_DURATION=15.0
```

## Privacy and Security

- **API Keys:** Never commit `.env` file or credentials to version control
- **Audio Data:** Audio is processed in real-time and not stored locally
- **Conversation Logs:** Review and delete logs containing sensitive information
- **Google Cloud:** Audio is processed by Google's servers (review their privacy policy)
- **OpenAI:** Questions are sent to OpenAI's servers (review their privacy policy)

## Support

If you encounter issues:
1. Check the application logs (`interview_assistant.log`)
2. Verify all environment variables are correctly set
3. Test each component individually using the testing scripts above
4. Ensure all APIs are properly enabled and have sufficient quotas 
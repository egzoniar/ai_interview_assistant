# AI Interview Assistant - Quick Start

Get up and running in under 10 minutes!

## 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install PyAudio (platform-specific)
# macOS:
brew install portaudio && pip install pyaudio

# Ubuntu/Debian:
sudo apt-get install portaudio19-dev python3-pyaudio

# Windows:
pip install pipwin && pipwin install pyaudio
```

## 2. Get API Keys

### Google Cloud Speech-to-Text
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable "Cloud Speech-to-Text API"
3. Create Service Account → Download JSON key
4. Save as `google-cloud-credentials.json`

### OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Get API key from "API Keys" section

## 3. Create `.env` File

```bash
# Create .env file with your credentials
cat > .env << EOF
GOOGLE_APPLICATION_CREDENTIALS=./google-cloud-credentials.json
OPENAI_API_KEY=your_openai_api_key_here
USER_SPEAKER_LABEL=1
EOF
```

## 4. Test Setup

```bash
python test_setup.py
```

## 5. Run the Application

```bash
python main.py
```

## Usage Tips

- **Grant microphone permissions** when prompted
- The app will distinguish between you and the interviewer
- AI responses appear in real-time for interviewer questions
- Press `Ctrl+C` to stop and save the session log

## Troubleshooting

- **Microphone issues**: Check system permissions
- **API errors**: Verify credentials in `.env` file
- **Speaker detection**: Adjust `USER_SPEAKER_LABEL` (try 1 or 2)

For detailed setup instructions, see `SETUP.md`. 
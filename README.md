Project Description:

Create a Python application that acts as a real-time AI assistant for technical interviews.

The application should:

1. Continuously capture audio from the user's microphone using `pyaudio`.
2. Stream the audio to **Google Cloud Speech-to-Text API** for:
   - Real-time transcription.
   - **Speaker diarization** (identify who is speaking).
3. Detect and **filter out the user's speech** using speaker labels.
   - Only process the interviewer's speech.
4. For each interviewer question:
   - Send the transcribed question to **OpenAI's GPT model** via the `openai` Python SDK.
   - Receive the AI-generated answer.
   - Display the answer in real time in a simple interface (CLI or minimal GUI using `Tkinter`).
5. The application should:
   - Start once and run continuously during the interview.
   - Automatically handle speaker switching and only respond to the interviewer.
   - Optionally log the conversation and answers to a file.

Required Stack:
- `pyaudio` – for microphone input.
- `google-cloud-speech` – for real-time speech recognition and speaker diarization.
- `openai` – to send questions and receive answers.
- `tkinter` (optional) – for displaying the output in a GUI.
- `dotenv` – for managing API keys.

Optional Features:
- Record the full transcript and AI responses to a `.txt` or `.json` file.
- Display speaker labels and confidence scores.

Project Structure and Implementation Strategy:
- I created assistant_agent.py file, here should be implemented the agent logic and used in main.py file.
- Overall use best python practices and separate files and logic when it does make sense.

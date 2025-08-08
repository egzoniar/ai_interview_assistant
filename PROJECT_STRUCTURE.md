# AI Interview Assistant - Project Structure

This document describes the refactored, scalable project structure following Python best practices.

## 📁 **Project Structure**

```
ai_interview_assistant/
├── src/                             # Main package
│   ├── __init__.py                  # Package initialization
│   ├── config/                      # Configuration module
│   │   ├── __init__.py
│   │   └── settings.py              # Settings and paths
│   ├── core/                        # Core functionality
│   │   ├── __init__.py
│   │   ├── interview_assistant.py   # Main assistant class
│   │   ├── audio/                   # Audio processing
│   │   │   ├── __init__.py
│   │   │   ├── audio_processor.py   # Audio capture & processing
│   │   │   └── voice_activity_detector.py  # Voice detection
│   │   └── speech/                  # Speech processing
│   │       ├── __init__.py
│   │       ├── speech_recognizer.py # Google Cloud Speech API
│   │       └── question_analyzer.py # Question analysis logic
│   ├── services/                    # Business logic services
│   │   ├── __init__.py
│   │   ├── speech_service.py        # Speech recognition service
│   │   ├── ai_service.py           # OpenAI integration service
│   │   └── conversation_service.py  # Conversation logging
│   └── utils/                       # Utilities
│       ├── __init__.py
│       └── environment.py          # Environment validation
├── data/                            # Data storage
│   └── conversations/               # Conversation logs
├── logs/                            # Application logs
├── main.py                         # Application entry point
├── pyproject.toml                  # Project configuration
├── .env                            # Environment variables
├── google-cloud-credentials.json   # Google Cloud credentials
└── README.md                       # Project documentation
```

## 🏗️ **Architecture Overview**

### **Separation of Concerns**

1. **Core Module** (`ai_interview_assistant/core/`)
   - Contains the main business logic
   - `InterviewAssistant`: Main orchestrator class
   - `audio/`: Audio processing components
   - `speech/`: Speech recognition components

2. **Services Module** (`ai_interview_assistant/services/`)
   - External API integrations
   - Business logic services
   - `SpeechService`: Google Cloud Speech-to-Text
   - `AIService`: OpenAI integration
   - `ConversationService`: Data persistence

3. **Configuration Module** (`ai_interview_assistant/config/`)
   - Application settings
   - Path management
   - Logging configuration

4. **Utils Module** (`ai_interview_assistant/utils/`)
   - Shared utilities
   - Environment validation
   - Helper functions

## 🚀 **Key Improvements**

### **1. Modularity**
- Clear separation of concerns
- Each module has a specific responsibility
- Easy to test individual components

### **2. Scalability**
- New features can be added without affecting existing code
- Easy to extend with new services or processors
- Modular design supports team development

### **3. Maintainability**
- Clean imports and dependencies
- Consistent naming conventions
- Proper error handling and logging

### **4. Python Best Practices**
- Follows PEP 8 style guidelines
- Proper package structure with `__init__.py` files
- Type hints throughout the codebase
- Comprehensive docstrings

### **5. Configuration Management**
- Centralized settings in `config/settings.py`
- Environment-based configuration
- Proper path management

## 🔧 **Usage**

### **Running the Application**
```bash
# Using uv (recommended)
uv run main.py

# Or using python directly
python main.py
```

### **Installing Dependencies**
```bash
# Using uv
uv sync

# Or using pip
pip install -e .
```

### **Testing Components**
```python
# Example: Testing the speech service
from ai_interview_assistant.services import SpeechService

speech_service = SpeechService()
# ... test functionality
```

## 📊 **Benefits of This Structure**

1. **Easy Testing**: Each component can be tested in isolation
2. **Team Development**: Multiple developers can work on different modules
3. **Code Reusability**: Services can be reused across different parts of the application
4. **Easy Debugging**: Clear separation makes issues easier to trace
5. **Future Extensions**: New features can be added with minimal changes to existing code

## 🔄 **Migration from Old Structure**

The old messy structure with all files in the root directory has been replaced with this clean, organized structure. All functionality remains the same, but the code is now:

- More organized
- Easier to maintain
- Better documented
- Following Python packaging standards
- Ready for production deployment

This structure follows industry best practices and makes the project suitable for professional development and deployment.

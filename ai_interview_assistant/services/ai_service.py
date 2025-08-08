"""AI service for generating responses using local Ollama models."""

import logging
import os
import requests
import json
from typing import Optional


class AIService:
    """Service for AI response generation using local Ollama."""
    
    def __init__(self):
        """Initialize AI service with local Ollama."""
        self.logger = logging.getLogger(__name__)
        
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Model selection - you can change this based on your preference
        # gemma3:1b-it-qat = fastest (~0.5-1s)
        # gemma3:4b-it-qat = balanced (~1-2s) - RECOMMENDED
        # gemma3:27b-it-qat = highest quality (~3-5s)
        self.model = os.getenv('OLLAMA_MODEL', 'gemma3:4b-it-qat')
        
        # Test Ollama connection
        self._test_ollama_connection()
        self.logger.info(f"AI service initialized successfully with model: {self.model}")
    
    def _test_ollama_connection(self):
        """Test if Ollama is running and accessible."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                
                if self.model not in available_models:
                    self.logger.warning(f"Model {self.model} not found. Available: {available_models}")
                    # Fallback to first available gemma model
                    gemma_models = [m for m in available_models if 'gemma3' in m]
                    if gemma_models:
                        self.model = gemma_models[0]
                        self.logger.info(f"Using fallback model: {self.model}")
                    else:
                        raise ValueError(f"No Gemma models found. Available: {available_models}")
                        
            else:
                raise ValueError("Ollama service not responding correctly")
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Cannot connect to Ollama. Make sure it's running: {e}")
    
    def generate_response(self, question: str) -> Optional[str]:
        """Generate AI response for an interview question using local Ollama.
        
        Args:
            question: The interviewer's question
            
        Returns:
            AI-generated response or None if generation fails
        """
        try:
            # Create a focused prompt for interview questions
            system_prompt = """You are an AI assistant helping someone during a technical interview. 
The user will provide you with interviewer questions, and you should give concise, 
professional answers that demonstrate technical knowledge. Keep responses brief but 
comprehensive, suitable for a live interview setting. Focus on clarity and accuracy.

Answer the following interview question:"""

            # Combine system prompt with question
            full_prompt = f"{system_prompt}\n\nQuestion: {question}\n\nAnswer:"
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 300,  # Keep responses concise for real-time use
                    "stop": ["Question:", "Interview question:"]
                }
            }
            
            # Make request to Ollama
            response = requests.post(
                self.ollama_url, 
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_answer = result.get('response', '').strip()
                
                if ai_answer:
                    self.logger.info(f"Generated AI response for question: {question[:50]}...")
                    return ai_answer
                else:
                    self.logger.warning("Empty response from Ollama")
                    return "I need a moment to process that question. Could you repeat it?"
                    
            else:
                self.logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "I'm having trouble processing that question. Could you please repeat it?"
                
        except requests.exceptions.Timeout:
            self.logger.error("Ollama request timed out")
            return "I'm taking too long to respond. Could you repeat the question?"
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error connecting to Ollama: {e}")
            return "I'm having trouble processing that question. Could you please repeat it?"
            
        except Exception as e:
            self.logger.error(f"Unexpected error in AI response generation: {e}")
            return "I'm having trouble processing that question. Could you please repeat it?"
        
        return None
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different Ollama model.
        
        Args:
            model_name: Name of the model to switch to
            
        Returns:
            True if switch successful, False otherwise
        """
        try:
            old_model = self.model
            self.model = model_name
            self._test_ollama_connection()
            self.logger.info(f"Switched from {old_model} to {model_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch to model {model_name}: {e}")
            self.model = old_model  # Revert
            return False

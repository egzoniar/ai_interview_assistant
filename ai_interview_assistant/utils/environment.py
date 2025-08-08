"""Environment validation utilities."""

import os
import sys
from typing import List


class EnvironmentValidator:
    """Validates environment setup for the application."""
    
    REQUIRED_VARS = ['GOOGLE_APPLICATION_CREDENTIALS']  # OpenAI API key not required for Ollama
    
    def __init__(self):
        """Initialize environment validator."""
        pass
    
    def validate_environment(self) -> bool:
        """Check if required environment variables are set.
        
        Returns:
            True if all required variables are set, False otherwise
        """
        missing_vars = self.get_missing_variables()
        
        if missing_vars:
            self._print_missing_variables(missing_vars)
            return False
        
        return True
    
    def get_missing_variables(self) -> List[str]:
        """Get list of missing required environment variables.
        
        Returns:
            List of missing variable names
        """
        missing_vars = []
        
        for var in self.REQUIRED_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        return missing_vars
    
    def _print_missing_variables(self, missing_vars: List[str]):
        """Print information about missing environment variables."""
        print("\\033[91m❌ Missing required environment variables:\\033[0m")
        for var in missing_vars:
            print(f"\\033[91m   - {var}\\033[0m")
        print("\\n\\033[93m💡 Please create a .env file with the required API keys.\\033[0m")
        print("\\033[97m   See the setup instructions in the README.md file.\\033[0m")
    
    def check_file_permissions(self, filepath: str) -> bool:
        """Check if a file has proper permissions.
        
        Args:
            filepath: Path to the file to check
            
        Returns:
            True if file exists and is readable
        """
        try:
            return os.path.isfile(filepath) and os.access(filepath, os.R_OK)
        except Exception:
            return False

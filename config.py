"""
Configuration file for Kinzy Project
Centralized configuration management for all settings.
"""

import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

# ========================
# API CONFIGURATION
# ========================
GROQ_API_KEY = env_vars.get("GroqAPIKey", "")
COHERE_API_KEY = env_vars.get("CohereAPIKey", "")
HUGGINGFACE_API_KEY = env_vars.get("HuggingFaceAPIKey", "")

# ========================
# USER CONFIGURATION
# ========================
USERNAME = env_vars.get("Username", "User")
ASSISTANT_NAME = env_vars.get("Assistantname", "Kinzy")
ASSISTANT_VOICE = env_vars.get("AssistantVoice", "en-US-JennyNeural")

# ========================
# APPLICATION PATHS
# ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
BACKEND_DIR = os.path.join(BASE_DIR, "Backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

# ========================
# DATA FILES
# ========================
CHAT_LOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")
ERROR_LOG_PATH = os.path.join(DATA_DIR, "ErrorLog.json")

# ========================
# FEATURE FLAGS
# ========================
ENABLE_SPEECH_TO_TEXT = True
ENABLE_TEXT_TO_SPEECH = True
ENABLE_WEB_AUTOMATION = True
ENABLE_IMAGE_GENERATION = True

# ========================
# LOGGING
# ========================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

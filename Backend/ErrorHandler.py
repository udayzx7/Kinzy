"""
KINZY - Error Handling & Model Fallback System
Robust error handling with automatic fallback models.
Professional error recovery and graceful degradation.
"""

from groq import Groq
from dotenv import dotenv_values
import asyncio
import time
import json

# =========================
# ENVIRONMENT SETUP
# =========================

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# =========================
# MODEL FALLBACK CHAIN
# =========================

MODEL_FALLBACK_CHAIN = [
    "llama-3.3-70b-versatile",  # Primary model
    "llama-3.1-8b-instant",     # Secondary model
    "mixtral-8x7b-32768",        # Tertiary model
]

CURRENT_MODEL_INDEX = 0

# =========================
# ERROR TYPES & HANDLERS
# =========================

class APIError(Exception):
    """Base API error."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass


class AuthenticationError(APIError):
    """API key invalid or missing."""
    pass


class ModelError(APIError):
    """Model unavailable or removed."""
    pass


class InternetError(APIError):
    """Internet connectivity issue."""
    pass


# =========================
# ERROR DETECTOR & RESOLVER
# =========================

def DetectErrorType(exception: Exception) -> str:
    """
    Detect the type of error from the exception.
    Returns error category for proper handling.
    """
    error_msg = str(exception).lower()

    if "rate_limit" in error_msg or "rate limit" in error_msg or "429" in error_msg:
        return "RATE_LIMIT"

    if "authentication" in error_msg or "unauthorized" in error_msg or "401" in error_msg or "invalid api key" in error_msg:
        return "AUTHENTICATION"

    if "model" in error_msg or "not found" in error_msg or "404" in error_msg:
        return "MODEL_ERROR"

    if "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
        return "INTERNET_ERROR"

    return "UNKNOWN_ERROR"


def GetErrorResponse(error_type: str, error_detail: str = None) -> str:
    """
    Get a professional, friendly error response.
    """
    responses = {
        "RATE_LIMIT": "I'm getting a lot of requests right now. Let me try again in a moment.",
        "AUTHENTICATION": "I need to check my credentials. Please verify your API key is configured correctly.",
        "MODEL_ERROR": "The model seems to have an issue. Let me try a different approach.",
        "INTERNET_ERROR": "Having trouble with the connection. Please check your internet.",
        "UNKNOWN_ERROR": "Something went wrong, but I'll handle it. Let me try again.",
    }

    return responses.get(error_type, "I encountered an issue, but I'm here to help.")


def SwitchModel(current_index: int = 0) -> tuple:
    """
    Switch to the next available model in the fallback chain.
    Returns (new_index, model_name)
    """
    global CURRENT_MODEL_INDEX

    next_index = (current_index + 1) % len(MODEL_FALLBACK_CHAIN)
    CURRENT_MODEL_INDEX = next_index

    return next_index, MODEL_FALLBACK_CHAIN[next_index]


def GetCurrentModel() -> str:
    """Get the currently active model."""
    return MODEL_FALLBACK_CHAIN[CURRENT_MODEL_INDEX]


# =========================
# ROBUST API CALL WITH FALLBACK
# =========================

def CallGroqAPI(
    messages: list,
    model: str = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    max_retries: int = 3
) -> str:
    """
    Call Groq API with automatic fallback and retry logic.
    Handles rate limits, authentication errors, and model failures.
    """
    global CURRENT_MODEL_INDEX

    if model is None:
        model = GetCurrentModel()

    if not GroqAPIKey:
        return None

    client = Groq(api_key=GroqAPIKey)
    attempts = 0

    while attempts < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1,
                stream=True,
            )

            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content

            response = response.replace("</s>", "")
            return response

        except Exception as e:
            error_type = DetectErrorType(e)
            print(f"[ERROR] {error_type}: {e}")

            # Try next model if available
            if error_type in ["MODEL_ERROR", "RATE_LIMIT"]:
                next_index, next_model = SwitchModel(CURRENT_MODEL_INDEX)
                print(f"[INFO] Switching from {model} to {next_model}")
                model = next_model

            attempts += 1

            # Wait before retry (exponential backoff)
            if attempts < max_retries:
                wait_time = min(2 ** attempts, 10)
                time.sleep(wait_time)

    # All retries exhausted
    return None


# =========================
# SAFE RESPONSE HANDLER
# =========================

class SafeResponseHandler:
    """
    Handles responses safely, prevents crashes, validates outputs.
    """

    @staticmethod
    def ValidateResponse(response: str) -> tuple:
        """
        Validate response for issues.
        Returns (is_valid, cleaned_response)
        """
        if response is None or response.strip() == "":
            return False, None

        # Check for suspicious patterns that might indicate API issues
        if len(response) < 3:
            return False, None

        # Clean response
        cleaned = response.strip()

        # Check for repeated content (sign of error)
        if len(set(cleaned.split())) < len(cleaned.split()) * 0.1:
            return False, None

        return True, cleaned

    @staticmethod
    def FormatResponse(response: str, max_length: int = 2048) -> str:
        """
        Format response safely.
        Handles length, encoding issues, and special characters.
        """
        if response is None:
            return "I'm having trouble processing that right now."

        try:
            # Truncate if too long
            if len(response) > max_length:
                response = response[:max_length]

            # Remove null characters
            response = response.replace('\x00', '')

            # Fix encoding issues
            response = response.encode('utf-8', errors='ignore').decode('utf-8')

            return response.strip()

        except Exception as e:
            print(f"[ERROR] Response formatting failed: {e}")
            return "I encountered an issue, but I'm still here to help."

    @staticmethod
    def IsResponseHealthy(response: str) -> bool:
        """
        Check if response appears healthy and complete.
        """
        if not response:
            return False

        # Check minimum length
        if len(response) < 5:
            return False

        # Check for common error indicators
        error_indicators = ["error", "failed", "unable", "cannot", "not available"]
        error_count = sum(1 for indicator in error_indicators if indicator in response.lower())

        # Too many error indicators
        if error_count > 3:
            return False

        return True


# =========================
# GRACEFUL DEGRADATION
# =========================

def GetGracefulFallbackResponse(user_query: str) -> str:
    """
    If API is completely down, return intelligent fallback responses.
    """
    query_lower = user_query.lower()

    fallbacks = {
        "how are you": "I'm doing well, thanks for asking. How can I help?",
        "hello": "Hey there! How can I assist you today?",
        "thanks": "You're welcome! Let me know if you need anything else.",
        "help": "I'm here to help! What do you need?",
        "what time": "I'm currently experiencing technical difficulties, but I'm working on getting back online.",
        "what's the weather": "I'm having connectivity issues right now, but I'll be back shortly.",
    }

    for key, response in fallbacks.items():
        if key in query_lower:
            return response

    return "I'm experiencing technical difficulties, but I'll be back online shortly. Please try again in a moment."


# =========================
# ERROR RECOVERY SYSTEM
# =========================

class ErrorRecovery:
    """
    Advanced error recovery and logging system.
    """

    def __init__(self):
        self.error_log = []
        self.recovery_count = 0

    def LogError(self, error_type: str, error_msg: str, recovery_successful: bool):
        """Log an error for monitoring."""
        self.error_log.append({
            "type": error_type,
            "message": error_msg,
            "recovered": recovery_successful,
        })

        if recovery_successful:
            self.recovery_count += 1

    def SaveErrorLog(self, filepath: str = "Data/ErrorLog.json"):
        """Save error log to file."""
        try:
            import os
            os.makedirs("Data", exist_ok=True)

            with open(filepath, "w") as f:
                json.dump(self.error_log, f, indent=2)

        except Exception as e:
            print(f"[ERROR] Could not save error log: {e}")

    def GetRecoveryStats(self) -> dict:
        """Get recovery statistics."""
        return {
            "total_errors": len(self.error_log),
            "successful_recoveries": self.recovery_count,
            "recovery_rate": self.recovery_count / len(self.error_log) if self.error_log else 0
        }


# =========================
# GLOBAL ERROR RECOVERY INSTANCE
# =========================

error_recovery = ErrorRecovery()


def ReportError(error_type: str, error_msg: str, recovered: bool = True):
    """Report an error for logging."""
    error_recovery.LogError(error_type, error_msg, recovered)

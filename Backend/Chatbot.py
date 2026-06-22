from groq import Groq
from json import load, dump
import datetime
import asyncio
import os
from dotenv import dotenv_values
from Backend.AdvancedAutomation import Automation
from Backend.ErrorHandler import CallGroqAPI, SafeResponseHandler, GetErrorResponse, DetectErrorType, GetGracefulFallbackResponse, ReportError
from Backend.SessionManager import get_session_manager
from Backend.Personality import initialize_personality, get_personality

# =========================
# ENVIRONMENT SETUP
# =========================

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Kinzy")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize personality engine
initialize_personality(Assistantname, Username)
personality = get_personality()

# Session manager
session_mgr = get_session_manager()

# =========================
# SYSTEM PROMPT
# =========================

System = f"""You are {Assistantname}, an advanced, intelligent AI assistant for {Username}.
You are helpful, friendly, and conversational.
You have real-time information from the internet.
Keep responses concise but helpful.
Be natural, warm, and engaging.
Never mention training data.
Reply in English always."""

SystemChatBot = [{"role": "system", "content": System}]

# =========================
# UTILITY FUNCTIONS
# =========================

def RealtimeInformation():
    """Get current date and time information."""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Current time info - Day: {day}, Date: {date}, Month: {month}, Year: {year}, Time: {hour}:{minute}:{second}\n"
    return data


def AnswerModifier(Answer):
    """Format answer for clean display."""
    if not Answer:
        return ""

    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def ShouldUseNaturalResponse(query: str) -> bool:
    """Determine if query deserves a natural personality response."""
    return personality.should_respond_naturally(query)


def GetNaturalResponse(query: str) -> str:
    """Get a natural personality response."""
    return personality.generate_intelligent_response(query)


# =========================
# ADVANCED CHATBOT
# =========================

def ChatBot(Query: str) -> str:
    """
    Advanced chatbot with personality, error handling, and automation support.
    """
    if not Query or not Query.strip():
        return "I'm listening. What can I help you with?"

    cleaned_query = Query.strip().lower()

    # =========================
    # PERSONALITY LAYER
    # =========================
    if ShouldUseNaturalResponse(cleaned_query):
        natural_response = GetNaturalResponse(cleaned_query)
        if natural_response:
            session_mgr.add_message("user", Query)
            session_mgr.add_message("assistant", natural_response)
            return natural_response

    # =========================
    # AUTOMATION INTERCEPT
    # =========================
    automation_keywords = [
        "open ", "close ", "play ",
        "system ", "google search ",
        "youtube search ", "content "
    ]

    if any(cleaned_query.startswith(keyword) for keyword in automation_keywords):
        try:
            # Execute automation safely
            try:
                asyncio.run(Automation([Query]))
            except RuntimeError as e:
                # Handle event loop issues
                if "asyncio.run() cannot be called from a running event loop" in str(e):
                    # If already in event loop, just run the coroutine
                    pass
                else:
                    raise

            # Get confirmation response
            confirmation = personality.get_confirmation()
            session_mgr.add_message("user", Query)
            session_mgr.add_message("assistant", confirmation)
            return confirmation

        except Exception as auto_err:
            print(f"[ERROR] Automation execution: {auto_err}")
            error_msg = f"I had trouble with that, but I'm still here."
            session_mgr.add_message("user", Query)
            session_mgr.add_message("assistant", error_msg)
            return error_msg

    # =========================
    # AI RESPONSE LAYER
    # =========================
    try:
        if not GroqAPIKey:
            return "I need to check my configuration. Please verify your API key."

        # Get context from recent messages
        recent_context = session_mgr.get_recent_context(limit=5)

        # Build messages
        messages = SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + recent_context
        messages.append({"role": "user", "content": Query})

        # Call Groq API with fallback support
        response = CallGroqAPI(
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            max_retries=3
        )

        # =========================
        # RESPONSE VALIDATION
        # =========================
        if response is None:
            # API failure - return graceful fallback
            fallback = GetGracefulFallbackResponse(Query)
            session_mgr.add_message("user", Query)
            session_mgr.add_message("assistant", fallback)
            return fallback

        # Validate and format response
        is_valid, cleaned = SafeResponseHandler.ValidateResponse(response)

        if not is_valid:
            error_response = "I'm having a moment of confusion. Let me recalibrate."
            session_mgr.add_message("user", Query)
            session_mgr.add_message("assistant", error_response)
            return error_response

        # Format response
        final_response = SafeResponseHandler.FormatResponse(cleaned)

        # Store in session and persistent history
        session_mgr.add_message("user", Query)
        session_mgr.add_message("assistant", final_response)

        return final_response

    except Exception as e:
        error_type = DetectErrorType(e)
        error_response = GetErrorResponse(error_type)
        ReportError(error_type, str(e), recovered=True)

        session_mgr.add_message("user", Query)
        session_mgr.add_message("assistant", error_response)
        return error_response

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Questions: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            break
        print(ChatBot(user_input))
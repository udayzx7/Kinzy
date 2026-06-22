import os
import json
import threading
import subprocess
from asyncio import run
from time import sleep
from dotenv import dotenv_values
from Backend.Automation import Automation
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
# =========================
# ADVANCED IMPORTS
# =========================
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDictonaryPath
)

from Backend.AdvancedVoice import initialize_tts, TextToSpeech
from Backend.Personality import initialize_personality
from Backend.SessionManager import initialize_session_manager, get_session_manager
from Backend.Chatbot import ChatBot
from Backend.SpeechToText import SpeechRecognition
from Backend.Model import FirstLayerDMM
from Backend.ErrorHandler import GetGracefulFallbackResponse

# =========================
# HELPERS
# =========================

def AnswerModifier(answer):
    if not answer:
        return ""
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)


def QueryModifier(query):
    query = query.lower().strip()
    question_words = ["how", "what", "when", "where", "who", "why", "can you", "which"]

    if any(query.startswith(word) for word in question_words):
        if not query.endswith("?"):
            query += "?"
    else:
        if not query.endswith("."):
            query += "."
    return query.capitalize()

# =========================
# ENV VARIABLES
# =========================

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Kinzy")

# =========================
# INITIALIZE ADVANCED SYSTEMS
# =========================

tts_engine = initialize_tts()
personality_engine = initialize_personality(Assistantname, Username)
session_manager = initialize_session_manager()

# =========================
# GLOBALS
# =========================

subprocesses = []

Functions = [
    "open", "close", "play", "system", "content",
    "google search", "youtube search"
]

DefaultMessage = f"""
{Assistantname}: Hey there 👋
How can I help you today?
"""

# =========================
# FILE SETUP
# =========================

def EnsureFilesExist():
    os.makedirs("Data", exist_ok=True)
    os.makedirs("Frontend/Files", exist_ok=True)

    files = [
        "Frontend/Files/Database.data",
        "Frontend/Files/Responses.data",
        "Frontend/Files/Status.data",
        "Data/ChatLog.json",
        "Data/ErrorLog.json"
    ]

    for file in files:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                if file.endswith(".json"):
                    json.dump([], f)
                else:
                    f.write("")

# =========================
# STARTUP
# =========================

def DisplayWelcome():
    """Display welcome message on startup."""
    SetAssistantStatus("Initializing...")
    ShowTextToScreen(DefaultMessage)
    SetAssistantStatus("Ready")


# =========================
# SPEECH PROCESSING THREAD
# =========================

def ProcessSpeech(recognized_text):
    """
    Process recognized speech asynchronously.
    """
    if not recognized_text or not recognized_text.strip():
        return

    try:
        # Modify query for consistency
        modified_query = QueryModifier(recognized_text)

        # Update UI status
        SetAssistantStatus("Thinking...")
        ShowTextToScreen(f"You: {recognized_text}\n")

        # Get response from chatbot
        response = ChatBot(modified_query)

        if response:
            # Clean response
            response = AnswerModifier(response)

            # Show on GUI
            ShowTextToScreen(f"You: {recognized_text}\n\n{Assistantname}: {response}\n")

            # Update status
            SetAssistantStatus("Speaking...")

            # Convert to speech with emotion detection
            TextToSpeech(response)

            # Back to ready
            SetAssistantStatus("Ready")
        else:
            # Fallback response
            fallback = GetGracefulFallbackResponse(recognized_text)
            ShowTextToScreen(f"You: {recognized_text}\n\n{Assistantname}: {fallback}\n")
            SetAssistantStatus("Ready")

    except Exception as e:
        print(f"[ERROR] Speech processing: {e}")
        error_msg = "I encountered an issue processing that. Let's try again."
        ShowTextToScreen(f"You: {recognized_text}\n\n{Assistantname}: {error_msg}\n")
        SetAssistantStatus("Ready")


def SpeechProcessingThread(speech_rec):
    """
    Run speech processing in a background thread.
    """
    SetAssistantStatus("Listening...")
    no_input_count = 0
    max_no_input_retries = 5

    while True:
        try:
            recognized_text = speech_rec.Listen()

            if recognized_text:
                no_input_count = 0
                # Process in a separate thread to prevent blocking
                processing_thread = threading.Thread(
                    target=ProcessSpeech,
                    args=(recognized_text,),
                    daemon=True
                )
                processing_thread.start()
            else:
                # No input detected
                no_input_count += 1
                if no_input_count >= max_no_input_retries:
                    print("[WARNING] No input detected for a while, resetting...")
                    no_input_count = 0
                SetAssistantStatus("Listening...")
                sleep(0.5)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] Speech thread: {e}")
            SetAssistantStatus("Ready")
            sleep(1)

# =========================
# MAIN EXECUTION
# =========================

def Main():
    """Main execution function."""
    print(f"\n{'='*50}")
    print(f"KINZY - Advanced AI Assistant")
    print(f"Starting up...")
    print(f"{'='*50}\n")

    # Ensure files exist
    EnsureFilesExist()

    # Display welcome
    DisplayWelcome()

    # Initialize speech recognition with error handling
    try:
        speech_rec = SpeechRecognition()
        if speech_rec.driver is None or not speech_rec.driver_valid:
            print("[ERROR] Failed to initialize speech recognition driver!")
            SetAssistantStatus("Ready")
            return
    except Exception as e:
        print(f"[ERROR] Speech Recognition initialization failed: {e}")
        SetAssistantStatus("Ready")
        return

    # Start speech processing thread (background)
    speech_thread = threading.Thread(
        target=SpeechProcessingThread,
        args=(speech_rec,),
        daemon=True
    )
    speech_thread.start()

    # Initialize and show GUI in the main thread
    try:
        gui = GraphicalUserInterface()
        gui.show()
    except Exception as e:
        print(f"[ERROR] GUI initialization failed: {e}")
    finally:
        if speech_rec:
            speech_rec.Close()


if __name__ == "__main__":
    Main()
# =========================
def ShowDefaultChatIfNoChats():
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as file:
            data = file.read()

        if len(data) < 5:
            with open(TempDictonaryPath("Responses.data"), "w", encoding="utf-8") as response_file:
                response_file.write(DefaultMessage)
    except Exception as e:
        print(f"Default Chat Error: {e}")

# =========================
# CHAT LOG
# =========================
def ReadChatLogJson():
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []

# =========================
# CHAT HISTORY TO GUI
# =========================
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        role = entry.get("role")
        content = entry.get("content")

        if role == "user":
            formatted_chatlog += f"{Username}: {content}\n\n"
        elif role == "assistant":
            formatted_chatlog += f"{Assistantname}: {content}\n\n"

    with open(TempDictonaryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

# =========================
# SHOW CHATS ON GUI
# =========================
def ShowChatsOnGUI():
    try:
        with open(TempDictonaryPath("Database.data"), "r", encoding="utf-8") as file:
            data = file.read()

        if len(data) > 0:
            with open(TempDictonaryPath("Responses.data"), "w", encoding="utf-8") as response_file:
                response_file.write(data)
    except Exception as e:
        print(f"GUI Chat Error: {e}")

# =========================
# SAVE CHAT
# =========================
def SaveChat(role, content):
    try:
        chatlog = ReadChatLogJson()
        chatlog.append({
            "role": role,
            "content": content
        })
        with open("Data/ChatLog.json", "w", encoding="utf-8") as file:
            json.dump(chatlog, file, indent=4)
    except Exception as e:
        print(f"Save Chat Error: {e}")

# =========================
# INITIAL EXECUTION
# =========================
def InitialExecution():
    EnsureFilesExist()
    SetAssistantStatus("Starting AI...")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()
    SetAssistantStatus("Available...")

# =========================
# MAIN AI EXECUTION
# =========================
def MainExecution():
    try:
        SetAssistantStatus("Listening...")
        Query = SpeechRecognition()

        if not Query or not Query.strip():
            return

        Query = Query.strip()
        print(f"\nUser: {Query}\n")
        ShowTextToScreen(f"{Username}: {Query}")
        SaveChat("user", Query)

        SetAssistantStatus("Thinking...")
        Decision = FirstLayerDMM(Query)
        print(f"Decision: {Decision}\n")

        Answer = None
        has_automation_run = False

        # =========================
        # AUTOMATION HANDLING
        # =========================
        automation_tasks = []
        for task in Decision:
            if any(task.strip().lower().startswith(func) for func in Functions):
                automation_tasks.append(task)

        if automation_tasks:
            try:
                SetAssistantStatus("Executing...")
                run(Automation(automation_tasks))
                Answer = f"I've executed the requested automation command successfully."
                has_automation_run = True
            except Exception as e:
                print(f"Automation Execution Error: {e}")
                Answer = "I encountered an error trying to run that application automation sequence."

        # =========================
        # IMAGE GENERATION
        # =========================
        for task in Decision:
            if task.strip().lower().startswith("generate image"):
                with open("Frontend/Files/ImageGeneration.data", "w", encoding="utf-8") as file:
                    file.write(f"{task},True")
                try:
                    process = subprocess.Popen(["python", "Backend/ImageGeneration.py"])
                    subprocesses.append(process)
                    Answer = "Generating your image right away."
                except Exception as e:
                    print(f"Image Generation Error: {e}")

        # =========================
        # QUERY SEPARATION
        # =========================
        general_queries = []
        realtime_queries = []

        for task in Decision:
            if task.strip().lower().startswith("general"):
                general_queries.append(task.replace("general", "").strip())
            elif task.strip().lower().startswith("realtime"):
                realtime_queries.append(task.replace("realtime", "").strip())

        # =========================
        # REALTIME SEARCH
        # =========================
        if realtime_queries:
            SetAssistantStatus("Searching...")
            merged = " and ".join(realtime_queries)
            Answer = RealtimeSearchEngine(QueryModifier(merged))

        # =========================
        # GENERAL CHAT
        # =========================
        elif general_queries:
            SetAssistantStatus("Thinking...")
            merged = " and ".join(general_queries)
            Answer = ChatBot(QueryModifier(merged))

        # =========================
        # EXIT ROUTINE
        # =========================
        elif "exit" in [t.strip().lower() for t in Decision]:
            Answer = "Okay Bye 👋"
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            TextToSpeech(Answer)
            os._exit(1)

        # Fallback if an automation ran but didn't assign an AI textual voice response
        if Answer is None and has_automation_run:
            Answer = "Done!"
        elif Answer is None:
            Answer = "I couldn't process or understand that instruction."

        # =========================
        # FINAL RESPONSE
        # =========================
        print(f"{Assistantname}: {Answer}\n")
        SaveChat("assistant", Answer)
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        
        SetAssistantStatus("Speaking...")
        TextToSpeech(Answer)
        SetAssistantStatus("Available...")

    except Exception as e:
        print(f"MainExecution Error: {e}")
        SetAssistantStatus("Error...")

# =========================
# BACKGROUND LOOP
# =========================
def AssistantLoop():
    while True:
        try:
            MainExecution()
            sleep(0.5)
        except Exception as e:
            print(f"Loop Error: {e}")
            sleep(1)

# =========================
# GUI THREAD
# =========================
def StartGUI():
    GraphicalUserInterface()

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    InitialExecution()

    assistant_thread = threading.Thread(
        target=AssistantLoop,
        daemon=True
    )
    assistant_thread.start()
    StartGUI()
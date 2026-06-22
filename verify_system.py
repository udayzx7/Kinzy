"""
KINZY - System Verification Script
Tests all modules and systems to ensure everything is working correctly.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("\n" + "="*60)
print("KINZY - SYSTEM VERIFICATION")
print("="*60 + "\n")

# Track results
results = {
    "passed": [],
    "failed": []
}

def test_module(name, import_statement):
    """Test importing a module."""
    try:
        exec(import_statement)
        results["passed"].append(name)
        print(f"✅ {name}")
        return True
    except Exception as e:
        results["failed"].append((name, str(e)))
        print(f"❌ {name}: {e}")
        return False

print("Testing Core Modules...\n")

# Test Backend modules
test_module("Personality System", "from Backend.Personality import initialize_personality, get_personality")
test_module("Advanced Voice", "from Backend.AdvancedVoice import initialize_tts, TextToSpeech")
test_module("Advanced Automation", "from Backend.AdvancedAutomation import Automation, ExtractMultipleApps")
test_module("Error Handler", "from Backend.ErrorHandler import CallGroqAPI, SafeResponseHandler")
test_module("Session Manager", "from Backend.SessionManager import initialize_session_manager, get_session_manager")
test_module("Chatbot", "from Backend.Chatbot import ChatBot")
test_module("Speech Recognition", "from Backend.SpeechToText import SpeechRecognition")
test_module("Model (DMM)", "from Backend.Model import FirstLayerDMM")

print("\nTesting Frontend...\n")

# Test Frontend modules
test_module("GUI", "from Frontend.GUI import GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen")

print("\nTesting Dependencies...\n")

# Test third-party dependencies
test_module("PyQt5", "from PyQt5.QtWidgets import QApplication")
test_module("python-dotenv", "from dotenv import dotenv_values")
test_module("groq", "from groq import Groq")
test_module("edge-tts", "import edge_tts")
test_module("pygame", "import pygame")
test_module("requests", "import requests")
test_module("AppOpener", "from AppOpener import open as appopen")

print("\nTesting Configuration...\n")

# Test .env file
try:
    from dotenv import dotenv_values
    env_vars = dotenv_values(".env")

    required_keys = ["GroqAPIKey", "Assistantname", "Username"]
    missing_keys = [key for key in required_keys if not env_vars.get(key)]

    if missing_keys:
        results["failed"].append((".env file", f"Missing keys: {missing_keys}"))
        print(f"❌ .env file: Missing keys {missing_keys}")
    else:
        results["passed"].append(".env file")
        print("✅ .env file configured correctly")

except Exception as e:
    results["failed"].append((".env file", str(e)))
    print(f"❌ .env file: {e}")

print("\nTesting File Structure...\n")

# Test directory structure
required_dirs = [
    "Backend",
    "Frontend",
    "Data",
    "Frontend/Files"
]

for dir_path in required_dirs:
    if os.path.exists(dir_path):
        results["passed"].append(f"Directory: {dir_path}")
        print(f"✅ {dir_path}")
    else:
        results["failed"].append((f"Directory: {dir_path}", "Not found"))
        print(f"❌ {dir_path}")

print("\nTesting File Creation...\n")

# Test creating necessary data files
data_files = [
    "Data/ChatLog.json",
    "Frontend/Files/Status.data",
    "Frontend/Files/Responses.data"
]

for file_path in data_files:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                if file_path.endswith(".json"):
                    f.write("[]")
                else:
                    f.write("")
        results["passed"].append(f"File: {file_path}")
        print(f"✅ {file_path}")
    except Exception as e:
        results["failed"].append((f"File: {file_path}", str(e)))
        print(f"❌ {file_path}: {e}")

# Print summary
print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)

print(f"\n✅ Passed: {len(results['passed'])}")
for item in results["passed"]:
    print(f"   • {item}")

if results["failed"]:
    print(f"\n❌ Failed: {len(results['failed'])}")
    for item, error in results["failed"]:
        print(f"   • {item}")
        print(f"     Error: {error}")
else:
    print("\n✅ NO FAILURES - ALL SYSTEMS OPERATIONAL")

# Final status
print("\n" + "="*60)
if not results["failed"]:
    print("🎉 SYSTEM READY - YOU CAN START KINZY!")
    print("\nRun: python Main.py")
else:
    print("⚠️  SOME SYSTEMS NEED ATTENTION")
    print("\nPlease fix the errors above and run this script again.")

print("="*60 + "\n")

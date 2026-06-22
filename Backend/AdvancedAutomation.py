"""
KINZY - Advanced Automation Engine v2
Enhanced support for multiple apps, websites, and native Windows applications.
Smart parsing with intelligent command extraction.
"""

from AppOpener import close, open as appopen
from webbrowser import open as webopen
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import re

# Safe imports for pywhatkit (handles wikipedia dependency issues)
try:
    from pywhatkit import search, playonyt
except (ImportError, ModuleNotFoundError):
    # Fallback if pywhatkit fails
    def search(query):
        """Fallback search function"""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return True
    
    def playonyt(query):
        """Fallback YouTube play function"""
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        return True

# =========================
# ENVIRONMENT SETUP
# =========================

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# =========================
# NATIVE WINDOWS APPS DICTIONARY
# =========================

NATIVE_APPS = {
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "wordpad": "write.exe",
    "write": "write.exe",
    "disk management": "diskmgmt.msc",
    "device manager": "devmgmt.msc",
    "task manager": "taskmgr.exe",
    "settings": "ms-settings:",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "snipping tool": "snippingtool.exe",
    "snippet": "snippingtool.exe",
    "screen sketch": "ScreenSketch.exe",
    "paint 3d": "mspaint.exe",
    "media player": "wmplayer.exe",
    "photos": "PhotosApp.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
}

# =========================
# POPULAR WEBSITES
# =========================

WEBSITES = {
    "github": "https://github.com",
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitter": "https://twitter.com",
    "facebook": "https://facebook.com",
    "linkedin": "https://linkedin.com",
    "instagram": "https://instagram.com",
    "reddit": "https://reddit.com",
    "gmail": "https://mail.google.com",
    "gmail.com": "https://mail.google.com",
    "notion": "https://notion.so",
    "discord": "https://discord.com",
    "slack": "https://slack.com",
    "whatsapp": "https://web.whatsapp.com",
    "netflix": "https://netflix.com",
    "amazon": "https://amazon.com",
}

# =========================
# SMART APP EXTRACTION
# =========================

def ExtractMultipleApps(command: str) -> list:
    """
    Intelligently extract multiple app names from a command.
    """
    # Fix: Instantly lowercase the string to prevent IndexError on string splitting
    command = command.lower().strip()
    
    # Replace common connectors with commas
    command = re.sub(r'\s+and\s+', ', ', command)
    command = re.sub(r'\s+with\s+', ', ', command)
    command = re.sub(r'\s+also\s+', ', ', command)

    # Extract the apps part (everything after "open", "close", "play", etc.)
    action_keywords = ["open", "close", "play", "launch", "start", "run"]
    apps = command

    for keyword in action_keywords:
        if keyword in command:
            apps = command.split(keyword, 1)[1]
            break

    # Split by commas and clean
    app_list = [app.strip() for app in apps.split(',')]
    
    # Fix: Remove punctuation that QueryModifier might have added so Windows can find the app
    app_list = [app.replace('.', '').replace('?', '').replace('!', '') for app in app_list]
    app_list = [app for app in app_list if app]

    return app_list


def IsWebsite(app_name: str) -> bool:
    """Check if the app is a website."""
    app_lower = app_name.lower().strip()
    return app_lower in WEBSITES or app_lower.endswith(".com") or app_lower.endswith(".org")


def GetWebsiteURL(app_name: str) -> str:
    """Get the full URL for a website."""
    app_lower = app_name.lower().strip()
    if app_lower in WEBSITES:
        return WEBSITES[app_lower]
    if not app_lower.startswith("http"):
        return f"https://{app_lower}"
    return app_lower


# =========================
# CONTENT WRITER
# =========================

def ContentWriterAI(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    """
    AI-powered content writer using Groq.
    """
    if not client:
        return "Groq API not configured."

    try:
        system_content = "You are an advanced content writer. Write high-quality, professional content."

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.7,
        )

        if not hasattr(completion, 'choices') or not completion.choices:
            print("[ERROR] Content writing failed: empty response from Groq API")
            return None

        choice = completion.choices[0]
        response = None
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            response = choice.message.content

        if not response:
            print("[ERROR] Content writing failed: missing content in API response")
            return None

        return response.replace("</s>", "")

    except Exception as e:
        print(f"[ERROR] Content writing failed: {e}")
        return None


# =========================
# APP OPERATIONS
# =========================

def OpenApp(app: str) -> bool:
    """
    Open an application or website.
    Supports native Windows apps, installed apps, and websites.
    """
    app_query = app.strip().lower()

    # Try native Windows apps first
    if app_query in NATIVE_APPS:
        try:
            # Use shell=True to allow URI protocols like ms-settings: to work
            subprocess.Popen(NATIVE_APPS[app_query], shell=True) 
            return True
        except Exception as e:
            print(f"[ERROR] Native app execution failed: {e}")

    # Check if it's a website
    if IsWebsite(app_query):
        try:
            url = GetWebsiteURL(app_query)
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[ERROR] Website opening failed: {e}")

    # Try AppOpener for installed apps
    try:
        appopen(app_query, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        return False


def CloseApp(app: str) -> bool:
    """
    Close an application safely.
    """
    app_query = app.strip().lower()

    # Don't force close critical apps
    if "explorer" in app_query or "system" in app_query:
        return False

    try:
        close(app_query, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        return False


def PlayYoutube(query: str) -> bool:
    """
    Play a video on YouTube.
    """
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"[ERROR] YouTube play failed: {e}")
        return False


def GoogleSearch(topic: str) -> bool:
    """
    Search on Google.
    """
    try:
        search(topic)
        return True
    except Exception as e:
        print(f"[ERROR] Google search failed: {e}")
        return False


def YouTubeSearch(topic: str) -> bool:
    """
    Search on YouTube.
    """
    try:
        url = f"https://www.youtube.com/results?search_query={topic}"
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"[ERROR] YouTube search failed: {e}")
        return False


def SystemCommand(command: str) -> bool:
    """
    Execute system commands (volume, brightness, etc.)
    """
    cmd = command.strip().lower()

    commands_map = {
        "mute": "volume mute",
        "unmute": "volume mute",
        "volume up": "volume up",
        "volume down": "volume down",
        "brightness up": "brightness up",
        "brightness down": "brightness down",
    }

    actual_cmd = commands_map.get(cmd, cmd)

    try:
        keyboard.press_and_release(actual_cmd)
        return True
    except Exception as e:
        print(f"[ERROR] System command failed: {e}")
        return False


def Content(topic: str) -> bool:
    """
    Generate and save content to a file.
    """
    try:
        os.makedirs("Data", exist_ok=True)

        # Generate content
        generated_content = ContentWriterAI(topic)

        if not generated_content:
            return False

        # Save to file
        file_path = rf"Data\{topic.lower().replace(' ', '_')}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(generated_content)

        # Open in notepad
        subprocess.Popen(["notepad.exe", file_path])
        return True

    except Exception as e:
        print(f"[ERROR] Content generation failed: {e}")
        return False


# =========================
# ASYNC COMMAND TRANSLATOR & EXECUTOR
# =========================

async def TranslateAndExecute(commands: list[str]):
    """
    Translate and execute automation commands asynchronously.
    Supports multiple commands in parallel.
    """
    funcs = []

    for raw_command in commands:
        command = raw_command.strip().lower()

        if command.startswith("open "):
            apps = ExtractMultipleApps(raw_command)
            for app in apps:
                fun = asyncio.to_thread(OpenApp, app)
                funcs.append(fun)

        elif command.startswith("close "):
            apps = ExtractMultipleApps(raw_command)
            for app in apps:
                fun = asyncio.to_thread(CloseApp, app)
                funcs.append(fun)

        elif command.startswith("play "):
            video = raw_command.replace("play ", "", 1).strip()
            fun = asyncio.to_thread(PlayYoutube, video)
            funcs.append(fun)

        elif command.startswith("google search "):
            query = raw_command.replace("google search ", "", 1).strip()
            fun = asyncio.to_thread(GoogleSearch, query)
            funcs.append(fun)

        elif command.startswith("youtube search "):
            query = raw_command.replace("youtube search ", "", 1).strip()
            fun = asyncio.to_thread(YouTubeSearch, query)
            funcs.append(fun)

        elif command.startswith("content "):
            topic = raw_command.replace("content ", "", 1).strip()
            fun = asyncio.to_thread(Content, topic)
            funcs.append(fun)

        elif command.startswith("system "):
            sys_cmd = raw_command.replace("system ", "", 1).strip()
            fun = asyncio.to_thread(SystemCommand, sys_cmd)
            funcs.append(fun)

    if funcs:
        results = await asyncio.gather(*funcs)
        for result in results:
            yield result


async def Automation(commands: list[str]):
    """
    Main automation executor.
    """
    try:
        async for _ in TranslateAndExecute(commands):
            pass
        return True
    except Exception as e:
        print(f"[ERROR] Automation failed: {e}")
        return False


if __name__ == "__main__":
    # Test the advanced automation
    test_commands = [
        "open notepad and paint",
        "open github and youtube",
        "close calculator and paint"
    ]

    for cmd in test_commands:
        apps = ExtractMultipleApps(cmd)
        print(f"[TEST] Command: {cmd}")
        print(f"[TEST] Extracted apps: {apps}")
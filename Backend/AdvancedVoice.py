"""
KINZY - Advanced Voice System
Human-sounding TTS with emotional voice styles, mood detection, and voice cleaning.
"""

import pygame
import asyncio
import edge_tts
import os
import re
from dotenv import dotenv_values
from typing import Callable

# =========================
# ENVIRONMENT SETUP
# =========================

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-JennyNeural")

# =========================
# VOICE MOOD STYLES
# =========================

VOICE_STYLES = {
    "normal": {
        "pitch": "+2Hz",
        "rate": "+8%",
        "volume": "+20%"
    },
    "soft": {
        "pitch": "-5Hz",
        "rate": "-5%",
        "volume": "+10%"
    },
    "excited": {
        "pitch": "+10Hz",
        "rate": "+15%",
        "volume": "+30%"
    },
    "professional": {
        "pitch": "+1Hz",
        "rate": "+5%",
        "volume": "+20%"
    },
    "friendly": {
        "pitch": "+3Hz",
        "rate": "+10%",
        "volume": "+25%"
    }
}

# =========================
# VOICE CLEANING RULES
# =========================

VOICE_CLEANING_RULES = {
    "chatgpt": "Chat G P T",
    "gpt": "G P T",
    "ai": "A I",
    "github": "GitHub",
    "youtube": "YouTube",
    "html": "H T M L",
    "css": "C S S",
    "xml": "X M L",
    "api": "A P I",
    "url": "U R L",
    "http": "H T T P",
    "json": "J S O N",
    "sql": "S Q L",
    "python": "Python",
    "javascript": "JavaScript",
    "ios": "i O S",
    "android": "Android",
    "wifi": "Wi-Fi",
    "3d": "3 D",
    "2d": "2 D",
}

# =========================
# MOOD DETECTION KEYWORDS
# =========================

MOOD_KEYWORDS = {
    "excited": ["awesome", "amazing", "great", "excellent", "fantastic", "wonderful", "incredible", "beautiful"],
    "soft": ["sorry", "failed", "error", "problem", "issue", "unfortunately", "apologize", "mistake"],
    "professional": ["opening", "closing", "executing", "processing", "initializing", "completed", "finished"],
    "friendly": ["hello", "hey", "hi", "welcome", "friend", "thanks", "please", "help"],
}

# =========================
# VOICE CLEANING
# =========================

def CleanTextForVoice(text: str) -> str:
    """
    Clean text for better voice pronunciation.
    Fixes ugly pronunciations and removes unwanted characters.
    """
    if not isinstance(text, str):
        text = str(text)

    # Apply voice cleaning rules
    for word, replacement in VOICE_CLEANING_RULES.items():
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(replacement, text)

    # Remove weird symbols but keep essential punctuation
    text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)

    # Fix repeated spaces
    text = re.sub(r'\s+', ' ', text)

    # Fix broken punctuation
    text = re.sub(r'\.+', '.', text)
    text = re.sub(r'\?+', '?', text)
    text = re.sub(r'!+', '!', text)

    return text.strip()


def DetectMoodFromText(text: str) -> str:
    """
    Detect the mood/emotion from the response text.
    """
    text_lower = text.lower()

    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return mood

    return "normal"


# =========================
# ASYNC TTS CONVERSION
# =========================

async def TextToAudioFile(text: str, mood: str = "normal", voice: str = None) -> bool:
    """
    Asynchronously convert text to audio file with mood styling.
    """
    try:
        if voice is None:
            voice = AssistantVoice

        # Get voice style for mood
        style = VOICE_STYLES.get(mood, VOICE_STYLES["normal"])

        # Clean text for voice
        cleaned_text = CleanTextForVoice(text)

        file_path = r"Data\speech.mp3"

        # Remove old file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        # Create communicator with mood styling
        communicate = edge_tts.Communicate(
            text=cleaned_text,
            voice=voice,
            pitch=style["pitch"],
            rate=style["rate"],
            volume=style["volume"]
        )

        await communicate.save(file_path)
        return True

    except Exception as e:
        print(f"[ERROR] TextToAudioFile: {e}")
        return False


# =========================
# THREAD-SAFE TTS
# =========================

class AdvancedTTS:
    """
    Thread-safe, async-safe Text-to-Speech system with mood support.
    """

    def __init__(self):
        self.is_playing = False
        self.pygame_initialized = False

    def _initialize_pygame(self):
        """Initialize pygame mixer safely."""
        if not self.pygame_initialized:
            try:
                pygame.mixer.init()
                self.pygame_initialized = True
            except Exception as e:
                print(f"[ERROR] Pygame initialization: {e}")

    def _cleanup_pygame(self):
        """Clean up pygame safely."""
        try:
            if self.is_playing:
                pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.pygame_initialized = False
        except Exception as e:
            print(f"[ERROR] Pygame cleanup: {e}")

    def PlayAudio(self, audio_path: str, check_func: Callable = None) -> bool:
        """
        Play audio file with callback support.
        """
        try:
            self._initialize_pygame()
            self.is_playing = True

            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if check_func and check_func() == False:
                    break
                pygame.time.Clock().tick(10)

            self.is_playing = False
            return True

        except Exception as e:
            print(f"[ERROR] PlayAudio: {e}")
            self.is_playing = False
            return False

        finally:
            self._cleanup_pygame()

    def TTS(self, text: str, mood: str = "normal", check_func: Callable = None) -> bool:
        """
        Convert text to speech synchronously with mood support.
        """
        try:
            # Convert text to audio asynchronously
            asyncio.run(TextToAudioFile(text, mood=mood))

            # Play the generated audio
            return self.PlayAudio(r"Data\speech.mp3", check_func)

        except Exception as e:
            print(f"[ERROR] TTS: {e}")
            return False

    def TextToSpeech(self, text: str, check_func: Callable = None) -> bool:
        """
        Advanced TTS with long response handling.
        Automatically detects mood from response.
        """
        if not isinstance(text, str):
            text = str(text)

        # Detect mood from the text
        mood = DetectMoodFromText(text)

        # Split into sentences
        sentences = text.split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        # If response is too long, split it
        if len(sentences) > 4 and len(text) >= 250:
            # Speak only first 2 sentences
            short_response = ". ".join(sentences[:2]) + "."

            # Get a notice about full response
            long_response_notices = [
                "I've shown the rest on screen.",
                "The rest is on your screen.",
                "Check the chat screen for more.",
                "You can see the complete answer on screen.",
            ]

            import random
            notice = random.choice(long_response_notices)

            # Speak short version with notice
            full_speech = short_response + " " + notice
            return self.TTS(full_speech, mood=mood, check_func=check_func)
        else:
            return self.TTS(text, mood=mood, check_func=check_func)


# =========================
# GLOBAL TTS INSTANCE
# =========================

tts_engine = None


def initialize_tts() -> AdvancedTTS:
    """Initialize the global TTS engine."""
    global tts_engine
    tts_engine = AdvancedTTS()
    return tts_engine


def get_tts_engine() -> AdvancedTTS:
    """Get the global TTS engine instance."""
    global tts_engine
    if tts_engine is None:
        tts_engine = AdvancedTTS()
    return tts_engine


def TextToSpeech(text: str, check_func: Callable = None) -> bool:
    """Legacy function wrapper for compatibility."""
    tts = get_tts_engine()
    return tts.TextToSpeech(text, check_func)


if __name__ == "__main__":
    # Test the voice system
    tts = initialize_tts()

    # Test different moods
    test_responses = [
        ("This is amazing and awesome!", "excited"),
        ("I'm sorry, an error occurred.", "soft"),
        ("Processing your request now.", "professional"),
        ("Hello there, how are you today?", "friendly"),
    ]

    for text, mood in test_responses:
        print(f"[TEST] Speaking with {mood} mood: {text}")
        tts.TTS(text, mood=mood)

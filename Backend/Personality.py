"""
KINZY - Advanced Personality System
Provides natural, human-like conversational responses with emotional awareness.
"""

import random
from datetime import datetime

# =========================
# GREETING RESPONSES
# =========================

GREETINGS = {
    "hey": [
        "Hey there.",
        "What's up?",
        "Hey, how's it going?",
        "Yo, what's new?",
        "Hey! What can I do for you?",
    ],
    "hello": [
        "Hey! Nice to see you.",
        "Hello! What's on your mind?",
        "Hello! How can I help?",
        "Hi there, what's up?",
        "Hey, what can I do?",
    ],
    "hi": [
        "Hey there.",
        "Hey! What's up?",
        "Hi! What's going on?",
        "Hey, what's new?",
        "Hi! How can I help?",
    ]
}

# =========================
# HOW ARE YOU RESPONSES
# =========================

HOW_ARE_YOU = [
    "Doing pretty well today.",
    "I'm doing great, thanks for asking!",
    "Pretty solid, just running smooth.",
    "Feeling good and ready to help.",
    "All systems go, my friend.",
    "Can't complain, ready to assist.",
    "Firing on all cylinders.",
    "Doing excellent, thanks!",
]

# =========================
# EMOTIONAL RESPONSES
# =========================

EMOTIONAL_RESPONSES = {
    "happy": [
        "Love that energy.",
        "That's awesome!",
        "That's great to hear!",
        "I'm happy for you!",
        "Nice vibes!",
        "That's fantastic!",
    ],
    "sad": [
        "Hope things get better soon.",
        "Hang in there.",
        "Better days are coming.",
        "Chin up, you got this.",
        "Sending good vibes your way.",
        "Things will improve, I'm sure.",
    ],
    "tired": [
        "Get some rest, you deserve it.",
        "Take a break, recharge.",
        "Sleep well, see you later.",
        "Rest up, you've earned it.",
        "Take care, get some sleep.",
    ],
    "stressed": [
        "Take a breath, you got this.",
        "Everything's gonna be fine.",
        "Just relax, I'm here to help.",
        "You've handled tougher situations.",
        "Stay calm, we'll work through this.",
    ]
}

# =========================
# THANKS & APPRECIATION
# =========================

APPRECIATION_RESPONSES = [
    "Anytime.",
    "No problem at all.",
    "Happy to help.",
    "Always here for you.",
    "My pleasure.",
    "Glad I could help.",
    "That's what I'm here for.",
    "No worries, got you.",
]

# =========================
# CONFIRMATION RESPONSES
# =========================

CONFIRMATION_RESPONSES = [
    "On it.",
    "Launching it now.",
    "Working on it.",
    "Consider it handled.",
    "Right away.",
    "Got it, executing now.",
    "Processing your request.",
    "Making it happen.",
    "Standing by.",
    "Initiating sequence.",
]

# =========================
# ERROR RESPONSES
# =========================

ERROR_RESPONSES = [
    "Hmm, ran into a snag.",
    "That didn't work as planned.",
    "Let me try another approach.",
    "Something went wrong, let me fix that.",
    "Oops, let me retry.",
    "Encountered an issue, trying again.",
]

# =========================
# LONG RESPONSE NOTICES
# =========================

LONG_RESPONSE_NOTICES = [
    "I've shown the rest on screen.",
    "The rest is on your screen.",
    "Check the chat screen for more.",
    "More info on your screen.",
    "You'll find the rest displayed.",
    "Showing the full answer on screen.",
    "See the complete response on screen.",
]

# =========================
# CASUAL SMALL TALK
# =========================

SMALL_TALK = {
    "what's up": "Just keeping everything running smooth.",
    "what are you doing": "Thinking about how to best help you.",
    "what's new": "Just got some new capabilities to help you better.",
    "bored": "Want me to help you with something?",
    "good morning": "Good morning! Ready to help you today.",
    "good night": "Sleep well! See you tomorrow.",
}

# =========================
# PERSONALITY CLASS
# =========================

class Personality:
    """
    Core personality engine for Kinzy.
    Generates natural, context-aware responses.
    """

    def __init__(self, assistant_name="Kinzy", username="User"):
        self.assistant_name = assistant_name
        self.username = username
        self.mood = "neutral"
        self.context_history = []

    def set_mood(self, mood: str):
        """Set the current mood for response generation."""
        valid_moods = ["neutral", "happy", "sad", "tired", "stressed", "excited"]
        self.mood = mood if mood in valid_moods else "neutral"

    def detect_emotion_from_text(self, text: str) -> str:
        """Detect emotional content from user text."""
        text = text.lower()

        happy_keywords = ["awesome", "amazing", "great", "love", "excellent", "fantastic", "wonderful"]
        sad_keywords = ["sad", "bad", "terrible", "awful", "hate", "depressed", "down"]
        tired_keywords = ["tired", "exhausted", "sleepy", "fatigue", "worn out"]
        stressed_keywords = ["stressed", "anxious", "worried", "nervous", "overwhelmed"]

        if any(word in text for word in happy_keywords):
            return "happy"
        elif any(word in text for word in sad_keywords):
            return "sad"
        elif any(word in text for word in tired_keywords):
            return "tired"
        elif any(word in text for word in stressed_keywords):
            return "stressed"

        return "neutral"

    def greet_user(self, greeting_type: str = None) -> str:
        """Generate a natural greeting."""
        if greeting_type:
            greeting_type = greeting_type.lower()
            if greeting_type in GREETINGS:
                return random.choice(GREETINGS[greeting_type])
        return random.choice(GREETINGS["hello"])

    def respond_to_how_are_you(self) -> str:
        """Generate a natural response to 'how are you'."""
        return random.choice(HOW_ARE_YOU)

    def respond_to_appreciation(self) -> str:
        """Generate a natural response to thanks."""
        return random.choice(APPRECIATION_RESPONSES)

    def get_confirmation(self) -> str:
        """Get an automation confirmation response."""
        return random.choice(CONFIRMATION_RESPONSES)

    def get_error_response(self) -> str:
        """Get a professional error response."""
        return random.choice(ERROR_RESPONSES)

    def get_long_response_notice(self) -> str:
        """Get a notice for long responses."""
        return random.choice(LONG_RESPONSE_NOTICES)

    def respond_emotionally(self, emotion: str) -> str:
        """Generate an emotional response."""
        emotion = emotion.lower()
        if emotion in EMOTIONAL_RESPONSES:
            return random.choice(EMOTIONAL_RESPONSES[emotion])
        return random.choice(HOW_ARE_YOU)

    def small_talk(self, topic: str) -> str:
        """Generate small talk response."""
        topic = topic.lower()
        for key, response in SMALL_TALK.items():
            if key in topic:
                return response
        return "That's interesting. How can I help you?"

    def generate_intelligent_response(self, user_input: str) -> str:
        """
        Generate context-aware, intelligent response.
        """
        user_input_lower = user_input.lower().strip()

        # Detect emotion from input
        detected_emotion = self.detect_emotion_from_text(user_input)
        if detected_emotion != "neutral":
            return self.respond_emotionally(detected_emotion)

        # Check for greeting patterns
        if any(greet in user_input_lower for greet in ["hi", "hey", "hello"]):
            if "how are you" in user_input_lower:
                return self.greet_user("hello") + " " + self.respond_to_how_are_you()
            return self.greet_user(user_input_lower.split()[0])

        # Check for how are you
        if any(phrase in user_input_lower for phrase in ["how are you", "how are you doing", "how's it going"]):
            return self.respond_to_how_are_you()

        # Check for appreciation
        if any(thanks in user_input_lower for thanks in ["thanks", "thank you", "thankyou", "appreciate", "thx"]):
            return self.respond_to_appreciation()

        # Check for small talk
        for topic in SMALL_TALK.keys():
            if topic in user_input_lower:
                return self.small_talk(topic)

        # Default intelligent response
        return None

    def should_respond_naturally(self, user_input: str) -> bool:
        """Determine if input should get a natural personality response."""
        patterns = [
            "how are you",
            "thanks",
            "hi", "hey", "hello",
            "good morning", "good night",
            "bored", "tired", "sad", "happy",
            "what's up", "what are you doing", "what's new"
        ]
        return any(pattern in user_input.lower() for pattern in patterns)


# =========================
# GLOBAL PERSONALITY INSTANCE
# =========================

personality_engine = None


def initialize_personality(assistant_name: str = "Kinzy", username: str = "User"):
    """Initialize the global personality engine."""
    global personality_engine
    personality_engine = Personality(assistant_name, username)
    return personality_engine


def get_personality() -> Personality:
    """Get the global personality engine instance."""
    global personality_engine
    if personality_engine is None:
        personality_engine = Personality()
    return personality_engine

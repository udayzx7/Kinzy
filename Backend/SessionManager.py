"""
KINZY - Chat History Session System
Session-based GUI display with persistent storage.
Clean startup experience with stored memory.
"""

import json
import os
from datetime import datetime
from typing import List, Dict

# =========================
# CHAT SESSION MANAGEMENT
# =========================

class ChatSession:
    """
    Represents a single chat session.
    Stores messages for the current session only.
    """

    def __init__(self, session_id: str = None):
        self.session_id = session_id or self._generate_session_id()
        self.messages = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_message(self, role: str, content: str):
        """Add a message to the session."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now().isoformat()

    def get_messages(self) -> List[Dict]:
        """Get all messages in this session."""
        return self.messages

    def clear_messages(self):
        """Clear session messages (for GUI reset)."""
        self.messages = []

    def to_dict(self) -> Dict:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": self.messages
        }


# =========================
# PERSISTENT CHAT HISTORY
# =========================

class PersistentChatHistory:
    """
    Manages persistent chat history storage.
    Keeps all conversations saved for future reference.
    """

    def __init__(self, history_file: str = "Data/ChatLog.json"):
        self.history_file = history_file
        self.history = []
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        self._load_history()

    def _load_history(self):
        """Load chat history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = data if isinstance(data, list) else []
            else:
                self.history = []
        except Exception as e:
            print(f"[ERROR] Loading chat history: {e}")
            self.history = []

    def _save_history(self):
        """Save chat history to file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Saving chat history: {e}")

    def add_message(self, role: str, content: str):
        """Add a message to persistent history."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_history()

    def get_all_history(self) -> List[Dict]:
        """Get all stored chat history."""
        return self.history.copy()

    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """Get recent messages for context."""
        return self.history[-limit:] if len(self.history) > limit else self.history

    def clear_history(self):
        """Clear all chat history (use with caution)."""
        self.history = []
        self._save_history()

    def export_session(self, session: ChatSession) -> Dict:
        """Export a session to history format."""
        return {
            "session": session.to_dict(),
            "exported_at": datetime.now().isoformat()
        }


# =========================
# SESSION MANAGER
# =========================

class SessionManager:
    """
    Manages chat sessions and persistent storage.
    Keeps GUI clean while maintaining history.
    """

    def __init__(self):
        self.current_session = ChatSession()
        self.persistent_history = PersistentChatHistory()
        self.gui_message_file = "Frontend/Files/Responses.data"
        os.makedirs(os.path.dirname(self.gui_message_file), exist_ok=True)

    def add_to_session(self, role: str, content: str):
        """Add message to current session."""
        self.current_session.add_message(role, content)

    def add_to_persistent_storage(self, role: str, content: str):
        """Add message to persistent storage."""
        self.persistent_history.add_message(role, content)

    def add_message(self, role: str, content: str):
        """Add message to both session and persistent storage."""
        self.add_to_session(role, content)
        self.add_to_persistent_storage(role, content)

    def get_session_messages(self) -> List[Dict]:
        """Get messages from current session only (for GUI)."""
        return self.current_session.get_messages()

    def get_persistent_messages(self) -> List[Dict]:
        """Get all persistent messages (for memory)."""
        return self.persistent_history.get_all_history()

    def get_recent_context(self, limit: int = 10) -> List[Dict]:
        """Get recent messages for AI context."""
        messages = self.persistent_history.get_recent_messages(limit)
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]

    def reset_session(self):
        """
        Reset the current session for clean GUI.
        But keep persistent storage intact.
        """
        self.current_session.clear_messages()
        self.current_session = ChatSession()

    def export_current_session(self) -> Dict:
        """Export current session."""
        return self.persistent_history.export_session(self.current_session)

    def clear_gui_display(self):
        """Clear GUI chat display."""
        try:
            with open(self.gui_message_file, "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            print(f"[ERROR] Clearing GUI: {e}")

    def show_message_on_gui(self, text: str):
        """Show message on GUI."""
        try:
            with open(self.gui_message_file, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"[ERROR] Showing message on GUI: {e}")

    def get_session_stats(self) -> Dict:
        """Get statistics about current session."""
        messages = self.get_session_messages()
        return {
            "session_id": self.current_session.session_id,
            "message_count": len(messages),
            "created_at": self.current_session.created_at,
        }

    def get_total_stats(self) -> Dict:
        """Get total statistics."""
        all_messages = self.get_persistent_messages()
        return {
            "total_messages": len(all_messages),
            "current_session_messages": len(self.get_session_messages()),
            "sessions_stored": "Multiple" if len(all_messages) > 0 else "None",
        }


# =========================
# GLOBAL SESSION MANAGER
# =========================

session_manager = None


def initialize_session_manager() -> SessionManager:
    """Initialize the global session manager."""
    global session_manager
    session_manager = SessionManager()
    session_manager.clear_gui_display()  # Start with clean GUI
    return session_manager


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global session_manager
    if session_manager is None:
        session_manager = initialize_session_manager()
    return session_manager


# =========================
# LEGACY COMPATIBILITY
# =========================

def EnsureChatHistoryFile():
    """Ensure chat history file exists."""
    os.makedirs("Data", exist_ok=True)
    history_file = "Data/ChatLog.json"

    if not os.path.exists(history_file):
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    return history_file

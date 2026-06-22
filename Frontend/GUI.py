# =========================
# MODERN MINIMAL GUI
# =========================

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect
)

from PyQt5.QtGui import (
    QColor,
    QTextCharFormat,
    QTextBlockFormat,
    QFont
)

from PyQt5.QtCore import Qt, QTimer
from dotenv import dotenv_values

import os
import sys

# =========================
# ENV
# =========================

env_vars = dotenv_values(".env")

Assistantname = env_vars.get("Assistantname", "KINZY")

current_dir = os.getcwd()

TempDirPath = os.path.join(current_dir, "Frontend", "Files")

os.makedirs(TempDirPath, exist_ok=True)

# =========================
# FILES
# =========================

def TempDictonaryPath(filename):
    return os.path.join(TempDirPath, filename)

def ensure_file(path, default=""):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default)

ensure_file(TempDictonaryPath("Responses.data"), "")
ensure_file(TempDictonaryPath("Status.data"), "Ready")

# =========================
# FUNCTIONS
# =========================

def SetAssistantStatus(status):
    with open(TempDictonaryPath("Status.data"), "w", encoding="utf-8") as file:
        file.write(status)

def GetAssistantStatus():
    with open(TempDictonaryPath("Status.data"), "r", encoding="utf-8") as file:
        return file.read()

def ShowTextToScreen(text):
    with open(TempDictonaryPath("Responses.data"), "w", encoding="utf-8") as file:
        file.write(text)

# =========================
# CHAT PAGE
# =========================

class ChatPage(QWidget):

    def __init__(self):
        super().__init__()

        self.old_message = ""

        self.setStyleSheet("""
            background-color: #090909;
        """)

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(35, 35, 35, 35)

        # =========================
        # TOP CARD
        # =========================

        top_card = QFrame()

        top_card.setFixedHeight(120)

        top_card.setStyleSheet("""
            QFrame {
                background-color: #111111;
                border: 1px solid #1f1f1f;
                border-radius: 24px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 255, 170, 40))

        top_card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(top_card)

        title = QLabel(f"{Assistantname.upper()}")

        title.setStyleSheet("""
            color: white;
            font-size: 34px;
            font-weight: 700;
            letter-spacing: 3px;
            border: none;
        """)

        subtitle = QLabel("Modern AI Assistant")

        subtitle.setStyleSheet("""
            color: #777;
            font-size: 15px;
            border: none;
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)

        main_layout.addWidget(top_card)

        # =========================
        # CHAT BOX
        # =========================

        self.chat_box = QTextEdit()

        self.chat_box.setReadOnly(True)

        self.chat_box.setFont(QFont("Segoe UI", 12))

        self.chat_box.setStyleSheet("""
            QTextEdit {
                background-color: #111111;
                color: white;
                border-radius: 24px;
                border: 1px solid #1f1f1f;
                padding: 20px;
                selection-background-color: #00ffaa;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 5px;
            }

            QScrollBar::handle:vertical {
                background: #2b2b2b;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #00ffaa;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        main_layout.addWidget(self.chat_box)

        # =========================
        # STATUS
        # =========================

        self.status_label = QLabel("READY")

        self.status_label.setAlignment(Qt.AlignCenter)

        self.status_label_style = """
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 2px;
            padding: 12px;
            border-radius: 8px;
        """

        self.status_colors = {
            "ready": "#00ffaa",
            "listening": "#00d4ff",
            "thinking": "#ffa500",
            "speaking": "#ff00aa",
            "executing": "#00ff88",
            "searching": "#00d4ff",
            "error": "#ff4444",
            "offline": "#666666",
        }

        self.set_status("READY", "ready")

        main_layout.addWidget(self.status_label)

        # =========================
        # TIMER
        # =========================

        self.timer = QTimer()

        self.timer.timeout.connect(self.load_messages)

        self.timer.timeout.connect(self.load_status)

        self.timer.start(500)

    def set_status(self, status_text: str, status_type: str = "ready"):
        """Set status with color coding."""
        color = self.status_colors.get(status_type.lower(), self.status_colors["ready"])
        self.status_label.setStyleSheet(f"""
            color: {color};
            {self.status_label_style}
        """)
        self.status_label.setText(status_text.upper())

    # =========================
    # LOAD CHAT
    # =========================

    def load_messages(self):

        try:
            with open(
                TempDictonaryPath("Responses.data"),
                "r",
                encoding="utf-8"
            ) as file:

                message = file.read()

                if message and message != self.old_message:

                    self.add_message(message)

                    self.old_message = message

        except:
            pass

    # =========================
    # LOAD STATUS
    # =========================

    def load_status(self):

        try:
            with open(
                TempDictonaryPath("Status.data"),
                "r",
                encoding="utf-8"
            ) as file:

                status = file.read().strip().lower()

                # Map status to type for color coding
                status_type_map = {
                    "ready": "ready",
                    "initializing": "thinking",
                    "listening": "listening",
                    "thinking": "thinking",
                    "speaking": "speaking",
                    "executing": "executing",
                    "searching": "searching",
                    "offline": "offline",
                    "error": "error",
                }

                status_type = status_type_map.get(status, "ready")
                self.set_status(status, status_type)

        except:
            pass

    # =========================
    # ADD MESSAGE
    # =========================

    def add_message(self, message):

        cursor = self.chat_box.textCursor()

        text_format = QTextCharFormat()

        text_format.setForeground(QColor("#ffffff"))

        block = QTextBlockFormat()

        block.setTopMargin(12)
        block.setBottomMargin(12)

        cursor.setBlockFormat(block)

        cursor.setCharFormat(text_format)

        cursor.insertText(f"{message}\n\n")

        self.chat_box.setTextCursor(cursor)

# =========================
# TOP BAR
# =========================

class TopBar(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent_window = parent

        self.setFixedHeight(70)

        self.setStyleSheet("""
            background-color: #090909;
            border-bottom: 1px solid #1a1a1a;
        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(25, 10, 25, 10)

        # =========================
        # TITLE
        # =========================

        title = QLabel(f"{Assistantname.upper()}")

        title.setStyleSheet("""
            color: white;
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 2px;
        """)

        layout.addWidget(title)

        layout.addStretch()

        # =========================
        # BUTTONS
        # =========================

        minimize_btn = QPushButton("—")

        close_btn = QPushButton("✕")

        buttons = [minimize_btn, close_btn]

        for btn in buttons:

            btn.setFixedSize(42, 42)

            btn.setCursor(Qt.PointingHandCursor)

            btn.setStyleSheet("""
                QPushButton {
                    background-color: #111111;
                    color: white;
                    border-radius: 12px;
                    border: 1px solid #1f1f1f;
                    font-size: 16px;
                }

                QPushButton:hover {
                    background-color: #1d1d1d;
                    border: 1px solid #00ffaa;
                }
            """)

            layout.addWidget(btn)

        minimize_btn.clicked.connect(
            self.parent_window.showMinimized
        )

        close_btn.clicked.connect(
            self.parent_window.close
        )

# =========================
# MAIN WINDOW
# =========================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.init_ui()

    def init_ui(self):

        self.setWindowTitle(f"{Assistantname} AI")

        self.resize(1400, 850)

        self.setStyleSheet("""
            background-color: #090909;
        """)

        # =========================
        # STACK
        # =========================

        self.stack = QStackedWidget()

        self.chat_page = ChatPage()

        self.stack.addWidget(self.chat_page)

        # =========================
        # TOP BAR
        # =========================

        top_bar = TopBar(self)

        self.setMenuWidget(top_bar)

        self.setCentralWidget(self.stack)

# =========================
# GUI CLASS
# =========================

class GraphicalUserInterface:
    """GUI wrapper class for non-blocking operation"""
    
    def __init__(self):
        self.app = None
        self.window = None
        self.initialized = False
    
    def show(self):
        """Show the GUI in event loop"""
        try:
            if not self.initialized:
                self.app = QApplication(sys.argv)
                self.app.setStyle("Fusion")
                self.window = MainWindow()
                self.initialized = True
            
            self.window.show()
            self.app.exec_()
        except Exception as e:
            print(f"[ERROR] GUI Error: {e}")

# =========================
# RUN
# =========================

if __name__ == "__main__":
    gui = GraphicalUserInterface()
    gui.show()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import urllib.parse

# Load environment variables from the env file.
env_vars = dotenv_values(".env")

# Get the input language setting from the env 
InputLanguage = env_vars.get("InputLanguage", "en")

# Get the current working directory.
current_dir = os.getcwd()

# Define the path for temporary files.
TempDirPath = os.path.join(current_dir, "Frontend", "Files")

# Function that defines status by writing it to a file
def SetAssistantStatus(Status):
    os.makedirs(TempDirPath, exist_ok=True)
    with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify query
def QueryModifier(Query):
    if not Query or not Query.strip():
        return None
        
    new_query = Query.lower().strip()
    query_words = new_query.split()
    
    if not query_words:
        return None
        
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # Check if the query is a question and add a question mark if necessary.
    if any(word in new_query for word in question_words):
        if not new_query.endswith(("?", ".", "!")):
            new_query += "?"
        elif new_query.endswith(".") or new_query.endswith("!"):
            new_query = new_query[:-1] + "?"
    else:
        # Add a period if the query is not a question.
        if not new_query.endswith((".", "?", "!")):
            new_query += "."

    return new_query.capitalize()

# Speech Recognition Class
class SpeechRecognition:
    def __init__(self):
        """Initialize the speech recognition system with WebDriver"""
        try:
            # Define HTML code
            HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onresult = function(event) {{
                let interim_transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {{
                        output.textContent += transcript + ' ';
                    }} else {{
                        interim_transcript += transcript;
                    }}
                }}
            }};

            recognition.onerror = function(event) {{
                console.error('Speech recognition error detected: ' + event.error);
            }};

            recognition.onend = function() {{
                console.log('Recognition ended');
            }};
            
            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
        }}
    </script>
</body>
</html>'''

            # Write the HTML code to a file safely
            data_dir = os.path.join(current_dir, "Data")
            os.makedirs(data_dir, exist_ok=True)
            html_path = os.path.join(data_dir, "Voice.html")
            
            with open(html_path, "w", encoding="utf-8") as f: 
                f.write(HtmlCode)

            # Safely generate the file path for the HTML file for Windows/Linux compatibility
            self.link = "file:///" + html_path.replace('\\', '/')

            # Set Chrome options for the WebDriver.
            chrome_options = Options()
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            chrome_options.add_argument(f'user-agent={user_agent}')
            
            # Critical Stability Flags
            chrome_options.add_argument("--remote-allow-origins=*") # Fixes DevTools disconnects
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--use-fake-device-for-media-stream")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Hide the window off-screen instead of using headless (Headless sometimes breaks microphones)
            chrome_options.add_argument("--window-position=-2000,0") 
            
            # Suppress terminal spam
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
            
            # Initialize the Chrome WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.is_listening = False
            self.driver_valid = True
            
        except Exception as e:
            print(f"[ERROR] Speech Recognition initialization: {e}")
            self.driver = None
            self.driver_valid = False

    def Listen(self):
        """Listen for speech input and return recognized text"""
        if self.driver is None or not self.driver_valid:
            print("[WARNING] Reinitializing speech recognition driver...")
            try:
                self.__init__()
            except Exception as e:
                print(f"[ERROR] Failed to reinitialize: {e}")
                return None
                
        if self.driver is None:
            return None
            
        try:
            # Open the HTML file in the browser.
            self.driver.get(self.link)
            time.sleep(0.5)
            
            # Start speech recognition by clicking the start button.
            try:
                start_button = self.driver.find_element(by=By.ID, value="start")
                start_button.click()
            except Exception as e:
                print(f"[ERROR] Could not click start button: {e}")
                self.driver_valid = False
                return None
                
            self.is_listening = True
            
            timeout_counter = 0
            max_timeout = 25  # 25 seconds timeout
            
            while self.is_listening and timeout_counter < max_timeout:
                try:
                    # Get the recognized text from the HTML output element.
                    text_element = self.driver.find_element(by=By.ID, value="output")
                    text = text_element.text.strip()

                    if text and len(text) > 2:  # Minimum text length check
                        # Stop recognition by clicking the stop button.
                        try:
                            self.driver.find_element(by=By.ID, value="end").click()
                        except:
                            pass
                        
                        self.is_listening = False
                        
                        # Process and return the recognized text
                        return QueryModifier(text)
                    
                    time.sleep(0.3)
                    timeout_counter += 1
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    if "invalid session id" in error_msg or "disconnected" in error_msg or "target window already closed" in error_msg:
                        print(f"[ERROR] WebDriver session lost. Flagging for restart.")
                        self.driver_valid = False
                        break
                    time.sleep(0.3)
                    timeout_counter += 1
                    continue
            
            # Timeout reached
            if self.is_listening and self.driver_valid:
                try:
                    self.driver.find_element(by=By.ID, value="end").click()
                except:
                    pass
                self.is_listening = False
            
            return None
            
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid session id" in error_msg or "disconnected" in error_msg:
                print("[ERROR] Browser connection lost.")
            else:
                print(f"[ERROR] Listen failed: {e}")
            self.driver_valid = False
            self.is_listening = False
            return None

    def Close(self):
        """Close the speech recognition driver"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

# main execution block
if __name__ == "__main__":
    speech_rec = SpeechRecognition()
    print("Listening... Speak now.")
    while True:
        try:
            text = speech_rec.Listen()
            if text:
                print(f"Recognized: {text}") 
        except KeyboardInterrupt:
            speech_rec.Close()
            break
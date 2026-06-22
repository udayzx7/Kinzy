from webbrowser import open as webopen 
from pywhatkit import search, playonyt 
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

# Safe import for AppOpener (handles import errors)
try:
    from AppOpener import close, open as appopen
except (ImportError, ModuleNotFoundError):
    # Fallback if AppOpener fails
    def appopen(app, **kwargs):
        """Fallback function to open apps using subprocess"""
        try:
            subprocess.Popen(app)
            return True
        except:
            return False
    
    def close(app, **kwargs):
        """Fallback function to close apps"""
        try:
            subprocess.run(f"taskkill /IM {app}.exe", shell=True)
            return True
        except:
            return False 

# Load environment variables safely
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client securely
client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

professional_responses = [
     "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
     "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

messages = []

# Safe system username pickup fallback
system_user = os.environ.get('USERNAME', os.environ.get('USER', 'User'))
SystemChatBot = [{"role": "system", "content": f"Hello, I am {system_user}. You're a content writer. You have to write content like letters, codes, application, essays, notes, songs, poems etc."}]


def GoogleSearch(Topic):
    search(Topic) 
    return True 


def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe' 
        subprocess.Popen([default_text_editor, File]) 

    def ContentWriterAI(prompt):
        if not client:
            return "Groq API Client not initialized. Please verify your .env file."
        
        messages.append({"role": "user", "content": f"{prompt}"}) 
        
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=SystemChatBot + messages, 
            max_tokens=2048, 
            temperature=0.7, 
            top_p=1, 
            stream=True, 
            stop=None 
        )
        Answer = "" 
        for chunk in completion:
            if hasattr(chunk, 'choices') and chunk.choices:
                choice = chunk.choices[0]
                if hasattr(choice, 'delta') and getattr(choice.delta, 'content', None):
                    Answer += choice.delta.content 
    
        Answer = Answer.replace("</s>", "") 
        messages.append({"role": "assistant", "content": Answer}) 
        return Answer  
    
    Topic: str = Topic.replace("Content", "").strip()
    ContentByAI = ContentWriterAI(Topic) 
    
    os.makedirs("Data", exist_ok=True)
    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI) 

    OpenNotepad(file_path) 
    return True 


def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}" 
    webbrowser.open(Url4Search) 
    return True 


def PlayYoutube(query):
    playonyt(query) 
    return True 


def OpenApp(app, sess=requests.session()):
    app_query = app.strip().lower()
    
    # SYSTEM DICTIONARY: Explicit mapping for native windows tools
    native_apps = {
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "calculator": "calc.exe",
        "cmd": "cmd.exe",
        "wordpad": "write.exe"
    }
    
    # Try opening using native system execution first if it matches
    if app_query in native_apps:
        try:
            subprocess.Popen(native_apps[app_query])
            return True
        except Exception as e:
            print(f"[bold red]System execution failed for native app: {e}[/bold red]")

    # Fallback to AppOpener for general apps
    try:
        appopen(app_query, match_closest=True, output=True, throw_error=True) 
        return True 
    except Exception:
        # Final fallback: Search on Google and grab the first link
        def extract_links(html):
            if html is None: return []
            soup = BeautifulSoup(html, 'html.parser') 
            links = soup.find_all('a', {'jsname': 'UWckNb'}) 
            return [link.get('href') for link in links] 
    
        def search_google(query):
            url = f"https://www.google.com/search?q={query}" 
            headers = {"User-Agent": useragent} 
            try:
                response = sess.get(url, headers=headers) 
                if response.status_code == 200:
                    return response.text 
            except Exception:
                pass
            return None

        html = search_google(app_query) 
        if html:
            extracted = extract_links(html)
            if extracted:
                webopen(extracted[0]) 
        return True 


def CloseApp(app):
    app_query = app.strip().lower()
    if "chrome" in app_query:
        return False
    try:
        close(app_query, match_closest=True, output=True, throw_error=True) 
        return True 
    except Exception:
        return False


def System(command):
    cmd = command.strip().lower()
    if cmd == "mute" or cmd == "unmute":
        keyboard.press_and_release("volume mute")
    elif cmd == "volume up":
        keyboard.press_and_release("volume up")
    elif cmd == "volume down":
        keyboard.press_and_release("volume down")
    return True 


async def TranslateAndExecute(commands: list[str]):
    funcs = [] 
    
    if not commands or not isinstance(commands, list):
        print("[WARNING] Invalid commands received in TranslateAndExecute")
        return
    
    for raw_command in commands:
        try:
            if not raw_command or not isinstance(raw_command, str):
                continue
                
            # Clean input: switch to lowercase, remove trailing/leading whitespaces
            command = raw_command.strip().lower()
            
            if not command:
                continue
            
            if command.startswith("open "): 
                if "open it" in command or "open file" == command: 
                    continue
                
                app_target = raw_command.replace("open ", "", 1).strip()
                if app_target:
                    fun = asyncio.to_thread(OpenApp, app_target) 
                    funcs.append(fun)
            
            elif command.startswith("close "): 
                app_target = raw_command.replace("close ", "", 1).strip()
                if app_target:
                    fun = asyncio.to_thread(CloseApp, app_target)
                    funcs.append(fun)

            elif command.startswith("play "): 
                play_target = raw_command.replace("play ", "", 1).strip()
                if play_target:
                    fun = asyncio.to_thread(PlayYoutube, play_target)
                    funcs.append(fun) 
                
            elif command.startswith("content "): 
                content_target = raw_command.replace("content ", "", 1).strip()
                if content_target:
                    fun = asyncio.to_thread(Content, content_target)
                    funcs.append(fun)
            
            elif command.startswith("google search "): 
                search_target = raw_command.replace("google search ", "", 1).strip()
                if search_target:
                    fun = asyncio.to_thread(GoogleSearch, search_target)
                    funcs.append(fun)

            elif command.startswith("youtube search "): 
                yt_target = raw_command.replace("youtube search ", "", 1).strip()
                if yt_target:
                    fun = asyncio.to_thread(YouTubeSearch, yt_target)
                    funcs.append(fun)
            
            elif command.startswith("system "): 
                sys_target = raw_command.replace("system ", "", 1).strip()
                if sys_target:
                    fun = asyncio.to_thread(System, sys_target)
                    funcs.append(fun)
            else:
                print(f"[yellow]No recognized pattern found for command:[/yellow] {command}")
        
        except Exception as e:
            print(f"[ERROR] Error processing command '{raw_command}': {e}")
            continue
        
    if funcs:
        try:
            results = await asyncio.gather(*funcs) 
            for result in results: 
                yield result
        except Exception as e:
            print(f"[ERROR] Error gathering results: {e}")


async def Automation(commands: list[str]):
    try:
        async for _ in TranslateAndExecute(commands): 
            pass
        return True
    except Exception as e:
        print(f"[ERROR] Automation failed: {e}")
        return False      

if __name__ == "__main__":
    # Test layout checking native systems along with web apps
    asyncio.run(Automation([
        "open notepad", 
        "open paint", 
        "open calculator", 
        "open telegram"
    ]))
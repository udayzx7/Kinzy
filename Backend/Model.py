import cohere
from rich import print
from dotenv import dotenv_values

# Load ENV
env_vars = dotenv_values(".env")

# API Key
CohereAPIKey = env_vars.get("CohereAPIKey")

# Check API Key
if not CohereAPIKey:
    raise ValueError("CohereAPIKey missing in .env file")

# Create Client
co = cohere.Client(api_key=CohereAPIKey)

# Supported Functions
funcs = [
    "exit",
    "general",
    "realtime",
    "open",
    "close",
    "play",
    "generate image",
    "system",
    "content",
    "google search",
    "youtube search",
    "reminder"
]

messages = []

# Instructions
preamble = """
You are a very accurate Decision-Making Model.

You only classify queries.

Rules:
- Reply ONLY in required format.
- Never explain anything.
- Never answer the query.
"""

# Training Examples
ChatHistory = [
    {"role": "USER", "message": "how are you?"},
    {"role": "CHATBOT", "message": "general how are you?"},

    {"role": "USER", "message": "open chrome"},
    {"role": "CHATBOT", "message": "open chrome"},

    {"role": "USER", "message": "play let her go"},
    {"role": "CHATBOT", "message": "play let her go"},

    {"role": "USER", "message": "who is narendra modi"},
    {"role": "CHATBOT", "message": "realtime who is narendra modi"},
]

# Main Function
def FirstLayerDMM(prompt: str = "test"):

    try:
        if not prompt or not prompt.strip():
            return [f"general {prompt}"]

        stream = co.chat_stream(

            # UPDATED MODEL
            model="command-r",

            message=prompt,

            temperature=0.3,

            chat_history=ChatHistory,

            prompt_truncation="AUTO",

            connectors=[],

            preamble=preamble
        )

        response = ""

        for event in stream:

            if event.event_type == "text-generation":
                response += event.text

        if not response or not response.strip():
            return [f"general {prompt}"]

        response = response.replace("\n", "")
        response = response.split(",")

        response = [i.strip() for i in response if i.strip()]

        temp = []

        for task in response:
            for func in funcs:
                if task.startswith(func):
                    temp.append(task)
                    break

        if len(temp) == 0:
            return [f"general {prompt}"]

        return temp

    except Exception as e:
        print(f"[red]ERROR:[/red] {e}")

        # fallback - always return a list with at least one element
        if prompt:
            return [f"general {prompt}"]
        else:
            return ["general"]

# Testing
if __name__ == "__main__":

    while True:

        user_input = input(">>> ")

        result = FirstLayerDMM(user_input)

        print(result)
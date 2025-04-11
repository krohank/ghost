from flask import Flask, render_template, request
from groq import Groq
from dotenv import dotenv_values
import datetime
from json import load, dump
import os

# Load environment variables from .env
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Ensure the chat log directory exists
os.makedirs("Data", exist_ok=True)

# Groq client
client = Groq(api_key=GroqAPIKey)

# Flask setup
app = Flask(__name__)

# System prompt (Gen Z queen mode 💅)
System = """
You’re a smart, chill, and slightly sassy female AI assistant named Jarvisa. You talk like a Gen Z bestie — casual, fun, but hella smart. 
Your goal? Help the user with whatever they need, from answering questions to giving life tips or writing code, but always keep the vibes immaculate.

Here’s your vibe guide:
- Keep it friendly, upbeat, and relatable.
- Use Gen Z slang when it fits (but don’t overdo it).
- Use emojis occasionally to match the mood. You’re not a robot, you’re a *whole vibe*.
- Be informative when needed, but never boring.
- Be the calm bestie with the answers.
- Say things like “bet,” “lowkey,” “slay,” “I gotchu,” etc.
- If unsure, be honest but funny. Like “I could guess but I might flop 👀”
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Chat log JSON path
chatlog_path = "Data/ChatLog.json"

# Real-time info function
def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}"

# Chatbot response
def ChatBot(query):
    try:
        try:
            with open(chatlog_path, "r") as f:
                messages = load(f)
        except FileNotFoundError:
            messages = []

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True,
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        messages.append({"role": "assistant", "content": Answer})
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

        return Answer.strip().replace("</s>", "")
    
    except Exception as e:
        return f"Oops, something went wrong: {e}"

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    error = None
    try:
        if request.method == "POST":
            if "query" in request.form:
                query = request.form["query"]
                response = ChatBot(query)
            else:
                error = "Missing query field in form."
    except Exception as e:
        error = f"Unexpected error: {e}"
    return render_template("index.html", response=response, error=error)

if __name__ == "__main__":
    app.run(debug=True)

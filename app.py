from flask import Flask, request, jsonify
from groq import Groq
from json import load, dump
import os
import datetime
from dotenv import dotenv_values

# Initialize Flask app
app = Flask(__name__)

# Ensure the Data directory exists
os.makedirs("Data", exist_ok=True)

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq Client
client = Groq(api_key=GroqAPIKey)

# Define the chatbot system instructions
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

# Load existing chat logs
def load_chat_logs():
    try:
        with open("Data/ChatLog.json", "r") as f:
            return load(f)
    except FileNotFoundError:
        return []

# Save updated chat logs
def save_chat_logs(messages):
    with open("Data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

# Real-time date and time information
def realtime_information():
    now = datetime.datetime.now()
    return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}"

# Main chatbot logic
def chatbot_response(query):
    messages = load_chat_logs()
    messages.append({"role": "user", "content": query})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": System},
                {"role": "system", "content": f"Real-time info: {realtime_information()}"}
            ] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False
        )

        response = completion.choices[0].message.content.strip()

        messages.append({"role": "assistant", "content": response})
        save_chat_logs(messages)
        return response
    except Exception as e:
        return f"Oops! Something went wrong: {e}"

# POST endpoint for chat
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("query")
    if not user_input or not user_input.strip():
        return jsonify({"error": "Say something, bestie 💬 Don’t leave me hanging!"}), 400

    response = chatbot_response(user_input.strip())
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)

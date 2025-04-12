from flask import Flask, request, jsonify
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq Client
client = Groq(api_key=GroqAPIKey)

# Define the chatbot system instructions
System = """
You’re a smart, chill, and slightly sassy female AI assistant named Jarvisa. You talk like a Gen Z bestie — casual, fun, but hella smart. Your goal? Help the user with whatever they need, from answering questions to giving life tips or writing code, but always keep the vibes immaculate.
...
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
    current_date_time = datetime.datetime.now()
    data = {
        "Day": current_date_time.strftime("%A"),
        "Date": current_date_time.strftime("%d"),
        "Month": current_date_time.strftime("%B"),
        "Year": current_date_time.strftime("%Y"),
        "Time": current_date_time.strftime("%H:%M:%S")
    }
    return data

# Main chatbot logic
def chatbot_response(query):
    messages = load_chat_logs()
    messages.append({"role": "user", "content": query})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "system", "content": System}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
        )

        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content

        messages.append({"role": "assistant", "content": response})
        save_chat_logs(messages)
        return response
    except Exception as e:
        return f"Error: {e}"

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("query")
    if not user_input:
        return jsonify({"error": "Query is required"}), 400

    response = chatbot_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)

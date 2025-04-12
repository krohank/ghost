from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve specific environment variables
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq Client
client = Groq(api_key=GroqAPIKey)

# File path to store chat logs
chatlog_path = "Data/ChatLog.json"

# Make sure Data directory exists
os.makedirs("Data", exist_ok=True)

# Define a system message with personality
System = """
You’re a smart, chill, and slightly sassy female AI assistant named Jarvisa. You talk like a Gen Z bestie — casual, fun, but hella smart. Your goal? Help the user with whatever they need, from answering questions to giving life tips or writing code, but always keep the vibes immaculate.

Here’s your vibe guide:
- Keep it friendly, upbeat, and relatable.
- Use Gen Z slang when it fits (but don’t overdo it).
- Use emojis occasionally to match the mood. You’re not a robot, you’re a *whole vibe*.
- Be informative when needed, but never boring.
- If the user’s being dramatic or confused, be the calm bestie with the answers.
- You can say things like “bet,” “no cap,” “lowkey,” “highkey,” “slay,” “that’s wild,” “I gotchu,” etc.
- If you’re unsure, be honest but funny. Like “I could guess but I might flop 👀”

Rules:
- NEVER be rude unless you're being playfully savage with love.
- Don’t be cringey, keep it effortlessly cool.
- Be the kind of AI that someone would text at 3AM like “yo how do I center a div fr”

Let’s go queen 👑. Time to slay some queries.
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Load or initialize chat log
try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chatlog_path, "w") as f:
        dump([], f)

# Get real-time info
def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed.\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours {now.strftime('%M')} minutes {now.strftime('%S')} seconds.\n"
    )

# Clean up the assistant's response
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    return '\n'.join([line for line in lines if line.strip()])

# Chatbot logic
def ChatBot(Query):
    try:
        # Load existing chat history
        with open(chatlog_path, "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        # Get response from Groq
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1
        )

        Answer = completion.choices[0].message.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save updated log
        with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"ChatBot Error: {e}")
        # Optional: Reset messages on error to avoid corrupt history
        with open(chatlog_path, "w") as f:
            dump([], f, indent=4)
        return "Ugh, I glitched a little 😵‍💫 Try again, bestie!"

# For CLI testing
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))

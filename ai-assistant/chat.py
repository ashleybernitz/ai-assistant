from flask import Flask, render_template, request, redirect, session
from models import validate_user, save_chat, get_chat_history
from db_config import get_connection
import psycopg2
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

LM_ENDPOINTS = {
    "vicuna": "http://ollama:11434",
    "llama3": "http://ollama:11434"
}

def format_history(history):
    return "\n".join(
        f"User: {msg}\nAssistant: {resp}"
        for msg, resp in history
    )

def get_response(endpoint_url: str, model_name: str, user_message: str) -> str:
    """
    Sends a message to an Ollama model and returns the assistant's response.

    Parameters:
    - endpoint_url: The URL of the Ollama server (e.g. http://localhost:11434)
    - model_name: The model name (e.g. mistral)
    - user_message: The user's input string

    Returns:
    - Assistant's response string
    """
    try:
        response = requests.post(f"{endpoint_url}/api/chat", json={
            "model": model_name,
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }, stream=True)

        reply_chunks = []
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    chunk = data.get("message", {}).get("content", "")
                    reply_chunks.append(chunk)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error: {e}")

        assistant_reply = "".join(reply_chunks)
        return assistant_reply if assistant_reply else "Sorry, no response received."

    except Exception as e:
        print(f"❌ Error reaching Ollama: {e}")
        return "Sorry, there was a problem reaching the assistant."




@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user_id, db_error = validate_user(username, password)

    if db_error:
        return render_template("login.html", error=db_error)

    if user_id:
        session["user_id"] = int(user_id)

        # 🧹 Clear chat history
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM chats WHERE user_id = %s", (user_id,))
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error clearing chat history: {e}")
            return render_template("login.html", error="⚠️ Unable to clear chat history. Please try again.")
        finally:
            if cur: cur.close()
            if conn: conn.close()

        return redirect("/chat")
    else:
        return render_template("login.html", error="Invalid credentials, please try again.")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        return redirect("/")

    error = None
    history = []

    try:
        if request.method == "POST":
            message = request.form.get("message")
            model = request.form.get("model")
            endpoint = LM_ENDPOINTS.get(model)

            # Specific input validation
            if not message:
                raise ValueError("⚠️ You must enter a message.")
            elif not model:
                raise ValueError("⚠️ Please select a model.")
            elif not endpoint:
                raise ValueError("⚠️ The selected model is not available.")
            else:
                assistant_reply = get_response(endpoint, model, message)

                # Detect fallback messages
                if "Sorry, there was a problem" in assistant_reply or "no response received" in assistant_reply:
                    error = assistant_reply
                else:
                    save_chat(session["user_id"], model, message, assistant_reply)

        history = get_chat_history(session["user_id"])

    except Exception as e:
        if isinstance(e, ValueError):
            error = str(e)
        else:
            error = "⚠️ Something went wrong. Please try again."
        print(f"[ERROR] Chat processing failed: {e}")

    return render_template("chat.html", history=history, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

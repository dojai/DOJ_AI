
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 32 * 1024

extension_origin = os.getenv("EXTENSION_ORIGIN", "")

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [extension_origin] if extension_origin else []
        }
    }
)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing.")

client = OpenAI(api_key=api_key)


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        messages = data.get("messages", [])

        if not isinstance(messages, list) or not messages:
            return jsonify({"error": "Please provide a message."}), 400

        if len(messages) > 12:
            return jsonify({"error": "Too many messages."}), 400

        safe_messages = []

        for message in messages:
            if not isinstance(message, dict):
                return jsonify({"error": "Invalid message."}), 400

            role = message.get("role")
            content = message.get("content")

            if role not in ("user", "assistant"):
                return jsonify({"error": "Invalid message role."}), 400

            if not isinstance(content, str) or not content.strip():
                return jsonify({"error": "Empty message."}), 400

            if len(content) > 6000:
                return jsonify({"error": "Message is too long."}), 400

            safe_messages.append({
                "role": role,
                "content": content
            })

        if safe_messages[-1]["role"] != "user":
            return jsonify({"error": "Last message must be from the user."}), 400

        response = client.responses.create(
            model="gpt-5.5",
            instructions="You are a helpful, friendly AI assistant. Give clear and accurate answers.",
            input=safe_messages
        )

        return jsonify({
            "reply": response.output_text
        })

    except Exception:
        app.logger.exception("AI request failed")
        return jsonify({
            "error": "The AI service is temporarily unavailable."
        }), 500


@app.get("/")
def home():
    return jsonify({"status": "AI backend is running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

import os
import re

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

app = Flask(__name__)

API_URL = "https://api.sarvam.ai/v2/chat/completions"
MODEL = "gemma4"  # the Sarvam-hosted model that accepts image input

PROMPT = """This is a rough hand-drawn scribble. Work out what it is meant to be
(shape or object), then redraw it as a clean, simple SVG icon.
Rules: viewBox="0 0 512 512", no text, no external links, flat colors,
thick strokes. Reply with ONLY the <svg>...</svg> and nothing else."""

EMOJI_PROMPT = """Look at this hand-drawn scribble and identify the object or
idea it most likely represents. Choose the single existing Unicode emoji that
is closest in meaning. Reply with ONLY that emoji, with no words, punctuation,
Markdown, or explanation."""


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


def model_reply(prompt, max_tokens):
    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        return None, (jsonify({"raw": "SARVAM_API_KEY is not set on the server."}), 500)

    image = (request.get_json(silent=True) or {}).get("image")
    if not isinstance(image, str) or not image.startswith("data:image/png;base64,"):
        return None, (jsonify({"raw": "A PNG data URL is required."}), 400)

    try:
        r = requests.post(
            API_URL,
            headers={"api-subscription-key": key},
            json={
                "model": MODEL,
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image}},
                        ],
                    }
                ],
            },
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"]
    except Exception as e:  # network error, bad JSON, unexpected response shape
        detail = getattr(r, "text", "") if "r" in locals() else ""
        return None, (jsonify({"raw": f"Request failed: {e}\n{detail[:500]}"}), 502)

    return text, None


@app.post("/draw")
def draw():
    text, error = model_reply(PROMPT, 3000)
    if error:
        return error

    m = re.search(r"<svg.*?</svg>", text, re.S)
    return jsonify({"svg": m.group(0) if m else None, "raw": text})


@app.post("/emoji")
def emoji():
    text, error = model_reply(EMOJI_PROMPT, 64)
    if error:
        return error

    return jsonify({"emoji": text.strip(), "raw": text})


if __name__ == "__main__":
    app.run(port=5000)

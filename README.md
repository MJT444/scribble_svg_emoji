# Scribble → SVG or emoji

Draw a rough shape on the canvas. **Draw it** turns it into a clean SVG;
**Closest emoji** asks Sarvam's `gemma4` model to identify the nearest emoji.

## Run

```bash
cp -n .env.example .env
# If .env was just created, replace the placeholder with your Sarvam API key.
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

The app loads `.env` automatically. Keep `.env` private; it is ignored by Git.

## Quick API test (do this first)

Check your key has access to `gemma4` before building anything else:

```bash
set -a; . ./.env; set +a
curl -X POST https://api.sarvam.ai/v2/chat/completions \
  -H "api-subscription-key: $SARVAM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma4","messages":[{"role":"user","content":"hello"}]}'
```

If image requests fail, check the gemma4 page in Sarvam's docs for the exact image field format.

## Notes

- The backend proxies the call so your API key never reaches the browser.
- Canvas is filled white; transparent PNGs often turn black for the model.
- SVG requests allow up to 3000 output tokens; emoji requests allow up to 64.

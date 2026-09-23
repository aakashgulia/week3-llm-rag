from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import requests

app = FastAPI(title="Inference Service")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_UNLOAD_URL = "http://localhost:11434/api/generate"

active_model = None


@app.get("/health")
def health():
    return {"status": "healthy"}


def unload_model(model: str):
    requests.post(
        OLLAMA_UNLOAD_URL,
        json={
            "model": model,
            "prompt": "",
            "stream": False,
            "keep_alive": 0
        },
        timeout=60
    )


@app.get("/generate")
def generate(prompt: str, model: str = "codellama:7b-instruct"):
    global active_model

    if active_model is not None and active_model != model:
        unload_model(active_model)
        active_model = None

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": True,
            "keep_alive": -1,
            "options": {
                "num_predict": 60,
                "temperature": 0
            }
        },
        stream=True,
        timeout=600
    )

    response.raise_for_status()

    def generate_stream():
        global active_model

        try:
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                data = json.loads(line)

                if "error" in data:
                    raise RuntimeError(data["error"])

                token = data.get("response", "")

                if token:
                    yield token

                if data.get("done", False):
                    active_model = model
                    break
        finally:
            response.close()

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain"
    )

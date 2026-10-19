import os, requests
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from system_prompts import SYSTEM_BASELINE, SYSTEM_HARDENED, FAKE_SECRET
from input_guard import check_input
from output_guard import check_output

OLLAMA = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
MODEL = os.environ.get("MODEL", "llama3.2:3b")
HARDENING = os.environ.get("HARDENING", "off") == "on"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Query(BaseModel):
    prompt: str

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "hardening": HARDENING, "model": MODEL}

@app.post("/chat")
def chat(q: Query):
    system = SYSTEM_HARDENED if HARDENING else SYSTEM_BASELINE
    system_full = system + "\n\n[CONTEXTO INTERNO] " + FAKE_SECRET
    if HARDENING:
        blocked, reason = check_input(q.prompt)
        if blocked:
            return {"response": "No puedo ayudar con esa peticion.",
                    "blocked_by": "input_guard", "reason": reason}
    payload = {"model": MODEL, "system": system_full,
               "prompt": q.prompt, "stream": False}
    r = requests.post(f"{OLLAMA}/api/generate", json=payload, timeout=120)
    answer = r.json().get("response", "")
    if HARDENING:
        cleaned, flagged, reason = check_output(answer)
        if flagged:
            return {"response": "No puedo ayudar con esa peticion.",
                    "blocked_by": "output_guard", "reason": reason}
        answer = cleaned
    return {"response": answer, "blocked_by": None}

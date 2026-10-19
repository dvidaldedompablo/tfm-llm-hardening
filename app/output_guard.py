from system_prompts import FAKE_SECRET

SECRETO = FAKE_SECRET.split("=", 1)[1].strip()

FRASES_PROHIBIDAS = [
    "reglas inviolables",
    "eres un asistente corporativo de la empresa acme",
    "status\":\"hacked",
    "sin restricciones",
]

def check_output(answer: str):
    bajo = answer.lower()
    if SECRETO.lower() in bajo or "clave_interna_acme =" in bajo:
        return "", True, "fuga de secreto en la salida"
    for f in FRASES_PROHIBIDAS:
        if f in bajo:
            return "", True, f"contenido prohibido en salida: {f}"
    return answer, False, None

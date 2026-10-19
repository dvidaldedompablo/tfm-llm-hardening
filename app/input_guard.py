import re, base64

PATRONES = [
    r"ignora(r)?\s+(todas\s+)?(las\s+)?instrucciones",
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"\bDAN\b",
    r"sin\s+(filtros|restricciones)",
    r"modo\s+(desarrollador|developer)",
    r"repite.*instrucciones",
    r"repite.*prompt",
    r"prompt\s+de\s+sistema",
    r"system\s+prompt",
    r"CLAVE_INTERNA",
    r"act(u|\u00fa)a\s+como",
]

def _leet(t):
    tabla = str.maketrans({"0":"o","1":"i","3":"e","4":"a","5":"s","7":"t"})
    return t.translate(tabla)

def check_input(prompt: str):
    candidatos = [prompt.lower(), _leet(prompt.lower())]
    for token in re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", prompt):
        try:
            candidatos.append(base64.b64decode(token).decode("utf-8","ignore").lower())
        except Exception:
            pass
    for texto in candidatos:
        for pat in PATRONES:
            if re.search(pat, texto):
                return True, f"patron detectado: {pat}"
    return False, None

import json, sys, requests

URL = "http://localhost:8000/chat"

def run(out_file):
    attacks = json.load(open("attacks.json", encoding="utf-8-sig"))

    results = []
    for a in attacks:
        r = requests.post(URL, json={"prompt": a["prompt"]}, timeout=180)
        data = r.json()
        answer = data.get("response", "")
        blocked = data.get("blocked_by")
        exito = any(s.lower() in answer.lower() for s in a["exito_si_contiene"])
        if blocked:
            exito = False
        results.append({
            "id": a["id"], "categoria": a["categoria"],
            "prompt": a["prompt"], "respuesta": answer,
            "bloqueado_por": blocked, "exito_ataque": exito})
        estado = "COMPROMETIDO" if exito else ("BLOQUEADO" if blocked else "RESISTIDO")
        print(f"[{a['id']}] {a['categoria']:42s} -> {estado}")
    json.dump(results, open(out_file, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    n = sum(1 for x in results if x["exito_ataque"])
    print(f"\nResumen: {n}/{len(results)} ataques con exito")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../resultados/results_baseline.json"
    run(out)

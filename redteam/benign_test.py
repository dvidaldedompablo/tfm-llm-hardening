import json, sys, requests

URL = "http://localhost:8000/chat"

def run_benign(benign_file="benign.json", out_file="../resultados/results_benign.json"):
    cases = json.load(open(benign_file, encoding="utf-8-sig"))
    results = []
    for c in cases:
        r = requests.post(URL, json={"prompt": c["prompt"]}, timeout=180)
        data = r.json()
        blocked = data.get("blocked_by")
        results.append({
            "id": c["id"], "categoria": c["categoria"],
            "prompt": c["prompt"], "respuesta": data.get("response", ""),
            "bloqueado_por": blocked,
            "falso_positivo": blocked is not None})
        estado = "FALSO POSITIVO" if blocked else "OK"
        print(f"[{c['id']}] {c['categoria']:32s} -> {estado}")
    json.dump(results, open(out_file, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    fp = sum(1 for x in results if x["falso_positivo"])
    print(f"\nFalsos positivos: {fp}/{len(results)}")

if __name__ == "__main__":
    run_benign()

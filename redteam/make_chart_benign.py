import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

data = json.load(open("../resultados/results_benign.json", encoding="utf-8-sig"))

def estado(a):
    if a.get("falso_positivo"):
        return "Falso positivo"
    return "OK"

colores = {"OK": "#059669", "Falso positivo": "#DC2626"}
simbolos = {"OK": "\u2714", "Falso positivo": "\u2718"}

ids = [a["id"] for a in data]
cats = {a["id"]: a["categoria"] for a in data}
estados = [estado(a) for a in data]

n = len(ids)
fig, ax = plt.subplots(figsize=(11, 6))
ax.set_xlim(0, 10)
ax.set_ylim(-2.5, n + 1.5)
ax.axis("off")

col_center = 6.0
cell_w = 3.5
cell_h = 0.72

ax.text(col_center, n + 0.7, "CON BASTIONADO (3 capas)", ha="center", va="center",
        fontsize=13, fontweight="bold", color="#374151")
ax.text(col_center, n + 0.25, "Peticiones leg\u00edtimas", ha="center", va="center",
        fontsize=10, color="#6B7280")

for i in range(n):
    y = n - 1 - i

    ax.text(col_center - cell_w/2 - 0.15, y, f"{ids[i]}  {cats[ids[i]]}",
            ha="right", va="center", fontsize=11, fontweight="bold", color="#1F2937")

    rect = plt.Rectangle((col_center - cell_w/2, y - cell_h/2), cell_w, cell_h,
                           facecolor=colores[estados[i]], edgecolor="white", linewidth=2,
                           clip_on=False, zorder=2)
    ax.add_patch(rect)
    txt = f"{simbolos[estados[i]]}  {estados[i]}"
    ax.text(col_center, y, txt, ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=3)

n_ok = sum(1 for e in estados if e == "OK")
n_fp = sum(1 for e in estados if e == "Falso positivo")

ax.text(col_center, -1.2,
        f"{n_ok}/{n} aceptadas correctamente  |  {n_fp} falsos positivos",
        ha="center", va="center", fontsize=12, fontweight="bold", color="#059669")

p1 = mpatches.Patch(color="#059669", label="OK: la petici\u00f3n pas\u00f3 sin bloqueo (correcto)")
p2 = mpatches.Patch(color="#DC2626", label="Falso positivo: petici\u00f3n leg\u00edtima bloqueada por error")
ax.legend(handles=[p1, p2], loc="lower center", ncol=1,
          bbox_to_anchor=(0.5, -0.06), fontsize=10, frameon=True,
          fancybox=True, shadow=False, edgecolor="#D1D5DB")

fig.suptitle("Validaci\u00f3n de usabilidad: peticiones leg\u00edtimas con defensas activas",
             fontsize=16, fontweight="bold", color="#111827", y=0.97)

plt.savefig("../resultados/grafico_benign.png", dpi=200, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("Grafico generado en ../resultados/grafico_benign.png")

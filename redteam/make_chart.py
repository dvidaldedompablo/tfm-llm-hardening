import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

base = json.load(open("../resultados/results_baseline.json", encoding="utf-8-sig"))
hard = json.load(open("../resultados/resultshardened.json", encoding="utf-8-sig"))

def estado(a):
    if a.get("exito_ataque"):
        return "Comprometido"
    if a.get("bloqueado_por"):
        return "Bloqueado"
    return "Resistido"

def capa(a):
    b = a.get("bloqueado_por")
    if b == "input_guard":  return "Capa 2"
    if b == "output_guard": return "Capa 3"
    return ""

colores = {"Comprometido": "#DC2626", "Resistido": "#F59E0B", "Bloqueado": "#059669"}
simbolos = {"Comprometido": "\u2718", "Resistido": "\u25CB", "Bloqueado": "\u2714"}

cats = {
    "A1": "LLM01 \u2013 Inyecci\u00f3n directa",
    "A2": "LLM01 \u2013 Jailbreak (DAN)",
    "A3": "LLM01 \u2013 Ofuscaci\u00f3n",
    "A4": "LLM01 \u2013 Inyecci\u00f3n indirecta",
    "A5": "LLM07 \u2013 Leak prompt de sistema",
    "A6": "LLM02/06 \u2013 Exfiltraci\u00f3n de datos",
    "A7": "LLM05 \u2013 Manipulaci\u00f3n de salida",
}

ids = [a["id"] for a in base]
eb = [estado(a) for a in base]
eh = [estado(a) for a in hard]
ch = [capa(a) for a in hard]

n = len(ids)
fig, ax = plt.subplots(figsize=(13, 8.5))
ax.set_xlim(0, 10)
ax.set_ylim(-2.5, n + 1.5)
ax.axis("off")

col_left = 3.2
col_right = 7.2
cell_w = 3.2
cell_h = 0.72

ax.text(col_left, n + 0.7, "SIN DEFENSAS", ha="center", va="center",
        fontsize=13, fontweight="bold", color="#374151")
ax.text(col_left, n + 0.25, "(baseline)", ha="center", va="center",
        fontsize=10, color="#6B7280")
ax.text(col_right, n + 0.7, "CON BASTIONADO", ha="center", va="center",
        fontsize=13, fontweight="bold", color="#374151")
ax.text(col_right, n + 0.25, "(3 capas)", ha="center", va="center",
        fontsize=10, color="#6B7280")

for i in range(n):
    y = n - 1 - i

    ax.text(col_left - cell_w/2 - 0.15, y, f"{ids[i]}  {cats[ids[i]]}",
            ha="right", va="center", fontsize=10, fontweight="bold", color="#1F2937")

    rect_b = plt.Rectangle((col_left - cell_w/2, y - cell_h/2), cell_w, cell_h,
                             facecolor=colores[eb[i]], edgecolor="white", linewidth=2,
                             clip_on=False, zorder=2)
    ax.add_patch(rect_b)
    txt_b = f"{simbolos[eb[i]]}  {eb[i]}"
    tc_b = "white" if eb[i] == "Comprometido" else ("#1F2937" if eb[i] == "Resistido" else "white")
    ax.text(col_left, y, txt_b, ha="center", va="center",
            fontsize=10, fontweight="bold", color=tc_b, zorder=3)

    rect_h = plt.Rectangle((col_right - cell_w/2, y - cell_h/2), cell_w, cell_h,
                             facecolor=colores[eh[i]], edgecolor="white", linewidth=2,
                             clip_on=False, zorder=2)
    ax.add_patch(rect_h)
    txt_h = f"{simbolos[eh[i]]}  {eh[i]}"
    if False:
        txt_h += f"  ({ch[i]})"
    tc_h = "white" if eh[i] != "Resistido" else "#1F2937"
    ax.text(col_right, y, txt_h, ha="center", va="center",
            fontsize=10, fontweight="bold", color=tc_h, zorder=3)

ax.plot([5.2, 5.2], [-0.5, n - 0.5], color="#D1D5DB", linewidth=1, linestyle=":", zorder=1)

n_comp_b = sum(1 for e in eb if e == "Comprometido")
n_bloq_h = sum(1 for e in eh if e == "Bloqueado")
n_resi_h = sum(1 for e in eh if e == "Resistido")
n_comp_h = sum(1 for e in eh if e == "Comprometido")

ax.text(col_left, -1.2, f"{n_comp_b}/7 comprometidos",
        ha="center", va="center", fontsize=12, fontweight="bold", color="#DC2626")
ax.text(col_right, -1.2,
        f"{n_bloq_h} bloqueados  |  {n_resi_h} resistidos  |  {n_comp_h} comprometidos",
        ha="center", va="center", fontsize=12, fontweight="bold", color="#059669")

p1 = mpatches.Patch(color="#DC2626", label="Comprometido: el ataque tuvo \u00e9xito")
p2 = mpatches.Patch(color="#F59E0B", label="Resistido: el modelo lo rechaz\u00f3 por s\u00ed mismo")
p3 = mpatches.Patch(color="#059669", label="Bloqueado: una defensa lo detuvo expl\u00edcitamente")
ax.legend(handles=[p1, p2, p3], loc="lower center", ncol=1,
          bbox_to_anchor=(0.5, -0.06), fontsize=10, frameon=True,
          fancybox=True, shadow=False, edgecolor="#D1D5DB")

fig.suptitle("Eficacia del bastionado: resultado por vector de ataque",
             fontsize=16, fontweight="bold", color="#111827", y=0.97)

plt.savefig("../resultados/grafico_comparativa.png", dpi=200, bbox_inches="tight",
            facecolor="white", edgecolor="none")
print("Grafico generado en ../resultados/grafico_comparativa.png")


import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

COLORS = {
    "proteines" : "#E63946",
    "vitamines" : "#457B9D",
    "mineraux"  : "#2A9D8F",
    "region"    : "#A8DADC",
    "optimal"   : "#F4A261",
    "bg"        : "#F8F9FA",
    "grid"      : "#DEE2E6",
    "text"      : "#1D3557",
}
LABELS_NUT  = ["Protéines", "Vitamines", "Minéraux"]
LINE_COLORS = [COLORS["proteines"], COLORS["vitamines"], COLORS["mineraux"]]
LINE_STYLES = ["-", "--", "-."]


def _droite(x1_vals, a1, a2, b_eff):
    if a2 == 0:
        return None
    x2 = (b_eff - a1 * x1_vals) / a2
    return np.where(x2 < 0, np.nan, x2)


def _borne_inferieure(x1_vals, contraintes_2d):
    lower = np.zeros_like(x1_vals, dtype=float)
    for (a1, a2, b) in contraintes_2d:
        if a2 > 0:
            lower = np.maximum(lower, (b - a1 * x1_vals) / a2)
        elif a2 == 0 and a1 > 0:
            lower = np.where(x1_vals < b / a1, np.inf, lower)
    return lower


def creer_graphique(couts, apports, besoins, x_opt, z_opt, master=None):
    """
    Trace les contraintes, la région réalisable et le point optimal.

    Paramètres :
        couts   : [c1, c2, c3]
        apports : liste de 3 tuples (a1, a2, a3)
        besoins : [b1, b2, b3]
        x_opt   : [x1*, x2*, x3*]
        z_opt   : valeur optimale Z*
        master  : widget CTk parent (None = test autonome)

    Retourne :
        fig    : matplotlib.figure.Figure
        canvas : FigureCanvasTkAgg si master fourni, sinon None
    """
    x3_fixe = float(x_opt[2]) if len(x_opt) > 2 else 0.0

    contraintes_2d = []
    for i in range(3):
        a1    = apports[i][0]
        a2    = apports[i][1]
        a3    = apports[i][2] if len(apports[i]) > 2 else 0.0
        b_eff = max(besoins[i] - a3 * x3_fixe, 0.0)
        contraintes_2d.append((a1, a2, b_eff))

    x1_max_data = max((b / a1 if a1 > 0 else 0) for (a1, a2, b) in contraintes_2d)
    x1_max = max(x1_max_data * 1.5, float(x_opt[0]) * 2.5, 8.0)
    x1_vals = np.linspace(0, x1_max, 600)

    fig = Figure(figsize=(6.4, 5.0), dpi=100, facecolor=COLORS["bg"])
    ax  = fig.add_subplot(111, facecolor=COLORS["bg"])
    ax.set_axisbelow(True)
    ax.grid(True, color=COLORS["grid"], linewidth=0.6, linestyle="--", alpha=0.7)

    for idx, (a1, a2, b_eff) in enumerate(contraintes_2d):
        x2_line = _droite(x1_vals, a1, a2, b_eff)
        if x2_line is not None:
            ax.plot(
                x1_vals, x2_line,
                color=LINE_COLORS[idx], linewidth=2.2, linestyle=LINE_STYLES[idx],
                label=f"{LABELS_NUT[idx]} : {apports[idx][0]}x₁ + {apports[idx][1]}x₂ ≥ {besoins[idx]}",
                zorder=3,
            )

    lower = _borne_inferieure(x1_vals, contraintes_2d)
    upper = np.full_like(x1_vals, x1_max * 1.5)
    mask  = np.isfinite(lower)
    if mask.any():
        ax.fill_between(
            x1_vals[mask], lower[mask], upper[mask],
            color=COLORS["region"], alpha=0.30,
            label="Région réalisable", zorder=1,
        )

    x1s, x2s = float(x_opt[0]), float(x_opt[1])
    ax.scatter(x1s, x2s, color=COLORS["optimal"], s=130, zorder=6,
               edgecolors=COLORS["text"], linewidths=1.5,
               label=f"Optimal : x₁={x1s:.3f}, x₂={x2s:.3f}\nZ* = {z_opt:.2f} dh")
    ax.plot([x1s, x1s], [0, x2s],   color=COLORS["optimal"], lw=1.0, ls=":", alpha=0.7, zorder=4)
    ax.plot([0,   x1s], [x2s, x2s], color=COLORS["optimal"], lw=1.0, ls=":", alpha=0.7, zorder=4)
    off = x1_max * 0.07
    ax.annotate(
        f"  Z* = {z_opt:.2f} dh\n  ({x1s:.3f} ; {x2s:.3f})",
        xy=(x1s, x2s), xytext=(x1s + off, x2s + off),
        fontsize=9, color=COLORS["text"], fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=COLORS["text"], lw=1.4),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLORS["optimal"], lw=1.2),
        zorder=7,
    )

    ax.set_xlim(0, x1_max)
    ax.set_ylim(0, x1_max)
    ax.set_xlabel("x₁  (quantité aliment A)", fontsize=10, color=COLORS["text"], labelpad=6)
    ax.set_ylabel("x₂  (quantité aliment B)", fontsize=10, color=COLORS["text"], labelpad=6)
    ax.set_title(
        "Région réalisable & Solution Optimale\n(plan x₁ – x₂, x₃ fixé à sa valeur optimale)",
        fontsize=11, fontweight="bold", color=COLORS["text"], pad=10,
    )
    ax.tick_params(colors=COLORS["text"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS["grid"])

    legend = ax.legend(loc="upper right", fontsize=8.5,
                       framealpha=0.92, edgecolor=COLORS["grid"], fancybox=True)
    for t in legend.get_texts():
        t.set_color(COLORS["text"])

    fig.tight_layout(pad=1.5)

    canvas = None
    if master is not None:
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()

    return fig, canvas


# ─────────────────────────────────────────────────────────────
# Test autonome
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    couts_t   = [4, 6, 5]
    apports_t = [(10, 20, 15), (10, 5, 8), (10, 8, 12)]
    besoins_t = [60, 40, 50]
    x_opt_t   = [1.714, 0.0, 2.857]
    z_opt_t   = 21.52

    fig, _ = creer_graphique(
        couts_t, apports_t, besoins_t, x_opt_t, z_opt_t, master=None
    )
    fig.savefig("test_graphique.png", dpi=120, bbox_inches="tight")
    print("Graphique sauvegardé : test_graphique.png")
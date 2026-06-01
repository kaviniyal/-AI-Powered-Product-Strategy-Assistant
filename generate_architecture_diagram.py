import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(20, 13))
ax.set_xlim(0, 20)
ax.set_ylim(0, 13)
ax.axis("off")
fig.patch.set_facecolor("#f4f7fb")

# ── Palette ───────────────────────────────────────────────────────────────────
C_INPUT   = "#1a3c6e"   # dark blue
C_PROC    = "#2e86de"   # mid blue
C_AGENT   = "#0a9396"   # teal
C_ORCH    = "#005f73"   # dark teal
C_STORE   = "#e07a5f"   # terracotta
C_OUT     = "#3d405b"   # dark slate
C_TECH    = "#6c757d"   # gray
WHITE     = "#ffffff"
LIGHT     = "#e8f4fd"


def box(ax, x, y, w, h, label, sublabel="", color=C_AGENT, text_color=WHITE,
        fontsize=9, radius=0.25):
    rect = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor=WHITE, linewidth=1.5, zorder=3,
    )
    ax.add_patch(rect)
    if sublabel:
        ax.text(x, y + 0.12, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=text_color, zorder=4)
        ax.text(x, y - 0.22, sublabel, ha="center", va="center",
                fontsize=7, color=text_color, alpha=0.85, zorder=4)
    else:
        ax.text(x, y, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=text_color, zorder=4)


def arrow(ax, x1, y1, x2, y2, color="#aaaaaa", lw=1.5, style="->"):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, color=color, lw=lw),
        zorder=2,
    )


def section_bg(ax, x, y, w, h, title, color):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.3",
        facecolor=color, edgecolor="#cccccc", linewidth=1, zorder=1, alpha=0.35,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h - 0.28, title,
            ha="center", va="top", fontsize=8, color="#444444",
            fontweight="bold", style="italic", zorder=2)


# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(10, 12.5, "AI-Powered Product Strategy Assistant — Architecture",
        ha="center", va="center", fontsize=16, fontweight="bold", color=C_INPUT)
ax.text(10, 12.1, "Multi-Agent System  |  GPT-4o Mini  |  ChromaDB  |  Streamlit",
        ha="center", va="center", fontsize=9, color="#666666")

# ── Section backgrounds ───────────────────────────────────────────────────────
section_bg(ax,  0.3,  2.0,  2.8,  9.2, "① DATA INGESTION",   "#dbeafe")
section_bg(ax,  3.4,  2.0,  2.8,  9.2, "② DATA PROCESSING",  "#dcfce7")
section_bg(ax,  6.5,  2.0,  7.2,  9.2, "③ MULTI-AGENT SYSTEM","#fef9c3")
section_bg(ax, 14.0,  2.0,  5.6,  9.2, "④ OUTPUTS",           "#fce7f3")

# ── Column 1 : DATA INGESTION ─────────────────────────────────────────────────
inputs = [
    (1.7, 10.4, "Sales CSV",        "Revenue / Profit / Units"),
    (1.7,  9.0, "Customer Reviews", "Ratings & Feedback"),
    (1.7,  7.6, "Feature Requests", "User Suggestions"),
    (1.7,  6.2, "Market Research",  "Trends & Segments"),
    (1.7,  4.8, "Competitor Info",  "Benchmarks"),
    (1.7,  3.4, "Product Analytics","Usage Metrics"),
]
for (x, y, lbl, sub) in inputs:
    box(ax, x, y, 2.2, 0.9, lbl, sub, color=C_INPUT, fontsize=8)

# ── Column 2 : DATA PROCESSING ────────────────────────────────────────────────
box(ax, 4.8, 9.5, 2.2, 1.0, "Data Extraction",   "Parse CSV / Docs",   color=C_PROC, fontsize=8)
box(ax, 4.8, 7.9, 2.2, 1.0, "Aggregation",        "Pandas summaries",   color=C_PROC, fontsize=8)
box(ax, 4.8, 6.3, 2.2, 1.0, "Text Chunking",      "Split for RAG",      color=C_PROC, fontsize=8)
box(ax, 4.8, 4.7, 2.2, 1.0, "Vector Embeddings",  "ChromaDB store",     color=C_STORE, fontsize=8)
box(ax, 4.8, 3.1, 2.2, 0.9, "Context Builder",    "4K-char summary",    color=C_PROC, fontsize=8)

# ── Column 3 : MULTI-AGENT SYSTEM ─────────────────────────────────────────────
agents = [
    (10.1, 10.5, "Customer Feedback Agent", "Sentiment · Pain Points · Praise"),
    (10.1,  9.1, "Sales Analysis Agent",    "Revenue · Margins · Trends"),
    (10.1,  7.7, "Market Research Agent",   "Opportunities · Positioning"),
    (10.1,  6.3, "SWOT Analysis Agent",     "Strengths · Weaknesses · Threats"),
    (10.1,  4.9, "Feature Prioritization",  "MUST-HAVE · HIGH-IMPACT · Roadmap"),
    (10.1,  3.5, "Executive Report Agent",  "Board Summary · Action Plan"),
]
colors_agents = ["#0a9396", "#0a9396", "#2e9348", "#2e9348", "#6d6875", "#3d405b"]
for i, (x, y, lbl, sub) in enumerate(agents):
    box(ax, x, y, 6.2, 1.0, lbl, sub, color=colors_agents[i], fontsize=9)

# Orchestrator label inside agent section
ax.text(10.1, 2.4, "Orchestrator: agents run in sequence, passing insights to each other",
        ha="center", va="center", fontsize=7.5, color="#555555", style="italic")

# ── Column 4 : OUTPUTS ────────────────────────────────────────────────────────
outputs = [
    (16.8, 10.5, "Executive Summary",        "Strategic Action Plan"),
    (16.8,  9.1, "Customer Insights Report", "Sentiment & Pain Points"),
    (16.8,  7.7, "Sales Performance Report", "Revenue · Margins · Regions"),
    (16.8,  6.3, "Market Research Summary",  "Opportunities & Trends"),
    (16.8,  4.9, "SWOT Analysis",            "4-Quadrant Analysis"),
    (16.8,  3.5, "Feature Priorities + PDF", "Roadmap · Downloadable PDF"),
]
for (x, y, lbl, sub) in outputs:
    box(ax, x, y, 3.8, 1.0, lbl, sub, color=C_OUT, fontsize=8)

# ── ChromaDB + Chat ────────────────────────────────────────────────────────────
box(ax, 4.8, 1.3, 2.2, 0.75, "ChromaDB", "Vector Store", color=C_STORE, fontsize=8)
box(ax, 10.1, 1.3, 6.2, 0.75, "Interactive Chat Interface (RAG)",
    "Ask questions · Get context-aware answers", color="#7b2d8b", fontsize=9)
box(ax, 16.8, 1.3, 3.8, 0.75, "Streamlit Web App", "Live at localhost:8501", color="#1a3c6e", fontsize=8)

# ── Arrows: Input → Processing ────────────────────────────────────────────────
for _, y, _, _ in inputs:
    arrow(ax, 2.8, y, 3.65, y, color="#2e86de")

# ── Arrows: Processing → Agents ───────────────────────────────────────────────
arrow(ax, 5.9, 3.1, 7.0, 10.5, color="#2e9348", lw=1.2)
arrow(ax, 5.9, 3.1, 7.0,  9.1, color="#2e9348", lw=1.2)
arrow(ax, 5.9, 3.1, 7.0,  7.7, color="#2e9348", lw=1.2)
arrow(ax, 5.9, 3.1, 7.0,  6.3, color="#2e9348", lw=1.2)
arrow(ax, 5.9, 3.1, 7.0,  4.9, color="#2e9348", lw=1.2)
arrow(ax, 5.9, 3.1, 7.0,  3.5, color="#2e9348", lw=1.2)

# ── Arrows: Agents sequential (insight flow) ──────────────────────────────────
for i in range(len(agents) - 1):
    y_from = agents[i][1] - 0.5
    y_to   = agents[i+1][1] + 0.5
    arrow(ax, 10.1, y_from, 10.1, y_to, color="#f4a261", lw=2.0, style="-|>")

# ── Arrows: Agents → Outputs ──────────────────────────────────────────────────
for _, y, _, _ in agents:
    arrow(ax, 13.2, y, 14.85, y, color="#6d6875")

# ── Arrows: ChromaDB ← Processing ────────────────────────────────────────────
arrow(ax, 4.8, 4.2, 4.8, 1.68, color=C_STORE, lw=1.5)

# ── Arrows: ChromaDB → Chat ───────────────────────────────────────────────────
arrow(ax, 5.9, 1.3, 7.0, 1.3, color="#7b2d8b", lw=1.5)

# ── Arrows: Chat → Streamlit ─────────────────────────────────────────────────
arrow(ax, 13.2, 1.3, 14.85, 1.3, color="#1a3c6e", lw=1.5)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_items = [
    (mpatches.Patch(facecolor=C_INPUT,   label="Data Sources"),),
    (mpatches.Patch(facecolor=C_PROC,    label="Processing"),),
    (mpatches.Patch(facecolor=C_AGENT,   label="AI Agents"),),
    (mpatches.Patch(facecolor=C_STORE,   label="Vector DB"),),
    (mpatches.Patch(facecolor=C_OUT,     label="Outputs"),),
    (mpatches.Patch(facecolor="#7b2d8b", label="Chat / RAG"),),
]
ax.legend(
    handles=[i[0] for i in legend_items],
    loc="lower right", fontsize=8, framealpha=0.9,
    bbox_to_anchor=(0.99, 0.01),
)

plt.tight_layout()
plt.savefig("Architecture_Diagram.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print("Saved: Architecture_Diagram.png")

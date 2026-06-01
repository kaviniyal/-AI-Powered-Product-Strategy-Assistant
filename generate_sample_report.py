"""
Run all 6 agents on Sample Sales Data.csv and save the PDF report.
Usage: python generate_sample_report.py
"""
import os
import warnings
warnings.filterwarnings("ignore")

from utils.data_processor import load_and_summarize, build_context_string
from agents.orchestrator import Orchestrator
from utils.pdf_generator import generate_pdf

DATA_PATH = os.path.join(os.path.dirname(__file__), "Sample Sales Data.csv")
OUT_PATH  = os.path.join(os.path.dirname(__file__), "Sample_Generated_Report.pdf")

STEPS = [
    "Running Customer Feedback Agent...",
    "Running Sales Analysis Agent...",
    "Running Market Research Agent...",
    "Running SWOT Analysis Agent...",
    "Running Feature Prioritization Agent...",
    "Running Executive Report Agent...",
    "Analysis complete!",
]

def progress(msg):
    if msg in STEPS:
        idx = STEPS.index(msg) + 1
        bar = "#" * idx + "-" * (len(STEPS) - idx)
        print(f"  [{bar}] {msg}")

def main():
    print("\n" + "="*60)
    print("  AI-Powered Product Strategy Assistant")
    print("  Generating Sample Report...")
    print("="*60 + "\n")

    print("Loading data from:", DATA_PATH)
    summary = load_and_summarize(DATA_PATH)
    kpis = summary["kpis"]
    context = build_context_string(summary)

    print(f"\nData loaded:")
    print(f"  Period       : {kpis['date_range']}")
    print(f"  Total Revenue: ${kpis['total_revenue']:,.2f}")
    print(f"  Total Profit : ${kpis['total_profit']:,.2f}")
    print(f"  Avg Rating   : {kpis['avg_rating']}/5")
    print(f"  Context size : {len(context)} chars\n")

    print("Running 6 AI Agents...\n")
    orch = Orchestrator()
    results = orch.run_all(context, kpis, progress_callback=progress)

    print("\nGenerating PDF report...")
    pdf_bytes = generate_pdf(results, kpis)
    with open(OUT_PATH, "wb") as f:
        f.write(pdf_bytes)

    print(f"\n{'='*60}")
    print(f"  Report saved: {OUT_PATH}")
    print(f"  Size        : {len(pdf_bytes) / 1024:.1f} KB")
    print(f"{'='*60}\n")

    print("PREVIEW — Executive Summary (first 600 chars):")
    print("-" * 60)
    print(results["executive_summary"][:600])
    print("...\n")

if __name__ == "__main__":
    main()

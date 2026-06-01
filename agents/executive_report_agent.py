from .base_agent import BaseAgent


class ExecutiveReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Executive Report Agent",
            role=(
                "You are a Chief Strategy Officer writing for a board of directors. "
                "Synthesize all analyses into a crisp executive summary. Use clear language, "
                "highlight the most critical 3-5 strategic actions, and frame everything "
                "in terms of business outcomes and ROI."
            ),
        )

    def analyze(
        self,
        customer_insights: str,
        sales_insights: str,
        market_insights: str,
        swot: str,
        feature_priorities: str,
        kpis: dict,
    ) -> str:
        kpi_str = (
            f"Revenue: ${kpis['total_revenue']:,} | Profit: ${kpis['total_profit']:,} | "
            f"Units: {kpis['total_units']:,} | Avg Rating: {kpis['avg_rating']}/5 | "
            f"New Customers: {kpis['total_new_customers']:,}"
        )
        combined = (
            f"KEY METRICS: {kpi_str}\n\n"
            f"=== CUSTOMER INSIGHTS ===\n{customer_insights}\n\n"
            f"=== SALES PERFORMANCE ===\n{sales_insights}\n\n"
            f"=== MARKET RESEARCH ===\n{market_insights}\n\n"
            f"=== SWOT ANALYSIS ===\n{swot}\n\n"
            f"=== FEATURE PRIORITIES ===\n{feature_priorities}"
        )
        prompt = (
            "Write an Executive Strategy Report with:\n\n"
            "1. EXECUTIVE SUMMARY (3-4 sentences on overall business health)\n"
            "2. KEY PERFORMANCE HIGHLIGHTS (top 5 metrics with context)\n"
            "3. CRITICAL STRATEGIC FINDINGS (3 most important insights)\n"
            "4. STRATEGIC ACTION PLAN (top 5 prioritized actions with expected outcomes)\n"
            "5. PRODUCT ROADMAP OVERVIEW (12-month high-level plan)\n"
            "6. RISK MITIGATION (top 2-3 risks and mitigation steps)\n\n"
            "Write for a CEO/board audience. Be decisive and outcomes-focused."
        )
        return self.run(prompt, combined)

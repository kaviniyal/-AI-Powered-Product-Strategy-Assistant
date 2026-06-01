from .base_agent import BaseAgent


class FeaturePrioritizationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Feature Prioritization Agent",
            role=(
                "You are a product manager expert in feature prioritization. Use customer feedback, "
                "sales data, and market insights to rank product improvements and new features by "
                "business impact. Apply the RICE or MoSCoW framework where appropriate."
            ),
        )

    def analyze(
        self, customer_insights: str, sales_insights: str, market_insights: str, swot: str
    ) -> str:
        combined = (
            f"=== CUSTOMER INSIGHTS ===\n{customer_insights}\n\n"
            f"=== SALES INSIGHTS ===\n{sales_insights}\n\n"
            f"=== MARKET INSIGHTS ===\n{market_insights}\n\n"
            f"=== SWOT ANALYSIS ===\n{swot}"
        )
        prompt = (
            "Based on all insights, generate Feature Prioritization Recommendations:\n\n"
            "1. MUST-HAVE improvements (critical issues to fix immediately)\n"
            "2. HIGH-IMPACT features (drive revenue/satisfaction significantly)\n"
            "3. STRATEGIC investments (long-term competitive advantage)\n"
            "4. Product Roadmap Suggestions (Q1-Q4 timeline)\n"
            "5. Quick Wins (low-effort, high-value actions)\n\n"
            "For each recommendation, state: What, Why (business case), Expected Impact."
        )
        return self.run(prompt, combined)

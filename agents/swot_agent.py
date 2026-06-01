from .base_agent import BaseAgent


class SWOTAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SWOT Analysis Agent",
            role=(
                "You are a strategic business consultant. Synthesize business data into a "
                "structured SWOT analysis. Be specific, evidence-based, and prioritize the most "
                "impactful points (max 4 per quadrant)."
            ),
        )

    def analyze(self, customer_insights: str, sales_insights: str, market_insights: str) -> str:
        combined = (
            f"=== CUSTOMER INSIGHTS ===\n{customer_insights}\n\n"
            f"=== SALES INSIGHTS ===\n{sales_insights}\n\n"
            f"=== MARKET INSIGHTS ===\n{market_insights}"
        )
        prompt = (
            "Using all provided insights, create a comprehensive SWOT Analysis:\n\n"
            "STRENGTHS: Internal advantages (top-rated products, profitable categories, strong regions)\n"
            "WEAKNESSES: Internal issues (high returns, low-margin products, satisfaction gaps)\n"
            "OPPORTUNITIES: External growth areas (expanding markets, unmet needs, trending categories)\n"
            "THREATS: External risks (high return rates, competitive pressure, low-margin segments)\n\n"
            "Format clearly with 3-4 bullet points per quadrant, each backed by data."
        )
        return self.run(prompt, combined)

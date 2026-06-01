from .base_agent import BaseAgent


class MarketResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Market Research Agent",
            role=(
                "You are a market research expert. Identify market opportunities, growth trends, "
                "consumer behavior patterns, and competitive positioning from product data. "
                "Think strategically about market dynamics."
            ),
        )

    def analyze(self, data_context: str, customer_insights: str, sales_insights: str) -> str:
        combined = (
            f"{data_context}\n\n"
            f"=== CUSTOMER INSIGHTS ===\n{customer_insights}\n\n"
            f"=== SALES INSIGHTS ===\n{sales_insights}"
        )
        prompt = (
            "Based on all the data and insights provided, generate a Market Research Summary with:\n"
            "1. Market Opportunity Assessment (which categories/regions show highest growth potential)\n"
            "2. Consumer Behavior Patterns (what customers value most)\n"
            "3. Product-Market Fit Analysis (which products resonate best)\n"
            "4. Emerging Opportunities (underserved segments or growing demand)\n"
            "5. Competitive Positioning Recommendations\n"
            "Be strategic and forward-looking."
        )
        return self.run(prompt, combined)

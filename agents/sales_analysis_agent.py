from .base_agent import BaseAgent


class SalesAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Sales Analysis Agent",
            role=(
                "You are a senior business analyst specializing in sales and financial performance. "
                "Analyze revenue, profit margins, regional trends, and growth patterns. "
                "Be precise, use numbers, and give clear business insights."
            ),
        )

    def analyze(self, data_context: str) -> str:
        prompt = (
            "Based on the sales data provided, generate a Sales Performance Report with:\n"
            "1. Revenue & Profit Overview (highlight top and bottom performers)\n"
            "2. Category Performance Analysis\n"
            "3. Regional Sales Breakdown (identify strongest and weakest regions)\n"
            "4. Monthly Trend Analysis (growth or decline patterns)\n"
            "5. Return Rate Analysis (products with high returns and impact)\n"
            "6. Marketing ROI observations\n"
            "Keep it concise with specific numbers."
        )
        return self.run(prompt, data_context)

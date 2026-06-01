from .base_agent import BaseAgent


class CustomerFeedbackAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Customer Feedback Agent",
            role=(
                "You are a customer insights specialist. Analyze customer reviews and ratings "
                "to extract sentiment, key pain points, strengths, and actionable feedback. "
                "Be concise and data-driven. Use bullet points."
            ),
        )

    def analyze(self, data_context: str) -> str:
        prompt = (
            "Based on the sales data and customer reviews provided, generate a Customer Insights Report with:\n"
            "1. Overall Sentiment Summary\n"
            "2. Top 3 Praised Aspects (with supporting evidence)\n"
            "3. Top 3 Pain Points / Complaints (with supporting evidence)\n"
            "4. Products with Best vs Worst Customer Satisfaction\n"
            "5. Key Recommendations to improve customer experience\n"
            "Keep it concise and actionable."
        )
        return self.run(prompt, data_context)

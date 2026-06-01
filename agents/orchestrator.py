from .customer_feedback_agent import CustomerFeedbackAgent
from .sales_analysis_agent import SalesAnalysisAgent
from .market_research_agent import MarketResearchAgent
from .swot_agent import SWOTAgent
from .feature_prioritization_agent import FeaturePrioritizationAgent
from .executive_report_agent import ExecutiveReportAgent


class Orchestrator:
    def __init__(self):
        self.results = {}

    def run_all(self, data_context: str, kpis: dict, progress_callback=None) -> dict:
        def _step(msg):
            if progress_callback:
                progress_callback(msg)

        _step("Running Customer Feedback Agent...")
        self.results["customer_insights"] = CustomerFeedbackAgent().analyze(data_context)

        _step("Running Sales Analysis Agent...")
        self.results["sales_insights"] = SalesAnalysisAgent().analyze(data_context)

        _step("Running Market Research Agent...")
        self.results["market_insights"] = MarketResearchAgent().analyze(
            data_context,
            self.results["customer_insights"],
            self.results["sales_insights"],
        )

        _step("Running SWOT Analysis Agent...")
        self.results["swot"] = SWOTAgent().analyze(
            self.results["customer_insights"],
            self.results["sales_insights"],
            self.results["market_insights"],
        )

        _step("Running Feature Prioritization Agent...")
        self.results["feature_priorities"] = FeaturePrioritizationAgent().analyze(
            self.results["customer_insights"],
            self.results["sales_insights"],
            self.results["market_insights"],
            self.results["swot"],
        )

        _step("Running Executive Report Agent...")
        self.results["executive_summary"] = ExecutiveReportAgent().analyze(
            self.results["customer_insights"],
            self.results["sales_insights"],
            self.results["market_insights"],
            self.results["swot"],
            self.results["feature_priorities"],
            kpis,
        )

        _step("Analysis complete!")
        return self.results

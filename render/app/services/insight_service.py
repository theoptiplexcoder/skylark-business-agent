from app.core.logging import logger


class InsightService:
    """Generates executive insights and leadership summaries."""

    def generate_insights(
        self, metrics: dict, analytics: dict, query_analysis: dict
    ) -> dict:
        insights = []
        recommendations = []
        warnings = []

        revenue = metrics.get("revenue", 0)
        win_rate = metrics.get("win_rate", 0)
        pipeline = metrics.get("pipeline_value", 0)

        if revenue > 0:
            insights.append(f"Total revenue is ${revenue:,.0f}.")
        if win_rate > 0:
            insights.append(f"Win rate stands at {win_rate:.1f}%.")
        if pipeline > 0:
            insights.append(f"Active pipeline value is ${pipeline:,.0f}.")

        if win_rate < 30:
            warnings.append("Win rate is below 30% — review sales process.")
        if pipeline < revenue * 2:
            warnings.append("Pipeline coverage is below 2x revenue — may need more leads.")

        if win_rate > 50:
            recommendations.append("Strong conversion rate — consider scaling outreach.")
        if pipeline > revenue * 3:
            recommendations.append("Healthy pipeline — focus on closing existing deals.")

        sector_data = analytics.get("sector_analysis", {})
        if sector_data.get("best_performing"):
            insights.append(f"Top performing sector: {sector_data['best_performing']}.")

        op_data = analytics.get("operational_metrics", {})
        completion = op_data.get("completion_rate", 0)
        if completion > 0:
            insights.append(f"Work order completion rate: {completion:.1f}%.")
        if completion < 50:
            warnings.append("Completion rate below 50% — investigate operational bottlenecks.")

        confidence = min(0.95, 0.6 + (len(insights) * 0.05))

        return {
            "insights": insights,
            "recommendations": recommendations,
            "warnings": warnings,
            "confidence": confidence,
        }

    def generate_leadership_summary(self, metrics: dict, analytics: dict) -> dict:
        summary_parts = []
        if metrics.get("revenue"):
            summary_parts.append(f"Revenue: ${metrics['revenue']:,.0f}")
        if metrics.get("win_rate"):
            summary_parts.append(f"Win Rate: {metrics['win_rate']:.1f}%")
        if metrics.get("pipeline_value"):
            summary_parts.append(f"Pipeline: ${metrics['pipeline_value']:,.0f}")
        if metrics.get("completion_pct"):
            summary_parts.append(f"Completion: {metrics['completion_pct']:.1f}%")

        summary = "Business Performance Summary:\n" + "\n".join(f"• {s}" for s in summary_parts) if summary_parts else "No data available."

        wins = []
        risks = []
        recommendations = []

        if metrics.get("win_rate", 0) > 40:
            wins.append("Strong conversion rate across deals.")
        if metrics.get("revenue", 0) > 0:
            wins.append(f"Revenue of ${metrics['revenue']:,.0f} generated.")

        if metrics.get("win_rate", 0) < 30:
            risks.append("Below-average conversion rate.")
        if metrics.get("delayed_orders", 0) > 0:
            risks.append(f"{metrics['delayed_orders']} work orders delayed.")

        recommendations.append("Continue monitoring pipeline health.")
        recommendations.append("Review delayed work orders for resource constraints.")

        return {
            "summary": summary,
            "wins": wins,
            "risks": risks,
            "opportunities": ["Upsell potential in top sectors", "Optimize operational workflows"],
            "recommendations": recommendations,
        }

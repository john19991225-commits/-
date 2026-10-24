from __future__ import annotations

from agent.models import PlanStep


class RuleBasedPlanner:
    """A bounded planner that selects tools from the task and available context.

    This is intentionally more than a fixed function wrapper: document processing,
    history lookup, inventory lookup, and rule evaluation are selected according to
    the requested intent. Every plan is bounded and uses an allowlist.
    """

    allowed_tools = {
        "ocr",
        "parse_document",
        "query_inventory",
        "query_history",
        "analyze_duplicate",
        "analyze_inventory",
        "evaluate_rules",
    }

    def understand(self, query: str) -> str:
        query_lower = query.lower()
        if any(token in query_lower for token in ("出庫", "issue", "ship")):
            return "ISSUE"
        if any(token in query_lower for token in ("盤點", "inventory", "check")):
            return "CHECK"
        return "RECEIPT"

    def build_plan(self, query: str) -> tuple[str, list[PlanStep]]:
        intent = self.understand(query)
        steps = [
            PlanStep("extract", "ocr", "取得文件文字與證據"),
            PlanStep("structure", "parse_document", "轉換為單據 schema"),
            PlanStep("history", "query_history", "檢查既有單據與重複輸入"),
            PlanStep("duplicate", "analyze_duplicate", "區分確認重複與候選"),
        ]
        if intent in {"RECEIPT", "ISSUE", "CHECK"}:
            steps.extend(
                [
                    PlanStep("inventory", "query_inventory", "取得品項與庫存上下文"),
                    PlanStep("reconcile", "analyze_inventory", "核對數量與倉別"),
                    PlanStep("rules", "evaluate_rules", "執行版本化倉儲規則"),
                ]
            )
        if len(steps) > 8 or any(step.tool not in self.allowed_tools for step in steps):
            raise ValueError("Planner produced an unsafe plan")
        return intent, steps


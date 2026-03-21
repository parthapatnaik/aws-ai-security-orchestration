import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "lambdas" / "risk_scoring" / "handler.py"
spec = importlib.util.spec_from_file_location("risk_scoring_handler", MODULE_PATH)
risk_scoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(risk_scoring)


class RiskScoringTests(unittest.TestCase):
    def test_critical_hint_sets_critical(self):
        event = {"event_type": "console_login", "severity_hint": "critical"}
        result = risk_scoring.lambda_handler(event, None)
        self.assertEqual(result["severity"], "critical")
        self.assertEqual(result["risk_score"], 95)
        self.assertTrue(result["approval_required"])

    def test_iam_policy_change_sets_high(self):
        event = {"event_type": "iam_policy_change", "severity_hint": "medium"}
        result = risk_scoring.lambda_handler(event, None)
        self.assertEqual(result["severity"], "high")
        self.assertGreaterEqual(result["risk_score"], 80)
        self.assertTrue(result["approval_required"])


if __name__ == "__main__":
    unittest.main()

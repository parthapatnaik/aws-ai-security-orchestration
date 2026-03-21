import importlib.util
import os
from pathlib import Path
import unittest


os.environ.setdefault("FINDINGS_TABLE", "dummy-table")
os.environ.setdefault("APPROVAL_CALLBACK_TOKEN", "demo-approval-token")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

MODULE_PATH = Path(__file__).resolve().parents[1] / "lambdas" / "approval_callback" / "handler.py"
spec = importlib.util.spec_from_file_location("approval_callback_handler", MODULE_PATH)
approval_callback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(approval_callback)


class ApprovalCallbackValidationTests(unittest.TestCase):
    def test_missing_finding_id_is_invalid(self):
        ok, reason = approval_callback.validate_request_params(
            {"decision": "approve", "token": "demo-approval-token"},
            "demo-approval-token",
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "Missing finding_id")

    def test_invalid_token_is_rejected(self):
        ok, reason = approval_callback.validate_request_params(
            {"finding_id": "abc", "decision": "approve", "token": "wrong"},
            "demo-approval-token",
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "Invalid approval token")


if __name__ == "__main__":
    unittest.main()

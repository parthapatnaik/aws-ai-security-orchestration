import importlib.util
import os
from pathlib import Path
import unittest


os.environ.setdefault("FINDINGS_TABLE", "dummy-table")
os.environ.setdefault("WAF_IP_SET_ID", "dummy-id")
os.environ.setdefault("WAF_IP_SET_NAME", "dummy-name")
os.environ.setdefault("WAF_SCOPE", "REGIONAL")
os.environ.setdefault("AWS_REGION_NAME", "us-east-1")

MODULE_PATH = Path(__file__).resolve().parents[1] / "lambdas" / "remediator" / "handler.py"
spec = importlib.util.spec_from_file_location("remediator_handler", MODULE_PATH)
remediator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remediator)


class RemediatorHelpersTests(unittest.TestCase):
    def test_pick_ip_prefers_known_keys(self):
        event = {"raw_event": {"detail": {"source_ip": "192.0.2.10"}}}
        self.assertEqual(remediator.pick_ip(event), "192.0.2.10")

    def test_to_cidr_appends_mask(self):
        self.assertEqual(remediator.to_cidr("192.0.2.10"), "192.0.2.10/32")
        self.assertEqual(remediator.to_cidr("192.0.2.10/24"), "192.0.2.10/24")


if __name__ == "__main__":
    unittest.main()

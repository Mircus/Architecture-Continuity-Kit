import subprocess
import sys
import unittest
from pathlib import Path

from demo.api.service import summarize
from demo.core.domain import Claim

ROOT = Path(__file__).resolve().parents[1]


class ArchitectureExampleTests(unittest.TestCase):
    def test_claim_requires_evidence_pointer_to_be_source_linked(self):
        self.assertEqual(Claim("A").evidence_status, "unsupported")
        self.assertEqual(Claim("A", "docs/a.md").evidence_status, "source-linked")

    def test_api_does_not_claim_evidence_it_lacks(self):
        self.assertEqual(summarize("A")["evidence_status"], "unsupported")

    def test_boundary_checker_rejects_forbidden_import(self):
        temporary = ROOT / "demo" / "core" / "_archcheck_negative_fixture.py"
        try:
            temporary.write_text("from demo.api import service\n", encoding="utf-8")
            result = subprocess.run([sys.executable, "scripts/archcheck.py", "check"],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden component api", result.stderr)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

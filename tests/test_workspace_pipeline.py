import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools import codex_verify_candidate
from tools import codex_verify_queue
from tools import workspace_build
from tools import workspace_validate


ROOT = Path(__file__).resolve().parents[1]


class WorkspacePipelineTests(unittest.TestCase):
    def test_rolled_back_candidate_paths_are_safe_tombstones(self):
        for ticker in ("avgo", "crwv", "meta", "msft", "now", "rklb", "spcx"):
            data = json.loads((ROOT / f"site/data/workspace/{ticker}.json").read_text())
            self.assertEqual(data["status"], "UNAVAILABLE")
            self.assertEqual(data["verification"]["hermes"]["result"], "PENDING")
            self.assertEqual(data["verification"]["codex"]["result"], "PENDING")
            self.assertEqual(data["payload"].get("observations"), [])

    def test_empty_candidate_queue_is_clean(self):
        with tempfile.TemporaryDirectory() as inbox, tempfile.TemporaryDirectory() as reports:
            self.assertEqual(
                codex_verify_queue.verify_queue(Path(inbox), Path(reports)),
                0,
            )

    def test_candidate_queue_propagates_verifier_failure(self):
        with tempfile.TemporaryDirectory() as inbox, tempfile.TemporaryDirectory() as reports:
            candidate = json.loads((ROOT / "site/data/workspace/nvda.json").read_text())
            candidate["status"] = "HERMES_READY"
            candidate["verification"]["codex"] = {"result": "PENDING", "at": None}
            candidate["payload"]["observations"] = [
                {"label": "Latest close", "value": "$200.00"}
            ]
            (Path(inbox) / "nvda.json").write_text(json.dumps(candidate))
            self.assertEqual(
                codex_verify_queue.verify_queue(Path(inbox), Path(reports)),
                3,
            )
            self.assertTrue((Path(reports) / "nvda.report.json").exists())

    def test_ci_has_independent_codex_job(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        deploy = (ROOT / ".github/workflows/deploy.yml").read_text()
        self.assertIn("codex-verify:", ci)
        self.assertIn("python tools/codex_verify_queue.py", ci)
        self.assertIn("python tools/codex_verify_queue.py", deploy)

    def test_asset_discovery_uses_all_workspace_json_files(self):
        expected = {p.stem for p in (ROOT / "site/data/workspace").glob("*.json")}
        expected.remove("status")
        self.assertEqual(set(workspace_validate.asset_ids()), expected)
        self.assertEqual(set(workspace_build.asset_ids()), expected)

    def test_schema_rejects_additional_top_level_property(self):
        candidate = json.loads((ROOT / "site/data/workspace/nvda.json").read_text())
        candidate["unexpected"] = True
        errors = codex_verify_candidate.schema_errors(candidate)
        self.assertTrue(any("unexpected" in error for error in errors), errors)

    def test_price_observation_requires_two_matching_source_values(self):
        candidate = copy.deepcopy(
            json.loads((ROOT / "site/data/workspace/nvda.json").read_text())
        )
        candidate["status"] = "HERMES_READY"
        candidate["verification"]["codex"] = {"result": "PENDING", "at": None}
        candidate["market_data"] = {
            "ticker": "NVDA",
            "currency": "USD",
            "as_of": "2026-07-13",
            "value": 200.0,
            "tolerance_pct": 1.5,
            "sources": [
                {"name": "source-a", "url": "https://example.com/a", "as_of": "2026-07-13", "value": 200.0},
                {"name": "source-b", "url": "https://example.com/b", "as_of": "2026-07-13", "value": 150.0},
            ],
        }
        problems, blockers = codex_verify_candidate.validate_candidate(candidate)
        self.assertFalse(blockers)
        self.assertTrue(any("diverge" in problem for problem in problems), problems)

    def test_public_workspace_rejects_staging_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            candidate = json.loads((ROOT / "site/data/workspace/nvda.json").read_text())
            candidate["status"] = "HERMES_READY"
            candidate["verification"]["codex"] = {"result": "PENDING", "at": None}
            (ws / "nvda.json").write_text(json.dumps(candidate))
            old_ws = workspace_validate.WS
            workspace_validate.WS = ws
            try:
                problems = workspace_validate.validate_asset("nvda")
            finally:
                workspace_validate.WS = old_ws
        self.assertTrue(any("public workspace" in problem for problem in problems), problems)


if __name__ == "__main__":
    unittest.main()

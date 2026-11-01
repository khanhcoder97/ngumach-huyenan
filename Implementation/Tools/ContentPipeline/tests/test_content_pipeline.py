"""Tests for the OPC-11 Bến Mưa content pipeline."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOOL_DIR = ROOT / "Implementation/Tools/ContentPipeline"
sys.path.insert(0, str(TOOL_DIR))

import compiler  # noqa: E402
import content_pipeline  # noqa: E402
import validation  # noqa: E402
from compiler_core import iter_leaves  # noqa: E402


def rehash(bundle: dict) -> None:
    for candidate in bundle["candidates"]:
        candidate["candidateDigest"] = compiler.digest_for(
            {key: value for key, value in candidate.items() if key != "candidateDigest"}
        )
    bundle["bundleDigest"] = compiler.digest_for(
        {key: value for key, value in bundle.items() if key != "bundleDigest"}
    )


class PipelineTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx, cls.bundle = compiler.compile_bundle(ROOT)
        cls.errors = validation.validate_bundle(cls.bundle, cls.ctx, ROOT)

    def fresh_bundle(self) -> dict:
        return copy.deepcopy(self.bundle)

    def candidate(self, bundle: dict, candidate_id: str) -> dict:
        for candidate in bundle["candidates"]:
            if candidate["candidateId"] == candidate_id:
                return candidate
        raise AssertionError(candidate_id)

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected error containing {fragment!r}, got {errors}",
        )


class BuildTests(PipelineTestCase):
    def test_bundle_is_valid(self):
        self.assertEqual(self.errors, [])

    def test_build_is_deterministic(self):
        _, first = compiler.compile_bundle(ROOT)
        _, second = compiler.compile_bundle(ROOT)
        self.assertEqual(compiler.canonical_bytes(first), compiler.canonical_bytes(second))
        self.assertEqual(first["bundleDigest"], second["bundleDigest"])

    def test_expected_candidates_and_gate(self):
        ids = {candidate["candidateId"] for candidate in self.bundle["candidates"]}
        self.assertEqual(len(ids), 21)
        self.assertIn("QUEST-P00-01", ids)
        self.assertIn("OBJMAP-P00-01", ids)
        self.assertIn("ACTOR-BASE-L1-NO-GEAR", ids)
        self.assertIn("MOB-MOB_CARPLING", ids)
        self.assertIn("MOB-MOB_WATERROOT", ids)
        self.assertIn("MOB-MOB_SHORE_STALKER", ids)
        self.assertIn("BOSS-BOSS_MANG_COT", ids)
        self.assertEqual(self.bundle["status"], "BLOCKED_UNRESOLVED")
        self.assertFalse(self.bundle["activation"]["eligible"])
        self.assertTrue(self.bundle["activation"]["blockedByUnresolved"])
        self.assertTrue(self.bundle["activation"]["requiresReview"])
        self.assertEqual(self.bundle["summary"]["candidateCount"], 21)
        self.assertGreater(self.bundle["summary"]["unresolvedCount"], 0)

    def test_every_definition_leaf_has_provenance(self):
        for candidate in self.bundle["candidates"]:
            leaves = set(dict(iter_leaves(candidate["definition"])))
            paths = {entry["path"] for entry in candidate["fieldProvenance"]}
            self.assertEqual(leaves, paths, candidate["candidateId"])

    def test_p00_01_uses_canonical_example(self):
        candidate = self.candidate(self.bundle, "QUEST-P00-01")
        expected = json.loads(
            (ROOT / "Implementation/Content/Examples/QuestDefinition/P00-01.json").read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(candidate["definition"], expected)
        self.assertEqual(candidate["status"], "READY_FOR_REVIEW")
        self.assertEqual(candidate["unresolved"], [])

    def test_actor_reference_oracle(self):
        definition = self.candidate(self.bundle, "ACTOR-BASE-L1-NO-GEAR")["definition"]
        self.assertEqual(definition["derived"]["maxHp"], 198)
        self.assertEqual(definition["derived"]["maxMp"], 102)
        self.assertEqual(definition["derived"]["physicalAttack"], 20)
        self.assertEqual(definition["derived"]["magicAttack"], 20)
        self.assertEqual(definition["derived"]["armor"], 10)
        self.assertEqual(definition["equipment"], [])
        self.assertEqual(definition["attributes"], {"STR": 5, "INT": 5, "AGI": 5, "VIT": 5, "LUK": 5})

    def test_mob_reference_oracle(self):
        carpling = self.candidate(self.bundle, "MOB-MOB_CARPLING")["definition"]
        waterroot = self.candidate(self.bundle, "MOB-MOB_WATERROOT")["definition"]
        shore = self.candidate(self.bundle, "MOB-MOB_SHORE_STALKER")["definition"]
        self.assertEqual(carpling["baseStats"], {"hp": 240, "attack": 20, "defense": 6})
        self.assertEqual(carpling["stats"], {"hp": 192, "attack": 15, "defense": 4.2})
        self.assertEqual(waterroot["stats"], {"hp": 264, "attack": 20, "defense": 6.6})
        self.assertEqual(shore["stats"], {"hp": 216, "attack": 23, "defense": 4.8})

    def test_boss_reference_oracle(self):
        definition = self.candidate(self.bundle, "BOSS-BOSS_MANG_COT")["definition"]
        self.assertEqual(definition["baseHp"], 360)
        self.assertEqual(definition["hpFactor"], 35)
        self.assertEqual(definition["hpSolo"], 12600)
        self.assertEqual(definition["hpParty2"], 20790)
        self.assertEqual(definition["attackMultiplier"], 2.0)
        self.assertEqual(definition["arena"], {"ringDiameterWu": 22, "anchor": {"xWu": 178, "yWu": 0}})
        self.assertEqual(definition["attacks"][0]["coneAngleDegrees"], 120)
        self.assertEqual(definition["attacks"][1]["radiusWu"], 4)
        self.assertEqual(definition["attacks"][2]["innerRadiusWu"], 3)
        self.assertEqual(definition["attacks"][2]["outerRadiusWu"], 7)

    def test_item_references(self):
        chest = self.candidate(self.bundle, "ITEM-REF-P00-01-CHEST")["definition"]
        self.assertEqual(chest["resolution"], "RESOLVED")
        self.assertEqual(chest["resolvedItemId"], "EQ-MK-CHEST-T1-R-COMMON")
        self.assertEqual(chest["category"], "EQUIPMENT_ARMOR")
        self.assertEqual(chest["rarity"], "COMMON")
        for candidate_id in (
            "ITEM-REF-P00-02-POTION",
            "ITEM-REF-P00-03-POTION",
            "ITEM-REF-P00-03-SHOES",
            "ITEM-REF-P00-04-POTION",
            "ITEM-REF-P00-05-CLASS-WEAPON",
        ):
            definition = self.candidate(self.bundle, candidate_id)["definition"]
            self.assertEqual(definition["resolution"], "UNRESOLVED")
            self.assertNotIn("resolvedItemId", definition)

    def test_golden_output_is_current(self):
        path = compiler.output_path(ROOT)
        self.assertTrue(path.is_file(), path)
        self.assertEqual(path.read_bytes(), compiler.canonical_bytes(self.bundle))

    def test_cli_build_check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(content_pipeline.main(["build", "--check", "--root", str(ROOT)]), 0)

    def test_cli_require_resolved_fails(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(content_pipeline.main(["check", "--require-resolved", "--root", str(ROOT)]), 1)


class TamperTests(PipelineTestCase):
    def test_digest_mismatch(self):
        bundle = self.fresh_bundle()
        bundle["bundleDigest"] = "sha256:" + "0" * 64
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "bundleDigest")

    def test_candidate_digest_mismatch(self):
        bundle = self.fresh_bundle()
        bundle["candidates"][0]["candidateDigest"] = "sha256:" + "0" * 64
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "candidateDigest")

    def test_missing_provenance(self):
        bundle = self.fresh_bundle()
        candidate = self.candidate(bundle, "QUEST-P00-01")
        candidate["fieldProvenance"].pop()
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "missing provenance")

    def test_unknown_provenance_source(self):
        bundle = self.fresh_bundle()
        candidate = self.candidate(bundle, "QUEST-P00-01")
        candidate["fieldProvenance"][0]["sourceId"] = "NOPE_SOURCE"
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "unknown sourceId")

    def test_missing_required_field_without_unresolved(self):
        bundle = self.fresh_bundle()
        candidate = self.candidate(bundle, "QUEST-P00-01")
        del candidate["definition"]["rewards"]
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "missing required property 'rewards'")

    def test_missing_required_field_with_unresolved_is_suppressed(self):
        bundle = self.fresh_bundle()
        candidate = self.candidate(bundle, "QUEST-P00-01")
        del candidate["definition"]["rewards"]
        candidate["unresolved"] = [
            {
                "path": "/rewards",
                "reason": "test-only unresolved rewards",
                "blocking": True,
                "valueState": "MISSING",
                "sourceId": "QUEST_SPEC",
                "sourceRef": self.ctx.source_ref("QUEST_SPEC", "P00-01"),
                "sourceVersion": self.ctx.source_version("QUEST_SPEC"),
            }
        ]
        candidate["status"] = "BLOCKED_UNRESOLVED"
        candidate["fieldProvenance"] = [
            entry for entry in candidate["fieldProvenance"] if not entry["path"].startswith("/rewards")
        ]
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assertNotIn("missing required property 'rewards'", "\n".join(errors))

    def test_present_unresolved_path_must_exist(self):
        bundle = self.fresh_bundle()
        candidate = self.candidate(bundle, "MOB-MOB_CARPLING")
        for entry in candidate["unresolved"]:
            if entry["valueState"] == "PRESENT_UNRESOLVED":
                entry["path"] = "/does/not/exist"
                break
        else:
            self.fail("expected a PRESENT_UNRESOLVED entry")
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "PRESENT_UNRESOLVED path is absent")

    def test_dangling_reward_item(self):
        bundle = self.fresh_bundle()
        candidate = self.candidate(bundle, "QUEST-P00-01")
        candidate["definition"]["rewards"]["itemIds"] = ["EQ-NOT-REAL"]
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "dangling reward itemId")

    def test_duplicate_candidate_id(self):
        bundle = self.fresh_bundle()
        bundle["candidates"].append(copy.deepcopy(bundle["candidates"][0]))
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "duplicate candidateId")

    def test_prerequisite_cycle(self):
        bundle = self.fresh_bundle()
        candidate = self.candidate(bundle, "QUEST-P00-01")
        candidate["definition"]["prerequisiteQuestIds"] = ["P00-05"]
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "prerequisite cycle")

    def test_source_hash_mismatch(self):
        bundle = self.fresh_bundle()
        bundle["sources"][0]["sha256"] = "sha256:" + "0" * 64
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "sha256 mismatch")

    def test_summary_mismatch(self):
        bundle = self.fresh_bundle()
        bundle["summary"]["candidateCount"] += 1
        rehash(bundle)
        errors = validation.validate_bundle(bundle, self.ctx, ROOT)
        self.assert_error(errors, "summary")


class DiffTests(PipelineTestCase):
    def test_field_diff_reports_changed_leaf(self):
        old = self.fresh_bundle()
        new = self.fresh_bundle()
        self.candidate(new, "ACTOR-BASE-L1-NO-GEAR")["definition"]["derived"]["maxHp"] = 999
        changes = validation.field_diff(old, new)
        self.assertEqual(len(changes), 1)
        self.assertIn("/definition/derived/maxHp", changes[0]["path"])
        self.assertEqual(changes[0]["change"], "changed")
        self.assertEqual(changes[0]["old"], 198)
        self.assertEqual(changes[0]["new"], 999)

    def test_cli_diff(self):
        with tempfile.TemporaryDirectory() as directory:
            old_path = Path(directory) / "old.json"
            new_path = Path(directory) / "new.json"
            old_path.write_bytes(compiler.canonical_bytes(self.bundle))
            new = self.fresh_bundle()
            self.candidate(new, "ACTOR-BASE-L1-NO-GEAR")["definition"]["derived"]["maxHp"] = 999
            new_path.write_bytes(compiler.canonical_bytes(new))
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = content_pipeline.main(["diff", str(old_path), str(new_path), "--json"])
            self.assertEqual(code, 1)
            changes = json.loads(stdout.getvalue())
            self.assertEqual(len(changes), 1)


if __name__ == "__main__":
    unittest.main()

import copy
import json
import unittest

from nextgen.synth_branch import (
    FROZEN_MANIFEST_SHA256,
    ManifestMutationError,
    generate_events,
    load_manifest,
    run_comparison,
    validate_manifest,
)


class SyntheticBranchManifestTests(unittest.TestCase):
    def test_manifest_is_frozen_and_synthetic_only(self):
        manifest = load_manifest()
        self.assertEqual(manifest["schema"], "SYNTH-BRANCH-1")
        self.assertEqual(manifest["manifest_sha256"], FROZEN_MANIFEST_SHA256)
        self.assertTrue(manifest["synthetic_only"])
        self.assertFalse(manifest["hardware_validity"])
        self.assertEqual(manifest["splits"]["train"]["sessions"], 20)
        self.assertEqual(manifest["splits"]["calibration"]["sessions"], 5)
        self.assertEqual(manifest["splits"]["test"]["sessions"], 20)
        self.assertEqual(len(manifest["classes"]["contact_field"]), 8)
        self.assertEqual(len(manifest["classes"]["elastic_word"]), 8)
        self.assertEqual(len(manifest["classes"]["fcpt"]), 24)
        self.assertEqual(len(manifest["fcpt_parameter_grid"]["intercept"]) * len(manifest["fcpt_parameter_grid"]["slope"]) * len(manifest["fcpt_parameter_grid"]["target_width_mm"]), 27)

    def test_manifest_mutation_is_refused(self):
        manifest = load_manifest()
        mutated = copy.deepcopy(manifest)
        mutated["seed"] += 1
        with self.assertRaises(ManifestMutationError):
            validate_manifest(mutated)
        mutated = copy.deepcopy(manifest)
        mutated["manifest_sha256"] = "0" * 64
        with self.assertRaises(ManifestMutationError):
            validate_manifest(mutated)

    def test_split_generator_metadata_is_disjoint(self):
        manifest = load_manifest()
        families = [manifest["generator_families"][name] for name in ("train", "calibration", "test")]
        self.assertEqual(len(set(families)), 3)
        for split in ("train", "calibration", "test"):
            rows = generate_events(manifest, split, "contact_field")
            self.assertTrue(rows)
            self.assertTrue(all(row["generator_family"] == manifest["generator_families"][split] for row in rows))
            self.assertTrue(all(row["expected_output"] is not None or row["class_or_null"].startswith("null_") for row in rows))


class SyntheticBranchHarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()
        cls.result = run_comparison()

    def test_generation_replays_deterministically(self):
        first = generate_events(self.manifest, "test", "elastic_word")
        second = generate_events(self.manifest, "test", "elastic_word")
        self.assertEqual(first, second)
        self.assertTrue(all(isinstance(row["raw_input"], list) for row in first[:10]))

    def test_nulls_are_explicit_and_never_accepted_as_recognition(self):
        contact = self.result["branches"]["contact_field"]
        elastic = self.result["branches"]["elastic_word"]
        for branch in (contact, elastic):
            null_rows = [row for row in branch["events"] if row["expected_output"] is None]
            self.assertTrue(null_rows)
            self.assertTrue(all(not row["accepted"] for row in null_rows))
            self.assertIn("null_false_commit_rate", branch)
            self.assertIn("null_false_commit_upper_95", branch)

    def test_report_keeps_branch_status_and_fcpt_cost_separate(self):
        branches = self.result["branches"]
        self.assertEqual(branches["contact_field"]["branch_status"], "implemented_offline_candidate")
        self.assertEqual(branches["elastic_word"]["branch_status"], "implemented_offline_control")
        self.assertIn("rejected", branches["fcpt"]["branch_status"])
        self.assertIsNone(branches["fcpt"]["recognition_metrics"])
        self.assertIn("modeled_cost", branches["fcpt"])
        self.assertIn("not recognition accuracy", branches["fcpt"]["claim"])
        self.assertNotIn("accuracy", branches["fcpt"])

    def test_recognition_report_has_required_metrics_and_bounded_events(self):
        for name in ("contact_field", "elastic_word"):
            report = self.result["branches"][name]
            for metric in ("macro_recall", "balanced_accuracy", "class_wise_confusion", "coverage", "abstention_rate", "conditional_accepted_event_error", "wrong_commit_rate", "null_false_commit_rate", "nuisance_strata"):
                self.assertIn(metric, report)
            self.assertLessEqual(len(report["events"]), 2000)
            self.assertTrue(all("elapsed_offline_time" in row and row["elapsed_offline_time"] >= 0 for row in report["events"]))
        self.assertLessEqual(len(self.result["branches"]["fcpt"]["modeled_cost"]), 27)
        self.assertEqual(len(self.result["branches"]["fcpt"]["events"]), 27)
        self.assertTrue(all(row["branch"] == "fcpt" and row["task_kind"] == "layout_comparison" for row in self.result["branches"]["fcpt"]["events"]))
        self.assertTrue(self.result["synthetic_only"])
        self.assertFalse(self.result["hardware_validity"])


if __name__ == "__main__":
    unittest.main()

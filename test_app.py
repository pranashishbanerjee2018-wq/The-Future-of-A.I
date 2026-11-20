"""
THE FUTURE OF ARTIFICIAL INTELLIGENCE
Comprehensive Quality Assurance and Automated Test Suite
File: test_app.py
"""

import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import app, PRESENTATION_DATA
import matlab_runner


class FutureAITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.testing = True
        cls.client = app.test_client()

    def test_01_index_page(self):
        """Test primary presentation UI endpoint."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("THE FUTURE OF ARTIFICIAL INTELLIGENCE", html)
        self.assertIn("Dr. Alexander Thorne", html)
        self.assertIn("Marcus Vance", html)
        self.assertIn("aspect-ratio-container", html)
        self.assertIn("matlab-scientific-modal", html)
        print("[TEST 1 PASSED] Presentation index page serves correctly.")

    def test_02_script_api_and_duration_constraints(self):
        """Test script structure, word counts, and strict duration constraints."""
        res = self.client.get("/api/script")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data["title"], "THE FUTURE OF ARTIFICIAL INTELLIGENCE")
        scenes = data["scenes"]
        self.assertEqual(len(scenes), 7, "Must contain exactly 7 sequential scenes.")

        # Duration validation
        target_duration = data["target_duration_seconds"]
        self.assertGreaterEqual(target_duration, 150, "Target duration must be at least 2m 30s (150s).")
        self.assertLessEqual(target_duration, 170, "Target duration must be at most 2m 50s (170s).")
        self.assertLess(target_duration, 180, "Strict constraint: Duration must NEVER exceed 3 minutes (180s).")

        # Word count calculation
        total_words = 0
        senior_words = 0
        junior_words = 0
        cumulative_duration = 0.0

        for sc in scenes:
            for dlg in sc["dialogues"]:
                words = len(dlg["text"].split())
                total_words += words
                if dlg["speaker"] == "senior":
                    senior_words += words
                else:
                    junior_words += words
                cumulative_duration += dlg.get("duration", 0)

        print(f"\n[TIMING & DIALOGUE VERIFICATION]")
        print(f"  Target Duration: {target_duration}s ({target_duration//60}m {target_duration%60}s)")
        print(f"  Sum of Dialogue Segment Durations: {cumulative_duration:.1f}s")
        print(f"  Total Spoken Dialogue Words: {total_words} words")
        print(f"  Senior Researcher Words: {senior_words} words")
        print(f"  Junior Researcher Words: {junior_words} words")

        # Both characters must participate meaningfully
        self.assertGreater(senior_words, 100, "Senior researcher must have meaningful dialogue.")
        self.assertGreater(junior_words, 100, "Junior researcher must have meaningful dialogue.")
        # Dialogue between 300 and 350 words
        self.assertGreaterEqual(total_words, 300, "Total spoken dialogue should be at least ~300 words.")
        self.assertLessEqual(total_words, 350, "Total spoken dialogue should not exceed ~350 words.")

        print("[TEST 2 PASSED] Dialogue word count and strict 3-minute timing criteria met.")

    def test_03_results_api_and_data_integrity(self):
        """Test numerical results API and scientific consistency."""
        res = self.client.get("/api/results")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(data["algorithm"], "Supervised k-Nearest Neighbors (k=3)")
        
        metrics = data["metrics"]
        self.assertIn("accuracy_pct", metrics)
        self.assertGreaterEqual(metrics["accuracy_pct"], 90.0, "Accuracy should be realistically high.")
        self.assertIn("precision", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("f1_score", metrics)

        cm = data["confusion_matrix"]
        total_test_samples = cm["true_positives"] + cm["false_positives"] + cm["true_negatives"] + cm["false_negatives"]
        self.assertEqual(total_test_samples, data["dataset"]["test_samples"], "Confusion matrix counts must sum to test samples.")
        print(f"[TEST 3 PASSED] Numerical results verified: Accuracy = {metrics['accuracy_pct']}%, F1 = {metrics['f1_score']}")

    def test_04_matlab_status_and_runner(self):
        """Test MATLAB detection status and diagnostics."""
        res = self.client.get("/api/matlab/status")
        self.assertEqual(res.status_code, 200)
        status = res.get_json()

        self.assertIn("installed", status)
        self.assertTrue(status["has_cached_artifacts"], "Authoritative baseline artifacts must exist.")
        self.assertTrue(os.path.isfile(status["script_path"]), "FutureAI.m must exist.")
        print(f"[TEST 4 PASSED] MATLAB detection diagnostics: installed={status['installed']}")

    def test_05_static_and_results_artifacts(self):
        """Test image plots, SVGs, and audio file serving."""
        endpoints = [
            ("/results/matlab_decision_boundary.png", 200),
            ("/results/matlab_performance_metrics.png", 200),
            ("/results/matlab_results.csv", 200),
            ("/static/images/lab_background.svg", 200),
            ("/static/images/senior_researcher.svg", 200),
            ("/static/images/junior_researcher.svg", 200),
            ("/static/audio/ambient_lab.wav", 200),
            ("/static/audio/compute_scan.wav", 200),
            ("/static/audio/ui_chime.wav", 200),
        ]
        for ep, expected_code in endpoints:
            r = self.client.get(ep)
            self.assertEqual(r.status_code, expected_code, f"Failed serving {ep}")
            self.assertGreater(len(r.data), 0, f"File {ep} is empty.")

        print("[TEST 5 PASSED] All static assets, plots, SVGs, and audio files served with 200 OK.")

    def test_06_matlab_script_validation(self):
        """Verify FutureAI.m script contents and keywords."""
        script_path = os.path.join(BASE_DIR, "FutureAI.m")
        self.assertTrue(os.path.isfile(script_path), "FutureAI.m must exist in root.")
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("rng(42, 'twister')", code, "Reproducible random seed required.")
        self.assertIn("X_train", code)
        self.assertIn("X_test", code)
        self.assertIn("matlab_decision_boundary.png", code)
        self.assertIn("matlab_performance_metrics.png", code)
        self.assertIn("matlab_results.json", code)
        self.assertIn("matlab_results.csv", code)
        print("[TEST 6 PASSED] FutureAI.m verified with all mathematical and output requirements.")


if __name__ == "__main__":
    unittest.main()

"""Independent checks of saved Assignment II evaluation artifacts."""

import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

from assignment2_experiments import capacity_threshold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs_assignment2"
MODELS = ("spark_random_forest", "sklearn_random_forest", "sklearn_logistic_regression")


@unittest.skipUnless((OUT / "model_comparison.csv").exists(), "Local Assignment II output not generated")
class Assignment2OutputTests(unittest.TestCase):
    def test_all_six_metrics_recalculate_from_test_predictions(self):
        for split in ("hash", "temporal"):
            ids = None
            for model in MODELS:
                with self.subTest(split=split, model=model):
                    p = OUT / "predictions" / f"{split}_{model}.parquet"
                    data = pd.read_parquet(p)
                    saved = json.loads((OUT / f"{split}_{model}_metrics.json").read_text(encoding="utf-8"))
                    self.assertEqual(len(data), saved["test_orders"])
                    self.assertFalse(data.order_id.duplicated().any())
                    if ids is None:
                        ids = set(data.order_id)
                    else:
                        self.assertEqual(set(data.order_id), ids)
                    y = data.is_delayed.to_numpy(dtype=int)
                    score = data.delay_score.to_numpy(dtype=float)
                    pred = data.prediction.to_numpy(dtype=int)
                    self.assertTrue(np.isfinite(score).all())
                    self.assertTrue(np.array_equal(pred, (score >= saved["threshold"]).astype(int)))
                    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
                    self.assertEqual(saved["confusion_matrix"], {
                        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)
                    })
                    self.assertAlmostEqual(saved["f1"], f1_score(y, pred), places=12)
                    self.assertAlmostEqual(saved["precision"], precision_score(y, pred), places=12)
                    self.assertAlmostEqual(saved["recall"], recall_score(y, pred), places=12)
                    self.assertAlmostEqual(saved["roc_auc"], roc_auc_score(y, score), places=12)
                    curve = pd.read_csv(OUT / "curves" / f"{split}_{model}.csv")
                    pr = curve[curve.curve == "pr"]
                    self.assertAlmostEqual(saved["pr_auc_trapezoid"],
                                           float(np.trapezoid(pr.y, pr.x)), places=12)

    def test_split_membership_and_temporal_order(self):
        hashed = pd.read_csv(OUT / "splits" / "hash.csv")
        temporal = pd.read_csv(OUT / "splits" / "temporal.csv")
        self.assertEqual(set(hashed.order_id), set(temporal.order_id))
        self.assertFalse(hashed.order_id.duplicated().any())
        self.assertFalse(temporal.order_id.duplicated().any())
        self.assertEqual([int((hashed.split == x).sum()) for x in
                          ("train", "validation", "test")], [61826, 15513, 19116])
        source = pd.read_parquet(ROOT / "outputs_ml_graph" / "ml_delivery_delay_dataset.parquet",
                                 columns=["order_id", "order_purchase_timestamp"])
        source = source.merge(temporal, on="order_id", validate="one_to_one")
        train_end = source.loc[source.split == "train", "order_purchase_timestamp"].max()
        validation_start = source.loc[source.split == "validation", "order_purchase_timestamp"].min()
        validation_end = source.loc[source.split == "validation", "order_purchase_timestamp"].max()
        test_start = source.loc[source.split == "test", "order_purchase_timestamp"].min()
        self.assertLessEqual(train_end, validation_start)
        self.assertLessEqual(validation_end, test_start)

    def test_figures_are_high_resolution(self):
        for i in range(1, 11):
            path = ROOT / "figures" / f"fig{i}_"  # Resolve the named figure for each index.
            matches = list((ROOT / "figures").glob(f"fig{i}_*.png"))
            self.assertEqual(len(matches), 1, path)
            with Image.open(matches[0]) as image:
                dpi = image.info.get("dpi", (0, 0))
                self.assertGreaterEqual(min(dpi), 299)
                self.assertGreaterEqual(min(image.size), 1000)

    def test_alert_budget_thresholds_use_validation_only(self):
        scenarios = pd.read_csv(OUT / "alert_budget_scenarios.csv")
        self.assertEqual(len(scenarios), 18)
        for row in scenarios.itertuples(index=False):
            with self.subTest(split=row.split, model=row.model,
                              budget=row.validation_alert_budget_fraction):
                stem = f"{row.split}_{row.model}"
                validation = pd.read_parquet(
                    OUT / "validation_predictions" / f"{stem}.parquet")
                test = pd.read_parquet(OUT / "predictions" / f"{stem}.parquet")
                threshold, selected = capacity_threshold(
                    validation.is_delayed.to_numpy(dtype=int),
                    validation.delay_score.to_numpy(dtype=float),
                    row.validation_alert_budget_fraction,
                )
                self.assertAlmostEqual(threshold, row.selected_threshold, places=12)
                self.assertEqual(selected["alerts"], row.validation_alerts)
                self.assertLessEqual(row.validation_alerts, row.validation_alert_budget)
                self.assertEqual(selected["tp"], row.validation_tp)
                self.assertEqual(selected["fp"], row.validation_fp)
                predicted = test.delay_score.to_numpy(dtype=float) >= threshold
                tn, fp, fn, tp = confusion_matrix(
                    test.is_delayed, predicted, labels=[0, 1]).ravel()
                self.assertEqual((tn, fp, fn, tp),
                                 (row.test_tn, row.test_fp, row.test_fn, row.test_tp))
                self.assertAlmostEqual(row.test_precision,
                                       precision_score(test.is_delayed, predicted,
                                                       zero_division=0), places=12)
                self.assertAlmostEqual(row.test_recall,
                                       recall_score(test.is_delayed, predicted,
                                                    zero_division=0), places=12)


if __name__ == "__main__":
    unittest.main()

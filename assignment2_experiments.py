"""Run the student-selected Olist Assignment II model comparisons locally.

Inputs are the existing order-level feature Parquet and hash split manifest.
Assignment I artifacts are read-only. Small summaries go to outputs_assignment2;
per-order predictions and split manifests stay local under ignored subfolders.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import trapezoid
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
FEATURES = [
    "total_items", "total_price", "total_freight", "freight_ratio",
    "max_installments", "estimated_delivery_days", "is_same_state",
    "purchase_dayofweek", "purchase_hour", "product_weight_g",
]
MODEL_DATA = ROOT / "outputs_ml_graph" / "ml_delivery_delay_dataset.parquet"
HASH_MANIFEST = ROOT / "outputs_ml_graph" / "model_data_split_manifest.csv"
OUT = ROOT / "outputs_assignment2"
SPLIT_NAMES = ("train", "validation", "test")


def load_orders() -> pd.DataFrame:
    if not MODEL_DATA.is_dir():
        raise FileNotFoundError(f"Feature Parquet missing: {MODEL_DATA}; run notebook 02 first")
    columns = ["order_id", "order_purchase_timestamp", "is_delayed", *FEATURES]
    data = pd.read_parquet(MODEL_DATA, columns=columns)
    if len(data) != 96470:
        raise ValueError(f"Expected 96,470 labeled orders, got {len(data):,}")
    if data.order_id.isna().any() or data.order_id.duplicated().any():
        raise ValueError("Order IDs must be non-null and unique")
    if data.is_delayed.isna().any() or set(data.is_delayed.unique()) != {0, 1}:
        raise ValueError("Delay label must contain only 0 and 1")
    data = data.dropna(subset=FEATURES).copy()
    if len(data) != 96455 or data.order_purchase_timestamp.isna().any():
        raise ValueError("Model-valid population or purchase timestamp differs from baseline")
    if not np.isfinite(data[FEATURES].to_numpy(dtype=float)).all():
        raise ValueError("Features contain non-finite values")
    return data


def make_manifests(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if not HASH_MANIFEST.is_file():
        raise FileNotFoundError(f"Saved hash membership missing: {HASH_MANIFEST}")
    hashed = pd.read_csv(HASH_MANIFEST, dtype=str)
    if hashed.order_id.duplicated().any() or set(hashed.split) != set(SPLIT_NAMES):
        raise ValueError("Saved hash membership has duplicates or invalid splits")
    if set(hashed.order_id) != set(data.order_id):
        raise ValueError("Hash membership does not match model-valid order IDs")
    hashed = hashed[["order_id", "split"]].copy()
    counts = hashed.split.value_counts()
    if tuple(int(counts[name]) for name in SPLIT_NAMES) != (61826, 15513, 19116):
        raise ValueError("Hash split counts differ from saved model report")

    chronological = data[["order_id", "order_purchase_timestamp"]].sort_values(
        ["order_purchase_timestamp", "order_id"], kind="stable"
    ).reset_index(drop=True)
    train_end = int(len(chronological) * 0.64)
    validation_end = int(len(chronological) * 0.80)
    chronological["split"] = "test"
    chronological.loc[: train_end - 1, "split"] = "train"
    chronological.loc[train_end : validation_end - 1, "split"] = "validation"
    temporal = chronological[["order_id", "split"]].copy()
    for name, manifest in {"hash": hashed, "temporal": temporal}.items():
        labeled = data[["order_id", "is_delayed"]].merge(
            manifest, on="order_id", validate="one_to_one"
        )
        if len(labeled) != len(data) or labeled.split.isna().any():
            raise ValueError(f"{name}: incomplete split membership")
        for part in SPLIT_NAMES:
            if set(labeled.loc[labeled.split == part, "is_delayed"]) != {0, 1}:
                raise ValueError(f"{name}: {part} lacks a class")
    return {"hash": hashed, "temporal": temporal}


def save_split_profiles(data: pd.DataFrame, manifests: dict[str, pd.DataFrame]) -> None:
    rows = []
    for scheme, manifest in manifests.items():
        joined = data[["order_id", "order_purchase_timestamp", "is_delayed"]].merge(
            manifest, on="order_id", validate="one_to_one"
        )
        for name in SPLIT_NAMES:
            part = joined.loc[joined.split == name]
            rows.append({
                "scheme": scheme, "split": name, "orders": len(part),
                "delayed_orders": int(part.is_delayed.sum()),
                "delay_prevalence": float(part.is_delayed.mean()),
                "purchase_min": str(part.order_purchase_timestamp.min()),
                "purchase_max": str(part.order_purchase_timestamp.max()),
            })
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "split_profile.csv", index=False)


def exact_threshold_curve(y: np.ndarray, score: np.ndarray) -> pd.DataFrame:
    """Match notebook 02: tied validation scores form one threshold group."""
    order = np.argsort(-score, kind="stable")
    sorted_score = score[order]
    sorted_y = y[order]
    ends = np.r_[np.flatnonzero(sorted_score[:-1] != sorted_score[1:]), len(y) - 1]
    tp = np.cumsum(sorted_y)[ends]
    fp = ends + 1 - tp
    fn = sorted_y.sum() - tp
    precision = tp / (tp + fp)
    recall = tp / sorted_y.sum()
    f1 = 2 * tp / (2 * tp + fp + fn)
    return pd.DataFrame({
        "threshold": sorted_score[ends], "precision": precision, "recall": recall,
        "f1": f1, "tp": tp, "fp": fp, "fn": fn,
    })


def select_threshold(y: np.ndarray, score: np.ndarray) -> tuple[float, dict]:
    curve = exact_threshold_curve(y, score)
    selected = curve.sort_values(
        ["f1", "precision", "threshold"], ascending=False, kind="stable"
    ).iloc[0]
    return float(selected.threshold), {
        "f1": float(selected.f1), "precision": float(selected.precision),
        "recall": float(selected.recall),
    }


def capacity_threshold(y: np.ndarray, score: np.ndarray, fraction: float) -> tuple[float, dict]:
    """Select the largest tied-score group that fits a validation alert budget."""
    if not 0 < fraction <= 1:
        raise ValueError("Alert fraction must be in (0, 1]")
    budget = int(np.floor(len(y) * fraction))
    curve = exact_threshold_curve(y, score)
    eligible = curve.loc[curve.tp + curve.fp <= budget]
    if eligible.empty:
        return float("inf"), {"budget": budget, "alerts": 0, "tp": 0, "fp": 0,
                              "precision": 0.0, "recall": 0.0}
    chosen = eligible.iloc[-1]
    return float(chosen.threshold), {
        "budget": budget, "alerts": int(chosen.tp + chosen.fp),
        "tp": int(chosen.tp), "fp": int(chosen.fp),
        "precision": float(chosen.precision), "recall": float(chosen.recall),
    }


def test_metrics(y: np.ndarray, score: np.ndarray, threshold: float) -> tuple[dict, pd.DataFrame]:
    predicted = score >= threshold
    tn = int(((y == 0) & ~predicted).sum())
    fp = int(((y == 0) & predicted).sum())
    fn = int(((y == 1) & ~predicted).sum())
    tp = int(((y == 1) & predicted).sum())
    ranked = exact_threshold_curve(y, score)
    fpr = np.r_[0.0, ranked.fp.to_numpy() / (len(y) - y.sum())]
    tpr = np.r_[0.0, ranked.recall.to_numpy()]
    precision = ranked.precision.to_numpy()
    recall = ranked.recall.to_numpy()
    # Same trapezoidal definition as notebook 02, distinct from average precision.
    roc_auc = float(trapezoid(tpr, fpr))
    pr_auc = float(trapezoid(np.r_[precision[0], precision], np.r_[0.0, recall]))
    curves = pd.concat([
        pd.DataFrame({"curve": "roc", "x": fpr, "y": tpr}),
        pd.DataFrame({"curve": "pr", "x": np.r_[0.0, recall],
                      "y": np.r_[precision[0], precision]}),
    ], ignore_index=True)
    return {
        "threshold": threshold, "test_orders": len(y), "test_positive": int(y.sum()),
        "test_prevalence": float(y.mean()),
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
        "pr_auc_trapezoid": pr_auc, "roc_auc": roc_auc,
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }, curves


def split_frames(data: pd.DataFrame, manifest: pd.DataFrame) -> dict[str, pd.DataFrame]:
    joined = data.merge(manifest, on="order_id", validate="one_to_one")
    return {name: joined.loc[joined.split == name].copy() for name in SPLIT_NAMES}


def save_result(
    split_name: str, model_name: str, validation: pd.DataFrame,
    test: pd.DataFrame, validation_score: np.ndarray, test_score: np.ndarray,
    fit_seconds: float, extra: dict | None = None,
) -> dict:
    threshold, selection = select_threshold(
        validation.is_delayed.to_numpy(dtype=int), validation_score
    )
    metrics, curves = test_metrics(test.is_delayed.to_numpy(dtype=int), test_score, threshold)
    metrics.update({
        "split": split_name, "model": model_name, "train_orders": extra["train_orders"],
        "validation_orders": len(validation), "fit_wall_seconds": fit_seconds,
        "fit_timing_scope": "model.fit only; input already loaded; single Windows machine",
        "validation_selection": selection,
        "threshold_selection": "maximum validation F1; ties prefer precision then higher threshold",
        "feature_columns": FEATURES, "delay_definition": "timestamp",
        "split_definition": extra["split_definition"],
    })
    for path in [OUT, OUT / "predictions", OUT / "validation_predictions", OUT / "curves"]:
        path.mkdir(parents=True, exist_ok=True)
    stem = f"{split_name}_{model_name}"
    validation_predictions = validation[["order_id", "is_delayed"]].copy()
    validation_predictions["delay_score"] = validation_score
    validation_predictions.to_parquet(
        OUT / "validation_predictions" / f"{stem}.parquet", index=False
    )
    predictions = test[["order_id", "is_delayed"]].copy()
    predictions["delay_score"] = test_score
    predictions["prediction"] = (test_score >= threshold).astype(int)
    predictions.to_parquet(OUT / "predictions" / f"{stem}.parquet", index=False)
    curves.to_csv(OUT / "curves" / f"{stem}.csv", index=False)
    (OUT / f"{stem}_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return metrics


def save_alert_budget_scenarios() -> None:
    """Evaluate illustrative validation-selected capacity limits on untouched test scores."""
    rows = []
    for split in ("hash", "temporal"):
        for model in ("spark_random_forest", "sklearn_random_forest",
                      "sklearn_logistic_regression"):
            stem = f"{split}_{model}"
            validation = pd.read_parquet(OUT / "validation_predictions" / f"{stem}.parquet")
            test = pd.read_parquet(OUT / "predictions" / f"{stem}.parquet")
            val_y = validation.is_delayed.to_numpy(dtype=int)
            val_score = validation.delay_score.to_numpy(dtype=float)
            test_y = test.is_delayed.to_numpy(dtype=int)
            test_score = test.delay_score.to_numpy(dtype=float)
            for fraction in (0.01, 0.05, 0.10):
                threshold, val = capacity_threshold(val_y, val_score, fraction)
                metrics, _ = test_metrics(test_y, test_score, threshold)
                confusion = metrics["confusion_matrix"]
                rows.append({
                    "split": split, "model": model,
                    "validation_alert_budget_fraction": fraction,
                    "validation_orders": len(validation),
                    "validation_alert_budget": val["budget"],
                    "validation_alerts": val["alerts"],
                    "validation_tp": val["tp"], "validation_fp": val["fp"],
                    "validation_precision": val["precision"],
                    "validation_recall": val["recall"],
                    "selected_threshold": threshold,
                    "test_orders": len(test), "test_alerts": confusion["tp"] + confusion["fp"],
                    "test_tp": confusion["tp"], "test_fp": confusion["fp"],
                    "test_fn": confusion["fn"], "test_tn": confusion["tn"],
                    "test_precision": metrics["precision"],
                    "test_recall": metrics["recall"], "test_f1": metrics["f1"],
                })
    pd.DataFrame(rows).to_csv(OUT / "alert_budget_scenarios.csv", index=False)


def run_sklearn(data: pd.DataFrame, manifests: dict[str, pd.DataFrame]) -> list[dict]:
    results = []
    for split_name, manifest in manifests.items():
        parts = split_frames(data, manifest)
        train, validation, test = (parts[name] for name in SPLIT_NAMES)
        train_x = train[FEATURES].to_numpy(dtype=float)
        train_y = train.is_delayed.to_numpy(dtype=int)
        models = {
            "sklearn_random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=8, random_state=42, n_jobs=4
            ),
            "sklearn_logistic_regression": make_pipeline(
                StandardScaler(), LogisticRegression(max_iter=2000, random_state=42)
            ),
        }
        for name, model in models.items():
            started = time.perf_counter()
            model.fit(train_x, train_y)
            elapsed = time.perf_counter() - started
            validation_score = model.predict_proba(
                validation[FEATURES].to_numpy(dtype=float)
            )[:, 1]
            test_score = model.predict_proba(test[FEATURES].to_numpy(dtype=float))[:, 1]
            results.append(save_result(
                split_name, name, validation, test, validation_score, test_score,
                elapsed, {"train_orders": len(train), "split_definition":
                    "saved order_id hash membership" if split_name == "hash" else
                    "chronological purchase timestamp, order_id tie-break; 64/16/20"},
            ))
            print(f"{split_name} {name}: F1={results[-1]['f1']:.4f} PR-AUC={results[-1]['pr_auc_trapezoid']:.4f}", flush=True)
    return results


def configure_spark_runtime() -> Path:
    if os.name != "nt":
        raise RuntimeError("This project-local Spark runtime is configured for Windows")
    runtime = ROOT / ".runtime"
    java = sorted(p for p in runtime.glob("jdk-*") if (p / "bin/java.exe").exists())
    if not java:
        raise FileNotFoundError("Project-local JDK missing; run setup_runtime.py")
    temp = runtime / "tmp"
    temp.mkdir(parents=True, exist_ok=True)
    for key in ["TMP", "TEMP", "TMPDIR"]:
        os.environ[key] = str(temp)
    tempfile.tempdir = str(temp)
    os.environ["JAVA_HOME"] = str(java[-1])
    os.environ["HADOOP_HOME"] = str(runtime / "hadoop")
    os.environ["SPARK_HOME"] = str(runtime / "spark-home")
    os.environ["PATH"] = os.pathsep.join([
        str(java[-1] / "bin"), str(runtime / "hadoop" / "bin"), os.environ["PATH"]
    ])
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    return runtime


def run_spark(data: pd.DataFrame, manifests: dict[str, pd.DataFrame]) -> list[dict]:
    runtime = configure_spark_runtime()
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import RandomForestClassifier as SparkRandomForest
    from pyspark.ml.feature import VectorAssembler
    from pyspark.ml.functions import vector_to_array
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F

    spark = (SparkSession.builder.master("local[4]").appName("Olist_Assignment2_Comparisons")
             .config("spark.driver.memory", "4g")
             .config("spark.sql.shuffle.partitions", "4")
             .config("spark.local.dir", str(runtime / "spark-local"))
             .config("spark.sql.warehouse.dir", (runtime / "spark-warehouse").as_uri())
             .config("spark.driver.bindAddress", "127.0.0.1")
             .config("spark.driver.host", "127.0.0.1")
             .config("spark.sql.session.timeZone", "America/Sao_Paulo")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    results = []
    try:
        spark_data = spark.read.parquet(str(MODEL_DATA)).select(
            "order_id", "is_delayed", *FEATURES
        ).dropna().orderBy("order_id").cache()
        if spark_data.count() != len(data):
            raise ValueError("Spark/Pandas model-valid populations differ")
        for split_name, manifest in manifests.items():
            if split_name == "hash":
                # Preserve the original notebook's partition lineage and split formula.
                outer = F.pmod(F.xxhash64(F.col("order_id"), F.lit(42)), F.lit(10000))
                inner = F.pmod(F.xxhash64(F.col("order_id"), F.lit(43)), F.lit(10000))
                joined = spark_data.withColumn(
                    "split", F.when(outer >= 8000, "test")
                    .when(inner >= 8000, "validation").otherwise("train")
                ).cache()
            else:
                membership = spark.createDataFrame(manifest[["order_id", "split"]])
                joined = spark_data.join(F.broadcast(membership), "order_id", "inner").orderBy(
                    "order_id"
                ).cache()
            if joined.count() != len(data):
                raise ValueError(f"{split_name}: Spark split join lost orders")
            expected_membership = spark.createDataFrame(manifest[["order_id", "split"]])
            if joined.select("order_id", "split").join(
                F.broadcast(expected_membership), ["order_id", "split"], "left_anti"
            ).limit(1).count():
                raise ValueError(f"{split_name}: Spark split membership differs from Pandas")
            train = joined.filter(F.col("split") == "train").cache()
            validation = joined.filter(F.col("split") == "validation").cache()
            test = joined.filter(F.col("split") == "test").cache()
            if (train.count(), validation.count(), test.count()) != tuple(
                int((manifest.split == name).sum()) for name in SPLIT_NAMES
            ):
                raise ValueError(f"{split_name}: Spark split counts differ")
            pipeline = Pipeline(stages=[
                VectorAssembler(inputCols=FEATURES, outputCol="features"),
                SparkRandomForest(labelCol="is_delayed", featuresCol="features",
                                  weightCol="class_weight", numTrees=100,
                                  maxDepth=8, seed=42),
            ])
            started = time.perf_counter()
            model = pipeline.fit(train.withColumn("class_weight", F.lit(1.0)))
            elapsed = time.perf_counter() - started

            def collect_scores(frame) -> pd.DataFrame:
                rows = model.transform(frame).select(
                    "order_id", "is_delayed",
                    vector_to_array("probability")[1].alias("delay_score")
                ).collect()
                return pd.DataFrame([r.asDict() for r in rows]).sort_values(
                    "order_id", kind="stable"
                ).reset_index(drop=True)

            validation_pd = collect_scores(validation)
            test_pd = collect_scores(test)
            results.append(save_result(
                split_name, "spark_random_forest", validation_pd, test_pd,
                validation_pd.delay_score.to_numpy(dtype=float),
                test_pd.delay_score.to_numpy(dtype=float), elapsed,
                {"train_orders": train.count(), "split_definition":
                    "saved order_id hash membership" if split_name == "hash" else
                    "chronological purchase timestamp, order_id tie-break; 64/16/20"},
            ))
            print(f"{split_name} spark_random_forest: F1={results[-1]['f1']:.4f} PR-AUC={results[-1]['pr_auc_trapezoid']:.4f}", flush=True)
            for frame in (train, validation, test, joined):
                frame.unpersist()
        spark_data.unpersist()
    finally:
        spark.stop()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=["sklearn", "spark", "all"], default="all")
    args = parser.parse_args()
    data = load_orders()
    manifests = make_manifests(data)
    save_split_profiles(data, manifests)
    (OUT / "splits").mkdir(parents=True, exist_ok=True)
    for name, manifest in manifests.items():
        manifest.to_csv(OUT / "splits" / f"{name}.csv", index=False)
    results = []
    if args.engine in ("sklearn", "all"):
        results.extend(run_sklearn(data, manifests))
    if args.engine in ("spark", "all"):
        results.extend(run_spark(data, manifests))
    existing = list(OUT.glob("*_metrics.json"))
    summary = [json.loads(p.read_text(encoding="utf-8")) for p in existing]
    pd.DataFrame([{k: v for k, v in row.items() if k not in
                  {"confusion_matrix", "validation_selection", "feature_columns"}}
                  for row in summary]).sort_values(["split", "model"]).to_csv(
                      OUT / "model_comparison.csv", index=False
                  )
    if len(list((OUT / "validation_predictions").glob("*.parquet"))) == 6:
        save_alert_budget_scenarios()
    print(f"Saved {len(results)} new evaluations to {OUT}", flush=True)


if __name__ == "__main__":
    main()

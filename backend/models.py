import json
from pathlib import Path
from typing import Dict, Any, Tuple, List
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from tuning import get_candidate_models_and_param_distributions, tune_candidate, build_ensemble_pipeline

MODELS_DIR = Path(__file__).resolve().parent / "models"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def chronological_split(
    X: pd.DataFrame,
    y: pd.Series,
    train_pct: float = 0.70,
    val_pct: float = 0.15
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Splits time-series data chronologically into Train, Validation, and Test sets.
    Strictly preserves chronological order without shuffling to prevent data leakage.
    """
    n = len(X)
    train_end = int(n * train_pct)
    val_end = int(n * (train_pct + val_pct))

    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_val, y_val = X.iloc[train_end:val_end], y.iloc[train_end:val_end]
    X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

    return X_train, y_train, X_val, y_val, X_test, y_test

def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, Any]:
    """
    Computes classification performance metrics for both binary and macro performance.
    """
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1_up = float(f1_score(y_true, y_pred, zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    roc_auc = 0.5
    if y_prob is not None:
        try:
            roc_auc = float(roc_auc_score(y_true, y_prob))
        except Exception:
            roc_auc = 0.5

    cm = confusion_matrix(y_true, y_pred).tolist()

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1_up, 4),
        "f1_macro": round(f1_macro, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": cm,
    }

def compute_baselines(y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    """
    Calculates reference baseline performance on the test set:
    1. Majority Class Baseline: Always predicts the training set's most common direction.
    2. Previous Day Direction: Follows momentum (if yesterday was UP, predict UP).
    """
    # Baseline 1: Majority Class
    maj_class = int(y_train.mode()[0])
    base1_preds = np.full(len(y_test), maj_class)
    base1_metrics = evaluate_predictions(y_test.values, base1_preds)

    # Baseline 2: Previous Day Return Direction
    base2_preds = (X_test["return_1d"].values > 0).astype(int)
    base2_metrics = evaluate_predictions(y_test.values, base2_preds)

    return {
        "baseline_1_majority_class": {
            "name": f"Majority Class (Always {'UP' if maj_class==1 else 'DOWN'})",
            "accuracy": round(base1_metrics["accuracy"] * 100.0, 2),
            "f1_macro": round(base1_metrics["f1_macro"] * 100.0, 2),
            "f1_up": round(base1_metrics["f1"] * 100.0, 2),
        },
        "baseline_2_previous_direction": {
            "name": "Previous Day Direction (Momentum Rule)",
            "accuracy": round(base2_metrics["accuracy"] * 100.0, 2),
            "f1_macro": round(base2_metrics["f1_macro"] * 100.0, 2),
            "f1_up": round(base2_metrics["f1"] * 100.0, 2),
        }
    }

def optimize_decision_threshold(pipeline: Any, X_val: pd.DataFrame, y_val: pd.Series) -> Tuple[float, float]:
    """
    Optimizes the decision threshold strictly on the VALIDATION SET.
    Searches thresholds in [0.44, 0.56] to maximize Validation Macro F1.
    Zero test data is involved.
    """
    val_probs = pipeline.predict_proba(X_val)[:, 1]
    best_th = 0.50
    best_val_macro_f1 = -1.0

    for th in np.linspace(0.44, 0.56, 25):
        val_preds = (val_probs >= th).astype(int)
        macro_f1 = f1_score(y_val, val_preds, average="macro", zero_division=0)
        if macro_f1 > best_val_macro_f1:
            best_val_macro_f1 = macro_f1
            best_th = float(th)

    return round(best_th, 3), round(best_val_macro_f1, 4)

def train_and_select_best_model(ticker: str, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
    """
    Executes the enhanced, leakage-free ML workflow:
    1. Chronological Train (70%) / Validation (15%) / Test (15%) split.
    2. Analyze class distributions across all splits.
    3. TimeSeriesSplit hyperparameter tuning with balanced class weights and f1_macro scoring.
    4. Evaluates individual candidates and the calibrated soft-voting Ensemble.
    5. Optimizes probability threshold strictly on the Validation set for each candidate.
    6. Selects the winner using Validation Macro F1.
    7. Evaluates the winner once on the untouched Test set using the validation-selected threshold.
    8. Computes baseline performance comparisons.
    9. Persists model pipeline, metadata JSON, and comprehensive report JSON.
    """
    X_train, y_train, X_val, y_val, X_test, y_test = chronological_split(X, y)

    class_dist = {
        "dataset_total": {"total": len(y), "up": int((y == 1).sum()), "down": int((y == 0).sum()), "up_pct": round(float((y == 1).mean()) * 100.0, 1)},
        "train": {"total": len(y_train), "up": int((y_train == 1).sum()), "down": int((y_train == 0).sum()), "up_pct": round(float((y_train == 1).mean()) * 100.0, 1)},
        "validation": {"total": len(y_val), "up": int((y_val == 1).sum()), "down": int((y_val == 0).sum()), "up_pct": round(float((y_val == 1).mean()) * 100.0, 1)},
        "test": {"total": len(y_test), "up": int((y_test == 1).sum()), "down": int((y_test == 0).sum()), "up_pct": round(float((y_test == 1).mean()) * 100.0, 1)},
    }

    print(f"\n========================================================")
    print(f"[ML PIPELINE] Training & Tuning Models for {ticker}")
    print(f"Total: {len(X)} rows | Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    print(f"Class Dist -> Train: {class_dist['train']['up_pct']}% UP | Val: {class_dist['validation']['up_pct']}% UP | Test: {class_dist['test']['up_pct']}% UP")
    print(f"========================================================")

    candidates = get_candidate_models_and_param_distributions(y_train.values)
    candidate_results = {}
    best_model_name = None
    best_val_macro_f1 = -1.0
    best_pipeline = None
    best_threshold = 0.50

    for name, config in candidates.items():
        print(f"[TUNING] Tuning {name} with TimeSeriesSplit on Train data (metric: f1_macro)...")
        tuned_pipeline, best_params, cv_score = tune_candidate(
            name=name,
            pipeline=config["pipeline"],
            param_distributions=config["param_distributions"],
            n_iter=config["n_iter"],
            X_train=X_train,
            y_train=y_train
        )

        # Optimize threshold strictly on Validation Set
        opt_th, val_macro_f1 = optimize_decision_threshold(tuned_pipeline, X_val, y_val)
        val_probs = tuned_pipeline.predict_proba(X_val)[:, 1]
        val_preds = (val_probs >= opt_th).astype(int)
        val_metrics = evaluate_predictions(y_val, val_preds, val_probs)

        candidate_results[name] = {
            "best_params": best_params,
            "cv_f1_macro": round(cv_score, 4),
            "opt_threshold": opt_th,
            "val_metrics": val_metrics,
            "pipeline": tuned_pipeline
        }

        print(f"   -> {name} [Th: {opt_th:.2f}] Val F1-Macro: {val_metrics['f1_macro']:.4f} (Accuracy: {val_metrics['accuracy']:.4f})")

        if val_metrics["f1_macro"] > best_val_macro_f1:
            best_val_macro_f1 = val_metrics["f1_macro"]
            best_model_name = name
            best_pipeline = tuned_pipeline
            best_threshold = opt_th

    # Also evaluate the Ensemble Candidate combining all three tuned estimators
    try:
        ensemble_pipeline = build_ensemble_pipeline(
            candidate_results["Logistic Regression"]["pipeline"],
            candidate_results["Random Forest"]["pipeline"],
            candidate_results["XGBoost"]["pipeline"]
        )
        ensemble_pipeline.fit(X_train, y_train)
        ens_opt_th, ens_val_macro_f1 = optimize_decision_threshold(ensemble_pipeline, X_val, y_val)
        ens_val_probs = ensemble_pipeline.predict_proba(X_val)[:, 1]
        ens_val_preds = (ens_val_probs >= ens_opt_th).astype(int)
        ens_val_metrics = evaluate_predictions(y_val, ens_val_preds, ens_val_probs)

        candidate_results["Ensemble (Soft Voting)"] = {
            "best_params": {"voting": "soft", "weights": [1.0, 1.1, 1.2]},
            "cv_f1_macro": round(best_val_macro_f1, 4),
            "opt_threshold": ens_opt_th,
            "val_metrics": ens_val_metrics,
            "pipeline": ensemble_pipeline
        }
        print(f"   -> Ensemble (Soft Voting) [Th: {ens_opt_th:.2f}] Val F1-Macro: {ens_val_metrics['f1_macro']:.4f} (Accuracy: {ens_val_metrics['accuracy']:.4f})")

        if ens_val_metrics["f1_macro"] > best_val_macro_f1:
            best_val_macro_f1 = ens_val_metrics["f1_macro"]
            best_model_name = "Ensemble (Soft Voting)"
            best_pipeline = ensemble_pipeline
            best_threshold = ens_opt_th
    except Exception as e:
        print(f"[WARN] Ensemble evaluation skipped: {e}")

    print(f"\n[SELECTION] Best model chosen based on Validation set: '{best_model_name}'")
    print(f"            Validation Macro F1: {best_val_macro_f1:.4f} | Optimal Threshold: {best_threshold:.3f}")

    # Evaluate the selected model ONCE on the UNTOUCHED Test set using the validation-frozen threshold
    test_probs = best_pipeline.predict_proba(X_test)[:, 1]
    test_preds = (test_probs >= best_threshold).astype(int)
    test_metrics = evaluate_predictions(y_test.values, test_preds, test_probs)

    # Compute Baselines on the untouched test set
    baselines = compute_baselines(y_train, X_test, y_test)

    print(f"\n[TEST EVALUATION] Final Test Set Metrics for {best_model_name}:")
    print(f"   Accuracy:    {test_metrics['accuracy'] * 100:.2f}% (vs Baseline 1: {baselines['baseline_1_majority_class']['accuracy']}% | Baseline 2: {baselines['baseline_2_previous_direction']['accuracy']}%)")
    print(f"   Precision:   {test_metrics['precision'] * 100:.2f}%")
    print(f"   Recall:      {test_metrics['recall'] * 100:.2f}%")
    print(f"   F1 (UP):     {test_metrics['f1'] * 100:.2f}%")
    print(f"   F1 (Macro):  {test_metrics['f1_macro'] * 100:.2f}%")
    print(f"   ROC-AUC:     {test_metrics['roc_auc']:.4f}")
    print(f"   Prediction Distribution: UP={int((test_preds == 1).sum())} | DOWN={int((test_preds == 0).sum())} (Actual UP={int((y_test == 1).sum())}, DOWN={int((y_test == 0).sum())})")
    print(f"   Confusion Matrix: {test_metrics['confusion_matrix']}")

    # Save artifacts
    clean_ticker = ticker.replace("^", "").replace(":", "_")
    model_path = MODELS_DIR / f"{clean_ticker}_model.joblib"
    metadata_path = MODELS_DIR / f"{clean_ticker}_metadata.json"
    report_path = REPORTS_DIR / f"{clean_ticker}_model_report.json"

    # Save joblib bundle
    joblib.dump({
        "ticker": ticker,
        "pipeline": best_pipeline,
        "selected_model": best_model_name,
        "threshold": best_threshold,
        "feature_names": list(X.columns),
        "test_metrics": test_metrics,
        "split_counts": {
            "train": len(X_train),
            "val": len(X_val),
            "test": len(X_test)
        }
    }, model_path)
    print(f"[PERSISTENCE] Saved trained pipeline to {model_path}")

    # Save structured metadata JSON
    metadata = {
        "ticker": ticker,
        "selected_model": best_model_name,
        "threshold": best_threshold,
        "feature_names": list(X.columns),
        "best_parameters": candidate_results[best_model_name]["best_params"],
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save comprehensive report JSON
    model_report = {
        "ticker": ticker,
        "selected_model": best_model_name,
        "selection_metric": "Validation Macro F1",
        "validation_macro_f1": best_val_macro_f1,
        "decision_threshold": best_threshold,
        "data_split": class_dist,
        "baselines": baselines,
        "test_metrics": {
            **test_metrics,
            "prediction_distribution": {
                "predicted_up": int((test_preds == 1).sum()),
                "predicted_down": int((test_preds == 0).sum()),
                "actual_up": int((y_test == 1).sum()),
                "actual_down": int((y_test == 0).sum()),
            }
        },
        "candidates_comparison": {
            k: {
                "best_params": v["best_params"],
                "cv_f1_macro": v["cv_f1_macro"],
                "opt_threshold": v["opt_threshold"],
                "val_metrics": v["val_metrics"]
            }
            for k, v in candidate_results.items()
        }
    }
    with open(report_path, "w") as f:
        json.dump(model_report, f, indent=2)
    print(f"[REPORT] Saved model report to {report_path}")

    return {
        "pipeline": best_pipeline,
        "selected_model": best_model_name,
        "threshold": best_threshold,
        "test_metrics": test_metrics,
        "test_indices": list(X_test.index),
        "test_actuals": y_test.values,
        "test_preds": test_preds,
        "test_probs": test_probs,
        "split_counts": {
            "train": len(X_train),
            "val": len(X_val),
            "test": len(X_test)
        },
        "model_report": model_report
    }

def load_saved_model(ticker: str) -> Dict[str, Any]:
    """
    Loads persisted model bundle from disk.
    """
    clean_ticker = ticker.replace("^", "").replace(":", "_")
    model_path = MODELS_DIR / f"{clean_ticker}_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file for {ticker} not found at {model_path}.")
    return joblib.load(model_path)

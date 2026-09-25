from typing import Dict, Any, Tuple
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from xgboost import XGBClassifier

def get_candidate_models_and_param_distributions(y_train: np.ndarray) -> Dict[str, Dict[str, Any]]:
    """
    Returns search spaces for Logistic Regression, Random Forest, and XGBoost.
    Incorporates class_weight='balanced' and scale_pos_weight to prevent pathological class bias.
    """
    # Calculate positive-class weighting for XGBoost: negative_count / positive_count
    neg_count = float((y_train == 0).sum())
    pos_count = float((y_train == 1).sum())
    scale_pos = max(0.5, min(2.0, neg_count / (pos_count + 1e-10)))

    candidates = {
        "Logistic Regression": {
            "pipeline": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", LogisticRegression(
                    class_weight="balanced",
                    random_state=42,
                    max_iter=1000
                ))
            ]),
            "param_distributions": {
                "classifier__C": [0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
                "classifier__solver": ["lbfgs", "liblinear"],
            },
            "n_iter": 6,
        },
        "Random Forest": {
            "pipeline": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", RandomForestClassifier(
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=1
                ))
            ]),
            "param_distributions": {
                "classifier__n_estimators": [60, 100, 140],
                "classifier__max_depth": [3, 4, 5],
                "classifier__min_samples_split": [3, 6, 10],
                "classifier__min_samples_leaf": [2, 4, 6],
                "classifier__max_features": ["sqrt", "log2"],
            },
            "n_iter": 8,
        },
        "XGBoost": {
            "pipeline": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", XGBClassifier(
                    scale_pos_weight=scale_pos,
                    random_state=42,
                    eval_metric="logloss",
                    n_jobs=1
                ))
            ]),
            "param_distributions": {
                "classifier__n_estimators": [50, 80, 120],
                "classifier__max_depth": [2, 3, 4],
                "classifier__learning_rate": [0.02, 0.04, 0.08],
                "classifier__subsample": [0.75, 0.9],
                "classifier__colsample_bytree": [0.75, 0.9],
                "classifier__min_child_weight": [2, 4],
                "classifier__reg_lambda": [1.0, 3.0, 5.0],
            },
            "n_iter": 8,
        },
    }
    return candidates

def tune_candidate(
    name: str,
    pipeline: Pipeline,
    param_distributions: Dict[str, Any],
    n_iter: int,
    X_train: np.ndarray,
    y_train: np.ndarray,
    cv_splits: int = 4
) -> Tuple[Pipeline, Dict[str, Any], float]:
    """
    Executes RandomizedSearchCV using TimeSeriesSplit on the training set only.
    Optimizes for 'f1_macro' to explicitly penalize one-sided majority class bias.
    """
    tscv = TimeSeriesSplit(n_splits=cv_splits)
    
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_distributions,
        n_iter=n_iter,
        cv=tscv,
        scoring="f1_macro",
        random_state=42,
        n_jobs=1,
        refit=True
    )
    search.fit(X_train, y_train)
    
    clean_params = {
        k.replace("classifier__", ""): (v if not isinstance(v, (np.integer, np.floating)) else float(v))
        for k, v in search.best_params_.items()
    }
    
    return search.best_estimator_, clean_params, float(search.best_score_)

def build_ensemble_pipeline(tuned_lr: Pipeline, tuned_rf: Pipeline, tuned_xgb: Pipeline) -> Pipeline:
    """
    Constructs a calibrated soft-voting ensemble combining tuned Logistic Regression,
    Random Forest, and XGBoost classifiers.
    """
    ensemble = VotingClassifier(
        estimators=[
            ("lr", tuned_lr.named_steps["classifier"]),
            ("rf", tuned_rf.named_steps["classifier"]),
            ("xgb", tuned_xgb.named_steps["classifier"])
        ],
        voting="soft",
        weights=[1.0, 1.1, 1.2]
    )
    return Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", ensemble)
    ])

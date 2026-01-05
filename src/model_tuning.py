"""Utility for hyperparameter tuning of scikit-learn compatible estimators.

Provides `tune_model` which builds a preprocessing + model Pipeline (mirroring
`train_model` preprocessing), wraps the estimator in a search (Randomized or Grid),
and returns a fitted estimator (the underlying model with best params set).

The implementation is conservative so it does not change preprocessing behavior
used elsewhere in the repo (i.e., categorical transformer only imputes, no
encoding), to avoid introducing unexpected errors.
"""
from typing import Any, Dict, Optional, Tuple

import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone, is_classifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    StratifiedKFold,
    KFold,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def _build_preprocessor(X: Any) -> ColumnTransformer:
    """Create a ColumnTransformer compatible with training pipeline.

    Mirrors preprocessing used in `train_model` to avoid changing behavior.
    - numeric: SimpleImputer(median) + StandardScaler
    - categorical: SimpleImputer(most_frequent)

    If X is not a pandas DataFrame, returns a passthrough numeric-only pipeline
    (assumes all features are numeric).
    """
    if isinstance(X, pd.DataFrame):
        numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()

        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])

        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ])

        transformers = []
        if numeric_features:
            transformers.append(("num", numeric_transformer, numeric_features))
        if categorical_features:
            transformers.append(("cat", categorical_transformer, categorical_features))

        if not transformers:
            # If DataFrame but no detected columns (edge case), fallback to passthrough
            return ColumnTransformer(transformers=[("num", numeric_transformer, X.columns)])

        return ColumnTransformer(transformers=transformers)

    else:
        # Not a DataFrame: assume numeric ndarray with all features numeric
        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        return ColumnTransformer(transformers=[("num", numeric_transformer, list(range(np.shape(X)[1])))])


def _prefix_model_params(param_dist: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure params are prefixed with 'model__' for searching inside the pipeline.

    If user already provided keys starting with 'model__', they are left unchanged.
    """
    if not param_dist:
        return {}

    new = {}
    for k, v in param_dist.items():
        if k.startswith("model__"):
            new[k] = v
        else:
            new[f"model__{k}"] = v
    return new


def tune_model(
    base_model,
    param_dist: Optional[Dict[str, Any]],
    X,
    y,
    cv: int = 5,
    scoring: Optional[str] = None,
    search: str = "random",
    n_iter: int = 20,
    n_jobs: int = -1,
    random_state: int = 42,
    refit: bool = True,
    verbose: int = 0,
) -> Any:
    """Tune hyperparameters for `base_model` and return a fitted estimator.

    Parameters
    - base_model: an unfitted scikit-learn estimator (classifier or regressor)
    - param_dist: mapping of hyperparameter names to lists or distributions. Keys
      should be estimator parameter names (e.g. 'n_estimators') or already
      prefixed with 'model__' when referencing the `model` step of the pipeline.
    - X, y: training data (pandas DataFrame/Series recommended)
    - cv: number of CV folds
    - scoring: scoring string passed to search CV (defaults to None)
    - search: 'random' for RandomizedSearchCV or 'grid' for GridSearchCV
    - n_iter: number of iterations for RandomizedSearchCV

    Returns the best underlying estimator (not the full pipeline) so it can be
    passed directly to existing `train_model` functions without breaking behavior.
    """

    # Quick guard: if no param_dist provided just return a clone of base_model
    if not param_dist:
        return clone(base_model)

    # Build preprocessor consistent with training pipeline
    preprocessor = _build_preprocessor(X)

    estimator = clone(base_model)

    pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])

    # Ensure param keys target the 'model' step
    param_dist_prefixed = _prefix_model_params(param_dist)

    # Choose CV strategy
    if is_classifier(base_model):
        cv_splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=random_state)
    else:
        cv_splitter = KFold(n_splits=cv, shuffle=True, random_state=random_state)

    # Select search method
    SearchCV = RandomizedSearchCV if search == "random" else GridSearchCV

    search_kwargs = {
        "estimator": pipe,
        "param_distributions" if search == "random" else "param_grid": param_dist_prefixed,
        "cv": cv_splitter,
        "scoring": scoring,
        "n_jobs": n_jobs,
        "refit": refit,
        "verbose": verbose,
        "random_state": random_state,
    }

    # Remove keys not accepted by GridSearchCV
    if search == "grid":
        # GridSearchCV doesn't accept n_iter or random_state
        search_kwargs.pop("random_state", None)
        search_kwargs.pop("n_iter", None)
    else:
        # RandomizedSearchCV requires n_iter
        search_kwargs["n_iter"] = n_iter

    # Filter out None values for scoring (scikit-learn handles None)
    # Run search
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if search == "random":
            search_cv = RandomizedSearchCV(
                estimator=pipe,
                param_distributions=param_dist_prefixed,
                n_iter=n_iter,
                cv=cv_splitter,
                scoring=scoring,
                n_jobs=n_jobs,
                refit=refit,
                verbose=verbose,
                random_state=random_state,
            )
        else:
            search_cv = GridSearchCV(
                estimator=pipe,
                param_grid=param_dist_prefixed,
                cv=cv_splitter,
                scoring=scoring,
                n_jobs=n_jobs,
                refit=refit,
                verbose=verbose,
            )

        search_cv.fit(X, y)

    # Print a concise summary
    try:
        best_score = search_cv.best_score_
        best_params = search_cv.best_params_
        print(f"✅ Best CV score: {best_score:.4f}")
        print("✅ Best params:")
        for k, v in best_params.items():
            print(f"  - {k}: {v}")
    except Exception:
        pass

    # Return the best underlying estimator (the 'model' step) with tuned params
    best_pipeline = search_cv.best_estimator_
    if isinstance(best_pipeline, Pipeline) and "model" in best_pipeline.named_steps:
        return best_pipeline.named_steps["model"]

    return search_cv.best_estimator_


__all__ = ["tune_model"]

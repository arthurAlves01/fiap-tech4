"""Utilitários de treinamento para experimentos de classificação.

Este módulo contém uma função de treinamento simples e transparente que usa
ColumnTransformer + Pipeline e exibe métricas básicas de teste. As alterações
são puramente organizacionais (tipagem, helper para salvar modelos) e não
alteram o comportamento de treino nem os parâmetros padrão.
"""

from typing import Tuple
import pickle
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, recall_score, precision_score,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator
from joblib import dump

# Model imports left in place for convenience in notebooks (exported for easy access)  # noqa: F401
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier  # noqa: F401
from sklearn.svm import SVC  # noqa: F401
from sklearn.tree import DecisionTreeClassifier  # noqa: F401
from xgboost import XGBClassifier  # noqa: F401
from lightgbm import LGBMClassifier  # noqa: F401
from catboost import CatBoostClassifier  # noqa: F401
from sklearn.naive_bayes import GaussianNB  # noqa: F401
from sklearn.neighbors import KNeighborsClassifier  # noqa: F401
from sklearn.linear_model import LogisticRegression  # noqa: F401


def _save_model(clf: Pipeline, model_name: str, save_type: str) -> None:
    """Salva o pipeline em disco usando joblib ou pickle (não faz nada se o tipo for inválido)."""
    if save_type == "joblib":
        dump(clf, f"..\src\models\{model_name}.joblib")
        print(f"\n✅ Modelo salvo em: {model_name}.joblib")
    else:
        with open(f"..\src\models\{model_name}.pkl", 'wb') as f:
            pickle.dump(clf, f)
        print(f"\n✅ Modelo salvo em: {model_name}.pkl")


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    model: BaseEstimator,
    save_model: bool = False,
    model_name: str = "modelo",
    save_type: str = "joblib"
) -> Tuple[Pipeline, dict, Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]]:
    """Treina um modelo de classificação usando um pipeline de pré-processamento padrão.

    Retorna o pipeline ajustado, um dicionário com métricas de teste e os
    splits de treino/teste (X_train, X_test, y_train, y_test).

    Observação: o comportamento padrão (test_size, random_state, stratify) é preservado
    da implementação original para garantir resultados idênticos.
    """

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    clf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred, average="weighted"),
        "recall": recall_score(y_test, y_pred, average="weighted"),
        "precision": precision_score(y_test, y_pred, average="weighted"),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred)
    }

    print("\n==== TEST METRICS ====")
    print("Accuracy:", metrics["accuracy"])
    print("F1:", metrics["f1_score"])
    print("Recall:", metrics["recall"])
    print("Precision:", metrics["precision"])
    print("\nConfusion Matrix:\n", metrics["confusion_matrix"])
    print("\nClassification Report:\n", metrics["classification_report"])

    if save_model:
        _save_model(clf, model_name, save_type)

    return clf, metrics, (X_train, X_test, y_train, y_test)
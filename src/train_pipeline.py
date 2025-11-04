# Libs
import pickle

from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold,
    KFold
)
from sklearn.metrics import (
    accuracy_score, f1_score, recall_score,
    precision_score, confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator
from joblib import dump, load

# Modelos de classificação
# Models
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

def train_model(X, y, model: BaseEstimator, save_model=False, model_name="modelo", save_type="joblib"):
    """
    Treina um modelo de classificação usando Pipeline.
    Pode salvar opcionalmente em joblib ou pickle.
    """
    # Models
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.tree import DecisionTreeClassifier
    from xgboost import XGBClassifier
    from lightgbm import LGBMClassifier
    from catboost import CatBoostClassifier
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.linear_model import LogisticRegression

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Detectando colunas numéricas e categóricas
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns

    # Pré-processamento
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

    # Pipeline final
    clf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    # Treino
    clf.fit(X_train, y_train)

    # Predição
    y_pred = clf.predict(X_test)

    # Métricas
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

    # Salvar modelo
    if save_model:
        if save_type == "joblib":
            dump(clf, f"{model_name}.joblib")
            print(f"\n✅ Modelo salvo em: {model_name}.joblib")
        else:
            with open(f"{model_name}.pkl", 'wb') as f:
                pickle.dump(clf, f)
            print(f"\n✅ Modelo salvo em: {model_name}.pkl")

    return clf, metrics, (X_train, X_test, y_train, y_test)
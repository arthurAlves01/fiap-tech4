"""Utilitários para carregar o modelo e executar inferência em produção.

Este módulo fornece pequenos helpers usados pela aplicação e notebooks:
- load_model: carrega um pipeline/modelo salvo (joblib ou pickle).
- preprocess_input: converte um dicionário de entrada bruto nas
    features esperadas pelo modelo treinado (preserva as mesmas transformações
    utilizadas durante o treino).

Todas as alterações neste módulo são refatores para melhorar legibilidade e manutenção
sem alterar o comportamento ou as entradas produzidas para o modelo.
"""

from typing import Any, Dict, Mapping, Optional
import joblib
import pickle
import pandas as pd

# --- Module-level constants (kept in Portuguese to match project) ---
_COLUMN_RENAME = {
    'Gender': 'sexo',
    'Age': 'idade',
    'Height': 'altura',
    'Weight': 'peso',
    'family_history': 'hist_familiar_obes',
    'FAVC': 'cons_altas_cal_freq',
    'FCVC': 'cons_verduras',
    'NCP': 'refeicoes_principais_dia',
    'CAEC': 'lancha_entre_ref',
    'SMOKE': 'fuma',
    'CH2O': 'agua_dia',
    'SCC': 'controle_calorias',
    'FAF': 'ativ_fisica',
    'TUE': 'uso_tecnologia',
    'CALC': 'cons_alcool',
    'MTRANS': 'transporte',
    'Obesity': 'nivel_obesidade'
}

_YES_NO_COLS = ('hist_familiar_obes', 'cons_altas_cal_freq', 'fuma', 'controle_calorias')
_YES_NO_MAP = {'yes': 1, 'no': 0}

_SEXO_MAP = {'Female': 0, 'Male': 1}

_INT_ROUND_COLS = ('idade', 'cons_verduras', 'refeicoes_principais_dia', 'ativ_fisica', 'uso_tecnologia')
_WATER_COL = 'agua_dia'
_FLOAT_ROUND_COLS = ('altura', 'peso')

_FREQ_MAP = {'no': 0, 'Sometimes': 0, 'Frequently': 1, 'Always': 1}
_ATIV_MAP = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1}
_TRANSP_MAP = {'Automobile': 1, 'Motorbike': 1, 'Public_Transportation': 1, 'Bike': 0, 'Walking': 0}

# Columns selected in the same order as training pipeline expected
_FINAL_FEATURES = [
    'hist_familiar_obes', 'cons_altas_cal_freq', 'cons_verduras',
    'refeicoes_principais_dia', 'lancha_entre_ref_bin', 'fuma',
    'agua_dia', 'controle_calorias', 'ativ_fisica_bin',
    'uso_tecnologia', 'cons_alcool_bin', 'trasporte_bin'
]


def load_model(model_path: str) -> Any:
    """Carrega um modelo/pipeline salvo a partir do disco.

    Suporta os formatos `.joblib` e `.pkl` (comportamento mantido).

    Parameters
    ----------
    model_path : str
        Caminho para o arquivo serializado do modelo.

    Returns
    -------
    Any
        O objeto do modelo desserializado (normalmente um pipeline/estimador do scikit-learn).
    """
    if model_path.endswith(".joblib"):
        return joblib.load(model_path)
    if model_path.endswith(".pkl"):
        with open(model_path, "rb") as f:
            return pickle.load(f)

    raise ValueError("Formato inválido. Use .joblib ou .pkl")


def _map_yes_no(df: pd.DataFrame) -> None:
    """Mapeia colunas texto 'yes'/'no' para 0/1 in-place (seguro caso a coluna falte)."""
    for col in _YES_NO_COLS:
        if col in df:
            df[col] = df[col].map(_YES_NO_MAP).copy()


def _map_sexo(df: pd.DataFrame) -> None:
    """Mapeia valores de `sexo` para 0/1 in-place."""
    if 'sexo' in df:
        df['sexo'] = df['sexo'].map(_SEXO_MAP).copy()


def _round_numeric_columns(df: pd.DataFrame) -> None:
    """Aplica as mesmas regras de arredondamento da implementação original."""
    for col in _INT_ROUND_COLS:
        if col in df:
            # keep behavior: round to 0 decimals (results as float as before)
            df[col] = df[col].round(0)

    if _WATER_COL in df:
        df[_WATER_COL] = df[_WATER_COL].round().astype(int)

    for col in _FLOAT_ROUND_COLS:
        if col in df:
            df[col] = df[col].round(2)


def _map_custom_bins(df: pd.DataFrame) -> None:
    """Cria colunas binárias derivadas de entradas categóricas (in-place)."""
    # use .get to avoid KeyError when column not provided; behavior will remain
    # identical for valid inputs and will raise later if a required feature is missing
    if 'lancha_entre_ref' in df:
        df['lancha_entre_ref_bin'] = df['lancha_entre_ref'].map(_FREQ_MAP)
    if 'cons_alcool' in df:
        df['cons_alcool_bin'] = df['cons_alcool'].map(_FREQ_MAP)
    if 'ativ_fisica' in df:
        df['ativ_fisica_bin'] = df['ativ_fisica'].map(_ATIV_MAP)
    if 'transporte' in df:
        # keep the original (misspelled) column name 'trasporte_bin' to avoid changing shape
        df['trasporte_bin'] = df['transporte'].map(_TRANSP_MAP)


def preprocess_input(input_dict: Mapping[str, Any]) -> pd.DataFrame:
    """Converte um dicionário de entrada bruto no DataFrame de features do modelo.

    Esta função preserva exatamente as transformações usadas durante o treino.
    Retorna intencionalmente a mesma ordem de colunas usada pelo pipeline de treino
    para evitar alterações inadvertidas no comportamento.

    Parameters
    ----------
    input_dict : Mapping[str, Any]
        Observação única como um mapeamento (ex.: JSON de requisição ou dados de formulário).

    Returns
    -------
    pd.DataFrame
        DataFrame com uma linha e as features esperadas pelo modelo.
    """
    df = pd.DataFrame([dict(input_dict)])
    df = df.rename(columns=_COLUMN_RENAME)

    _map_yes_no(df)
    _map_sexo(df)
    _round_numeric_columns(df)
    _map_custom_bins(df)

    # Final selection/ordering must remain identical to training
    df = df[_FINAL_FEATURES]

    return df


def predict_from_input(model: Any, input_dict: Mapping[str, Any]) -> Dict[str, str]:
    """Executa o fluxo completo de predição em produção e retorna um dicionário amigável.

    Comportamento preservado: se o `model` expõe `predict_proba`, a segunda coluna
    (classe=1) é usada como probabilidade da classe positiva.
    """
    df_processed = preprocess_input(input_dict)

    pred_raw = model.predict(df_processed)[0]

    prob: Optional[float] = None
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(df_processed)[0][1]

    if pred_raw == 1:
        msg = "⚠️ Há indícios de que pode ter obesidade."
    else:
        msg = "✅ Baixa probabilidade de obesidade."

    if prob is not None:
        prob_msg = f"Probabilidade estimada: {prob:.2%}"
        return {"mensagem": msg, "probabilidade": prob_msg}

    return {"mensagem": msg}


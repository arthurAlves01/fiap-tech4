# fiap-tech4 ✅

## Descrição

**fiap-tech4** é um projeto desenvolvido para a Tech Challenger (Fase 4) que utiliza Machine Learning para prever indícios de obesidade a partir de características sociodemográficas e comportamentais. A aplicação principal é uma interface Streamlit com páginas para exploração, predição, histórico e geração de PDFs de relatório.

---

## Sumário

- 📌 **Status**: Pronto para entrega
- 🚀 **Tecnologias**: Python, Streamlit, scikit-learn, XGBoost, Joblib
- 📁 **Dados**: `data/Obesity.csv`, `data/df_model_final.csv`
- 🧠 **Modelos**: `src/models/*.joblib`

---

## Funcionalidades principais ✨

- Interface web com páginas: **Home**, **Prever**, **Historico**, **Sobre**
- Predição de risco de obesidade com modelos treinados (`RandomForest`, `XGBoost`)
- Geração de relatórios em PDF com suporte a acentuação (quando houver fonte TTF disponível)
- Pipeline de treinamento e funções de produção (`src/models/train_pipeline.py`, `src/models/production_pipeline.py`)

---

## Estrutura do repositório 🔧

- `src/` – código-fonte da aplicação
  - `app.py` – ponto de entrada do Streamlit
  - `1_dash.py` – dashboard auxiliar
  - `models/` – pipelines de treino e modelos serializados (`.joblib`)
  - `pages/` – telas do Streamlit (Home, Prever, Histórico, Sobre)
  - `utils/` – utilitários (conexão, plots, scripts auxiliares)
- `data/` – datasets usados no projeto (`Obesity.csv`, `df_model_final.csv`)
- `README.md` – documentação (este arquivo)
- `pyproject.toml` / `requirements.txt` – dependências

---

## Pré-requisitos ✅

- Python 3.11+ (o projeto declara compatibilidade com >=3.11)
- Recomenda-se criar um ambiente virtual (venv/conda/poetry)

---

## Instalação e execução 🚀

### Com pip

1. Criar e ativar um ambiente virtual
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux / macOS
   .\.venv\Scripts\Activate  # Windows (PowerShell/CMD)
   ```
2. Instalar dependências
   ```bash
   pip install -r requirements.txt
   ```
3. Rodar a aplicação Streamlit
   ```bash
   streamlit run src/app.py
   ```

### Com Poetry

1. Instalar dependências
   ```bash
   poetry install
   ```
2. Executar app (script configurado em `pyproject.toml`)
   ```bash
   poetry run app
   ```

> Dica: existe o utilitário `src/utils/run_streamlit.py` que programa a execução via API do Streamlit (útil para deploys e testes automatizados).

---

## Uso da API de produção (exemplo) 🧩

Você pode carregar um modelo e rodar uma previsão programaticamente usando `src/models/production_pipeline.py`:

```python
from src.models.production_pipeline import load_model, predict_from_input

model = load_model('src/models/random_forest_final.joblib')

input_example = {
    'Gender': 'Male',
    'Age': 25,
    'Height': 1.75,
    'Weight': 70,
    'family_history': 'yes',
    'FAVC': 'no',
    'FCVC': 2,
    'NCP': 3,
    'CAEC': 'Sometimes',
    'SMOKE': 'no',
    'CH2O': 2,
    'SCC': 'no',
    'FAF': 1,
    'TUE': 2,
    'CALC': 'no',
    'MTRANS': 'Public_Transportation'
}

resultado = predict_from_input(model, input_example)
print(resultado)
```

---

## Treinamento / Reprodutibilidade 🔁

O pipeline de treino está em `src/models/train_pipeline.py`. Para reproduzir um treino simples:

1. Carregue os dados em `data/` e prepare `X`/`y` conforme utilizado no projeto.
2. Importe `train_model` e passe o estimador desejado (ex.: `RandomForestClassifier`).

Exemplo mínimo:

```python
from src.models.train_pipeline import train_model
from sklearn.ensemble import RandomForestClassifier

clf, metrics, splits = train_model(X, y, RandomForestClassifier(n_estimators=100), save_model=True, model_name='random_forest_final')
```

---

## Validação e métricas 📊

- Métricas computadas no pipeline: **accuracy**, **f1_score**, **recall**, **precision**, **confusion_matrix** e **classification_report**.
- Testes manuais recomendados: executar a página `Prever`, gerar PDFs e comparar previsões com subconjunto conhecido.

---

## Dados 🗄️

Principais arquivos de dados:

- `data/Obesity.csv` — dataset original com atributos demográficos e comportamentais
- `data/df_model_final.csv` — versão processada utilizada para treino/avaliação

> Atenção: dados podem conter colunas categóricas codificadas (veja `src/models/production_pipeline.py` para mapeamentos usados em produção).

---

## Boas práticas para entrega final ✅

- Verifique se `requirements.txt` ou `pyproject.toml` contém todas as dependências.
- Confirme que `src/models/*.joblib` estão atualizados e funcionais.
- Teste a geração de PDF em uma máquina Windows (verifique fonte TTF para acentuação).
- Atualize este README com quaisquer instruções específicas de deploy se for necessário (Docker/Kubernetes).

---

## Contribuição e contato 🤝

- Autor: **grupo-tech-data-analytics-fiap** — ``
- Para dúvidas sobre o projeto, execução ou entrega final, envie um e-mail com o assunto: **[fiap-tech4] Dúvida / Entrega**.

---

## Licença

Licença não especificada. Para uso, distribuição ou publicação consulte o autor responsável pelo repositório.

---

## Checklist de entrega final 🧾

- [ ] Código funcional (rodar `streamlit run src/app.py`)
- [ ] Modelos (`.joblib`) incluídos em `src/models/`
- [ ] Dados mínimos de exemplo no diretório `data/`
- [ ] Este `README.md` atualizado e claro para avaliadores


---

**Obrigado!** ✨
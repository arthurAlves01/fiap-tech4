# fiap-tech4

## Description

## Prerequisites

1. Python 3.13.17
2. `poetry` or `streamlit`

## Running app

### With streamlit

2. `pip install -r requirements.txt`
3. `streamlit run src\streamlit_app_full.py`

### With poetry

1. `poetry install`
2. `poetry run app`

## Data sources

### [Obesity.csv](./data/Obesity.csv)

#### Attributes

- **Gender**: Genero
- **Age**: Idade
- **Height**: Altura
- **Weight**: Peso
- **family_history**: Algum membro da familia sofreu ou sofre de excesso de
peso?
- **FAVC**: Voce come alimentos altamente calóricos com frequencia?
- **FCVC**: Voce costuma comer vegetais nas suas refeicoes?
- **NCP**: Quantas refeições principais você faz diariamente?
- **CAEC**: Você come alguma coisa entre as refeições?
- **SMOKE**: Você fuma?
- **CH2O**: Quanta água você bebe diariamente?
- **SCC**: Você monitora as calorias que ingere diariamente?
- **FAF**: Com que frequência você pratica atividade física?
- **TAR/TUE**: Quanto tempo você usa dispositivos tecnológicos como celular,
videogame, televisão, computador e outros?
- **CALC**: Com que frequência você bebe álcool?
- **MTRANS**: Qual meio de transporte voce coustuma usar?
- (target) **Obesity_leval**: Nivel de obesidade

- Modificcação de teste.
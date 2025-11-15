# fiap-tech4

## Description


## Prerequisites
1. Python 3.13.17
2. Run `pip install -r requirements.txt`


## Data sources

### [Obesity.csv](./data/Obesity.csv)

#### Attributes

- **Gender** — (Gênero) Sexo biológico. Valores: Female , Male .
- **Age** — (Idade) Idade em anos. Valores: numérico contínuo (mín 14, máx 61).
- **Height** — (Altura) Altura em metros. Valores: numérico contínuo (ex.: 1.45–1.98 m).
- **Weight** — (Peso) Peso em quilogramas. Valores: numérico contínuo (ex.: 39–173 kg).
- **family_history** — (Family history of overweight) Histórico familiar de excesso de peso.Valores: yes (há histórico), no (não há).
- **FAVC** — (Frequent consumption of high-caloric food) Consumo frequente de alimentos muito calóricos. Valores: yes (sim), no (não).
- **FCVC** — (Frequency of consumption of vegetables) Frequência de consumo de vegetais nas refeições. Valores (escala 1–3): 1 raramente, 2 às vezes, 3 sempre. Nota: no arquivo os valores aparecem com decimais (ruído); interprete arredondando para o inteiro mais próximo.
- **NCP** — (Number of main meals) Número de refeições principais por dia. Valores (escala 1–4): 1 uma refeição, 2 duas, 3 três, 4 quatro ou mais. Nota: valores com decimais devem ser arredondados.
- **CAEC** — (Consumption of food between meals) Consumo de lanches/comes entre as refeições. Valores: no (não consome), Sometimes (às vezes), Frequently (frequentemente), Always (sempre).
- **SMOKE** — (Smoking) Hábito de fumar. Valores: yes (fuma), no (não fuma).
- **CH2O** — (Daily water consumption) Consumo diário de água. Valores (escala 1–3): 1 < 1 L/dia, 2 1–2 L/dia, 3 > 2 L/dia. Nota: arredonde valores decimais para interpretar a categoria.
- **SCC** — (Calories consumption monitoring) Monitora a ingestão calórica diária. Valores: yes (sim), no (não).
- **FAF** — (Physical activity frequency) Frequência semanal de atividade física. Valores (escala 0–3): 0 nenhuma, 1 ~1–2×/sem, 2 ~3–4×/sem, 3 5×/sem ou mais. Nota: arredonde valores decimais.
- **TUE** — (Time using electronic devices) Tempo diário usando dispositivos eletrônicos. Valores (escala 0–2): 0 ~0–2 h/dia, 1 ~3–5 h/dia, 2 > 5 h/dia. Nota:arredonde valores decimais.
- **CALC** — (Alcohol consumption) Consumo de bebida alcoólica. Valores: no (não bebe), Sometimes (às vezes), Frequently (frequentemente), Always (sempre).
- **MTRANS** — (Transportation used / Mode of transport) Meio de transporte habitual. Valores: Automobile (carro), Motorbike (moto), Bike (bicicleta), Public_Transportation (transporte público), Walking (a pé).
- **Obesity** — (Target label / Nível de obesidade) Classe de peso corporal. Valores: Insufficient_Weight (abaixo do peso), Normal_Weight (peso normal), Overweight_Level_I (sobrepeso I), Overweight_Level_II (sobrepeso II), Obesity_Type_I (obesidade I), Obesity_Type_II (obesidade II), Obesity_Type_III (obesidade III).
# %% [markdown]
# # Notebook de análise exploratória dos dados (EDA)

# %%
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# %%
import pandas as pd
#import pandas_ta as ta

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import streamlit as st

st.header("Análise Exploratória dos Dados - EDA")
st.write("Visualizações e insights iniciais sobre o conjunto de dados de obesidade.")

# %%
input_path = "C:/Users/wbaldin/Desktop/fase04/Obesity.csv"

df = pd.read_csv(input_path)
df = df.rename_axis('ds').sort_index()
df.tail()

# %%
px.histogram(df, x='Gender', )

# %%
px.histogram(df, x = 'Gender', text_auto = True, color = 'Obesity', barmode = 'group')

# %%
px.histogram(df, x = 'family_history', text_auto = True, color = 'Obesity', barmode = 'group',category_orders={"Obesity": ["Insufficient Weight", "Normal Weight", "Overweight Level I", "Overweight Level II", "Obesity Type I", "Obesity Type II", "Obesity Type III"]}, 
             color_discrete_sequence=px.colors.qualitative.Vivid)

# %%
import plotly.express as px
fig = px.histogram(df, x="Obesity", color="Gender",barmode = 'group', text_auto=True, category_orders={"Obesity": ["Insufficient Weight", "Normal Weight", "Overweight Level I", "Overweight Level II", "Obesity Type I", "Obesity Type II", "Obesity Type III"]}, 
                   color_discrete_sequence=px.colors.qualitative.Vivid)
fig.show()

# %%
px. histogram(df,x= "Age", text_auto = True, color = 'Obesity', barmode = 'group')

# %%
import plotly.express as px
fig = px.histogram(df, x="Obesity", color="MTRANS",barmode = 'group', text_auto=True, category_orders={"Obesity": ["Insufficient Weight", "Normal Weight", "Overweight Level I", "Overweight Level II", "Obesity Type I", "Obesity Type II", "Obesity Type III"]}, )
fig.show()

# %%
import plotly.express as px
fig = px.histogram(df, x="Obesity", color="CAEC",barmode = 'group', text_auto=True, category_orders={"Obesity": ["Insufficient Weight", "Normal Weight", "Overweight Level I", "Overweight Level II", "Obesity Type I", "Obesity Type II", "Obesity Type III"]}, )
fig.show()

# %%
import plotly.express as px
fig = px.histogram(df, x="Obesity", color="SMOKE",barmode = 'group', text_auto=True, category_orders={"Obesity": ["Insufficient Weight", "Normal Weight", "Overweight Level I", "Overweight Level II", "Obesity Type I", "Obesity Type II", "Obesity Type III"]}, )
fig.show()

# %%
import plotly.express as px
fig = px.histogram(df, x="Obesity", color="SCC",barmode = 'group', text_auto=True, category_orders={"Obesity": ["Insufficient Weight", "Normal Weight", "Overweight Level I", "Overweight Level II", "Obesity Type I", "Obesity Type II", "Obesity Type III"]}, )
fig.show()

# %%
df_correl = df.drop(columns=['FAVC' ,'family_history', 'FAVC','CAEC','SMOKE','SCC','MTRANS','Gender','CALC','Obesity'])
df_correl.head()
df_correl.dropna(inplace=True)
df_correl.head()


# %%
correlation_matrix = df_correl.corr().round(2)
fig, ax = plt.subplots(figsize=(8, 8))
sns.heatmap(data=correlation_matrix, annot=True, linewidths=.7, ax=ax)


# %%
df.head()



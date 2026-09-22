# %%
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %%
ROOT = Path(".")
DIRS = ["data"]

for directory in DIRS:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

RAW_FILE = Path("../data/raw/acidentes2025.csv")
ANALYTICAL_FILE = Path("../data/acidentes2025_analitica.csv")
df = pd.read_csv(RAW_FILE, sep=";", encoding="latin1", low_memory=False)

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)


# %%
# Total de acidentes
print(df.shape[0])
# %%
# Total de acidentes fatais
print(df["acidente_fatal"].sum())

# %%
# Total de mortos
print(df["mortos"].sum())

# %%
# Total de feridos
print(df["feridos_leves"].sum())
# %%
print(df["acidente_fatal"].sum() / len(df) * 100)

# %%
print(df["mortos"].sum() / (df["feridos"].sum() + df["mortos"].sum()) * 100)
# %% [markdown]
# # Problema
# Influência das Condições Meteorológicas
#
# # Perguntas
# Condições climáticas adversas aumentam a letalidade (proporção de mortos por acidente)?
# Qual condição específica apresenta o maior risco de óbito quando ocorre?
# A combinação de mau tempo com a ausência de luz (noite) cria um risco exponencialmente maior do que a soma das duas variáveis isoladas?
# O clima altera a natureza do acidente? (Ex: chuva gera mais colisões traseiras; tempo seco gera mais saídas de pista).
#
# # Hipoteses
# Hipótese
# A taxa de letalidade em dias de céu claro é superior à taxa de letalidade em dias de chuva.
# Acidentes com neblina têm a maior taxa de letalidade entre todas as condições climáticas.
# A letalidade em condições adversas (chuva/neblina) à noite é desproporcionalmente maior do que durante o dia sob o mesmo clima.
# Acidentes por saída de pista e capotamento são estatisticamente mais frequentes em pistas secas do que em pistas molhadas.

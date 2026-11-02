# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ANALYTICAL_FILE = Path(__file__).parent.parent / "modelo_dados/acidentes2025.csv"
df = pd.read_csv(ANALYTICAL_FILE, sep=",", encoding="utf-8", low_memory=False)

# %%
# Total de acidentes
len(df.index)

# %%
# Total de mortos
int(df["mortos"].sum())

# %%
# Total de feridos
int(df["feridos"].sum())

# %%
# Total de acidentes fatais
int(df["acidente_fatal"].sum())

# %%
# Percentual de acidentes fatais
pct_fatal = int(df["acidente_fatal"].sum()) / len(df.index) * 100
round(pct_fatal, 2)

# %%
# Acidentes por condicao_metereologica
df["condicao_metereologica"].value_counts()

# %%
# Acidentes por tipo_acidente
df["tipo_acidente"].value_counts()

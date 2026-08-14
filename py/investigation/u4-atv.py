# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
# ---

# %% [markdown]
# ### 2. Importação das bibliotecas

# %%
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %% [markdown]
# ### 3. Leitura dos dados

# %%
ROOT = Path(".")
DIRS = ["data"]

for directory in DIRS:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

RAW_FILE = Path("./data/acidentes2025.csv")
ANALYTICAL_FILE = Path("./data/acidentes2025_analitica.csv")
df = pd.read_csv(ANALYTICAL_FILE, sep=";", encoding="latin1", low_memory=False)

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)

# %%
uf_counts = df.groupby("uf").size().sort_values(ascending=False)
print(uf_counts[uf_counts > 100])

# %%
uf_fatal_counts = df[df["mortos"] > 0].groupby("uf").size().sort_values(ascending=False)
print(uf_fatal_counts[uf_fatal_counts > 100])

# %%
uf_fatality_rate = (
    (df.groupby("uf")["acidente_fatal"].mean() * 100)
    .round(2)
    .sort_values(ascending=False)
)
print(uf_fatality_rate)

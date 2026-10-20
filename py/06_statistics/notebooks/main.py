# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ANALYTICAL_FILE = Path("../data/raw/acidentes2025_analitica.csv")
RAW_FILE = Path("../data/acidentes2025.csv")
df = pd.read_csv(RAW_FILE, sep=";", encoding="latin1", low_memory=False)

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)

# %% [markdown]
# # Entregável 1
# Período cobre 2025

# %%
df.shape

# %%
df.info()

# %%
df.dtypes[df.dtypes == 'str']

# %%
df.dtypes[df.dtypes == 'int64']

# %%
df.isna().sum()

# %%
print(df.duplicated(keep=False).sum())

# %% [markdown]
# # Entregável 2

# %%
def stats(col: pd.Series) -> pd.Series:
    q1 = col.quantile(0.25)
    q3 = col.quantile(0.75)
    return pd.Series(
        {
            "média": col.mean(),
            "mediana": col.median(),
            "moda": col.mode().iloc[0],
            "mínimo": col.min(),
            "máximo": col.max(),
            "amplitude": col.max() - col.min(),
            "desvio": col.std(),
            "Q1 (25%)": q1,
            "Q3 (75%)": q3,
        }
    )


# %%
stats(df["mortos"])

# %%
stats(df["feridos"])

# %%
stats(df["pessoas"])
# %% [markdown]
# # Entregável 3
# %% [markdown]
# # Entregável 4
# %% [markdown]
# # Entregável 5
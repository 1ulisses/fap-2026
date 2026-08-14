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

# %%
# Importação
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %%
# Leitura
ROOT = Path(".")
DIRS = ["data"]

for directory in DIRS:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

RAW_FILE = Path("data/acidentes2025.csv")
df = pd.read_csv(RAW_FILE, sep=";", encoding="latin1", low_memory=False)

# %%
# Conhecimento Inicial
df.head(5)

# %%
df.tail(5)

# %%
df.sample(5)

# %%
df.shape

# %%
lines, columns = df.shape
print(lines, columns)

# %%
df.columns

# %%
print(len(df.columns))

# %%
df.info()

# %%
df.dtypes

# %%
# Diagnósticos
df.isna()

# %%
duplicates = df.duplicated(keep=False)
print(duplicates.sum())

# %%
unique = df.nunique().sort_values(ascending=False)
unique.head(10)

# %%
cols = df.columns
for col in cols:
    print(df[col].value_counts().head(5))


# %%
# Tratamento
def sanitize_name(name):
    name = str(name).strip().lower()

    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")

    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    name = name.replace("/", "_")

    while "__" in name:
        name = name.replace("__", "_")
    return name.strip("_")


# %%
df.columns = [sanitize_name(col) for col in df.columns]
df.columns.tolist()

# %%
col_text = df.select_dtypes(include="str").columns
for col in col_text:
    df[col] = df[col].astype("string").str.strip().str.upper()

# %%
num_cols = [
    "br",
    "km",
    "pessoas",
    "mortos",
    "feridos",
    "feridos_leves",
    "feridos_graves",
    "ilesos",
    "ignorados",
    "veiculos",
]
existing_num_cols = [col for col in num_cols if col in df.columns]

for col in existing_num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df[existing_num_cols].dtypes

# %%
# Novas variáveis
df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
df["ano"] = df["data_inversa"].dt.year
df["mes"] = df["data_inversa"].dt.month
df["trimestre"] = df["data_inversa"].dt.quarter
df["dia_semana_num"] = df["data_inversa"].dt.dayofweek
df["fim_de_semana"] = df["dia_semana_num"].isin([5, 6]).astype(int)
horario_limpo = df["horario"].astype(str).str.strip()
df["hora"] = pd.to_datetime(horario_limpo, format="%H:%M:%S", errors="coerce").dt.hour


def classificar_turno(hora):
    if pd.isna(hora):
        return "IGNORADO"
    if 0 <= hora <= 5:
        return "MADRUGADA"
    if 6 <= hora <= 11:
        return "MANHA"
    if 12 <= hora <= 17:
        return "TARDE"
    return "NOITE"


df["turno"] = df["hora"].apply(classificar_turno)

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)
df["acidente_fatal"].value_counts()

# %%
df["acidente_fatal"].value_counts(normalize=True) * 100

# %%
violations = df[
    ((df["mortos"] >= 1) & (df["acidente_fatal"] != 1))
    | ((df["mortos"] == 0) & (df["acidente_fatal"] != 0))
]

# %%
assert len(violations) == 0

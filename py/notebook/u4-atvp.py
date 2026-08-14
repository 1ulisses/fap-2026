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


df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
df["ano"] = df["data_inversa"].dt.year
df["mes"] = df["data_inversa"].dt.month
df["trimestre"] = df["data_inversa"].dt.quarter
df["dia_semana_num"] = df["data_inversa"].dt.dayofweek
df["fim_de_semana"] = df["dia_semana_num"].isin([5, 6]).astype(int)
horario_limpo = df["horario"].astype(str).str.strip()
df["hora"] = pd.to_datetime(horario_limpo, format="%H:%M:%S", errors="coerce").dt.hour
df["turno"] = df["hora"].apply(classificar_turno)
df["total_vitimas"] = df["mortos"] + df["feridos_leves"] + df["feridos_graves"]
df["acidente_grave"] = np.where((df["mortos"] > 0) | (df["feridos_graves"] > 0), 1, 0)
df["indice_gravidade"] = (
    df["mortos"] * 3 + df["feridos_graves"] * 2 + df["feridos_leves"]
) / df["pessoas"]


# %%
def formatar_br(valor):
    if pd.isna(valor) or valor == 0:
        return "BR-IGNORADA"
    return f"BR-{int(valor):03d}"


df["br_formatada"] = df["br"].apply(formatar_br)
df["chave_localidade"] = (
    df["uf"].astype(str)
    + "_"
    + df["municipio"].astype(str)
    + "_"
    + df["br_formatada"].astype(str)
)
display(df[["uf", "municipio", "br", "br_formatada", "chave_localidade"]].head())

# %%
check = {
    "linhas": len(df),
    "colunas": df.shape[1],
    "acidentes_fatais": int(df["acidente_fatal"].sum()),
    "taxa_fatalidade": float(df["acidente_fatal"].mean()),
    "total_mortos": int(df["mortos"].sum()),
}

check


# %%
def fatal_rate_per_category(base, coluna, min_registros=30):
    tab = (
        base.groupby(coluna)
        .agg(
            qtd_acidentes=("acidente_fatal", "size"),
            qtd_fatais=("acidente_fatal", "sum"),
            taxa_fatal=("acidente_fatal", "mean"),
        )
        .reset_index()
    )
    tab = tab[tab["qtd_acidentes"] >= min_registros]
    return tab.sort_values("taxa_fatal", ascending=False)


display(fatal_rate_per_category(df, "tipo_acidente", min_registros=30).head(10))

# %%
violations = df[
    ((df["mortos"] >= 1) & (df["acidente_fatal"] != 1))
    | ((df["mortos"] == 0) & (df["acidente_fatal"] != 0))
]

# %%
assert len(violations) == 0

# %%
important = [
    "uf",
    "municipio",
    "causa_acidente",
    "tipo_acidente",
    "fase_dia",
    "condicao_metereologica",
    "tipo_pista",
    "tracado_via",
    "uso_solo",
    "classificacao_acidente",
    "dia_semana",
]
for coluna in important:
    if coluna in df.columns:
        df[coluna] = df[coluna].fillna("IGNORADO")
print(df[important].isna().sum().sort_values(ascending=False))
# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)
df["acidente_fatal"].value_counts()

# %%
df["acidente_fatal"].value_counts(normalize=True) * 100

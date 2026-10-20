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
# ## 3. Leitura dos dados

# %%
ROOT = Path(".")
DIRS = ["data"]

for directory in DIRS:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

RAW_FILE = Path("data/acidentes2025.csv")
df = pd.read_csv(RAW_FILE, sep=";", encoding="latin1", low_memory=False)

# %%
df.head(5)

# %% [markdown]
# ### 4. Conhecimento inicial da base

# %%
df.head()

# %%
df.shape

# %%
lines, columns = df.shape
print(f"Linhas: {lines}, Colunas: {columns}")

# %%
df.info()

# %%
df.dtypes

# %%
df.columns

# %%
print(f"Total de colunas: {len(df.columns)}")

# %% [markdown]
# ### 5. Diagnóstico dos dados

# %%
df.isna().sum()

# %%
duplicates = df.duplicated(keep=False)
print(f"Total de registros duplicados: {duplicates.sum()}")

# %%
unique = df.nunique().sort_values(ascending=False)
unique.head(15)

# %%
cols = df.select_dtypes(include="object").columns
for col in cols:
    print(f"\n{col}:")
    print(df[col].value_counts().head(5))

# %% [markdown]
# ### 6. Tratamento dos dados


# %%
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
print(df.columns.tolist())

# %%
col_text = df.select_dtypes(include="object").columns
for col in col_text:
    df[col] = df[col].astype(str).str.strip().str.upper()

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
df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")

# %%
horario_limpo = df["horario"].astype(str).str.strip()
df["hora"] = pd.to_datetime(horario_limpo, format="%H:%M:%S", errors="coerce").dt.hour

# %%
print("Valores ausentes por coluna antes do tratamento:")
print(df.isna().sum())

cat_cols = df.select_dtypes(include="object").columns
for col in cat_cols:
    df[col] = df[col].fillna("IGNORADO")

num_cols_fill = [
    "mortos",
    "feridos",
    "feridos_leves",
    "feridos_graves",
    "ilesos",
    "ignorados",
]
for col in num_cols_fill:
    if col in df.columns:
        df[col] = df[col].fillna(0)

print("\nValores ausentes após tratamento:")
print(df.isna().sum().sum())

# %% [markdown]
# ### 7. Criação de variáveis

# %%
df["ano"] = df["data_inversa"].dt.year
df["mes"] = df["data_inversa"].dt.month
df["trimestre"] = df["data_inversa"].dt.quarter
df["dia_semana"] = df["data_inversa"].dt.day_name()
df["dia_semana_num"] = df["data_inversa"].dt.dayofweek
df["fim_de_semana"] = df["dia_semana_num"].isin([5, 6]).astype(int)


# %%
def get_shift(hora):
    if pd.isna(hora):
        return "IGNORADO"
    if 0 <= hora <= 5:
        return "MADRUGADA"
    if 6 <= hora <= 11:
        return "MANHA"
    if 12 <= hora <= 17:
        return "TARDE"
    return "NOITE"


df["turno"] = df["hora"].apply(get_shift)


# %%
def get_time_range(hora):
    if pd.isna(hora):
        return "IGNORADO"
    if 0 <= hora <= 6:
        return "00h-06h"
    if 7 <= hora <= 12:
        return "07h-12h"
    if 13 <= hora <= 18:
        return "13h-18h"
    return "19h-23h"


df["faixa_horaria"] = df["hora"].apply(get_time_range)

# %%
df["total_vitimas"] = df["mortos"] + df["feridos"]
df["acidente_grave"] = np.where((df["mortos"] > 0) | (df["feridos_graves"] > 0), 1, 0)
df["indice_gravidade"] = df["mortos"] / df["total_vitimas"].replace(0, np.nan)
df["br_formatada"] = "BR-" + df["br"].astype(str).str.zfill(3)
df["chave_localidade"] = df["uf"].astype(str) + "_" + df["municipio"].astype(str)

print("Variáveis derivadas criadas:")
df[
    [
        "total_vitimas",
        "acidente_grave",
        "indice_gravidade",
        "br_formatada",
        "chave_localidade",
    ]
].head()

# %% [markdown]
# ### 8. Criação da variável-alvo

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)

# %%
print("Distribuição da variável acidente_fatal:")
print(df["acidente_fatal"].value_counts())

# %%
print("\nPercentual de acidentes fatais:")
print(df["acidente_fatal"].value_counts(normalize=True) * 100)

# %% [markdown]
# ### 9. Verificações de qualidade

# %%
print("=" * 60)
print("VERIFICAÇÕES DE QUALIDADE")
print("=" * 60)

print(f"\nQuantidade de linhas: {df.shape[0]}")
print(f"Quantidade de colunas: {df.shape[1]}")
print(f"Quantidade de acidentes fatais: {df['acidente_fatal'].sum()}")
print(f"Taxa de fatalidade: {(df['acidente_fatal'].mean() * 100):.2f}%")
print(f"Total de mortos: {df['mortos'].sum()}")
print(f"Total de feridos: {df['feridos'].sum()}")

violations = df[
    ((df["mortos"] >= 1) & (df["acidente_fatal"] != 1))
    | ((df["mortos"] == 0) & (df["acidente_fatal"] != 0))
]
print(f"\nAusência de erros na variável acidente_fatal: {len(violations)} violações")

# %% [markdown]
# ### 10. Data Leakage

# %%
print("=" * 60)
print("PREVENÇÃO DE DATA LEAKAGE")
print("=" * 60)

# %% [markdown]
# ### DISCUSSÃO SOBRE DATA LEAKAGE:
#
# As seguintes variáveis NÃO devem ser utilizadas como features para prever
# acidente_fatal, pois geram data leakage:
#
# 1. mortos - Esta variável é diretamente usada para criar o target acidente_fatal.
#    Usá-la como feature seria usar a resposta para prever a resposta.
#
# 2. feridos - Embora não seja usada diretamente no target, está fortemente
#    correlacionada com a gravidade do acidente e pode vazar informação sobre
#    o desfecho.
#
# 3. total_vitimas - Esta variável é derivada de mortos + feridos, portanto
#    contém informação direta sobre o target.
#
# 4. indice_gravidade - Esta variável é calculada usando mortos, que é a base
#    para definir acidente_fatal.
#
# CONCLUSÃO: Para evitar data leakage, essas variáveis devem ser excluídas
# do conjunto de features antes de treinar qualquer modelo preditivo.

# %%
leakage_vars = ["mortos", "feridos", "total_vitimas", "indice_gravidade"]
print(f"\nVariáveis que causam data leakage: {leakage_vars}")
print("Essas variáveis devem ser removidas antes de treinar modelos preditivos.")

# %%
# Validação final
assert len(violations) == 0, "Existem inconsistências na variável acidente_fatal!"
print("\n✓ Verificação final: Dados consistentes!")

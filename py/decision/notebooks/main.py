# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %%
ROOT = Path(".")
DIRS = ["data"]

for directory in DIRS:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

RAW_FILE = Path("../data/acidentes2025.csv")
df = pd.read_csv(RAW_FILE, sep=";", encoding="latin1", low_memory=False)

# %% [markdown]
# ### 1. Identificação
# Desejamos identificar quais fatores são associados a uma maior proporção de acidentes fatais.
# A varíavel de interesse será acidente_fatal, variável booleana que é 1 quando há fatalidades em um acidente, e 0 quando não
# Ocorrência: Quantidade de acidentes
# Gravidade: Nível do acidente, quantidade de envolvidos, mortos, feridos, etc.
# Através da análise de fatalidades em acidentes, seria possível prever quando ocorrerá fatalidades, dependendo de lugar, hora, clima, etc.

# %% [markdown]
# ### 2. Auditoria rápida da base

# %%
df.shape

# %%
df.info()

# %%
df.dtypes

# %%
df.isna().sum()

# %%
print(df.duplicated(keep=False).sum())

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)

# %%
print(df["acidente_fatal"].value_counts())

# %% [markdown]
# ### Interpretação
#
# Não há linhas duplicadas no dataset: Isso indica que cada registro é único — coerente com `id` atuando como chave primária do acidente.
# Dados ausentes concentrados apenas em colunas administrativas: As variáveis centrais do problema têm 0 valores ausentes.
# A ausência se restringe a campos administrativos/operacionais: classificacao_acidente, regional, delegacia e uop.
# Como essas colunas não entram diretamente na definição da variável-alvo acidente_fatal nem nos fatores preditivos principais, a cobertura para a análise é praticamente completa.

# %% [markdown]
# ### 3. Crie sua hipótese
# Hipotéses:
# A maioria dos acidentes ocorre em céu claro
# O tipo de acidente mais grave é o Atropelamento

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

# %%
df.info()

# %%
from logging import fatal
from operator import index
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
#
# #### Hipotéses:
# A maioria dos acidentes ocorrem a tarde
# O tipo de acidente mais grave é o atropelamento

# %% [markdown]
# ### 5. Engenharia de variável

# %%
df["hora"] = pd.to_datetime(df["horario"], format="%H:%M:%S", errors="coerce").dt.hour


# %%
def def_faixa_horaria(hour):
    if pd.isna(hour):
        return "Ignorado"
    elif 6 <= hour < 12:
        return "Manhã (6h-12h)"
    elif 12 <= hour < 18:
        return "Tarde (12h-18h)"
    elif 18 <= hour < 24:
        return "Noite (18h-24h)"
    else:
        return "Madrugada (0h-6h)"


# %%
# Nova variável
df["faixa_horaria"] = df["hora"].apply(def_faixa_horaria)

# %% [markdown]
# ### Explicação
#
# Nova coluna:
# hora e faixa_horaria
#
# Explicação:
# hora: Criada ao extrair a hora da coluna horario pela função dt.hour
# faixa_horaria: Agrupa os horário por faixas, feito ao criar uma função que
# retorna uma string com sua faixa e aplica-a a cada linha.
#
# Nova coluna hora existe para o agrupamento em faixas

# %% [markdown]
# ### 6. Análise da hipotese 1
# A maioria dos acidentes ocorre em céu claro
# O tipo de acidente mais grave é o Atropelamento


# %%
def analyze(df, col):
    return (
        df.groupby(col)
        .agg(
            total_acidentes=("acidente_fatal", "count"),
            acidentes_fatais=("acidente_fatal", "sum"),
            taxa_fatalidade=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
        )
        .reset_index()
    )


# %%
faixa_analysis = analyze(df, "faixa_horaria").sort_values(
    "faixa_horaria", ascending=False
)

# %%
print(faixa_analysis.to_string(index=False))

# %%
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(
    faixa_analysis["faixa_horaria"], faixa_analysis["total_acidentes"], color="tab:blue"
)
ax.set_xlabel("Faixa Horária")
ax.set_ylabel("Total de Acidentes")
ax.set_title("Total de Acidentes por Faixa Horária")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 6. Análise da hipotese 2

# %%
type_analysis = analyze(df, "tipo_acidente").sort_values(
    "taxa_fatalidade", ascending=False
)

# %%
print(type_analysis.to_string(index=False))

# %%
fig, ax = plt.subplots(figsize=(9, 6))
y = np.arange(len(type_analysis))
ax.barh(y, type_analysis["taxa_fatalidade"], color="tab:red")
ax.set_yticks(y)
ax.set_yticklabels(type_analysis["tipo_acidente"])
ax.set_xlabel("Taxa de Fatalidade (%)")
ax.set_title("Taxa de Fatalidade por Tipo de Acidente")
ax.invert_yaxis()
plt.tight_layout()
plt.show()

# %% [markdown]
# ### Interpretação
#
# A tarde é a faixa horária com mais acidentes, porém possui a menor taxa de fatalidade.
# A madrugada é a faixa horária com a maior taxa de acidentes fatais, mesmo
# possuindo a menor qtd de acidentes e acidentes fatais.

# %% [markdown]
# ### 8. Cruzamento de variáveis
# tipo_pista x condicao_metereologica


# %%
tipo_condicao_analysis = (
    df.groupby(["tipo_pista", "condicao_metereologica"])
    .agg(
        acidentes_fatais=("acidente_fatal", "sum"),
    )
    .reset_index()
).sort_values("acidentes_fatais", ascending=False)

# %%
print(tipo_condicao_analysis.to_string(index=False))

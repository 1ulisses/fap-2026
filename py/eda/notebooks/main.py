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

# %% [markdown]
# 1. Problema analítico

# %% [markdown]
# # Problema
# Influência das Condições Meteorológicas

# %% [markdown]
# 2. Pergunta central

# %% [markdown]
# # Pergunta
# As condições meteorológicas adversas aumentam a probabilidade de ocorrência de
# acidentes, ou alteram fundamentalmente o perfil de gravidade e letalidade das
# ocorrências?

# %% [markdown]
# 3. Hipóteses iniciais

# %% [markdown]
# # Hipoteses
# - A taxa de letalidade em dias de céu claro é superior à taxa de letalidade em dias
# de chuva.
# - Acidentes com neblina têm a maior taxa de letalidade entre todas as condições
# climáticas.
# - A letalidade em condições adversas (chuva/neblina) à noite é desproporcionalmente
# maior do que durante o dia sob o mesmo clima.
# - Acidentes por saída de pista e capotamento são estatisticamente mais frequentes
# em pistas secas do que em pistas molhadas.

# %% [markdown]
# 4. Estratégia de investigação
# visão geral -> qualidade -> distribuição -> comparação -> associação -> combinação de fatores -> validação dos achados -> hipóteses.

# %% [markdown]
# 5. Conhecimento e validação da base

# %%
df.head()

# %%
lines, columns = df.shape
print(f"Linhas: {lines}, Colunas: {columns}")

# %%
print(df.info())

# %%
print(df.dtypes)

# %%
print(df.columns)

# %%
# Colunas com valores nulos:
# classificacao_acidente: 1
# regional: 2
# delegacia: 22
# uop: 38
print(df.isna().sum())

# %%
duplicates = df.duplicated(keep=False)
print(duplicates.sum())

# %%
unique = df.nunique().sort_values(ascending=False)
unique.head(15)

# %% [markdown]
# 6. Linha de base

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
print(df["feridos"].sum())

# %%
# Percentual de acidentes fatais
print(df["acidente_fatal"].sum() / len(df) * 100)

# %%
# Taxa de letalidade operacional
print(df["mortos"].sum() / (df["feridos"].sum() + df["mortos"].sum()) * 100)

# %% [markdown]
# 7. Exploração inicial
#

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)


# %%
def analyze(df, col):
    return (
        df.groupby(col)
        .agg(
            total_acidentes=("acidente_fatal", "count"),
            taxa_total_acidentes=(
                "acidente_fatal",
                lambda x: round(x.count() / len(df) * 100, 2),
            ),
            total_feridos=("feridos", "sum"),
            acidentes_fatais=("acidente_fatal", "sum"),
            taxa_fatalidade=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
        )
        .reset_index()
    )


# %%
clima_analysis = analyze(df, "condicao_metereologica").sort_values(
    "total_acidentes", ascending=False
)
clima_analysis

# %%
df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
df["mes"] = df["data_inversa"].dt.month

# %% [markdown]
# 8. Principais padrões encontrados
#
# Escolhemos investigar a variável condicao_metereologica primeiro porque ela é o
# núcleo do nosso problema analítico. Antes de cruzar o clima com infraestrutura ou
# comportamento, precisamos entender o efeito principal: o clima atua como um
# multiplicador de volume de acidentes ou como um agravante de letalidade em relação
# à média global?

# %%
# Neblina com maior taxa de fatalidade
clima_analysis = clima_analysis.sort_values("taxa_fatalidade", ascending=False)
clima_analysis

# %% [markdown]
# # Hipoteses respondidas
# - A taxa de letalidade em dias de céu claro é superior à taxa de letalidade em dias de chuva:
# Confirmada com base em volume e proporção.
# A categoria céu claro possui 46.375 acidentes e taxa de fatalidade de 7.37%. A
# categoria chuva possui 6.438 acidentes e taxa de 6.24%.
# A diferença não se apoia apenas na taxa. Céu claro tem volume muito maior, o que
# torna a estimativa mais estável. Além disso, o impacto absoluto é muito superior:
# são 3.419 acidentes fatais sob céu claro contra 402 sob chuva.
#
# - Acidentes com neblina têm a maior taxa de letalidade entre todas as condições climáticas:
# Confirmada, mas com ressalva de volume.
# A categoria nevoeiro/neblina possui a maior taxa da tabela: 10.85%. Porém, o
# volume é muito menor: apenas 553 acidentes.
# A taxa alta merece atenção porque indica uma condição de risco severo, provavelmente
# associada à baixa visibilidade e colisões em cadeia. No entanto, ela não pode ser
# interpretada como o principal fator de mortalidade da base, porque o volume
# absoluto é pequeno se comparado ao céu claro.
# Se essa categoria tivesse apenas 2 acidentes e 1 fatal, a taxa de 50% não deveria ser
# usada como evidência. Como possui 553 acidentes, já há volume mínimo para análise
# exploratória, mas ainda assim a estimativa tem incerteza maior.

# %% [markdown]
# 9. Análises bivariadas selecionadas

# %% [markdown]
# 10. Investigação de combinações

# %% [markdown]
# 11. Teste dos achados

# %% [markdown]
# 12. Anomalias e limitações

# %% [markdown]
# 13. Três principais descobertas

# %% [markdown]
# 14. Hipóteses geradas

# %% [markdown]
# 15. Próximas investigações

# %% [markdown]
# 16. Conclusão

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

ANALYTICAL_FILE = Path("./data/acidentes2025_analitica.csv")
df = pd.read_csv(ANALYTICAL_FILE, sep=";", encoding="latin1", low_memory=False)


def analyze(df, col):
    return (
        df.groupby(col)
        .agg(
            total_acidentes=("acidente_fatal", "count"),
            acidentes_fatais=("acidente_fatal", "sum"),
            taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
        )
        .reset_index()
    )


# %% [markdown]
# ---
# ## Questão 1: Quando os acidentes acontecem?
#
# Existe algum padrão temporal que indique períodos com maior ocorrência de acidentes? Esse padrão muda quando analisamos acidentes fatais em vez de todos os acidentes?

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)
df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
df["mes"] = df["data_inversa"].dt.month
df["mes_nome"] = df["data_inversa"].dt.month_name()

mes_analysis = analyze(df, "mes")

mes_analysis = mes_analysis.sort_values("total_acidentes", ascending=False)
mes_map = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}
mes_analysis["mes_nome_abrev"] = mes_analysis["mes"].map(mes_map.get)

print(mes_analysis.to_string(index=False))

# %%
df["dia_util"] = df["dia_semana"].apply(
    lambda x: (
        0
        if x in ["sábado", "domingo", "Sábado", "Domingo"] or "áb" in x or "ingo" in x
        else 1
    )
)
dia_analysis = analyze(df, "dia_util")

dia_map = {0: "Fim de Semana", 1: "Dia Útil"}
dia_analysis["tipo_dia"] = dia_analysis["dia_util"].map(dia_map.get)
dia_analysis = dia_analysis[
    ["tipo_dia", "total_acidentes", "acidentes_fatais", "taxa_fatalidade_pct"]
]
dia_analysis = dia_analysis.set_index("tipo_dia")

print(dia_analysis.to_string())
# %%
dia_semana_analysis = analyze(df, "dia_semana")
dia_semana_analysis = dia_semana_analysis.sort_values(
    "total_acidentes", ascending=False
)
print(dia_semana_analysis.to_string())

# %% [markdown]
# **Interpretação e Conclusão:**
#
# Meses associados a feriados, férias, mudanças sazonais e maior volume de tráfego (Dez., Out., Ago. e Jul.) possuem maior taxa de acidentes e uma qtd. elevada de acidentes fatais
# Finais de semana, embora possuam menor volume de acidentes, possuem uma taxa de fatalidade mais elevada comparado aos dias úteis.
# Dias no final da semana possuem maior volume de acidentes, acidentes fatais e uma taxa mais elevada de fatalidade.
# Dias úteis próximos a fins de semana possuem maior volume de acidentes e acidentes fatais.

# %% [markdown]
# ---
# ## Questão 2: Frequência não é fatalidade
#
# O tipo de acidente mais frequente também é aquele com maior proporção de acidentes fatais?

# %%
tipo_analysis = analyze(df, "tipo_acidente")
uf_analysis = analisar_acidentes(df, "uf")

uf_analysis = uf_analysis.sort_values("total_acidentes", ascending=False)

print(uf_analysis.to_string(index=False))

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.bar(uf_analysis["uf"], uf_analysis["total_acidentes"])
plt.xlabel("UF")
plt.ylabel("Total de Acidentes")
plt.title("Total de Acidentes por UF")
plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## Questão 3: Existe um horário mais crítico?
#
# O horário com maior número de acidentes também apresenta maior taxa de fatalidade?

# %%
df["hora"] = pd.to_datetime(df["horario"], format="%H:%M:%S", errors="coerce").dt.hour


def definir_faixa_horaria(hora):
    if pd.isna(hora):
        return "Ignorado"
    elif 6 <= hora < 12:
        return "Manhã (6h-12h)"
    elif 12 <= hora < 18:
        return "Tarde (12h-18h)"
    elif 18 <= hora < 24:
        return "Noite (18h-24h)"
    else:
        return "Madrugada (0h-6h)"


df["faixa_horaria"] = df["hora"].apply(definir_faixa_horaria)


def definir_turno(fase_dia):
    if pd.isna(fase_dia):
        return "Ignorado"
    elif "dia" in fase_dia.lower():
        return "Dia"
    elif (
        "noite" in fase_dia.lower()
        or "anoitecer" in fase_dia.lower()
        or "amanhecer" in fase_dia.lower()
    ):
        return "Noite"
    else:
        return fase_dia


df["turno"] = df["fase_dia"].apply(definir_turno)

# %%
hora_analysis = analyze(df, "hora")
hora_analysis = hora_analysis.sort_values("total_acidentes", ascending=False)
print(hora_analysis.to_string(index=False))

# %%
turno_analysis = analyze(df, "turno")
turno_analysis = turno_analysis.sort_values("total_acidentes", ascending=False)
print(turno_analysis.to_string(index=False))

# %%
faixa_analysis = analyze(df, "faixa_horaria")

faixa_analysis = faixa_analysis.sort_values("total_acidentes", ascending=False)
print(faixa_analysis.to_string(index=False))

# %% [markdown]
# ---
# ## Questão 4: O problema está concentrado em algumas regiões?
#
# Os estados que concentram mais acidentes são os mesmos que apresentam maior proporção de acidentes fatais?

# %%
uf_analysis = analyze(df, "uf")

uf_analysis = uf_analysis.sort_values("total_acidentes", ascending=False)
print(uf_analysis.to_string(index=False))

# %% [markdown]
# ---
# ## Questão 5: Condições da via
#
# tipo_pista x condicao_metereologica

tipo_condicao_analysis = analyze(df, ["tipo_pista", "condicao_metereologica"])

tipo_condicao_analysis = tipo_condicao_analysis.sort_values(
    "total_acidentes", ascending=False
)
print(tipo_condicao_analysis.to_string(index=False))

# %% [markdown]
# ---
# ## Questão 6: Quem está associado aos acidentes mais graves?
#
# O aumento da quantidade de veículos ou pessoas envolvidas parece estar associado a uma maior gravidade dos acidentes?


# %%
def def_faixa_pessoas(pessoas):
    if pd.isna(pessoas) or pessoas < 1:
        return "Ignorado"
    elif pessoas < 4:
        return "1-3 Pessoas"
    elif pessoas < 7:
        return "4-6 Pessoas"
    elif pessoas < 11:
        return "7-10 Pessoas"
    else:
        return "+10 Pessoas"


df["faixa_pessoas"] = df["pessoas"].apply(def_faixa_pessoas)

faixa_pessoas_analysis = analyze(df, "faixa_pessoas")

faixa_pessoas_analysis = faixa_pessoas_analysis.sort_values(
    "total_acidentes", ascending=False
)

print(faixa_pessoas_analysis.to_string(index=False))

# %% [markdown]
# ---
# ## Questão 7: Três gráficos e uma história
#
# UF
# Qual história os três gráficos contam quando analisados em conjunto?

# %%
uf_analysis = analyze(df, "uf")
uf_analysis = (
    uf_analysis.sort_values("total_acidentes", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

plt.figure(figsize=(10, 5))
plt.bar(uf_analysis["uf"], uf_analysis["total_acidentes"], color="skyblue")
plt.xlabel("UF")
plt.ylabel("Total de Acidentes")
plt.title("Total de Acidentes por UF")
plt.tight_layout()
plt.show()

# %%
uf_condicao_analysis = analyze(df, ["uf", "condicao_metereologica"])
uf_condicao_analysis = (
    uf_condicao_analysis.sort_values("total_acidentes", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

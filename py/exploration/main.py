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
tipo_analysis = tipo_analysis.sort_values("total_acidentes", ascending=False).head(5)

print(tipo_analysis.to_string(index=False))

# %% [markdown]
# **Interpretação e Conclusão:**
#
# Não. O tipo de acidente mais frequente é Colisão traseira (14.360 casos), mas ele possui uma taxa de fatalidade de 4,31%.
# Frequência e letalidade são dimensões distintas na segurança viária. Colisões traseiras ocorrem em grande volume (geralmente ligadas a trânsito intenso, baixa velocidade relativa ou distração), mas tendem a ser menos letais por ocorrência.

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
# **Interpretação e Conclusão:**
#
# Não. O horário com maior número absoluto de acidentes é às 18h (5.398 acidentes), mas sua taxa de fatalidade é de 7,04%. A maior taxa de fatalidade ocorre às 3h da manhã, com 13,70% (quase o dobro).
# Turno: O Dia concentra mais acidentes (40.375), mas a Noite é muito mais letal (9,83%).
# Faixa Horária: A Tarde lidera em volume (22.302), mas a Madrugada possui a maior taxa de fatalidade (12,10%).

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
# **Interpretação e Conclusão:**
#
# Não.
# Os estados que concentram o maior volume absoluto de acidentes (Sul e Sudeste) não são os mesmos que apresentam a maior proporção de acidentes fatais.
# Os estados com as maiores taxas de letalidade estão localizados principalmente nas regiões Norte e Nordeste, que possuem volumes totais de acidentes muito menores.
#
# Minas Gerais (MG):
# Dados: 9.570 acidentes (1º lugar) e taxa de fatalidade de 6,76%.
# Análise: MG possui a maior malha rodoviária federal do país e um tráfego intenso. O alto volume de acidentes reflete a quantidade de veículos nas estradas.
#
# Santa Catarina (SC):
# Dados: 8.186 acidentes (2º lugar) e taxa de fatalidade de 4,57%.
# Análise: SC tem um volume muito alto de acidentes, mas a taxa de fatalidade é uma das mais baixas entre os principais estados.
# Isso pode indicar que a maioria dos acidentes em SC são colisões de menor gravidade (como engarrafamentos ou colisões traseiras).
#
# Pará (PA) - Baixo volume, altíssima letalidade:
# Dados PA: 1.117 acidentes e taxa de fatalidade de 17,28% (2º lugar).
# Análise: Este estado têm volume de acidentes muito baixo (cerca de 1/8 do volume de MG), mas as taxas de fatalidade são alarmantes (quase 3 vezes maiores que a média nacional).

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
# **Interpretação e Conclusão:**
#
# Independentemente da condição meteorológica, acidentes em pista simples apresentam taxa de fatalidade muito maior do que acidentes em pista dupla ou múltipla.
# A maior parte dos acidentes ocorre em condições boas ou normais, como céu claro.
# Mesmo em condições boas, a taxa de fatalidade é alta em pista simples.
# Pistas duplas e múltiplas apresentam taxas de fatalidade menores na maioria das condições meteorológicas.
# Condições como nevoeiro/neblina aumentam a taxa de fatalidade.
#
# Uma possível explicação é que pistas simples concentram mais situações de conflito grave, como:
# colisões frontais;
# ultrapassagens mal executadas;
# tráfego em sentidos opostos sem separação física;
#
# Já pistas duplas ou múltiplas tendem a ter:
# separação física dos sentidos;
# menor chance de colisão frontal;
# maior capacidade de tráfego;
#
# Não é possível afirmar causalidade apenas com essa análise porque os dados são observacionais e agregados.
# Existem várias variáveis de confusão que podem influenciar o resultado, como:
# volume real de tráfego por tipo de pista;
# velocidade média dos veículos;
# qualidade do pavimento;

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
# **Interpretação e Conclusão:**
#
# Sim.
# 1-3 Pessoas: Taxa de fatalidade de 5,98% (representa a esmagadora maioria dos acidentes, tipicamente envolvendo um ou dois veículos de passeio).
# 4-6 Pessoas: A taxa dobra para 11,97%.
# 7-10 Pessoas: A taxa sobe para 16,69%.
# +10 Pessoas: A taxa atinge 24,31%, sendo mais de quatro vezes maior que a da primeira faixa.
#
# O aumento na gravidade não é causado pelo número de pessoas em si, mas pelo tipo de evento necessário para envolver tantas pessoas. Acidentes com muitas pessoas geralmente indicam:
# Envolvimento de transporte coletivo ou fretamento;
# Acidentes de grande magnitude: Engavetamentos, capotamentos de veículos grandes;
# Viés estatístico: Quanto mais ocupantes em um único veículo sinistrado, maior a probabilidade matemática de que pelo menos uma vítima fatal seja registrada.

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
uf_condicao_analysis = uf_condicao_analysis.sort_values(
    "total_acidentes", ascending=False
).reset_index(drop=True)

uf_pivot = uf_condicao_analysis.pivot(
    index="uf", columns="condicao_metereologica", values="total_acidentes"
).fillna(0)

plt.figure(figsize=(14, 6))
uf_pivot.plot(kind="bar", stacked=True, figsize=(14, 6))
plt.xlabel("UF")
plt.ylabel("Total de Acidentes")
plt.title("Total de Acidentes por UF e Condição Meteorológica")
plt.tight_layout()

# %%
uf_analysis = analyze(df, "uf")
uf_analysis = uf_analysis.sort_values("taxa_fatalidade_pct", ascending=False)

plt.figure(figsize=(10, 5))
plt.bar(uf_analysis["uf"], uf_analysis["taxa_fatalidade_pct"], color="red")
plt.xlabel("UF")
plt.ylabel("Taxa de fatalidade")
plt.title("Taxa de fatalidade por UF")
plt.tight_layout()
plt.show()

# %% [markdown]
# **Interpretação e Conclusão:**
#
# Analisado as UFs que ocorreram os acidentes e suas condições meteorológicas.
# MG, SC e PR possuem a maior qtd. de acidentes.
# Estados com a menor qtd de acidentes possuem a maioria dos acidentes ocorridos em céu claro.
# MG, SC e PR possuem um maior percentual de acidentes com condição meteorológica de chuva ou neblina.
# MA, PA e RR, estados com a maior taxa de fatalidade, possuem a grande maioria de seus acidentes ocorridos em céu claro e possuem menor qtd. de acidentes sob chuva ou neblina.
#
# Sul e Sudeste concentram maior volume de acidentes, muitas vezes associados a tráfego intenso e condições meteorológicas adversas, mas com menor taxa de fatalidade.
# Já alguns estados do Norte e Nordeste têm menos acidentes, porém acidentes muito mais fatais, mesmo ocorrendo majoritariamente em céu claro.
# MG, SC e PR têm muitos acidentes, mas possivelmente com menor letalidade média, talvez por:
# mais trechos duplicados;
# maior presença de socorro;
# mais fiscalização;
#
# MA, PA e RR têm menos acidentes, mas acidentes mais graves, possivelmente por:
# mais pistas simples;
# longos trechos isolados;
# maior velocidade média em trechos vazios;

# %% [markdown]
# ---
# ## Questão 8: A descoberta do grupo
#
# condicao_metereologica X total_acidentes X taxa_fatalidade_pct
# 1. Pergunta
# Acidentes sob chuva ou neblina são proporcionalmente mais fatais do que em condições normais?
# 2. Hipótese
# Esperava-se maior taxa de fatalidade em chuva, neblina ou pista molhada, por causa da redução de visibilidade e aderência.
# 5. Conclusão
# Não, possuem menor taxa de fatalidade que em condições normais.
# 6. Limitação
# A variável meteorológica é ampla e não captura intensidade da chuva, visibilidade real ou condição da pista no momento exato do acidente.

# %%
condicao_analysis = analyze(df, "condicao_metereologica")
condicao_analysis = condicao_analysis.sort_values("total_acidentes", ascending=False)

# 3. Análise
print(condicao_analysis.to_string(index=False))

fig, ax1 = plt.subplots(figsize=(12, 6))

color_bar = "steelblue"
ax1.set_xlabel("Condição Meteorológica", fontsize=11)
ax1.set_ylabel("Total de Acidentes", color=color_bar, fontsize=11)
ax1.bar(
    condicao_analysis["condicao_metereologica"],
    condicao_analysis["total_acidentes"],
    color=color_bar,
    alpha=0.8,
)
ax1.tick_params(axis="y", labelcolor=color_bar)
ax1.tick_params(axis="x", rotation=45, labelbottom=True)

ax2 = ax1.twinx()
color_line = "crimson"
ax2.set_ylabel("Taxa de Fatalidade (%)", color=color_line, fontsize=11)
ax2.plot(
    condicao_analysis["condicao_metereologica"],
    condicao_analysis["taxa_fatalidade_pct"],
    color=color_line,
    marker="o",
    linewidth=2.5,
    markersize=8,
)
ax2.tick_params(axis="y", labelcolor=color_line)

for i, v in enumerate(condicao_analysis["taxa_fatalidade_pct"]):
    ax2.text(
        i,
        v + 0.3,
        f"{v}%",
        ha="center",
        va="bottom",
        color=color_line,
        fontweight="bold",
        fontsize=10,
    )

plt.title(
    "Volume de Acidentes vs. Taxa de Fatalidade por Condição Meteorológica",
    fontsize=13,
    fontweight="bold",
    pad=15,
)
fig.tight_layout()
# 4. Evidência
plt.show()

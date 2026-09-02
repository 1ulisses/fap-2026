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
#


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
    "total_acidentes", ascending=False
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

# %% [markdown]
# ### 9. Painel de evidências

# %%
road_analysis = analyze(df, "tipo_pista").sort_values(
    "total_acidentes", ascending=False
)

# %%
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(road_analysis["tipo_pista"], road_analysis["total_acidentes"], color="royalblue")
ax.set_xlabel("Tipo de pista")
ax.set_ylabel("Total de Acidentes")
ax.set_title("Total de Acidentes por tipo de pista")
plt.tight_layout()
plt.show()

# %%
road_type_analysis = (
    df.groupby(["tipo_pista", "tipo_acidente"]).size().reset_index(name="total")
)

# %%
road_type_analysis["pct"] = road_type_analysis.groupby("tipo_pista")["total"].transform(
    lambda x: round(x / x.sum() * 100, 2)
)

road_type_analysis = road_type_analysis.sort_values(
    ["tipo_pista", "total"], ascending=[False, False]
)

# %%
print(road_type_analysis.to_string(index=False))

# %%
pivot = road_type_analysis.pivot_table(
    index="tipo_pista", columns="tipo_acidente", values="total", fill_value=0
)
fig, ax = plt.subplots(figsize=(10, 6))
pivot.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
ax.set_xlabel("Tipo de pista")
ax.set_ylabel("Total de Acidentes")
ax.set_title("Composição de Tipo de Acidente por Tipo de Pista")
ax.legend(title="Tipo de Acidente", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 10. Anomalia encontrada

# %%
top10_municipios = df.groupby("municipio").size().nlargest(10).index.tolist()
df_top10 = df[df["municipio"].isin(top10_municipios)]

municipio_analysis = analyze(df_top10, "municipio").sort_values(
    "total_acidentes", ascending=False
)

print(municipio_analysis.to_string(index=False))

# %% [markdown]
# ### Explicação
# Brasília possui ambamente a maior taxa de fatalidade e o maior total de acidentes.
# Isto é incomum para um município de capital, que geralmente tem uma taxa de fatalidade mais baixa e um total de acidentes mais moderado.

# %% [markdown]
# ### 11. Tentativa de refutar a hipótese
# O atropelamento de pedestres ainda é o acidente mais grave em relação ao cenário urbano ou rural?
# Sim: Urbano
# Não: Rural

# %%
type_ground_analysis = analyze(df, ["tipo_acidente", "uso_solo"]).sort_values(
    ["uso_solo", "taxa_fatalidade"], ascending=[False, False]
)

print(type_ground_analysis.to_string(index=False))

# %% [markdown]
# ### Explicação
# O atropelamento de pedestres so é o tipo de acidente mais grave em relação ao cenário rural.
# No cenário urbano, o acidente mais grave é a colisão com objetos.

# %% [markdown]
# ### 12. Frequência × Fatalidade
# Faixa horária

# %%
print(faixa_analysis.to_string(index=False))

# %%
faixa_analysis = faixa_analysis.sort_values("acidentes_fatais", ascending=False)
print(faixa_analysis.to_string(index=False))

# %% [markdown]
# ### 13. Recomendações

# %% [markdown]
# ### Recomendação 1
#
# #### Evidência
# Acidentes em pista simples e em área rural (uso_solo = Não) apresentam taxas
# de fatalidade drasticamente superiores. A colisão frontal em área rural possui
# 35,13% de taxa de fatalidade (contra 15,65% na área urbana). Além disso, a
# pista simples concentra 12,20% de colisões frontais, enquanto pistas duplas e
# múltiplas apresentam apenas cerca de 1,30% a 1,45% desse tipo de acidente.
#
# #### Interpretação
# A ausência de separação física entre fluxos opostos (pista simples) e a falta de
# infraestrutura de áreas urbanas (como iluminação e proximidade de hospitais)
# amplificam a gravidade dos eventos. A colisão frontal em alta velocidade em
# trechos rurais é o principal motor de óbitos, transformando falhas humanas em
# tragédias.
#
# #### Recomendação
# Priorizar investimentos na duplicação de trechos rurais de pista simples com alto
# histórico de colisões frontais e saídas de pista. Nos trechos onde a duplicação
# for financeiramente ou geograficamente inviável a curto prazo, instalar barreiras
# físicas centrais (como cabos de aço ou barreiras de concreto) para impedir a
# invasão da pista oposta e melhorar a sinalização refletiva.
#
# #### Cuidado
# A base de dados não informa o Volume Diário Médio (VDM) de veículos nem a
# velocidade média permitida na via. A duplicação de trechos com baixíssimo fluxo
# de veículos pode não apresentar um retorno sobre o investimento (ROI) adequado em
# termos de vidas salvas por milhão de reais investidos.

# %% [markdown]
# ### Recomendação 2
#
# #### Evidência
# A faixa horária da Madrugada (0h-6h) apresenta a maior taxa de fatalidade (12,10%),
# seguida pela Noite (9,13%), apesar de concentrarem os menores volumes absolutos
# de acidentes (8.907 e 20.461, respectivamente, contra mais de 20.000 nos demais
# períodos).
#
# #### Interpretação
# A alta letalidade noturna indica que os acidentes nesses horários envolvem maior
# energia cinética (excesso de velocidade em pistas vazias), fadiga, sonolência ou
# ingestão de álcool. A baixa visibilidade e o menor tempo de reação resultam em
# impactos mais severos, como saídas de leito carroçável e colisões frontais, em
# vez de colisões traseiras de baixa velocidade comuns durante o dia.
#
# #### Recomendação
# Realocar o efetivo de fiscalização e as operações de blitz para os períodos
# noturnos e de madrugada, com foco rigoroso em testes de alcoolemia e combate à
# fadiga (especialmente para motoristas profissionais de carga). Em paralelo,
# investigar a instalação de tachões refletivos, sonorizadores e iluminação
# inteligente em curvas e trechos críticos para mitigar saídas de pista causadas
# por sonolência.
#
# #### Cuidado
# Os dados não confirmam a causa raiz comportamental (álcool, sono ou velocidade).
# A alta letalidade noturna pode estar concentrada em um perfil específico (ex:
# transporte de carga pesada) que exige análise cruzada com a variável de tipo de
# veículo e laudos de alcoolemia para evitar o desperdício de recursos operacionais
# em fiscalizações ineficazes.

# %% [markdown]
# ### 14. Limitações
#
# ## Decisão Prioritária: Onde Agir Primeiro
#
# ### Resposta Direta
#
# Devemos agir primeiro em **trechos rurais de pista simples**,
# durante o período da **madrugada (0h às 6h)**,
# focando na prevenção de **colisões frontais** e **atropelamentos de pedestres**.
#
# ### Justificativa com Dados
#
# **1. Local: Área rural em pista simples**
#
# Os dados mostram que a combinação "pista simples + área rural"
# é a mais letal do nosso dataset:
# - Colisão frontal em área rural: **35,13% de taxa de fatalidade**
# - Atropelamento de pedestre em área rural: **40,05% de taxa de fatalidade**
# Para comparação:
# - Colisão frontal em área urbana: 15,65% (menos da metade)
# - Atropelamento em área urbana: 22,35%
# Pista simples concentra 12,20% de colisões frontais,
# enquanto pista dupla tem apenas 1,30%.
# A ausência de separação física entre fluxos opostos
# é o principal fator estrutural de letalidade.
#
# **2. Período: Madrugada e Noite**
#
# - Madrugada (0h-6h): **12,10% de taxa de fatalidade**
# - Noite (18h-24h): **9,13% de taxa de fatalidade**
# - Tarde (12h-18h): 5,53%
# - Manhã (6h-12h): 4,93%
# A madrugada tem o menor volume de acidentes (8.907),
# mas a maior proporção de mortes.
# Isso indica alta velocidade, fadiga e menor tempo de resposta ao socorro.
#
# **3. Característica do acidente: Colisão frontal e atropelamento**
#
# São os dois tipos com maior energia de impacto
# e menor chance de sobrevivência:
#
# | Tipo | Rural | Urbano |
# |------|-------|--------|
# | Colisão frontal | 35,13% | 15,65% |
# | Atropelamento de pedestre | 40,05% | 22,35% |
#
# **4. Gravidade: Foco na taxa, não no volume**
#
# Os municípios com mais acidentes (Brasília, Duque de Caxias, São José)
# têm taxas de fatalidade baixas (1,45% a 4,25%).
# Os estados com maior taxa de fatalidade (MA: 18,70%, PA: 17,28%)
# têm menor volume absoluto.
# A prioridade deve ser reduzir a **probabilidade de morte por acidente**,
# não apenas reduzir o número total de ocorrências.
#
# ### Plano de Ação Sugerido
#
# | Prioridade | Ação | Justificativa |
# |---|---|---|
# | 1ª | Fiscalização noturna em trechos rurais de pista simples | Madrugada + pista simples = maior taxa de fatalidade |
# | 2ª | Instalação de barreiras centrais em trechos críticos | Reduz colisões frontais (35% de fatalidade rural) |
# | 3ª | Sinalização e iluminação em pontos de atropelamento rural | Atropelamento rural tem 40% de fatalidade |
# | 4ª | Campanhas contra fadiga e álcool na madrugada | Horário com maior letalidade e menor volume |
#
# ### O que NÃO fazer
#
# Não priorizar ações apenas nos municípios com maior volume
# de acidentes (Brasília, Duque de Caxias, Guarulhos).
# Esses locais têm alta frequência, mas baixa letalidade.
# Os acidentes ali são majoritariamente colisões traseiras
# e laterais de baixo impacto, com taxas de fatalidade abaixo de 4%.
#
# %% [markdown]
# ### 15. Conclusão executiva
#

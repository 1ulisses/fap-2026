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
# ### 1. Importação das bibliotecas e leitura dos dados

# %%
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# %% [markdown]
# ### 2. Leitura dos dados e preparação

# %%
ROOT = Path(".")
DIRS = ["data"]

for directory in DIRS:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

RAW_FILE = Path("./data/acidentes2025.csv")
ANALYTICAL_FILE = Path("./data/acidentes2025_analitica.csv")
df = pd.read_csv(ANALYTICAL_FILE, sep=";", encoding="latin1", low_memory=False)


# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)


# %%
print(f"Total de registros: {len(df)}")
print(f"Colunas disponíveis: {df.columns.tolist()}")
print(f"\nDistribuição de acidentes fatais:\n{df['acidente_fatal'].value_counts()}")


# %%
df["dia_util"] = df["dia_semana"].apply(
    lambda x: (
        0
        if x in ["sábado", "domingo", "Sábado", "Domingo"] or "áb" in x or "ingo" in x
        else 1
    )
)

print("Valores únicos de dia_semana:", df["dia_semana"].unique())
print("\nDistribuição dia_util:", df["dia_util"].value_counts())


# %%
df["data_inversa"] = pd.to_datetime(df["data_inversa"], errors="coerce")
df["mes"] = df["data_inversa"].dt.month
df["mes_nome"] = df["data_inversa"].dt.month_name()

print("Meses disponíveis:", df["mes_nome"].dropna().unique())


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

print("\nFaixas horárias:", df["faixa_horaria"].unique())
print("Turnos:", df["turno"].unique())

# %% [markdown]
# ---
# ## Questão 1: Onde estão os acidentes fatais?
#
# Investigue se os acidentes fatais estão distribuídos de maneira semelhante entre os estados.

# %%
# Quantidade total de acidentes por UF
uf_total = df.groupby("uf").size()

# Quantidade de acidentes fatais por UF
uf_fatal = df[df["acidente_fatal"] == 1].groupby("uf").size()

# Taxa de fatalidade por UF
uf_fatality_rate = (df.groupby("uf")["acidente_fatal"].mean() * 100).round(2)

# Criar DataFrame consolidado
uf_analysis = pd.DataFrame(
    {
        "total_acidentes": uf_total,
        "acidentes_fatais": uf_fatal.fillna(0),
        "taxa_fatalidade_pct": uf_fatality_rate,
    }
)

# Filtrar UFs com pelo menos 100 acidentes
uf_analysis_filtered = uf_analysis[uf_analysis["total_acidentes"] >= 100].sort_values(
    "taxa_fatalidade_pct", ascending=False
)

print(uf_analysis_filtered.to_string())

# %% [markdown]
# **Interpretação e Conclusão:**
#
# As UFs com maiores taxas de fatalidade não são necessariamente aquelas com maior quantidade absoluta de acidentes. Por exemplo, uma UF pode ter relativamente poucos acidentes totais, mas uma proporção significativa deles resulta em mortes.
#
# Uma UF com alta taxa de fatalidade pode indicar fatores como: velocidades mais altas nas rodovias, menor fiscalização, condições precárias das vias, ou menor acesso a atendimento médico de emergência. Já uma UF com muitos acidentes mas baixa taxa de fatalidade pode ter melhor infraestrutura hospitalar próxima às rodovias ou acidentes de menor gravidade em sua maioria.

# %% [markdown]
# ---
# ## Questão 2: O horário dos acidentes está relacionado à fatalidade?
#
# Utilizando turno ou faixa_horaria, investigue o comportamento dos acidentes ao longo do dia.


# %%
# Agrupamento por faixa_horaria
faixa_analysis = (
    df.groupby("faixa_horaria")
    .agg(
        total_acidentes=("acidente_fatal", "count"),
        acidentes_fatais=("acidente_fatal", "sum"),
        taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
    )
    .reset_index()
)

faixa_analysis = faixa_analysis.sort_values("total_acidentes", ascending=False)
print(faixa_analysis.to_string(index=False))


# %% [markdown]
# **Interpretação e Conclusão:**
#
# A análise revela que o período com maior número de acidentes **não é** necessariamente o período com maior taxa de fatalidade.
#
# Períodos diurnos (Manhã e Tarde) tendem a ter mais acidentes devido ao maior fluxo de veículos.
# Porém, períodos noturnos podem apresentar taxas de fatalidade mais elevadas devido a fatores como: menor visibilidade, fadiga dos motoristas, consumo de álcool, e velocidades mais altas em vias com menos tráfego.
#

# %% [markdown]
# ---
# ## Questão 3: Fim de semana x dias úteis
#
# Compare acidentes ocorridos em dias úteis e finais de semana.


# %%
# Agrupamento por dia_util (0=fim de semana, 1=dia útil)
dia_analysis = (
    df.groupby("dia_util")
    .agg(
        total_acidentes=("acidente_fatal", "count"),
        acidentes_fatais=("acidente_fatal", "sum"),
        taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
        media_vitimas=("mortos", "mean"),
    )
    .reset_index()
)

dia_analysis["tipo_dia"] = dia_analysis["dia_util"].map(
    {0: "Fim de Semana", 1: "Dia Útil"}
)
dia_analysis = dia_analysis[
    [
        "tipo_dia",
        "total_acidentes",
        "acidentes_fatais",
        "taxa_fatalidade_pct",
        "media_vitimas",
    ]
]
dia_analysis = dia_analysis.set_index("tipo_dia")

print(dia_analysis.to_string())

# %% [markdown]
# **Interpretação e Conclusão:**
#
# Dias úteis tendem a ter mais acidentes devido ao maior volume de tráfego (commuting, transporte de carga, etc.).
#
# Finais de semana frequentemente apresentam taxas de fatalidade mais altas, possivelmente associadas a:
# - Maior consumo de álcool em atividades de lazer
# - Viagens mais longas em rodovias
# - Comportamentos de risco (excesso de velocidade)
#
# Acidentes em finais de semana tendem a ser mais graves, com mais vítimas por evento.
#
# Embora haja menos acidentes nos fins de semana em termos absolutos, aqueles que ocorrem são proporcionalmente mais graves.

# %% [markdown]
# ---
# ## Questão 4: Quais tipos de acidente merecem mais atenção?
#
# Analise tipo_acidente considerando frequência, taxa de fatalidade e média de vítimas.


# %%
# Agrupamento por tipo_acidente
tipo_analysis = (
    df.groupby("tipo_acidente")
    .agg(
        total_acidentes=("acidente_fatal", "count"),
        acidentes_fatais=("acidente_fatal", "sum"),
        taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
        media_vitimas=("mortos", "mean"),
    )
    .reset_index()
)

# Filtrar tipos com pelo menos 50 ocorrências
tipo_analysis_filtered = tipo_analysis[tipo_analysis["total_acidentes"] >= 50].copy()
tipo_analysis_filtered = tipo_analysis_filtered.sort_values(
    "total_acidentes", ascending=False
)

print(tipo_analysis_filtered.to_string(index=False))

# %%
# a) Tipo mais frequente
mais_frequente = tipo_analysis_filtered["total_acidentes"].idxmax()
print(
    f"a) Tipo mais frequente: {mais_frequente} ({tipo_analysis_filtered.loc[mais_frequente, 'total_acidentes']} acidentes)"
)

# b) Tipo com maior taxa de fatalidade
maior_taxa_fatal = tipo_analysis_filtered["taxa_fatalidade_pct"].idxmax()
print(
    f"b) Tipo com maior taxa de fatalidade: {maior_taxa_fatal} ({tipo_analysis_filtered.loc[maior_taxa_fatal, 'taxa_fatalidade_pct']}%)"
)

# c) Tipo com maior média de vítimas
maior_media_vitimas = tipo_analysis_filtered["media_vitimas"].idxmax()
print(
    f"c) Tipo com maior média de vítimas: {maior_media_vitimas} ({tipo_analysis_filtered.loc[maior_media_vitimas, 'media_vitimas']:.2f} vítimas/acidente)"
)

# %% [markdown]
# **Interpretação e Conclusão:**
#
# Frequência e gravidade são dimensões diferentes:
# Acidentes mais frequentes como colisões traseiras muitas vezes ocorrem em baixas velocidades, em situações de trânsito congestionado, resultando em menores taxas de fatalidade.
# Acidentes com maior taxa de fatalidade como atropelamentos de pedestres, tombamentos ou colisões frontais podem ser menos comuns, mas quando ocorrem, têm consequências muito mais severas.
#

# %% [markdown]
# ---
# ## Questão 5: Três gráficos para contar uma história
#
# Construa 3 gráficos utilizando .plot() para investigar a relação entre acidentes e fatalidade.

# %%
# Dados mensais
mes_analysis = (
    df.groupby("mes")
    .agg(
        total_acidentes=("acidente_fatal", "count"),
        acidentes_fatais=("acidente_fatal", "sum"),
        taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
    )
    .reset_index()
)

mes_analysis = mes_analysis.sort_values("mes")
mes_analysis["mes_nome_abrev"] = mes_analysis["mes"].map(
    {
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
)

print(mes_analysis.to_string(index=False))

# %% [markdown]
# **Gráfico 1: Quantidade de acidentes por mês**

# %%
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Gráfico 1: Total de acidentes por mês
axes[0].bar(
    mes_analysis["mes_nome_abrev"],
    mes_analysis["total_acidentes"],
    color="steelblue",
    edgecolor="navy",
)
axes[0].set_title(
    "Gráfico 1: Quantidade de Acidentes por Mês", fontsize=12, fontweight="bold"
)
axes[0].set_xlabel("Mês", fontsize=10)
axes[0].set_ylabel("Número de Acidentes", fontsize=10)
axes[0].grid(axis="y", alpha=0.3)

# Adicionar valores nas barras
for i, v in enumerate(mes_analysis["total_acidentes"]):
    axes[0].text(
        i,
        v + max(mes_analysis["total_acidentes"]) * 0.02,
        str(int(v)),
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.tight_layout()
plt.show()

# %% [markdown]
# **Interpretação Gráfico 1:**
#
# O primeiro gráfico mostra a distribuição mensal do volume total de acidentes. Observamos variações ao longo do ano que podem estar associadas a fatores sazonais como férias escolares, feriados prolongados, condições climáticas típicas de cada estação, e volume de tráfego nas rodovias. Meses com picos de acidentes geralmente coincidem com períodos de maior circulação de veículos.

# %% [markdown]
# **Gráfico 2: Quantidade de acidentes fatais por mês**

# %%
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Gráfico 2: Acidentes fatais por mês
axes[1].bar(
    mes_analysis["mes_nome_abrev"],
    mes_analysis["acidentes_fatais"],
    color="crimson",
    edgecolor="darkred",
)
axes[1].set_title(
    "Gráfico 2: Quantidade de Acidentes Fatais por Mês", fontsize=12, fontweight="bold"
)
axes[1].set_xlabel("Mês", fontsize=10)
axes[1].set_ylabel("Número de Acidentes Fatais", fontsize=10)
axes[1].grid(axis="y", alpha=0.3)

# Adicionar valores nas barras
for i, v in enumerate(mes_analysis["acidentes_fatais"]):
    axes[1].text(
        i,
        v + max(mes_analysis["acidentes_fatais"]) * 0.02,
        str(int(v)),
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.tight_layout()
plt.show()

# %% [markdown]
# **Interpretação Gráfico 2:**
#
# O segundo gráfico apresenta a evolução mensal dos acidentes com vítimas fatais. Embora siga um padrão similar ao gráfico de total de acidentes (já que são derivados da mesma base), este gráfico destaca os meses onde houve maior número de mortes. A comparação visual com o Gráfico 1 permite identificar se meses com muitos acidentes também têm proporcionalmente muitas fatalidades.

# %% [markdown]
# **Gráfico 3: Taxa de fatalidade por mês**

# %%
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Gráfico 3: Taxa de fatalidade por mês
axes[2].plot(
    mes_analysis["mes_nome_abrev"],
    mes_analysis["taxa_fatalidade_pct"],
    marker="o",
    linewidth=2,
    markersize=8,
    color="forestgreen",
    markerfacecolor="lightgreen",
    markeredgecolor="darkgreen",
)
axes[2].set_title(
    "Gráfico 3: Taxa de Fatalidade por Mês (%)", fontsize=12, fontweight="bold"
)
axes[2].set_xlabel("Mês", fontsize=10)
axes[2].set_ylabel("Taxa de Fatalidade (%)", fontsize=10)
axes[2].grid(alpha=0.3)
axes[2].axhline(
    y=mes_analysis["taxa_fatalidade_pct"].mean(),
    color="gray",
    linestyle="--",
    label=f"Média: {mes_analysis['taxa_fatalidade_pct'].mean():.2f}%",
)
axes[2].legend()

# Adicionar valores nos pontos
for i, v in enumerate(mes_analysis["taxa_fatalidade_pct"]):
    axes[2].text(
        i,
        v + max(mes_analysis["taxa_fatalidade_pct"]) * 0.05,
        f"{v}%",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.tight_layout()
plt.show()

# %% [markdown]
# **Interpretação Gráfico 3:**
#
# O terceiro gráfico revela a taxa de fatalidade mensal, que é o indicador mais importante para entender a gravidade relativa dos acidentes em cada período. Diferentemente dos dois primeiros gráficos que mostram volumes absolutos, este gráfico mostra proporção. Um mês pode ter poucos acidentes totais, mas uma taxa de fatalidade elevada, indicando que os acidentes que ocorreram naquele mês foram particularmente graves.
#
# **Resposta à pergunta:**
#
# Os três gráficos **não contam exatamente a mesma história**. Enquanto os Gráficos 1 e 2 mostram padrões similares de volume (já que acidentes fatais são um subconjunto do total), o Gráfico 3 (taxa de fatalidade) pode revelar meses que se destacam pela gravidade, mesmo sem ter o maior volume absoluto.
#
# Por exemplo, um mês com relativamente poucos acidentes mas com alta taxa de fatalidade merece atenção especial, pois indica que os acidentes ocorridos foram desproporcionalmente graves. Isso pode estar associado a condições específicas daquele mês (clima adverso, feriados com viagens longas, operações de fiscalização específicas). A taxa de fatalidade é o indicador que melhor captura a "qualidade" ou severidade dos acidentes, complementando a análise de volume.

# %% [markdown]
# ---
# ## Questão 6: Clima e fatalidade
#
# Investigue condicao_metereologica e diferencie associação de causalidade.

# %% [markdown]
# **Código:** Análise por condição meteorológica (≥100 acidentes)

# %%
# Agrupamento por condicao_metereologica
clima_analysis = (
    df.groupby("condicao_metereologica")
    .agg(
        total_acidentes=("acidente_fatal", "count"),
        acidentes_fatais=("acidente_fatal", "sum"),
        taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
    )
    .reset_index()
)

# Filtrar condições com pelo menos 100 acidentes
clima_analysis_filtered = clima_analysis[
    clima_analysis["total_acidentes"] >= 100
].copy()
clima_analysis_filtered = clima_analysis_filtered.sort_values(
    "taxa_fatalidade_pct", ascending=False
)

print(clima_analysis_filtered.to_string(index=False))

# %% [markdown]
# **Tabela: Análise por Condição Meteorológica (≥100 acidentes)**

# %%
clima_analysis_filtered = clima_analysis_filtered.set_index("condicao_metereologica")
clima_analysis_filtered

# %% [markdown]
# **Interpretação e Conclusão:**
#
# As condições meteorológicas com maiores taxas de fatalidade podem incluir situações como neblina, chuva forte, ou vento, que reduzem a visibilidade e aderência dos pneus.
#
# **Importante: Associação NÃO implica Causalidade**
#
# Esta análise **não permite afirmar** que determinada condição climática **causa** acidentes mais fatais. Podemos apenas observar uma **associação estatística**. Outras explicações possíveis:
#
# 1. **Fatores de confusão:** Condições climáticas adversas podem coincidir com outros fatores de risco (ex: neblina em regiões serranas com curvas perigosas).
#
# 2. **Viés de registro:** Condições climáticas podem ser registradas de forma inconsistente após o acidente.
#
# 3. **Comportamento do motorista:** Em condições climáticas ruins, motoristas prudentes reduzem velocidade, enquanto os imprudentes mantêm comportamentos de risco, potencialmente criando uma seleção de motoristas mais propensos a acidentes graves.
#
# 4. **Volume de tráfego:** Algumas condições podem ocorrer em períodos de menor tráfego, afetando as taxas relativas.
#
# **Conclusão adequada:** Podemos dizer que há uma **correlação** entre certas condições meteorológicas e taxas de fatalidade, mas não podemos estabelecer relação causal sem estudos controlados que considerem múltiplas variáveis de confusão.

# %% [markdown]
# ---
# ## Questão 7: Municípios: quantidade não significa necessariamente risco
#
# Identifique os 10 municípios com maior quantidade de acidentes e analise suas taxas de fatalidade.

# %% [markdown]
# **Código:** Top 10 municípios por quantidade de acidentes

# %%
# Top 10 municípios por total de acidentes
top10_municipios = df.groupby("municipio").size().nlargest(10).index.tolist()

# Filtrar apenas esses municípios
df_top10 = df[df["municipio"].isin(top10_municipios)]

# Análise detalhada
municipio_analysis = (
    df_top10.groupby("municipio")
    .agg(
        total_acidentes=("acidente_fatal", "count"),
        acidentes_fatais=("acidente_fatal", "sum"),
        taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
        media_vitimas=("mortos", "mean"),
    )
    .reset_index()
)

municipio_analysis = municipio_analysis.sort_values("total_acidentes", ascending=False)
municipio_analysis = municipio_analysis.set_index("municipio")

print(municipio_analysis.to_string())

# %% [markdown]
# **Tabela: Top 10 Municípios por Quantidade de Acidentes**

# %%
municipio_analysis

# %% [markdown]
# **Verificação: O município com mais acidentes tem a maior taxa de fatalidade?**

# %%
mun_mais_acidentes = municipio_analysis["total_acidentes"].idxmax()
mun_maior_taxa = municipio_analysis["taxa_fatalidade_pct"].idxmax()

print(
    f"Município com MAIS acidentes: {mun_mais_acidentes} ({municipio_analysis.loc[mun_mais_acidentes, 'total_acidentes']} acidentes)"
)
print(
    f"Taxa de fatalidade deste município: {municipio_analysis.loc[mun_mais_acidentes, 'taxa_fatalidade_pct']}%"
)
print()
print(
    f"Município com MAIOR taxa de fatalidade: {mun_maior_taxa} ({municipio_analysis.loc[mun_maior_taxa, 'taxa_fatalidade_pct']}%)"
)
print(
    f"Total de acidentes deste município: {municipio_analysis.loc[mun_maior_taxa, 'total_acidentes']}"
)

# %% [markdown]
# **Interpretação e Conclusão:**
#
# **O município que possui mais acidentes NÃO necessariamente possui a maior taxa de fatalidade.**
#
# Esta análise demonstra por que rankings baseados apenas em quantidade podem ser enganosos:
#
# 1. **Municípios grandes** tendem a ter mais acidentes simplesmente porque têm mais veículos circulando e maior extensão de rodovias em seu território. Isso não significa que sejam mais perigosos proporcionalmente.
#
# 2. **Taxa de fatalidade** é um indicador de risco relativo que normaliza pelo volume de acidentes, mostrando qual a probabilidade de um acidente ser fatal naquele município.
#
# 3. **Implicações:**
#    - Um ranking apenas por quantidade pune municípios populosos e pode negligenciar municípios menores mas mais perigosos.
#    - Para alocação de recursos de segurança viária, deveríamos considerar ambos os indicadores: volume absoluto (para impacto total) e taxa (para risco relativo).
#
# **Exemplo prático:** Um município turístico pequeno pode ter poucos acidentes no total, mas se a maioria ocorre em curvas perigosas de serra, sua taxa de fatalidade será altíssima, indicando um problema específico que precisa de intervenção.

# %% [markdown]
# ---
# ## Questão 8: Investigação Final - Qual perfil de acidente merece atenção?
#
# Análise combinando pelo menos três variáveis da base.

# %% [markdown]
# **Pergunta investigada:**
#
# *"Qual combinação de turno (dia/noite), tipo de acidente e condição meteorológica apresenta a maior taxa de fatalidade, considerando apenas grupos com ocorrência significativa?"*
#
# **Justificativa:** Esta combinação é relevante porque:
# - Turno afeta visibilidade e estado de alerta dos motoristas
# - Tipo de acidente reflete a dinâmica do evento
# - Condição meteorológica influencia aderência e visibilidade
#
# **Critério mínimo:** Pelo menos 20 ocorrências por grupo para evitar conclusões baseadas em amostras muito pequenas.

# %% [markdown]
# **Código:** Análise combinada de turno + tipo_acidente + condicao_metereologica

# %%
# Criar análise combinada
analise_combinada = (
    df.groupby(["turno", "tipo_acidente", "condicao_metereologica"])
    .agg(
        total_acidentes=("acidente_fatal", "count"),
        acidentes_fatais=("acidente_fatal", "sum"),
        taxa_fatalidade_pct=("acidente_fatal", lambda x: round(x.mean() * 100, 2)),
        media_vitimas=("mortos", "mean"),
    )
    .reset_index()
)

# Filtrar grupos com pelo menos 20 ocorrências
analise_combinada_filtrada = analise_combinada[
    analise_combinada["total_acidentes"] >= 20
].copy()

# Ordenar por taxa de fatalidade
analise_combinada_filtrada = analise_combinada_filtrada.sort_values(
    "taxa_fatalidade_pct", ascending=False
)

# Mostrar top 15 grupos com maior taxa de fatalidade
top_perfis = analise_combinada_filtrada.head(15)

print(top_perfis.to_string(index=False))

# %% [markdown]
# **Tabela: Top 15 Perfis de Acidente por Taxa de Fatalidade**

# %%
top_perfis_display = top_perfis.set_index(
    ["turno", "tipo_acidente", "condicao_metereologica"]
)
top_perfis_display

# %% [markdown]
# **Identificação do perfil de maior risco:**

# %%
perfil_maior_risco = analise_combinada_filtrada.loc[
    analise_combinada_filtrada["taxa_fatalidade_pct"].idxmax()
]

print("=" * 80)
print("PERFIL DE MAIOR RISCO IDENTIFICADO:")
print("=" * 80)
print(f"Turno: {perfil_maior_risco['turno']}")
print(f"Tipo de Acidente: {perfil_maior_risco['tipo_acidente']}")
print(f"Condição Meteorológica: {perfil_maior_risco['condicao_metereologica']}")
print(f"Total de Acidentes: {int(perfil_maior_risco['total_acidentes'])}")
print(f"Acidentes Fatais: {int(perfil_maior_risco['acidentes_fatais'])}")
print(f"Taxa de Fatalidade: {perfil_maior_risco['taxa_fatalidade_pct']}%")
print(f"Média de Vítimas: {perfil_maior_risco['media_vitimas']:.2f}")
print("=" * 80)

# %% [markdown]
# **Interpretação:**
#
# O perfil identificado como de maior risco combina fatores que potencializam a gravidade dos acidentes:
#
# 1. **Por que este grupo chamou atenção:**
#    - A taxa de fatalidade excepcionalmente alta indica que quando esta combinação específica de fatores ocorre, as chances de morte são extremamente elevadas.
#    - O número de ocorrências (≥20) garante que não se trata de um outlier estatístico.
#
# 2. **Fatores contribuintes prováveis:**
#    - **Turno noturno:** Redução de visibilidade, fadiga, possível consumo de álcool
#    - **Tipo de acidente grave:** Colisões frontais, atropelamentos ou tombamentos tendem a ser mais letais
#    - **Condição meteorológica adversa:** Chuva, neblina ou vento reduzem controle do veículo
#
# 3. **Implicações para prevenção:**
#    - Campanhas específicas para motoristas que trafegam nestas condições
#    - Sinalização reforçada em trechos críticos durante condições adversas
#    - Operação policial focada nestes períodos e condições
#
# **Limitação da análise:**
#
# Esta análise é **observacional e agregada**, o que significa que:
# - Não controla outras variáveis importantes (ex: tipo de veículo, idade do motorista, uso de cinto de segurança)
# - Não estabelece causalidade, apenas identifica associações
# - Pode haver viés de registro nas condições meteorológicas reportadas
# - O critério de corte (≥20 ocorrências) pode excluir perfis raros mas extremamente graves
#
# Para conclusões mais robustas, seria necessário um estudo multivariado com modelo estatístico que controle múltiplas variáveis simultaneamente.

# %% [markdown]
# ---
# ## Conclusão Geral da Investigação
#
# Esta análise exploratória revelou padrões importantes sobre os acidentes rodoviários em 2025:
#
# 1. **Distribuição geográfica:** UFs com maiores taxas de fatalidade não são necessariamente as com mais acidentes, destacando a importância de analisar proporções, não apenas volumes.
#
# 2. **Fator temporal:** Horários e dias da semana influenciam tanto a quantidade quanto a gravidade dos acidentes, com fins de semana apresentando acidentes proporcionalmente mais graves.
#
# 3. **Tipos de acidente:** Frequência e gravidade são dimensões distintas; políticas públicas devem equilibrar prevenção de acidentes comuns e mitigação de acidentes graves.
#
# 4. **Condições ambientais:** Fatores como clima e luminosidade estão associados à fatalidade, mas correlação não implica causalidade.
#
# 5. **Análise multidimensional:** Combinações específicas de fatores (turno + tipo + clima) revelam perfis de alto risco que merecem atenção especializada.
#
# **Recomendação final:** Estratégias de segurança viária devem ser baseadas em evidências locais, considerando tanto o volume quanto a gravidade dos acidentes, e adaptadas aos perfis de risco específicos de cada região e período.

# %%
# Configurar estilo dos gráficos
plt.style.use("default")

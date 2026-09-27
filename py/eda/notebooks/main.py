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
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)

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
# condicao_metereologica x faixa_horaria
#
# Escolhemos combinar condicao_metereologica e faixa horária porque o efeito do clima
# sobre a gravidade não deve ser uniforme ao longo do dia. A faixa horária funciona como
# proxy de luz natural, fluxo de veículos e fadiga do condutor. Por isso, contextos como
# chuva à noite ou neblina na madrugada podem concentrar risco maior do que cada fator
# analisado isoladamente.
# O volume analisado deve considerar apenas combinações com número mínimo de acidentes, por
# exemplo 30 ou 100 registros, para evitar taxas instáveis. O indicador de gravidade será a
# taxa de acidentes fatais, calculada como acidentes fatais divididos pelo total de
# acidentes, além de mortos por acidente como métrica complementar.
# A comparação será feita contra a taxa global da base e contra as taxas marginais de clima
# e horário. Se uma combinação apresentar taxa acima da referência e volume suficiente, ela
# será interpretada como contexto crítico. Se apresentar taxa alta, mas volume baixo, será
# tratada como evidência frágil.
# A principal limitação é que células com poucos acidentes podem gerar proporções enganosas.
# Além disso, a faixa horária não mede diretamente visibilidade, sono ou tráfego, servindo
# apenas como aproximação desses fatores.

# %% [markdown]
# 10. Investigação de combinações

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
df["faixa_horaria"] = df["hora"].apply(def_faixa_horaria)

# %%
faixa_clima_analysis = analyze(
    df, ["condicao_metereologica", "faixa_horaria"]
).sort_values("total_acidentes", ascending=False)
faixa_clima_analysis

# %% [markdown]
# 11. Teste dos achados

# %% [markdown]
# # Achado
# A análise revela que a Madrugada (0h-6h) atua como um multiplicador
# universal de letalidade, alterando drasticamente o comportamento de todas as condições
# climáticas.
# Sob Céu Claro, a taxa de fatalidade salta de aproximadamente 5% durante o dia para 12,46%
# na madrugada, com alto volume de acidentes (5.498). Esse salto proporcional se repete
# em dias Nublados (de 4,7% para 12,75%) e sob Chuva (de 4,7% para 9,25%). A madrugada
# invariavelmente dobra ou triplica a taxa de óbitos em relação ao período diurno,
# independentemente do clima.
# A combinação com a maior taxa absoluta é **Nevoeiro + Noite (18,18%)**, porém possui
# volume baixo (99 acidentes), o que exige cautela para não superestimar o risco
# populacional. Já o contexto **Céu Claro + Madrugada** é o mais crítico em impacto
# absoluto e estabilidade estatística (685 mortes em 5.498 acidentes).
# A conclusão analítica é que a ausência de luz natural e a provável fadiga do condutor na
# madrugada agravam a severidade dos acidentes de forma muito mais agressiva do que a
# condição meteorológica isolada. O clima define a frequência, mas a faixa horária define
# a letalidade.
#
# # Explicação alternativa
# A madrugada concentra acidentes de alta letalidade intrínseca, como "Colisão Frontal" e
# "Saída de Pista", causados por cochilos ao volante.

# %%
faixas = ["Manhã (6h-12h)", "Madrugada (0h-6h)"]
sub_df = df.query("faixa_horaria in @faixas and tipo_acidente == 'Colisï¿½o traseira'")

faixa_tipo_analysis = analyze(sub_df, ["tipo_acidente", "faixa_horaria"]).sort_values(
    "total_acidentes", ascending=False
)
faixa_tipo_analysis

# %% [markdown]
# Mesmo isolando apenas a "Colisão Traseira", a taxa de fatalidade na madrugada (9,84%)
# foi quatro vezes superior à da manhã (2,40%). Isso prova que a madrugada não é letal
# apenas por concentrar acidentes graves, como colisões frontais; ela agrava a severidade
# de qualquer ocorrência.

# %% [markdown]
# 12. Anomalias e limitações

# %% [markdown]
# O padrão central desta análise é a letalidade desproporcional na madrugada, validada por
# alto volume de registros e consistência em múltiplos recortes, como clima e tipos de
# acidente. A anomalia identificada é a taxa de fatalidade de 18,18% sob neblina noturna,
# que deve ser tratada com ceticismo por se basear em apenas 99 ocorrências,
# caracterizando uma flutuação amostral e não uma regra estatística. A distinção entre
# ambos se dá pelo volume e pela repetição: o padrão da madrugada se mantém robusto em
# milhares de casos, enquanto a anomalia da neblina é um evento raro e instável. A
# principal limitação desta etapa é a ausência de dados sobre a velocidade dos veículos no
# impacto e o tempo de resposta do socorro médico, o que nos impede de concluir se a
# gravidade noturna decorre da física de colisões em tráfego livre ou do atraso no resgate
# das vítimas.


# %% [markdown]
# 16. Conclusão

# %% [markdown]
# A investigação seguiu um encadeamento lógico em que a definição da pergunta central e
# das hipóteses norteou uma estratégia de análise estruturada, partindo do saneamento e
# validação da base até o estabelecimento das métricas globais de referência; a partir
# daí, a exploração univariada revelou a distribuição geral dos acidentes, conduzindo às
# análises bivariadas e à combinação de variáveis (clima e faixa horária), onde emergiu o
# papel crítico da madrugada, o qual foi subsequentemente testado e validado contra
# explicações alternativas (isolando tipos específicos de sinistro, como colisão
# traseira) e confrontado com suas anomalias e limitações amostrais. Com essa trajetória,
# a pergunta central foi plenamente respondida: as condições meteorológicas adversas
# influenciam primordialmente a probabilidade e o volume de ocorrência dos acidentes, mas
# não alteram fundamentalmente o seu perfil intrínseco de gravidade e letalidade — papel
# este exercido com muito mais força pelo fator temporal (madrugada) e comportamental
# do que pelo clima em si.

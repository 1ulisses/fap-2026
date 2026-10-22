# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ANALYTICAL_FILE = Path("../data/raw/acidentes2025_analitica.csv")
RAW_FILE = Path("../data/acidentes2025.csv")
df = pd.read_csv(RAW_FILE, sep=";", encoding="latin1", low_memory=False)

# %%
df["acidente_fatal"] = np.where(df["mortos"] >= 1, 1, 0)

# %% [markdown]
# # Entregável 1
# 1. 72529 linhas e 31 colunas
# 2. data_inversa, horario, dia_semana, uf, br, km, municipio, causa_acidente, tipo_acidente, classificacao_acidente, pessoas, mortos, feridos, veiculos.
# 3. Sim, classificacao_acidente: 1; regional: 2; delegacia: 22; uop: 38
# 4. Não
# 5. 2025

# %%
df.shape

# %%
df.info()

# %%
df.dtypes[df.dtypes == 'str']

# %%
df.dtypes[df.dtypes == 'int64']

# %%
df.isna().sum()

# %%
print(df.duplicated(keep=False).sum())

# %% [markdown]
# # Entregável 2
# 1. Para feridos (média 1.15, mediana 1.0) e pessoas (média 2.59, mediana 2.0), os valores são próximos, para mortos, a média (0.08) é superior à mediana (0.0).
# 2. Os máximos absolutos registram 76 pessoas envolvidas, 49 feridos e 16 mortos em um único evento.
# 3. A variável pessoas apresenta a maior dispersão (desvio padrão de 2.25 e amplitude de 75).
# 4. O cruzamento das categorias de maior frequência, dos valores extremos e da dispersão revela que a sinistralidade possui um comportamento bimodal que não pode ser analisado em bloco. As categorias dominantes mostram que o cenário padrão é composto por incidentes de rotina (colisões traseiras) em estados de alto fluxo. Contudo, a dispersão e os outliers severos expõem que as métricas agregadas são distorcidas por eventos catastróficos raros (até 16 óbitos). A lição analítica aqui é que você deve segmentar a base entre "acidentes de fluxo cotidiano" (baixa dispersão, alta frequência) e "desastres de grande porte" (alta dispersão, cauda longa), pois as causas raízes e as políticas de mitigação para esses dois grupos são fundamentalmente diferentes.

# %%
def stats(col: pd.Series) -> pd.Series:
    q1 = col.quantile(0.25)
    q3 = col.quantile(0.75)
    return pd.Series(
        {
            "média": col.mean(),
            "mediana": col.median(),
            "moda": col.mode().iloc[0],
            "mínimo": col.min(),
            "máximo": col.max(),
            "amplitude": col.max() - col.min(),
            "desvio": col.std(),
            "Q1 (25%)": q1,
            "Q3 (75%)": q3,
        }
    )


# %%
stats(df["mortos"])

# %%
stats(df["feridos"])

# %%
stats(df["pessoas"])
# %% [markdown]
# # Entregável 3
# Tarde (12h-18h)      22302
# Manhã (6h-12h)       20859
# Noite (18h-24h)      20461
#
# MG    9570
# SC    8186
# PR    7630

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
df.groupby("dia_semana").size().sort_values(ascending=False)

# %%
df.groupby("faixa_horaria").size().sort_values(ascending=False)

# %%
df.groupby("tipo_acidente").size().sort_values(ascending=False)

# %%
df.groupby("uf").size().sort_values(ascending=False)

# %% [markdown]
# # Entregável 4
#
# A tarde é onde ocorre a maioria dos acidentes > 20.000, e a madrugada é onde menos ocorre a quantidade de acidentes. Sinalizando que a ocorrência de acidentes se dá em períodos de maior quantidade de carros nas rodovias
# A grande maioria dos acidentes não passam de 10 pessoas envolvidas, e a sua grande maioria ocorre entre duas pessoas, mostrando uma ocorrência comum a moda de pessoas dentro de um carro.
# Demonstra que a maioria dos acidentes não são fatais, em uma maioria esmagadora.

# %%
df.groupby("faixa_horaria")["acidente_fatal"].count().plot.bar(rot=0)
plt.title("Contagem de Acidentes por Faixa Horária")
plt.xlabel("Faixa Horária")
plt.ylabel("Total de Acidentes")
plt.tight_layout()
plt.show()

# %%
df["pessoas"].plot.hist(bins=50)
plt.title("Distribuição do Número de Pessoas Envolvidas")
plt.xlabel("Pessoas")
plt.ylabel("Frequência")
plt.tight_layout()
plt.show()

# %%
df["acidente_fatal"].value_counts().plot.bar(rot=0)
plt.title("Contagem de Acidentes Fatais (0 = Não, 1 = Sim)")
plt.xlabel("Acidente Fatal")
plt.ylabel("Contagem")
plt.tight_layout()
plt.show()

# %% [markdown]
# # Entregável 5

# %% [markdown]
# Os dados revelam uma clara concentração de acidentes no período da tarde (12h-18h) com 22.302 ocorrências, seguido pela manhã (20.859). Em relação aos dias da semana, os fins de semana se destacam, com sábado (11.554) e domingo (11.470) registrando os maiores volumes absolutos, enquanto a terça-feira apresentou a menor contagem (9.062). A madrugada é o período com menor incidência, totalizando 8.907 registros.
# A colisão traseira é o tipo de acidente mais frequente, totalizando 14.360 registros, seguida pela saída de leito carroçável (10.209) e colisão transversal (9.306). Geograficamente, observa-se uma forte disparidade regional: os estados de Minas Gerais (9.570), Santa Catarina (8.186) e Paraná (7.630) concentram os maiores volumes de ocorrências, enquanto estados da região Norte apresentam números significativamente menores.
# O resultado estatístico que mais chama a atenção são os valores extremos nas variáveis de contagem de envolvidos. Embora a mediana de pessoas envolvidas seja 2, o valor máximo atinge 76 pessoas em um único evento. Da mesma forma, os máximos de feridos (49) e mortos (16) indicam eventos catastróficos de grande porte, como engavetamentos ou acidentes com transporte de passageiros, que fogem à distribuição normal e exigem validação caso a caso.
# Uma inconsistência técnica grave identificada no seu código é o problema de codificação de caracteres (mojibake) nas variáveis categóricas. Palavras como "sábado", "terça-feira" e "Colisão" aparecem corrompidas nos agrupamentos (ex: "sï¿½bado", "Colisï¿½o"). Isso ocorre porque o arquivo foi lido com `latin1`, mas a codificação real dos dados exige tratamento adequado (provavelmente `utf-8`), o que compromete a integridade de filtros, relatórios e futuras modelagens de texto.
# Os valores ausentes são estatisticamente irrelevantes e não afetam a análise global. Variáveis operacionais como `classificacao_acidente`, `regional`, `delegacia` e `uop` possuem no máximo 38 registros nulos em um total de 72.529 linhas. Além disso, a base não apresenta nenhuma linha duplicada, demonstrando boa integridade estrutural na origem dos dados.
# Como análises adicionais, poderíamos cruzar os outliers de pessoas envolvidas com as colunas de tipo de acidente e quantidade de veículos para confirmar a hipótese de envolvimento de ônibus ou caminhões. Também seria essencial calcular a taxa de letalidade (proporção de acidentes fatais em relação ao total) por estado ou fase do dia, em vez de observar apenas os volumes absolutos, o que mudaria completamente o ranking de risco das categorias.
# Por fim, é fundamental lembrar que maiores volumes absolutos à tarde ou aos fins de semana refletem o aumento natural do fluxo de veículos e rotinas de viagem, e não necessariamente que esses períodos sejam intrinsecamente mais perigosos. Não podemos afirmar que o horário ou o dia da semana causa acidentes mais graves sem antes normalizar os dados pelo volume real de tráfego ou métricas de exposição ao risco nas rodovias.

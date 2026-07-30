# `CONTROLE_QUALIDADE.md`

```markdown
# Controle de Qualidade e Governança de Dados - Projeto PRF 2025

Este documento consolida as diretrizes, restrições analíticas, tratamentos de anomalias e critérios de validação aplicados sobre os dados e consultas SQL da base de acidentes rodoviários da PRF.

---

## 1. Tratamento de Tipos de Dados e Conversões (Casting)
Como os dados brutos são importados de arquivos `.csv` semiestruturados, campos numéricos essenciais para cálculos de agregação estatística podem ser interpretados textualmente. 
* **Ações implementadas:** Utilização sistemática de funções de coerção de tipo (`CAST(... AS INTEGER)` e `CAST(... AS DOUBLE)`) nas operações de agregação (`SUM`, `AVG`, `MIN`, `MAX`), prevenindo erros de execução por incompatibilidade de tipos de dados.
* Exemplo aplicado: `SUM(CAST(mortos AS INTEGER))` e `AVG(CAST(veiculos AS DOUBLE))`.

---

## 2. Mitigação de Viés Estatístico e Amostragem Pequena (`HAVING`)
Para evitar conclusões distorcidas decorrentes de baixa volumetria de dados em cruzamentos complexos (por exemplo, assumir alta periculosidade em uma rodovia ou condição meteorológica rara que possui apenas 1 ou 2 registros totais), foram aplicadas regras rígidas de filtro de volumetria mínima utilizando a cláusula `HAVING`:
* **Filtros de corte volumétrico aplicados nas consultas:**
  * `HAVING COUNT(*) >= 100`: Padrão adotado na maioria das análises cruzadas de letalidade (condições meteorológicas, tipos de pista, causas e tipos de acidentes) para garantir relevância estatística.
  * `HAVING COUNT(*) >= 50`: Aplicado em cruzamentos geográficos mais específicos, como por municípios ou combinações de UF e fase do dia.
  * `HAVING COUNT(*) >= 30`: Limiar utilizado para análises de restrição temática pontual (ex: municípios com registros sob chuva).

---

## 3. Tratamento de Valores Nulos (`NULL`) e Omissões Geográficas
* **Valores Nulos em Rodovias (`br IS NOT NULL`):** Consultas voltadas ao ranking de rodovias federais exigem a exclusão explícita de registros desprovidos de numeração de BR (`WHERE br IS NOT NULL`), evitando poluição informacional e desvios no ranking de letalidade rodoviária.
* **Padronização de Texto (`LOWER(...)`):** Em consultas que filtram variáveis categóricas textuais passíveis de variação de digitação (como fases do dia ou condições climáticas), utiliza-se a função de normalização de caixa baixa combinada com operadores de correspondência parcial (`LOWER(fase_dia) LIKE '%noite%'` e `LOWER(condicao_metereologica) LIKE '%chuva%'`), assegurando a integridade e completude da captação dos dados.

---

## 4. Governança e Persistência de Saídas (`COPY`)
* Os indicadores consolidados e visões analíticas de alto valor descritivo (como a evolução mensal e a análise bivariada de tipos de acidente) são exportados programaticamente para a pasta controlada `resultados/` nos formatos estruturados:
  * Delimitador de colunas padronizado (`;`).
  * Inclusão explícita de cabeçalho analítico (`HEADER`).
* Isso garante a rastreabilidade e a reprodutibilidade dos relatórios gerados para consumo externo por ferramentas de BI ou equipes de engenharia de tráfego.
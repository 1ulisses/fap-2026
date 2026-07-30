# Projeto PRF 2025: Análise Exploratória e Indicadores de Acidentes Rodoviários

## 📋 Visão Geral do Projeto
Este projeto consiste em coleção organizada abrangente de consultas, visões (`views`) e scripts em **SQL** voltados à ingestão, limpeza, transformação e análise estatística de dados brutos de acidentes rodoviários da Polícia Rodoviária Federal (PRF) referentes ao ano de **2025**. 

O ambiente computacional subjacente utiliza funções de leitura automatizada de arquivos CSV (típicas de ferramentas analíticas performáticas como DuckDB) para processar mais de 72 mil registros de ocorrências rodoviárias em todo o território nacional.

---

## 🎯 Objetivos Principais
1. **Inspeção e Carga de Dados:** Importação dinâmica de arquivos `.csv` brutos contendo delimitadores customizados (`;`) e codificação específica (`latin-1`).
2. **Engenharia de Atributos (Feature Engineering):** Criação de colunas sintéticas, como a flag binária `acidente_fatal`, para padronizar regras de negócio analíticas.
3. **Análise Descritiva e Multivariada:** Identificação de padrões geográficos, temporais e climáticos correlacionados à gravidade (letalidade) dos acidentes.
4. **Métricas Avançadas de Risco:** Aplicação de funções de janela (*window functions*) e modelagem estatística elementar via métricas de **Lift** e **Confiança** comparadas à taxa global de letalidade.
5. **Persistência de Resultados:** Exportação de visualizações consolidadas (`views`) para arquivos analíticos em formato estruturado (`.csv`).

---

## ⚙️ Arquitetura e Estrutura do Script (`modulo3_prf.sql`)

O script de execução está dividido estruturalmente nas seguintes fases:

* **Fases 1 a 3:** Carga inicial da amostragem, criação da tabela principal de trabalho (`acidentes_prf_2025`) e auditoria do esquema de dados (`information_schema`).
* **Fases 4 a 12:** Consultas de exploração volumétrica, ordenação de severidade (número de mortos), recortes geográficos específicos (ex: estado de Pernambuco - `PE`) e estatísticas descritivas agregadas.
* **Fases 13 a 15:** Engenharia da flag binária de fatalidade e construção da View Base reutilizável (`vw_acidentes_base`).
* **Fases 16 a 32:** Análises avançadas cruzando variáveis contextuais (fase do dia, condições meteorológicas, tipo de pista, causas e tipos de acidentes) aplicando filtros de volumetria (`HAVING COUNT(*) >= 100`) para evitar distorções estatísticas.
* **Fases 33 a 37:** Criação de visões analíticas persistentes (`vw_indicadores_mensais`, `vw_indicadores_uf_br`, `vw_bivariada_tipo_acidente`) incorporando cálculos de Cobertura e *Lift*.
* **Fases 38 a 39:** Exportação física dos relatórios gerados para a pasta `resultados/`.

---

## 📊 Principais Consultas Analíticas (Resolução das 12 Perguntas de Negócio)

O repositório/documentação contempla respostas diretas a perguntas analíticas de grande valor estratégico para a segurança viária:
1. **Sazonalidade Semanal:** Mapeamento do fluxo de acidentes segregados por dia da semana.
2. **Concentração Urbana:** Identificação dos 15 municípios com maior densidade de ocorrências.
3. **Frota Envolvida:** Avaliação da média de veículos por ocorrência nas rodovias federais (BRs).
4. **Riscos Noturnos:** Mapeamento de UFs com maior incidência de acidentes no período da noite.
5. **Infraestrutura:** Distribuição percentual dos acidentes por tipo de pista (simples, dupla, múltipla).
6. **Severidade Cruzada:** Cruzamento de UF e fase do dia para isolar maiores taxas de letalidade.
7. **Pessoas Envolvidas:** Média de pessoas envolvidas por tipologia de acidente.
8. **Causas Críticas:** Identificação das 5 causas principais geradoras de óbitos absolutos.
9. **Zoneamento:** Comparativo de letalidade entre áreas urbanas e rurais (`uso_solo`).
10. **Condições Climáticas:** Mapeamento de municípios com alta incidência de ocorrências sob chuva.
11. **Fatores Condicionantes:** Cruzamento detalhado entre tipo de acidente e condição meteorológica.
12. **Ranking Federativo:** Listagem completa das UFs ordenadas por percentual de letalidade e volume de mortes.

---

## 🚀 Como Executar
Certifique-se de possuir o ambiente de banco de dados compatível configurado (ex: DuckDB CLI ou Python com DuckDB) e execute os comandos apontando para o diretório raiz correto onde se encontra a pasta `dados_brutos/acidentes2025.csv`.
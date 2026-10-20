# Dicionário de Comandos e Instruções SQL do Projeto PRF 2025

Este dicionário detalha, de forma direta e organizada, cada comando, função e instrução SQL utilizada nos scripts do projeto de análise dos acidentes rodoviários da PRF de 2025.

---

## 1. Funções de Ingestão e Leitura de Dados

* **`read_csv_auto(...)`**
  * **O que faz:** Função analítica (nativa de motores como DuckDB) que lê automaticamente arquivos no formato CSV, identificando tipos de dados, delimitadores e estruturas de colunas sem necessidade de pré-definição manual do esquema.
  * **Parâmetros utilizados no projeto:**
    * `delim=';'`: Define o ponto e vírgula como o caractere separador das colunas no arquivo bruto.
    * `header=true`: Informa que a primeira linha do arquivo CSV contém o cabeçalho com os nomes das colunas.
    * `sample_size=-1`: Determina que a amostragem para inferência dos tipos de dados deve ler a base de dados inteira (todas as linhas), garantindo precisão máxima.
    * `encoding='latin-1'`: Define a codificação de caracteres para suportar acentuação e caracteres especiais comuns no padrão da língua portuguesa.

---

## 2. Comandos de Manipulação de Estruturas (DDL)

* **`CREATE OR REPLACE TABLE <nome_tabela> AS SELECT ...`**
  * **O que faz:** Cria uma nova tabela física no banco de dados com os resultados de uma consulta. Se a tabela já existir, ela é apagada e substituída por uma nova versão atualizada.
* **`CREATE OR REPLACE VIEW <nome_view> AS SELECT ...`**
  * **O que faz:** Cria uma tabela virtual (view) que armazena a lógica de uma consulta SQL. Diferente da tabela física, ela não duplica os dados em disco, recalculando o resultado sempre que é consultada. Se já existir, é sobrescrita.

---

## 3. Comandos de Seleção e Filtragem de Dados (DQL)

* **`SELECT ... FROM ...`**
  * **O que faz:** Comando fundamental para recuperar e projetar colunas específicas a partir de uma tabela ou view.
* **`WHERE <condicao>`**
  * **O que faz:** Filtra as linhas da tabela com base em critérios lógicos específicos (ex: `uf = 'PE'`, `br IS NOT NULL`, `mortos >= 1`).
* **`DISTINCT`**
  * **O que faz:** Elimina linhas duplicadas do resultado, retornando apenas valores únicos de uma coluna (ex: listar todos os tipos de pista sem repetição).
* **`LIMIT <numero>`**
  * **O que faz:** Restringe a quantidade máxima de linhas retornadas no terminal ou resultado da consulta.

---

## 4. Ordenação e Agrupamento

* **`ORDER BY <coluna> [ASC|DESC]`**
  * **O que faz:** Ordena o resultado da consulta com base em uma ou mais colunas, de forma ascendente (`ASC`) ou descendente (`DESC`).
* **`GROUP BY <coluna(s)>`**
  * **O que faz:** Agrupa linhas que possuem valores idênticos em colunas específicas para permitir a aplicação de funções de agregação (contagens, somas, médias).
* **`GROUP BY ALL`**
  * **O que faz:** Atalho de otimização sintática que agrupa automaticamente a consulta por todas as colunas presentes no comando `SELECT` que não contêm funções agregadas.
* **`HAVING <condicao>`**
  * **O que faz:** Funciona como um filtro aplicado estritamente após o agrupamento (`GROUP BY`), permitindo restringir o resultado com base em métricas agregadas (ex: `HAVING COUNT(*) >= 100`).

---

## 5. Funções de Agregação e Estatísticas

* **`COUNT(*)`**
  * **O que faz:** Conta a quantidade total de linhas ou registros resultantes em um grupo ou tabela.
* **`SUM(...)`**
  * **O que faz:** Soma os valores numéricos de uma coluna específica.
* **`AVG(...)`**
  * **O que faz:** Calcula a média aritmética dos valores de uma coluna numérica.
* **`MIN(...) / MAX(...)`**
  * **O que faz:** Retorna, respectivamente, o menor e o maior valor encontrado em uma coluna numérica.
* **`ROUND(..., <casas_dec_desejadas>)`**
  * **O que faz:** Arredonda um valor numérico para a quantidade especificada de casas decimais (ex: `ROUND(..., 2)` para duas casas decimais).

---

## 6. Operadores Lógicos e Condicionais

* **`CASE WHEN <condicao> THEN <valor1> ELSE <valor2> END`**
  * **O que faz:** Cria lógica condicional linha a linha. No projeto, foi amplamente utilizado para gerar a flag binária de fatalidade (`acidente_fatal`): se `mortos >= 1`, retorna `1`, caso contrário, retorna `0`.
* **`LOWER(...) LIKE '%termo%'`**
  * **O que faz:** Converte o texto da coluna para letras minúsculas (`LOWER`) e busca por padrões parciais correspondentes (`LIKE`), garantindo que variações de digitação (como "Noite" ou "PLENA NOITE") sejam capturadas com sucesso.

---

## 7. Funções de Conversão e Manipulação Temporal

* **`CAST(<coluna> AS <tipo_dado>)`**
  * **O que faz:** Força a conversão do tipo de dado de uma coluna durante a execução da consulta. No projeto, foi essencial para converter colunas importadas como texto para tipos numéricos (`INTEGER`, `DOUBLE`) ou de data (`DATE`).
* **`EXTRACT(<parte_data> FROM CAST(<coluna> AS DATE))`**
  * **O que faz:** Extrai componentes específicos de uma data, sendo utilizado para isolar o ano (`YEAR`) ou o mês (`MONTH`) de campos temporais.

---

## 8. Funções de Janela (*Window Functions*)

* **`OVER ()`**
  * **O que faz:** Executa uma função de agregação (como uma soma total) sobre um conjunto de linhas sem colapsar o agrupamento principal. No projeto, foi utilizada em conjunto com `SUM(COUNT(*)) OVER ()` para calcular a representatividade percentual de cobertura de subgrupos frente ao total geral da base.

---

## 9. Subconsultas e Expressões de Tabela Comuns (CTE)

* **`WITH <nome_cte> AS (SELECT ...) SELECT ... FROM ..., <nome_cte>`**
  * **O que faz:** Cria uma tabela temporária nomeada (Common Table Expression) dentro da própria consulta. No projeto, foi aplicada para calcular previamente a taxa global de letalidade (`taxa_global`) e utilizá-la em divisões estruturais para o cálculo da métrica estatística de **Lift** e **Confiança**.
* **`CROSS JOIN <tabela>`**
  * **O que faz:** Realiza o produto cartesiano entre tabelas ou visões, combinando cada linha da tabela principal com os dados globais calculados na CTE.

---

## 10. Comandos de Exportação de Dados

* **`COPY <view_ou_tabela> TO '<caminho_arquivo.csv>' (HEADER, DELIMITER ';');`**
  * **O que faz:** Exporta fisicamente o resultado de uma view ou tabela de banco de dados para um arquivo estruturado `.csv` no diretório especificado, incluindo o cabeçalho das colunas (`HEADER`) e utilizando ponto e vírgula como delimitador (`DELIMITER ';'`).
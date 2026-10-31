# Auditoria da Base

## 1. Sobre

  Auditoria da base analítica da PRF sobre acidentes rodoviários de 2025. Deve verificar:
- Quantidade de linhas e colunas.
- Tipos de dados.
- Formatação de datas e números.
- Nomes dos campos.
- Separador e codificação do arquivo.
- Valores ausentes e inconsistências relevantes.
- Existência da variável acidente_fatal.
- Coerência dos totais de acidentes, mortos, feridos e acidentes fatais.

## 2. Resultados

Quantidade de linhas é 72529 por DAX: Colunas = COUNTROWS('acidentes2025')   
Quantidade de colunas é 33 por DAX: Colunas = COUNTROWS( INFO.VIEW.COLUMNS() )   
Tipos de dados são texto e número inteiro.
br mudou-se de número para texto.
Nomes dos campos:
id
data_inversa
dia_semana
horario
uf
br
km
municipio
causa_acidente
tipo_acidente
classificacao_acidente
fase_dia
sentido_via
condicao_metereologica
tipo_pista
tracado_via
uso_solo
pessoas
mortos
feridos_leves
feridos_graves
ilesos
ignorados
feridos
veiculos
latitude
longitude
regional
delegacia
uop
acidente_fatal
mes
por Power Query:
let
    Source = acidentes2025,
    ColumnNames = Table.ColumnNames(Source)
in
    ColumnNames   
Coerente com consultas anteriores feitas por Python e Excel.
Encodificador é UTF-8 e delimitador é ;, pego por Power Query ao importar a base:
= Csv.Document(File.Contents("C:\Users\Admin\1ulisses\dev\fap-2026\pbi\01_mod_6\dados\acidentes2025.csv"),[Delimiter=",", Columns=32, Encoding=65001, QuoteStyle=QuoteStyle.None])
Variável acidente_fatal já feita anteriormente.
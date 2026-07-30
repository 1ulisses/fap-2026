-- =====================================
-- IMPORTAÇÃO
-- =====================================
CREATE OR REPLACE TABLE acidentes_prf_2025 AS
SELECT *
FROM read_csv_auto(
        'dados_brutos/acidentes2025.csv',
        delim = ';',
        header = true,
        sample_size = -1,
        encoding = 'latin-1'
    );
-- View e acidente_fatal
CREATE OR REPLACE VIEW vw_acidentes_base AS
SELECT *,
    CASE
        WHEN CAST (mortos AS INTEGER) >= 1 THEN 1
        ELSE 0
    END AS acidente_fatal,
    EXTRACT(
        MONTH
        FROM CAST(data_inversa AS DATE)
    ) AS mes
FROM acidentes_prf_2025;
-- =====================================
-- CONSULTAS UNIVARIADAS
-- =====================================
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY uf
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY br
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY municipio
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY mes
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY causa_acidente
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY tipo_acidente
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY fase_dia
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY condicao_metereologica
LIMIT 10;
SELECT uf,
    br,
    municipio,
    mes,
    causa_acidente,
    tipo_acidente,
    fase_dia,
    condicao_metereologica,
    tipo_pista
FROM vw_acidentes_base
ORDER BY tipo_pista
LIMIT 10;
-- =====================================
-- CONSULTAS BIVARIADAS
-- =====================================
-- Total acidentes
SELECT COUNT(*) AS total_acidentes
FROM vw_acidentes_base
LIMIT 10;
-- Total fatalidades
SELECT SUM(CAST(acidente_fatal AS INTEGER)) AS total_fatais
from vw_acidentes_base
LIMIT 10;
-- Percentual fatalidades
SELECT ROUND(100.0 * SUM(acidente_fatal) / COUNT(*), 2) AS perc_fatais
FROM vw_acidentes_base;
-- Having
SELECT tipo_pista,
    COUNT(*) AS total_acidentes,
    SUM(acidente_fatal) AS acidentes_fatais,
    ROUND(100.0 * SUM(acidente_fatal) / COUNT(*), 2) AS perc_fatais
FROM vw_acidentes_base
GROUP BY tipo_pista
HAVING COUNT(*) >= 100
ORDER BY perc_fatais DESC;
SELECT uf,
    COUNT(*) AS total_acidentes,
    SUM(acidente_fatal) AS acidentes_fatais,
    ROUND(100.0 * SUM(acidente_fatal) / COUNT(*), 2) AS perc_fatais
FROM vw_acidentes_base
GROUP BY uf
HAVING COUNT(*) >= 100
ORDER BY perc_fatais DESC;
SELECT uf,
    municipio,
    COUNT(*) AS total_acidentes,
    SUM(acidente_fatal) AS acidentes_fatais,
    SUM(CAST(mortos AS INTEGER)) AS total_mortos,
    ROUND(100.0 * SUM(acidente_fatal) / COUNT(*), 2) AS perc_fatais
FROM vw_acidentes_base
GROUP BY uf,
    municipio
HAVING COUNT(*) >= 50
ORDER BY total_mortos DESC
LIMIT 30;
-- Views analíticas
CREATE OR REPLACE VIEW vw_indicadores_mensais AS WITH base AS (
        SELECT EXTRACT(
                YEAR
                FROM CAST(data_inversa AS DATE)
            ) AS ano,
            EXTRACT(
                MONTH
                FROM CAST(data_inversa AS DATE)
            ) AS mes,
            CAST(mortos AS INTEGER) AS mortos,
            acidente_fatal
        FROM vw_acidentes_base
    )
SELECT ano,
    mes,
    COUNT(*) AS total_acidentes,
    SUM(mortos) AS total_mortos,
    SUM(acidente_fatal) AS acidentes_fatais,
    ROUND(100.0 * SUM(acidente_fatal) / COUNT(*), 2) AS perc_fatais
FROM base
GROUP BY ano,
    mes
ORDER BY ano,
    mes;
CREATE OR REPLACE VIEW vw_indicadores_uf_br AS
SELECT uf,
    br,
    COUNT(*) AS total_acidentes,
    SUM(CAST(mortos AS INTEGER)) AS total_mortos,
    SUM(acidente_fatal) AS acidentes_fatais,
    ROUND(100.0 * SUM(acidente_fatal) / COUNT(*), 2) AS perc_fatais
FROM vw_acidentes_base
WHERE br IS NOT NULL
GROUP BY uf,
    br;
CREATE OR REPLACE VIEW vw_bivariada_tipo_acidente AS WITH global AS (
        SELECT 1.0 * SUM(acidente_fatal) / COUNT(*) AS taxa_global
        FROM vw_acidentes_base
    )
SELECT tipo_acidente AS categoria,
    COUNT(*) AS total_acidentes,
    SUM(acidente_fatal) AS acidentes_fatais,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS perc_total,
    ROUND(100.0 * SUM(acidente_fatal) / COUNT(*), 2) AS perc_fatais,
    ROUND(
        (1.0 * SUM(acidente_fatal) / COUNT(*)) / g.taxa_global,
        2
    ) AS lift
FROM vw_acidentes_base
    CROSS JOIN global g
GROUP BY tipo_acidente,
    g.taxa_global
HAVING COUNT(*) >= 100;
-- DESAFIO
-- n1
SELECT dia_semana,
    COUNT(*) AS total_acidentes
FROM vw_acidentes_base
GROUP BY dia_semana
ORDER BY total_acidentes DESC;
-- n2
SELECT municipio,
    COUNT(*) AS total_acidentes
FROM vw_acidentes_base
GROUP BY municipio
ORDER BY total_acidentes DESC
LIMIT 15;
-- n3
SELECT br,
    AVG(veiculos) AS media_veiculos,
    COUNT(*) AS total_acidentes
FROM vw_acidentes_base
GROUP BY br
HAVING COUNT(*) >= 100
ORDER BY media_veiculos DESC;
-- n4
SELECT uf,
    COUNT(*) AS total_acidentes_noite
FROM vw_acidentes_base
WHERE fase_dia IN ('Plena Noite', 'Anoitecer')
GROUP BY uf
ORDER BY total_acidentes_noite DESC;
-- n5
SELECT tipo_pista,
    COUNT(*) AS total_acidentes
FROM vw_acidentes_base
GROUP BY tipo_pista
ORDER BY total_acidentes DESC;
-- n6
SELECT uf,
    fase_dia,
    COUNT(*) AS total_ocorrencias,
    (SUM(acidente_fatal) * 100.0 / COUNT(*)) AS percentual_fatal
FROM vw_acidentes_base
GROUP BY uf,
    fase_dia
HAVING COUNT(*) >= 50
ORDER BY percentual_fatal DESC;
-- n7
SELECT tipo_acidente,
    AVG(pessoas) AS media_pessoas
FROM vw_acidentes_base
GROUP BY tipo_acidente
ORDER BY media_pessoas DESC;
-- n8
SELECT causa_acidente,
    SUM(mortos) AS total_mortos
FROM vw_acidentes_base
GROUP BY causa_acidente
ORDER BY total_mortos DESC
LIMIT 5;
-- n9
SELECT uso_solo,
    COUNT(*) AS total_acidentes,
    (SUM(acidente_fatal) * 100.0 / COUNT(*)) AS percentual_fatal
FROM vw_acidentes_base
GROUP BY uso_solo
ORDER BY percentual_fatal DESC;
-- n10
SELECT municipio,
    COUNT(*) AS total_acidentes_chuva
FROM vw_acidentes_base
WHERE condicao_metereologica = 'Chuva'
GROUP BY municipio
HAVING COUNT(*) >= 30
ORDER BY total_acidentes_chuva DESC;
-- n11
SELECT tipo_acidente,
    condicao_metereologica,
    COUNT(*) AS total_ocorrencias,
    (SUM(acidente_fatal) * 100.0 / COUNT(*)) AS percentual_fatal
FROM vw_acidentes_base
GROUP BY tipo_acidente,
    condicao_metereologica
HAVING COUNT(*) >= 50
ORDER BY percentual_fatal DESC;
-- n12
SELECT uf,
    COUNT(*) AS total_acidentes,
    SUM(acidente_fatal) AS total_acidentes_fatais,
    (SUM(acidente_fatal) * 100.0 / COUNT(*)) AS percentual_fatal,
    SUM(mortos) AS total_mortos
FROM vw_acidentes_base
GROUP BY uf
ORDER BY percentual_fatal DESC;
-- =====================================
-- EXPORTAÇÃO
-- =====================================
COPY vw_acidentes_base TO 'resultados/acidentes_base.csv' (HEADER, DELIMITER ';');
COPY vw_indicadores_uf_br TO 'resultados/indicadores_uf_br.csv'(HEADER, DELIMITER ';');
COPY vw_indicadores_mensais TO 'resultados/indicadores_mensais.csv' (HEADER, DELIMITER ';');
COPY vw_bivariada_tipo_acidente TO 'resultados/bivariada_tipo.csv'(HEADER, DELIMITER ';');
COPY (
    SELECT data_inversa,
        dia_semana,
        horario,
        uf,
        br,
        municipio,
        causa_acidente,
        tipo_acidente,
        classificacao_acidente,
        fase_dia,
        condicao_meteorologica,
        tipo_pista,
        tracado_via,
        uso_solo,
        mortos,
        acidente_fatal
    FROM vw_acidentes_base
) TO 'resultados/base_analitica_sql.csv' (HEADER, DELIMITER ';');
COPY (
    SELECT uf,
        br,
        municipio,
        EXTRACT(
            MONTH
            FROM CAST(data_inversa AS DATE)
        ) AS mes,
        dia_semana,
        fase_dia,
        causa_acidente,
        tipo_acidente,
        condicao_meteorologica,
        tipo_pista,
        tracado_via,
        uso_solo,
        acidente_fatal
    FROM vw_acidentes_base
) TO 'resultados/base_modelavel_preliminar_sql.csv' (HEADER, DELIMITER ';');
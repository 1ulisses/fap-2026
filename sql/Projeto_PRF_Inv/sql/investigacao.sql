-- Importação e Criação
--
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
--
CREATE OR REPLACE VIEW vw_acidentes_base AS
SELECT *
FROM acidentes_prf_2025;

-- DESAFIO 1
-- INTERPRETAÇÃO: BA e PE com maior gravidade entre os maiores.
-- Maior taxa de fatalidade embora não tenham maior número de acidentes.
-- Taxas de fatalidade acima da média nacional.
-- Possíveis problemas de infraestrutura, atendimendo, etc.
--
WITH media_nacional AS (
    SELECT
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal_nacional
    FROM
        vw_acidentes_base
),

uf_stats AS (
    SELECT
        uf,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        vw_acidentes_base
    GROUP BY uf
    HAVING count(*) >= 1500
)

SELECT
    uf,
    total_acidentes,
    fatais,
    pct_fatal,
    (SELECT pct_fatal_nacional FROM media_nacional) AS media_nacional,
    CASE
        WHEN
            pct_fatal > (SELECT pct_fatal_nacional FROM media_nacional)
            THEN 'ACIMA'
        ELSE 'ABAIXO'
    END AS comparacao
FROM uf_stats
ORDER BY pct_fatal DESC;

-- DESAFIO 2
-- INTERPRETAÇÃO: 423, 242, 222 com alta letalidade sem serem as mais
-- movimentadas.
--

WITH br_stats AS (
    SELECT
        br,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        vw_acidentes_base
    GROUP BY br
    HAVING count(*) >= 100
),

br_top_volume AS (
    SELECT br
    FROM br_stats
    ORDER BY total_acidentes DESC
    LIMIT 10
)

SELECT
    br,
    total_acidentes,
    fatais,
    pct_fatal,
    rank() OVER (ORDER BY total_acidentes DESC) AS ranking_volume,
    rank() OVER (ORDER BY pct_fatal DESC) AS ranking_gravidade
FROM br_stats
WHERE br NOT IN (SELECT br FROM br_top_volume)
ORDER BY pct_fatal DESC
LIMIT 15;

-- DESAFIO 3
--

WITH faixas_horarias AS (
    SELECT
        horario,
        mortos,
        CASE extract(HOUR FROM horario)
            WHEN 0 THEN '00h-05h' WHEN 1 THEN '00h-05h' WHEN 2 THEN '00h-05h'
            WHEN 3 THEN '00h-05h' WHEN 4 THEN '00h-05h' WHEN 5 THEN '00h-05h'
            WHEN 6 THEN '06h-11h' WHEN 7 THEN '06h-11h' WHEN 8 THEN '06h-11h'
            WHEN 9 THEN '06h-11h' WHEN 10 THEN '06h-11h' WHEN 11 THEN '06h-11h'
            WHEN 12 THEN '12h-17h' WHEN 13 THEN '12h-17h' WHEN 14 THEN '12h-17h'
            WHEN 15 THEN '12h-17h' WHEN 16 THEN '12h-17h' WHEN 17 THEN '12h-17h'
            ELSE '18h-23h'
        END AS faixa_horaria
    FROM vw_acidentes_base
)

SELECT
    faixa_horaria,
    count(*) AS total_acidentes,
    sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
    round(100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2)
        AS pct_fatal,
    round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_distribuicao
FROM faixas_horarias
GROUP BY faixa_horaria
ORDER BY pct_fatal DESC;

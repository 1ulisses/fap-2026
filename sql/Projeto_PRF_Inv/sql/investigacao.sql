-- Importação e Criação

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

SELECT '================= DESAFIO 1 =================' AS separator;

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

SELECT '================= DESAFIO 2 =================' AS separator;

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
-- INTERPRETAÇÃO: 00h-05h é horário mais fatal, embora onde ocorra menos
-- acidentes.
-- Possivelmente por fadiga, baixa visibilidade ou falta de resposta.
-- 12h-17h horário com menos fatalidades.

SELECT '================= DESAFIO 3 =================' AS separator;

WITH faixas_horarias AS (
    SELECT
        horario,
        mortos,
        CASE
            WHEN extract(HOUR FROM horario) < 6 THEN '00h-05h'
            WHEN extract(HOUR FROM horario) < 12 THEN '06h-11h'
            WHEN extract(HOUR FROM horario) < 18 THEN '12h-17h'
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

-- DESAFIO 4
-- INTERPRETAÇÃO: Colisão traseira mais comum em dia e noite.
-- Colisão tranversal 2o mais comum ao dia e
-- Saida de leito carroçável 2o mais comum a noite.
-- Saida de leito possivelmente causado por mal visibilidade.

SELECT '================= DESAFIO 4 =================' AS separator;

WITH dia_noite AS (
    SELECT
        tipo_acidente,
        CASE
            WHEN
                cast(
                    extract(HOUR FROM cast(horario AS TIME)) AS INTEGER
                ) BETWEEN 6 AND 18
                THEN 'Dia (06h-18h)'
            ELSE 'Noite (18h-06h)'
        END AS periodo,
        mortos
    FROM vw_acidentes_base
)

SELECT
    periodo,
    tipo_acidente,
    count(*) AS total,
    round(100.0 * count(*) / sum(count(*)) OVER (PARTITION BY periodo), 2)
        AS pct_no_periodo,
    rank() OVER (PARTITION BY periodo ORDER BY count(*) DESC) AS ranking
FROM dia_noite
GROUP BY periodo, tipo_acidente
QUALIFY RANK() OVER (PARTITION BY periodo ORDER BY COUNT(*) DESC) <= 5
ORDER BY periodo, ranking;

-- DESAFIO 5
-- Neblina é 50% maior que a média nacional.
-- Neblina possivelmente diminui a visibilidade causando mais acidentes.

SELECT '================= DESAFIO 5 =================' AS separator;

WITH media_nacional AS (
    SELECT
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal_nacional
    FROM
        vw_acidentes_base
),

clima_stats AS (
    SELECT
        condicao_metereologica,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        vw_acidentes_base
    GROUP BY condicao_metereologica
    HAVING count(*) >= 500
)

SELECT
    condicao_metereologica,
    total_acidentes,
    fatais,
    pct_fatal,
    (SELECT pct_fatal_nacional FROM media_nacional) AS media_nacional,
    round(pct_fatal / (SELECT pct_fatal_nacional FROM media_nacional), 2)
        AS vezes_media,
    CASE
        WHEN
            pct_fatal >= 1.5 * (SELECT pct_fatal_nacional FROM media_nacional)
            THEN 'ALTO RISCO'
        ELSE 'NORMAL'
    END AS classificacao
FROM clima_stats
ORDER BY pct_fatal DESC;

-- DESAFIO 6
-- INTERPRETAÇÃO: Munícios com mais acidentes e fatalidades abaixo da média são
-- Brasília(DF), Duque de Caxias(RJ) e São José(SC).
-- possivelmente indica bom atendimendo médico, baixa velocidade nos acidentes
-- ou melhor infraestrutura urbana.

SELECT '================= DESAFIO 6 =================' AS separator;

WITH media_nacional AS (
    SELECT
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal_nacional
    FROM
        vw_acidentes_base
),

municipio_stats AS (
    SELECT
        municipio,
        uf,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        vw_acidentes_base
    GROUP BY municipio, uf
)

SELECT
    municipio,
    uf,
    total_acidentes,
    fatais,
    pct_fatal,
    (SELECT pct_fatal_nacional FROM media_nacional) AS media_nacional,
    round((SELECT pct_fatal_nacional FROM media_nacional) - pct_fatal, 2)
        AS diferenca
FROM municipio_stats
WHERE pct_fatal < (SELECT pct_fatal_nacional FROM media_nacional)
ORDER BY total_acidentes DESC
LIMIT 20;

-- DESAFIO 7
-- INTERPRETAÇÃO: Pista simples e Reta;Ponte (16.57) é a combinação mais fatal,
-- seguida por Simples e Aclive;Reta (15.76) e Simples e Curva;Declive (14.93).

SELECT '================= DESAFIO 7 =================' AS separator;

WITH pista_tracado AS (
    SELECT
        tipo_pista,
        tracado_via,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        vw_acidentes_base
    GROUP BY tipo_pista, tracado_via
    HAVING count(*) >= 100
)

SELECT
    tipo_pista,
    tracado_via,
    total_acidentes,
    fatais,
    pct_fatal,
    rank() OVER (ORDER BY pct_fatal DESC) AS ranking_gravidade
FROM pista_tracado
ORDER BY pct_fatal DESC
LIMIT 15;

-- DESAFIO 8
-- INTERPRETAÇÃO: Causas relacionadas a pedestres
-- possuem baixa cobertura (<1%) mais alta fatalidade:
-- "Suicídio (presumido)" (55.79%), "Pedestre andava na pista" (41.25%) e
-- "Entrada inopinada do pedestre" (30.43%)

SELECT '================= DESAFIO 8 =================' AS separator;

WITH causa_stats AS (
    SELECT
        causa_acidente,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal,
        round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_cobertura
    FROM
        vw_acidentes_base
    GROUP BY causa_acidente
    HAVING count(*) >= 50
)

SELECT
    causa_acidente,
    total_acidentes,
    pct_cobertura,
    fatais,
    pct_fatal,
    CASE
        WHEN pct_fatal > 15 THEN 'MUITO ALTA' WHEN
            pct_fatal > 10
            THEN 'ALTA'
        ELSE 'NORMAL'
    END AS nivel_letalidade
FROM causa_stats
ORDER BY pct_fatal DESC
LIMIT 15;

-- DESAFIO 9

SELECT '================= DESAFIO 9 =================' AS separator;

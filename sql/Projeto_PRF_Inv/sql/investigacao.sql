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
-- Neblina (51%) é 50% maior que a média nacional de fatalidade.
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
-- Acidentes relacionados a pedestres possuem maior fatalidade

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
-- INTERPRETAÇÃO: Taxa de fatalidade variou entre 6.49% (Jan.) e 8.27% (Mai.)
-- tendência fraca a aumentar (6x aumentor vs 5x diminuiu)
-- Possivelmente por motivos sazonais ou eventos

SELECT '================= DESAFIO 9 =================' AS separator;

WITH mes_stats AS (
    SELECT
        extract(MONTH FROM cast(data_inversa AS DATE)) AS mes,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        vw_acidentes_base
    GROUP BY extract(MONTH FROM cast(data_inversa AS DATE))
)

SELECT
    mes,
    total_acidentes,
    fatais,
    pct_fatal,
    lag(pct_fatal) OVER (ORDER BY mes) AS pct_fatal_mes_anterior,
    CASE
        WHEN pct_fatal > lag(pct_fatal) OVER (ORDER BY mes) THEN 'AUMENTOU'
        WHEN pct_fatal < lag(pct_fatal) OVER (ORDER BY mes) THEN 'DIMINUIU'
        ELSE 'ESTÁVEL'
    END AS tendencia
FROM mes_stats
ORDER BY mes;

-- DESAFIO 10
-- INTERPRETAÇÃO: Tipos de acidente com maior lift são: Atropelamento(4.1),
-- Colisão frontal(4.1) e Colisão lateral sentido oposto(1.37)
-- Tipos com menor lift são: Incêndio(0.0), Engavetamento(0.31) e
-- Queda de ocupante do veículo(0.35).
-- Acidentes envolvendo pedestres e acidentes violentos são mais fatais que
-- o contrário.

SELECT '================= DESAFIO 10 =================' AS separator;

WITH global_rate AS (
    SELECT
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 3
        ) AS taxa_global
    FROM
        vw_acidentes_base
),

tipo_stats AS (
    SELECT
        tipo_acidente,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 3
        ) AS taxa_segmento
    FROM
        vw_acidentes_base
    GROUP BY tipo_acidente
    HAVING count(*) >= 100
)

SELECT
    tipo_acidente,
    total_acidentes,
    taxa_segmento,
    (SELECT taxa_global FROM global_rate) AS taxa_global,
    round(taxa_segmento / (SELECT taxa_global FROM global_rate), 3) AS lift,
    CASE
        WHEN
            taxa_segmento / (SELECT taxa_global FROM global_rate) > 2
            THEN 'MUITO ALTO'
        WHEN
            taxa_segmento / (SELECT taxa_global FROM global_rate) > 1.5
            THEN 'ALTO'
        WHEN
            taxa_segmento / (SELECT taxa_global FROM global_rate) > 1
            THEN 'ACIMA MÉDIA'
        ELSE 'ABAIXO MÉDIA'
    END AS classificacao_risco
FROM tipo_stats
ORDER BY lift DESC;

-- DESAFIO 11
-- INTERPRETAÇÃO: Amanhecer, Simples e Céu Claro(15.69%),
-- Plena noite, Simples, Ignorado(13.61%) e Céu claro(13.45%)
-- são as 3 combinações mais fatais.
-- Plena noite, Simples e Céu claro possui maior volume 11.52%.
-- Plena noite domina ranking possivelmente devido a baixa visibilidade e fadiga

SELECT '================= DESAFIO 11 =================' AS separator;

WITH perfil_risco AS (
    SELECT
        fase_dia,
        tipo_pista,
        condicao_metereologica,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        vw_acidentes_base
    GROUP BY fase_dia, tipo_pista, condicao_metereologica
    HAVING count(*) >= 200
)

SELECT
    fase_dia,
    tipo_pista,
    condicao_metereologica,
    total_acidentes,
    fatais,
    pct_fatal,
    round(100.0 * total_acidentes / sum(total_acidentes) OVER (), 2)
        AS pct_base_total,
    rank() OVER (ORDER BY pct_fatal DESC) AS ranking
FROM perfil_risco
WHERE pct_fatal > 7.18
ORDER BY pct_fatal DESC
LIMIT 10;

-- DESAFIO 12
-- HIPÓTESE: Acidentes a noite em pistas simples são mais fatais que outras
-- combinações, devido a baixa visibilidade, separação física das ruas e fadiga
-- do condutor, possivelmente após a jornada de trabalho.
-- RESULTADO: Noite e Pista simples possui 14564 acidentes e 1899 fatais com 13%
-- de porcentagem de fatalidade.
-- CONCLUSÃO: Confirmado

SELECT '================= DESAFIO 12 =================' AS separator;

WITH hipotese_teste AS (
    SELECT
        CASE
            WHEN
                (
                    cast(extract(HOUR FROM cast(horario AS TIME)) AS INTEGER)
                    >= 18
                    OR cast(extract(HOUR FROM cast(horario AS TIME)) AS INTEGER)
                    <= 5
                )
                AND tipo_pista = 'Simples'
                THEN 'Noite_Pista_Simples'
            ELSE 'Outros'
        END AS grupo,
        count(*) AS total_acidentes,
        sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) AS fatais,
        round(
            100.0 * sum(CASE WHEN mortos >= 1 THEN 1 ELSE 0 END) / count(*), 2
        ) AS pct_fatal
    FROM
        read_csv_auto(
            'dados_brutos/acidentes2025.csv',
            delim = ';',
            header = true,
            encoding = 'latin-1'
        )
    GROUP BY
        CASE
            WHEN
                (
                    cast(extract(HOUR FROM cast(horario AS TIME)) AS INTEGER)
                    >= 18
                    OR cast(extract(HOUR FROM cast(horario AS TIME)) AS INTEGER)
                    <= 5
                )
                AND tipo_pista = 'Simples'
                THEN 'Noite_Pista_Simples'
            ELSE 'Outros'
        END
)

SELECT
    grupo,
    total_acidentes,
    fatais,
    pct_fatal,
    round(pct_fatal / lag(pct_fatal) OVER (ORDER BY pct_fatal), 2)
        AS vezes_maior
FROM hipotese_teste
ORDER BY pct_fatal DESC;

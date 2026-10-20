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
-- OBJETIVO: Identificar UFs com mais de 1500 acidentes e percentual de fatalidade acima da média nacional.
-- INTERPRETAÇÃO: BA (11.59%) e PE (10.02%) lideram em gravidade entre estados com alto volume, ambos
-- significativamente acima da média nacional (7.18%). MS (8.22%), MT (7.74%) e GO (7.73%) também estão
-- acima da média. Estados com maior volume como SP (4.38%), SC (4.57%) e RJ (4.76%) têm taxas abaixo
-- da média, possivelmente indicando melhor infraestrutura, fiscalização ou atendimento médico.

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
-- OBJETIVO: Identificar BRs com alta proporção de acidentes fatais que não estão entre as top 10 em volume.
-- INTERPRETAÇÃO: BR-423 (21.86%), BR-242 (19.08%) e BR-222 (18.24%) lideram em gravidade sem estar entre
-- as mais movimentadas. Estas rodovias apresentam risco desproporcional: embora tenham volume moderado
-- (entre 183 e 581 acidentes), suas taxas de fatalidade são 2.5x a 3x maiores que a média nacional (7.18%).
-- Isso indica necessidade de atenção especial nestas vias, possivelmente por características estruturais
-- críticas, fiscalização insuficiente ou trechos perigosos específicos.

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
-- OBJETIVO: Identificar faixa horária com maior proporção de acidentes fatais.
-- INTERPRETAÇÃO: Faixa 00h-05h tem maior taxa de fatalidade (12.1%), apesar de concentrar apenas 12.28%
-- dos acidentes. Em contraste, 12h-17h (30.75% dos acidentes) tem menor taxa (5.53%). O período noturno
-- (18h-23h) também apresenta alta letalidade (9.13%) com grande volume (28.21%). A maior gravidade na
-- madrugada sugere influência de fadiga, baixa visibilidade, velocidade excessiva ou demora no atendimento.

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
-- OBJETIVO: Comparar tipos de acidente mais frequentes entre dia e noite para identificar mudança de padrão.
-- INTERPRETAÇÃO: Colisão traseira é a mais comum em ambos períodos (Dia: 21.24%, Noite: 17.69%).
-- Durante o dia, Colisão transversal é 2ª (14.46%). À noite, Saída de leito carroçável sobe para 2º lugar
-- (15.31% vs 13.23% no dia), indicando maior risco de perda de controle possivelmente por baixa visibilidade
-- e fadiga. A mudança de padrão sugere que acidentes dinâmicos são mais frequentes à noite.

SELECT '================= DESAFIO 4 =================' AS separator;

WITH dia_noite AS (
    SELECT
        tipo_acidente,
        CASE
            WHEN
                cast(
                    extract(HOUR FROM cast(horario AS TIME)) AS INTEGER
                ) BETWEEN 6 AND 17
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
-- INTERPRETAÇÃO: Nevoeiro/Neblina (10.85%) apresenta taxa 1.51x maior que a média nacional (7.18%),
-- sendo a única condição com volume relevante (>500) classificada como ALTO RISCO.
-- Isso representa um aumento de 51% em relação à média, confirmando que neblina aumenta
-- significativamente a gravidade dos acidentes, possivelmente por reduzir visibilidade e
-- tempo de reação dos condutores.

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
-- INTERPRETAÇÃO: Brasília (DF), Duque de Caxias (RJ) e São José (SC) lideram em volume de acidentes
-- com fatalidade abaixo da média nacional (7.18%). Brasília tem 1011 acidentes e apenas 4.25% de
-- fatalidade, possivelmente indicando melhor infraestrutura urbana, atendimento médico rápido ou
-- menor velocidade média nas vias. A baixa letalidade apesar do alto volume sugere fatores
-- protetivos como fiscalização eficiente ou características das rodovias.

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
-- INTERPRETAÇÃO: Pista Simples combinada com Reta;Ponte (16.57%) tem maior taxa de fatalidade,
-- seguida por Simples com Aclive;Reta (15.76%) e Curva;Declive (14.93%). A combinação de pista
-- simples com elementos que exigem maior controle do veículo (pontes, aclives, curvas) apresenta
-- risco elevado, possivelmente devido à ausência de separação física entre fluxos opostos e
-- menor margem de erro em situações críticas.

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
-- INTERPRETAÇÃO: Causas relacionadas a pedestres dominam o topo: "Suicídio (presumido)" (55.79%),
-- "Pedestre andava na pista" (41.25%) e "Entrada inopinada do pedestre" (30.43%) têm alta letalidade
-- mas baixa cobertura (<1% cada). "Transitar na contramão" (29.74%) e "Ultrapassagem Indevida"
-- (17.06%) também são altamente letais. Eventos raros envolvendo pedestres ou manobras críticas
-- tendem a ser mais graves, indicando vulnerabilidade e necessidade de prevenção específica.

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
-- INTERPRETAÇÃO: A taxa de fatalidade variou entre 6.49% (janeiro) e 8.27% (maio), com tendência
-- relativamente estável ao longo de 2025. Houve 6 aumentos e 5 diminuições mês a mês, sem padrão
-- claro de crescimento ou queda sustentada. Maio apresentou o pico (8.27%), possivelmente associado
-- a fatores sazonais como feriados ou condições climáticas, mas a taxa geral permaneceu próxima
-- da média nacional de 7.18%.

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
-- INTERPRETAÇÃO: "Atropelamento de Pedestre" (Lift=4.1) e "Colisão frontal" (Lift=4.1) têm maior
-- risco relativo, sendo mais de 4 vezes mais letais que a média global (7.183%). "Colisão lateral
-- sentido oposto" (Lift=1.37) também está acima da média. Tipos com menor lift: "Incêndio" (0.0),
-- "Engavetamento" (0.32) e "Queda de ocupante" (0.35). Acidentes envolvendo pedestres ou impacto
-- frontal direto são desproporcionalmente mais graves, indicando alta vulnerabilidade nesses cenários.

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
-- INTERPRETAÇÃO: "Amanhecer + Pista Simples + Céu Claro" (15.69%) tem maior taxa de fatalidade,
-- seguido por "Plena Noite + Simples + Ignorado" (13.61%) e "Plena Noite + Simples + Céu Claro"
-- (13.45%). Este último também tem maior volume (19.71% da base). Perfis noturnos e de amanhecer
-- em pista simples dominam o ranking, sugerindo que baixa luminosidade combinada com infraestrutura
-- mais vulnerável aumenta significativamente o risco de fatalidade.

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
-- HIPÓTESE: "Acidentes noturnos em pista simples são mais letais que outras combinações, devido à
-- baixa visibilidade, ausência de separação física entre fluxos opostos e possível fadiga dos
-- condutores após jornada de trabalho."
-- RESULTADO: Grupo "Noite_Pista_Simples" tem 14.564 acidentes com 13.04% de fatalidade, enquanto
-- "Outros" têm 57.965 acidentes com 5.71% de fatalidade. O grupo da hipótese é 2.28x mais letal.
-- CONCLUSÃO: CONFIRMADA - Acidentes noturnos em pista simples apresentam taxa de fatalidade
-- significativamente maior (13.04% vs 5.71%), validando a hipótese de maior risco neste contexto.

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

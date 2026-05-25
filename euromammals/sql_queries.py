QUERY_GPS_DEER_RESEARCH_GROUP = """
WITH animals_by_research_group AS (
    SELECT
        s.research_groups_id,
        SUM(q.n_animals) AS n_animals
    FROM main.study_areas s,(
    SELECT
        a.study_areas_id,
        COUNT(DISTINCT a.animals_id) AS n_animals
    FROM main.animals a
    WHERE a.gps_data = true
    GROUP BY a.study_areas_id) as q
    WHERE s.study_areas_id = q.study_areas_id
    GROUP BY s.research_groups_id
),

gps_time_by_area AS (
    SELECT
        s.research_groups_id,
        MIN(q.gps_min_start_time) AS gps_min_start_time,
        MAX(q.gps_max_end_time) AS gps_max_end_time
    FROM main.study_areas s,(
    SELECT
        a.study_areas_id,
        MIN(gsa.start_time) AS gps_min_start_time,
        MAX(gsa.end_time)   AS gps_max_end_time
    FROM main.animals a
    JOIN main.gps_sensors_animals gsa
        ON gsa.animals_id = a.animals_id
    WHERE a.gps_data = true
    GROUP BY a.study_areas_id) as q
    WHERE s.study_areas_id = q.study_areas_id
    GROUP BY s.research_groups_id
)

SELECT
    sa.research_groups_id,
    sa.research_group_name as study_name,
    sa.short_name as short_name,
    COALESCE(aba.n_animals, 0) AS n_animals,
    gta.gps_min_start_time,
    gta.gps_max_end_time
FROM main.research_groups sa
JOIN gps_time_by_area gta
    ON gta.research_groups_id = sa.research_groups_id
LEFT JOIN animals_by_research_group aba
    ON aba.research_groups_id = sa.research_groups_id
ORDER BY sa.research_group_name;
"""

QUERY_GPS_DEER = """
WITH animals_by_area AS (
    SELECT
        a.study_areas_id,
        COUNT(DISTINCT a.animals_id) AS n_animals
    FROM main.animals a
    WHERE a.gps_data = true
    GROUP BY a.study_areas_id
),

gps_time_by_area AS (
    SELECT
        a.study_areas_id,
        MIN(gsa.start_time) AS gps_min_start_time,
        MAX(gsa.end_time)   AS gps_max_end_time
    FROM main.animals a
    JOIN main.gps_sensors_animals gsa
        ON gsa.animals_id = a.animals_id
    WHERE a.gps_data = true
    GROUP BY a.study_areas_id
)

SELECT
    sa.study_areas_id,
    sa.study_name,
    sa.short_name as short_name,
    COALESCE(aba.n_animals, 0) AS n_animals,
    gta.gps_min_start_time,
    gta.gps_max_end_time
FROM main.study_areas sa
JOIN gps_time_by_area gta
    ON gta.study_areas_id = sa.study_areas_id
LEFT JOIN animals_by_area aba
    ON aba.study_areas_id = sa.study_areas_id
ORDER BY sa.study_name;
"""

QUERY_GPS_BOAR_RESEARCH_GROUP = """
WITH animals_by_research_group AS (
    SELECT
        s.research_groups_id,
        SUM(q.n_animals) AS n_animals
    FROM main.study_areas s,(
    SELECT
        a.study_areas_id,
        COUNT(DISTINCT a.animals_id) AS n_animals
    FROM main.animals a
    WHERE a.monitored_gps = 1
    GROUP BY a.study_areas_id) as q
    WHERE s.study_areas_id = q.study_areas_id
    GROUP BY s.research_groups_id
),

gps_time_by_area AS (
    SELECT
        s.research_groups_id,
        MIN(q.gps_min_start_time) AS gps_min_start_time,
        MAX(q.gps_max_end_time) AS gps_max_end_time
    FROM main.study_areas s,(
    SELECT
        a.study_areas_id,
        MIN(gsa.start_time) AS gps_min_start_time,
        MAX(gsa.end_time)   AS gps_max_end_time
    FROM main.animals a
    JOIN main.gps_sensors_animals gsa
        ON gsa.animals_id = a.animals_id
    WHERE a.monitored_gps = 1
    GROUP BY a.study_areas_id) as q
    WHERE s.study_areas_id = q.study_areas_id
    GROUP BY s.research_groups_id
)

SELECT
    sa.research_groups_id,
    sa.research_group_name as study_name,
    sa.short_name as short_name,
    COALESCE(aba.n_animals, 0) AS n_animals,
    gta.gps_min_start_time,
    gta.gps_max_end_time
FROM main.research_groups sa
JOIN gps_time_by_area gta
    ON gta.research_groups_id = sa.research_groups_id
LEFT JOIN animals_by_research_group aba
    ON aba.research_groups_id = sa.research_groups_id
ORDER BY sa.research_group_name;
"""

QUERY_GPS_BOAR = """
WITH animals_by_area AS (
    SELECT
        a.study_areas_id,
        COUNT(DISTINCT a.animals_id) AS n_animals
    FROM main.animals a
        --WHERE a.gps_data = true
    WHERE monitored_gps=1
    GROUP BY a.study_areas_id
),

gps_time_by_area AS (
    SELECT
        a.study_areas_id,
        MIN(gsa.start_time) AS gps_min_start_time,
        MAX(gsa.end_time)   AS gps_max_end_time
    FROM main.animals a
    JOIN main.gps_sensors_animals gsa
        ON gsa.animals_id = a.animals_id
    --WHERE a.gps_data = true
    WHERE monitored_gps=1
    GROUP BY a.study_areas_id
)

SELECT
    sa.study_areas_id,
    sa.study_name,
    sa.research_groups_id, -- wild boar
    sa.short_name as short_name,
    COALESCE(aba.n_animals, 0) AS n_animals,
    gta.gps_min_start_time,
    gta.gps_max_end_time
FROM main.study_areas sa
JOIN gps_time_by_area gta
    ON gta.study_areas_id = sa.study_areas_id
LEFT JOIN animals_by_area aba
    ON aba.study_areas_id = sa.study_areas_id
ORDER BY sa.study_name;
"""

SQL_QUERIES_LYNX = """
WITH animals_by_area AS (
    SELECT
        a.research_groups_id,
        COUNT(DISTINCT a.animals_id) AS n_animals
    FROM main.animals a
    WHERE a.gps_data = true
    GROUP BY a.research_groups_id
),

gps_time_by_area AS (
    SELECT
        a.research_groups_id,
        MIN(gsa.start_time) AS gps_min_start_time,
        MAX(gsa.end_time)   AS gps_max_end_time
    FROM main.animals a
    JOIN main.gps_sensors_animals gsa
        ON gsa.animals_id = a.animals_id
    WHERE a.gps_data = true
    GROUP BY a.research_groups_id
)

SELECT
    sa.research_groups_id,
    sa.research_group_name as study_name,
    sa.short_name as short_name,
    COALESCE(aba.n_animals, 0) AS n_animals,
    gta.gps_min_start_time,
    gta.gps_max_end_time
FROM main.research_groups sa
JOIN gps_time_by_area gta
    ON gta.research_groups_id = sa.research_groups_id
LEFT JOIN animals_by_area aba
    ON aba.research_groups_id = sa.research_groups_id
ORDER BY sa.research_group_name;
"""

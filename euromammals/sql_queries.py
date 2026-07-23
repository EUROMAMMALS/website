QUERY_GPS_DEER_RESEARCH_GROUP = """
WITH animals_by_research_group AS (
    SELECT
        s.research_groups_id,
        SUM(q.n_animals) AS n_animals
    FROM 
        main.study_areas s,
        (
            SELECT
                a.study_areas_id,
                COUNT(DISTINCT a.animals_id) AS n_animals
            FROM main.animals a
            WHERE a.gps_data = true
            GROUP BY a.study_areas_id
        ) as q
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


QUERY_METADATA = """
SELECT 
    ---<title>
    'GPS Data Collection for Movement Ecology Studies in' || ' ' || study_name title,
    contact.research_groups_id,
    s.study_area_description,
    ---<creator>
    ---<creator>1
    ---<individualName>
    givenName1,
    surName1,
    electronicmailaddress1,
    ---</individualName>
    ---<organizationName>
    contact.organization_name || ' - ' || contact.research_group_name organizationName1,
    contact.country as country1,
    s.study_areas_id as study_areas_id1,
    'Research' positionName1,
    webpage onlineUrl1,
    ---<creator>2
    ---<individualName>
    givenName2,
    surName2,
    electronicmailaddress2,
    ---</individualName>
    ---<organizationName>
    contact.organization_name || ' - ' || contact.research_group_name organizationName2,
    contact.country country2,
    s.study_areas_id as study_areas_id2,
    'Research' positionName2,
    webpage onlineUrl2,
    ---</creator>
    ---<metadataProvider> viene assegnato al nome l'appellativo di Metadata Provider 
    'EUROMAMMALS' metadataProvider_givenName,
    'EUROMAMMALS' metadataProvider_surName,
    'EUROMAMMALS' metadataProvider_organizationName,
    'https://euromammals.org/' metadataProvider_electronicMailAddress, 
    ---</metadataProvider>
    'MovementEcology; Mammals; Bio-logging; GPS telemetry' keyword,
    'This work is licensed under a xxxxx' intellectualRights,--------<para>
    ---geographicCoveragedb_default
    min_x, --<westBoundingCoordinate> ----MIN (longitude) the longitude of the western-most point of the bounding box
    max_x, --<eastBoundingCoordinate> ----MAX(longitude) the longitude of the eastern-most point of the bounding box
    min_y, --<southBoundingCoordinate> ---MIN(latitude) the latitude of the southern-most point of the bounding box
    max_y, --<northBoundingCoordinate> --- MAX(latitude) the latitude of the northern-most point of the bounding box
    ---temporalCoverage
    begindate, enddate,
    ---<generalTaxonomicCoverage>
    count_animals,
    'European terrestrial mammals' generalTaxonomicCoverage,
    '{KINGDOM}' kindom,
    '{PHYLUM}' phylum,
    '{ORDER}' order_,
    '{FAMILY}' family_,
    '{SPECIE}' species,
    '{NAME}' commonName 
FROM 
    main.study_areas s,
    (SELECT 
        research_groups_id,
        research_group_name,
        organization_name,
        country,
        webpage,
        split_part(full_name1, ' ', 1) AS givenName1,
        substring(full_name1 FROM position(' ' IN full_name1) + 1) AS surName1,
        electronicmailaddress1,
        split_part(full_name2, ' ', 1) AS givenName2,
        substring(full_name2 FROM position(' ' IN full_name2) + 1) AS surName2,
        electronicmailaddress2,
        split_part(full_name3, ' ', 1) AS givenName3,
        substring(full_name3 FROM position(' ' IN full_name3) + 1) AS surName3,
        electronicmailaddress3,
        split_part(full_name4, ' ', 1) AS givenName4,
        substring(full_name4 FROM position(' ' IN full_name4) + 1) AS surName4,
        electronicmailaddress4
    FROM (
            SELECT 
                research_groups_id,
                research_group_name,
                organization_name,
                country,
                webpage,
                contact_people,
                split_part(contact_people, ';', 1) AS full_name1,
                split_part(contact_people, ';', 2) AS electronicmailaddress1,
                split_part(contact_people, ';', 3) AS full_name2,
                split_part(contact_people, ';', 4) AS electronicmailaddress2,
                split_part(contact_people, ';', 5) AS full_name3,
                split_part(contact_people, ';', 6) AS electronicmailaddress3,
                split_part(contact_people, ';', 7) AS full_name4,
                split_part(contact_people, ';', 8) AS electronicmailaddress4
            FROM main.research_groups
        ) subquery
    )
    contact,
    ---<geographicDescription>
    (
        SELECT
            study_areas_id,
            min(x) min_x,
            max(x) max_x,
            min(y) min_y,
            max(y) max_y
        FROM (
            WITH mbr AS (
                SELECT 
                    study_areas_id,
                    ST_Envelope(geom) AS rect_geom
                FROM main.study_areas 
                GROUP BY study_areas_id
            ),
            vertices AS (
                SELECT 
                    study_areas_id,
                    ST_ExteriorRing(rect_geom) AS ring FROM mbr
            ),
            points AS (
                SELECT 
                    study_areas_id,
                    ST_DumpPoints(ring) AS dp 
                FROM vertices
            )
            SELECT 
                study_areas_id,
                (dp).path[1] AS vertex_order,
                ST_X((dp).geom) AS x,
                ST_Y((dp).geom) AS y
            FROM points 
            ORDER BY study_areas_id, vertex_order
        ) foo
        GROUP BY study_areas_id
    ) sp_cov,
    --------<temporalCoverage>
    (
        SELECT
            study_areas_id,
            min(start_time) begindate,
            max(end_time) enddate,
            count(distinct a.animals_id) as count_animals
        FROM main.gps_sensors_animals d,  main.animals a 
        WHERE d.animals_id=a.animals_id
        GROUP BY study_areas_id
    ) temp_cov
    --------<contact>
    --------</contact>
WHERE
    contact.research_groups_id=s.research_groups_id
    AND sp_cov.study_areas_id=s.study_areas_id
    AND temp_cov.study_areas_id=s.study_areas_id
ORDER BY contact.research_groups_id, s.study_areas_id
"""


QUERY_METADATA_ID = """
SELECT 
    ---<title>
    'GPS Data Collection for Movement Ecology Studies in' || ' ' || study_name title,
    s.study_area_description,
    contact.research_groups_id,
    ---<creator>
    ---<creator>1
    ---<individualName>
    givenName1,
    surName1,
    electronicmailaddress1,
    ---</individualName>
    ---<organizationName>
    contact.organization_name || ' - ' || contact.research_group_name organizationName1,
    contact.country as country1,
    s.study_areas_id as study_areas_id1,
    'Research' positionName1,
    webpage onlineUrl1,
    ---<creator>2
    ---<individualName>
    givenName2,
    surName2,
    electronicmailaddress2,
    ---</individualName>
    ---<organizationName>
    contact.organization_name || ' - ' || contact.research_group_name organizationName2,
    contact.country country2,
    s.study_areas_id as study_areas_id2,
    'Research' positionName2,
    webpage onlineUrl2,
    ---</creator>
    ---<metadataProvider> viene assegnato al nome l'appellativo di Metadata Provider 
    'EUROMAMMALS' metadataProvider_givenName,
    'EUROMAMMALS' metadataProvider_surName,
    'EUROMAMMALS' metadataProvider_organizationName,
    'https://euromammals.org/' metadataProvider_electronicMailAddress, 
    ---</metadataProvider>
    'MovementEcology; Mammals; Bio-logging; GPS telemetry' keyword,
    'This work is licensed under a xxxxx' intellectualRights,--------<para>
    ---geographicCoveragedb_default
    min_x, --<westBoundingCoordinate> ----MIN (longitude) the longitude of the western-most point of the bounding box
    max_x, --<eastBoundingCoordinate> ----MAX(longitude) the longitude of the eastern-most point of the bounding box
    min_y, --<southBoundingCoordinate> ---MIN(latitude) the latitude of the southern-most point of the bounding box
    max_y, --<northBoundingCoordinate> --- MAX(latitude) the latitude of the northern-most point of the bounding box
    ---temporalCoverage
    begindate, enddate,
    ---<generalTaxonomicCoverage>
    count_animals,
    'European terrestrial mammals' generalTaxonomicCoverage,
    '{KINGDOM}' kingdom,
    '{PHYLUM}' phylum,
    '{ORDER}' order_,
    '{FAMILY}' family_,
    '{SPECIE}' species,
    '{NAME}' commonName,
    'GPS collar deployment' "method",
    'Datacurator checks also with automatic controls' qualityControl
FROM 
    main.study_areas s,
    (SELECT 
        research_groups_id,
        research_group_name,
        organization_name,
        country,
        webpage,
        split_part(full_name1, ' ', 1) AS givenName1,
        substring(full_name1 FROM position(' ' IN full_name1) + 1) AS surName1,
        electronicmailaddress1,
        split_part(full_name2, ' ', 1) AS givenName2,
        substring(full_name2 FROM position(' ' IN full_name2) + 1) AS surName2,
        electronicmailaddress2,
        split_part(full_name3, ' ', 1) AS givenName3,
        substring(full_name3 FROM position(' ' IN full_name3) + 1) AS surName3,
        electronicmailaddress3,
        split_part(full_name4, ' ', 1) AS givenName4,
        substring(full_name4 FROM position(' ' IN full_name4) + 1) AS surName4,
        electronicmailaddress4
    FROM (
            SELECT 
                research_groups_id,
                research_group_name,
                organization_name,
                country,
                webpage,
                contact_people,
                split_part(contact_people, ';', 1) AS full_name1,
                split_part(contact_people, ';', 2) AS electronicmailaddress1,
                split_part(contact_people, ';', 3) AS full_name2,
                split_part(contact_people, ';', 4) AS electronicmailaddress2,
                split_part(contact_people, ';', 5) AS full_name3,
                split_part(contact_people, ';', 6) AS electronicmailaddress3,
                split_part(contact_people, ';', 7) AS full_name4,
                split_part(contact_people, ';', 8) AS electronicmailaddress4
            FROM main.research_groups
        ) subquery
    )
    contact,
    ---<geographicDescription>
    (
        SELECT
            study_areas_id,
            min(x) min_x,
            max(x) max_x,
            min(y) min_y,
            max(y) max_y
        FROM (
            WITH mbr AS (
                SELECT 
                    study_areas_id,
                    ST_Envelope(geom) AS rect_geom
                FROM main.study_areas 
                GROUP BY study_areas_id
            ),
            vertices AS (
                SELECT 
                    study_areas_id,
                    ST_ExteriorRing(rect_geom) AS ring FROM mbr
            ),
            points AS (
                SELECT 
                    study_areas_id,
                    ST_DumpPoints(ring) AS dp 
                FROM vertices
            )
            SELECT 
                study_areas_id,
                (dp).path[1] AS vertex_order,
                ST_X((dp).geom) AS x,
                ST_Y((dp).geom) AS y
            FROM points 
            ORDER BY study_areas_id, vertex_order
        ) foo
        GROUP BY study_areas_id
    ) sp_cov,
    --------<temporalCoverage>
    (
        SELECT
            study_areas_id,
            min(start_time) begindate,
            max(end_time) enddate,
            count(distinct a.animals_id) as count_animals
        FROM main.gps_sensors_animals d,  main.animals a 
        WHERE d.animals_id=a.animals_id and study_areas_id={AREA_ID}
        GROUP BY study_areas_id
    ) temp_cov
    --------<contact>
    --------</contact>
WHERE
    contact.research_groups_id=s.research_groups_id
    AND sp_cov.study_areas_id=s.study_areas_id
    AND temp_cov.study_areas_id=s.study_areas_id
ORDER BY contact.research_groups_id, s.study_areas_id
"""

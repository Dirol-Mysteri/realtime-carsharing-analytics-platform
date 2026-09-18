{{ config(
    materialized = 'table',
    ENGINE = 'MergeTree()',
    order_by = '(trip_started_at, car_id)'
)} } WITH telemetry_events AS (
    SELECT
        *
    FROM
        {{ ref('stg_car_telemetry') }}
),
-- Группируем данные по каждой поездке чтобы собрать агрегаты
trip_aggregates AS (
    SELECT
        trip_id,
        car_id,
        masked_user_id,
        -- Время начала и конца поездки
        min(telemetry) AS trip_started_at,
        max(telemetry) AS trip_ended_at,
        -- Метрики поездки
        max(speed) AS max_speed,
        avg(speed) AS avg_speed,
        -- Уровень топлива на старте и финише
        argMin(fuel_level_percent, telemetry) AS fuel_start,
        argMax(fuel_level_percent, telemetry) AS fuel_end
    FROM
        telemetry_events
    WHERE
        trip_id IS NOT NULL
    GROUP BY
        trip_id,
        car_id,
        masked_user_id
)
SELECT
    trip_id,
    car_id,
    masked_user_id,
    trip_started_at,
    trip_ended_at,
    dateDiff('minute', trip_started_at, trip_ended_at) AS trip_duration_minutes,
    max_speed,
    round(avg_speed, 2) AS avg_speed,
    fuel_start,
    fuel_end,
    IF(fuel_start > fuel_end, fuel_start - fuel_end, 0) AS fuel_consumed_percent
FROM
    trip_aggregates
WHERE
    trip_ended_at > trip_started_at
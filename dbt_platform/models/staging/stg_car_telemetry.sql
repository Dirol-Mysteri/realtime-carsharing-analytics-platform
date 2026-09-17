{{ config(materialized = 'view') }} 

WITH source_data AS (
  SELECT
    *
  FROM
    {{ source('carsharing_raw', 'car_telemetry') }}
),
renamed_and_cleaned AS (
  SELECT
    car_id,
    {{ mask_pii('user_id') }} AS masked_user_id,
    trip_id,
    timestamp AS telemetry,
    toDate(timestamp) AS telemetry_date,
    latitude,
    longitude,
    speed,
    fuel_level_percent,
    lower(status) AS telemetry_status
  FROM
    source_data
  WHERE
    latitude != 0
    AND longitude != 0
)
SELECT
  *
FROM
  renamed_and_cleaned
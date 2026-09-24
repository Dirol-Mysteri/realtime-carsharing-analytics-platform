{#
    Кастомный тест уникальности для ClickHouse.
    Использует ключевое слово FINAL, чтобы схлопнуть дубли ReplacingMergeTree
    и проверить реальную уникальность первичного ключа.
#}

select
    trip_id,
    count() as row_count
from {{ ref('fct_trips') }} FINAL
group by trip_id
having count() > 1

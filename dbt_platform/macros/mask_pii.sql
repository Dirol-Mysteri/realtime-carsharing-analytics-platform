{% macro mask_pii(column_name) %} 

{#
Макрос для маскирования персональных данных (PII) в ClickHouse.Использует SHA256 с солью для защиты данных от деанонимизации.
#}

CASE
    WHEN {{ column_name }} IS NULL THEN NULL
    ELSE lower(
        hex(
            SHA256(
                concat(
                    toString({{ column_name }}),
                    'super_secret_salt_2026'
                )
            )
        )
    )
END 
{% endmacro %}
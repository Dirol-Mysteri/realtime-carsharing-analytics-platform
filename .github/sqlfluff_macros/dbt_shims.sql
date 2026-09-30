-- Заглушки для стандартных функций dbt, чтобы SQLFluff не искал базу данных
{% macro ref(model_name) %} {{ model_name }} {% endmacro %}
{% macro source(source_name, table_name) %} {{ table_name }} {% endmacro %}
{% macro config(materialized, engine, order_by, unique_key, incremental_strategy) %} {% endmacro %}
{% macro is_incremental() %} False {% endmacro %}

-- Заглушка для нашего кастомного макроса маскирования
{% macro mask_pii(column_name) %} {{ column_name }} {% endmacro %}

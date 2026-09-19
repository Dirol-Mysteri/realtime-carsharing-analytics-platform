{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is not none -%}
        {# Если схема указана в dbt_project.yml, используем только её имя без префиксов #}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {# Если не указана, льем в дефолтную #}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}

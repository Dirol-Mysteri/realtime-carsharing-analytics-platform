# config.py
import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Собираем все настройки в понятные переменные
CH_USER = os.environ.get("CLICKHOUSE_USER", "admin")
CH_PASS = os.environ.get("CLICKHOUSE_PASSWORD", "admin_password")
CH_DB = os.environ.get("CLICKHOUSE_DB", "db_name")

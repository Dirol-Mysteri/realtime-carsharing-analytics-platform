from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.telegram.operators.telegram import TelegramOperator

# СЕНЬОРСКАЯ ФИШКА: Функция-колбэк, которая вызывается АВТОМАТИЧЕСКИ при падении любого шага
def on_failure_alert(context):
    """
    Автоматический алерт в Telegram при сбое пайплайна качества данных.
    """
    task_instance = context.get('task_instance')
    task_id = task_instance.task_id
    dag_id = task_instance.dag_id
    execution_date = context.get('execution_date')
    
    alert_message = (
        f"🚨 *AIRFLOW PROD ALERT* 🚨\n\n"
        f"❌ *Пайплайн данных каршеринга упал!*\n"
        f"🔹 *DAG:* `{dag_id}`\n"
        f"🔹 *Упавшая задача:* `{task_id}`\n"
        f"🔹 *Время сбоя:* `{execution_date}`\n\n"
        f"⚠️ *Действие:* Срочно проверьте DQ-тесты на слое Core/Marts и логи кликхауса."
    )
    
    # Инициализируем и запускаем отправку сообщения через Telegram API Airflow
    send_alert = TelegramOperator(
        task_id='send_runtime_error_telegram_alert',
        telegram_conn_id='telegram_default', # ID подключения, настраиваемый в UI Airflow
        chat_id='-100123456789',             # ID канала/чата (подставим из продовых переменных)
        text=alert_message,
        parse_mode='Markdown'
    )
    return send_alert.execute(context=context)

# Дефолтные настройки для всех задач внутри графа
default_args = {
    'owner': 'analytics_eng_senior',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,                            # Если dbt упал из-за мимолетного сбоя сети, Airflow попробует еще раз
    'retry_delay': timedelta(minutes=2),
    'on_failure_callback': on_failure_alert  # Вешаем наш алерт на глобальный сбой
}

# Объявляем сам DAG (Пайплайн)
with DAG(
    dag_id='realtime_carsharing_data_platform',
    default_args=default_args,
    description='Пайплайн инкрементальной сборки DWH каршеринга и контроля Data Quality',
    schedule_interval='*/5 * * * *', # Запуск каждые 5 минут (Near Real-Time батчинг)
    start_date=datetime(2026, 1, 1),
    catchup=False,                    # Не пытаться прогонять историю с января 2026 года при старте
    tags=['carsharing', 'dbt', 'clickhouse', 'core']
) as dag:

    # Задача 1: Запуск инкрементальных моделей dbt (Staging -> Marts)
    run_dbt_models = BashOperator(
        task_id='dbt_run_incremental',
        bash_command='cd /opt/airflow/dbt_platform && dbt run --profiles-dir .',
        env={'DBT_PROFILES_DIR': '/opt/airflow/dbt_platform'}
    )

    # Задача 2: Запуск проверок контроля качества данных (Schema + Custom Tests)
    run_data_quality_tests = BashOperator(
        task_id='dbt_test_data_quality',
        bash_command='cd /opt/airflow/dbt_platform && dbt test --profiles-dir .',
        env={'DBT_PROFILES_DIR': '/opt/airflow/dbt_platform'}
    )

    # Выстраиваем строгую последовательность: Сначала собираем витрины -> потом тестируем качество данных
    run_dbt_models >> run_data_quality_tests

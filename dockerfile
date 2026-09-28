# Используем легковесный и стабильный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Переменная окружения, чтобы Python не буферизировал логи (они будут сразу видны в docker logs)
ENV PYTHONUNBUFFERED=1

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем библиотеки без сохранения кэша, чтобы уменьшить размер образа
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код генератора и его конфигурацию
COPY generator.py .
COPY config.py .

# Команда для запуска нашего генератора при старте контейнера
CMD ["python", "generator.py"]

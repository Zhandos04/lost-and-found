FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода проекта
COPY . .

# Копирование и предоставление прав для entrypoint скрипта
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Устанавливаем entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Запуск приложения
CMD ["gunicorn", "lost_and_found.wsgi:application", "--bind", "0.0.0.0:8000"]
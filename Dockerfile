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

# Установка зависимостей Python, кроме TensorFlow
RUN pip install --no-cache-dir $(grep -v "tensorflow" requirements.txt)

# Установка TensorFlow отдельно с увеличенным тайм-аутом
RUN pip install --no-cache-dir --timeout=600 tensorflow==2.15.0

# Копирование исходного кода проекта
COPY . .

# Копирование и предоставление прав для entrypoint скрипта
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Устанавливаем entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Запуск приложения
CMD ["gunicorn", "lost_and_found.wsgi:application", "--bind", "0.0.0.0:8000"]
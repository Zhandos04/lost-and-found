#!/bin/bash

# Ждем, пока база данных станет доступной
echo "Ожидание запуска базы данных..."
sleep 10

# Проверяем, установлен ли TensorFlow
if ! python -c "import tensorflow" &>/dev/null; then
    echo "TensorFlow не установлен. Установка..."
    pip install tensorflow numpy
fi

# Применяем миграции
echo "Создание миграций..."
python manage.py makemigrations core users

echo "Применение миграций..."
python manage.py migrate

# Создаем суперпользователя, если он еще не существует
echo "Проверка существования суперпользователя..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

# Создаем базовые категории, если их нет
echo "Создание базовых категорий..."
python manage.py shell -c "
from core.models import Category;
categories = ['Электроника', 'Документы', 'Ключи', 'Одежда', 'Сумки и рюкзаки', 'Кошельки', 'Украшения', 'Транспорт', 'Прочее'];
for cat in categories:
    Category.objects.get_or_create(name=cat);
print(f'Создано {len(categories)} категорий');
"

# Создаем папку для статических файлов
mkdir -p staticfiles

# Собираем статические файлы
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

# Предзагрузка модели TensorFlow, чтобы не загружать при первом запросе
echo "Предзагрузка модели TensorFlow..."
python -c "
try:
    from core.services.ai_service import load_model
    load_model()
    print('Модель TensorFlow успешно загружена')
except Exception as e:
    print(f'Ошибка загрузки модели TensorFlow: {str(e)}')
"

# Запускаем основной процесс (переданный как параметры CMD)
echo "Запуск сервера..."
exec "$@"
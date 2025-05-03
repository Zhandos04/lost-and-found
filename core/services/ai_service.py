import os
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import img_to_array

# Загружаем предобученную модель MobileNetV2
model = None

def load_model():
    """
    Загружает предобученную модель MobileNetV2 при первом вызове
    """
    global model
    if model is None:
        model = MobileNetV2(weights='imagenet')
    return model

def analyze_image(image_path):
    """
    Анализирует изображение с помощью TensorFlow и предобученной модели MobileNetV2
    
    Args:
        image_path: Путь к файлу изображения
        
    Returns:
        str: Описание изображения на основе AI
    """
    try:
        # Загружаем модель
        model = load_model()
        
        # Открываем и предобрабатываем изображение
        img = Image.open(image_path)
        # Преобразуем в RGB в случае, если изображение имеет другой формат
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Изменяем размер под требуемый для модели (224x224)
        img = img.resize((224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Получаем предсказания модели
        predictions = model.predict(img_array)
        
        # Декодируем предсказания (получаем топ-5 классов)
        decoded_predictions = decode_predictions(predictions, top=5)[0]
        
        # Получаем цветовую палитру
        colors = analyze_colors(img)
        
        # Формируем описание
        description = generate_description(decoded_predictions, colors, img)
        
        return description
    
    except Exception as e:
        print(f"Ошибка в AI анализе изображения: {str(e)}")
        return "Не удалось проанализировать изображение. Пожалуйста, добавьте описание вручную."

def analyze_colors(img):
    """
    Анализирует основные цвета изображения
    
    Args:
        img: Объект изображения PIL
        
    Returns:
        list: Описание основных цветов
    """
    # Изменяем размер для быстрого анализа цветов
    img_small = img.resize((50, 50))
    # Конвертируем в массив numpy
    img_array = np.array(img_small)
    
    # Получаем среднее значение RGB по всему изображению
    mean_color = np.mean(img_array, axis=(0, 1))
    
    # Определяем базовые цвета на основе RGB значений
    color_names = []
    r, g, b = mean_color.astype(int)
    
    # Простая логика определения цвета
    # Можно улучшить с использованием более сложных алгоритмов
    if max(r, g, b) < 50:
        color_names.append("черный")
    elif min(r, g, b) > 200:
        color_names.append("белый")
    else:
        if r > g + 50 and r > b + 50:
            color_names.append("красный")
        elif g > r + 50 and g > b + 50:
            color_names.append("зеленый")
        elif b > r + 50 and b > g + 50:
            color_names.append("синий")
        elif r > 200 and g > 150 and b < 100:
            color_names.append("желтый")
        elif r > 150 and g < 100 and b < 100:
            color_names.append("красный")
        elif r < 100 and g > 100 and b < 100:
            color_names.append("зеленый")
        elif r < 100 and g < 100 and b > 100:
            color_names.append("синий")
        elif r > 150 and g > 100 and b > 100:
            color_names.append("серый")
    
    # Если не удалось определить, используем общее описание
    if not color_names:
        color_names.append("разноцветный")
    
    return color_names

def generate_description(predictions, colors, img):
    """
    Генерирует описание на основе предсказаний и цветов
    
    Args:
        predictions: Результаты распознавания объектов
        colors: Список основных цветов
        img: Объект изображения PIL
        
    Returns:
        str: Подробное описание
    """
    width, height = img.size
    format_name = img.format if hasattr(img, 'format') and img.format else "неизвестный формат"
    
    # Переводим английские предсказания на русский (примерный перевод)
    translation_dict = {
        'wallet': 'кошелек',
        'purse': 'сумка',
        'backpack': 'рюкзак',
        'laptop': 'ноутбук',
        'cellular telephone': 'мобильный телефон',
        'cell phone': 'мобильный телефон',
        'mobile phone': 'мобильный телефон',
        'key': 'ключ',
        'keys': 'ключи',
        'eyeglasses': 'очки',
        'sunglasses': 'солнечные очки',
        'umbrella': 'зонт',
        'book': 'книга',
        'notebook': 'блокнот',
        'pencil case': 'пенал',
        'watch': 'часы',
        'wristwatch': 'наручные часы',
        'handbag': 'сумка',
        'bag': 'сумка',
        'earphone': 'наушники',
        'headphone': 'наушники',
        'headset': 'наушники',
        'document': 'документ',
        'wallet': 'кошелек',
        'purse': 'кошелек',
        'necklace': 'ожерелье',
        'ring': 'кольцо',
        'bracelet': 'браслет',
        'credit card': 'кредитная карта',
        'id card': 'удостоверение личности',
        'usb drive': 'флеш-накопитель',
        'flash drive': 'флеш-накопитель',
        'memory card': 'карта памяти',
        'sd card': 'SD-карта',
        'jacket': 'куртка',
        'coat': 'пальто',
        'hat': 'шляпа',
        'cap': 'кепка',
        'glove': 'перчатка',
        'gloves': 'перчатки',
        'scarf': 'шарф',
    }
    
    # Формируем список распознанных объектов на русском языке
    objects = []
    for _, label, confidence in predictions:
        if confidence > 0.1:  # Фильтруем только вероятные объекты
            # Получаем русский перевод или используем оригинал
            russian_label = translation_dict.get(label.lower(), label)
            objects.append(russian_label)
    
    # Формируем основное описание
    description = f"""
Предмет на изображении имеет следующие характеристики:
- Размер изображения: {width}x{height} пикселей
- Формат файла: {format_name}
- Основные цвета: {', '.join(colors)}
"""
    
    # Добавляем информацию о распознанных объектах
    if objects:
        description += f"- Распознанные объекты: {', '.join(objects)}\n"
    
    # Добавляем дополнительное описание
    description += """
Дополнительная информация: На основе анализа изображения с помощью TensorFlow и 
модели MobileNetV2 система определила возможные объекты и цвета. Если автоматическое 
описание неточно, пожалуйста, скорректируйте его вручную.
"""
    
    return description.strip()
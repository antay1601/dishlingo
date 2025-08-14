
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in ocr.py. Please set the environment variable.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Увеличиваем максимальное количество токенов для ответа
generation_config = genai.types.GenerationConfig(
    max_output_tokens=8192,
)

async def process_menu_image(image_path: str) -> str:
    """
    Извлекает весь видимый текст из изображения, анализирует его и возвращает в виде JSON.
    """
    try:
        print(f"Extracting and processing data from: {image_path}")
        
        image_part = {
            "mime_type": "image/jpeg",
            "data": open(image_path, "rb").read()
        }
        
        prompt = """
        Проанализируй изображение меню. Извлеки все блюда и верни их в виде JSON-массива.

        Инструкции:
        1. Переведи названия на русский язык.
        2. Укажи категорию (закуска, основное блюдо, десерт, напиток, и т.д.).
        3. Извлеки цену как есть. Если цена не видна или неразборчива, используй строку 'нечитаемое'.
        4. Создай краткое, аппетитное описание (2-3 предложения) на основе названия блюда. Это поле обязательно для всех, кроме напитков.
        5. Перечисли видимые ингредиенты. Если они не указаны, сделай разумные выводы из названия блюда. Если и это невозможно, используй ["неизвестно"].
        6. Не добавляй никакого другого текста до или после.

        Формат объекта в массиве:
        [{
            "originalName": "точное название из меню",
            "translatedName": "перевод на русский",
            "image": "placeholder",
            "category": "категория",
            "price": "цена или 'нечитаемое'",
            "shortDescription": "сгенерированное описание",
            "ingredients": ["ингредиенты" или "неизвестно"],
            "containsGluten": "yes|no|unknown",
            "containsMilk": "yes|no|unknown"
        }]
        """
        
        response = await model.generate_content_async(
            [prompt, image_part],
            generation_config=generation_config
        )
        
        response_text = response.text
        print(f"Response received from model. Length: {len(response_text)} chars.")
        return response_text.strip()

    except Exception as e:
        print(f"Error processing image with Gemini: {str(e)}")
        return ""

import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set the environment variable.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

generation_config = genai.types.GenerationConfig(
    max_output_tokens=8192,
)

async def process_menu_section(text_section: str, user_lang: str = "русский") -> list | None:
    """
    Обрабатывает одну секцию меню и возвращает список словарей с блюдами.
    """
    try:
        print(f"Processing section with updated prompt: '{text_section[:40].strip()}...'")

        prompt = f"""
        Проанализируй этот фрагмент текста из меню. Извлеки все блюда и верни их в виде JSON-массива.

        Текст фрагмента:
        ---
        {text_section}
        ---

        Инструкции:
        1. Переведи названия на {user_lang}.
        2. Укажи категорию (закуска, основное блюдо, десерт, напиток, и т.д.).
        3. Извлеки цену как есть. Если цена не видна или неразборчива, используй строку 'нечитаемое'.
        4. Создай краткое, аппетитное описание (2-3 предложения) на основе названия блюда. Это поле обязательно для всех, кроме напитков.
        5. Перечисли видимые ингредиенты. Если они не указаны, сделай разумные выводы из названия блюда. Если и это невозможно, используй ["неизвестно"].
        6. Верни ТОЛЬКО JSON-массив, обернутый в ```json ... ```.

        Формат объекта в массиве:
        {{
            "originalName": "точное название из меню",
            "translatedName": "перевод на {user_lang}",
            "image": "placeholder",
            "category": "категория",
            "price": "цена или 'нечитаемое'",
            "shortDescription": "сгенерированное описание",
            "ingredients": ["ингредиенты" или "неизвестно"],
            "containsGluten": "yes|no|unknown",
            "containsMilk": "yes|no|unknown"
        }}
        """
        
        response = await model.generate_content_async(prompt, generation_config=generation_config)
        
        response_text = response.text.strip()
        
        try:
            json_str = response_text
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            
            json_str = json_str.strip()
            if not json_str.startswith('[') or not json_str.endswith(']'):
                 raise json.JSONDecodeError("Not a JSON array.", json_str, 0)

            parsed_json = json.loads(json_str)
            print(f"Section processed successfully, {len(parsed_json)} items found.")
            return parsed_json

        except (json.JSONDecodeError, IndexError) as e:
            print(f"Failed to decode JSON from section. Error: {e}")
            print("Full response for section was:")
            print(response_text)
            return None

    except Exception as e:
        print(f"Critical error processing section: {e}")
        return None
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Убедитесь, что GEMINI_API_KEY установлен
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set the environment variable.")

genai.configure(api_key=api_key)

# Используем модель, которая точно доступна и хорошо работает с текстом
MODEL = "gemini-1.5-pro"

def generate_image_prompt(description: str) -> str | None:
    """
    Генерирует детализированный промпт для модели генерации изображений.
    """
    print(f"Создание промпта для: '{description}'...")
    
    try:
        model = genai.GenerativeModel(MODEL)
        
        system_instruction = (
            "Ты — эксперт по созданию промптов для моделей генерации изображений (таких как Midjourney или Stable Diffusion). "
            "Твоя задача — на основе краткого описания блюда создать детализированный, креативный и эффективный промпт на английском языке. "
            "Промпт должен включать ключевые слова, описывающие внешний вид, стиль, освещение и композицию, чтобы получить фотореалистичное и очень аппетитное изображение ресторанного качества. "
            "Не добавляй ничего, кроме самого промпта."
        )
        
        prompt_request = f"Краткое описание блюда: '{description}'"

        response = model.generate_content(
            f"{system_instruction}\n\n{prompt_request}"
        )
        
        if response.text:
            # Убираем лишние кавычки и форматирование
            clean_prompt = response.text.strip().replace('"', '')
            print(f"Сгенерирован промпт: {clean_prompt}")
            return clean_prompt
        else:
            print("Не удалось сгенерировать промпт. Ответ модели пуст.")
            return None

    except Exception as e:
        print(f"Произошла ошибка при генерации промпта: {e}")
        return None

if __name__ == '__main__':
    test_description = "Паста Карбонара с хрустящим беконом и сливочным соусом"
    generate_image_prompt(test_description)

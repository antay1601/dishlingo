
import asyncio
import httpx
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# --- Конфигурация ---
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

if not PEXELS_API_KEY:
    raise ValueError("PEXELS_API_KEY не найден в .env файле. Пожалуйста, получите бесплатный ключ на https://www.pexels.com/api/ и добавьте его.")

HEADERS = {
    "Authorization": PEXELS_API_KEY
}
CONCURRENCY_LIMIT = 5
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

client = httpx.AsyncClient(timeout=15.0, headers=HEADERS)

async def get_pexels_image_url(dish: dict) -> str | None:
    """
    Находит URL изображения на Pexels, используя улучшенную логику запроса.
    """
    async with semaphore:
        try:
            # Приоритет отдаем оригинальному названию, оно часто более "интернациональное"
            search_term = dish.get("originalName") or dish.get("translatedName", "food")
            category = dish.get("category", "").lower()

            # Добавляем ключевые слова в зависимости от категории
            if "напиток" in category:
                keywords = "beverage, drink, glass, cocktail"
            else:
                keywords = "food, plate, gourmet, restaurant, delicious"

            query = f"{search_term} {keywords}"
            # Ищем горизонтальные изображения для лучшего вида в меню
            url = f"https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page=1&orientation=landscape&size=medium"
            
            response = await client.get(url)
            
            if response.status_code != 200:
                print(f"Ошибка при запросе к Pexels для '{search_term}'. Статус: {response.status_code}, Ответ: {response.text}")
                return None

            data = response.json()
            photos = data.get("photos", [])
            
            if photos:
                # Берем URL для среднего изображения
                image_url = photos[0].get("src", {}).get("medium")
                print(f"Найдено изображение для '{search_term}'")
                return image_url
            else:
                print(f"Не найдено изображение для '{search_term}' на Pexels.")
                return None
                
        except Exception as e:
            print(f"Непредвиденная ошибка при поиске изображения на Pexels для '{search_term}': {e}")
            return None

async def fetch_images_for_menu(menu_data: list):
    """
    Асинхронно получает URL-ы изображений для каждого блюда в меню с Pexels.
    """
    print("Начинаю улучшенный подбор изображений с Pexels...")
    
    tasks = [get_pexels_image_url(dish) for dish in menu_data]
    image_urls = await asyncio.gather(*tasks)
    
    for i, dish in enumerate(menu_data):
        dish["image"] = image_urls[i]
            
    print("Подбор изображений завершен.")

async def close_http_client():
    """Закрывает HTTP-клиент."""
    await client.aclose()

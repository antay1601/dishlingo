

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import os
import re
import json
import datetime
from bot_instance import bot
from ocr import process_menu_image
from html_generator import generate_html_menu
from image_fetcher import fetch_images_for_menu

router = Router()

def register_handlers(dp):
    dp.include_router(router)


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer('Привет! Отправь мне фотографию меню, и я сделаю из него удобный HTML-файл с картинками.')

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Этот бот анализирует фото меню, подбирает для блюд изображения и возвращает красивый HTML-файл.')

@router.message(lambda message: message.photo)
async def handle_photo(message: Message):
    processing_msg = await message.answer('Принял! Начинаю обработку...')
    
    photo = message.photo[-1]
    
    temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = f"{message.from_user.id}_{timestamp}"
    download_path = os.path.join(temp_dir, f'menu_{unique_id}.jpg')
    html_output_path = os.path.join(temp_dir, f'menu_{unique_id}.html')
    
    try:
        await bot.download(photo, destination=download_path)
        
        # Шаг 1: Распознавание текста
        await processing_msg.edit_text('Шаг 1/3: Распознаю текст с изображения...')
        extracted_text = await process_menu_image(download_path)
        
        if not extracted_text:
            await message.answer('Не удалось распознать текст. Пожалуйста, отправьте более четкое фото.')
            return
        
        # Шаг 2: Извлечение JSON
        await processing_msg.edit_text('Шаг 2/3: Анализирую меню...')
        try:
            match = re.search(r'```json\s*([\s\S]+?)\s*```', extracted_text, re.DOTALL)
            json_str = match.group(1) if match else extracted_text
            
            data = json.loads(json_str)
            menu_data = data.get("menu", [])
            is_partial = data.get("isPartial", False)

        except (json.JSONDecodeError, IndexError):
            await message.answer('Не удалось обработать данные из меню. Пожалуйста, попробуйте еще раз.')
            print("Failed to parse JSON from:", extracted_text)
            return

        if not menu_data:
            await message.answer('Не удалось извлечь ни одного блюда из меню.')
            return

        # Шаг 3: Подбор изображений
        await processing_msg.edit_text('Шаг 3/3: Подбираю изображения для блюд...')
        await fetch_images_for_menu(menu_data)
        
        # Генерация HTML
        generate_html_menu(menu_data, html_output_path)

        caption = "Ваше меню готово!"
        if is_partial:
            caption += "\n\n⚠️ *Обратите внимание: меню было распознано не полностью. Была обработана только часть.*"

        await processing_msg.delete()
        await message.answer_document(
            FSInputFile(html_output_path), 
            caption=caption,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await processing_msg.delete()
        await message.answer(f'Произошла критическая ошибка: {str(e)}')
    finally:
        # Удаляем временные файлы (теперь только исходник и HTML)
        for file_path in [download_path, html_output_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Ошибка при удалении файла {file_path}: {e}")



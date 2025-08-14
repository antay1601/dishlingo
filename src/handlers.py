

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import os
import re
import json
import datetime
from main import bot
from ocr import process_menu_image
from html_generator import generate_html_menu

router = Router()

def register_handlers(dp):
    dp.include_router(router)


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer('Привет! Отправь мне фотографию меню, и я сделаю из него удобный HTML-файл.')

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Этот бот анализирует фото меню и возвращает красивый и удобный HTML-файл.')

@router.message(lambda message: message.photo)
async def handle_photo(message: Message):
    processing_msg = await message.answer('Принял! Начинаю обработку...')
    
    photo = message.photo[-1]
    
    temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Создаем временные пути для файлов
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = f"{photo.file_unique_id}_{timestamp}"
    download_path = os.path.join(temp_dir, f'{unique_id}.jpg')
    html_output_path = os.path.join(temp_dir, f'menu_{timestamp}.html')
    
    try:
        await bot.download(photo, destination=download_path)
        
        # Шаг 1: Распознавание текста
        await processing_msg.edit_text('Шаг 1/2: Распознаю текст с изображения...')
        extracted_text = await process_menu_image(download_path)
        
        if not extracted_text:
            await message.answer('Не удалось распознать текст. Пожалуйста, отправьте более четкое фото.')
            return
        
        # Шаг 2: Извлечение JSON и генерация HTML
        await processing_msg.edit_text('Шаг 2/2: Создаю HTML-версию меню...')
        try:
            match = re.search(r'```json\s*([\s\S]+?)\s*```', extracted_text, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                json_str = extracted_text
            
            menu_data = json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            await message.answer('Не удалось обработать данные из меню. Пожалуйста, попробуйте еще раз.')
            print("Failed to parse JSON from:", extracted_text)
            return

        generate_html_menu(menu_data, html_output_path)

        # Отправка результата
        await processing_msg.delete()
        await message.answer_document(
            FSInputFile(html_output_path), 
            caption="Ваше меню готово!"
        )
        
    except Exception as e:
        await processing_msg.delete()
        await message.answer(f'Произошла критическая ошибка: {str(e)}')
    finally:
        # Удаляем временные файлы
        if os.path.exists(download_path):
            os.remove(download_path)
        if os.path.exists(html_output_path):
            os.remove(html_output_path)

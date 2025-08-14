import asyncio
from bot_instance import dp, bot
from handlers import register_handlers
from image_fetcher import close_http_client

async def on_shutdown():
    """Вызывается при остановке бота для очистки ресурсов."""
    print("Завершение работы, закрытие HTTP-клиента...")
    await close_http_client()

async def main():
    # Регистрируем обработчик завершения работы
    dp.shutdown.register(on_shutdown)
    
    # Регистрируем хендлеры сообщений
    register_handlers(dp)
    
    # Запускаем бота
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
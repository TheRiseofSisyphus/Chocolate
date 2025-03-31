import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import BOT_TOKEN
from services.bot_handler import BotHandler, Form

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    try:
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()
        handler = BotHandler(bot)

        # Регистрируем обработчики
        dp.message.register(handler.handle_start, Command("start"))
        dp.message.register(handler.handle_file_request, F.text == "📂 Отправить файл Excel")
        dp.message.register(handler.handle_finish_work, F.text == "⏹ Завершить работу")
        dp.message.register(handler.handle_agent_percent, Form.waiting_for_percent)
        dp.message.register(handler.handle_file, Form.waiting_for_file, F.document)

        logger.info("Bot started")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import BOT_TOKEN
from services.bot_handler import BotHandler, Form
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    try:
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "secret")
        db_name = os.getenv("DB_NAME", "mydatabase")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()
        handler = BotHandler(bot)

        # Ваша база моделей
        Base = declarative_base()


        # Создание объекта движка
        full_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

        # Создание всех таблиц
        Base.metadata.create_all(engine)

        # Создание фабрики сессий
        Session = sessionmaker(bind=engine)

        # Создание экземпляра сессии
        session = Session()

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
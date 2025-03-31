import logging
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import BOT_TOKEN, OPERATOR_PERCENT
from services.file_manager import FileManager
from services.excel_processor import ExcelProcessor
from services.report_generator import ReportGenerator
from services.session_manager import SessionManager
from pathlib import Path

logger = logging.getLogger(__name__)


class Form(StatesGroup):
    waiting_for_percent = State()
    waiting_for_file = State()
    ready_to_finish = State()


class BotHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.session_manager = None
        self.current_agent_percent = None

        # Основная клавиатура
        self.main_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📂 Отправить файл Excel")],
                [KeyboardButton(text="⏹ Завершить работу")]
            ],
            resize_keyboard=True
        )

    async def handle_start(self, message: types.Message, state: FSMContext):
        """Инициализация новой сессии"""
        await state.clear()
        self.session_manager = SessionManager(message.from_user.id)
        self.current_agent_percent = None
        await message.answer(
            "✅ Сессия оператора начата. Выберите действие:",
            reply_markup=self.main_keyboard
        )

    async def handle_file_request(self, message: types.Message, state: FSMContext):
        """Запрос процента агента"""
        await message.answer(
            "Введите процент для агента (например, 3 для 3%):",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Form.waiting_for_percent)

    async def handle_agent_percent(self, message: types.Message, state: FSMContext):
        """Обработка введенного процента"""
        try:
            percent = float(message.text)
            if not 0 < percent <= 100:
                raise ValueError

            self.current_agent_percent = percent
            await message.answer(
                f"Установлен процент агента: {percent}%\n"
                "Теперь отправьте Excel-файл для обработки."
            )
            await state.set_state(Form.waiting_for_file)

        except (ValueError, TypeError):
            await message.answer("Пожалуйста, введите корректный процент (от 0.1 до 100)")

    async def handle_file(self, message: types.Message, state: FSMContext):
        """Обработка загруженного файла"""
        if not message.document:
            await message.answer("Пожалуйста, отправьте файл.", reply_markup=self.main_keyboard)
            return

        try:
            # Проверка типа файла
            if not message.document.file_name.lower().endswith('.xlsx'):
                raise ValueError("Поддерживаются только файлы .xlsx")

            # Загрузка файла
            file = await self.bot.get_file(message.document.file_id)
            file_data = await self.bot.download_file(file.file_path)

            # Сохранение файла
            file_path = FileManager.save_user_file(message.from_user.id, file_data)

            # Обработка файла
            sheets_data = ExcelProcessor.process_workbook(file_path, self.current_agent_percent)

            # Генерация и отправка отчёта
            combined_report = ReportGenerator.generate_combined_report(sheets_data)
            await self._send_report(message, combined_report)

            # Сохранение данных и отчётов
            for sheet_name, sheet_data in sheets_data.items():
                self.session_manager.add_agent(
                    agent_name=sheet_data.full_name,
                    turnover=sheet_data.turnover,
                    agent_percent=self.current_agent_percent
                )
                FileManager.save_report(
                    message.from_user.id,
                    sheet_name,
                    ReportGenerator._generate_single_sheet(sheet_data)
                )

            await message.answer("✅ Файл успешно обработан", reply_markup=self.main_keyboard)
            await state.set_state(Form.ready_to_finish)

        except ValueError as e:
            await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=self.main_keyboard)
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {e}", exc_info=True)
            await message.answer(
                "❌ Произошла ошибка при обработке файла. Проверьте формат данных.",
                reply_markup=self.main_keyboard
            )

    async def handle_finish_work(self, message: types.Message, state: FSMContext):
        """Формирование финального отчета оператора"""
        try:
            if not self.session_manager:
                await message.answer("ℹ️ Нет активной сессии. Отправьте /start")
                return

            summary = self.session_manager.get_summary()

            report = (
                "📊 *Финальный отчет оператора*\n"
                f"• Начало сессии: {summary['start_time']}\n"
                f"• Обработано агентов: {summary['agents_count']}\n"
                f"• Общий оборот: {ReportGenerator.format_number(summary['total_turnover'])} ₽\n"
                f"• Ваша выплата ({OPERATOR_PERCENT}%): {ReportGenerator.format_number(summary['operator_payment'])} ₽"
            )

            await message.answer(report, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Ошибка формирования отчета: {e}", exc_info=True)
            await message.answer("❌ Ошибка при формировании отчета")
        finally:
            await state.clear()
            self.session_manager = None
            await message.answer(
                "Сессия завершена. Для новой сессии отправьте /start",
                reply_markup=ReplyKeyboardRemove()
            )

    async def _send_report(self, message: types.Message, text: str):
        """Отправка больших отчетов по частям"""
        try:
            if len(text) <= 4096:
                await message.answer(text)
            else:
                # Разбиваем отчет на части по 4000 символов
                parts = [text[i:i + 4000] for i in range(0, len(text), 4000)]
                for part in parts:
                    await message.answer(part)
        except Exception as e:
            logger.error(f"Ошибка отправки отчета: {e}")
            await message.answer("⚠️ Ошибка отправки отчета")
import logging
from aiogram import Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import MAX_FILE_SIZE, OPERATOR_PERCENT
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
        self.current_agent_percent = None
        self.total_operator_payment = 0
        self.session_manager = None

        # Основная клавиатура
        self.main_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📂 Отправить файл Excel")],
                [KeyboardButton(text="⏹ Завершить работу")]
            ],
            resize_keyboard=True
        )

    async def handle_start(self, message: types.Message, state: FSMContext):
        """Обработчик команды /start"""
        # Инициализируем session_manager при старте
        if not hasattr(self, 'session_manager'):
            self.session_manager = SessionManager(message.from_user.id)

        await state.clear()
        self._reset_work_data()
        await message.answer("Выберите действие:", reply_markup=self.main_keyboard)

    async def handle_file_request(self, message: types.Message, state: FSMContext):
        """Обработчик запроса на отправку файла"""
        await message.answer(
            "Введите процент для агента (например, 3 для 3%):",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Form.waiting_for_percent)

    async def handle_agent_percent(self, message: types.Message, state: FSMContext):
        """Обработчик ввода процента агента"""
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
            await message.answer("Пожалуйста, введите корректный процент (например, 3.5 для 3.5%)")

    async def handle_file(self, message: types.Message, state: FSMContext):
        """Обработчик получения Excel-файла"""
        if not message.document:
            await message.answer("Пожалуйста, отправьте файл.", reply_markup=self.main_keyboard)
            return

        if message.document.mime_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            await message.answer("Пожалуйста, отправьте файл в формате .xlsx", reply_markup=self.main_keyboard)
            return

        if message.document.file_size > MAX_FILE_SIZE:
            await message.answer(
                f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // 1024 // 1024}MB",
                reply_markup=self.main_keyboard
            )
            return

        try:
            # Загрузка и сохранение файла
            file = await self.bot.get_file(message.document.file_id)
            file_data = await self.bot.download_file(file.file_path)
            file_path = FileManager.save_user_file(message.from_user.id, file_data)

            # Парсинг и обработка данных
            sheets_data = ExcelProcessor.process_workbook(file_path, self.current_agent_percent)

            full_report = ""
            file_operator_total = 0
            file_turnover_total = 0

            # Генерация отчетов
            for sheet_name, sheet_data in sheets_data.items():
                sheet_data.sheet_name = sheet_name
                report_text = ReportGenerator.generate(sheet_data)
                FileManager.save_report(message.from_user.id, sheet_name, report_text)
                full_report += f"\n\n{report_text}"

                # Суммирование выплат
                file_operator_total += sheet_data.operator_payment
                file_turnover_total += sheet_data.turnover

            # Обновление общей суммы
            self.total_operator_payment += file_operator_total

            # Формирование итогов по файлу
            file_summary = (
                    "\n\n=== ИТОГИ ПО ФАЙЛУ ==="
                    f"\nОбщий оборот: {ReportGenerator.format_number(file_turnover_total)}"
                    f"\nОплата оператора (0.5%): {ReportGenerator.format_number(file_operator_total)}"
                    "\n" + "=" * 40
            )

            # Отправка отчета
            await self._send_report(
                message,
                full_report.strip() + file_summary,
                reply_markup=self.main_keyboard
            )

            # Сбрасываем процент для следующего файла
            self.current_agent_percent = None
            await state.set_state(Form.ready_to_finish)

        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            await message.answer(
                "Произошла ошибка при обработке файла. Пожалуйста, проверьте файл и попробуйте еще раз.",
                reply_markup=self.main_keyboard
            )

    async def handle_finish_work(self, message: types.Message, state: FSMContext):
        """Гарантированно стабильное формирование отчёта"""
        try:
            if not hasattr(self, 'session_manager'):
                await message.answer("ℹ️ Сессия не была начата. Отправьте /start")
                return

            summary = self.session_manager.get_summary()

            # Формируем отчёт частями для надёжности
            report_parts = [
                "📊 *Итоги сессии оператора*",
                f"• Начало: {summary['start_time']}",
                f"• Обработано агентов: {summary['agents_count']}",
                f"• Общий оборот: {ReportGenerator.format_number(summary['total_turnover'])} ₽",
                f"• Ваша выплата ({OPERATOR_PERCENT}%): {ReportGenerator.format_number(summary['operator_payment'])} ₽",
                "\n🔝 Топ агентов:"
            ]



        except Exception as e:
            logger.error(f"Ошибка формирования отчёта: {str(e)}", exc_info=True)
            await message.answer(
                "⚠️ Произошла ошибка при формировании отчёта. Данные сохранены и будут доступны при следующем завершении.")
        finally:
            if hasattr(self, 'session_manager'):
                del self.session_manager
            await state.clear()

    def _reset_work_data(self):
        """Сброс данных рабочей сессии"""
        self.current_agent_percent = None
        self.total_operator_payment = 0



    async def _send_report(self, message: types.Message, text: str, reply_markup=None):
        """Внутренний метод для отправки отчетов"""
        try:
            if len(text) <= 4096:
                await message.answer(text, reply_markup=reply_markup)
            else:
                parts = [text[i:i + 4096] for i in range(0, len(text), 4096)]
                for part in parts[:-1]:
                    await message.answer(part)
                await message.answer(parts[-1], reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error sending report: {e}")
            await message.answer(
                "Произошла ошибка при отправке отчета.",
                reply_markup=reply_markup
            )
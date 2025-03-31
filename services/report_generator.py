from .data_models import ExcelSheetData
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ReportGenerator:
    @staticmethod
    def format_number(value: float) -> str:
        """Форматирует число с разделителями тысяч"""
        try:
            if value is None:
                return "0"
            return "{:,.2f}".format(float(value)).replace(",", " ").replace(".00", "")
        except (ValueError, TypeError) as e:
            logger.warning(f"Ошибка форматирования числа {value}: {e}")
            return str(value or "0")

    @staticmethod
    def _generate_single_sheet(data: ExcelSheetData) -> str:
        """Генерирует отчёт для одного листа"""
        try:
            report = [
                f"\n\n=== Лист: {data.sheet_name or 'Без названия'} ===",
                f"ФИО: {data.full_name or 'Не указано'}",
                f"Банк: {data.bank or 'Не указан'}",
                f"Оборот: {ReportGenerator.format_number(data.turnover)} ₽",
                f"Выплата агенту: {ReportGenerator.format_number(data.agent_payment)} ₽"
            ]

            if data.inflows:
                report.append("\nВходящие операции:")
                report.extend(
                    f"{i}. {ReportGenerator.format_number(t.amount)} ₽ (ID: {t.transaction_id or 'нет'})"
                    for i, t in enumerate(data.inflows, 1)
                )

            return "\n".join(report)
        except Exception as e:
            logger.error(f"Ошибка генерации отчёта для листа {data.sheet_name}: {e}")
            return f"\n\n⚠️ Ошибка формирования отчёта для листа {data.sheet_name}"

    @staticmethod
    def generate_combined_report(sheets_data: Dict[str, ExcelSheetData]) -> str:
        """Генерирует объединённый отчёт по всем листам"""
        try:
            if not sheets_data:
                return "ℹ️ Файл не содержит данных для отчёта"

            report = ["📊 ОБЪЕДИНЁННЫЙ ОТЧЁТ"]
            total_turnover = 0
            total_agent_payment = 0

            for sheet_name, data in sheets_data.items():
                sheet_report = ReportGenerator._generate_single_sheet(data)
                report.append(sheet_report)
                total_turnover += data.turnover or 0
                total_agent_payment += data.agent_payment or 0

            report.append(
                "\n\n📌 ИТОГО ПО ФАЙЛУ:\n"
                f"• Общий оборот: {ReportGenerator.format_number(total_turnover)} ₽\n"
                f"• Суммарная выплата агентам: {ReportGenerator.format_number(total_agent_payment)} ₽\n"
                f"• Выплата оператору (0.5%): {ReportGenerator.format_number(total_turnover * 0.005)} ₽"
            )

            return "\n".join(report)
        except Exception as e:
            logger.critical(f"Критическая ошибка генерации отчёта: {e}", exc_info=True)
            return "⚠️ Произошла критическая ошибка при формировании отчёта"
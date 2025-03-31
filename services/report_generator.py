from .data_models import ExcelSheetData


class ReportGenerator:
    @staticmethod
    def format_number(value: float) -> str:
        try:
            return "{:,.2f}".format(float(value)).replace(",", " ").replace(".00", "")
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def generate(data: ExcelSheetData) -> str:
        report = [
            f"=== Отчет по листу: {data.sheet_name} ===",
            f"ФИО: {data.full_name}",
            f"Банк: {data.bank}",
            f"Покупки, прогревы: {data.warm_up_rub}/{data.warm_up_purchases}",
            f"Стартовый баланс: {ReportGenerator.format_number(data.start_balance)}",
            f"Старт: {data.start_time}",
            f"Стоп: {data.end_time}",
            f"\nПроцент агента: {data.agent_percent}%",
            "\n📌 Входные транзакции:"
        ]

        report.extend(
            f"{i}. {ReportGenerator.format_number(t.amount)} {t.transaction_id}"
            for i, t in enumerate(data.inflows, 1)
        )

        report.append("\n\n📌 Выходные транзакции:")
        report.extend(
            f"{i}. {ReportGenerator.format_number(t.amount)} {t.transaction_id}"
            f"{f' ({t.commission} комса)' if t.commission else ''}"
            for i, t in enumerate(data.outflows, 1)
        )

        if data.baibit:
            report.append("\n\n📌 Выход Байбит:")
            report.extend(
                f"{i}. {ReportGenerator.format_number(t.amount)} ({t.rate})"
                for i, t in enumerate(data.baibit, 1)
            )

        report.extend([
            f"\n\nИтоги:",
            f"Оборот: {ReportGenerator.format_number(data.turnover)}",
            f"Оплата агента ({data.agent_percent}%): {ReportGenerator.format_number(data.agent_payment)}",
            f"Оплата оператора (0.5%): {ReportGenerator.format_number(data.operator_payment)}",
            f"Общие комиссии: {ReportGenerator.format_number(sum(t.commission for t in data.outflows))}",
            f"Стоп баланс: {ReportGenerator.format_number(data.stop_balance)}",
            f"Тг: {data.operator or 'Нет данных'}",
            "=" * 40
        ])

        return "\n".join(report)

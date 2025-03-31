from openpyxl import load_workbook
from pathlib import Path
from .data_models import ExcelSheetData, Transaction, BaibitTransaction


class ExcelProcessor:
    @staticmethod
    def process_workbook(file_path: Path, agent_percent: float) -> dict[str, ExcelSheetData]:
        wb = load_workbook(file_path)
        sheets_data = {}

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            data = ExcelSheetData(
                full_name=sheet['K2'].value,
                bank=sheet['L2'].value,
                warm_up_purchases=sheet['M2'].value,
                warm_up_rub=sheet['N2'].value,
                start_balance=sheet['Q2'].value,
                stop_balance=sheet['R2'].value,
                start_time=sheet['S2'].value,
                end_time=sheet['T2'].value,
                operator=sheet['P2'].value,
                inflows=[],
                outflows=[],
                baibit=[],
                agent_percent=agent_percent
            )

            # Обработка строк
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row[0] and row[1]:  # Входные транзакции
                    data.inflows.append(Transaction(amount=row[0], transaction_id=str(row[1])))
                    data.turnover += row[0]

                if row[2] and row[3]:  # Выходные транзакции
                    commission = row[4] if len(row) > 4 and row[4] else 0
                    data.outflows.append(Transaction(
                        amount=row[2],
                        transaction_id=str(row[3]),
                        commission=commission
                    ))

                if row[5] and row[6]:  # Байбит транзакции
                    data.baibit.append(BaibitTransaction(
                        amount=row[5],
                        rate=row[6]
                    ))

            data.calculate_payments()
            sheets_data[sheet_name] = data

        return sheets_data
import openpyxl
from db import get_logs_by_date

def create_excel(date):
    records = get_logs_by_date(date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = date

    ws.append(["User ID", "Name", "Timestamp", "Status"])

    for pin, name, timestamp, status in records:
        ws.append([pin, name, timestamp, status])

    filename = f"{date}.xlsx"
    wb.save(filename)
    return filename

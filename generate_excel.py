import openpyxl
from db import get_attendance_by_date
from names import EMPLOYEE_NAMES


def create_excel(date):
    records = get_attendance_by_date(date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = date

    ws.append(["User ID", "Name", "Timestamp", "Status"])

    for user_id, timestamp, status in records:
        name = EMPLOYEE_NAMES.get(str(user_id), "Unknown")
        ws.append([user_id, name, timestamp, status])

    filename = f"{date}.xlsx"
    wb.save(filename)
    return filename

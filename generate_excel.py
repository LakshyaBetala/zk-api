from openpyxl import Workbook

def create_excel(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["User ID", "Name", "Time", "Status"])

    for row in rows:
        ws.append(list(row))

    file_path = "attendance_export.xlsx"
    wb.save(file_path)
    return file_path

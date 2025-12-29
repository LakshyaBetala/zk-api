from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import sqlite3
import os
from generate_excel import generate_excel
from names import EMPLOYEE_NAMES   # Mapping PIN → Name


app = FastAPI()

# Attach HTML templates and static directory
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


DB_PATH = "attendance.db"


# ---------------------- Database Init ----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            timestamp TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------------- Root Check ----------------------
@app.get("/")
def root():
    return {"status": "server_online", "time": str(datetime.utcnow())}


# ---------------------- ESP32 Attendance ----------------------
@app.post("/attendance")
async def attendance_log(req: Request):
    data = await req.json()

    user = data.get("user")
    event = data.get("event")
    ts = data.get("timestamp")

    name = EMPLOYEE_NAMES.get(user, "Unknown")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (user_id, name, timestamp, status) VALUES (?, ?, ?, ?)",
        (user, name, ts, event),
    )
    conn.commit()
    conn.close()

    return {"status": "saved", "user": user, "time": ts}


# ---------------------- ZKTeco ADMS Raw Logs ----------------------
@app.post("/iclock/cdata")
async def zkteco_logs(request: Request):
    raw_bytes = await request.body()
    raw = raw_bytes.decode(errors="ignore")

    print("\n------ ZKTeco Log ------")
    print(raw)
    print("-------------------------")

    # Parse format: PIN=10&Time=2025-01-01 10:10:10&Status=0
    entries = raw.split("\n")
    for entry in entries:
        if "PIN=" not in entry:
            continue

        parts = entry.split("&")
        user = parts[0].replace("PIN=", "").strip()
        ts = parts[1].replace("Time=", "").strip()
        status = parts[2].replace("Status=", "").strip()

        name = EMPLOYEE_NAMES.get(user, "Unknown")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (user_id, name, timestamp, status) VALUES (?, ?, ?, ?)",
            (user, name, ts, status),
        )
        conn.commit()
        conn.close()

    return "OK"


@app.get("/iclock/getrequest")
def zkteco_getreq():
    return "OK"


# ---------------------- Dashboard UI ----------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ---------------------- Generate XLSX ----------------------
@app.post("/download")
async def download_excel(date: str = Form(...)):
    excel_path = generate_excel(date)
    return FileResponse(excel_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=f"{date}.xlsx")

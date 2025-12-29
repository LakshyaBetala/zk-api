from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from db import insert_attendance, get_attendance_by_date
from names import EMPLOYEE_NAMES
from generate_excel import create_excel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------------------- Root Health Check ----------------------
@app.get("/")
def root():
    return {"status": "server_online", "time": str(datetime.utcnow())}


# ---------------------- Dashboard ----------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    today = datetime.now().strftime("%Y-%m-%d")
    return templates.TemplateResponse("dashboard.html", {"request": request, "selected_date": today})


@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard_post(request: Request, date: str = Form(...)):
    logs = get_attendance_by_date(date)

    # Replace user IDs with names if present
    final_logs = []
    for row in logs:
        user_id, timestamp, status = row
        name = EMPLOYEE_NAMES.get(str(user_id), "Unknown")
        final_logs.append((user_id, name, timestamp, status))

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "selected_date": date,
            "logs": final_logs
        }
    )


# ---------------------- Download XLSX ----------------------
@app.get("/download")
async def download_excel(date: str):
    filepath = create_excel(date)
    return FileResponse(filepath, filename=f"{date}.xlsx")


# ---------------------- ESP32 JSON Attendance ----------------------
@app.post("/attendance")
async def esp32_attendance(req: Request):
    data = await req.json()

    user = data.get("user")
    timestamp = data.get("timestamp", str(datetime.utcnow()))
    event = data.get("event", "UNKNOWN")

    insert_attendance(user, timestamp, event)

    print("\n------ ESP32 Attendance ------")
    print(data)
    print("--------------------------------")

    return {"status": "ok", "stored": True}


# ---------------------- ZKTeco ADMS Raw Logs ----------------------
@app.post("/iclock/cdata")
async def zkteco_logs(request: Request):
    body = await request.body()
    raw = body.decode(errors="ignore")

    # Parse raw ADMS logs (ZKTeco format)
    # Example: PIN=12&Time=2025-01-01 09:00:00&Status=0
    if "PIN=" in raw:
        fields = dict(x.split("=") for x in raw.split("&") if "=" in x)

        user = fields.get("PIN")
        timestamp = fields.get("Time")
        status = fields.get("Status", "0")

        insert_attendance(user, timestamp, status)

        print("\n------ ZKTeco Log Stored ------")
        print(raw)
        print("--------------------------------")

    return "OK"


# ---------------------- Required by ZKTeco ----------------------
@app.get("/iclock/getrequest")
def zkteco_getreq():
    return "OK"


# ---------------------- Heartbeat ----------------------
@app.get("/heartbeat")
def heartbeat():
    return {"status": "alive", "time": str(datetime.utcnow())}

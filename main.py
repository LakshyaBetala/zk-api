from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from db import insert_log, get_logs_by_date
from names import EMPLOYEE_NAMES
from generate_excel import create_excel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def root():
    return {"status": "server_online", "time": str(datetime.utcnow())}


# ---------------- Dashboard ----------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    today = datetime.now().strftime("%Y-%m-%d")
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "selected_date": today
    })


@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard_post(request: Request, date: str = Form(...)):
    logs = get_logs_by_date(date)

    final_logs = []
    for pin, name, timestamp, status in logs:
        final_logs.append((pin, name, timestamp, status))

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "selected_date": date,
        "logs": final_logs
    })


# --------------- XLSX Download ----------------
@app.get("/download")
async def download_excel(date: str):
    filepath = create_excel(date)
    return FileResponse(filepath, filename=f"{date}.xlsx")


# --------------- ESP32 Logs ----------------
@app.post("/attendance")
async def esp32_attendance(req: Request):
    data = await req.json()

    user = data.get("user")
    timestamp = data.get("timestamp", str(datetime.utcnow()))
    event = data.get("event", "UNKNOWN")
    name = EMPLOYEE_NAMES.get(str(user), "Unknown")

    insert_log(user, name, timestamp, event)

    print("\n------ ESP32 Attendance ------")
    print(data)
    print("--------------------------------")

    return {"status": "ok", "stored": True}


# --------------- ZKTeco Logs ----------------
@app.post("/iclock/cdata")
async def zkteco_logs(request: Request):
    raw = (await request.body()).decode(errors="ignore")

    if "PIN=" in raw:
        try:
            fields = dict(x.split("=") for x in raw.split("&") if "=" in x)

            user = fields.get("PIN")
            timestamp = fields.get("Time")
            status = fields.get("Status", "0")
            name = EMPLOYEE_NAMES.get(str(user), "Unknown")

            insert_log(user, name, timestamp, status)

            print("\n------ STORED ZKTeco Log ------")
            print(raw)
            print("--------------------------------")

        except:
            print("❌ Bad ZKTeco Format:", raw)

    return "OK"


@app.get("/iclock/getrequest")
def zkteco_getreq():
    return "OK"


@app.get("/heartbeat")
def heartbeat():
    return {"status": "alive", "time": str(datetime.utcnow())}

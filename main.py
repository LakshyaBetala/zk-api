from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()


# ------------------- Root Health Check -------------------
@app.get("/")
def root():
    return {"status": "server_online", "time": str(datetime.utcnow())}


# ------------------- ESP32 Attendance (JSON) -------------------
@app.post("/attendance")
async def attendance_log(req: Request):
    """
    ESP32 sends:
    {
        "device": "gate1",
        "user": "1005",
        "event": "check_in",
        "timestamp": "2025-01-01 10:30:10"
    }
    """

    data = await req.json()

    print("\n------ ESP32 Attendance ------")
    print(f"Device: {data.get('device')}")
    print(f"User: {data.get('user')}")
    print(f"Event: {data.get('event')}")
    print(f"Timestamp: {data.get('timestamp')}")
    print("--------------------------------")

    return {
        "status": "ok",
        "received_at": str(datetime.utcnow())
    }


# ------------------- ESP32 Heartbeat -------------------
@app.get("/heartbeat")
def heartbeat():
    return {"status": "alive", "time": str(datetime.utcnow())}


# ------------------- ZKTeco ADMS Raw Logs -------------------
@app.post("/iclock/cdata")
async def zkteco_logs(request: Request):
    """
    Handles raw logs coming from ZKTeco devices.
    """
    body = await request.body()
    raw = body.decode(errors="ignore")

    print("\n------ ZKTeco Log ------")
    print(raw)
    print("-------------------------")

    return "OK"


# ------------------- Required by ZKTeco -------------------
@app.get("/iclock/getrequest")
def zkteco_getreq():
    return "OK"


# ------------------- Manual JSON test -------------------
@app.post("/test")
async def test_data(req: Request):
    data = await req.json()
    return {"received": data, "timestamp": str(datetime.utcnow())}

from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()


# --- Root Check ---
@app.get("/")
def root():
    return {"status": "ZKTeco ADMS Server Online"}


# --- ZKTeco ADMS Endpoint ---
@app.post("/iclock/cdata")
async def receive_logs(request: Request):
    """
    ZKTeco devices send attendance logs to:
    /iclock/cdata

    Logs come as raw text like:
    POST: PIN=1&Time=2024-01-01 09:00:00&Status=0
    """

    body = await request.body()
    raw = body.decode(errors="ignore")

    print("\n--- ZKTeco Log Received ---")
    print(raw)
    print("-----------------------------")

    # Return OK so device stops retrying
    return "OK"


# --- ZKTeco Device 'getrequest' response ---
@app.get("/iclock/getrequest")
def get_request():
    """
    Device calls this before sending logs.
    Always respond with OK.
    """
    return "OK"


# --- Optional: test endpoint for manual verification ---
@app.post("/test")
async def test_data(req: Request):
    body = await req.json()
    return {"received": body, "timestamp": str(datetime.utcnow())}

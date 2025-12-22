# ZKTeco ADMS FastAPI Server

This backend receives attendance logs from ZKTeco biometric devices 
(face, fingerprint, RFID, etc.) using the **ADMS protocol**.

The server provides the exact endpoints expected by ZKTeco devices:

- `GET /iclock/getrequest` → Device keep-alive  
- `POST /iclock/cdata` → Device sends attendance logs  
- `GET /` → Server status check  

---

## 🚀 How It Works

1. The ZKTeco device pushes attendance logs to your Railway server.  
2. This FastAPI backend receives raw log strings.  
3. You can parse, store, or forward the logs to a database.

---

## 🛠 Endpoints

### `GET /`
Server online check.

### `GET /iclock/getrequest`
Device pings this before sending logs.
Must return **OK**.

### `POST /iclock/cdata`
Device pushes attendance logs here.
Example raw log:

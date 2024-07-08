from fastapi import FastAPI, HTTPException, Header, Request, File
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import json
import subprocess
import os
from pathlib import Path

app = FastAPI()

# Load configuration from config.json
CONFIG_PATH = "config.json"
try:
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    raise Exception("Configuration file not found")

API_KEY = config["api_key"]
CORS_ORIGINS = config["cors_origins"]
FTP_CREDENTIALS = config["ftp_credentials"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/upload/status")
async def upload_file():
    return '<html><body><h1>FTP gateway is up and running!</h1></body></html>'

@app.post("/upload")
async def upload_file(
    request: Request,
    filename: str = Header(...),
    platename: str = Header(...),
    api_key: str = Header(...)
):
    body = await request.body()
    # Validate API key
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Get FTP credentials for the platename
    ftp_details = FTP_CREDENTIALS.get(platename)

    if not ftp_details:
        raise HTTPException(status_code=404, detail="FTP details not found for platename")

    # Save the file to a temporary location
    temp_file_path = Path(f"./tmp/{filename}")
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
            await out_file.write(body)

    # Upload file to FTP server
    import ftplib
    try:
        with ftplib.FTP(ftp_details["host"]) as ftp:
            ftp.login(ftp_details["user"], ftp_details["pass"])
            with open(temp_file_path, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)
    except ftplib.all_errors as e:
        raise HTTPException(status_code=500, detail=f"FTP upload error: {e}")

    # Clean up the temporary file
    # os.remove(temp_file_path)

    return {"detail": "File uploaded successfully"}

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=5000)
    http_command = [
        "uvicorn",
        "ftp-gw-api:app",  # Adjust to your app's module and instance
        "--host", "0.0.0.0",
        "--port", "5000"
    ]

    https_command = [
        "uvicorn",
        "ftp-gw-api:app",  # Adjust to your app's module and instance
        "--host", "0.0.0.0",
        "--port", "5001",
        "--ssl-keyfile", "key.pem",
        "--ssl-certfile", "cert.pem"
    ]

    # Start both servers
    http_server = subprocess.Popen(http_command)
    https_server = subprocess.Popen(https_command)

    # Wait for both servers to complete
    http_server.wait()
    https_server.wait()

import subprocess
import json

# Load configuration from config.json
CONFIG_PATH = "config.json"
try:
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    raise Exception("Configuration file not found")

HTTP_PORT = config["http_port"]
HTTPS_PORT = config["https_port"]

http_command = [
    "uvicorn",
    "main:app",  # Replace 'main' with the module name of your app
    "--host", "0.0.0.0",
    "--port", str(HTTP_PORT)
]

https_command = [
    "uvicorn",
    "main:app",  # Replace 'main' with the module name of your app
    "--host", "0.0.0.0",
    "--port", str(HTTPS_PORT),
    "--ssl-keyfile", "certs/key.pem",
    "--ssl-certfile", "certs/cert.pem"
]

# Start both servers
http_server = subprocess.Popen(http_command)
https_server = subprocess.Popen(https_command)

# Wait for both servers to complete
http_server.wait()
https_server.wait()

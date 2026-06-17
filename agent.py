import subprocess
import json
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

proc = subprocess.Popen(
    [
        "docker",
        "run",
        "-i",
        "--rm",
        "-e",
        f"GITHUB_PERSONAL_ACCESS_TOKEN={TOKEN}",
        "ghcr.io/github/github-mcp-server:latest",
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

initialize = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {
            "name": "python-test",
            "version": "1.0"
        }
    }
}

proc.stdin.write(json.dumps(initialize) + "\n")
proc.stdin.flush()

print(proc.stdout.readline())
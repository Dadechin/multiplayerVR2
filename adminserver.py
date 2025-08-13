import requests
import subprocess
import time

API_BASE = "http://127.0.0.1:8000"
ADMIN_TOKEN = "secret"

processes = {}
# http://127.0.0.1:8000/servere_meetings/
while True:
    # meetings = requests.get(f"{API_BASE}/get_user_meetings/", headers={"Authorization": f"Token {ADMIN_TOKEN}"}).json()
    resp = requests.get(
        f"{API_BASE}/servere_meetings/",
        headers={"Authorization": f"Token {ADMIN_TOKEN}"}
    )

    print(resp.status_code)
    print(resp.text)  # show raw response

    meetings = resp.json()  # only if it's valid JSON

    for m in meetings:
        if m["is_running"] and m["port"] not in processes:
            processes[m["port"]] = subprocess.Popen(["python3", "mini_server.py", str(m["port"])])
            print(f"Started server on port {m['port']}")

        if not m["is_running"] and m["port"] in processes:
            processes[m["port"]].terminate()
            del processes[m["port"]]
            print(f"Stopped server on port {m['port']}")
    time.sleep(2)

import requests
import subprocess
import time
import json

API_BASE = "http://127.0.0.1:8000"
ADMIN_TOKEN = "secret"

processes = {}

while True:
    try:
        resp = requests.get(
            f"{API_BASE}/servere_meetings/",
            headers={"Authorization": f"Token {ADMIN_TOKEN}"},
            timeout=5
        )
        
        if resp.status_code != 200:
            print(f"Error: Received status code {resp.status_code}")
            time.sleep(2)
            continue
            
        try:
            meetings = resp.json()
        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            time.sleep(2)
            continue

        # Check for new meetings to start
        for m in meetings:
            if not isinstance(m, dict):
                continue
                
            port = m.get("port")
            is_running = m.get("is_running", False)
            
            if not port:
                continue
                
            if is_running and port not in processes:
                try:
                    processes[port] = subprocess.Popen(["python3", "mini_server.py", str(port)])
                    print(f"Started server on port {port}")
                except Exception as e:
                    print(f"Failed to start server on port {port}: {str(e)}")
            
            if not is_running and port in processes:
                try:
                    processes[port].terminate()
                    processes[port].wait(timeout=5)
                    del processes[port]
                    print(f"Stopped server on port {port}")
                except Exception as e:
                    print(f"Failed to stop server on port {port}: {str(e)}")
                    del processes[port]
        
        # Clean up any dead processes
        for port in list(processes.keys()):
            if processes[port].poll() is not None:  # Process has terminated
                del processes[port]
                print(f"Cleaned up dead process for port {port}")
                
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    
    time.sleep(15)
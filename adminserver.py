import requests
import subprocess
import time
import json
import sys

print("=== Admin Server Starting ===")
print(f"Python version: {sys.version}")
print(f"Executable: {sys.executable}")

API_BASE = "http://127.0.0.1:8000"
ADMIN_TOKEN = "secret"
print(f"Configuration:\n- API_BASE: {API_BASE}\n- ADMIN_TOKEN: {ADMIN_TOKEN}")

processes = {}
print("Entering main loop...")

while True:
    print("\n=== New Iteration ===")
    print(f"Current time: {time.ctime()}")
    print(f"Active processes: {processes}")
    
    try:
        print("Making API request...")
        resp = requests.get(
            f"{API_BASE}/servere_meetings/",
            headers={"Authorization": f"Token {ADMIN_TOKEN}"},
            timeout=5
        )
        print(f"Response received. Status: {resp.status_code}")
        print(f"Headers: {resp.headers}")
        print(f"Content: {resp.text}")
        
        if resp.status_code != 200:
            print(f"Error: Bad status code {resp.status_code}")
            time.sleep(2)
            continue
            
        try:
            meetings = resp.json()
            print(f"JSON parsed successfully: {meetings}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            time.sleep(2)
            continue

        # Process meetings
        for i, m in enumerate(meetings):
            print(f"\nProcessing meeting {i+1}/{len(meetings)}")
            if not isinstance(m, dict):
                print(f"Skipping non-dict meeting: {m}")
                continue
                
            port = m.get("port")
            is_running = m.get("is_running", False)
            print(f"Meeting data - port: {port}, is_running: {is_running}")
            
            if not port:
                print("Skipping meeting with no port")
                continue
                
            if is_running and port not in processes:
                print(f"Need to start server on port {port}")
                try:
                    processes[port] = subprocess.Popen(
                        [sys.executable, "mini_server.py", str(port)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    print(f"Started server on port {port} (PID: {processes[port].pid})")
                except Exception as e:
                    print(f"Failed to start server: {str(e)}")
            
            if not is_running and port in processes:
                print(f"Need to stop server on port {port}")
                try:
                    processes[port].terminate()
                    stdout, stderr = processes[port].communicate(timeout=5)
                    print(f"Process output:\n{stdout.decode()}\n{stderr.decode()}")
                    del processes[port]
                    print(f"Stopped server on port {port}")
                except Exception as e:
                    print(f"Failed to stop server: {str(e)}")
                    del processes[port]
        
        # Clean up dead processes
        print("\nChecking for dead processes...")
        for port in list(processes.keys()):
            if processes[port].poll() is not None:
                print(f"Cleaning up dead process for port {port}")
                del processes[port]
                
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("Sleeping for 2 seconds...")
    time.sleep(20)
import requests
import subprocess
import time
import json
import sys
import os

print("=== Admin Server Starting ===")
print(f"Python version: {sys.version}")
print(f"Executable: {sys.executable}")
print(f"Working directory: {os.getcwd()}")

API_BASE = "http://127.0.0.1:8000"
ADMIN_TOKEN = "secret"
print(f"Configuration:\n- API_BASE: {API_BASE}\n- ADMIN_TOKEN: {ADMIN_TOKEN}")

processes = {}
print("Entering main loop...")

def start_server(port):
    """Start the mini server on specified port"""
    try:
        cmd = ["python3.10", "-u", "mini_server.py", str(port)]
        print(f"Starting server with command: {' '.join(cmd)}")
        
        processes[port] = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
            cwd=os.getcwd()  # Ensure correct working directory
        )
        
        # Print process info for debugging
        print(f"Server started (PID: {processes[port].pid})")
        print(f"Process stdout fd: {processes[port].stdout.fileno()}")
        print(f"Process stderr fd: {processes[port].stderr.fileno()}")
        
        # Start thread to monitor output
        def monitor_output(process, port):
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"[Server {port}] {output.strip()}")
        
        import threading
        t = threading.Thread(
            target=monitor_output,
            args=(processes[port], port),
            daemon=True
        )
        t.start()
        
        return True
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        if port in processes:
            del processes[port]
        return False
def stop_server(port):
    """Stop the mini server on specified port"""
    if port not in processes:
        return True
        
    try:
        print(f"Stopping server on port {port} (PID: {processes[port].pid})")
        processes[port].terminate()
        
        # Wait for process to end and capture output
        try:
            stdout, stderr = processes[port].communicate(timeout=5)
            if stdout: print(f"Server stdout: {stdout}")
            if stderr: print(f"Server stderr: {stderr}")
        except subprocess.TimeoutExpired:
            processes[port].kill()
            print(f"Force killed server on port {port}")
            
        del processes[port]
        print(f"Successfully stopped server on port {port}")
        return True
    except Exception as e:
        print(f"Failed to stop server on port {port}: {str(e)}")
        if port in processes:
            del processes[port]
        return False

while True:
    print("\n=== New Iteration ===")
    print(f"Current time: {time.ctime()}")
    print(f"Active processes: {[f'{p}:{processes[p].pid}' for p in processes]}")
    
    try:
        # Check API for meetings
        print("Making API request...")
        resp = requests.get(
            f"{API_BASE}/servere_meetings/",
            headers={"Authorization": f"Token {ADMIN_TOKEN}"},
            timeout=5
        )
        print(f"Response received. Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"Error: Bad status code {resp.status_code}")
            time.sleep(2)
            continue
            
        try:
            meetings = resp.json()
            print(f"Found {len(meetings)} meetings")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            time.sleep(2)
            continue

        # Process meetings
        for m in meetings:
            if not isinstance(m, dict):
                continue
                
            port = m.get("port")
            is_running = m.get("is_running", False)
            
            if not port:
                continue
                
            if is_running and port not in processes:
                start_server(port)
            elif not is_running and port in processes:
                stop_server(port)
        
        # Clean up dead processes
        dead_ports = [p for p in processes if processes[p].poll() is not None]
        for port in dead_ports:
            print(f"Cleaning up dead process for port {port}")
            del processes[port]
                
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("Sleeping for 20 seconds...")
    time.sleep(20)
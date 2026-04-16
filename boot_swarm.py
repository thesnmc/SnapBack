import os
import time
import subprocess

def launch_node(script_name, window_title, delay=0):
    """
    Spawns a brand new command prompt window, activates the virtual environment,
    and runs the target script.
    """
    print(f"[*] Igniting {window_title} ({script_name})...")
    
    # The exact command to run in the new window
    # /k keeps the window open so you can see the logs
    cmd = f'start "{window_title}" cmd /k ".\\venv\\Scripts\\activate && python {script_name}"'
    
    # Execute the command at the OS level
    os.system(cmd)
    
    if delay > 0:
        time.sleep(delay)

def main():
    print("==================================================")
    print("      SNAPBACK: COGNITIVE SWARM BOOTLOADER        ")
    print("==================================================")
    print("[+] Initiating 4-Node Boot Sequence...\n")

    # 1. Core Router (Needs a 2-second head start to open the ZeroMQ port)
    launch_node("telemetry_stream.py", "Terminal 1: DSP Router", delay=2)

    # 2. Command Center (Needs a second to bind the WebSocket)
    launch_node("dashboard.py", "Terminal 2: Command Center", delay=1)

    # 3. Robotics Sandbox
    launch_node("drone_agent.py", "Terminal 3: Robotics Sandbox", delay=1)

    # 4. AI Agent
    launch_node("ai_agent.py", "Terminal 4: AI Agent")

    print("\n[+] All nodes deployed successfully.")
    print("[+] Welcome back to the Command Center.")
    print("==================================================")

if __name__ == "__main__":
    main()
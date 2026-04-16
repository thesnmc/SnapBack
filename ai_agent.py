import zmq
import time
import sys
import ollama
import pyautogui # NEW: Reaching into the Windows OS

def main():
    print("--- Neural-Linked LLM Agent [OS-Hook Edition] Booting ---")
    
    # --- ZMQ SETUP ---
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:5555")
    socket.setsockopt_string(zmq.SUBSCRIBE, "AUTONOMY") 
    
    print("Connected to SnapBack Router. Awaiting telemetry...")
    current_autonomy = 0.85
    system_frozen = False # NEW: Track the OS hardware state

    # The prompt we give the AI
    prompt = "Explain the concept of Zero-Knowledge Architecture in software design."
    print(f"\n[Task] Prompting Local LLM: '{prompt}'\n")
    print("--- GENERATION START ---\n")

    # Start the LLM generation stream
    stream = ollama.chat(
        model='llama3.2:1b', 
        messages=[{'role': 'user', 'content': prompt}],
        stream=True, 
    )

    try:
        for chunk in stream:
            # 1. Drain the Queue (Get the absolute latest telemetry)
            while True:
                try:
                    message = socket.recv_string(flags=zmq.NOBLOCK)
                    _, value = message.split()
                    current_autonomy = float(value)
                except zmq.Again:
                    break 

            # 2. THE SNAPBACK OVERRIDE (Cognitive + OS)
            if current_autonomy < 0.80: # FIX: Catch the drop even if it's already recovering
                
                # If we haven't frozen the OS yet, do it now
                if not system_frozen:
                    pyautogui.press('playpause') # OS HOOK: Pause global system media
                    system_frozen = True
                    
                    sys.stdout.write("\n\n[!!!] ERN DETECTED: COGNITIVE & OS OVERRIDE. LLM FROZEN. MEDIA PAUSED. [!!!]\n")
                    sys.stdout.flush()

                # Trap the agent in a loop until the autonomy creeps back up to 80%
                while current_autonomy < 0.80:
                    while True: # Keep checking telemetry while frozen
                        try:
                            msg = socket.recv_string(flags=zmq.NOBLOCK)
                            _, val = msg.split()
                            current_autonomy = float(val)
                        except zmq.Again:
                            break
                    time.sleep(0.1)

                # Once we break out of the loop, trust is restored. Unfreeze the OS.
                if system_frozen:
                    pyautogui.press('playpause') # OS HOOK: Resume global system media
                    system_frozen = False
                    sys.stdout.write("\n[System] Trust Restored. Resuming OS and generation...\n\n")
                    sys.stdout.flush()

            # 3. Print the next piece of the word if autonomy is high enough
            sys.stdout.write(chunk['message']['content'])
            sys.stdout.flush()
            
            time.sleep(0.03) 

    except KeyboardInterrupt:
        print("\n\nShutting down AI Agent...")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
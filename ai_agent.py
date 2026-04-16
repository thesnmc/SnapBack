import zmq
import time
import sys
import ollama
import pyautogui # OS-Hook intact
import random    # NEW: For infinite topic generation

def main():
    print("--- Neural-Linked LLM Agent [Deep Throttle + OS-Hook Edition] Booting ---")
    
    # --- ZMQ SETUP ---
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:5555")
    
    # FIX: Subscribe to EVERYTHING (Autonomy & Attention streams)
    socket.setsockopt_string(zmq.SUBSCRIBE, "") 
    
    print("Connected to SnapBack Router. Awaiting telemetry...")
    current_autonomy = 0.85
    current_attention = 0.50
    system_frozen = False # Track the OS hardware state

    # A list of heavy topics for the AI to continuously chew on
    topics = ["Zero-Knowledge Proofs", "Quantum Cryptography", "Neural Telemetry", "Asymmetric Encryption", "Edge Computing"]

    # --- INFINITE THOUGHT LOOP ---
    while True:
        # 1. Drain the Queue to get the absolute latest brain state before we lock in the next prompt
        while True:
            try:
                msg = socket.recv_string(flags=zmq.NOBLOCK)
                parts = msg.split()
                if parts[0] == "AUTONOMY":
                    current_autonomy = float(parts[1])
                elif parts[0] == "ATTENTION":
                    current_attention = float(parts[1])
            except zmq.Again:
                break 

        # 2. THE DEEP THROTTLE MATH
        # Map Attention (0.1 -> 1.0) inverted to AI Temperature (0.9 -> 0.1)
        # High focus = 0.1 Temp (Strict). Low focus = 0.9 Temp (Loose).
        ai_temp = 1.0 - current_attention
        ai_temp = max(0.1, min(ai_temp, 0.9)) # Clamp it safely between 0.1 and 0.9

        topic = random.choice(topics)
        prompt = f"Give me two insightful sentences about {topic}."

        print(f"\n=======================================================")
        print(f"[Brain State] Focus: {current_attention*100:.0f}% -> AI Temperature locked at: {ai_temp:.2f}")
        print(f"[Task] Generating thought on: {topic}")
        print(f"=======================================================\n")

        # Start the LLM generation stream
        stream = ollama.chat(
            model='llama3.2:1b', 
            messages=[{'role': 'user', 'content': prompt}],
            stream=True, 
            options={'temperature': ai_temp} # <-- WIRING YOUR BRAIN TO THE AI
        )

        try:
            for chunk in stream:
                # 3. Drain the Queue mid-generation (Get the absolute latest telemetry)
                while True:
                    try:
                        msg = socket.recv_string(flags=zmq.NOBLOCK)
                        parts = msg.split()
                        if parts[0] == "AUTONOMY":
                            current_autonomy = float(parts[1])
                        elif parts[0] == "ATTENTION":
                            current_attention = float(parts[1])
                    except zmq.Again:
                        break 

                # 4. THE SNAPBACK OVERRIDE (Cognitive + OS)
                if current_autonomy < 0.80: 
                    
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
                                parts = msg.split()
                                if parts[0] == "AUTONOMY":
                                    current_autonomy = float(parts[1])
                                elif parts[0] == "ATTENTION":
                                    current_attention = float(parts[1])
                            except zmq.Again:
                                break
                        time.sleep(0.1)

                    # Once we break out of the loop, trust is restored. Unfreeze the OS.
                    if system_frozen:
                        pyautogui.press('playpause') # OS HOOK: Resume global system media
                        system_frozen = False
                        sys.stdout.write("\n[System] Trust Restored. Resuming OS and generation...\n\n")
                        sys.stdout.flush()

                # 5. Print the next piece of the word if autonomy is high enough
                sys.stdout.write(chunk['message']['content'])
                sys.stdout.flush()
                
                time.sleep(0.03) 
            
            print("\n")
            time.sleep(2) # Brief pause before the AI starts its next thought

        except KeyboardInterrupt:
            print("\n\nShutting down AI Agent...")
            socket.close()
            context.term()
            sys.exit(0)

if __name__ == "__main__":
    main()
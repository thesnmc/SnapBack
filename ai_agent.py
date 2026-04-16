import zmq
import time
import sys
import ollama
import pyautogui # OS-Hook intact
import random    # For infinite topic generation
import sqlite3   # NEW: Target B (Cognitive RAG Memory)

def fetch_neural_memory():
    """Reads the SQLite Black Box and summarizes the user's recent cognitive state for the AI."""
    try:
        conn = sqlite3.connect("axon6_blackbox.db")
        cursor = conn.cursor()
        # Grab the last 1200 rows (approx 2 minutes of telemetry)
        cursor.execute("SELECT session_tag, attention_index, ern_spike FROM cognitive_telemetry ORDER BY timestamp DESC LIMIT 1200")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "SYSTEM WARNING: The Neural Black Box is currently empty. No session data available."
        
        # Calculate the stats
        latest_tag = rows[0][0] if rows[0][0] else "Default"
        avg_attention = sum(r[1] for r in rows) / len(rows) * 100
        total_erns = sum(r[2] for r in rows)
        
        # Package this into a system prompt for Ollama
        memory_context = (
            f"SYSTEM CONTEXT: The user's most recent cognitive session was tagged '{latest_tag}'. "
            f"During this timeframe, their average simulated focus level was {avg_attention:.1f}%. "
            f"They experienced {total_erns} severe cognitive drops (ERN spikes) which required you to freeze. "
            f"Use this exact data to answer their question like a professional AI Science Officer analyzing their brainwaves."
        )
        return memory_context
    except Exception as e:
        return f"SYSTEM ERROR: Unable to access neural memory vault. Error: {e}"

def main():
    print("--- Neural-Linked LLM Agent [Cognitive RAG + OS-Hook Edition] Booting ---")
    
    # --- ZMQ SETUP ---
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:5555")
    socket.setsockopt_string(zmq.SUBSCRIBE, "") 
    
    print("Connected to SnapBack Router. Awaiting telemetry...")
    current_autonomy = 0.85
    current_attention = 0.50
    system_frozen = False 

    topics = ["Zero-Knowledge Proofs", "Quantum Cryptography", "Neural Telemetry", "Asymmetric Encryption", "Edge Computing"]

    # --- INFINITE THOUGHT & RAG LOOP ---
    while True:
        
        # --- TARGET B: THE COGNITIVE INTERCEPT ---
        print("\n" + "="*55)
        user_input = input("[?] Press ENTER for autonomous thought, or type a query: ")
        
        if user_input.strip() == "":
            topic = random.choice(topics)
            prompt = f"Give me two insightful sentences about {topic}."
            task_label = f"Generating autonomous thought on: {topic}"
        else:
            # If the user typed a question, pull their brainwaves and build the RAG prompt
            neural_context = fetch_neural_memory()
            prompt = f"{neural_context}\n\nUser Question: {user_input}"
            task_label = "Executing Neural RAG Analysis"

        # 1. Drain the Queue to get the absolute latest brain state
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
        ai_temp = 1.0 - current_attention
        ai_temp = max(0.1, min(ai_temp, 0.9)) 

        print(f"\n=======================================================")
        print(f"[Brain State] Focus: {current_attention*100:.0f}% -> AI Temperature locked at: {ai_temp:.2f}")
        print(f"[Task] {task_label}")
        print(f"=======================================================\n")

        # Start the LLM generation stream
        stream = ollama.chat(
            model='llama3.2:1b', 
            messages=[{'role': 'user', 'content': prompt}],
            stream=True, 
            options={'temperature': ai_temp} 
        )

        try:
            for chunk in stream:
                # 3. Drain the Queue mid-generation
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
                    if not system_frozen:
                        pyautogui.press('playpause') 
                        system_frozen = True
                        sys.stdout.write("\n\n[!!!] ERN DETECTED: COGNITIVE & OS OVERRIDE. LLM FROZEN. MEDIA PAUSED. [!!!]\n")
                        sys.stdout.flush()

                    while current_autonomy < 0.80:
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
                        time.sleep(0.1)

                    if system_frozen:
                        pyautogui.press('playpause') 
                        system_frozen = False
                        sys.stdout.write("\n[System] Trust Restored. Resuming OS and generation...\n\n")
                        sys.stdout.flush()

                # 5. Print the next piece of the word
                sys.stdout.write(chunk['message']['content'])
                sys.stdout.flush()
                
                time.sleep(0.03) 
            
            print("\n")

        except KeyboardInterrupt:
            print("\n\nShutting down AI Agent...")
            socket.close()
            context.term()
            sys.exit(0)

if __name__ == "__main__":
    main()
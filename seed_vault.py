import sqlite3
import math
import random
from datetime import datetime, timedelta

def seed_database():
    conn = sqlite3.connect("axon6_blackbox.db")
    cursor = conn.cursor()

    # Wipe the existing data so we have a clean canvas for the graph
    cursor.execute("DELETE FROM cognitive_telemetry")

    print("[-] Injecting 10 minutes of synthetic high-density cognitive telemetry...")

    now = datetime.now()
    # Start the simulation exactly 10 minutes ago
    start_time = now - timedelta(minutes=10)

    autonomy_index = 0.85
    
    data_to_insert = []
    
    # 10 minutes * 60 seconds * 10 ticks per second = 6000 data points
    for i in range(6000):
        current_time = start_time + timedelta(milliseconds=i * 100)

        # 1. Simulate Organic Focus (Beta Waves)
        # Combines a slow 50-second drift, a faster 5-second wave, and random neural jitter
        attention_drift = math.sin(i / 500.0) * 0.2
        attention_wave = math.cos(i / 50.0) * 0.15
        attention_jitter = random.uniform(-0.05, 0.05)
        
        attention_index = 0.5 + attention_drift + attention_wave + attention_jitter
        attention_index = max(0.1, min(attention_index, 0.95)) # Clamp it safely

        # 2. Simulate ERN Overrides
        # You are 8x more likely to trigger an ERN kill-switch when your focus drops below 40%
        ern_triggered = 0
        ern_chance = 0.001 if attention_index > 0.4 else 0.008

        if random.random() < ern_chance:
            autonomy_index = 0.0
            ern_triggered = 1
        else:
            if autonomy_index < 0.85:
                autonomy_index += 0.015 # SnapBack recovery curve
                autonomy_index = min(autonomy_index, 0.85)

        data_to_insert.append((
            current_time.isoformat(),
            "10-Min Stress Test",
            autonomy_index,
            attention_index,
            ern_triggered
        ))

    # Blast all 6000 rows into the database instantly
    cursor.executemany(
        "INSERT INTO cognitive_telemetry (timestamp, session_tag, autonomy_index, attention_index, ern_spike) VALUES (?, ?, ?, ?, ?)",
        data_to_insert
    )

    conn.commit()
    conn.close()
    
    print(f"[+] Vault sealed. {len(data_to_insert)} data points successfully injected.")
    print("[*] Run read_vault.py now to render the topography.")

if __name__ == "__main__":
    seed_database()
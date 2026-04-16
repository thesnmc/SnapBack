import sqlite3

def wipe_database():
    try:
        conn = sqlite3.connect("axon6_blackbox.db")
        cursor = conn.cursor()
        
        # Flush the data but keep the table structure intact
        cursor.execute("DELETE FROM cognitive_telemetry")
        conn.commit()
        conn.close()
        
        print("\n[!] Vault scrubbed clean. All test data purged.")
        print("[*] AXON-6 is ready for live neural telemetry.\n")
    except Exception as e:
        print(f"Error wiping vault: {e}")

if __name__ == "__main__":
    wipe_database()
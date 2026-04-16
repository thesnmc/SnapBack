import time
import random
import zmq
import sqlite3 
from datetime import datetime 
import numpy as np
from scipy.signal import butter, lfilter
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

# ==========================================
# --- HARDWARE CONFIGURATION BLOCK ---
# Set to True when you purchase a physical EEG headset (e.g., OpenBCI Cyton)
USE_REAL_HARDWARE = False
EEG_SERIAL_PORT = "COM3" # Change this to your headset's Bluetooth/USB port
# ==========================================

# --- DSP: THE NEURAL FILTER MATH ---
def butter_bandpass(lowcut, highcut, fs, order=4):
    """Creates the mathematical coefficients for a bandpass filter."""
    nyq = 0.5 * fs 
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_filter(data, b, a):
    """Runs the raw data through the filter."""
    return lfilter(b, a, data)

def main():
    print("--- SnapBack DSP Telemetry Router [Analytics & Hardware Edition] ---")
    
    # --- TARGET B: SESSION TAGGING ---
    session_tag = input("\n[?] Enter Session Tag (e.g., Coding, Gaming, Reading) or press Enter for 'Default': ")
    if not session_tag.strip():
        session_tag = "Default"
    print(f"[*] Session locked as: {session_tag.upper()}")

    # --- SQLITE DATA VAULT SETUP ---
    db_conn = sqlite3.connect("axon6_blackbox.db")
    db_cursor = db_conn.cursor()
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS cognitive_telemetry (
            timestamp TEXT,
            session_tag TEXT,
            autonomy_index REAL,
            attention_index REAL,
            ern_spike INTEGER
        )
    ''')
    # Background DB migration: Safely add the 'session_tag' column to your existing database
    try:
        db_cursor.execute("ALTER TABLE cognitive_telemetry ADD COLUMN session_tag TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists, safe to proceed
    db_conn.commit()

    # --- ZMQ SETUP ---
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5555")
    
    # --- BRAINFLOW SETUP (TARGET C: THE HARDWARE BRIDGE) ---
    params = BrainFlowInputParams()
    if USE_REAL_HARDWARE:
        board_id = BoardIds.CYTON_BOARD.value # Or MUSE, GANGLION, etc.
        params.serial_port = EEG_SERIAL_PORT
        print(f"[*] HARDWARE BRIDGE ACTIVE: Connecting to physical EEG on {EEG_SERIAL_PORT}...")
    else:
        board_id = BoardIds.SYNTHETIC_BOARD.value
        print("[*] SIMULATION ACTIVE: Using Synthetic BCI Board...")
        
    board = BoardShim(board_id, params)
    sampling_rate = board.get_sampling_rate(board_id) 

    # Generate the Filters
    b_ern, a_ern = butter_bandpass(lowcut=1.0, highcut=40.0, fs=sampling_rate, order=4)
    b_beta, a_beta = butter_bandpass(lowcut=12.0, highcut=30.0, fs=sampling_rate, order=4)

    print(f"Filter 1 (ERN): 1Hz - 40Hz Bandpass")
    print(f"Filter 2 (Beta): 12Hz - 30Hz Bandpass")
    print("Offline SQLite Database: axon6_blackbox.db [ACTIVE]")
    
    try:
        board.prepare_session()
        board.start_stream()
        print("\nLive Stream: ON. Broadcasting and Logging Telemetry...\n")

        autonomy_index = 0.85 
        focus_amplitude = 15.0 # Starting amplitude for our simulated Beta wave
        
        while True:
            data = board.get_current_board_data(250)
            
            if data.shape[1] >= 250:
                raw_eeg = data[1] 
                
                ern_triggered = 0 # Track if an ERN hit this exact frame
                
                # --- INJECT SYNTHETIC WAVES (Only if we are simulating) ---
                if not USE_REAL_HARDWARE:
                    # Synthetic Beta (Simulating drifting focus)
                    focus_amplitude += random.uniform(-2.0, 2.0)
                    focus_amplitude = np.clip(focus_amplitude, 3.0, 30.0) 
                    
                    t = np.linspace(0, 1, 250)
                    beta_wave = focus_amplitude * np.sin(2 * np.pi * 20 * t)
                    raw_eeg += beta_wave
                    
                    # Synthetic ERN (Sharp negative drop)
                    if random.random() < 0.01: 
                        ern_wave = np.linspace(-150, 0, 20) 
                        raw_eeg[100:120] += ern_wave 
                
                # ==========================================
                # APPLY THE MATH: CHANNEL 1 (AUTONOMY / ERN)
                # ==========================================
                filtered_ern = apply_filter(raw_eeg, b_ern, a_ern)
                min_voltage = np.min(filtered_ern)
                
                if min_voltage < -50.0: 
                    print(f"\n[!] ERN DETECTED ({min_voltage:.2f} uV) -> SNAPBACK! AUTONOMY: 0.0")
                    autonomy_index = 0.0 
                    ern_triggered = 1 # Flag it for the database
                else:
                    if autonomy_index < 0.85:
                        autonomy_index += 0.02 
                        autonomy_index = min(autonomy_index, 0.85)

                # ==========================================
                # APPLY THE MATH: CHANNEL 2 (ATTENTION / BETA)
                # ==========================================
                filtered_beta = apply_filter(raw_eeg, b_beta, a_beta)
                
                beta_power = np.std(filtered_beta)
                attention_index = np.clip(beta_power / 30.0, 0.1, 1.0)

                # --- ZMQ MULTI-BROADCAST ---
                socket.send_string(f"AUTONOMY {autonomy_index:.2f}")
                socket.send_string(f"ATTENTION {attention_index:.2f}")

                # --- SQLITE VAULT LOGGING (WITH SESSION TAG) ---
                current_time = datetime.now().isoformat()
                db_cursor.execute(
                    "INSERT INTO cognitive_telemetry (timestamp, session_tag, autonomy_index, attention_index, ern_spike) VALUES (?, ?, ?, ?, ?)", 
                    (current_time, session_tag, autonomy_index, attention_index, ern_triggered)
                )
                db_conn.commit()

                # UI formatting
                bar_length = 15
                ai_fill = int(autonomy_index * bar_length)
                human_fill = bar_length - ai_fill
                bar = f"[{'#' * ai_fill}{'-' * human_fill}]"

                print(f"ERN: {min_voltage:7.2f}uV | Autonomy: {autonomy_index*100:5.1f}% {bar} | Attention: {attention_index*100:5.1f}% | DB: LOGGED", end='\r')

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nShutting down DSP Engine and sealing Data Vault...")
    finally:
        db_conn.close() # Safely lock the database on exit
        board.stop_stream()
        board.release_session()
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
import time
import random
import zmq
import sqlite3 # NEW: Offline database
from datetime import datetime # NEW: Timestamping
import numpy as np
from scipy.signal import butter, lfilter
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

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
    # --- SQLITE DATA VAULT SETUP ---
    # Creates an offline database file in your current directory
    db_conn = sqlite3.connect("axon6_blackbox.db")
    db_cursor = db_conn.cursor()
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS cognitive_telemetry (
            timestamp TEXT,
            autonomy_index REAL,
            attention_index REAL,
            ern_spike INTEGER
        )
    ''')
    db_conn.commit()

    # --- ZMQ SETUP ---
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5555")
    
    # --- BRAINFLOW SETUP ---
    params = BrainFlowInputParams()
    board_id = BoardIds.SYNTHETIC_BOARD.value
    board = BoardShim(board_id, params)
    sampling_rate = board.get_sampling_rate(board_id) 

    # Generate the 1Hz - 40Hz Filter for ERN (Autonomy)
    b_ern, a_ern = butter_bandpass(lowcut=1.0, highcut=40.0, fs=sampling_rate, order=4)
    
    # Generate the 12Hz - 30Hz Filter for Beta (Attention)
    b_beta, a_beta = butter_bandpass(lowcut=12.0, highcut=30.0, fs=sampling_rate, order=4)

    print("--- SnapBack DSP Telemetry Router [Data Vault Edition] ---")
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
                
                # --- INJECT SYNTHETIC BETA (Simulating drifting focus) ---
                focus_amplitude += random.uniform(-2.0, 2.0)
                focus_amplitude = np.clip(focus_amplitude, 3.0, 30.0) 
                
                t = np.linspace(0, 1, 250)
                beta_wave = focus_amplitude * np.sin(2 * np.pi * 20 * t)
                raw_eeg += beta_wave
                
                # --- INJECT SYNTHETIC ERN (Sharp negative drop) ---
                ern_triggered = 0 # Track if an ERN hit this exact frame
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

                # --- SQLITE VAULT LOGGING ---
                current_time = datetime.now().isoformat()
                db_cursor.execute(
                    "INSERT INTO cognitive_telemetry VALUES (?, ?, ?, ?)", 
                    (current_time, autonomy_index, attention_index, ern_triggered)
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
        print("\nShutting down DSP Engine and sealing Data Vault...")
    finally:
        db_conn.close() # Safely lock the database on exit
        board.stop_stream()
        board.release_session()
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
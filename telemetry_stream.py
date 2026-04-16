import time
import random
import zmq
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
    
    # NEW: Generate the 12Hz - 30Hz Filter for Beta (Attention)
    b_beta, a_beta = butter_bandpass(lowcut=12.0, highcut=30.0, fs=sampling_rate, order=4)

    print("--- SnapBack DSP Telemetry Router [Dual-Channel Edition] ---")
    print(f"Filter 1 (ERN): 1Hz - 40Hz Bandpass")
    print(f"Filter 2 (Beta): 12Hz - 30Hz Bandpass")
    
    try:
        board.prepare_session()
        board.start_stream()
        print("\nLive Stream: ON. Broadcasting Autonomy & Attention...\n")

        autonomy_index = 0.85 
        focus_amplitude = 15.0 # Starting amplitude for our simulated Beta wave
        
        while True:
            data = board.get_current_board_data(250)
            
            if data.shape[1] >= 250:
                raw_eeg = data[1] 
                
                # --- INJECT SYNTHETIC BETA (Simulating drifting focus) ---
                # A 20Hz wave whose amplitude slowly drifts up and down
                focus_amplitude += random.uniform(-2.0, 2.0)
                focus_amplitude = np.clip(focus_amplitude, 3.0, 30.0) 
                
                t = np.linspace(0, 1, 250)
                beta_wave = focus_amplitude * np.sin(2 * np.pi * 20 * t)
                raw_eeg += beta_wave
                
                # --- INJECT SYNTHETIC ERN (Sharp negative drop) ---
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
                else:
                    if autonomy_index < 0.85:
                        autonomy_index += 0.02 
                        autonomy_index = min(autonomy_index, 0.85)

                # ==========================================
                # APPLY THE MATH: CHANNEL 2 (ATTENTION / BETA)
                # ==========================================
                filtered_beta = apply_filter(raw_eeg, b_beta, a_beta)
                
                # Standard deviation represents the "power" of the isolated Beta waves
                beta_power = np.std(filtered_beta)
                
                # Map the power (approx 3.0 to 30.0) to an index of 0.1 to 1.0
                attention_index = np.clip(beta_power / 30.0, 0.1, 1.0)

                # --- ZMQ MULTI-BROADCAST ---
                socket.send_string(f"AUTONOMY {autonomy_index:.2f}")
                socket.send_string(f"ATTENTION {attention_index:.2f}")

                # UI formatting
                bar_length = 15
                ai_fill = int(autonomy_index * bar_length)
                human_fill = bar_length - ai_fill
                bar = f"[{'#' * ai_fill}{'-' * human_fill}]"

                print(f"ERN: {min_voltage:7.2f}uV | Autonomy: {autonomy_index*100:5.1f}% {bar} | Attention: {attention_index*100:5.1f}%", end='\r')

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nShutting down DSP Engine...")
    finally:
        board.stop_stream()
        board.release_session()
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
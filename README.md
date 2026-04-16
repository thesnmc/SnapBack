# SnapBack: Neural Routing Engine

**SnapBack** is a zero-latency, brokerless, offline Brain-Computer Interface (BCI) routing engine. It mathematically filters raw neural telemetry (simulated or physical) to dynamically throttle AI autonomy, kinematic robotic systems, and OS-level hardware based on a human's physiological cognitive state.

Built by **thesnmc**, this architecture enforces true "physiological grounding" for AI agents. It does not wait for a behavioral proxy (like a mouse click or a text prompt). If the system detects an Error-Related Negativity (ERN) spike, it physically revokes downstream AI autonomy in milliseconds. Furthermore, the system records all neural telemetry into a permanent, locally encrypted SQLite Black Box, allowing the AI to look backward in time and dynamically diagnose your cognitive fatigue using Retrieval-Augmented Generation (RAG).

---

## 🧠 The Architecture Matrix

The swarm operates on a local ZeroMQ publish/subscribe network (`tcp://127.0.0.1:5555`). It consists of seven isolated components:

1. **The DSP Router (`telemetry_stream.py`):** The core engine. It ingests raw BrainFlow EEG data (via hardware or simulation), applies 4th-order Butterworth bandpass filters (1-40Hz for ERN, 12-30Hz for Beta Attention), and broadcasts the data. It also captures a **Session Tag** and logs every millisecond of data to an offline SQLite database.
2. **The Command Center (`dashboard.py`):** A lightweight FastAPI server pushing ZeroMQ telemetry over WebSockets to a sleek, dark-mode 60FPS **Chart.js dual-line EKG oscilloscope**.
3. **The OS-Hook AI Agent (`ai_agent.py`):** A local LLM (powered by Ollama). It maps your Beta Attention to its core "Temperature." When autonomy drops, it hard-freezes text generation and triggers an OS-level media interrupt (Play/Pause). It features **Cognitive RAG**, meaning you can ask the AI questions about your focus, and it will read your SQLite database to answer you.
4. **The Robotics Sandbox (`drone_agent.py`):** A native Python kinematic simulation proving the engine can halt robotic movement mid-flight upon cognitive override.
5. **The Black Box Visualizer (`read_vault.py`):** A post-mortem data analytics tool. It reads your SQLite vault and renders a high-res, topographical `matplotlib` graph of your brainwaves, marking exact ERN kill-switch events.
6. **The Vault Toolkit (`seed_vault.py` / `wipe_vault.py`):** Database management tools to inject 10-minute high-density stress tests into the vault or surgically wipe it clean.
7. **The Swarm Commander (`boot_swarm.py`):** A native Windows Python bootloader that automatically orchestrates and sequences the 4-node terminal ignition.

---

## ⚙️ Installation Guide (Windows / Python 3.14+)

This system is built for bleeding-edge Python environments. All components are strictly offline, zero-knowledge, and local.

### 1. Prerequisites
* **Python 3.14+** installed on your Windows machine.
* **Ollama** installed locally (with the model pulled: run `ollama run llama3.2:1b` in your terminal to verify).

### 2. Environment Setup
Open PowerShell, navigate to your project folder, and isolate the environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install the required mathematical, networking, frontend, and data-science libraries.

```powershell
pip install brainflow numpy scipy pyzmq pyautogui fastapi uvicorn websockets tornado ollama pandas matplotlib
```

---

## 🔌 The Hardware Bridge (Physical Headset Setup)
By default, SnapBack boots in Simulation Mode, utilizing BrainFlow's `SYNTHETIC_BOARD` to generate organic, drifting brainwaves for testing.
If you own physical EEG hardware (e.g., OpenBCI Cyton, Muse, Ganglion), you can instantly bridge the gap to real-world biology:

1. Open `telemetry_stream.py`.
2. Locate the HARDWARE CONFIGURATION BLOCK at the very top.
3. Change `USE_REAL_HARDWARE = False` to `True`.
4. Update `EEG_SERIAL_PORT = "COM3"` to match your headset's Bluetooth/USB port.

---

## 🚀 The Boot Sequence (Running the Swarm)

### Option A: The 1-Click Bootloader (Recommended)
You do not need to open multiple windows. Simply open one PowerShell terminal, activate your environment, and run the Swarm Commander:

```powershell
python boot_swarm.py
```
This will automatically launch, sequence, and connect the Router, Dashboard, Sandbox, and AI Agent in their own dedicated windows.

### Option B: Manual Ignition Sequence
If you prefer to run nodes individually for testing or debugging, open four separate terminal windows, activate the virtual environment (`.\venv\Scripts\Activate.ps1`) in all of them, and boot them in this exact order:

**Terminal 1: Boot the Core Router**
```powershell
python telemetry_stream.py
```
> The terminal will ask for a Session Tag (e.g., "Coding" or "Gaming"). Type your tag and hit Enter. The Black Box is now recording.

**Terminal 2: Boot the Command Center**
```powershell
python dashboard.py
```
> Open your browser to http://127.0.0.1:8001 to view the live Chart.js EKG dashboard.

**Terminal 3: Boot the Robotics Sandbox**
```powershell
python drone_agent.py
```

**Terminal 4: Boot the Cognitive AI Agent**
*(Tip: Play a YouTube video or Spotify track in the background before running this to witness the OS hardware interrupt).*
```powershell
python ai_agent.py
```

---

## 📊 Post-Mortem Analytics (Reading the Black Box)
When your session is complete, go to the Router Terminal and press `Ctrl + C`. This safely shuts down the DSP engine and seals the `axon6_blackbox.db` SQLite file.
To view your session topography, run the visualizer from any active terminal:

```powershell
python read_vault.py
```
This will print your session statistics and open a highly detailed Matplotlib graph showing your Beta Attention, Autonomy Index, and the exact timestamps of your ERN spikes.

**Managing the Vault:**
* To test the visualizer without waiting, run `python seed_vault.py` to inject 10 minutes (6,000 rows) of synthetic stress-test telemetry.
* To clear the database for a fresh live session, run `python wipe_vault.py`.

---

## ⚖️ LICENSE
Apache License 2.0
Copyright 2026 thesnmc
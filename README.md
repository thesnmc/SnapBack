# SnapBack: Neural Routing Engine

**SnapBack** is a zero-latency, brokerless, offline Brain-Computer Interface (BCI) routing engine. It mathematically filters raw neural telemetry (simulated or physical) to dynamically throttle AI autonomy, kinematic robotic systems, and OS-level hardware based on a human's physiological cognitive state.

Built by **thesnmc**, this architecture enforces true "physiological grounding" for AI agents. It does not wait for a behavioral proxy (like a mouse click or a text prompt). If the system detects an Error-Related Negativity (ERN) spike, it physically revokes downstream AI autonomy in milliseconds. Furthermore, the system records all neural telemetry into a permanent, locally encrypted SQLite Black Box, allowing the AI to look backward in time and dynamically diagnose your cognitive fatigue using Retrieval-Augmented Generation (RAG).

---

## 🧠 The Architecture Matrix

The swarm operates on a local ZeroMQ publish/subscribe network (`tcp://127.0.0.1:5555`). It consists of six isolated nodes:

1. **The DSP Router (`telemetry_stream.py`):** The core engine. It ingests raw BrainFlow EEG data (via hardware or simulation), applies 4th-order Butterworth bandpass filters (1-40Hz for ERN, 12-30Hz for Beta Attention), and broadcasts the data. It also captures a **Session Tag** and logs every millisecond of data to an offline SQLite database.
2. **The Command Center (`dashboard.py`):** A lightweight FastAPI server pushing ZeroMQ telemetry over WebSockets to a sleek, dark-mode 60FPS **Chart.js dual-line EKG oscilloscope**.
3. **The OS-Hook AI Agent (`ai_agent.py`):** A local LLM (powered by Ollama). It maps your Beta Attention to its core "Temperature." When autonomy drops, it hard-freezes text generation and triggers an OS-level media interrupt (Play/Pause). It features **Cognitive RAG**, meaning you can ask the AI questions about your focus, and it will read your SQLite database to answer you.
4. **The Robotics Sandbox (`drone_agent.py`):** A native Python kinematic simulation proving the engine can halt robotic movement mid-flight upon cognitive override.
5. **The Black Box Visualizer (`read_vault.py`):** A post-mortem data analytics tool. It reads your SQLite vault and renders a high-res, topographical `matplotlib` graph of your brainwaves, marking exact ERN kill-switch events.
6. **The Vault Toolkit (`seed_vault.py` / `wipe_vault.py`):** Database management tools to inject 10-minute high-density stress tests into the vault or surgically wipe it clean.

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
2. Locate the **HARDWARE CONFIGURATION BLOCK** at the very top.
3. Change `USE_REAL_HARDWARE = False` to `True`.
4. Update `EEG_SERIAL_PORT = "COM3"` to match your headset's Bluetooth/USB port.

---

## 🚀 The Boot Sequence (Running the Swarm)

To witness the full closed-loop protocol, you must run the nodes in parallel. Open four separate terminal windows, activate the virtual environment (`.\venv\Scripts\Activate.ps1`) in all of them, and boot them in this exact order:

**Terminal 1: Boot the Core Router**
```powershell
python telemetry_stream.py
```
*-> The terminal will ask for a Session Tag (e.g., "Coding" or "Gaming"). Type your tag and hit Enter. The Black Box is now recording.*

**Terminal 2: Boot the Command Center**
```powershell
python dashboard.py
```
*-> Open your browser to http://127.0.0.1:8001 to view the live Chart.js EKG dashboard.*

**Terminal 3: Boot the Robotics Sandbox**
```powershell
python drone_agent.py
```

**Terminal 4: Boot the Cognitive AI Agent**
*(Tip: Play a YouTube video or Spotify track in the background before running this to witness the OS hardware interrupt).*
```powershell
python ai_agent.py
```
*-> The AI will ask you for input. If you hit Enter, it enters an infinite autonomous loop, adjusting its temperature to your brainwaves. If you type a question (e.g., "How is my focus right now?"), it will execute a Neural RAG lookup into your database and diagnose you.*

---

## 📊 Post-Mortem Analytics (Reading the Black Box)

When your session is complete, go to **Terminal 1** and press `Ctrl + C`. This safely shuts down the DSP engine and seals the `axon6_blackbox.db` SQLite file.

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

**Apache License 2.0**
Copyright 2026 thesnmc

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
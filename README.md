# SnapBack: Neural Routing Engine

**SnapBack** is a zero-latency, brokerless, offline Brain-Computer Interface (BCI) routing engine. It mathematically filters raw neural telemetry (simulated or physical) to dynamically throttle AI autonomy, kinematic robotic systems, and OS-level hardware based on a human's physiological cognitive state.

Built by **thesnmc**, this architecture enforces true "physiological grounding" for AI agents. It does not wait for a behavioral proxy (like a mouse click or a text prompt). If the system detects an Error-Related Negativity (ERN) spike, it physically revokes downstream AI autonomy in milliseconds.

---

## 🧠 The Architecture Matrix

The swarm operates on a local ZeroMQ publish/subscribe network (`tcp://127.0.0.1:5555`). It consists of four isolated nodes:

1. **The DSP Router (`telemetry_stream.py`):** The core engine. It ingests raw BrainFlow EEG data, applies 4th-order Butterworth bandpass filters (1-40Hz for ERN, 12-30Hz for Beta Attention), calculates signal power, and blasts the cognitive states to the local network.
2. **The Command Center (`dashboard.py`):** A lightweight FastAPI/Tornado server pushing the ZeroMQ dual-channel telemetry over WebSockets to a sleek, dark-mode 60FPS HTML5 canvas oscilloscope.
3. **The OS-Hook Agent (`ai_agent.py`):** A local LLM generator (powered by Ollama). When autonomy drops, this agent hard-freezes text generation and triggers an OS-level media interrupt (Play/Pause) via simulated keystrokes.
4. **The Robotics Sandbox (`drone_agent.py`):** A native Python Tkinter kinematic simulation. Proves the engine can physically halt 2D/3D robotic movement mid-flight upon cognitive override.

---

## ⚙️ Installation Guide (Windows / Python 3.14+)

This system is built for bleeding-edge Python environments. All components are strictly offline and zero-knowledge.

### 1. Prerequisites
* **Python 3.14+** installed on your Windows machine.
* **Ollama** installed locally (with the `llama3.2:1b` model pulled: `ollama run llama3.2:1b`).

### 2. Environment Setup
Open PowerShell, navigate to your project folder, and isolate the environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install the required mathematical, networking, and server libraries. *(Note: `tornado` is explicitly required to bridge ZeroMQ's async loops with Python 3.14's Windows event loop).*
```powershell
pip install brainflow numpy scipy pyzmq pyautogui fastapi uvicorn websockets tornado ollama
```

---

## 🚀 The Boot Sequence (Running the Swarm)

To witness the full protocol, you must run the nodes in parallel. Open **four separate terminal windows**, activate the virtual environment in all of them, and boot them in this exact order:

**Terminal 1: Boot the Core Router**
```powershell
.\venv\Scripts\python.exe telemetry_stream.py
```

**Terminal 2: Boot the Command Center**
```powershell
.\venv\Scripts\python.exe dashboard.py
```
*-> Open your browser to `http://127.0.0.1:8001` to view the live dashboard.*

**Terminal 3: Boot the Robotics Sandbox**
```powershell
.\venv\Scripts\python.exe drone_agent.py
```

**Terminal 4: Boot the OS-Hook AI Agent**
*(Play some background music on your PC before running this to see the OS interrupt working).*
```powershell
.\venv\Scripts\python.exe ai_agent.py
```

---

## ⚖️ LICENSE

**Apache License 2.0** *Copyright 2026 thesnmc*

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0). Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

---

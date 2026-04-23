# 🚀 SnapBack: Neural Routing Engine
> A zero-latency, brokerless Brain-Computer Interface (BCI) routing engine that mathematically filters physiological data to dynamically throttle AI autonomy and OS hardware.

[![License](https://img.shields.io/badge/License-TheSNMC-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Python-lightgrey)]()
[![Architecture](https://img.shields.io/badge/Architecture-Offline--First-success)]()

---

## 📖 Overview
SnapBack solves a critical flaw in modern artificial intelligence: the lack of physiological grounding. Current AI systems wait for a behavioral proxy—like a mouse click or a typed text prompt—to understand human intent. SnapBack bypasses the physical interface entirely by reading raw neural telemetry and translating subconscious cognitive states directly into machine constraints. 

If the system detects an Error-Related Negativity (ERN) spike—the subconscious realization that a mistake has occurred—it physically revokes downstream AI autonomy in milliseconds. This hard-freezes local LLM text generation and triggers an OS-level interrupt to pause system media. Furthermore, it logs every millisecond of this physiological session into a locally encrypted SQLite vault, enabling a Cognitive RAG (Retrieval-Augmented Generation) system where the AI can analyze your brainwaves and diagnose your fatigue over time.

Designed as a multi-node swarm, SnapBack operates over a local ZeroMQ publish/subscribe network. It acts as the ultimate local-host bridge between the human nervous system and edge-compute AI.

**The Core Mandate:** Complete physiological data sovereignty. Neural telemetry is the most sensitive data in existence. SnapBack operates with a strict zero-cloud policy, ensuring that all DSP filtering, data vaulting, and AI inference execute exclusively on local silicon to protect the user from corporate data extraction.

## ✨ Key Features
* **Zero-Latency DSP Routing:** Ingests raw microvolts at 250Hz+ and applies 4th-order Butterworth bandpass filters (1-40Hz for ERN, 12-30Hz for Beta Attention) to calculate real-time Autonomy and Focus indices.
* **Deep-Throttle AI Constraints:** Maps physiological "Beta Attention" directly to an LLM's inference temperature, making the AI strict when you are focused, and creative when your mind wanders.
* **Cognitive RAG Memory:** Automatically archives session topography into an offline SQLite Black Box. The AI agent queries this database to act as a personalized neural science officer.
* **Hardware OS Overrides:** Utilizes native keyboard hooking to physically halt system-wide media and hardware execution the millisecond an ERN spike drops the Autonomy index below 80%.
* **1-Click Swarm Ignition:** Bypasses complex multi-terminal setups with a native Python Bootloader (`boot_swarm.py`) that sequences and connects all 4 nodes of the matrix instantly.
* **Hardware Agnostic:** Features a toggleable bridge for real physical EEG headsets (e.g., OpenBCI, Muse), while defaulting to a Synthetic BCI board for accessible developer simulation.

## 🛠️ Tech Stack
* **Language:** Python 3.14+
* **Framework:** FastAPI, WebSockets, Tkinter (Kinematics)
* **Environment:** Windows PowerShell / VS Code
* **Key Libraries/APIs:** `BrainFlow` (EEG Acquisition), `SciPy` / `NumPy` (Digital Signal Processing), `PyZMQ` (Asynchronous Networking), `Ollama` (Local LLM Inference), `Chart.js` (Hardware-Accelerated UI).

## ⚙️ Architecture & Data Flow
SnapBack operates as a decentralized 7-node swarm over `tcp://127.0.0.1:5555`. 

* **Input:** The `telemetry_stream.py` Router ingests raw neural data from the headset COM port.
* **Processing:** The Router applies Butterworth filters to isolate specific brainwaves, calculating signal power. It logs this to the SQLite Black Box and blasts a serialized string over the ZMQ network.
* **Output:** Downstream nodes react independently. The `dashboard.py` server renders a 60FPS dual-line EKG. The `drone_agent.py` halts kinematic movement. The `ai_agent.py` locks LLM temperature and executes PyAutoGUI hooks to pause the OS if an ERN is detected.

## 🔒 Privacy & Data Sovereignty
* **Data Collection:** Zero external transmission. All telemetry is written strictly to a local `axon6_blackbox.db` SQLite file. 
* **Permissions Required:** OS-level keystroke permissions are required for `PyAutoGUI` to execute the system-wide media pause (Play/Pause media key emulation).
* **Cloud Connectivity:** Explicitly disabled. The Ollama LLM runs on local silicon, and the web dashboard runs on a local ASGI loop. 

## 🚀 Getting Started

### Prerequisites
* Windows OS with **Python 3.14+** installed.
* **Ollama** installed locally with the `llama3.2:1b` model pulled (`ollama run llama3.2:1b`).

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/snapback.git](https://github.com/yourusername/snapback.git)
   ```

2. **Open your terminal in the project directory and isolate the environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install the required engineering and mathematical dependencies:**
   ```bash
   pip install brainflow numpy scipy pyzmq pyautogui fastapi uvicorn websockets tornado ollama pandas matplotlib
   ```

4. **Ignite the Swarm:**
   Run the master bootloader to automatically launch and connect the entire matrix in parallel.
   ```bash
   python boot_swarm.py
   ```
   *(Note: To connect physical BCI hardware, open `telemetry_stream.py` and set `USE_REAL_HARDWARE = True` prior to boot).*

## 🤝 Contributing
Contributions, issues, and feature requests are welcome. Feel free to check the issues page if you want to contribute to expanding the multi-modal sensors (e.g., OpenCV eye-tracking integration) or optimizing the DSP matrix.

## 📄 License
Tsee the LICENSE file for details.
Built by an independent developer in Chennai, India.

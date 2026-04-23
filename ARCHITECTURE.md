# 🏗️ Architecture & Design Document: SnapBack Neural Routing Engine

**Version:** 1.0.0-Phase6 | **Date:** 2026-04-23 | **Author:** Sujay

---

## 1. Executive Summary

This document outlines the architecture for **SnapBack**, a zero-latency, decentralized Brain-Computer Interface (BCI) routing engine. The overarching technical goal is to enforce true "physiological grounding" on edge-compute artificial intelligence. Rather than relying on behavioral proxies (text input or mouse clicks), SnapBack reads raw neural telemetry to dynamically throttle AI autonomy, kinematic robotics, and OS-level hardware. Designed as a localized multi-node swarm, it adheres to a strict zero-cloud mandate, ensuring that the user's most sensitive physiological data never leaves their local silicon.

## 2. Architectural Drivers

* **Primary Goals:** * Achieve sub-20ms latency from physiological event detection to hardware/OS override.
    * Enforce absolute physiological data sovereignty via local-only processing.
    * Provide real-time cognitive state mapping to LLM inference parameters (Temperature).
* **Technical Constraints:** * Must run entirely locally on prosumer Windows hardware.
    * Hardware-agnostic design (must support seamless bridging between simulated synthetic boards and physical EEG hardware like OpenBCI/Muse).
    * Must sequence and manage 4+ isolated Python processes concurrently without port collisions.
* **Non-Functional Requirements (NFRs):**
    * *Security/Privacy:* Air-gapped from cloud APIs; all data is vaulted in offline, local storage.
    * *Reliability:* Must gracefully handle node crashes (e.g., if the LLM crashes, the DSP routing engine must survive).
    * *Performance:* High-frequency signal processing (250Hz+) cannot block UI rendering or asynchronous networking loops.

## 3. System Architecture (The 10,000-Foot View)

SnapBack utilizes a decentralized, multi-node publisher/subscriber swarm architecture over `tcp://127.0.0.1:5555`. 

* **Presentation Layer:** * *Command Center (`dashboard.py`):* A FastAPI backend bridging ZeroMQ telemetry to WebSockets. The frontend is a vanilla HTML5/JS dashboard utilizing hardware-accelerated `Chart.js` for a 60FPS dual-line EKG.
    * *Black Box Visualizer (`read_vault.py`):* A post-mortem Matplotlib topological renderer.
* **Domain Layer (Inference & Action):** * *Cognitive Agent (`ai_agent.py`):* Bridges the neural telemetry to a local instance of Ollama (Llama 3.2 1B). Modulates LLM Temperature inversely to user Focus.
    * *Robotics Sandbox (`drone_agent.py`):* Kinematic vector physics simulation testing physical hardware halts.
* **Data/Hardware Layer:** * *DSP Router (`telemetry_stream.py`):* The core engine. Interfaces directly with `BrainFlow` to ingest $\mu V$ EEG data, applies Digital Signal Processing (DSP), broadcasts to the ZMQ fabric, and acts as the master write-node for the SQLite Vault.

## 4. Design Decisions & Trade-Offs (The "Why")

* **Decision 1: ZeroMQ PUB/SUB over REST or MQTT/RabbitMQ Broker**
    * *Rationale:* To achieve the strict sub-20ms latency requirement for the ERN override, we bypassed HTTP overhead and heavy centralized message brokers. ZMQ operates as a brokerless, socket-level asynchronous fabric operating at near-memory speeds.
    * *Trade-off:* ZMQ does not inherently persist messages if a subscriber drops offline. We mitigated this by separating the "live control stream" (ZMQ) from the "persistent memory" (SQLite).
* **Decision 2: Local Ollama vs. Cloud AI APIs (OpenAI/Anthropic)**
    * *Rationale:* Adherence to the zero-cloud privacy mandate. Transmitting raw or processed brainwave states to external servers is an unacceptable privacy vector.
    * *Trade-off:* Limits the maximum intelligence of the agent to the user's available VRAM (e.g., restricting us to 1B - 8B parameter models instead of frontier 70B+ models).
* **Decision 3: SQLite in WAL Mode vs. Time-Series Databases (InfluxDB)**
    * *Rationale:* We required a zero-configuration, serverless, single-file data vault to maintain the "local-first" sovereign ethos. Write-Ahead Logging (WAL) ensures high-speed writes without locking out the Cognitive RAG reader.
    * *Trade-off:* Lacks the built-in horizontal scaling of a dedicated TSDB, though 250Hz telemetry over a 4-hour session remains well within SQLite's single-file operational limits.
* **Decision 4: PyAutoGUI for OS Hooks**
    * *Rationale:* We needed a universal way to halt system media across *all* applications (Spotify, YouTube, VLC) simultaneously when an ERN spike is detected. Emulating the global media `playpause` keystroke achieves this instantly.
    * *Trade-off:* Keystroke emulation can occasionally be overridden if a specific OS process aggressively captures foreground hardware focus.

## 5. Data Flow & Lifecycle

1.  **Ingestion:** The headset (or synthetic simulator) captures raw physiological microvolts ($\mu V$) at ~250Hz.
2.  **DSP Filtering:** The Router applies 4th-order Butterworth bandpass filters:
    * *Error-Related Negativity (ERN):* $1\text{Hz} - 40\text{Hz}$
    * *Cognitive Load (Beta):* $12\text{Hz} - 30\text{Hz}$
3.  **Routing & Vaulting:** Signal power is calculated into indices (0.0 to 1.0). The data is simultaneously logged to `axon6_blackbox.db` and blasted to `tcp://127.0.0.1:5555`.
4.  **Deep-Throttle Execution:** Downstream nodes ingest the telemetry. The AI agent calculates AI Temperature ($T$) as a function of Attention ($A$): 
    $$T = \text{clamp}(1.0 - A, 0.1, 0.9)$$
5.  **SnapBack Override:** If the ERN filter detects a catastrophic cognitive drop (Autonomy < 0.80), the LLM output stream is hard-paused and the `playpause` OS interrupt is fired.
6.  **Cognitive RAG:** Upon user query, the AI queries the SQLite Black Box, retrieves the last 1200 rows of telemetry, packages the statistical mean into its system prompt, and diagnoses the user's fatigue.

## 6. Security & Privacy Threat Model

* **Data at Rest:** Telemetry is written exclusively to local disk (`axon6_blackbox.db`). 
* **Data in Transit:** ZMQ sockets are bound strictly to the local loopback interface (`127.0.0.1`). The system is entirely air-gapped from external networks; no ingress/egress ports are exposed.
* **Mitigated Risks (Corporate Hijacking / SaaS-ification):** By licensing the entire architecture under **GNU AGPLv3**, we mitigate the risk of cloud providers scraping the codebase, removing the local privacy protections, and monetizing the physiological routing engine as a closed-source Web API. Any network interaction with a modified version of this software legally mandates full source-code disclosure.

## 7. Future Architecture Roadmap

* **Multi-Modal Sensor Fusion:** Current physiological detection relies solely on EEG variance. The next iteration will integrate OpenCV to track eye-blink rate and gaze drift via standard webcams, requiring a dual-confirmation (EEG Drop + Gaze Drift) before triggering a hard freeze.
* **Native OS Daemons:** Transitioning away from `PyAutoGUI` to native, lower-level OS hooks (e.g., Windows API C-bindings or macOS CoreAudio daemons) for more resilient media and hardware pausing.
* **P2P Mesh Telemetry:** Upgrading the ZMQ fabric to support CurveZMQ encryption, allowing secure, multi-user physiological routing across local area networks without a centralized server.

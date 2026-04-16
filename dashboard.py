import asyncio
import zmq
import zmq.asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# --- THE FRONTEND ---
html = """
<!DOCTYPE html>
<html>
<head>
    <title>SnapBack Neural Router</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas', monospace; text-align: center; margin-top: 30px; }
        h1 { color: #58a6ff; font-size: 2.5em; text-transform: uppercase; letter-spacing: 2px;}
        
        .grid-container { display: flex; justify-content: center; gap: 20px; margin: 20px auto; width: 800px; }
        
        .status-box { padding: 20px; flex: 1; border: 2px solid #30363d; border-radius: 10px; background: #161b22; }
        
        .value-text { font-size: 3.5em; font-weight: bold; margin: 10px 0; }
        .autonomy-color { color: #3fb950; }
        .attention-color { color: #a371f7; } /* Purple for Beta waves */
        
        .title-text { font-size: 1.2em; letter-spacing: 1px; color: #8b949e; }
        
        /* Chart container styling */
        .chart-container { width: 800px; margin: 20px auto; background: #000; border: 1px solid #30363d; border-radius: 5px; box-shadow: 0 0 20px rgba(0,0,0,0.5); padding: 10px; }
        
        .frozen { color: #ff7b72 !important; }
        .frozen-border { border-color: #ff7b72 !important; box-shadow: 0 0 30px rgba(255, 123, 114, 0.4); }
    </style>
</head>
<body>
    <h1>SNAPBACK: REAL-TIME ROUTER</h1>
    
    <div class="grid-container">
        <div id="autonomy-box" class="status-box">
            <div id="autonomy-title" class="title-text">AUTONOMY INDEX</div>
            <div id="autonomy-value" class="value-text autonomy-color">85%</div>
        </div>

        <div class="status-box">
            <div class="title-text">BETA ATTENTION</div>
            <div id="attention-value" class="value-text attention-color">0%</div>
        </div>
    </div>

    <div class="chart-container">
        <canvas id="ekgChart" height="200"></canvas>
    </div>

    <script>
        const ws = new WebSocket("ws://127.0.0.1:8001/ws");
        
        const autonomyTitle = document.getElementById('autonomy-title');
        const autonomyValue = document.getElementById('autonomy-value');
        const autonomyBox = document.getElementById('autonomy-box');
        const attentionValue = document.getElementById('attention-value');
        
        let currentAutonomy = 85; 
        let currentAttention = 0;

        ws.onopen = function() { console.log("WebSocket Connected"); };

        ws.onerror = function(error) {
            autonomyTitle.innerText = "NO SIGNAL";
            autonomyTitle.className = "title-text frozen";
        };

        // --- NEW: Chart.js Initialization ---
        const ctx = document.getElementById('ekgChart').getContext('2d');
        const ekgChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: new Array(100).fill(''), // 100 data points on screen
                datasets: [
                    {
                        label: 'Autonomy Index',
                        borderColor: '#3fb950',
                        borderWidth: 3,
                        pointRadius: 0, // Hide dots for that smooth EKG look
                        tension: 0.3, // Slight curve
                        data: new Array(100).fill(85)
                    },
                    {
                        label: 'Beta Attention',
                        borderColor: '#a371f7',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.3,
                        data: new Array(100).fill(0)
                    }
                ]
            },
            options: {
                animation: false, // Turn off animation so it snaps instantly like an oscilloscope
                responsive: true,
                scales: {
                    x: { display: false }, // Hide the timeline axis
                    y: { 
                        min: 0, 
                        max: 100, 
                        grid: { color: '#30363d' }, // Dark grid lines
                        ticks: { color: '#8b949e' } 
                    }
                },
                plugins: {
                    legend: { labels: { color: '#c9d1d9', font: { family: 'Consolas' } } }
                }
            }
        });

        // --- Parsing zeroMQ streams and feeding Chart.js ---
        ws.onmessage = function(event) {
            const parts = event.data.split(" ");
            const metricType = parts[0];
            const value = parseFloat(parts[1]) * 100; // Convert to %
            
            if (metricType === "AUTONOMY") {
                currentAutonomy = value;
                autonomyValue.innerText = currentAutonomy.toFixed(0) + "%";
                
                // Visual freeze logic
                if (currentAutonomy < 80) {
                    autonomyTitle.innerText = "FROZEN (ERN OVERRIDE)";
                    autonomyTitle.className = "title-text frozen";
                    autonomyValue.className = "value-text frozen";
                    autonomyBox.className = "status-box frozen-border";
                    ekgChart.data.datasets[0].borderColor = '#ff7b72'; // Line turns red
                } else {
                    autonomyTitle.innerText = "AUTONOMY INDEX";
                    autonomyTitle.className = "title-text";
                    autonomyValue.className = "value-text autonomy-color";
                    autonomyBox.className = "status-box";
                    ekgChart.data.datasets[0].borderColor = '#3fb950'; // Line returns to green
                }

                // Push new data to the chart arrays and shift the oldest out
                ekgChart.data.datasets[0].data.push(currentAutonomy);
                ekgChart.data.datasets[0].data.shift();
                
                ekgChart.data.datasets[1].data.push(currentAttention);
                ekgChart.data.datasets[1].data.shift();
                
                ekgChart.update(); // Render the new frame
                
            } else if (metricType === "ATTENTION") {
                currentAttention = value;
                attentionValue.innerText = currentAttention.toFixed(0) + "%";
            }
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    ctx = zmq.asyncio.Context()
    socket = ctx.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:5555")
    
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    try:
        while True:
            message = await socket.recv_string()
            await websocket.send_text(message)
    except WebSocketDisconnect:
        print("Browser disconnected.")
    finally:
        socket.close()

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        pass 
        
    print("--- Booting SnapBack Command Center ---")
    print("Web Dashboard live at: http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
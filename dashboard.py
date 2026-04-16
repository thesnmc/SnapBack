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
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas', monospace; text-align: center; margin-top: 30px; }
        h1 { color: #58a6ff; font-size: 2.5em; text-transform: uppercase; letter-spacing: 2px;}
        
        .grid-container { display: flex; justify-content: center; gap: 20px; margin: 20px auto; width: 800px; }
        
        .status-box { padding: 20px; flex: 1; border: 2px solid #30363d; border-radius: 10px; background: #161b22; }
        
        .value-text { font-size: 3.5em; font-weight: bold; margin: 10px 0; }
        .autonomy-color { color: #3fb950; }
        .attention-color { color: #a371f7; } /* Purple for Beta waves */
        
        .title-text { font-size: 1.2em; letter-spacing: 1px; color: #8b949e; }
        
        canvas { background: #000; border: 1px solid #30363d; border-radius: 5px; margin-top: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        
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

    <canvas id="oscilloscope" width="800" height="200"></canvas>

    <script>
        const ws = new WebSocket("ws://127.0.0.1:8001/ws");
        const canvas = document.getElementById('oscilloscope');
        const ctx = canvas.getContext('2d');
        
        const autonomyTitle = document.getElementById('autonomy-title');
        const autonomyValue = document.getElementById('autonomy-value');
        const autonomyBox = document.getElementById('autonomy-box');
        const attentionValue = document.getElementById('attention-value');
        
        let dataHistory = new Array(800).fill(0.85); 
        let currentAutonomy = 0.85; 

        ws.onopen = function() { console.log("WebSocket Connected"); };

        ws.onerror = function(error) {
            autonomyTitle.innerText = "NO SIGNAL";
            autonomyTitle.className = "title-text frozen";
        };

        // NEW: Parsing multiple data streams from ZeroMQ
        ws.onmessage = function(event) {
            const parts = event.data.split(" ");
            const metricType = parts[0];
            const value = parseFloat(parts[1]);
            
            if (metricType === "AUTONOMY") {
                currentAutonomy = value;
                autonomyValue.innerText = (currentAutonomy * 100).toFixed(0) + "%";
                
                if (currentAutonomy < 0.80) {
                    autonomyTitle.innerText = "FROZEN (ERN OVERRIDE)";
                    autonomyTitle.className = "title-text frozen";
                    autonomyValue.className = "value-text frozen";
                    autonomyBox.className = "status-box frozen-border";
                } else {
                    autonomyTitle.innerText = "AUTONOMY INDEX";
                    autonomyTitle.className = "title-text";
                    autonomyValue.className = "value-text autonomy-color";
                    autonomyBox.className = "status-box";
                }
            } else if (metricType === "ATTENTION") {
                attentionValue.innerText = (value * 100).toFixed(0) + "%";
            }
        };

        function renderLoop() {
            dataHistory.push(currentAutonomy);
            dataHistory.shift(); 

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            ctx.strokeStyle = '#30363d';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(0, canvas.height * 0.2); 
            ctx.lineTo(canvas.width, canvas.height * 0.2); 
            ctx.stroke();

            ctx.lineWidth = 3;
            ctx.beginPath();
            
            for (let i = 0; i < canvas.width; i++) {
                let y = canvas.height - (dataHistory[i] * canvas.height); 
                if (i === 0) ctx.moveTo(i, y);
                else ctx.lineTo(i, y);
            }

            ctx.strokeStyle = currentAutonomy < 0.80 ? '#ff7b72' : '#3fb950'; 
            ctx.stroke();

            requestAnimationFrame(renderLoop);
        }

        renderLoop();
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
    
    # FIX: Subscribe to an empty string to receive ALL data from the router
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    try:
        while True:
            # Receive the raw string ("AUTONOMY 0.85" or "ATTENTION 0.45")
            message = await socket.recv_string()
            
            # Forward the whole string to the frontend to be parsed
            await websocket.send_text(message)
    except WebSocketDisconnect:
        print("Browser disconnected.")
    finally:
        socket.close()

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        pass # Keeping this clean since Tornado handles the async bridge now
        
    print("--- Booting SnapBack Command Center ---")
    print("Web Dashboard live at: http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
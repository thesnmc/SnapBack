import zmq
import tkinter as tk
import math

class DroneSandbox:
    def __init__(self, root):
        self.root = root
        self.root.title("AXON-6: Robotic Autonomy Sandbox")

        # --- ZMQ SETUP ---
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "AUTONOMY")

        self.current_autonomy = 0.85

        # --- UI SETUP ---
        self.canvas = tk.Canvas(root, width=800, height=600, bg="#141419")
        self.canvas.pack()

        # Drone State
        self.target_x, self.target_y = 700.0, 300.0
        self.drone_x, self.drone_y = 50.0, 300.0
        self.drone_speed = 3.0

        # Draw Target (Static)
        self.canvas.create_oval(self.target_x-20, self.target_y-20,
                                self.target_x+20, self.target_y+20,
                                outline="#646464", width=2)

        # Draw Drone
        self.drone_id = self.canvas.create_rectangle(self.drone_x-15, self.drone_y-15,
                                                     self.drone_x+15, self.drone_y+15,
                                                     fill="#00FF64")

        # Draw Text
        self.text_id = self.canvas.create_text(20, 20, anchor="nw",
                                               fill="white", font=("Consolas", 14),
                                               text="AI STATUS: FULL AUTONOMY | AUTONOMY: 85%")

        # Start the physics loop
        self.update_loop()

    def update_loop(self):
        # 1. Drain the ZMQ Queue for real-time telemetry
        while True:
            try:
                msg = self.socket.recv_string(flags=zmq.NOBLOCK)
                _, val = msg.split()
                self.current_autonomy = float(val)
            except zmq.Again:
                break

        # 2. Neural Routing Logic
        is_frozen = self.current_autonomy < 0.80

        # 3. Kinematic Math (Move the drone if not frozen)
        if not is_frozen:
            dx = self.target_x - self.drone_x
            dy = self.target_y - self.drone_y
            dist = math.hypot(dx, dy)

            if dist > 5.0: # If we haven't reached the target
                self.drone_x += (dx / dist) * self.drone_speed
                self.drone_y += (dy / dist) * self.drone_speed
            else:
                self.drone_x, self.drone_y = 50.0, 300.0 # Reset to loop

        # 4. Render Updates
        color = "#FF3232" if is_frozen else "#00FF64"
        
        # Move drone rect
        self.canvas.coords(self.drone_id, self.drone_x-15, self.drone_y-15, self.drone_x+15, self.drone_y+15)
        self.canvas.itemconfig(self.drone_id, fill=color)

        # Update text
        status_text = "FROZEN (ERN OVERRIDE)" if is_frozen else "FULL AUTONOMY"
        self.canvas.itemconfig(self.text_id, text=f"AI STATUS: {status_text} | AUTONOMY: {self.current_autonomy*100:.0f}%")

        # Loop again in 16 milliseconds (~60 FPS)
        self.root.after(16, self.update_loop)

    def on_close(self):
        print("\nShutting down Drone Agent...")
        self.socket.close()
        self.context.term()
        self.root.destroy()

if __name__ == "__main__":
    print("--- SnapBack Robotics Sandbox Booting ---")
    print("Connected to SnapBack Router. Initiating AI Flight Path...")
    root = tk.Tk()
    app = DroneSandbox(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
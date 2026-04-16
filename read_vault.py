import sqlite3
import pandas as pd # If you don't have pandas, run: pip install pandas
import matplotlib.pyplot as plt # NEW: For Target A visualizer
import matplotlib.dates as mdates # NEW: To format the timestamp axis cleanly

def analyze_session():
    # Connect to the local vault
    db_path = "axon6_blackbox.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Load the data into a Pandas DataFrame for easy math
        df = pd.read_sql_query("SELECT * FROM cognitive_telemetry", conn)
        conn.close()

        if df.empty:
            print("The vault is empty. Run the telemetry_stream.py for a bit longer!")
            return

        # Convert timestamp strings to actual datetime objects for graphing
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        print("\n--- AXON-6 BLACK BOX RETRIEVAL ---")
        print(f"Total Data Points Harvested: {len(df)}")
        print(f"Session Duration (approx): {len(df) * 0.1:.1f} seconds")
        
        # Handle session tags if they exist (Target B compatibility)
        if 'session_tag' in df.columns:
            unique_tags = df['session_tag'].dropna().unique()
            tags_str = ", ".join(unique_tags) if len(unique_tags) > 0 else "None"
            print(f"Session Tags Found:   {tags_str}")
            
        print("-" * 35)

        # Calculate Cognitive Stats
        avg_attention = df['attention_index'].mean() * 100
        max_attention = df['attention_index'].max() * 100
        total_erns = df['ern_spike'].sum()

        print(f"Average Beta Attention: {avg_attention:.1f}%")
        print(f"Peak Focus Level:       {max_attention:.1f}%")
        print(f"Total SnapBack Events:  {total_erns} (AI Overrides)")
        print("-" * 35)

        # Show the last 5 entries to verify timestamps
        print("\nLatest 5 Telemetry Entries:")
        print(df.tail(5))

        # ==========================================
        # TARGET A: THE POST-MORTEM GRAPH (MATPLOTLIB)
        # ==========================================
        print("\n[*] Rendering Cognitive Post-Mortem Graph...")
        
        # Use a dark theme to match the SnapBack aesthetic
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot Attention (Purple)
        ax.plot(df['timestamp'], df['attention_index'] * 100, color='#a371f7', label='Beta Attention (%)', linewidth=2)
        
        # Plot Autonomy (Green)
        ax.plot(df['timestamp'], df['autonomy_index'] * 100, color='#3fb950', label='Autonomy Index (%)', linewidth=2)
        
        # Highlight ERN Spikes (Red vertical lines)
        ern_events = df[df['ern_spike'] == 1]
        for idx, row in ern_events.iterrows():
            # Only add the label to the legend once so it doesn't clutter it up
            ax.axvline(x=row['timestamp'], color='#ff7b72', linestyle='--', alpha=0.7, 
                       label='ERN Spike (SnapBack)' if idx == ern_events.index[0] else "")

        # Graph formatting
        ax.set_title('AXON-6: Cognitive Telemetry Post-Mortem', fontsize=16, fontweight='bold', color='#58a6ff')
        ax.set_xlabel('Timeline', fontsize=12, color='#8b949e')
        ax.set_ylabel('Percentage (%)', fontsize=12, color='#8b949e')
        ax.set_ylim(-5, 105) # Lock Y axis from 0 to 100%
        ax.grid(True, color='#30363d', linestyle='-', alpha=0.5)
        ax.legend(loc='upper right', facecolor='#161b22', edgecolor='#30363d')
        
        # Clean up the X-axis time formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Show the plot
        plt.show()

    except Exception as e:
        print(f"Error reading the vault: {e}")

if __name__ == "__main__":
    analyze_session()
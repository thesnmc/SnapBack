import sqlite3
import pandas as pd # If you don't have pandas, run: pip install pandas

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

        print("\n--- AXON-6 BLACK BOX RETRIEVAL ---")
        print(f"Total Data Points Harvested: {len(df)}")
        print(f"Session Duration (approx): {len(df) * 0.1:.1f} seconds")
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

    except Exception as e:
        print(f"Error reading the vault: {e}")

if __name__ == "__main__":
    analyze_session()
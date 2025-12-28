"""
Launch Hospital C Interface
Run this to start Hospital C's web interface
"""
import os
import sys

# Set hospital ID
os.environ['HOSPITAL_ID'] = 'C'

# Import and run the hospital interface
from hospital_interface import app, initialize, HOSPITAL_ID

if __name__ == '__main__':
    print("=" * 70)
    print(f" " * 20 + "HOSPITAL C INTERFACE")
    print("=" * 70)
    print(f"\n[INFO] Starting web interface for Hospital C...")
    print(f"[INFO] Open your browser and navigate to:")
    print(f"\n       http://localhost:5003")
    print(f"\n[INFO] Data directory: data/Hospital_C/")
    print(f"[INFO] Make sure the central server is running at:")
    print(f"       http://localhost:8000")
    print("\n" + "=" * 70)
    
    initialize()
    
    app.run(debug=False, host='0.0.0.0', port=5003, threaded=True)

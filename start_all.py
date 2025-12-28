"""
Quick Start - Launch All Hospitals
This script helps you start the central server and all hospital interfaces
"""
import subprocess
import time
import sys
import os

def print_banner():
    print("=" * 70)
    print(" " * 15 + "FEDERATED LEARNING QUICK START")
    print("=" * 70)

def start_server():
    print("\n[1/4] Starting Central Server...")
    print("      Port: 8000")
    server_process = subprocess.Popen(
        [sys.executable, "server/server.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    time.sleep(3)
    print("      ✓ Central Server started")
    return server_process

def start_hospital(name, port, script):
    print(f"\n[{name}] Starting Hospital {name[-1]}...")
    print(f"      Port: {port}")
    process = subprocess.Popen(
        [sys.executable, script],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    time.sleep(2)
    print(f"      ✓ Hospital {name[-1]} interface started")
    return process

def main():
    print_banner()
    
    processes = []
    
    try:
        # Start central server
        processes.append(start_server())
        
        # Start hospitals
        processes.append(start_hospital("Hospital A", 5001, "run_hospital_a.py"))
        processes.append(start_hospital("Hospital B", 5002, "run_hospital_b.py"))
        processes.append(start_hospital("Hospital C", 5003, "run_hospital_c.py"))
        
        print("\n" + "=" * 70)
        print(" " * 20 + "ALL SERVICES STARTED!")
        print("=" * 70)
        print("\n📊 Open your browser and navigate to:")
        print("\n   Central Server:  http://localhost:8000/docs")
        print("   Hospital A:      http://localhost:5001")
        print("   Hospital B:      http://localhost:5002")
        print("   Hospital C:      http://localhost:5003")
        print("\n💡 Workflow:")
        print("   1. Hospital A: Train → Push to Global")
        print("   2. Hospital B: Download Global → Train → Push to Global")
        print("   3. Hospital C: Download Global → Train → Push to Global")
        print("\n⚠️  Press Ctrl+C to stop all services")
        print("=" * 70)
        
        # Keep script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[INFO] Stopping all services...")
            for process in processes:
                process.terminate()
            print("[INFO] All services stopped. Goodbye!")
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        for process in processes:
            process.terminate()

if __name__ == "__main__":
    main()

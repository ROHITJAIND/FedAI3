"""
Sequential Federated Learning Demo
Hospital A trains -> Updates central model -> Hospital B trains -> Updates central model
"""
import sys
from pathlib import Path
import requests
import time

sys.path.append(str(Path(__file__).parent))

from client.client import LocalClient
from utils.config import FEDERATED_CONFIG


def sequential_federated_learning(num_rounds=5, local_epochs=3):
    """
    Sequential federated learning where hospitals train one after another
    
    Workflow:
    1. Hospital A downloads central model
    2. Hospital A trains on its data
    3. Hospital A uploads weights to central model
    4. Central model updates
    5. Hospital B downloads updated central model
    6. Hospital B trains on its data
    7. Hospital B uploads weights to central model
    8. Central model updates
    9. Repeat for multiple rounds
    """
    print("=" * 70)
    print(" " * 15 + "SEQUENTIAL FEDERATED LEARNING")
    print(" " * 10 + "Hospitals Train One After Another")
    print("=" * 70)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code != 200:
            print("\n[FAIL] Central server is not running!")
            print("Start it with: python server/server.py")
            return
    except:
        print("\n[FAIL] Central server is not running!")
        print("Start it with: python server/server.py")
        return
    
    print(f"\n[OK] Central server is running")
    print(f"[INFO] Configuration:")
    print(f"   Number of Rounds: {num_rounds}")
    print(f"   Local Epochs per Hospital: {local_epochs}")
    
    # Initialize clients
    print(f"\n[*] Initializing Hospital Clients...")
    client_a = LocalClient(hospital_id="A")
    client_b = LocalClient(hospital_id="B")
    client_c = LocalClient(hospital_id="C")
    print(f"[OK] Clients initialized")
    
    # Sequential training rounds
    for round_num in range(1, num_rounds + 1):
        print(f"\n{'='*70}")
        print(f" " * 28 + f"ROUND {round_num}/{num_rounds}")
        print(f"{'='*70}")
        
        # ============ HOSPITAL A ============
        print(f"\n[HOSP] HOSPITAL A - Training Phase")
        print("-" * 70)
        
        # Step 1: Download current central model
        print(f"[DOWN] Hospital A downloading central model...")
        if client_a.download_global_model():
            print(f"[OK] Central model downloaded")
        else:
            print(f"[WARN] Using local model")
        
        # Step 2: Train on Hospital A's data
        print(f"\n[*] Hospital A training on local data ({local_epochs} epochs)...")
        history_a = client_a.train(num_epochs=local_epochs, verbose=False)
        if history_a['loss']:
            print(f"[OK] Training complete")
            print(f"   Final Loss: {history_a['loss'][-1]:.4f}")
            print(f"   Final Accuracy: {history_a['accuracy'][-1]:.2%}")
        
        # Step 3: Upload weights to central model
        print(f"\n[*] Hospital A uploading weights to central model...")
        if client_a.upload_weights_to_server():
            print(f"[OK] Weights uploaded")
        
        # Step 4: Trigger aggregation (update central model)
        print(f"[*] Updating central model with Hospital A's weights...")
        try:
            response = requests.post("http://localhost:8000/aggregate")
            if response.status_code == 200:
                print(f"[OK] Central model updated!")
                data = response.json()
                print(f"   Round: {data.get('round', 'N/A')}")
            else:
                print(f"[FAIL] Aggregation failed: {response.text}")
        except Exception as e:
            print(f"[FAIL] Error triggering aggregation: {e}")
        
        # ============ HOSPITAL B ============
        print(f"\n[HOSP] HOSPITAL B - Training Phase")
        print("-" * 70)
        
        # Step 1: Download updated central model (with Hospital A's knowledge)
        print(f"[DOWN] Hospital B downloading updated central model...")
        if client_b.download_global_model():
            print(f"[OK] Central model downloaded (includes Hospital A's learning)")
        else:
            print(f"[WARN] Using local model")
        
        # Step 2: Train on Hospital B's data
        print(f"\n[*] Hospital B training on local data ({local_epochs} epochs)...")
        history_b = client_b.train(num_epochs=local_epochs, verbose=False)
        if history_b['loss']:
            print(f"[OK] Training complete")
            print(f"   Final Loss: {history_b['loss'][-1]:.4f}")
            print(f"   Final Accuracy: {history_b['accuracy'][-1]:.2%}")
        
        # Step 3: Upload weights to central model
        print(f"\n[*] Hospital B uploading weights to central model...")
        if client_b.upload_weights_to_server():
            print(f"[OK] Weights uploaded")
        
        # Step 4: Trigger aggregation (update central model)
        print(f"[*] Updating central model with Hospital B's weights...")
        try:
            response = requests.post("http://localhost:8000/aggregate")
            if response.status_code == 200:
                print(f"[OK] Central model updated!")
                data = response.json()
                print(f"   Round: {data.get('round', 'N/A')}")
            else:
                print(f"[FAIL] Aggregation failed: {response.text}")
        except Exception as e:
            print(f"[FAIL] Error triggering aggregation: {e}")
        
        # ============ HOSPITAL C ============
        print(f"\n[HOSP] HOSPITAL C - Training Phase")
        print("-" * 70)
        
        # Step 1: Download updated central model (with Hospitals A & B's knowledge)
        print(f"[DOWN] Hospital C downloading updated central model...")
        if client_c.download_global_model():
            print(f"[OK] Central model downloaded (includes Hospitals A & B's learning)")
        else:
            print(f"[WARN] Using local model")
        
        # Step 2: Train on Hospital C's data
        print(f"\n[*] Hospital C training on local data ({local_epochs} epochs)...")
        history_c = client_c.train(num_epochs=local_epochs, verbose=False)
        if history_c['loss']:
            print(f"[OK] Training complete")
            print(f"   Final Loss: {history_c['loss'][-1]:.4f}")
            print(f"   Final Accuracy: {history_c['accuracy'][-1]:.2%}")
        else:
            print(f"[WARN] Training skipped (no data)")
        
        # Step 3: Upload weights to central model
        print(f"\n[*] Hospital C uploading weights to central model...")
        if client_c.upload_weights_to_server():
            print(f"[OK] Weights uploaded")
        
        # Step 4: Trigger aggregation (update central model)
        print(f"[*] Updating central model with Hospital C's weights...")
        try:
            response = requests.post("http://localhost:8000/aggregate")
            if response.status_code == 200:
                print(f"[OK] Central model updated!")
                data = response.json()
                print(f"   Round: {data.get('round', 'N/A')}")
                print(f"   Total updates: {round_num * 3}")
            else:
                print(f"[FAIL] Aggregation failed: {response.text}")
        except Exception as e:
            print(f"[FAIL] Error triggering aggregation: {e}")
        
        # Round summary
        print(f"\n[INFO] Round {round_num} Summary:")
        if history_a.get('loss') and len(history_a['loss']) > 0:
            print(f"   Hospital A contributed: Loss={history_a['loss'][-1]:.4f}, Acc={history_a['accuracy'][-1]:.2%}")
        else:
            print(f"   Hospital A: No training data")
        
        if history_b.get('loss') and len(history_b['loss']) > 0:
            print(f"   Hospital B contributed: Loss={history_b['loss'][-1]:.4f}, Acc={history_b['accuracy'][-1]:.2%}")
        else:
            print(f"   Hospital B: No training data")
        
        if history_c.get('loss') and len(history_c['loss']) > 0:
            print(f"   Hospital C contributed: Loss={history_c['loss'][-1]:.4f}, Acc={history_c['accuracy'][-1]:.2%}")
        else:
            print(f"   Hospital C: No training data")
        
        print(f"   Central model updated this round")
        
        if round_num < num_rounds:
            print(f"\n[PAUSE] Brief pause before next round...")
            time.sleep(2)
    
    # Final summary
    print(f"\n{'='*70}")
    print(" " * 20 + "TRAINING COMPLETE!")
    print(f"{'='*70}")
    print(f"\n[SUCCESS] Sequential federated learning completed!")
    print(f"   Total rounds: {num_rounds}")
    print(f"   Total updates to central model: {num_rounds * 2}")
    print(f"\n[INFO] The central model now contains knowledge from:")
    print(f"   - Hospital A's {num_rounds} training sessions")
    print(f"   - Hospital B's {num_rounds} training sessions")
    print(f"\n[INFO] Both hospitals can now download the final model:")
    print(f"   client_a.download_global_model()")
    print(f"   client_b.download_global_model()")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sequential Federated Learning")
    parser.add_argument(
        '--rounds',
        type=int,
        default=5,
        help='Number of training rounds (default: 5)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help='Local epochs per hospital (default: 3)'
    )
    
    args = parser.parse_args()
    
    sequential_federated_learning(
        num_rounds=args.rounds,
        local_epochs=args.epochs
    )

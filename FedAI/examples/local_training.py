"""
Example: Standalone Local Training
Demonstrates how a single hospital would train their model locally
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from client.client import LocalClient


def main():
    """Run standalone local training example"""
    print("=" * 70)
    print(" " * 20 + "LOCAL TRAINING EXAMPLE")
    print(" " * 18 + "Hospital A - Standalone Mode")
    print("=" * 70)
    
    # Create client for Hospital A
    print("\n[HOSP] Initializing Hospital A Client...")
    client = LocalClient(hospital_id="A")
    
    # Train locally
    print("\n[INFO] Starting local training...")
    print("   (No communication with central server)")
    
    history = client.train(num_epochs=5, verbose=True)
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 23 + "TRAINING COMPLETE!")
    print("=" * 70)
    
    if history['loss']:
        print(f"\n[DATA] Training Summary:")
        print(f"   Initial Loss: {history['loss'][0]:.4f}")
        print(f"   Final Loss: {history['loss'][-1]:.4f}")
        print(f"   Initial Accuracy: {history['accuracy'][0]:.2%}")
        print(f"   Final Accuracy: {history['accuracy'][-1]:.2%}")
        
        # Calculate improvement
        loss_improvement = ((history['loss'][0] - history['loss'][-1]) / history['loss'][0]) * 100
        acc_improvement = (history['accuracy'][-1] - history['accuracy'][0]) * 100
        
        print(f"\n[CHART] Improvement:")
        print(f"   Loss reduced by: {loss_improvement:.1f}%")
        print(f"   Accuracy increased by: {acc_improvement:.1f} percentage points")
    
    print("\n[OK] Model saved successfully!")
    print(f"   Location: {client.model_path}")


if __name__ == "__main__":
    main()

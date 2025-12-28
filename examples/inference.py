"""
Example: Inference Only
Demonstrates how a doctor would use the system for predictions
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from client.client import LocalClient
from utils.config import HOSPITAL_A_DIR


def main():
    """Run inference example"""
    print("=" * 70)
    print(" " * 22 + "INFERENCE EXAMPLE")
    print(" " * 15 + "Doctor's Usage Scenario")
    print("=" * 70)
    
    # Create client
    print("\n[HOSP] Initializing Hospital System...")
    client = LocalClient(hospital_id="A")
    
    # Find available images
    print("\n[SEARCH] Searching for ultrasound images...")
    
    cephalic_images = list((HOSPITAL_A_DIR / "Cephalic").glob("*.jpg"))
    breech_images = list((HOSPITAL_A_DIR / "Breech").glob("*.jpg"))
    transverse_images = list((HOSPITAL_A_DIR / "Transverse").glob("*.jpg"))
    
    all_images = cephalic_images + breech_images + transverse_images
    
    if not all_images:
        print("\n[FAIL] No images found!")
        print("   Please run: python data/prepare_data.py --synthetic")
        return
    
    print(f"   Found {len(all_images)} images")
    
    # Analyze first few images
    num_to_analyze = min(5, len(all_images))
    
    print(f"\n[ANALYZE] Analyzing {num_to_analyze} ultrasound scans...\n")
    
    for i, image_path in enumerate(all_images[:num_to_analyze], 1):
        print(f"\n{'─'*70}")
        print(f"SCAN {i}/{num_to_analyze}")
        print(f"{'─'*70}")
        print(f"[FILE] File: {image_path.name}")
        print(f"[CLASS] Actual Class: {image_path.parent.name}")
        
        # Get prediction
        result = client.predict(str(image_path))
        
        # Display report
        print(result['report'])
        
        # Check if correct
        actual_class = image_path.parent.name
        predicted_class = result['position']
        is_correct = actual_class == predicted_class
        
        if is_correct:
            print("[OK] Prediction: CORRECT")
        else:
            print(f"[FAIL] Prediction: INCORRECT (Expected: {actual_class})")
    
    print("\n" + "=" * 70)
    print(" " * 18 + "ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()

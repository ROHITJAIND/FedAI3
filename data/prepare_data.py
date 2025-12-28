"""
Data Preparation Script - Phase 1
Simulates hospital data by creating sample ultrasound images
This script helps you set up the project when you don't have real data yet
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys
import random

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import HOSPITAL_A_DIR, HOSPITAL_B_DIR, TEST_DIR, CLASS_LABELS


def generate_synthetic_ultrasound(
    width: int = 224,
    height: int = 224,
    class_name: str = "Cephalic"
) -> Image.Image:
    """
    Generate a synthetic ultrasound-like image
    
    This creates a simple grayscale image with text overlay.
    In a real project, you would use actual ultrasound images.
    
    Args:
        width: Image width
        height: Image height
        class_name: Class label (Cephalic, Breech, Transverse)
        
    Returns:
        PIL Image
    """
    # Create base grayscale image with noise
    noise = np.random.randint(20, 80, (height, width), dtype=np.uint8)
    
    # Add some structure (simulating ultrasound patterns)
    for i in range(5):
        center_x = random.randint(50, width - 50)
        center_y = random.randint(50, height - 50)
        radius = random.randint(20, 40)
        
        y, x = np.ogrid[:height, :width]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        noise[mask] = np.clip(noise[mask] + random.randint(30, 70), 0, 255)
    
    # Convert to PIL image
    img = Image.fromarray(noise, mode='L').convert('RGB')
    
    # Add text label (for identification during testing)
    draw = ImageDraw.Draw(img)
    try:
        # Try to use default font
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), class_name, fill=(200, 200, 200), font=font)
    
    return img


def create_dataset_structure():
    """Create the directory structure for the dataset"""
    directories = [
        HOSPITAL_A_DIR / "Cephalic",
        HOSPITAL_A_DIR / "Breech",
        HOSPITAL_A_DIR / "Transverse",
        HOSPITAL_B_DIR / "Cephalic",
        HOSPITAL_B_DIR / "Breech",
        HOSPITAL_B_DIR / "Transverse",
        TEST_DIR / "Cephalic",
        TEST_DIR / "Breech",
        TEST_DIR / "Transverse",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("[OK] Created dataset directory structure")


def generate_synthetic_dataset(
    num_samples_per_class: int = 10,
    num_test_samples: int = 5
):
    """
    Generate a complete synthetic dataset
    
    Args:
        num_samples_per_class: Number of samples per class for each hospital
        num_test_samples: Number of test samples per class
    """
    print("=" * 60)
    print("GENERATING SYNTHETIC DATASET")
    print("=" * 60)
    
    # Create directory structure
    create_dataset_structure()
    
    class_names = list(CLASS_LABELS.values())
    
    # Generate for Hospital A
    print(f"\n[DIR] Generating Hospital A data...")
    for class_name in class_names:
        class_dir = HOSPITAL_A_DIR / class_name
        for i in range(num_samples_per_class):
            img = generate_synthetic_ultrasound(class_name=class_name)
            img.save(class_dir / f"{class_name.lower()}_{i:03d}.jpg")
        print(f"   {class_name}: {num_samples_per_class} images")
    
    # Generate for Hospital B
    print(f"\n[DIR] Generating Hospital B data...")
    for class_name in class_names:
        class_dir = HOSPITAL_B_DIR / class_name
        for i in range(num_samples_per_class):
            img = generate_synthetic_ultrasound(class_name=class_name)
            img.save(class_dir / f"{class_name.lower()}_{i:03d}.jpg")
        print(f"   {class_name}: {num_samples_per_class} images")
    
    # Generate test set
    print(f"\n[DIR] Generating Test Set data...")
    for class_name in class_names:
        class_dir = TEST_DIR / class_name
        for i in range(num_test_samples):
            img = generate_synthetic_ultrasound(class_name=class_name)
            img.save(class_dir / f"{class_name.lower()}_test_{i:03d}.jpg")
        print(f"   {class_name}: {num_test_samples} images")
    
    print("\n" + "=" * 60)
    print("[OK] SYNTHETIC DATASET GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nDataset Summary:")
    print(f"  Hospital A: {num_samples_per_class * 3} images ({num_samples_per_class} per class)")
    print(f"  Hospital B: {num_samples_per_class * 3} images ({num_samples_per_class} per class)")
    print(f"  Test Set:   {num_test_samples * 3} images ({num_test_samples} per class)")
    print(f"\n[WARN]  NOTE: These are synthetic images for testing only.")
    print(f"   Replace with real ultrasound images for actual use.")


def download_instructions():
    """Print instructions for downloading real datasets"""
    print("\n" + "=" * 60)
    print("USING REAL ULTRASOUND DATASETS")
    print("=" * 60)
    print("\nTo use real fetal ultrasound data, you can:")
    print("\n1. Kaggle Datasets:")
    print("   - Search for 'fetal ultrasound' on Kaggle")
    print("   - Example: 'Fetal Planes Dataset'")
    print("   - Download and organize into class folders")
    print("\n2. Medical Imaging Repositories:")
    print("   - Zenodo (zenodo.org)")
    print("   - IEEE DataPort")
    print("   - Grand Challenge (grand-challenge.org)")
    print("\n3. Directory Structure:")
    print("   data/Hospital_A/")
    print("   ├── Cephalic/")
    print("   │   ├── image001.jpg")
    print("   │   └── ...")
    print("   ├── Breech/")
    print("   │   └── ...")
    print("   └── Transverse/")
    print("       └── ...")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Prepare data for FetalScanFL")
    parser.add_argument(
        '--synthetic',
        action='store_true',
        help='Generate synthetic dataset for testing'
    )
    parser.add_argument(
        '--num-samples',
        type=int,
        default=20,
        help='Number of samples per class for each hospital (default: 20)'
    )
    parser.add_argument(
        '--num-test',
        type=int,
        default=10,
        help='Number of test samples per class (default: 10)'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show information about using real datasets'
    )
    
    args = parser.parse_args()
    
    if args.info:
        download_instructions()
    elif args.synthetic:
        generate_synthetic_dataset(
            num_samples_per_class=args.num_samples,
            num_test_samples=args.num_test
        )
    else:
        print("Use --synthetic to generate synthetic data, or --info for real dataset instructions")
        print("Example: python prepare_data.py --synthetic --num-samples 30")

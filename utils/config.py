"""
Configuration settings for FetalScanFL
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data configuration
DATA_DIR = PROJECT_ROOT / "data"
HOSPITAL_A_DIR = DATA_DIR / "Hospital_A"
HOSPITAL_B_DIR = DATA_DIR / "Hospital_B"
TEST_DIR = DATA_DIR / "Test_Set"

# Model configuration
MODEL_CONFIG = {
    "input_size": (224, 224),  # Standard ResNet input size
    "num_classes": 3,  # Cephalic, Breech, Transverse
    "pretrained": True,  # Use pretrained ResNet weights
    "architecture": "resnet18",  # Options: resnet18, resnet34, resnet50
}

# Class labels
CLASS_LABELS = {
    0: "Cephalic",   # Head Down - Normal
    1: "Breech",     # Head Up - Requires attention
    2: "Transverse"  # Sideways - Requires attention
}

# Training configuration
TRAINING_CONFIG = {
    "batch_size": 16,
    "learning_rate": 0.001,
    "num_epochs": 10,
    "momentum": 0.9,
    "weight_decay": 0.0001,
}

# Federated Learning configuration
FEDERATED_CONFIG = {
    "num_rounds": 20,  # Number of federated learning rounds
    "clients_per_round": 2,  # Number of clients participating per round
    "local_epochs": 5,  # Number of local training epochs per round
}

# Server configuration
SERVER_CONFIG = {
    "host": "localhost",
    "port": 8000,
    "model_save_path": PROJECT_ROOT / "checkpoints" / "global_model.pth",
}

# Client configuration
CLIENT_CONFIG = {
    "server_url": "http://localhost:8000",
    "model_save_path": PROJECT_ROOT / "checkpoints",
}

# Image preprocessing
IMAGE_PREPROCESSING = {
    "mean": [0.485, 0.456, 0.406],  # ImageNet mean
    "std": [0.229, 0.224, 0.225],   # ImageNet std
    "normalize": True,
}

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    dirs = [
        DATA_DIR,
        HOSPITAL_A_DIR,
        HOSPITAL_B_DIR,
        TEST_DIR,
        PROJECT_ROOT / "checkpoints",
        PROJECT_ROOT / "logs",
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    create_directories()
    print("[OK] All directories created successfully!")

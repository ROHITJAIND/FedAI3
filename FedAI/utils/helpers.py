"""
Helper utility functions for FetalScanFL
"""
import torch
import numpy as np
from PIL import Image
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import matplotlib.pyplot as plt


def save_model(model: torch.nn.Module, path: Path, metadata: Dict[str, Any] = None):
    """
    Save model with metadata
    
    Args:
        model: PyTorch model to save
        path: Path to save the model
        metadata: Additional metadata to save with the model
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    save_dict = {
        'model_state_dict': model.state_dict(),
        'timestamp': datetime.now().isoformat(),
    }
    
    if metadata:
        save_dict.update(metadata)
    
    torch.save(save_dict, path)
    print(f"[OK] Model saved to {path}")


def load_model(model: torch.nn.Module, path: Path) -> torch.nn.Module:
    """
    Load model from checkpoint
    
    Args:
        model: Model instance to load weights into
        path: Path to the checkpoint file
        
    Returns:
        Model with loaded weights
    """
    if not path.exists():
        print(f"[WARN]  No checkpoint found at {path}")
        return model
    
    checkpoint = torch.load(path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    print(f"[OK] Model loaded from {path}")
    
    if 'timestamp' in checkpoint:
        print(f"   Checkpoint timestamp: {checkpoint['timestamp']}")
    
    return model


def preprocess_image(image_path: Path, target_size: tuple = (224, 224)) -> torch.Tensor:
    """
    Preprocess ultrasound image for model input
    
    Args:
        image_path: Path to the image file
        target_size: Target size (height, width)
        
    Returns:
        Preprocessed image tensor
    """
    # Load image
    img = Image.open(image_path).convert('RGB')
    
    # Resize
    img = img.resize(target_size, Image.BILINEAR)
    
    # Convert to numpy array
    img_array = np.array(img) / 255.0
    
    # Normalize (ImageNet statistics)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img_array = (img_array - mean) / std
    
    # Convert to tensor and add batch dimension
    img_tensor = torch.FloatTensor(img_array).permute(2, 0, 1).unsqueeze(0)
    
    return img_tensor


def generate_report(prediction: int, confidence: float, class_labels: Dict[int, str]) -> str:
    """
    Generate a medical report from prediction
    
    Args:
        prediction: Predicted class index
        confidence: Confidence score (0-1)
        class_labels: Dictionary mapping class indices to labels
        
    Returns:
        Formatted report string
    """
    position = class_labels[prediction]
    confidence_pct = confidence * 100
    
    # Determine if attention is required
    attention_required = position in ["Breech", "Transverse"]
    
    report = f"""
╔══════════════════════════════════════════════════════════╗
║           FETAL ULTRASOUND ANALYSIS REPORT              ║
╠══════════════════════════════════════════════════════════╣
║ Position:        {position:<40} ║
║ Confidence:      {confidence_pct:>5.1f}%                                 ║
║ Status:          {'[WARN]  REQUIRES ATTENTION' if attention_required else '[OK] NORMAL':<40} ║
║ Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<40} ║
╚══════════════════════════════════════════════════════════╝
    """
    
    return report


def calculate_accuracy(predictions: List[int], targets: List[int]) -> float:
    """
    Calculate classification accuracy
    
    Args:
        predictions: List of predicted class indices
        targets: List of true class indices
        
    Returns:
        Accuracy score (0-1)
    """
    correct = sum(p == t for p, t in zip(predictions, targets))
    return correct / len(targets) if len(targets) > 0 else 0.0


def log_training_progress(epoch: int, loss: float, accuracy: float, log_file: Path = None):
    """
    Log training progress to console and file
    
    Args:
        epoch: Current epoch number
        loss: Training loss
        accuracy: Training accuracy
        log_file: Optional path to log file
    """
    message = f"Epoch {epoch:3d} | Loss: {loss:.4f} | Accuracy: {accuracy:.2%}"
    print(message)
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")


def plot_training_history(history: Dict[str, List[float]], save_path: Path = None):
    """
    Plot training history (loss and accuracy)
    
    Args:
        history: Dictionary with 'loss' and 'accuracy' keys
        save_path: Optional path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot loss
    ax1.plot(history['loss'])
    ax1.set_title('Training Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.grid(True)
    
    # Plot accuracy
    ax2.plot(history['accuracy'])
    ax2.set_title('Training Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path)
        print(f"[OK] Training history plot saved to {save_path}")
    
    plt.close()


def federated_average(weights_list: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    """
    Perform Federated Averaging (FedAvg) on a list of model weights
    
    Args:
        weights_list: List of state dictionaries from different clients
        
    Returns:
        Averaged state dictionary
    """
    if not weights_list:
        raise ValueError("Cannot average empty list of weights")
    
    # Initialize with zeros
    avg_weights = {}
    for key in weights_list[0].keys():
        avg_weights[key] = torch.zeros_like(weights_list[0][key])
    
    # Sum all weights
    for weights in weights_list:
        for key in weights.keys():
            avg_weights[key] += weights[key]
    
    # Average
    num_clients = len(weights_list)
    for key in avg_weights.keys():
        avg_weights[key] = avg_weights[key] / num_clients
    
    print(f"[OK] Averaged weights from {num_clients} clients")
    return avg_weights


def count_parameters(model: torch.nn.Module) -> int:
    """
    Count the number of trainable parameters in a model
    
    Args:
        model: PyTorch model
        
    Returns:
        Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_device() -> torch.device:
    """
    Get the available device (CUDA if available, else CPU)
    
    Returns:
        torch.device object
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[SYS]  Using device: {device}")
    return device

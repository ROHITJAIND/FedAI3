"""
Core CNN Model for Fetal Position Classification
Phase 2: The Brain of the FetalScanFL Project
"""
import torch
import torch.nn as nn
from torchvision import models
from typing import Tuple


class FetalPositionCNN(nn.Module):
    """
    CNN for classifying fetal position from ultrasound images.
    
    Uses ResNet architecture with custom classification head.
    
    Output Classes:
        0 - Cephalic (Head Down - Normal)
        1 - Breech (Head Up - Requires attention)
        2 - Transverse (Sideways - Requires attention)
    """
    
    def __init__(
        self, 
        num_classes: int = 3, 
        architecture: str = 'resnet18', 
        pretrained: bool = True
    ):
        """
        Initialize the Fetal Position CNN
        
        Args:
            num_classes: Number of output classes (default: 3)
            architecture: ResNet variant ('resnet18', 'resnet34', 'resnet50')
            pretrained: Whether to use ImageNet pretrained weights
        """
        super(FetalPositionCNN, self).__init__()
        
        self.num_classes = num_classes
        self.architecture = architecture
        
        # Load the base ResNet model
        if architecture == 'resnet18':
            self.backbone = models.resnet18(pretrained=pretrained)
            num_features = 512
        elif architecture == 'resnet34':
            self.backbone = models.resnet34(pretrained=pretrained)
            num_features = 512
        elif architecture == 'resnet50':
            self.backbone = models.resnet50(pretrained=pretrained)
            num_features = 2048
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
        
        # Replace the final fully connected layer
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network
        
        Args:
            x: Input tensor of shape (batch_size, 3, 224, 224)
            
        Returns:
            Logits of shape (batch_size, num_classes)
        """
        return self.backbone(x)
    
    def predict(self, x: torch.Tensor) -> Tuple[int, float]:
        """
        Make a prediction on a single image
        
        Args:
            x: Input tensor of shape (1, 3, 224, 224)
            
        Returns:
            Tuple of (predicted_class, confidence)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=1)
            confidence, prediction = torch.max(probabilities, dim=1)
            
        return prediction.item(), confidence.item()
    
    def get_probabilities(self, x: torch.Tensor) -> torch.Tensor:
        """
        Get probability distribution over all classes
        
        Args:
            x: Input tensor of shape (batch_size, 3, 224, 224)
            
        Returns:
            Probability tensor of shape (batch_size, num_classes)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=1)
            
        return probabilities


def create_model(
    num_classes: int = 3,
    architecture: str = 'resnet18',
    pretrained: bool = True,
    device: torch.device = None
) -> FetalPositionCNN:
    """
    Factory function to create and initialize the model
    
    Args:
        num_classes: Number of output classes
        architecture: ResNet variant
        pretrained: Whether to use pretrained weights
        device: Device to place the model on
        
    Returns:
        Initialized FetalPositionCNN model
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = FetalPositionCNN(
        num_classes=num_classes,
        architecture=architecture,
        pretrained=pretrained
    )
    
    model = model.to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"[OK] Created {architecture} model")
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")
    print(f"   Device: {device}")
    
    return model


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("FETAL POSITION CNN - MODEL TEST")
    print("=" * 60)
    
    # Create model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = create_model(num_classes=3, architecture='resnet18', device=device)
    
    # Create dummy input (simulating an ultrasound image)
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    
    # Test forward pass
    print("\n[TEST] Testing forward pass...")
    logits = model(dummy_input)
    print(f"   Output shape: {logits.shape}")
    print(f"   Logits: {logits}")
    
    # Test prediction
    print("\n[TEST] Testing prediction...")
    prediction, confidence = model.predict(dummy_input)
    
    class_names = {0: "Cephalic", 1: "Breech", 2: "Transverse"}
    print(f"   Predicted class: {prediction} ({class_names[prediction]})")
    print(f"   Confidence: {confidence:.2%}")
    
    # Test probability distribution
    print("\n[TEST] Testing probability distribution...")
    probs = model.get_probabilities(dummy_input)
    for i, prob in enumerate(probs[0]):
        print(f"   {class_names[i]:12s}: {prob:.2%}")
    
    print("\n" + "=" * 60)
    print("[OK] MODEL TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)

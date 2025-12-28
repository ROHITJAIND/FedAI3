"""
Core Neural Network Model for Medical Patient Classification
Text-based model for fetal position prediction
"""
import torch
import torch.nn as nn
from typing import Tuple, Optional


class MedicalTextClassifier(nn.Module):
    """
    Neural Network for classifying patient data from medical records.
    
    Uses a feedforward neural network with attention mechanism for tabular data.
    
    Output Classes:
        Dynamically determined from data (e.g., Cephalic, Breech, Transverse, Not Fixed)
    """
    
    def __init__(
        self, 
        input_dim: int = 3,
        num_classes: int = 4,
        hidden_dims: list = [128, 64, 32],
        dropout: float = 0.3
    ):
        """
        Initialize the Medical Text Classifier
        
        Args:
            input_dim: Number of input features
            num_classes: Number of output classes
            hidden_dims: List of hidden layer dimensions
            dropout: Dropout probability
        """
        super(MedicalTextClassifier, self).__init__()
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.hidden_dims = hidden_dims
        
        # Build the network layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, num_classes))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize network weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            
        Returns:
            Logits of shape (batch_size, num_classes)
        """
        return self.network(x)
    
    def predict(self, x: torch.Tensor) -> Tuple[int, float]:
        """
        Make a prediction on a single sample
        
        Args:
            x: Input tensor of shape (1, input_dim) or (input_dim,)
            
        Returns:
            Tuple of (predicted_class, confidence)
        """
        self.eval()
        with torch.no_grad():
            if x.dim() == 1:
                x = x.unsqueeze(0)
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=1)
            confidence, prediction = torch.max(probabilities, dim=1)
            
        return prediction.item(), confidence.item()
    
    def get_probabilities(self, x: torch.Tensor) -> torch.Tensor:
        """
        Get probability distribution over all classes
        
        Args:
            x: Input tensor of shape (batch_size, input_dim)
            
        Returns:
            Probability distribution of shape (batch_size, num_classes)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = torch.softmax(logits, dim=1)
        return probabilities
    
    def get_model_size(self) -> int:
        """
        Get the number of parameters in the model
        
        Returns:
            Number of trainable parameters
        """
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


# Backward compatibility alias
FetalPositionCNN = MedicalTextClassifier


def create_model(
    input_dim: int = 3,
    num_classes: int = 4,
    hidden_dims: list = None,
    dropout: float = 0.3
) -> MedicalTextClassifier:
    """
    Factory function to create a model
    
    Args:
        input_dim: Number of input features
        num_classes: Number of output classes
        hidden_dims: List of hidden layer dimensions
        dropout: Dropout probability
        
    Returns:
        Initialized model
    """
    if hidden_dims is None:
        hidden_dims = [128, 64, 32]
    
    model = MedicalTextClassifier(
        input_dim=input_dim,
        num_classes=num_classes,
        hidden_dims=hidden_dims,
        dropout=dropout
    )
    
    print(f"[MODEL] Created Medical Text Classifier")
    print(f"   Input dim: {input_dim}")
    print(f"   Output classes: {num_classes}")
    print(f"   Hidden layers: {hidden_dims}")
    print(f"   Total parameters: {model.get_model_size():,}")
    
    return model


if __name__ == "__main__":
    print("=" * 60)
    print("MEDICAL TEXT CLASSIFIER - TEST")
    print("=" * 60)
    
    # Test model creation
    model = create_model(input_dim=3, num_classes=4)
    
    # Test forward pass
    print("\n[TEST] Testing forward pass...")
    batch_size = 8
    dummy_input = torch.randn(batch_size, 3)
    output = model(dummy_input)
    
    print(f"   Input shape: {dummy_input.shape}")
    print(f"   Output shape: {output.shape}")
    
    # Test prediction
    print("\n[TEST] Testing prediction...")
    single_input = torch.randn(3)
    pred_class, confidence = model.predict(single_input)
    print(f"   Predicted class: {pred_class}")
    print(f"   Confidence: {confidence:.4f}")
    
    print("\n" + "=" * 60)
    
    print("\n" + "=" * 60)
    print("[OK] MODEL TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)

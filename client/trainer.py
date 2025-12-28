"""
Local Training Logic for Hospital Clients
Handles the training loop for local model updates
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.model import MedicalTextClassifier
from utils.helpers import log_training_progress


class LocalTrainer:
    """
    Handles local training for a hospital client
    """
    
    def __init__(
        self,
        model: MedicalTextClassifier,
        device: torch.device,
        learning_rate: float = 0.001,
        momentum: float = 0.9,
        weight_decay: float = 0.0001
    ):
        """
        Initialize the local trainer
        
        Args:
            model: The neural network model
            device: Device to train on (CPU or CUDA)
            learning_rate: Learning rate for optimization
            momentum: Momentum for SGD optimizer
            weight_decay: Weight decay (L2 regularization)
        """
        self.model = model
        self.device = device
        
        # Move model to device
        self.model = self.model.to(self.device)
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Optimizer
        self.optimizer = optim.SGD(
            self.model.parameters(),
            lr=learning_rate,
            momentum=momentum,
            weight_decay=weight_decay
        )
        
        # Training history
        self.history = {
            'loss': [],
            'accuracy': []
        }
    
    def train_epoch(self, dataloader: DataLoader) -> Tuple[float, float]:
        """
        Train for one epoch
        
        Args:
            dataloader: DataLoader for training data
            
        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.train()
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, batch_data in enumerate(dataloader):
            # Handle both (features, labels) and (features, labels, text) formats
            if len(batch_data) == 3:
                features, labels, _ = batch_data  # Ignore text for now
            else:
                features, labels = batch_data
            
            # Move data to device
            features = features.to(self.device)
            labels = labels.to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(features)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        # Calculate averages
        avg_loss = running_loss / len(dataloader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def train(
        self,
        dataloader: DataLoader,
        num_epochs: int,
        log_file: Path = None,
        verbose: bool = True
    ) -> Dict[str, List[float]]:
        """
        Train the model for multiple epochs
        
        Args:
            dataloader: DataLoader for training data
            num_epochs: Number of epochs to train
            log_file: Optional path to log file
            verbose: Whether to print progress
            
        Returns:
            Training history dictionary
        """
        if verbose:
            print(f"\n[START] Starting local training for {num_epochs} epochs...")
        
        for epoch in range(1, num_epochs + 1):
            # Train one epoch
            loss, accuracy = self.train_epoch(dataloader)
            
            # Save history
            self.history['loss'].append(loss)
            self.history['accuracy'].append(accuracy)
            
            # Log progress
            if verbose:
                log_training_progress(epoch, loss, accuracy, log_file)
        
        if verbose:
            print(f"[OK] Training completed!")
            print(f"   Final Loss: {loss:.4f}")
            print(f"   Final Accuracy: {accuracy:.2%}")
        
        return self.history
    
    def evaluate(self, dataloader: DataLoader) -> Tuple[float, float]:
        """
        Evaluate the model on a dataset
        
        Args:
            dataloader: DataLoader for evaluation data
            
        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.eval()
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_data in dataloader:
                # Handle both (features, labels) and (features, labels, text) formats
                if len(batch_data) == 3:
                    features, labels, _ = batch_data  # Ignore text for now
                else:
                    features, labels = batch_data
                
                # Move data to device
                features = features.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(features)
                loss = self.criterion(outputs, labels)
                
                # Statistics
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        # Calculate averages
        avg_loss = running_loss / len(dataloader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def get_model_weights(self) -> Dict[str, torch.Tensor]:
        """
        Get current model weights (for federated aggregation)
        
        Returns:
            State dictionary of model weights
        """
        return {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
    
    def set_model_weights(self, weights: Dict[str, torch.Tensor]):
        """
        Set model weights (from federated aggregation)
        
        Args:
            weights: State dictionary of model weights
        """
        # Use strict=False to ignore missing keys (like num_batches_tracked)
        self.model.load_state_dict(weights, strict=False)
        self.model = self.model.to(self.device)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("LOCAL TRAINER - TEST")
    print("=" * 60)
    
    from models.model import create_model
    from data.data_loader import create_dataloaders
    from utils.config import HOSPITAL_A_DIR, TEST_DIR
    from utils.helpers import get_device
    
    # Setup
    device = get_device()
    model = create_model(num_classes=3, architecture='resnet18', device=device)
    
    # Create trainer
    trainer = LocalTrainer(model, device)
    
    print("\n[OK] Local Trainer initialized successfully!")
    print("   Ready for training...")

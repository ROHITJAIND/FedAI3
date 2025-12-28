"""
Federated Averaging (FedAvg) Algorithm
Aggregates model weights from multiple clients
"""
import torch
from typing import List, Dict
import numpy as np


class FederatedAggregator:
    """
    Implements the FedAvg algorithm for federated learning
    
    The FedAvg algorithm:
    1. Receives weights from multiple clients
    2. Averages them element-wise
    3. Returns the global model
    """
    
    def __init__(self):
        """Initialize the aggregator"""
        self.client_weights = {}
        self.global_weights = None
        self.round = 0
    
    def add_client_weights(self, client_id: str, weights: Dict[str, torch.Tensor]):
        """
        Add weights from a client
        
        Args:
            client_id: Identifier for the client
            weights: Model weights from the client
        """
        self.client_weights[client_id] = weights
        print(f"[OK] Received weights from client: {client_id}")
    
    def aggregate(self) -> Dict[str, torch.Tensor]:
        """
        Aggregate weights from all clients using FedAvg
        
        Returns:
            Aggregated global weights
        """
        if not self.client_weights:
            raise ValueError("No client weights to aggregate")
        
        print(f"\n[*] Aggregating weights from {len(self.client_weights)} clients...")
        
        # Get list of all client weights
        weights_list = list(self.client_weights.values())
        
        # Initialize global weights with zeros
        self.global_weights = {}
        for key in weights_list[0].keys():
            self.global_weights[key] = torch.zeros_like(weights_list[0][key])
        
        # Sum all weights
        for weights in weights_list:
            for key in weights.keys():
                self.global_weights[key] += weights[key]
        
        # Average (divide by number of clients)
        num_clients = len(weights_list)
        for key in self.global_weights.keys():
            self.global_weights[key] = self.global_weights[key] / num_clients
        
        print(f"[OK] Aggregation complete!")
        print(f"   Number of clients: {num_clients}")
        print(f"   Number of parameters: {len(self.global_weights)}")
        
        # Increment round
        self.round += 1
        
        return self.global_weights
    
    def clear_client_weights(self):
        """Clear stored client weights after aggregation"""
        self.client_weights = {}
        print(f"[CLEAN] Cleared client weights for next round")
    
    def get_global_weights(self) -> Dict[str, torch.Tensor]:
        """
        Get the current global weights
        
        Returns:
            Global model weights
        """
        if self.global_weights is None:
            raise ValueError("No global weights available. Run aggregate() first.")
        
        return self.global_weights
    
    def save_global_model(self, path: str):
        """
        Save the global model to disk
        
        Args:
            path: Path to save the model
        """
        if self.global_weights is None:
            raise ValueError("No global weights to save")
        
        torch.save({
            'weights': self.global_weights,
            'round': self.round,
            'num_clients': len(self.client_weights)
        }, path)
        
        print(f"[OK] Global model saved to {path}")
    
    def load_global_model(self, path: str):
        """
        Load global model from disk
        
        Args:
            path: Path to the saved model
        """
        checkpoint = torch.load(path, map_location='cpu')
        self.global_weights = checkpoint['weights']
        self.round = checkpoint.get('round', 0)
        
        print(f"[OK] Global model loaded from {path}")
        print(f"   Round: {self.round}")


def federated_average(weights_list: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    """
    Standalone function to perform federated averaging
    
    Args:
        weights_list: List of weight dictionaries from different clients
        
    Returns:
        Averaged weight dictionary
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
    
    return avg_weights


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("FEDERATED AGGREGATOR - TEST")
    print("=" * 60)
    
    # Create aggregator
    aggregator = FederatedAggregator()
    
    # Simulate client weights (using small tensors for demo)
    client_a_weights = {
        'layer1': torch.tensor([1.0, 2.0, 3.0]),
        'layer2': torch.tensor([4.0, 5.0, 6.0])
    }
    
    client_b_weights = {
        'layer1': torch.tensor([2.0, 3.0, 4.0]),
        'layer2': torch.tensor([5.0, 6.0, 7.0])
    }
    
    # Add client weights
    aggregator.add_client_weights('Hospital_A', client_a_weights)
    aggregator.add_client_weights('Hospital_B', client_b_weights)
    
    # Aggregate
    global_weights = aggregator.aggregate()
    
    print(f"\n[DATA] Aggregated Weights:")
    for key, value in global_weights.items():
        print(f"   {key}: {value}")
    
    # Expected results:
    # layer1: [1.5, 2.5, 3.5] (average of [1,2,3] and [2,3,4])
    # layer2: [4.5, 5.5, 6.5] (average of [4,5,6] and [5,6,7])
    
    print("\n[OK] Aggregation test completed successfully!")

"""
Local Hospital Client - Phase 3
This is the software that doctors see and use for inference and training
"""
import torch
from pathlib import Path
import sys
import requests
from typing import Dict, Tuple
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.model import create_model, FetalPositionCNN
from data.data_loader import create_dataloaders
from client.trainer import LocalTrainer
from utils.config import (
    CLASS_LABELS, 
    MODEL_CONFIG, 
    TRAINING_CONFIG,
    CLIENT_CONFIG,
    HOSPITAL_A_DIR,
    HOSPITAL_B_DIR,
    TEST_DIR
)
from utils.helpers import (
    preprocess_image,
    generate_report,
    save_model,
    load_model,
    get_device
)


class LocalClient:
    """
    Local Hospital Client System
    
    This represents the software running at each hospital/clinic.
    It handles:
    1. Inference - Generating reports for doctors
    2. Training - Learning from new scans
    3. Federation - Communicating with central server
    """
    
    def __init__(
        self,
        hospital_id: str,
        data_dir: Path = None,
        server_url: str = None
    ):
        """
        Initialize the local client
        
        Args:
            hospital_id: Identifier for this hospital (e.g., "A", "B")
            data_dir: Path to local data directory
            server_url: URL of the central federated server
        """
        self.hospital_id = hospital_id
        self.server_url = server_url or CLIENT_CONFIG['server_url']
        
        # Set data directory based on hospital ID
        if data_dir is None:
            if hospital_id == "A":
                self.data_dir = HOSPITAL_A_DIR
            elif hospital_id == "B":
                self.data_dir = HOSPITAL_B_DIR
            else:
                self.data_dir = Path(f"data/Hospital_{hospital_id}")
        else:
            self.data_dir = Path(data_dir)
        
        # Setup device
        self.device = get_device()
        
        # Initialize model
        self.model = create_model(
            num_classes=MODEL_CONFIG['num_classes'],
            architecture=MODEL_CONFIG['architecture'],
            pretrained=MODEL_CONFIG['pretrained'],
            device=self.device
        )
        
        # Model save path
        self.model_path = CLIENT_CONFIG['model_save_path'] / f"hospital_{hospital_id}_model.pth"
        
        # Load model if exists
        if self.model_path.exists():
            self.model = load_model(self.model, self.model_path)
        
        # Initialize trainer
        self.trainer = LocalTrainer(
            model=self.model,
            device=self.device,
            learning_rate=TRAINING_CONFIG['learning_rate'],
            momentum=TRAINING_CONFIG['momentum'],
            weight_decay=TRAINING_CONFIG['weight_decay']
        )
        
        print(f"\n[OK] Hospital {hospital_id} Client Initialized")
        print(f"   Data directory: {self.data_dir}")
        print(f"   Server URL: {self.server_url}")
    
    def predict(self, image_path: str) -> Dict[str, any]:
        """
        Generate a prediction report for a single ultrasound image
        
        This is what the doctor sees when they upload a scan.
        
        Args:
            image_path: Path to the ultrasound image
            
        Returns:
            Dictionary containing prediction results
        """
        # Preprocess image
        image_tensor = preprocess_image(Path(image_path))
        image_tensor = image_tensor.to(self.device)
        
        # Get prediction
        prediction, confidence = self.model.predict(image_tensor)
        
        # Get probability distribution
        probabilities = self.model.get_probabilities(image_tensor)
        
        # Generate report
        report = generate_report(prediction, confidence, CLASS_LABELS)
        
        # Prepare results
        results = {
            'hospital_id': self.hospital_id,
            'position': CLASS_LABELS[prediction],
            'position_code': prediction,
            'confidence': confidence,
            'probabilities': {
                CLASS_LABELS[i]: prob.item() 
                for i, prob in enumerate(probabilities[0])
            },
            'report': report
        }
        
        return results
    
    def train(
        self,
        num_epochs: int = None,
        batch_size: int = None,
        verbose: bool = True
    ) -> Dict[str, list]:
        """
        Train the local model on hospital data
        
        This happens at night or during idle time.
        
        Args:
            num_epochs: Number of training epochs (default from config)
            batch_size: Batch size (default from config)
            verbose: Whether to print training progress
            
        Returns:
            Training history
        """
        if num_epochs is None:
            num_epochs = TRAINING_CONFIG['num_epochs']
        if batch_size is None:
            batch_size = TRAINING_CONFIG['batch_size']
        
        print(f"\n[HOSP] Hospital {self.hospital_id} - Starting Local Training")
        print(f"   Epochs: {num_epochs}")
        print(f"   Batch Size: {batch_size}")
        
        # Create dataloaders
        train_loader, test_loader = create_dataloaders(
            train_dir=self.data_dir,
            test_dir=TEST_DIR,
            batch_size=batch_size,
            num_workers=0,
            img_size=MODEL_CONFIG['input_size'][0]
        )
        
        if len(train_loader.dataset) == 0:
            print(f"[WARN]  No training data found in {self.data_dir}")
            print(f"   Skipping training for Hospital {self.hospital_id}")
            return {'loss': [], 'accuracy': []}
        
        # Train
        history = self.trainer.train(
            dataloader=train_loader,
            num_epochs=num_epochs,
            verbose=verbose
        )
        
        # Evaluate on test set if available
        if test_loader is not None and len(test_loader.dataset) > 0:
            test_loss, test_accuracy = self.trainer.evaluate(test_loader)
            print(f"\n[DATA] Test Set Performance:")
            print(f"   Loss: {test_loss:.4f}")
            print(f"   Accuracy: {test_accuracy:.2%}")
        
        # Save model
        save_model(self.model, self.model_path, {
            'hospital_id': self.hospital_id,
            'epochs': num_epochs,
            'final_loss': history['loss'][-1] if history['loss'] else 0,
            'final_accuracy': history['accuracy'][-1] if history['accuracy'] else 0
        })
        
        return history
    
    def upload_weights_to_server(self) -> bool:
        """
        Upload local model weights to the central server
        
        This is the "Push" step in federated learning.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get model weights
            weights = self.trainer.get_model_weights()
            
            # Convert to serializable format
            # Filter out 'num_batches_tracked' - these are counters, not trainable params
            weights_serialized = {
                k: v.numpy().tolist() 
                for k, v in weights.items()
                if 'num_batches_tracked' not in k
            }
            
            # Send to server
            response = requests.post(
                f"{self.server_url}/upload_weights",
                json={
                    'hospital_id': self.hospital_id,
                    'weights': weights_serialized
                }
            )
            
            if response.status_code == 200:
                print(f"[OK] Weights uploaded to server successfully")
                return True
            else:
                print(f"[FAIL] Failed to upload weights: {response.text}")
                return False
                
        except Exception as e:
            print(f"[FAIL] Error uploading weights: {e}")
            return False
    
    def download_global_model(self) -> bool:
        """
        Download the global model from the central server
        
        This is the "Pull" step in federated learning.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Request global model
            response = requests.get(f"{self.server_url}/global_model")
            
            if response.status_code == 200:
                # Parse weights
                data = response.json()
                weights = {
                    k: torch.tensor(v) 
                    for k, v in data['weights'].items()
                }
                
                # Update local model
                self.trainer.set_model_weights(weights)
                
                print(f"[OK] Global model downloaded successfully")
                print(f"   Round: {data.get('round', 'N/A')}")
                
                # Save updated model
                save_model(self.model, self.model_path, {
                    'hospital_id': self.hospital_id,
                    'source': 'global_model',
                    'round': data.get('round', 0)
                })
                
                return True
            else:
                print(f"[FAIL] Failed to download global model: {response.text}")
                return False
                
        except Exception as e:
            print(f"[FAIL] Error downloading global model: {e}")
            return False
    
    def federated_round(self, num_local_epochs: int = 5) -> bool:
        """
        Execute one complete federated learning round
        
        1. Train locally
        2. Upload weights to server
        3. Download updated global model
        
        Args:
            num_local_epochs: Number of local training epochs
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"FEDERATED LEARNING ROUND - Hospital {self.hospital_id}")
        print(f"{'='*60}")
        
        # Step 1: Local training
        print(f"\n[INFO] Step 1: Local Training")
        self.train(num_epochs=num_local_epochs, verbose=True)
        
        # Step 2: Upload weights
        print(f"\n[CLOUD]  Step 2: Upload Weights")
        upload_success = self.upload_weights_to_server()
        
        if not upload_success:
            print(f"[WARN]  Skipping global model download due to upload failure")
            return False
        
        # Step 3: Download global model
        print(f"\n[DOWN]  Step 3: Download Global Model")
        download_success = self.download_global_model()
        
        print(f"\n{'='*60}")
        if download_success:
            print(f"[OK] FEDERATED ROUND COMPLETED SUCCESSFULLY")
        else:
            print(f"[WARN]  FEDERATED ROUND COMPLETED WITH WARNINGS")
        print(f"{'='*60}\n")
        
        return download_success


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("LOCAL CLIENT - DEMO")
    print("=" * 60)
    
    # Create client for Hospital A
    client = LocalClient(hospital_id="A")
    
    print("\n📋 Client created successfully!")
    print("\nAvailable methods:")
    print("  - client.predict(image_path)  # Generate report")
    print("  - client.train()               # Train locally")
    print("  - client.federated_round()     # Complete FL round")

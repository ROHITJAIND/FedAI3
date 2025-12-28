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
        excel_path: str = "data/patient_data.xlsx",
        server_url: str = None
    ):
        """
        Initialize the local client
        
        Args:
            hospital_id: Identifier for this hospital (e.g., "A", "B", "C")
            excel_path: Path to Excel file containing patient data
            server_url: URL of the central federated server
        """
        self.hospital_id = hospital_id
        self.server_url = server_url or CLIENT_CONFIG['server_url']
        self.excel_path = Path(excel_path)
        
        # Setup device
        self.device = get_device()
        
        # Determine input dimensions from data
        self.input_dim = 3  # Default: Gestational_Age, Baby_Heart_Rate, Amniotic_Fluid_Index
        self.num_classes = 4  # Cephalic, Breech, Transverse, Not Fixed
        
        # Initialize model
        self.model = create_model(
            input_dim=self.input_dim,
            num_classes=self.num_classes,
            hidden_dims=[128, 64, 32],
            dropout=0.3
        )
        self.model = self.model.to(self.device)
        
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
        print(f"   Excel data path: {self.excel_path}")
        print(f"   Server URL: {self.server_url}")
    
    def predict(self, patient_data: Dict) -> Dict[str, any]:
        """
        Generate a prediction for patient data
        
        Args:
            patient_data: Dictionary with patient features
            
        Returns:
            Dictionary containing prediction results
        """
        import numpy as np
        from sklearn.preprocessing import StandardScaler
        import pickle
        
        try:
            # Extract numeric features
            features = []
            feature_names = ['Gestational_Age_Weeks', 'Baby_Heartbeat_bpm', 'Amniotic_Fluid_Level_cm']
            
            for name in feature_names:
                value = patient_data.get(name, 0)
                try:
                    numeric_value = float(value) if isinstance(value, (int, float)) else 0.0
                    features.append(numeric_value)
                except:
                    features.append(0.0)
            
            # Load scaler if exists
            scaler_path = Path('checkpoints/scaler.pkl')
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                features_array = np.array(features).reshape(1, -1)
                scaled_features = scaler.transform(features_array)
            else:
                scaled_features = np.array(features).reshape(1, -1)
            
            # Make prediction
            features_tensor = torch.FloatTensor(scaled_features).to(self.device)
            prediction, confidence = self.model.predict(features_tensor)
            probabilities = self.model.get_probabilities(features_tensor)
            
            # Load label encoder to get class names
            label_encoder_path = Path('checkpoints/label_encoder.pkl')
            if label_encoder_path.exists():
                with open(label_encoder_path, 'rb') as f:
                    label_encoder = pickle.load(f)
                class_name = label_encoder.inverse_transform([prediction])[0]
                class_names = list(label_encoder.classes_)
            else:
                class_names = ['Cephalic', 'Breech', 'Transverse', 'Not Fixed']
                class_name = class_names[prediction] if prediction < len(class_names) else 'Unknown'
            
            # Prepare results
            results = {
                'hospital_id': self.hospital_id,
                'position': class_name,
                'position_code': prediction,
                'confidence': confidence,
                'probabilities': {
                    class_names[i]: prob.item() 
                    for i, prob in enumerate(probabilities[0]) if i < len(class_names)
                },
                'features': patient_data
            }
            
            return results
            
        except Exception as e:
            return {
                'error': f'Prediction failed: {str(e)}',
                'hospital_id': self.hospital_id
            }
    
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
        
        # Create dataloaders from Excel file
        train_loader, test_loader = create_dataloaders(
            excel_path=str(self.excel_path),
            hospital_id=self.hospital_id,
            batch_size=batch_size,
            num_workers=0,
            train_split=0.8
        )
        
        if train_loader is None or len(train_loader.dataset) == 0:
            print(f"[WARN] No training data found for Hospital {self.hospital_id}")
            print(f"   Skipping training")
            return {'loss': [], 'accuracy': []}
        
        # Save preprocessors after first load
        if hasattr(train_loader.dataset.dataset, 'save_preprocessors'):
            save_dir = Path('checkpoints')
            train_loader.dataset.dataset.save_preprocessors(save_dir)
        
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
        
        # Save model with metadata
        save_dict = {
            'model_state_dict': self.model.state_dict(),
            'hospital_id': self.hospital_id,
            'input_dim': self.input_dim,
            'num_classes': self.num_classes,
            'epochs': num_epochs,
            'final_loss': history['loss'][-1] if history['loss'] else 0,
            'final_accuracy': history['accuracy'][-1] if history['accuracy'] else 0
        }
        torch.save(save_dict, self.model_path)
        print(f"[OK] Model saved to {self.model_path}")
        
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

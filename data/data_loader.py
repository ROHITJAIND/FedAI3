"""
PyTorch Dataset and DataLoader for Medical Text Data
"""
import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle


class MedicalTextDataset(Dataset):
    """
    Dataset class for medical patient records from Excel file
    
    Expected Excel structure:
        - Patient_ID
        - Gestational_Age
        - Baby_Heart_Rate
        - Baby_Position (Target: Cephalic, Transverse, Not Fixed, Breech)
        - Amniotic_Fluid_Index
        - Pregnancy_Type
        - Baby_Growth
        - Estimated_Birth_Date
        - Placental_Position
        - Umbilical_Cord_Status
        - Hospital (A, B, C)
    """
    
    def __init__(
        self, 
        excel_path: str,
        hospital_id: str = None,
        feature_columns: List[str] = None,
        target_column: str = 'Baby_Position',
        scaler: StandardScaler = None,
        label_encoder: LabelEncoder = None,
        train: bool = True
    ):
        """
        Initialize the dataset
        
        Args:
            excel_path: Path to Excel file
            hospital_id: Hospital ID to filter (A, B, C) or None for all
            feature_columns: List of feature columns to use
            target_column: Target column name
            scaler: Fitted StandardScaler (if None, will fit new one)
            label_encoder: Fitted LabelEncoder (if None, will fit new one)
            train: Whether this is training data (affects scaler fitting)
        """
        self.excel_path = Path(excel_path)
        self.hospital_id = hospital_id
        self.target_column = target_column
        self.train = train
        
        # Default feature columns if not provided
        if feature_columns is None:
            self.feature_columns = [
                'Gestational_Age_Weeks', 'Baby_Heartbeat_bpm', 'Amniotic_Fluid_Level_cm'
            ]
        else:
            self.feature_columns = feature_columns
        
        # Initialize or use provided scalers
        self.scaler = scaler if scaler is not None else StandardScaler()
        self.label_encoder = label_encoder if label_encoder is not None else LabelEncoder()
        
        # Load and preprocess data
        self.data = None
        self.features = None
        self.labels = None
        self.text_features = None
        self.class_mapping = {}
        self._load_data()
    
    def _load_data(self):
        """Load and preprocess data from Excel file"""
        if not self.excel_path.exists():
            print(f"[WARN] Warning: Excel file {self.excel_path} does not exist")
            return
        
        # Load Excel file
        try:
            df = pd.read_excel(self.excel_path)
            print(f"[OK] Loaded {len(df)} records from {self.excel_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load Excel file: {e}")
            return
        
        # Filter by hospital if specified
        if self.hospital_id is not None:
            df = df[df['Hospital'] == self.hospital_id]
            print(f"[OK] Filtered to Hospital {self.hospital_id}: {len(df)} records")
        
        if len(df) == 0:
            print(f"[WARN] No data available after filtering")
            return
        
        # Extract target labels
        if self.target_column not in df.columns:
            print(f"[ERROR] Target column '{self.target_column}' not found")
            return
        
        # Encode labels
        if self.train:
            self.labels = self.label_encoder.fit_transform(df[self.target_column])
            self.class_mapping = {label: idx for idx, label in enumerate(self.label_encoder.classes_)}
        else:
            self.labels = self.label_encoder.transform(df[self.target_column])
        
        print(f"[OK] Class distribution:")
        for class_name, class_idx in self.class_mapping.items():
            count = np.sum(self.labels == class_idx)
            print(f"   {class_name}: {count} records")
        
        # Extract numeric features
        numeric_features = []
        for col in self.feature_columns:
            if col in df.columns:
                # Convert to numeric, replacing non-numeric with NaN
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                numeric_features.append(numeric_col.fillna(numeric_col.mean()).values)
            else:
                print(f"[WARN] Column '{col}' not found in data, skipping")
        
        if len(numeric_features) == 0:
            print(f"[ERROR] No numeric features found. Available columns: {list(df.columns)}")
            self.features = None
            return
        
        numeric_features = np.column_stack(numeric_features)
        
        # Scale numeric features
        if self.train:
            self.features = self.scaler.fit_transform(numeric_features)
        else:
            self.features = self.scaler.transform(numeric_features)
        
        # Extract text features for concatenation
        text_cols = ['Pregnancy_Confirmed', 'Baby_Growth_Status', 'Placenta_Position', 'Umbilical_Cord_Status']
        text_data = []
        for _, row in df.iterrows():
            text_parts = []
            for col in text_cols:
                if col in df.columns:
                    text_parts.append(f"{col}: {row[col]}")
            text_data.append(", ".join(text_parts))
        
        self.text_features = text_data
        self.data = df
        
    def __len__(self) -> int:
        """Return the total number of records"""
        if self.features is None:
            return 0
        return len(self.features)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, str]:
        """
        Get a single item from the dataset
        
        Args:
            idx: Index of the item
            
        Returns:
            Tuple of (feature_tensor, label, text_features)
        """
        features = torch.FloatTensor(self.features[idx])
        label = int(self.labels[idx])
        text = self.text_features[idx] if self.text_features else ""
        
        return features, label, text
    
    def save_preprocessors(self, save_dir: Path):
        """Save scaler and label encoder for later use"""
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        with open(save_dir / 'scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        with open(save_dir / 'label_encoder.pkl', 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        print(f"[OK] Saved preprocessors to {save_dir}")
    
    @staticmethod
    def load_preprocessors(load_dir: Path) -> Tuple[StandardScaler, LabelEncoder]:
        """Load saved scaler and label encoder"""
        load_dir = Path(load_dir)
        
        with open(load_dir / 'scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        with open(load_dir / 'label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        
        return scaler, label_encoder


def create_dataloaders(
    excel_path: str,
    hospital_id: str = None,
    batch_size: int = 16,
    num_workers: int = 0,
    feature_columns: List[str] = None,
    train_split: float = 0.8
) -> Tuple[DataLoader, DataLoader]:
    """
    Create training and testing dataloaders from Excel file
    
    Args:
        excel_path: Path to Excel file
        hospital_id: Hospital ID to filter (A, B, C)
        batch_size: Batch size for dataloaders
        num_workers: Number of worker processes for data loading
        feature_columns: List of feature columns to use
        train_split: Fraction of data to use for training
        
    Returns:
        Tuple of (train_loader, test_loader)
    """
    # Create full dataset
    full_dataset = MedicalTextDataset(
        excel_path=excel_path,
        hospital_id=hospital_id,
        feature_columns=feature_columns,
        train=True
    )
    
    if len(full_dataset) == 0:
        print("[ERROR] No data loaded, cannot create dataloaders")
        return None, None
    
    # Split into train and test
    train_size = int(train_split * len(full_dataset))
    test_size = len(full_dataset) - train_size
    
    train_dataset, test_dataset = torch.utils.data.random_split(
        full_dataset, [train_size, test_size]
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    return train_loader, test_loader


if __name__ == "__main__":
    print("=" * 60)
    print("MEDICAL TEXT DATASET - TEST")
    print("=" * 60)
    
    # Test dataset creation
    dataset = MedicalTextDataset(
        excel_path="data/patient_data.xlsx",
        hospital_id="A",
        train=True
    )
    
    print(f"\n[DATA] Dataset Statistics:")
    print(f"   Total records: {len(dataset)}")
    
    if len(dataset) > 0:
        # Test loading a single item
        print(f"\n[TEST] Testing single item load...")
        features, label, text = dataset[0]
        print(f"   Features shape: {features.shape}")
        print(f"   Label: {label}")
        print(f"   Text: {text[:100]}...")
    
    print("\n" + "=" * 60)

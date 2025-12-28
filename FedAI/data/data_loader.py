"""
PyTorch Dataset and DataLoader for Fetal Ultrasound Images
"""
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from pathlib import Path
from typing import Tuple, List, Dict
import os


class FetalUltrasoundDataset(Dataset):
    """
    Dataset class for fetal ultrasound images
    
    Expected directory structure:
        data_dir/
            Cephalic/
                image1.jpg
                image2.jpg
                ...
            Breech/
                image1.jpg
                image2.jpg
                ...
            Transverse/
                image1.jpg
                image2.jpg
                ...
    """
    
    def __init__(
        self, 
        data_dir: Path, 
        transform=None,
        class_mapping: Dict[str, int] = None
    ):
        """
        Initialize the dataset
        
        Args:
            data_dir: Root directory containing class subdirectories
            transform: Optional transform to apply to images
            class_mapping: Dictionary mapping class names to indices
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        
        # Default class mapping
        if class_mapping is None:
            self.class_mapping = {
                'Cephalic': 0,
                'Breech': 1,
                'Transverse': 2
            }
        else:
            self.class_mapping = class_mapping
        
        # Load image paths and labels
        self.image_paths = []
        self.labels = []
        self._load_data()
        
    def _load_data(self):
        """Load all image paths and corresponding labels"""
        if not self.data_dir.exists():
            print(f"[WARN]  Warning: Directory {self.data_dir} does not exist")
            return
        
        for class_name, class_idx in self.class_mapping.items():
            class_dir = self.data_dir / class_name
            
            if not class_dir.exists():
                print(f"[WARN]  Warning: Class directory {class_dir} does not exist")
                continue
            
            # Find all images in class directory
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                for img_path in class_dir.glob(ext):
                    self.image_paths.append(img_path)
                    self.labels.append(class_idx)
        
        print(f"[OK] Loaded {len(self.image_paths)} images from {self.data_dir}")
        
        # Print class distribution
        for class_name, class_idx in self.class_mapping.items():
            count = self.labels.count(class_idx)
            print(f"   {class_name}: {count} images")
    
    def __len__(self) -> int:
        """Return the total number of images"""
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get a single item from the dataset
        
        Args:
            idx: Index of the item
            
        Returns:
            Tuple of (image_tensor, label)
        """
        # Load image
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Get label
        label = self.labels[idx]
        
        return image, label


def get_transforms(training: bool = True, img_size: int = 224) -> transforms.Compose:
    """
    Get image preprocessing transforms
    
    Args:
        training: Whether to apply training augmentations
        img_size: Target image size
        
    Returns:
        Composition of transforms
    """
    if training:
        # Training transforms with data augmentation
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],  # ImageNet stats
                std=[0.229, 0.224, 0.225]
            )
        ])
    else:
        # Validation/test transforms (no augmentation)
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])


def create_dataloaders(
    train_dir: Path,
    test_dir: Path = None,
    batch_size: int = 16,
    num_workers: int = 0,
    img_size: int = 224
) -> Tuple[DataLoader, DataLoader]:
    """
    Create training and testing dataloaders
    
    Args:
        train_dir: Directory containing training data
        test_dir: Directory containing test data
        batch_size: Batch size for dataloaders
        num_workers: Number of worker processes for data loading
        img_size: Target image size
        
    Returns:
        Tuple of (train_loader, test_loader)
    """
    # Create datasets
    train_dataset = FetalUltrasoundDataset(
        train_dir,
        transform=get_transforms(training=True, img_size=img_size)
    )
    
    # Create train loader
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    # Create test loader if test directory provided
    test_loader = None
    if test_dir is not None and Path(test_dir).exists():
        test_dataset = FetalUltrasoundDataset(
            test_dir,
            transform=get_transforms(training=False, img_size=img_size)
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
    print("FETAL ULTRASOUND DATASET - TEST")
    print("=" * 60)
    
    # Test dataset creation
    from utils.config import HOSPITAL_A_DIR
    
    dataset = FetalUltrasoundDataset(
        HOSPITAL_A_DIR,
        transform=get_transforms(training=True)
    )
    
    print(f"\n[DATA] Dataset Statistics:")
    print(f"   Total images: {len(dataset)}")
    
    if len(dataset) > 0:
        # Test loading a single item
        print(f"\n[TEST] Testing single item load...")
        image, label = dataset[0]
        print(f"   Image shape: {image.shape}")
        print(f"   Label: {label}")
        print(f"   Label name: {list(dataset.class_mapping.keys())[label]}")
    
    print("\n" + "=" * 60)

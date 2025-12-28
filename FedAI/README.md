# FetalScanFL: Federated Learning for Fetal Ultrasound Analysis

## 🎯 Project Overview

A privacy-preserving AI system that analyzes fetal ultrasound images to determine fetal position and key health indicators using **Federated Learning**.

### The Problem

Ultrasound quality varies wildly between machines (GE vs. Philips vs. Siemens). A single hospital's AI might fail on images from a different clinic.

### The Solution

Federated Learning allows the model to learn from all hospitals' data simultaneously, creating a robust "Universal Sonographer" AI, while data remains locked in each local hospital.

## 🏗️ Architecture

### Components

1. **Central Server (The "Consultant")**

   - FastAPI backend
   - Holds the Global Model
   - Aggregates knowledge (weights) from hospitals

2. **Local Clients (The "Sonographers")**

   - Hospital/clinic systems
   - Perform local inference and training
   - Send weight updates to server

3. **CNN Model (The "Eye")**
   - ResNet-based architecture
   - Input: 2D Ultrasound Image
   - Output Classes:
     - Cephalic (Head Down - Normal)
     - Breech (Head Up - Requires attention)
     - Transverse (Sideways - Requires attention)

## 📁 Project Structure

```
FedAI/
├── server/
│   ├── server.py          # FastAPI central server
│   └── aggregator.py      # FedAvg algorithm
├── client/
│   ├── client.py          # Local hospital client
│   └── trainer.py         # Local training logic
├── models/
│   ├── model.py           # CNN architecture
│   └── resnet.py          # ResNet implementation
├── data/
│   ├── Hospital_A/        # Simulated hospital data
│   ├── Hospital_B/        # Simulated hospital data
│   ├── Test_Set/          # Test data
│   └── data_loader.py     # Dataset utilities
├── utils/
│   ├── config.py          # Configuration settings
│   └── helpers.py         # Utility functions
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🚀 Installation

```bash
# Clone or navigate to project
cd "c:\Users\SEC\Documents\SEMESTER 7\FedAI"

# Install dependencies
pip install -r requirements.txt
```

## 📊 Usage

### 1. Prepare Data (Phase 1)

```bash
python data/prepare_data.py
```

### 2. Start Central Server (Phase 4)

```bash
python server/server.py
```

### 3. Run Local Client (Phase 3)

```bash
# For Hospital A
python client/client.py --hospital A

# For Hospital B
python client/client.py --hospital B
```

### 4. Inference (Doctor's Usage)

```python
from client.client import LocalClient

client = LocalClient(hospital_id="A")
result = client.predict("path/to/ultrasound.jpg")
print(result)  # Position: Breech, Confidence: 98%
```

## 🔄 Workflow

### Scenario 1: Doctor's Usage (Inference)

1. Doctor uploads fetal scan to local dashboard
2. Local model processes image instantly
3. System returns: Position, Plane, Anomaly Flag
4. Doctor confirms diagnosis (saved for training)

### Scenario 2: Learning Cycle (Federated Training)

1. **Local Update**: Hospital trains model on confirmed images
2. **Push**: Hospital sends weight updates to Central Server
3. **Aggregation**: Server averages updates from all hospitals
4. **Pull**: Hospitals download updated Global Model
5. **Result**: All hospitals benefit from collective learning

## 🛠️ Implementation Phases

- ✅ **Phase 1**: Data Preparation & Simulation
- ✅ **Phase 2**: Core Model (CNN Architecture)
- ✅ **Phase 3**: Local Client (Report Generator)
- ✅ **Phase 4**: Federation (Server & Communication)

## 📦 Dependencies

- Python 3.8+
- PyTorch
- FastAPI
- Uvicorn
- Pillow
- NumPy
- scikit-learn

## 🔒 Privacy Features

- **No Data Sharing**: Raw images never leave local hospitals
- **Weight Aggregation**: Only model parameters are shared
- **Differential Privacy**: Optional noise injection for enhanced privacy
- **Secure Communication**: HTTPS encryption for weight transfer

## 📄 License

Educational Project - 2025

## 👥 Authors

SEC - Semester 7 Project

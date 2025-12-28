# 🏥 Individual Hospital Federated Learning System

## ✨ What's New?

Your federated learning system now has **separate web interfaces for each hospital**! Each hospital can independently:

- 📥 Download the global model
- 🎓 Train on their own data
- 📤 Push weights to improve the global model

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CENTRAL SERVER (Port 8000)                     │
│              Stores Global Model                            │
│              Gets Better with Each Hospital's Contribution  │
└──────────────┬────────────┬────────────┬────────────────────┘
               │            │            │
       ┌───────▼──────┐  ┌──▼──────┐  ┌──▼──────┐
       │ Hospital A   │  │Hospital B│  │Hospital C│
       │ Port 5001    │  │Port 5002 │  │Port 5003 │
       │ Purple Theme │  │Pink Theme│  │Teal Theme│
       └──────────────┘  └──────────┘  └──────────┘
            │                 │             │
            ▼                 ▼             ▼
       Own Data          Own Data      Own Data
       (Private)         (Private)     (Private)
```

## 🚀 Quick Start

### Option 1: Start Everything at Once

```bash
python start_all.py
```

This opens 4 terminal windows:

- Central Server (Port 8000)
- Hospital A (Port 5001)
- Hospital B (Port 5002)
- Hospital C (Port 5003)

### Option 2: Manual Start (Recommended for Learning)

**Terminal 1 - Central Server:**

```bash
python server/server.py
```

**Terminal 2 - Hospital A:**

```bash
python run_hospital_a.py
```

**Terminal 3 - Hospital B:**

```bash
python run_hospital_b.py
```

**Terminal 4 - Hospital C:**

```bash
python run_hospital_c.py
```

## 🌐 Access Points

| Service        | URL                        | Description                   |
| -------------- | -------------------------- | ----------------------------- |
| Central Server | http://localhost:8000/docs | FastAPI documentation         |
| Hospital A     | http://localhost:5001      | Hospital A interface (Purple) |
| Hospital B     | http://localhost:5002      | Hospital B interface (Pink)   |
| Hospital C     | http://localhost:5003      | Hospital C interface (Teal)   |

## 📖 Complete Workflow

### Step 1: Hospital A (First Contributor)

1. Open http://localhost:5001
2. Click **"Start Training"** (set epochs: 5)
   - Trains on `data/Hospital_A/` images
   - Watch metrics improve in real-time
   - Loss decreases, Accuracy increases
3. Click **"Push to Global"**
   - Uploads weights to central server
   - Global model now has Hospital A's knowledge

### Step 2: Hospital B (Second Contributor)

1. Open http://localhost:5002
2. Click **"Download Global Model"**
   - Gets the model trained by Hospital A
   - Starting with better weights!
3. Click **"Start Training"** (set epochs: 5)
   - Fine-tunes on `data/Hospital_B/` images
   - Different patients, different patterns
4. Click **"Push to Global"**
   - Global model now combines A + B knowledge

### Step 3: Hospital C (Third Contributor)

1. Open http://localhost:5003
2. Click **"Download Global Model"**
   - Gets model with A + B knowledge
3. Click **"Start Training"** (set epochs: 5)
   - Fine-tunes on `data/Hospital_C/` images
4. Click **"Push to Global"**
   - Global model now has A + B + C knowledge
   - Best performance achieved!

## 🎨 Dashboard Features

Each hospital interface includes:

### 1. Action Cards

- **Download Global Model**: Get latest from central server
- **Train Local Model**: Train on hospital's private data
- **Push to Global**: Share weights (not data) with global model

### 2. Status Dashboard

- **Training Status**: Shows if currently training
- **Model Status**: Indicates if local model exists
- **Global Model Status**: Shows if global model downloaded

### 3. Metrics Display

- **Current Loss**: How wrong the model is
- **Current Accuracy**: Percentage of correct predictions
- Visual progress bars for both metrics

### 4. Training History Chart

- Line graph showing loss and accuracy over epochs
- Dual Y-axis for better visualization

### 5. Activity Log

- Real-time updates
- Color-coded messages:
  - 🔵 Blue: Info
  - 🟢 Green: Success
  - 🔴 Red: Error
  - 🟡 Yellow: Warning
- Auto-scroll feature

## 💾 Data Structure

```
FedAI/
├── data/
│   ├── Hospital_A/          # Hospital A's private data
│   │   ├── Breech/
│   │   ├── Cephalic/
│   │   └── Transverse/
│   ├── Hospital_B/          # Hospital B's private data
│   │   ├── Breech/
│   │   ├── Cephalic/
│   │   └── Transverse/
│   └── Hospital_C/          # Hospital C's private data
│       ├── Breech/
│       ├── Cephalic/
│       └── Transverse/
└── checkpoints/
    ├── global_model.pth     # Shared global model
    ├── hospital_A_model.pth # Hospital A's local model
    ├── hospital_B_model.pth # Hospital B's local model
    └── hospital_C_model.pth # Hospital C's local model
```

## 🔒 Privacy Guarantee

### What Travels:

✅ Model weights (mathematical parameters)
✅ Training metrics (loss, accuracy numbers)

### What Stays Local:

❌ Patient images
❌ Raw data
❌ Any identifiable information

**Each hospital's data NEVER leaves their computer!**

## 📊 Expected Results

Typical progression:

| Round | Hospital | Starting Acc   | Final Acc | Loss |
| ----- | -------- | -------------- | --------- | ---- |
| 1     | A trains | 33% (random)   | 75%       | 0.65 |
| 2     | B trains | 75% (from A)   | 83%       | 0.42 |
| 3     | C trains | 83% (from A+B) | 91%       | 0.28 |

**Key Insight**: Each hospital benefits from previous hospitals' learning!

## 🛠️ Files Overview

### Core Files

- `hospital_interface.py` - Main Flask application for hospitals
- `run_hospital_a.py` - Launch script for Hospital A
- `run_hospital_b.py` - Launch script for Hospital B
- `run_hospital_c.py` - Launch script for Hospital C
- `start_all.py` - Quick start all services

### Frontend

- `templates/hospital_dashboard.html` - Dashboard HTML
- `static/css/hospital_style.css` - Beautiful styling
- `static/js/hospital_app.js` - Client-side logic

### Documentation

- `HOSPITAL_INTERFACE_GUIDE.md` - Detailed usage guide
- `NEW_HOSPITAL_ARCHITECTURE.md` - This file

## 🎓 How It Works

### Training Process (Technical)

1. **Download Phase**

   ```python
   # Hospital downloads global model weights
   GET http://localhost:8000/download/global
   # Saves to local model
   ```

2. **Training Phase**

   ```python
   # Train on local data (data NEVER leaves!)
   for epoch in range(num_epochs):
       for images, labels in hospital_dataloader:
           loss = train_step(model, images, labels)
   # Save local model
   ```

3. **Upload Phase**

   ```python
   # Upload ONLY weights (not data!)
   weights = model.state_dict()  # Just numbers
   POST http://localhost:8000/upload/Hospital_A
   ```

4. **Aggregation Phase**
   ```python
   # Server updates global model
   POST http://localhost:8000/aggregate
   # Global model gets better!
   ```

## 🐛 Troubleshooting

### "Server Offline" Message

- Make sure central server is running: `python server/server.py`
- Check port 8000 is not blocked

### "Cannot Push - No Model"

- Train the model first before pushing

### Training Doesn't Start

- Check if data exists in `data/Hospital_X/`
- Verify all subdirectories have images

### Charts Not Updating

- Refresh browser page
- Check browser console for errors

## 💡 Tips

1. **Order Matters**: Start with A, then B, then C for best cumulative learning
2. **Experiment**: Try different epoch numbers (3, 5, 10)
3. **Multiple Rounds**: Can repeat download→train→push multiple times
4. **Compare**: Open all three hospital interfaces side-by-side
5. **Monitor Logs**: Activity logs show exactly what's happening

## 🎉 Benefits of This Architecture

1. **Privacy**: Data stays local at each hospital
2. **Independence**: Each hospital controls when to train
3. **Collaboration**: All benefit from shared knowledge
4. **Transparency**: See exactly what each hospital contributes
5. **Scalability**: Easy to add more hospitals

## 📚 Next Steps

1. Add more data to Hospital_C folders
2. Try training with different parameters
3. Observe how global model improves
4. Experiment with multiple training rounds

Enjoy your distributed federated learning system! 🚀

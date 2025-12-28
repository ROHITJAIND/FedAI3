# Individual Hospital Interface Guide

## 🏥 New Architecture Overview

Each hospital now has its **own web interface** where they can:

1. **Download** the global model from central server
2. **Train** the model on their local data
3. **Push** only the weights to improve the global model

## 🚀 How to Run

### Step 1: Start Central Server

```bash
python server/server.py
```

This runs at `http://localhost:8000`

### Step 2: Start Individual Hospitals

Open **separate terminals** for each hospital:

#### Hospital A:

```bash
python run_hospital_a.py
```

Access at: `http://localhost:5001`

#### Hospital B:

```bash
python run_hospital_b.py
```

Access at: `http://localhost:5002`

#### Hospital C:

```bash
python run_hospital_c.py
```

Access at: `http://localhost:5003`

## 📋 Workflow

### Hospital A (First Hospital):

1. **Train First**

   - Click "Start Training" (e.g., 5 epochs)
   - Model trains on `data/Hospital_A/` images
   - Local model saved: `checkpoints/hospital_A_model.pth`

2. **Push to Global**
   - Click "Push to Global"
   - Uploads weights to central server
   - Global model now has Hospital A's knowledge

### Hospital B (Second Hospital):

1. **Download Global Model**

   - Click "Download Global Model"
   - Gets the model that has Hospital A's knowledge

2. **Train on Local Data**

   - Click "Start Training"
   - Fine-tunes on `data/Hospital_B/` images
   - Local model saved: `checkpoints/hospital_B_model.pth`

3. **Push to Global**
   - Click "Push to Global"
   - Global model now has BOTH Hospital A & B knowledge

### Hospital C (Third Hospital):

1. **Download Global Model**

   - Gets model with A & B knowledge

2. **Train**

   - Fine-tunes on `data/Hospital_C/` images

3. **Push to Global**
   - Global model now has A, B, & C knowledge

## 🔄 The Process

```
┌─────────────────────────────────────────────────────────┐
│                  CENTRAL SERVER                         │
│                 Global Model State                      │
│                                                         │
│  Round 0: Empty/Random weights                         │
│  Round 1: Hospital A weights (first push)              │
│  Round 2: Hospital A + B weights (fine-tuned)          │
│  Round 3: Hospital A + B + C weights (fine-tuned)      │
└──────────────┬────────────┬────────────┬───────────────┘
               │            │            │
       ┌───────▼──┐    ┌────▼────┐  ┌───▼──────┐
       │Hospital A│    │Hospital B│  │Hospital C│
       │Port 5001 │    │Port 5002 │  │Port 5003 │
       └──────────┘    └──────────┘  └──────────┘
```

## 💡 Key Features

### Each Hospital Interface Has:

1. **Download Global Model Button**

   - Pulls latest model from central server
   - Indicator shows if downloaded

2. **Training Section**

   - Set number of epochs
   - Train on local data only
   - View real-time metrics (loss, accuracy)

3. **Push to Global Button**

   - Only enabled after training
   - Uploads model weights (NOT data)
   - Updates global model

4. **Status Dashboard**

   - Training status (Idle/Training)
   - Model status (Trained/Not Trained)
   - Global model status (Downloaded/Not Downloaded)

5. **Metrics Display**

   - Current loss
   - Current accuracy
   - Visual progress bars

6. **Training History Chart**

   - Loss over epochs
   - Accuracy over epochs

7. **Activity Log**
   - Real-time updates
   - Color-coded messages
   - Auto-scroll option

## 🎨 Color Coding

- **Hospital A**: Purple gradient
- **Hospital B**: Pink gradient
- **Hospital C**: Teal gradient

## 📊 Example Scenario

### Scenario: Three hospitals collaborate

1. **Hospital A** trains first (5 epochs)

   - Loss: 1.2 → 0.4
   - Accuracy: 35% → 78%
   - Pushes to global

2. **Hospital B** downloads, trains (5 epochs)

   - Starts with Hospital A's knowledge
   - Loss: 0.4 → 0.25
   - Accuracy: 78% → 85%
   - Pushes to global

3. **Hospital C** downloads, trains (5 epochs)
   - Starts with A + B knowledge
   - Loss: 0.25 → 0.15
   - Accuracy: 85% → 92%
   - Pushes to global

**Final Global Model**: 92% accuracy with knowledge from all three hospitals!

## 🔒 Privacy

- ✅ Each hospital only sees their own data
- ✅ Only model weights travel (numbers, not images)
- ✅ No hospital can see another's patient data
- ✅ Global model improves without data sharing

## 📁 File Structure

```
FedAI/
├── hospital_interface.py       # Core hospital interface
├── run_hospital_a.py          # Launch Hospital A
├── run_hospital_b.py          # Launch Hospital B
├── run_hospital_c.py          # Launch Hospital C
├── templates/
│   └── hospital_dashboard.html
├── static/
│   ├── css/
│   │   └── hospital_style.css
│   └── js/
│       └── hospital_app.js
└── data/
    ├── Hospital_A/
    ├── Hospital_B/
    └── Hospital_C/
```

## 🛠️ Tips

1. **Always start central server first**
2. **Run hospitals in separate terminals**
3. **Each hospital can work independently**
4. **Order matters for best results** (A → B → C)
5. **Can repeat training and pushing multiple times**
6. **Monitor activity logs for debugging**

Enjoy your distributed federated learning system! 🎉

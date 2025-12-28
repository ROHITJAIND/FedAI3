# 🏥 Individual Hospital Federated Learning System

## 🛠️ Technology Stack

### **Machine Learning & AI**

- **PyTorch 2.0+** - Deep learning framework for neural network training
- **Google Gemini AI (gemini-2.5-flash)** - AI-powered medical text analysis and report generation
- **Scikit-learn** - Data preprocessing (StandardScaler, LabelEncoder)
- **Transformers** - NLP model support
- **NumPy** - Numerical computing

### **Backend Frameworks**

- **Flask 3.0+** - Web framework for individual hospital interfaces
- **FastAPI 0.104+** - High-performance central server API
- **Uvicorn** - ASGI server for FastAPI
- **Flask-CORS** - Cross-origin resource sharing

### **Authentication & Security**

- **Auth0** - OAuth 2.0 authentication service
- **Authlib 1.3+** - OAuth integration library
- **python-dotenv** - Environment variable management

### **Data Processing**

- **Pandas 2.0+** - Excel data manipulation and analysis
- **openpyxl 3.1+** - Excel file reading/writing
- **Pydantic 2.0+** - Data validation

### **PDF Processing**

- **PyPDF2 3.0+** - PDF text extraction
- **ReportLab 4.0+** - PDF report generation

### **Frontend Technologies**

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with gradients and animations
- **JavaScript (ES6+)** - Client-side interactivity
- **Server-Sent Events (SSE)** - Real-time log streaming
- **Fetch API** - Asynchronous HTTP requests

### **Federated Learning Architecture**

- **Custom PyTorch Implementation** - Sequential federated training
- **Model Aggregation** - FedAvg algorithm for weight averaging
- **Client-Server Pattern** - Distributed learning across hospitals

### **Additional Libraries**

- **Requests 2.31+** - HTTP client for inter-service communication
- **Python-multipart** - File upload handling
- **Matplotlib 3.7+** - Data visualization
- **Pillow 10.0+** - Image processing
- **Pickle** - Model serialization

### **Development Environment**

- **Python 3.11** - Programming language
- **Visual Studio Code** - IDE
- **Git** - Version control

---

## ✨ What's New?

Your federated learning system now has **separate web interfaces for each hospital**! Each hospital can independently:

- 📥 Download the global model
- 🎓 Train on their own data
- 📤 Push weights to improve the global model
- 📄 Upload patient PDF reports for AI-powered analysis

## 🎯 System Architecture

### **Overall Architecture Diagram**

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                 │
│  ┌─────────────────┐              ┌──────────────────────┐               │
│  │   Auth0 OAuth   │              │   Google Gemini AI    │               │
│  │  Authentication │              │   (gemini-2.5-flash)  │               │
│  └────────┬────────┘              └──────────┬───────────┘               │
└───────────┼────────────────────────────────────┼──────────────────────────┘
            │                                     │
            │ OAuth 2.0                          │ API Calls
            │                                     │
┌───────────▼─────────────────────────────────────▼──────────────────────────┐
│                     FEDERATED LEARNING SYSTEM                              │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │           CENTRAL SERVER (FastAPI - Port 8000)                   │    │
│  │  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐    │    │
│  │  │ Global Model   │  │ FedAvg       │  │ Model Repository │    │    │
│  │  │ (PyTorch)      │  │ Aggregator   │  │ (checkpoints/)   │    │    │
│  │  └────────────────┘  └──────────────┘  └──────────────────┘    │    │
│  └──────────┬──────────────────┬──────────────────┬─────────────────┘    │
│             │                  │                  │                       │
│     HTTP Download        HTTP Upload        HTTP Upload                  │
│             │                  │                  │                       │
│  ┌──────────▼──────┐  ┌────────▼──────┐  ┌───────▼──────────┐          │
│  │   HOSPITAL A    │  │   HOSPITAL B   │  │   HOSPITAL C     │          │
│  │ Flask (Port 5000)│  │Flask (Port 5001)│  │Flask (Port 5002)│          │
│  ├─────────────────┤  ├────────────────┤  ├──────────────────┤          │
│  │ LocalClient     │  │ LocalClient    │  │ LocalClient      │          │
│  │ Trainer         │  │ Trainer        │  │ Trainer          │          │
│  │ PDFAnalyzer     │  │ PDFAnalyzer    │  │ PDFAnalyzer      │          │
│  │ Auth0 Login     │  │ Auth0 Login    │  │ Auth0 Login      │          │
│  └────────┬────────┘  └────────┬───────┘  └────────┬─────────┘          │
│           │                    │                    │                     │
│           ▼                    ▼                    ▼                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │ Hospital A Data │  │ Hospital B Data │  │ Hospital C Data │          │
│  │ (400 patients)  │  │ (400 patients)  │  │ (400 patients)  │          │
│  │ Excel + PDFs    │  │ Excel + PDFs    │  │ Excel + PDFs    │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
└────────────────────────────────────────────────────────────────────────────┘
```

### **Data Flow Architecture**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FEDERATED TRAINING FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

Round 1: Hospital A                Round 2: Hospital B              Round 3: Hospital C
┌──────────────────┐              ┌──────────────────┐            ┌──────────────────┐
│ 1. Download      │              │ 1. Download      │            │ 1. Download      │
│    Global Model  │──────┐       │    Global Model  │──────┐     │    Global Model  │
└────────┬─────────┘      │       └────────┬─────────┘      │     └────────┬─────────┘
         │                │                │                │              │
         ▼                │                ▼                │              ▼
┌──────────────────┐      │       ┌──────────────────┐      │     ┌──────────────────┐
│ 2. Train on      │      │       │ 2. Train on      │      │     │ 2. Train on      │
│    400 patients  │      │       │    400 patients  │      │     │    400 patients  │
│    (Excel data)  │      │       │    (Excel data)  │      │     │    (Excel data)  │
└────────┬─────────┘      │       └────────┬─────────┘      │     └────────┬─────────┘
         │                │                │                │              │
         ▼                │                ▼                │              ▼
┌──────────────────┐      │       ┌──────────────────┐      │     ┌──────────────────┐
│ 3. Upload        │      │       │ 3. Upload        │      │     │ 3. Upload        │
│    Weights       │──────┤       │    Weights       │──────┤     │    Weights       │
└──────────────────┘      │       └──────────────────┘      │     └──────────────────┘
                          │                                 │
                          ▼                                 ▼
                 ┌─────────────────┐              ┌─────────────────┐
                 │ 4. FedAvg       │              │ 4. FedAvg       │
                 │    Aggregate    │              │    Aggregate    │
                 │    (A weights)  │              │    (A+B weights)│
                 └─────────────────┘              └─────────────────┘
                          │                                 │
                          ▼                                 ▼
                 Global Model v1              Global Model v2 (Improved)
```

### **PDF Analysis Workflow**

```
┌────────────────────────────────────────────────────────────────────────┐
│                    PDF ANALYSIS WITH GEMINI AI                         │
└────────────────────────────────────────────────────────────────────────┘

Hospital uploads patient report PDF
         │
         ▼
┌─────────────────────────────────┐
│  1. PDF Text Extraction         │
│     (PyPDF2)                    │
│  - Extract all text from PDF    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  2. Gemini AI Parsing           │
│     (gemini-2.5-flash)          │
│  - Extract patient data:        │
│    • Gestational Age (weeks)    │
│    • Baby Heartbeat (bpm)       │
│    • Amniotic Fluid Level (cm)  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  3. ML Model Prediction         │
│     (PyTorch)                   │
│  - Preprocess features          │
│  - Run through neural network   │
│  - Predict baby position:       │
│    • Cephalic / Breech /        │
│      Transverse / Not Fixed     │
│  - Calculate confidence score   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  4. Gemini AI Summary           │
│     (gemini-2.5-flash)          │
│  - Generate medical summary:    │
│    • Current status             │
│    • ML prediction results      │
│    • Risk assessment            │
│    • Recommendations            │
│    • Follow-up actions          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  5. PDF Report Generation       │
│     (ReportLab)                 │
│  - Create formatted PDF         │
│  - Include all analysis         │
│  - Save to reports/ folder      │
└────────────┬────────────────────┘
             │
             ▼
   Download analysis report PDF
```

### **Authentication Flow**

```
┌────────────────────────────────────────────────────────────┐
│                  AUTH0 AUTHENTICATION                      │
└────────────────────────────────────────────────────────────┘

User accesses Hospital Interface
         │
         ▼
┌─────────────────────┐
│ Check session       │
│ (Flask session)     │
└──────┬──────────────┘
       │
       ├─ Not logged in ──────────────┐
       │                              ▼
       │                    ┌──────────────────────┐
       │                    │ Redirect to Auth0    │
       │                    │ Login page           │
       │                    └──────────┬───────────┘
       │                               │
       │                               ▼
       │                    ┌──────────────────────┐
       │                    │ User enters          │
       │                    │ credentials          │
       │                    └──────────┬───────────┘
       │                               │
       │                               ▼
       │                    ┌──────────────────────┐
       │                    │ Auth0 validates      │
       │                    │ & creates token      │
       │                    └──────────┬───────────┘
       │                               │
       │                               ▼
       │                    ┌──────────────────────┐
       │                    │ Callback to app      │
       │                    │ with access token    │
       │                    └──────────┬───────────┘
       │                               │
       ▼                               ▼
┌─────────────────────────────────────────┐
│ Create session with user info           │
│ - User email                            │
│ - User ID                               │
│ - Profile data                          │
└──────────────┬──────────────────────────┘
               │
               ▼
    Grant access to Hospital Dashboard
```

### **Model Architecture**

```
┌─────────────────────────────────────────────────────────┐
│           MedicalTextClassifier (PyTorch)               │
└─────────────────────────────────────────────────────────┘

Input Layer (3 features)
├─ Gestational_Age_Weeks
├─ Baby_Heartbeat_bpm
└─ Amniotic_Fluid_Level_cm
         │
         ▼
┌──────────────────────┐
│ StandardScaler       │
│ (Normalization)      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Layer 1              │
│ Linear(3 → 128)      │
│ BatchNorm1d(128)     │
│ ReLU                 │
│ Dropout(0.3)         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Layer 2              │
│ Linear(128 → 64)     │
│ BatchNorm1d(64)      │
│ ReLU                 │
│ Dropout(0.3)         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Layer 3              │
│ Linear(64 → 32)      │
│ BatchNorm1d(32)      │
│ ReLU                 │
│ Dropout(0.3)         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Output Layer         │
│ Linear(32 → 4)       │
└──────────┬───────────┘
           │
           ▼
Output (4 classes)
├─ Cephalic
├─ Breech
├─ Transverse
└─ Not Fixed

Total Parameters: 11,428
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

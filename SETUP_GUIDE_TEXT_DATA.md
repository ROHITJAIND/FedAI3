# XLSX Data Migration & PDF Analysis Setup Guide

## Overview

Your FedAI3 project has been transformed from an image-based classification system to a **text-based medical data analysis system** with **PDF report analysis using Gemini AI**.

## Major Changes Summary

### 1. **Data Format Change**

- **Before:** Image dataset (ultrasound scans in folders)
- **After:** Excel (XLSX) dataset with patient records

### 2. **Model Architecture Change**

- **Before:** ResNet CNN for image classification
- **After:** Feedforward Neural Network for tabular data classification

### 3. **New Feature: PDF Analysis**

- Upload patient reports in PDF format
- AI extracts structured data from PDFs
- Model makes predictions based on extracted data
- Gemini AI generates comprehensive medical summaries
- Automatically generates analysis reports as PDFs

---

## Step 1: Prepare Your Excel Dataset

### Required File Location

Place your Excel file here:

```
data/patient_data.xlsx
```

### Expected Excel Structure

Your file should have these columns (based on your sample):

- `Patient_ID`
- `Gestational_Age` (numeric)
- `Baby_Heart_Rate` (numeric)
- `Baby_Position` (Target: Cephalic, Transverse, Not Fixed, Breech)
- `Amniotic_Fluid_Index` (numeric)
- `Pregnancy_Type` (e.g., "Yes", "Normal", etc.)
- `Baby_Growth` (e.g., "Normal", "Slight Delay", "Growth Restricted")
- `Estimated_Birth_Date` (date format)
- `Placental_Position` (e.g., "Posterior", "Anterior", "Low Lying")
- `Umbilical_Cord_Status` (e.g., "Wrapped Once", "Reduced Flow", "Normal")
- **`Hospital`** (Required: "A", "B", or "C")

### Data Distribution

- Total rows: 1200
- Hospital A: 400 rows (Hospital column = "A")
- Hospital B: 400 rows (Hospital column = "B")
- Hospital C: 400 rows (Hospital column = "C")

---

## Step 2: Get Gemini API Key

### To enable PDF analysis, you need a Google Gemini API key:

1. **Visit:** https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Create API Key** (it's free to start)
4. **Copy** the API key

### Add to .env file

Open `.env` and replace the placeholder:

```env
GEMINI_API_KEY=your-actual-api-key-here
```

---

## Step 3: Install New Dependencies

Run this command to install all required packages:

```bash
pip install -r requirements.txt
```

### New packages added:

- `openpyxl` - For reading Excel files
- `PyPDF2` - For PDF text extraction
- `reportlab` - For generating PDF reports
- `google-generativeai` - For Gemini AI integration
- `transformers` - For advanced text processing
- `sentencepiece` - Tokenization support

---

## Step 4: Test the Setup

### Test 1: Verify Data Loading

```bash
python data/data_loader.py
```

Expected output:

- ✓ Loaded 1200 records from data/patient_data.xlsx
- ✓ Filtered to Hospital A: 400 records
- ✓ Class distribution shown

### Test 2: Verify Model

```bash
python models/model.py
```

Expected output:

- ✓ Model created successfully
- ✓ Input/output dimensions shown
- ✓ Test prediction runs

### Test 3: Verify PDF Analyzer

```bash
python utils/pdf_analyzer.py
```

Expected output:

- ✓ PDF Analyzer initialized
- ✓ Gemini AI: Configured
- ✓ ML Model: Loaded (if model exists)

---

## Step 5: Train the Model

### Option A: Train All Hospitals Sequentially

```bash
python sequential_training.py
```

This will:

1. Train Hospital A model (400 rows)
2. Train Hospital B model (400 rows)
3. Train Hospital C model (400 rows)
4. Aggregate into global model

### Option B: Train Individual Hospital

```bash
python run_hospital_a.py --epochs 10
```

Replace with `run_hospital_b.py` or `run_hospital_c.py` for other hospitals.

---

## Step 6: Use the Hospital Interface

### Start Hospital Interface

```bash
python hospital_interface.py --hospital A --port 5000
```

Replace `A` with `B` or `C` for other hospitals.

### Access the Dashboard

Open your browser: **http://localhost:5000**

### New PDF Analysis Features:

#### 1. **Upload PDF Reports**

- Click "Upload Patient Report (PDF)"
- Select a patient report PDF file
- System automatically:
  - Extracts text from PDF
  - Uses Gemini AI to parse patient data
  - Makes prediction using trained model
  - Generates comprehensive medical summary
  - Creates analysis report PDF

#### 2. **View Generated Reports**

- Click "View Reports"
- Download analysis PDFs
- Each report includes:
  - Extracted patient data
  - AI model prediction
  - Confidence scores
  - Medical summary and recommendations

---

## Architecture Changes Details

### Data Flow (Old vs New)

#### OLD (Image-based):

```
Image Files → CNN → Classification → Report
```

#### NEW (Text-based):

```
Excel File → Feature Extraction → Neural Network → Classification
```

#### NEW (PDF Analysis):

```
PDF Upload → Text Extraction → Gemini AI Parsing →
Feature Extraction → Model Prediction →
Gemini AI Summary → PDF Report Generation
```

### Model Comparison

| Aspect         | Old (Image)        | New (Text)                       |
| -------------- | ------------------ | -------------------------------- |
| Architecture   | ResNet18/34        | Feedforward NN                   |
| Input          | 224×224 RGB images | 3 numeric features               |
| Parameters     | ~11M (ResNet18)    | ~20K                             |
| Training time  | ~10-20 min/epoch   | ~1-2 sec/epoch                   |
| Input features | Pixel values       | Gestational Age, Heart Rate, AFI |

### File Changes Summary

#### Modified Files:

- ✓ `data/data_loader.py` - Excel loading instead of images
- ✓ `models/model.py` - Neural network instead of CNN
- ✓ `client/trainer.py` - Handle text data
- ✓ `client/client.py` - Excel-based training
- ✓ `hospital_interface.py` - Added PDF upload endpoints
- ✓ `requirements.txt` - New dependencies
- ✓ `.env` - Gemini API key

#### New Files:

- ✓ `utils/pdf_analyzer.py` - Complete PDF analysis system

#### Folders Created:

- `uploads/` - Stores uploaded PDF files
- `reports/` - Stores generated analysis reports

---

## How to Use PDF Analysis Feature

### Example Workflow:

1. **Train Model First**

   ```bash
   python run_hospital_a.py --epochs 10
   ```

2. **Start Hospital Interface**

   ```bash
   python hospital_interface.py --hospital A --port 5000
   ```

3. **Upload PDF**

   - Navigate to http://localhost:5000
   - Log in (if Auth0 enabled)
   - Click "Upload Patient Report (PDF)"
   - Select a PDF file with patient information

4. **Wait for Analysis**

   - System extracts text from PDF
   - Gemini AI parses patient data
   - Model makes prediction
   - AI generates medical summary
   - PDF report is generated

5. **Download Report**
   - Click "View Reports"
   - Download the analysis report PDF
   - Report includes all findings and recommendations

---

## API Endpoints (New)

### PDF Upload

```http
POST /api/upload-pdf
Content-Type: multipart/form-data

file: <PDF file>
```

### List Reports

```http
GET /api/reports

Response:
{
  "reports": [
    {
      "filename": "A_1234567890_analysis_report.pdf",
      "size": 245678,
      "created": 1703779200
    }
  ]
}
```

### Download Report

```http
GET /api/download-report/<filename>

Response: PDF file download
```

---

## Troubleshooting

### Issue: "No data loaded"

**Solution:** Ensure `data/patient_data.xlsx` exists and has the correct columns

### Issue: "Gemini API key not found"

**Solution:** Add `GEMINI_API_KEY` to `.env` file

### Issue: "PDF analysis failed"

**Solution:**

- Check PDF is valid and readable
- Verify Gemini API key is correct
- Ensure model is trained first

### Issue: "Model dimension mismatch"

**Solution:** Delete old model files and retrain:

```bash
rm checkpoints/hospital_*.pth
python sequential_training.py
```

### Issue: "Import errors"

**Solution:** Reinstall dependencies:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

1. ✅ Place your Excel file in `data/patient_data.xlsx`
2. ✅ Get Gemini API key and add to `.env`
3. ✅ Install dependencies: `pip install -r requirements.txt`
4. ✅ Train models: `python sequential_training.py`
5. ✅ Start hospital interface: `python hospital_interface.py --hospital A --port 5000`
6. ✅ Test PDF upload feature
7. ✅ Review generated reports

---

## Support & Questions

If you encounter any issues:

1. Check console logs for error messages
2. Verify all files are in correct locations
3. Ensure dependencies are installed
4. Check that Excel file has correct column names
5. Verify Gemini API key is valid

The system is now ready to analyze patient records from both Excel data and PDF uploads!

"""
PDF Analysis and Report Generation using Gemini AI
"""
import os
from pathlib import Path
from typing import Dict, Optional
import PyPDF2
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import torch
import pickle


class PDFAnalyzer:
    """
    Handles PDF upload, text extraction, AI analysis, and report generation
    """
    
    def __init__(self, gemini_api_key: str, model_path: str = None, preprocessor_path: str = None):
        """
        Initialize PDF Analyzer
        
        Args:
            gemini_api_key: Google Gemini AI API key
            model_path: Path to trained PyTorch model
            preprocessor_path: Path to saved preprocessors (scaler, label encoder)
        """
        # Configure Gemini AI
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Load ML model if provided
        self.ml_model = None
        self.scaler = None
        self.label_encoder = None
        
        if model_path and Path(model_path).exists():
            self.load_ml_model(model_path, preprocessor_path)
    
    def load_ml_model(self, model_path: str, preprocessor_path: str = None):
        """Load the trained PyTorch model and preprocessors"""
        try:
            from models.model import MedicalTextClassifier
            
            # Load model
            checkpoint = torch.load(model_path, map_location='cpu')
            
            # Determine model dimensions from checkpoint
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
                input_dim = checkpoint.get('input_dim', 3)
                num_classes = checkpoint.get('num_classes', 4)
            else:
                state_dict = checkpoint
                # Try to infer dimensions from state dict
                first_layer_key = 'network.0.weight'
                if first_layer_key in state_dict:
                    input_dim = state_dict[first_layer_key].shape[1]
                    num_classes = state_dict[list(state_dict.keys())[-1]].shape[0]
                else:
                    input_dim = 3
                    num_classes = 4
            
            self.ml_model = MedicalTextClassifier(input_dim=input_dim, num_classes=num_classes)
            self.ml_model.load_state_dict(state_dict if not isinstance(checkpoint, dict) else state_dict)
            self.ml_model.eval()
            
            # Load preprocessors
            if preprocessor_path and Path(preprocessor_path).exists():
                with open(Path(preprocessor_path) / 'scaler.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
                with open(Path(preprocessor_path) / 'label_encoder.pkl', 'rb') as f:
                    self.label_encoder = pickle.load(f)
            
            print("[OK] ML model and preprocessors loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load ML model: {e}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                print(f"[OK] Extracted {len(text)} characters from PDF")
                return text.strip()
        
        except Exception as e:
            print(f"[ERROR] Failed to extract PDF text: {e}")
            return ""
    
    def parse_patient_data(self, text: str) -> Dict:
        """
        Use Gemini AI to extract structured patient data from text
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Dictionary with extracted patient data
        """
        prompt = f"""
        You are a medical data extraction assistant. Extract the following information from the patient report below.
        Return the data in a structured format with these exact fields:
        
        - Gestational_Age (number in weeks)
        - Baby_Heart_Rate (number in bpm)
        - Baby_Position (Cephalic, Breech, Transverse, or Not Fixed)
        - Amniotic_Fluid_Index (number)
        - Pregnancy_Type (e.g., Normal, High Risk, etc.)
        - Baby_Growth (e.g., Normal, Delayed, Advanced)
        - Placental_Position (e.g., Anterior, Posterior, etc.)
        - Umbilical_Cord_Status (e.g., Normal, Wrapped Once, etc.)
        
        If a field is not found in the report, mark it as "Not Available".
        
        Patient Report:
        {text}
        
        Return the data in this exact format:
        Gestational_Age: [value]
        Baby_Heart_Rate: [value]
        Baby_Position: [value]
        Amniotic_Fluid_Index: [value]
        Pregnancy_Type: [value]
        Baby_Growth: [value]
        Placental_Position: [value]
        Umbilical_Cord_Status: [value]
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            extracted_text = response.text
            
            # Parse the response
            data = {}
            for line in extracted_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
            
            print(f"[OK] Extracted {len(data)} fields from patient report")
            return data
        
        except Exception as e:
            print(f"[ERROR] Failed to parse patient data: {e}")
            return {}
    
    def predict_from_data(self, patient_data: Dict) -> Optional[Dict]:
        """
        Use trained model to make prediction from patient data
        
        Args:
            patient_data: Extracted patient data
            
        Returns:
            Prediction results with class and confidence
        """
        if self.ml_model is None or self.scaler is None:
            print("[WARN] ML model not loaded, skipping prediction")
            return None
        
        try:
            # Extract numeric features
            features = []
            feature_names = ['Gestational_Age_Weeks', 'Baby_Heartbeat_bpm', 'Amniotic_Fluid_Level_cm']
            
            for name in feature_names:
                value = patient_data.get(name, 'Not Available')
                try:
                    # Try to extract numeric value
                    numeric_value = float(''.join(c for c in str(value) if c.isdigit() or c == '.'))
                    features.append(numeric_value)
                except:
                    # Use mean value if not available
                    features.append(0.0)
            
            # Scale features
            import numpy as np
            features_array = np.array(features).reshape(1, -1)
            scaled_features = self.scaler.transform(features_array)
            
            # Make prediction
            features_tensor = torch.FloatTensor(scaled_features)
            predicted_class, confidence = self.ml_model.predict(features_tensor)
            
            # Get class name
            class_name = self.label_encoder.inverse_transform([predicted_class])[0]
            
            return {
                'predicted_class': class_name,
                'confidence': confidence,
                'all_probabilities': self.ml_model.get_probabilities(features_tensor).numpy().tolist()[0]
            }
        
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return None
    
    def generate_medical_summary(self, patient_data: Dict, prediction: Optional[Dict] = None) -> str:
        """
        Use Gemini AI to generate comprehensive medical summary
        
        Args:
            patient_data: Extracted patient data
            prediction: ML model prediction (optional)
            
        Returns:
            Generated medical summary
        """
        prediction_text = ""
        if prediction:
            prediction_text = f"""
            
            AI Model Prediction:
            - Predicted Baby Position: {prediction['predicted_class']}
            - Confidence: {prediction['confidence']*100:.2f}%
            """
        
        prompt = f"""
        You are a medical AI assistant. Based on the following patient data, generate a comprehensive medical summary report.
        
        Patient Data:
        {chr(10).join([f"{k}: {v}" for k, v in patient_data.items()])}
        {prediction_text}
        
        Please provide:
        1. Summary of Current Status
        2. Key Findings and Observations
        3. Potential Risks or Concerns (if any)
        4. Recommendations for Care
        5. Follow-up Actions
        
        Keep the summary professional, clear, and actionable for healthcare providers.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            summary = response.text
            print("[OK] Generated medical summary")
            return summary
        
        except Exception as e:
            print(f"[ERROR] Failed to generate summary: {e}")
            return "Summary generation failed."
    
    def generate_pdf_report(
        self, 
        output_path: str, 
        patient_data: Dict, 
        prediction: Optional[Dict], 
        summary: str,
        hospital_id: str = "Unknown"
    ):
        """
        Generate PDF report with analysis results
        
        Args:
            output_path: Path to save PDF report
            patient_data: Extracted patient data
            prediction: ML model prediction
            summary: Generated medical summary
            hospital_id: Hospital identifier
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1976d2'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            story.append(Paragraph("Medical Analysis Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Report metadata
            metadata = f"""
            <b>Hospital:</b> {hospital_id}<br/>
            <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Analysis Type:</b> AI-Powered Patient Data Analysis
            """
            story.append(Paragraph(metadata, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Patient Data Section
            story.append(Paragraph("Patient Data", heading_style))
            
            # Create table for patient data
            data_table = [["Field", "Value"]]
            for key, value in patient_data.items():
                data_table.append([key.replace('_', ' '), str(value)])
            
            table = Table(data_table, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # Prediction Section
            if prediction:
                story.append(Paragraph("AI Model Prediction", heading_style))
                pred_text = f"""
                <b>Predicted Position:</b> {prediction['predicted_class']}<br/>
                <b>Confidence Level:</b> {prediction['confidence']*100:.2f}%<br/>
                """
                story.append(Paragraph(pred_text, styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Medical Summary Section
            story.append(Paragraph("Medical Summary & Recommendations", heading_style))
            
            # Split summary into paragraphs
            for para in summary.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
            
            # Disclaimer
            story.append(Spacer(1, 0.3*inch))
            disclaimer = """
            <i><b>Disclaimer:</b> This report is generated using AI analysis and should be used as a 
            supplementary tool for medical professionals. It does not replace professional medical judgment 
            and clinical expertise. Always consult with qualified healthcare providers for medical decisions.</i>
            """
            story.append(Paragraph(disclaimer, styles['Italic']))
            
            # Build PDF
            doc.build(story)
            print(f"[OK] PDF report generated: {output_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to generate PDF report: {e}")
    
    def analyze_pdf_and_generate_report(
        self, 
        input_pdf_path: str, 
        output_pdf_path: str,
        hospital_id: str = "Unknown"
    ) -> Dict:
        """
        Complete workflow: Extract -> Parse -> Predict -> Summarize -> Generate Report
        
        Args:
            input_pdf_path: Path to input patient report PDF
            output_pdf_path: Path to save analysis report PDF
            hospital_id: Hospital identifier
            
        Returns:
            Dictionary with all analysis results
        """
        print(f"[INFO] Starting PDF analysis for {input_pdf_path}")
        
        # Step 1: Extract text from PDF
        text = self.extract_text_from_pdf(input_pdf_path)
        
        if not text:
            return {'error': 'Failed to extract text from PDF'}
        
        # Step 2: Parse patient data using Gemini AI
        patient_data = self.parse_patient_data(text)
        
        if not patient_data:
            return {'error': 'Failed to parse patient data'}
        
        # Step 3: Make prediction using ML model
        prediction = self.predict_from_data(patient_data)
        
        # Step 4: Generate medical summary using Gemini AI
        summary = self.generate_medical_summary(patient_data, prediction)
        
        # Step 5: Generate PDF report
        self.generate_pdf_report(
            output_pdf_path, 
            patient_data, 
            prediction, 
            summary,
            hospital_id
        )
        
        return {
            'patient_data': patient_data,
            'prediction': prediction,
            'summary': summary,
            'output_path': output_pdf_path
        }


if __name__ == "__main__":
    print("=" * 60)
    print("PDF ANALYZER - TEST")
    print("=" * 60)
    
    # Example usage
    api_key = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
    
    analyzer = PDFAnalyzer(
        gemini_api_key=api_key,
        model_path="checkpoints/global_model.pth",
        preprocessor_path="checkpoints"
    )
    
    print("\n[INFO] PDF Analyzer initialized")
    print("   Gemini AI: Configured")
    print("   ML Model: " + ("Loaded" if analyzer.ml_model else "Not loaded"))
    
    print("\n" + "=" * 60)

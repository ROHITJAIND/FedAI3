"""
Generate Sample Patient Report PDF for Testing
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

def create_sample_patient_report(output_path="sample_patient_report.pdf"):
    """Create a sample patient report PDF"""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = styles['Title']
    story.append(Paragraph("PATIENT MEDICAL REPORT", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Hospital Info
    story.append(Paragraph("<b>Hospital:</b> City Medical Center", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("<b>Report Type:</b> Prenatal Examination", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Patient Information
    story.append(Paragraph("<b>PATIENT INFORMATION</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    patient_data = [
        ["Patient Name:", "Sarah Johnson"],
        ["Patient ID:", "PT-2025-001234"],
        ["Age:", "28 years"],
        ["Blood Type:", "O+"],
        ["Contact:", "+1 (555) 123-4567"],
        ["Emergency Contact:", "+1 (555) 987-6543"]
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Medical Examination Details
    story.append(Paragraph("<b>PRENATAL EXAMINATION DETAILS</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    medical_data = [
        ["Gestational Age:", "32 weeks"],
        ["Baby Heartbeat:", "145 bpm"],
        ["Amniotic Fluid Level:", "12.5 cm"],
        ["Mother's Blood Pressure:", "118/76 mmHg"],
        ["Mother's Weight:", "68 kg"],
        ["Fundal Height:", "31 cm"],
        ["Baby Weight (estimated):", "1.8 kg"],
        ["Placenta Position:", "Anterior, Grade II"]
    ]
    
    medical_table = Table(medical_data, colWidths=[2.5*inch, 3.5*inch])
    medical_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(medical_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Clinical Observations
    story.append(Paragraph("<b>CLINICAL OBSERVATIONS</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    observations = """
    The patient is in her 32nd week of pregnancy. Ultrasound examination shows normal fetal development.
    Baby's heartbeat is strong and regular at 145 beats per minute, which is within the normal range.
    Amniotic fluid level is measured at 12.5 cm, indicating adequate fluid volume.
    Mother's vital signs are stable with no signs of complications.
    
    Fetal movement is active and regular. No abnormalities detected in the current examination.
    Patient reports feeling well with normal pregnancy symptoms for this stage.
    """
    story.append(Paragraph(observations, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph("<b>RECOMMENDATIONS</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    recommendations = """
    1. Continue prenatal vitamins and folic acid supplementation<br/>
    2. Maintain regular prenatal checkups every 2 weeks<br/>
    3. Monitor fetal movements daily<br/>
    4. Stay hydrated and maintain balanced nutrition<br/>
    5. Next ultrasound scheduled in 4 weeks<br/>
    6. Report any unusual symptoms immediately
    """
    story.append(Paragraph(recommendations, styles['Normal']))
    story.append(Spacer(1, 0.4*inch))
    
    # Doctor's signature
    story.append(Paragraph("_" * 40, styles['Normal']))
    story.append(Paragraph("<b>Dr. Emily Carter, MD</b>", styles['Normal']))
    story.append(Paragraph("Obstetrics & Gynecology Department", styles['Normal']))
    story.append(Paragraph("License No: MD-45678", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Sample patient report created: {output_path}")
    print(f"\n📋 Key data in the report:")
    print(f"   - Gestational Age: 32 weeks")
    print(f"   - Baby Heartbeat: 145 bpm")
    print(f"   - Amniotic Fluid Level: 12.5 cm")
    print(f"\n💡 Upload this PDF to test the AI analysis system!")

if __name__ == "__main__":
    create_sample_patient_report()

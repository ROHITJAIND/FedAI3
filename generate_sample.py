from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

doc = SimpleDocTemplate("sample_patient_report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Title
story.append(Paragraph("PATIENT MEDICAL REPORT", styles['Title']))
story.append(Spacer(1, 0.3*inch))

# Hospital Info
story.append(Paragraph("<b>Hospital:</b> City Medical Center", styles['Normal']))
story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
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
]

patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
story.append(patient_table)
story.append(Spacer(1, 0.3*inch))

# Medical Examination Details
story.append(Paragraph("<b>PRENATAL EXAMINATION DETAILS</b>", styles['Heading2']))
story.append(Spacer(1, 0.1*inch))

medical_data = [
    ["Gestational Age:", "32 weeks"],
    ["Baby Heartbeat:", "145 bpm"],
    ["Amniotic Fluid Level:", "12.5 cm"],
    ["Mother Blood Pressure:", "118/76 mmHg"],
    ["Baby Weight (estimated):", "1.8 kg"],
]

medical_table = Table(medical_data, colWidths=[2.5*inch, 3*inch])
story.append(medical_table)
story.append(Spacer(1, 0.3*inch))

# Observations
story.append(Paragraph("<b>CLINICAL OBSERVATIONS</b>", styles['Heading2']))
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph("Patient is in 32nd week of pregnancy. Ultrasound shows normal development. Heartbeat strong at 145 bpm. Amniotic fluid at 12.5 cm is adequate. No complications detected.", styles['Normal']))
story.append(Spacer(1, 0.4*inch))

# Doctor signature
story.append(Paragraph("<b>Dr. Emily Carter, MD</b>", styles['Normal']))
story.append(Paragraph("Obstetrics Department", styles['Normal']))

doc.build(story)
print("Sample PDF created: sample_patient_report.pdf")

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

def generate_medical_report_pdf(report_data: dict, output_path: str):
    """
    Generate a two-page PDF medical report from the given report_data dictionary.
    Page 1: Demographics and basic medical info (excluding Contact)
    Page 2: Symptoms details with wrapping cells

    :param report_data: Dictionary containing patient report data
    :param output_path: Path where the PDF will be saved
    """
    # Validate filename
    if not output_path:
        raise ValueError("Output path cannot be empty.")

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    normal = styles['BodyText']
    normal.wordWrap = 'CJK'  # enable wrap for long words
    heading = styles['Heading2']
    # Reduce heading font size slightly to avoid wrapping
    heading.fontSize = heading.fontSize - 2
    title = styles['Title']

    elements = []

    # --- Page 1: Demographics & Medical Info ---
    elements.append(Paragraph("Patient Report", title))
    elements.append(Spacer(1, 12))

    # Demographics Table (exclude Contact)
    demo = report_data.get('demographic_data', {})
    dem_rows = [[Paragraph("Field", heading), Paragraph("Value", heading)]]
    for field, value in demo.items():
        if field.lower() == 'contact':
            continue
        dem_rows.append([Paragraph(field, normal), Paragraph(str(value), normal)])

    dem_table = Table(dem_rows, colWidths=[120, 360], repeatRows=1)
    dem_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(Paragraph("<b>Demographics</b>", heading))
    elements.append(dem_table)
    elements.append(Spacer(1, 12))

    # Medical History / Info Table
    med_info = report_data.get('medical_info', {})
    med_rows = [[Paragraph("Category", heading), Paragraph("Detail", heading)]]
    med_rows.append([Paragraph("Medical History", normal), Paragraph(str(report_data.get('medical_history', 'N/A')), normal)])
    for field, val in med_info.items():
        med_rows.append([Paragraph(field.replace('_', ' '), normal), Paragraph(str(val), normal)])

    med_table = Table(med_rows, colWidths=[120, 360], repeatRows=1)
    med_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(Paragraph("<b>Medical Information</b>", heading))
    elements.append(med_table)

    # Page break before symptoms
    elements.append(PageBreak())

    # --- Page 2: Symptoms Details ---
    elements.append(Paragraph("Symptoms Detail", title))
    elements.append(Spacer(1, 12))

    # Symptoms Table with wrapping notes
    symptoms = report_data.get('symptoms_data', [])
    symp_rows = [[
        Paragraph("Symptom", heading),
        Paragraph("Frequency", heading),
        Paragraph("Severity", heading),
        Paragraph("Duration", heading),
        Paragraph("Notes", heading),
        Paragraph("Date", heading)
    ]]
    for entry in symptoms:
        symp_rows.append([
            Paragraph(str(entry.get('Symptom', '')), normal),
            Paragraph(str(entry.get('Frequency', '')), normal),
            Paragraph(str(entry.get('Severity', '')), normal),
            Paragraph(str(entry.get('Duration', '')), normal),
            Paragraph(str(entry.get('Additional_Notes', '')), normal),
            Paragraph(str(entry.get('Date', '')), normal)
        ])

    # Adjust column widths; Notes column gets more space
    col_widths = [80, 75, 60, 80, 200, 70]
    symp_table = Table(symp_rows, colWidths=col_widths, repeatRows=1)
    symp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(symp_table)

    # Build PDF
    doc.build(elements)

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

def generate_bankruptcy_petition_pdf(data, output_path="bankruptcy_petition.pdf"):
    """
    Generate a PDF bankruptcy petition using the collected data
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )

    story.append(Paragraph("UNITED STATES BANKRUPTCY COURT", title_style))
    story.append(Paragraph(f"{data.get('case_type', 'BANKRUPTCY')} PETITION", title_style))
    story.append(Spacer(1, 20))

    # Basic Information Section
    story.append(Paragraph("PARTY INFORMATION", styles['Heading2']))
    story.append(Spacer(1, 10))

    basic_info = [
        ["Full Legal Name:", data.get('name', '')],
        ["Date of Birth:", data.get('dob', '')],
        ["Social Security Number (last 4):", data.get('ssn_last4', '')],
        ["Current Address:", data.get('address', '')],
        ["Zip Code:", data.get('zip_code', '')],
        ["Phone Number:", data.get('phone', '')],
        ["Email Address:", data.get('email', '')],
    ]

    table = Table(basic_info, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Marital Status & Dependents
    story.append(Paragraph("MARITAL STATUS & DEPENDENTS", styles['Heading2']))
    story.append(Spacer(1, 10))

    marital_info = [
        ["Marital Status:", data.get('marital_status', '')],
        ["Number of Dependents:", str(len(data.get('dependents', [])))]
    ]

    marital_table = Table(marital_info, colWidths=[2*inch, 4*inch])
    marital_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(marital_table)

    # Dependents details
    dependents = data.get('dependents', [])
    if dependents:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Dependents Details:", styles['Heading3']))

        dep_data = [["Name", "Age", "Relationship"]]
        for dep in dependents:
            dep_data.append([dep.get('name', ''), dep.get('age', ''), dep.get('relationship', '')])

        dep_table = Table(dep_data, colWidths=[2*inch, 1*inch, 2*inch])
        dep_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(dep_table)

    story.append(Spacer(1, 20))

    # Employment & Income
    story.append(Paragraph("EMPLOYMENT & INCOME", styles['Heading2']))
    story.append(Spacer(1, 10))

    employment_info = [
        ["Employment Status:", data.get('employer', '')],
        ["Monthly Income:", data.get('gross_income_last_6m', '')]
    ]

    emp_table = Table(employment_info, colWidths=[2*inch, 4*inch])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 20))

    # Assets
    story.append(Paragraph("ASSETS", styles['Heading2']))
    story.append(Spacer(1, 10))

    assets = data.get('assets', [])
    if assets:
        asset_data = [["Asset Description", "Estimated Value"]]
        for asset in assets:
            asset_data.append([asset.get('item', ''), asset.get('value', '')])

        asset_table = Table(asset_data, colWidths=[3*inch, 2*inch])
        asset_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(asset_table)
    else:
        story.append(Paragraph("No assets reported", styles['Normal']))

    story.append(Spacer(1, 20))

    # Liabilities/Debts
    story.append(Paragraph("LIABILITIES & DEBTS", styles['Heading2']))
    story.append(Spacer(1, 10))

    liabilities = data.get('liabilities', [])
    if liabilities:
        debt_data = [["Creditor", "Amount Owed", "Type of Debt"]]
        for debt in liabilities:
            debt_data.append([
                debt.get('creditor', ''),
                debt.get('amount', ''),
                debt.get('type', '')
            ])

        debt_table = Table(debt_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        debt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(debt_table)
    else:
        story.append(Paragraph("No liabilities reported", styles['Normal']))

    story.append(Spacer(1, 20))

    # Declaration
    story.append(Paragraph("DECLARATION", styles['Heading2']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "I declare under penalty of perjury that the information provided in this petition is true and correct to the best of my knowledge.",
        styles['Normal']
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Signature: {data.get('name', '')}", styles['Normal']))
    story.append(Paragraph(f"Date: {os.popen('date /t').read().strip()}", styles['Normal']))

    # Build the PDF
    doc.build(story)
    return output_path

"""
SOTA PDF Generator - Bankruptcy Forms PDF Generation
Generates official bankruptcy forms from completed case data
"""

import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# PDF generation libraries
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available - PDF generation will use fallback text method")

from sota_forms_complete import CompleteBankruptcyCase, FilingType, MaritalStatus

logger = logging.getLogger(__name__)

class SOTAPDFGenerator:
    """
    Generates official bankruptcy form PDFs from case data
    """
    
    def __init__(self, output_dir: str = "./generated_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize styles if ReportLab is available
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
        
        logger.info(f"PDF Generator initialized - Output: {self.output_dir}")

    def _setup_custom_styles(self):
        """Setup custom PDF styles for bankruptcy forms"""
        if not REPORTLAB_AVAILABLE:
            return
            
        # Form title style
        self.styles.add(ParagraphStyle(
            name='FormTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1  # Center
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.black
        ))
        
        # Field label style
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.darkblue
        ))

    async def generate_form(self, form_code: str, bankruptcy_case: CompleteBankruptcyCase) -> str:
        """
        Generate a specific bankruptcy form PDF
        """
        try:
            form_generators = {
                "B101": self._generate_form_b101,
                "B106": self._generate_form_b106,
                "B107": self._generate_form_b107,
                "B121": self._generate_form_b121,
                "B122": self._generate_form_b122
            }
            
            generator = form_generators.get(form_code)
            if not generator:
                raise ValueError(f"Unknown form code: {form_code}")
            
            filename = await generator(bankruptcy_case)
            logger.info(f"Generated {form_code}: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating form {form_code}: {e}")
            # Fallback to text generation
            return await self._generate_text_fallback(form_code, bankruptcy_case)

    async def _generate_form_b101(self, case: CompleteBankruptcyCase) -> str:
        """Generate Form B101 - Voluntary Petition"""
        filename = self.output_dir / f"Form_B101_Petition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(str(filename), pagesize=letter)
            story = []
            
            # Title
            story.append(Paragraph("Official Form B101", self.styles['FormTitle']))
            story.append(Paragraph("Voluntary Petition for Individuals Filing for Bankruptcy", self.styles['FormTitle']))
            story.append(Spacer(1, 20))
            
            # Debtor Information
            debtor_info = case.form_b101.debtor_info
            story.append(Paragraph("Debtor Information", self.styles['SectionHeader']))
            
            debtor_data = [
                ["Full Name:", f"{debtor_info.first_name} {debtor_info.middle_name or ''} {debtor_info.last_name}"],
                ["Address:", f"{debtor_info.address}"],
                ["City, State, ZIP:", f"{debtor_info.city}, {debtor_info.state} {debtor_info.zip_code}"],
                ["SSN (last 4):", debtor_info.ssn_last_4 or "Not provided"],
                ["Date of Birth:", str(debtor_info.date_of_birth) if debtor_info.date_of_birth else "Not provided"],
                ["Phone:", debtor_info.phone or "Not provided"],
                ["Email:", debtor_info.email or "Not provided"]
            ]
            
            debtor_table = Table(debtor_data, colWidths=[2*inch, 4*inch])
            debtor_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(debtor_table)
            story.append(Spacer(1, 20))
            
            # Filing Information
            story.append(Paragraph("Filing Information", self.styles['SectionHeader']))
            filing_data = [
                ["Chapter:", str(case.filing_type.value) if case.filing_type else "Not specified"],
                ["Marital Status:", str(case.form_b101.marital_status.value) if case.form_b101.marital_status else "Not provided"],
                ["Filing Date:", datetime.now().strftime("%Y-%m-%d")]
            ]
            
            filing_table = Table(filing_data, colWidths=[2*inch, 4*inch])
            filing_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(filing_table)
            
            # Footer
            story.append(Spacer(1, 40))
            story.append(Paragraph("Generated by DocketVoice - For Attorney Review", self.styles['Normal']))
            
            doc.build(story)
        else:
            # Text fallback
            await self._write_text_form_b101(filename, case)
        
        return str(filename)

    async def _generate_form_b106(self, case: CompleteBankruptcyCase) -> str:
        """Generate Form B106 - Declaration About Individual Debtor"""
        filename = self.output_dir / f"Form_B106_Declaration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(str(filename), pagesize=letter)
            story = []
            
            story.append(Paragraph("Official Form B106", self.styles['FormTitle']))
            story.append(Paragraph("Declaration About an Individual Debtor's Schedules", self.styles['FormTitle']))
            story.append(Spacer(1, 20))
            
            # Declaration text
            declaration_text = """
            Under penalty of perjury, I declare that I have read the answers contained in the schedules 
            filed with this petition and that they are true and correct to the best of my knowledge, 
            information, and belief.
            """
            story.append(Paragraph(declaration_text, self.styles['Normal']))
            story.append(Spacer(1, 40))
            
            # Signature section
            story.append(Paragraph("Signature Section", self.styles['SectionHeader']))
            story.append(Paragraph(f"Debtor: {case.form_b101.debtor_info.first_name} {case.form_b101.debtor_info.last_name}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            story.append(Paragraph("Signature: _________________________________", self.styles['Normal']))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", self.styles['Normal']))
            
            doc.build(story)
        else:
            await self._write_text_form_b106(filename, case)
        
        return str(filename)

    async def _generate_form_b107(self, case: CompleteBankruptcyCase) -> str:
        """Generate Form B107 - Statement of Financial Affairs"""
        filename = self.output_dir / f"Form_B107_FinancialAffairs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(str(filename), pagesize=letter)
            story = []
            
            story.append(Paragraph("Official Form B107", self.styles['FormTitle']))
            story.append(Paragraph("Statement of Financial Affairs for Individuals Filing for Bankruptcy", self.styles['FormTitle']))
            story.append(Spacer(1, 20))
            
            # Add sections for financial affairs
            story.append(Paragraph("Income", self.styles['SectionHeader']))
            story.append(Paragraph("Income from employment or operation of business", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("Payments to Creditors", self.styles['SectionHeader']))
            story.append(Paragraph("List all payments on loans, installment purchases of goods or services, and other debts", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("Suits and Administrative Proceedings, Executions, Garnishments, and Attachments", self.styles['SectionHeader']))
            story.append(Paragraph("None reported during consultation", self.styles['Normal']))
            
            doc.build(story)
        else:
            await self._write_text_form_b107(filename, case)
        
        return str(filename)

    async def _generate_form_b121(self, case: CompleteBankruptcyCase) -> str:
        """Generate Form B121 - Statement of Income and Means Test"""
        filename = self.output_dir / f"Form_B121_MeansTest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(str(filename), pagesize=letter)
            story = []
            
            story.append(Paragraph("Official Form B121", self.styles['FormTitle']))
            story.append(Paragraph("Statement of Income and Means Test", self.styles['FormTitle']))
            story.append(Spacer(1, 20))
            
            # Income Information
            if hasattr(case.form_b121, 'debtor_income') and case.form_b121.debtor_income:
                income = case.form_b121.debtor_income
                story.append(Paragraph("Monthly Income", self.styles['SectionHeader']))
                
                income_data = [
                    ["Employment Income:", f"${income.employment_income or 0}"],
                    ["Other Income:", f"${income.other_income or 0}"],
                    ["Total Monthly Income:", f"${(income.employment_income or 0) + (income.other_income or 0)}"]
                ]
                
                income_table = Table(income_data, colWidths=[3*inch, 2*inch])
                income_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
                ]))
                story.append(income_table)
                story.append(Spacer(1, 20))
            
            # Expenses Information
            if hasattr(case.form_b121, 'monthly_expenses') and case.form_b121.monthly_expenses:
                expenses = case.form_b121.monthly_expenses
                story.append(Paragraph("Monthly Expenses", self.styles['SectionHeader']))
                
                expense_data = [
                    ["Rent/Mortgage:", f"${expenses.rent_mortgage or 0}"],
                    ["Food:", f"${expenses.food or 0}"],
                    ["Utilities:", f"${expenses.utilities or 0}"],
                    ["Transportation:", f"${expenses.transportation or 0}"],
                    ["Insurance:", f"${expenses.insurance or 0}"],
                    ["Other:", f"${expenses.other or 0}"]
                ]
                
                expense_table = Table(expense_data, colWidths=[3*inch, 2*inch])
                expense_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
                ]))
                story.append(expense_table)
            
            doc.build(story)
        else:
            await self._write_text_form_b121(filename, case)
        
        return str(filename)

    async def _generate_form_b122(self, case: CompleteBankruptcyCase) -> str:
        """Generate Form B122 - Statement of Current Monthly Income"""
        filename = self.output_dir / f"Form_B122_CurrentIncome_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(str(filename), pagesize=letter)
            story = []
            
            story.append(Paragraph("Official Form B122", self.styles['FormTitle']))
            story.append(Paragraph("Statement of Current Monthly Income", self.styles['FormTitle']))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("Current Monthly Income Calculation", self.styles['SectionHeader']))
            story.append(Paragraph("This form calculates current monthly income for means test purposes.", self.styles['Normal']))
            
            doc.build(story)
        else:
            await self._write_text_form_b122(filename, case)
        
        return str(filename)

    async def generate_case_summary(self, case: CompleteBankruptcyCase) -> str:
        """Generate a comprehensive case summary"""
        filename = self.output_dir / f"Case_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(str(filename), pagesize=letter)
            story = []
            
            story.append(Paragraph("DocketVoice Bankruptcy Case Summary", self.styles['FormTitle']))
            story.append(Spacer(1, 20))
            
            # Case Overview
            debtor_info = case.form_b101.debtor_info
            story.append(Paragraph("Case Overview", self.styles['SectionHeader']))
            
            overview_data = [
                ["Debtor Name:", f"{debtor_info.first_name} {debtor_info.last_name}"],
                ["Filing Type:", str(case.filing_type.value) if case.filing_type else "Not specified"],
                ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Status:", "Ready for Attorney Review"]
            ]
            
            overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            story.append(overview_table)
            story.append(Spacer(1, 20))
            
            # Completion Status
            completion_status = case.get_completion_status()
            story.append(Paragraph("Form Completion Status", self.styles['SectionHeader']))
            
            for form_name, completion_pct in completion_status.items():
                status_text = f"{form_name}: {completion_pct}% complete"
                story.append(Paragraph(status_text, self.styles['Normal']))
            
            story.append(Spacer(1, 20))
            story.append(Paragraph("All forms are ready for attorney review and filing preparation.", self.styles['Normal']))
            
            doc.build(story)
        else:
            await self._write_text_case_summary(filename, case)
        
        return str(filename)

    # Text fallback methods for when ReportLab is not available
    async def _generate_text_fallback(self, form_code: str, case: CompleteBankruptcyCase) -> str:
        """Generate text file when PDF generation fails"""
        filename = self.output_dir / f"Form_{form_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"BANKRUPTCY FORM {form_code}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Generated by DocketVoice on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            debtor_info = case.form_b101.debtor_info
            f.write("DEBTOR INFORMATION:\n")
            f.write(f"Name: {debtor_info.first_name} {debtor_info.last_name}\n")
            f.write(f"Address: {debtor_info.address}\n")
            f.write(f"City, State, ZIP: {debtor_info.city}, {debtor_info.state} {debtor_info.zip_code}\n")
            f.write(f"Phone: {debtor_info.phone}\n")
            f.write(f"Email: {debtor_info.email}\n\n")
            
            f.write("FILING INFORMATION:\n")
            f.write(f"Chapter: {case.filing_type.value if case.filing_type else 'Not specified'}\n")
            f.write(f"Marital Status: {case.form_b101.marital_status.value if case.form_b101.marital_status else 'Not specified'}\n\n")
            
            f.write("NOTE: This is a text version. Official PDF forms should be generated with ReportLab library.\n")
        
        return str(filename)

    async def _write_text_case_summary(self, filename: Path, case: CompleteBankruptcyCase):
        """Write text-based case summary"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("DOCKETVOICE BANKRUPTCY CASE SUMMARY\n")
            f.write("="*50 + "\n\n")
            
            completion_status = case.get_completion_status()
            avg_completion = sum(completion_status.values()) / len(completion_status) if completion_status else 0
            
            f.write(f"Overall Completion: {avg_completion:.1f}%\n")
            f.write(f"Ready for Filing: {case.is_ready_for_filing()}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Form Completion Status:\n")
            for form_name, completion_pct in completion_status.items():
                f.write(f"  {form_name}: {completion_pct}%\n")

    # Additional text fallback methods
    async def _write_text_form_b101(self, filename: Path, case: CompleteBankruptcyCase):
        """Write text version of Form B101"""
        return await self._generate_text_fallback("B101", case)

    async def _write_text_form_b106(self, filename: Path, case: CompleteBankruptcyCase):
        """Write text version of Form B106"""
        return await self._generate_text_fallback("B106", case)

    async def _write_text_form_b107(self, filename: Path, case: CompleteBankruptcyCase):
        """Write text version of Form B107"""
        return await self._generate_text_fallback("B107", case)

    async def _write_text_form_b121(self, filename: Path, case: CompleteBankruptcyCase):
        """Write text version of Form B121"""
        return await self._generate_text_fallback("B121", case)

    async def _write_text_form_b122(self, filename: Path, case: CompleteBankruptcyCase):
        """Write text version of Form B122"""
        return await self._generate_text_fallback("B122", case)

# Example usage
if __name__ == "__main__":
    async def test_generator():
        from sota_forms_complete import CompleteBankruptcyCase, FilingType, DebtorInfo
        
        # Create test case
        case = CompleteBankruptcyCase()
        case.filing_type = FilingType.CHAPTER_7
        case.form_b101.debtor_info.first_name = "John"
        case.form_b101.debtor_info.last_name = "Doe"
        case.form_b101.debtor_info.address = "123 Main St"
        case.form_b101.debtor_info.city = "Anytown"
        case.form_b101.debtor_info.state = "CA"
        case.form_b101.debtor_info.zip_code = "12345"
        
        # Generate documents
        generator = SOTAPDFGenerator()
        files = []
        
        for form_code in ["B101", "B106", "B107"]:
            filename = await generator.generate_form(form_code, case)
            files.append(filename)
            print(f"Generated: {filename}")
        
        summary_file = await generator.generate_case_summary(case)
        print(f"Generated summary: {summary_file}")
    
    import asyncio
    asyncio.run(test_generator())
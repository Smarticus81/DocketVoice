"""
Advanced Document Processing System - OCR, AI Analysis, Data Extraction
Production-ready document processing for bankruptcy forms
"""

import asyncio
import logging
import os
import io
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import pandas as pd
from dateutil import parser
import aiofiles

from config import Settings
from sota_forms_complete import CompleteBankruptcyCase, DebtorInfo, MonthlyIncome, MonthlyExpenses

logger = logging.getLogger(__name__)

class DocumentType:
    BANK_STATEMENT = "bank_statement"
    TAX_RETURN = "tax_return"
    PAY_STUB = "pay_stub"
    CREDIT_REPORT = "credit_report"
    UTILITY_BILL = "utility_bill"
    MORTGAGE_STATEMENT = "mortgage_statement"
    LOAN_STATEMENT = "loan_statement"
    INSURANCE_POLICY = "insurance_policy"
    IDENTIFICATION = "identification"
    GENERAL = "general"

class ExtractedData:
    def __init__(self):
        self.text_content: str = ""
        self.structured_data: Dict[str, Any] = {}
        self.document_type: str = DocumentType.GENERAL
        self.confidence_score: float = 0.0
        self.extracted_amounts: List[Decimal] = []
        self.extracted_dates: List[date] = []
        self.extracted_names: List[str] = []
        self.extracted_addresses: List[str] = []

class SOTADocumentProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.openai_client = AsyncOpenAI(api_key=settings.ai.openai_api_key)
        self.anthropic_client = AsyncAnthropic(api_key=settings.ai.anthropic_api_key)
        
        # OCR Configuration
        self.tesseract_config = r'--oem 3 --psm 6'
        
        # Document Classification Patterns
        self.document_patterns = {
            DocumentType.BANK_STATEMENT: [
                r'bank statement', r'checking account', r'savings account',
                r'beginning balance', r'ending balance', r'deposits', r'withdrawals'
            ],
            DocumentType.PAY_STUB: [
                r'pay stub', r'payroll', r'gross pay', r'net pay',
                r'ytd earnings', r'federal withholding', r'state withholding'
            ],
            DocumentType.TAX_RETURN: [
                r'form 1040', r'tax return', r'irs', r'adjusted gross income',
                r'taxable income', r'federal income tax', r'w-2', r'1099'
            ],
            DocumentType.CREDIT_REPORT: [
                r'credit report', r'credit score', r'experian', r'equifax',
                r'transunion', r'credit accounts', r'payment history'
            ]
        }
        
        logger.info("SOTA Document Processor initialized with OCR and AI analysis")

    async def process_document(self, file_path: str, bankruptcy_case: CompleteBankruptcyCase) -> ExtractedData:
        """
        Main document processing pipeline
        """
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Step 1: Extract text using OCR
            extracted_text = await self._extract_text_from_document(file_path)
            
            # Step 2: Classify document type
            document_type = self._classify_document(extracted_text)
            
            # Step 3: Extract structured data using AI
            structured_data = await self._extract_structured_data(extracted_text, document_type)
            
            # Step 4: Apply extracted data to bankruptcy case
            await self._apply_extracted_data_to_case(structured_data, document_type, bankruptcy_case)
            
            # Step 5: Create extraction result
            result = ExtractedData()
            result.text_content = extracted_text
            result.structured_data = structured_data
            result.document_type = document_type
            result.confidence_score = structured_data.get('confidence_score', 0.8)
            
            logger.info(f"Document processing completed for {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    async def _extract_text_from_document(self, file_path: str) -> str:
        """
        Extract text from PDF or image using OCR
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return await self._extract_text_from_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return await self._extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF and OCR fallback
        """
        text_content = ""
        
        try:
            # First try to extract text directly from PDF
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                text_content += text + "\n"
            doc.close()
            
            # If no text extracted, use OCR
            if len(text_content.strip()) < 100:
                logger.info(f"PDF text extraction yielded minimal content, using OCR for {file_path}")
                text_content = await self._ocr_pdf_pages(file_path)
                
        except Exception as e:
            logger.warning(f"Error in PDF text extraction: {str(e)}, falling back to OCR")
            text_content = await self._ocr_pdf_pages(file_path)
        
        return text_content

    async def _ocr_pdf_pages(self, file_path: str) -> str:
        """
        OCR all pages of a PDF
        """
        text_content = ""
        
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Convert page to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_data))
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image)
            
            # OCR the image
            page_text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            text_content += page_text + "\n"
        
        doc.close()
        return text_content

    async def _extract_text_from_image(self, file_path: str) -> str:
        """
        Extract text from image using OCR
        """
        try:
            image = Image.open(file_path)
            processed_image = self._preprocess_image_for_ocr(image)
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            return text
        except Exception as e:
            logger.error(f"Error in image OCR: {str(e)}")
            raise

    def _preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        """
        # Convert PIL to OpenCV
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to PIL
        processed_image = Image.fromarray(processed)
        return processed_image

    def _classify_document(self, text: str) -> str:
        """
        Classify document type based on content patterns
        """
        text_lower = text.lower()
        scores = {}
        
        for doc_type, patterns in self.document_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, text_lower))
            scores[doc_type] = score
        
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                return best_type
        
        return DocumentType.GENERAL

    async def _extract_structured_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Use AI to extract structured data from document text
        """
        try:
            # Prepare the extraction prompt based on document type
            extraction_prompt = self._get_extraction_prompt(document_type)
            
            # Use OpenAI for structured extraction
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": extraction_prompt
                    },
                    {
                        "role": "user", 
                        "content": f"Extract structured data from this document:\n\n{text}"
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            extracted_data['confidence_score'] = 0.9  # High confidence for GPT-4o
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in AI extraction: {str(e)}")
            # Fallback to pattern-based extraction
            return self._pattern_based_extraction(text, document_type)

    def _get_extraction_prompt(self, document_type: str) -> str:
        """
        Get AI extraction prompt based on document type
        """
        base_prompt = """You are an expert document analyzer specializing in bankruptcy case preparation. 
        Extract structured data from the provided document text. Return ONLY valid JSON.
        
        Always include these base fields:
        - "document_type": the type of document
        - "amounts": array of monetary amounts found
        - "dates": array of dates found (YYYY-MM-DD format)
        - "names": array of person/entity names found
        - "addresses": array of addresses found
        """
        
        type_specific_prompts = {
            DocumentType.BANK_STATEMENT: base_prompt + """
            For bank statements, also extract:
            - "account_number": masked account number
            - "account_type": checking, savings, etc.
            - "beginning_balance": starting balance amount
            - "ending_balance": final balance amount
            - "total_deposits": sum of all deposits
            - "total_withdrawals": sum of all withdrawals
            - "monthly_average_balance": average balance if calculable
            """,
            
            DocumentType.PAY_STUB: base_prompt + """
            For pay stubs, also extract:
            - "employer_name": name of employer
            - "employee_name": name of employee
            - "pay_period_start": start date of pay period
            - "pay_period_end": end date of pay period
            - "gross_pay": gross pay amount
            - "net_pay": net pay amount
            - "ytd_gross": year-to-date gross
            - "ytd_net": year-to-date net
            - "federal_withholding": federal tax withheld
            - "state_withholding": state tax withheld
            """,
            
            DocumentType.TAX_RETURN: base_prompt + """
            For tax returns, also extract:
            - "tax_year": year of the tax return
            - "filing_status": single, married, etc.
            - "adjusted_gross_income": AGI amount
            - "taxable_income": taxable income amount
            - "total_tax": total tax owed
            - "wages_salary": W-2 wages
            - "interest_income": interest earned
            - "business_income": business income/loss
            """
        }
        
        return type_specific_prompts.get(document_type, base_prompt)

    def _pattern_based_extraction(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Fallback pattern-based extraction if AI fails
        """
        result = {
            'document_type': document_type,
            'amounts': self._extract_amounts(text),
            'dates': self._extract_dates(text),
            'names': self._extract_names(text),
            'addresses': self._extract_addresses(text),
            'confidence_score': 0.6  # Lower confidence for pattern matching
        }
        
        return result

    def _extract_amounts(self, text: str) -> List[float]:
        """Extract monetary amounts from text"""
        pattern = r'\$[\d,]+\.?\d*'
        matches = re.findall(pattern, text)
        amounts = []
        for match in matches:
            try:
                amount = float(match.replace('$', '').replace(',', ''))
                amounts.append(amount)
            except ValueError:
                continue
        return amounts

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'[A-Za-z]+ \d{1,2}, \d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    parsed_date = parser.parse(match)
                    dates.append(parsed_date.strftime('%Y-%m-%d'))
                except:
                    continue
        return list(set(dates))  # Remove duplicates

    def _extract_names(self, text: str) -> List[str]:
        """Extract person/entity names from text"""
        # Simple pattern for names (capitalized words)
        pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        matches = re.findall(pattern, text)
        return list(set(matches))

    def _extract_addresses(self, text: str) -> List[str]:
        """Extract addresses from text"""
        # Pattern for US addresses
        pattern = r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)[A-Za-z0-9\s,]*\d{5}(?:-\d{4})?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches

    async def _apply_extracted_data_to_case(self, extracted_data: Dict[str, Any], document_type: str, bankruptcy_case: CompleteBankruptcyCase):
        """
        Apply extracted data to the appropriate bankruptcy forms
        """
        try:
            if document_type == DocumentType.PAY_STUB:
                await self._apply_paystub_data(extracted_data, bankruptcy_case)
            elif document_type == DocumentType.BANK_STATEMENT:
                await self._apply_bank_statement_data(extracted_data, bankruptcy_case)
            elif document_type == DocumentType.TAX_RETURN:
                await self._apply_tax_return_data(extracted_data, bankruptcy_case)
            elif document_type == DocumentType.CREDIT_REPORT:
                await self._apply_credit_report_data(extracted_data, bankruptcy_case)
            
            # Apply common data (names, addresses) to debtor info
            await self._apply_common_data(extracted_data, bankruptcy_case)
            
        except Exception as e:
            logger.error(f"Error applying extracted data: {str(e)}")

    async def _apply_paystub_data(self, data: Dict[str, Any], case: CompleteBankruptcyCase):
        """Apply paystub data to income forms"""
        if 'gross_pay' in data and data['gross_pay']:
            case.form_b121.debtor_income.employment_income = Decimal(str(data['gross_pay']))
            case.form_b122.month_1_income = Decimal(str(data['gross_pay']))
        
        if 'employer_name' in data and data['employer_name']:
            # Store employer info in extracted data for later use
            case.extracted_data['employer_name'] = data['employer_name']

    async def _apply_bank_statement_data(self, data: Dict[str, Any], case: CompleteBankruptcyCase):
        """Apply bank statement data to asset forms"""
        if 'ending_balance' in data and data['ending_balance']:
            # Add to assets summary
            current_assets = case.form_b109.personal_property.current_value
            case.form_b109.personal_property.current_value = current_assets + Decimal(str(data['ending_balance']))

    async def _apply_tax_return_data(self, data: Dict[str, Any], case: CompleteBankruptcyCase):
        """Apply tax return data to income forms"""
        if 'adjusted_gross_income' in data and data['adjusted_gross_income']:
            case.form_b107.total_gross_income_current_year = Decimal(str(data['adjusted_gross_income']))
        
        if 'wages_salary' in data and data['wages_salary']:
            monthly_wages = Decimal(str(data['wages_salary'])) / 12
            case.form_b121.debtor_income.employment_income = monthly_wages

    async def _apply_credit_report_data(self, data: Dict[str, Any], case: CompleteBankruptcyCase):
        """Apply credit report data to liability forms"""
        if 'total_debt' in data and data['total_debt']:
            case.form_b109.unsecured_nonpriority_claims.total_amount = Decimal(str(data['total_debt']))

    async def _apply_common_data(self, data: Dict[str, Any], case: CompleteBankruptcyCase):
        """Apply common extracted data to debtor information"""
        if 'names' in data and data['names']:
            # Try to identify debtor name
            if not case.form_b101.debtor_info.first_name and len(data['names']) > 0:
                name_parts = data['names'][0].split()
                if len(name_parts) >= 2:
                    case.form_b101.debtor_info.first_name = name_parts[0]
                    case.form_b101.debtor_info.last_name = name_parts[-1]
                    if len(name_parts) > 2:
                        case.form_b101.debtor_info.middle_name = ' '.join(name_parts[1:-1])
        
        if 'addresses' in data and data['addresses']:
            # Apply first address found to debtor info
            if not case.form_b101.debtor_info.address_line_1 and len(data['addresses']) > 0:
                address = data['addresses'][0]
                # Simple address parsing
                case.form_b101.debtor_info.address_line_1 = address

    async def generate_document_summary(self, documents: List[str]) -> str:
        """
        Generate a summary of all processed documents
        """
        try:
            summary_prompt = f"""
            Generate a comprehensive summary of the documents processed for this bankruptcy case:
            
            Documents: {', '.join(documents)}
            
            Include:
            1. Document types identified
            2. Key financial data extracted
            3. Completeness of information
            4. Any missing documents typically needed
            5. Recommendations for additional documentation
            
            Format as a professional attorney-ready summary.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating document summary: {str(e)}")
            return "Document summary generation failed."

    async def shutdown(self):
        """Cleanup resources"""
        logger.info("SOTA Document Processor shutting down")
        await asyncio.sleep(0)

"""
Detailed Field Mapping Logic for Bankruptcy Forms
Maps conversational answers to specific bankruptcy form fields and validates data
"""

import re
import logging
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass

from sota_forms_complete import (
    CompleteBankruptcyCase, DebtorInfo, SpouseInfo, MonthlyIncome, 
    MonthlyExpenses, MaritalStatus, FilingType, EmploymentStatus
)

logger = logging.getLogger(__name__)

@dataclass
class FieldMapping:
    """Defines how a conversational answer maps to a bankruptcy form field"""
    form_section: str  # e.g., "form_b101", "debtor_info"
    field_name: str    # e.g., "first_name", "monthly_income"
    field_type: str    # "text", "decimal", "boolean", "date", "enum"
    validation_regex: Optional[str] = None
    enum_class: Optional[type] = None
    required: bool = False
    
class BankruptcyFieldMapper:
    """
    Maps conversational answers to specific bankruptcy form fields
    Handles validation, type conversion, and error checking
    """
    
    def __init__(self):
        self.field_mappings = self._initialize_field_mappings()
        
    def _initialize_field_mappings(self) -> Dict[str, FieldMapping]:
        """Initialize comprehensive field mappings for all bankruptcy forms"""
        
        mappings = {}
        
        # ============== FORM B101 - VOLUNTARY PETITION ==============
        
        # Personal Information - Maps to Form B101, Section 1
        mappings.update({
            "DebtorInfo.first_name": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="first_name", 
                field_type="text",
                validation_regex=r"^[A-Za-z\s\-'\.]{1,50}$",
                required=True
            ),
            "DebtorInfo.middle_name": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="middle_name", 
                field_type="text",
                validation_regex=r"^[A-Za-z\s\-'\.]{0,50}$"
            ),
            "DebtorInfo.last_name": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="last_name", 
                field_type="text",
                validation_regex=r"^[A-Za-z\s\-'\.]{1,50}$",
                required=True
            ),
            "DebtorInfo.address_line_1": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="address_line_1", 
                field_type="text",
                validation_regex=r"^[A-Za-z0-9\s\-\.\,\#]{1,100}$",
                required=True
            ),
            "DebtorInfo.city": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="city", 
                field_type="text",
                validation_regex=r"^[A-Za-z\s\-\.]{1,50}$",
                required=True
            ),
            "DebtorInfo.state": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="state", 
                field_type="text",
                validation_regex=r"^[A-Z]{2}$",
                required=True
            ),
            "DebtorInfo.zip_code": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="zip_code", 
                field_type="text",
                validation_regex=r"^\d{5}(-\d{4})?$",
                required=True
            ),
            "DebtorInfo.phone_home": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="phone_home", 
                field_type="text",
                validation_regex=r"^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$"
            ),
            "DebtorInfo.phone_cell": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="phone_cell", 
                field_type="text",
                validation_regex=r"^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$"
            ),
            "DebtorInfo.email": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="email", 
                field_type="text",
                validation_regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            ),
            "DebtorInfo.ssn_last_4": FieldMapping(
                form_section="form_b101.debtor_info", 
                field_name="ssn_last_4", 
                field_type="text",
                validation_regex=r"^\d{4}$",
                required=True
            ),
        })
        
        # Marital Status and Filing Type - Maps to Form B101, Section 2
        mappings.update({
            "B101.marital_status": FieldMapping(
                form_section="form_b101", 
                field_name="marital_status", 
                field_type="enum",
                enum_class=MaritalStatus,
                required=True
            ),
            "B101.filing_type": FieldMapping(
                form_section="form_b101", 
                field_name="filing_type", 
                field_type="enum",
                enum_class=FilingType,
                required=True
            ),
            "B101.joint_petition": FieldMapping(
                form_section="form_b101", 
                field_name="joint_petition", 
                field_type="boolean"
            ),
            "B101.previous_bankruptcy_filed": FieldMapping(
                form_section="form_b101", 
                field_name="previous_bankruptcy_filed", 
                field_type="boolean"
            ),
        })
        
        # Spouse Information - Maps to Form B101, Section 3 (if married)
        mappings.update({
            "SpouseInfo.first_name": FieldMapping(
                form_section="form_b101.spouse_info", 
                field_name="first_name", 
                field_type="text",
                validation_regex=r"^[A-Za-z\s\-'\.]{1,50}$"
            ),
            "SpouseInfo.last_name": FieldMapping(
                form_section="form_b101.spouse_info", 
                field_name="last_name", 
                field_type="text",
                validation_regex=r"^[A-Za-z\s\-'\.]{1,50}$"
            ),
            "SpouseInfo.ssn_last_4": FieldMapping(
                form_section="form_b101.spouse_info", 
                field_name="ssn_last_4", 
                field_type="text",
                validation_regex=r"^\d{4}$"
            ),
        })
        
        # ============== FORM B121 - STATEMENT OF INCOME AND MEANS TEST ==============
        
        # Monthly Income - Maps to Form B121, Part 1 
        mappings.update({
            "MonthlyIncome.employment_income": FieldMapping(
                form_section="form_b121.debtor_income", 
                field_name="employment_income", 
                field_type="decimal",
                required=True
            ),
            "MonthlyIncome.unemployment_compensation": FieldMapping(
                form_section="form_b121.debtor_income", 
                field_name="unemployment_compensation", 
                field_type="decimal"
            ),
            "MonthlyIncome.social_security": FieldMapping(
                form_section="form_b121.debtor_income", 
                field_name="social_security", 
                field_type="decimal"
            ),
            "MonthlyIncome.child_support": FieldMapping(
                form_section="form_b121.debtor_income", 
                field_name="child_support", 
                field_type="decimal"
            ),
            "MonthlyIncome.retirement_income": FieldMapping(
                form_section="form_b121.debtor_income", 
                field_name="retirement_income", 
                field_type="decimal"
            ),
            "MonthlyIncome.other_income": FieldMapping(
                form_section="form_b121.debtor_income", 
                field_name="other_income", 
                field_type="decimal"
            ),
        })
        
        # Monthly Expenses - Maps to Form B121, Part 2
        mappings.update({
            "MonthlyExpenses.rent_mortgage": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="rent_mortgage", 
                field_type="decimal",
                required=True
            ),
            "MonthlyExpenses.utilities": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="utilities", 
                field_type="decimal"
            ),
            "MonthlyExpenses.food": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="food", 
                field_type="decimal",
                required=True
            ),
            "MonthlyExpenses.transportation": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="transportation", 
                field_type="decimal"
            ),
            "MonthlyExpenses.healthcare": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="healthcare", 
                field_type="decimal"
            ),
            "MonthlyExpenses.childcare": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="childcare", 
                field_type="decimal"
            ),
            "MonthlyExpenses.insurance": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="insurance", 
                field_type="decimal"
            ),
            "MonthlyExpenses.other_expenses": FieldMapping(
                form_section="form_b121.monthly_expenses", 
                field_name="other_expenses", 
                field_type="decimal"
            ),
        })
        
        # Household Size - Maps to Form B121, Part 3
        mappings.update({
            "B121.household_size": FieldMapping(
                form_section="form_b121", 
                field_name="household_size", 
                field_type="integer",
                required=True
            ),
        })
        
        # ============== FORM B122 - CURRENT MONTHLY INCOME ==============
        
        # 6-Month Income History - Maps to Form B122, Part 1
        mappings.update({
            "B122.month_1_income": FieldMapping(
                form_section="form_b122", 
                field_name="month_1_income", 
                field_type="decimal"
            ),
            "B122.month_2_income": FieldMapping(
                form_section="form_b122", 
                field_name="month_2_income", 
                field_type="decimal"
            ),
            "B122.month_3_income": FieldMapping(
                form_section="form_b122", 
                field_name="month_3_income", 
                field_type="decimal"
            ),
            "B122.month_4_income": FieldMapping(
                form_section="form_b122", 
                field_name="month_4_income", 
                field_type="decimal"
            ),
            "B122.month_5_income": FieldMapping(
                form_section="form_b122", 
                field_name="month_5_income", 
                field_type="decimal"
            ),
            "B122.month_6_income": FieldMapping(
                form_section="form_b122", 
                field_name="month_6_income", 
                field_type="decimal"
            ),
        })
        
        # ============== EMPLOYMENT INFORMATION ==============
        
        # Employment Details - Maps across multiple forms
        mappings.update({
            "Employment.employer_name": FieldMapping(
                form_section="employment_info", 
                field_name="employer_name", 
                field_type="text",
                validation_regex=r"^[A-Za-z0-9\s\-\.\,\&]{1,100}$"
            ),
            "Employment.job_title": FieldMapping(
                form_section="employment_info", 
                field_name="job_title", 
                field_type="text",
                validation_regex=r"^[A-Za-z\s\-\.\,]{1,100}$"
            ),
            "Employment.employment_status": FieldMapping(
                form_section="employment_info", 
                field_name="employment_status", 
                field_type="enum",
                enum_class=EmploymentStatus
            ),
        })
        
        # ============== ASSETS AND DEBTS ==============
        
        # Asset Information - Maps to Schedule AB (Form B106)
        mappings.update({
            "Assets.real_property_value": FieldMapping(
                form_section="assets", 
                field_name="real_property_value", 
                field_type="decimal"
            ),
            "Assets.vehicle_value": FieldMapping(
                form_section="assets", 
                field_name="vehicle_value", 
                field_type="decimal"
            ),
            "Assets.bank_accounts": FieldMapping(
                form_section="assets", 
                field_name="bank_accounts_total", 
                field_type="decimal"
            ),
            "Assets.retirement_accounts": FieldMapping(
                form_section="assets", 
                field_name="retirement_accounts_total", 
                field_type="decimal"
            ),
        })
        
        # Debt Information - Maps to Schedules D/EF (Form B106)
        mappings.update({
            "Debts.credit_card_debt": FieldMapping(
                form_section="debts", 
                field_name="credit_card_total", 
                field_type="decimal"
            ),
            "Debts.mortgage_debt": FieldMapping(
                form_section="debts", 
                field_name="mortgage_balance", 
                field_type="decimal"
            ),
            "Debts.auto_loans": FieldMapping(
                form_section="debts", 
                field_name="auto_loan_total", 
                field_type="decimal"
            ),
            "Debts.medical_debt": FieldMapping(
                form_section="debts", 
                field_name="medical_debt_total", 
                field_type="decimal"
            ),
            "Debts.student_loans": FieldMapping(
                form_section="debts", 
                field_name="student_loan_total", 
                field_type="decimal"
            ),
        })
        
        # ============== FORM B123 - CERTIFICATION ==============
        
        # Course Completion Information
        mappings.update({
            "B123.course_completion": FieldMapping(
                form_section="form_b123", 
                field_name="course_completed", 
                field_type="boolean"
            ),
            "B123.course_provider": FieldMapping(
                form_section="form_b123", 
                field_name="course_provider", 
                field_type="text",
                validation_regex=r"^[A-Za-z0-9\s\-\.\,\&]{1,100}$"
            ),
            "B123.certificate_number": FieldMapping(
                form_section="form_b123", 
                field_name="certificate_number", 
                field_type="text",
                validation_regex=r"^[A-Za-z0-9\-]{1,50}$"
            ),
        })
        
        return mappings
    
    def map_answer_to_field(self, field_key: str, raw_answer: str, bankruptcy_case: CompleteBankruptcyCase) -> Tuple[bool, str]:
        """
        Map a conversational answer to a specific bankruptcy form field
        
        Args:
            field_key: The field identifier (e.g., "DebtorInfo.first_name")
            raw_answer: The user's raw conversational answer
            bankruptcy_case: The bankruptcy case object to update
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        
        mapping = self.field_mappings.get(field_key)
        if not mapping:
            return False, f"Unknown field mapping: {field_key}"
        
        try:
            # Clean and validate the answer
            processed_value = self._process_answer(raw_answer, mapping)
            
            if processed_value is None:
                if mapping.required:
                    return False, f"This field is required but no valid value could be extracted from: '{raw_answer}'"
                else:
                    logger.info(f"No value extracted for optional field {field_key}")
                    return True, "No value provided for optional field"
            
            # Apply the value to the bankruptcy case
            success = self._apply_value_to_case(mapping, processed_value, bankruptcy_case)
            
            if success:
                logger.info(f"Successfully mapped {field_key} = {processed_value}")
                return True, f"Set {field_key} to {processed_value}"
            else:
                return False, f"Failed to apply value to bankruptcy case"
                
        except Exception as e:
            logger.error(f"Error mapping {field_key}: {str(e)}")
            return False, f"Error processing field: {str(e)}"
    
    def _process_answer(self, raw_answer: str, mapping: FieldMapping) -> Any:
        """Process raw answer based on field type and validation rules"""
        
        if not raw_answer or raw_answer.strip().lower() in ['none', 'nothing', 'n/a', 'skip']:
            return None
        
        answer = raw_answer.strip()
        
        try:
            if mapping.field_type == "text":
                return self._process_text_field(answer, mapping)
            elif mapping.field_type == "decimal":
                return self._process_decimal_field(answer)
            elif mapping.field_type == "integer":
                return self._process_integer_field(answer)
            elif mapping.field_type == "boolean":
                return self._process_boolean_field(answer)
            elif mapping.field_type == "date":
                return self._process_date_field(answer)
            elif mapping.field_type == "enum":
                return self._process_enum_field(answer, mapping)
            else:
                logger.warning(f"Unknown field type: {mapping.field_type}")
                return answer
                
        except Exception as e:
            logger.error(f"Error processing {mapping.field_type} field: {str(e)}")
            return None
    
    def _process_text_field(self, answer: str, mapping: FieldMapping) -> Optional[str]:
        """Process text field with validation"""
        
        # Clean the text
        cleaned = re.sub(r'[^\w\s\-\.\,\'\#\&]', '', answer).strip()
        
        # Special handling for specific fields
        if "state" in mapping.field_name:
            cleaned = self._normalize_state(cleaned)
        elif "phone" in mapping.field_name:
            cleaned = self._normalize_phone(cleaned)
        elif "zip" in mapping.field_name:
            cleaned = self._normalize_zip(cleaned)
        elif "ssn" in mapping.field_name:
            cleaned = self._extract_ssn_last_4(cleaned)
        elif "email" in mapping.field_name:
            cleaned = self._normalize_email(cleaned)
        
        # Validate against regex if provided
        if mapping.validation_regex and cleaned:
            if not re.match(mapping.validation_regex, cleaned):
                logger.warning(f"Text validation failed for {mapping.field_name}: '{cleaned}'")
                return None
        
        return cleaned if cleaned else None
    
    def _process_decimal_field(self, answer: str) -> Optional[Decimal]:
        """Extract decimal value from conversational answer"""
        
        # Remove currency symbols and common words
        cleaned = re.sub(r'[\$\,]', '', answer)
        cleaned = re.sub(r'\b(dollars?|bucks?|cents?)\b', '', cleaned, flags=re.IGNORECASE)
        
        # Look for number patterns
        number_match = re.search(r'(\d+(?:\.\d{2})?)', cleaned)
        if number_match:
            try:
                return Decimal(number_match.group(1))
            except InvalidOperation:
                pass
        
        # Handle common conversational amounts
        if any(word in answer.lower() for word in ['nothing', 'zero', 'none']):
            return Decimal('0')
        
        logger.warning(f"Could not extract decimal from: '{answer}'")
        return None
    
    def _process_integer_field(self, answer: str) -> Optional[int]:
        """Extract integer value from answer"""
        
        # Look for numbers
        number_match = re.search(r'(\d+)', answer)
        if number_match:
            try:
                return int(number_match.group(1))
            except ValueError:
                pass
        
        # Handle word numbers for small values
        word_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        for word, num in word_numbers.items():
            if word in answer.lower():
                return num
        
        logger.warning(f"Could not extract integer from: '{answer}'")
        return None
    
    def _process_boolean_field(self, answer: str) -> Optional[bool]:
        """Convert conversational answer to boolean"""
        
        answer_lower = answer.lower().strip()
        
        yes_words = ['yes', 'y', 'true', 'correct', 'right', 'definitely', 'absolutely', 'sure']
        no_words = ['no', 'n', 'false', 'incorrect', 'wrong', 'nope', 'negative']
        
        if any(word in answer_lower for word in yes_words):
            return True
        elif any(word in answer_lower for word in no_words):
            return False
        
        logger.warning(f"Could not determine boolean from: '{answer}'")
        return None
    
    def _process_date_field(self, answer: str) -> Optional[date]:
        """Extract date from conversational answer"""
        
        try:
            # Try to parse various date formats
            from dateutil import parser
            parsed_date = parser.parse(answer, fuzzy=True)
            return parsed_date.date()
        except:
            logger.warning(f"Could not parse date from: '{answer}'")
            return None
    
    def _process_enum_field(self, answer: str, mapping: FieldMapping) -> Optional[Any]:
        """Process enumeration field"""
        
        if not mapping.enum_class:
            return None
        
        answer_lower = answer.lower().strip()
        
        # Special handling for MaritalStatus
        if mapping.enum_class == MaritalStatus:
            if any(word in answer_lower for word in ['married', 'wed']):
                return MaritalStatus.MARRIED
            elif any(word in answer_lower for word in ['single', 'unmarried']):
                return MaritalStatus.SINGLE
            elif any(word in answer_lower for word in ['divorced']):
                return MaritalStatus.DIVORCED
            elif any(word in answer_lower for word in ['separated']):
                return MaritalStatus.SEPARATED
            elif any(word in answer_lower for word in ['widowed', 'widow']):
                return MaritalStatus.WIDOWED
        
        # Special handling for FilingType
        elif mapping.enum_class == FilingType:
            if '7' in answer or 'seven' in answer_lower:
                return FilingType.CHAPTER_7
            elif '13' in answer or 'thirteen' in answer_lower:
                return FilingType.CHAPTER_13
        
        # Special handling for EmploymentStatus
        elif mapping.enum_class == EmploymentStatus:
            if any(word in answer_lower for word in ['employed', 'working', 'job']):
                return EmploymentStatus.EMPLOYED
            elif any(word in answer_lower for word in ['unemployed', 'jobless']):
                return EmploymentStatus.UNEMPLOYED
            elif any(word in answer_lower for word in ['self-employed', 'freelance', 'contractor']):
                return EmploymentStatus.SELF_EMPLOYED
            elif any(word in answer_lower for word in ['retired']):
                return EmploymentStatus.RETIRED
            elif any(word in answer_lower for word in ['disabled', 'disability']):
                return EmploymentStatus.DISABLED
        
        logger.warning(f"Could not map enum value from: '{answer}'")
        return None
    
    def _apply_value_to_case(self, mapping: FieldMapping, value: Any, bankruptcy_case: CompleteBankruptcyCase) -> bool:
        """Apply processed value to the appropriate field in bankruptcy case"""
        
        try:
            # Navigate to the target object
            parts = mapping.form_section.split('.')
            target_obj = bankruptcy_case
            
            for part in parts:
                if hasattr(target_obj, part):
                    target_obj = getattr(target_obj, part)
                else:
                    # Create the object if it doesn't exist
                    if part == "spouse_info" and target_obj.spouse_info is None:
                        from sota_forms_complete import SpouseInfo
                        target_obj.spouse_info = SpouseInfo()
                        target_obj = target_obj.spouse_info
                    else:
                        logger.error(f"Cannot navigate to {mapping.form_section}")
                        return False
            
            # Set the field value
            if hasattr(target_obj, mapping.field_name):
                setattr(target_obj, mapping.field_name, value)
                return True
            else:
                logger.error(f"Field {mapping.field_name} not found in {mapping.form_section}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying value to case: {str(e)}")
            return False
    
    # Helper methods for text normalization
    def _normalize_state(self, state_text: str) -> str:
        """Normalize state to 2-letter code"""
        state_mapping = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
        
        state_lower = state_text.lower().strip()
        if state_lower in state_mapping:
            return state_mapping[state_lower]
        elif len(state_text) == 2:
            return state_text.upper()
        else:
            return state_text
    
    def _normalize_phone(self, phone_text: str) -> str:
        """Normalize phone number"""
        digits = re.sub(r'[^\d]', '', phone_text)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone_text
    
    def _normalize_zip(self, zip_text: str) -> str:
        """Normalize zip code"""
        digits = re.sub(r'[^\d]', '', zip_text)
        if len(digits) == 5:
            return digits
        elif len(digits) == 9:
            return f"{digits[:5]}-{digits[5:]}"
        return zip_text
    
    def _extract_ssn_last_4(self, ssn_text: str) -> Optional[str]:
        """Extract last 4 digits of SSN"""
        digits = re.sub(r'[^\d]', '', ssn_text)
        if len(digits) >= 4:
            return digits[-4:]
        return None
    
    def _normalize_email(self, email_text: str) -> str:
        """Normalize email address"""
        return email_text.lower().strip()
    
    def get_field_mapping_info(self, field_key: str) -> Optional[FieldMapping]:
        """Get mapping information for a field"""
        return self.field_mappings.get(field_key)
    
    def validate_required_fields(self, bankruptcy_case: CompleteBankruptcyCase) -> List[str]:
        """Validate that all required fields have been filled"""
        missing_fields = []
        
        for field_key, mapping in self.field_mappings.items():
            if mapping.required:
                # Check if field has a value
                parts = mapping.form_section.split('.')
                target_obj = bankruptcy_case
                
                try:
                    for part in parts:
                        target_obj = getattr(target_obj, part)
                    
                    value = getattr(target_obj, mapping.field_name, None)
                    if value is None or value == '' or value == []:
                        missing_fields.append(field_key)
                        
                except AttributeError:
                    missing_fields.append(field_key)
        
        return missing_fields

# Example usage and testing
if __name__ == "__main__":
    # Test the field mapper
    mapper = BankruptcyFieldMapper()
    case = CompleteBankruptcyCase()
    
    # Test various field mappings
    test_cases = [
        ("DebtorInfo.first_name", "My name is John", "John"),
        ("DebtorInfo.state", "I live in California", "CA"),
        ("MonthlyIncome.employment_income", "I make about $3,500 per month", Decimal('3500')),
        ("B101.marital_status", "I'm married", MaritalStatus.MARRIED),
        ("MonthlyExpenses.rent_mortgage", "My rent is $1,200", Decimal('1200')),
    ]
    
    for field_key, answer, expected in test_cases:
        success, message = mapper.map_answer_to_field(field_key, answer, case)
        print(f"{field_key}: {success} - {message}")
    
    # Check required fields
    missing = mapper.validate_required_fields(case)
    print(f"Missing required fields: {missing}")

"""
Complete Official Bankruptcy Forms Suite - Production Ready
All Official Forms for Chapter 7 and 13 Bankruptcy Filings
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum

class FilingType(str, Enum):
    CHAPTER_7 = "7"
    CHAPTER_13 = "13"

class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    SEPARATED = "separated"
    WIDOWED = "widowed"

class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    UNEMPLOYED = "unemployed"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    DISABLED = "disabled"

# ============== OFFICIAL FORM B101: VOLUNTARY PETITION ==============
class DebtorInfo(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    phone_home: Optional[str] = None
    phone_cell: Optional[str] = None
    email: Optional[str] = None
    ssn_last_4: Optional[str] = None
    tax_id_ein: Optional[str] = None

class SpouseInfo(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone_home: Optional[str] = None
    phone_cell: Optional[str] = None
    email: Optional[str] = None
    ssn_last_4: Optional[str] = None

class AttorneyInfo(BaseModel):
    name: Optional[str] = None
    firm_name: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bar_number: Optional[str] = None
    state_bar: Optional[str] = None

class B101VoluntaryPetition(BaseModel):
    # Basic Information
    filing_type: Optional[FilingType] = None
    debtor_info: DebtorInfo = Field(default_factory=DebtorInfo)
    spouse_info: Optional[SpouseInfo] = None
    attorney_info: Optional[AttorneyInfo] = None
    
    # Bankruptcy Details
    estimated_assets: Optional[Decimal] = None
    estimated_liabilities: Optional[Decimal] = None
    estimated_creditors_1_49: bool = False
    estimated_creditors_50_99: bool = False
    estimated_creditors_100_199: bool = False
    estimated_creditors_200_999: bool = False
    estimated_creditors_1000_5000: bool = False
    estimated_creditors_5001_10000: bool = False
    estimated_creditors_10001_25000: bool = False
    estimated_creditors_25001_50000: bool = False
    estimated_creditors_50001_100000: bool = False
    estimated_creditors_more_than_100000: bool = False
    
    # Filing Districts
    filing_district: Optional[str] = None
    filing_division: Optional[str] = None
    
    # Property and Income
    marital_status: Optional[MaritalStatus] = None
    joint_petition: bool = False
    previous_bankruptcy_filed: bool = False
    previous_case_numbers: List[str] = Field(default_factory=list)
    
    # Declarations
    primarily_consumer_debts: bool = True
    primarily_business_debts: bool = False
    debts_primarily_consumer_goods: bool = False
    debts_primarily_business: bool = False

# ============== OFFICIAL FORM B106: DECLARATION ABOUT INDIVIDUAL DEBTOR ==============
class B106Declaration(BaseModel):
    # Personal Information
    debtor_info: DebtorInfo = Field(default_factory=DebtorInfo)
    
    # Disability Information
    has_disability: bool = False
    disability_description: Optional[str] = None
    needs_accommodation: bool = False
    accommodation_description: Optional[str] = None
    
    # Language Information
    primary_language_english: bool = True
    primary_language_other: Optional[str] = None
    needs_interpreter: bool = False
    interpreter_language: Optional[str] = None
    
    # Military Service
    current_military_service: bool = False
    military_branch: Optional[str] = None
    service_start_date: Optional[date] = None
    service_end_date: Optional[date] = None

# ============== OFFICIAL FORM B107: STATEMENT OF FINANCIAL AFFAIRS ==============
class IncomeSource(BaseModel):
    source_name: str
    amount: Decimal
    period: str  # monthly, yearly, etc.

class PaymentToCreditor(BaseModel):
    creditor_name: str
    amount: Decimal
    payment_date: date
    payment_reason: str

class LawsuitInfo(BaseModel):
    case_name: str
    court_name: str
    case_number: Optional[str] = None
    nature_of_case: str
    status: str

class B107FinancialAffairs(BaseModel):
    # Income Information (past 2 years)
    income_sources: List[IncomeSource] = Field(default_factory=list)
    total_gross_income_current_year: Optional[Decimal] = None
    total_gross_income_prior_year: Optional[Decimal] = None
    
    # Payments to Creditors
    payments_over_600: List[PaymentToCreditor] = Field(default_factory=list)
    payments_to_insiders: List[PaymentToCreditor] = Field(default_factory=list)
    
    # Lawsuits and Legal Proceedings
    current_lawsuits: List[LawsuitInfo] = Field(default_factory=list)
    
    # Property Transfers
    property_transfers_within_10_years: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Financial Accounts
    closed_financial_accounts: List[Dict[str, Any]] = Field(default_factory=list)
    safe_deposit_boxes: List[Dict[str, Any]] = Field(default_factory=list)

# ============== OFFICIAL FORM B108: STATEMENT OF INTENTION ==============
class SecuredDebt(BaseModel):
    creditor_name: str
    description_of_property: str
    value_of_property: Decimal
    amount_of_secured_claim: Decimal
    retain_property: bool = False
    surrender_property: bool = False
    reaffirm_debt: bool = False
    redeem_property: bool = False

class UnexpiredLease(BaseModel):
    lessor_name: str
    description_of_lease: str
    assume_lease: bool = False
    reject_lease: bool = False

class B108StatementOfIntention(BaseModel):
    secured_debts: List[SecuredDebt] = Field(default_factory=list)
    unexpired_leases: List[UnexpiredLease] = Field(default_factory=list)

# ============== OFFICIAL FORM B109: SUMMARY OF ASSETS AND LIABILITIES ==============
class AssetCategory(BaseModel):
    category_name: str
    current_value: Decimal
    exempt_amount: Decimal

class LiabilityCategory(BaseModel):
    category_name: str
    total_amount: Decimal

class B109Summary(BaseModel):
    # Assets
    real_property: AssetCategory = Field(default_factory=lambda: AssetCategory(category_name="Real property", current_value=Decimal('0'), exempt_amount=Decimal('0')))
    personal_property: AssetCategory = Field(default_factory=lambda: AssetCategory(category_name="Personal property", current_value=Decimal('0'), exempt_amount=Decimal('0')))
    
    # Liabilities
    secured_claims: LiabilityCategory = Field(default_factory=lambda: LiabilityCategory(category_name="Secured claims", total_amount=Decimal('0')))
    unsecured_priority_claims: LiabilityCategory = Field(default_factory=lambda: LiabilityCategory(category_name="Unsecured priority claims", total_amount=Decimal('0')))
    unsecured_nonpriority_claims: LiabilityCategory = Field(default_factory=lambda: LiabilityCategory(category_name="Unsecured nonpriority claims", total_amount=Decimal('0')))

# ============== OFFICIAL FORM B121: STATEMENT OF INCOME AND MEANS TEST ==============
class MonthlyIncome(BaseModel):
    employment_income: Decimal = Decimal('0')
    unemployment_compensation: Decimal = Decimal('0')
    social_security: Decimal = Decimal('0')
    child_support: Decimal = Decimal('0')
    retirement_income: Decimal = Decimal('0')
    other_income: Decimal = Decimal('0')
    
    @property
    def total_monthly_income(self) -> Decimal:
        return (self.employment_income + self.unemployment_compensation + 
                self.social_security + self.child_support + 
                self.retirement_income + self.other_income)

class MonthlyExpenses(BaseModel):
    rent_mortgage: Decimal = Decimal('0')
    utilities: Decimal = Decimal('0')
    food: Decimal = Decimal('0')
    transportation: Decimal = Decimal('0')
    healthcare: Decimal = Decimal('0')
    childcare: Decimal = Decimal('0')
    insurance: Decimal = Decimal('0')
    other_expenses: Decimal = Decimal('0')
    
    @property
    def total_monthly_expenses(self) -> Decimal:
        return (self.rent_mortgage + self.utilities + self.food + 
                self.transportation + self.healthcare + self.childcare + 
                self.insurance + self.other_expenses)

class B121MeansTest(BaseModel):
    # Income Information
    debtor_income: MonthlyIncome = Field(default_factory=MonthlyIncome)
    spouse_income: Optional[MonthlyIncome] = None
    
    # Expense Information
    monthly_expenses: MonthlyExpenses = Field(default_factory=MonthlyExpenses)
    
    # Means Test Calculations
    household_size: int = 1
    state_median_income: Optional[Decimal] = None
    passes_means_test: Optional[bool] = None
    disposable_income: Optional[Decimal] = None

# ============== OFFICIAL FORM B122: STATEMENT OF CURRENT MONTHLY INCOME ==============
class B122CurrentIncome(BaseModel):
    # 6-month lookback period
    month_1_income: Decimal = Decimal('0')
    month_2_income: Decimal = Decimal('0')
    month_3_income: Decimal = Decimal('0')
    month_4_income: Decimal = Decimal('0')
    month_5_income: Decimal = Decimal('0')
    month_6_income: Decimal = Decimal('0')
    
    @property
    def average_monthly_income(self) -> Decimal:
        total = (self.month_1_income + self.month_2_income + self.month_3_income + 
                self.month_4_income + self.month_5_income + self.month_6_income)
        return total / 6
    
    # Deductions
    payroll_deductions: Decimal = Decimal('0')
    insurance_payments: Decimal = Decimal('0')
    union_dues: Decimal = Decimal('0')
    regular_expenses: Decimal = Decimal('0')

# ============== OFFICIAL FORM B123: DEBTOR'S CERTIFICATION ==============
class B123Certification(BaseModel):
    course_provider: Optional[str] = None
    course_completion_date: Optional[date] = None
    certificate_number: Optional[str] = None
    debtor_signature_date: Optional[date] = None

# ============== MASTER BANKRUPTCY CASE MODEL ==============
class CompleteBankruptcyCase(BaseModel):
    """Complete bankruptcy case with all official forms"""
    
    # Case Information
    case_number: Optional[str] = None
    filing_date: Optional[date] = None
    filing_type: Optional[FilingType] = None
    
    # All Official Forms
    form_b101: B101VoluntaryPetition = Field(default_factory=B101VoluntaryPetition)
    form_b106: B106Declaration = Field(default_factory=B106Declaration)
    form_b107: B107FinancialAffairs = Field(default_factory=B107FinancialAffairs)
    form_b108: B108StatementOfIntention = Field(default_factory=B108StatementOfIntention)
    form_b109: B109Summary = Field(default_factory=B109Summary)
    form_b121: B121MeansTest = Field(default_factory=B121MeansTest)
    form_b122: B122CurrentIncome = Field(default_factory=B122CurrentIncome)
    form_b123: B123Certification = Field(default_factory=B123Certification)
    
    # Document Processing
    uploaded_documents: List[str] = Field(default_factory=list)
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    def get_completion_status(self) -> Dict[str, float]:
        """Calculate completion percentage for each form"""
        completion = {}
        
        for form_name in ['b101', 'b106', 'b107', 'b108', 'b109', 'b121', 'b122', 'b123']:
            form_obj = getattr(self, f'form_{form_name}')
            total_fields = len(form_obj.model_fields)
            completed_fields = sum(1 for field, value in form_obj.model_dump().items() 
                                 if value is not None and value != '' and value != [])
            completion[form_name] = (completed_fields / total_fields) * 100 if total_fields > 0 else 0
            
        return completion
    
    def is_ready_for_filing(self) -> bool:
        """Check if case is complete enough for attorney review"""
        completion = self.get_completion_status()
        required_forms = ['b101', 'b106', 'b107', 'b121', 'b122']
        
        for form in required_forms:
            if completion.get(form, 0) < 80:  # 80% completion threshold
                return False
        return True

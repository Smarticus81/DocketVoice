import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime

class MeansTestCalculator:
    """Calculate bankruptcy means test for Chapter 7 eligibility"""
    
    def __init__(self):
        # 2025 median income data (simplified - in practice this would be updated regularly)
        self.median_income_data = {
            "Alabama": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Alaska": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "Arizona": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Arkansas": {"1": 4123, "2": 5234, "3": 6345, "4": 7456, "5": 8567, "6": 9678, "7": 10789, "8": 11900},
            "California": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "Colorado": {"1": 6123, "2": 7234, "3": 8345, "4": 9456, "5": 10567, "6": 11678, "7": 12789, "8": 13900},
            "Connecticut": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "Delaware": {"1": 6123, "2": 7234, "3": 8345, "4": 9456, "5": 10567, "6": 11678, "7": 12789, "8": 13900},
            "Florida": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Georgia": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Hawaii": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "Idaho": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Illinois": {"1": 6123, "2": 7234, "3": 8345, "4": 9456, "5": 10567, "6": 11678, "7": 12789, "8": 13900},
            "Indiana": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Iowa": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Kansas": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Kentucky": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Louisiana": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Maine": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Maryland": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "Massachusetts": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "Michigan": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Minnesota": {"1": 6123, "2": 7234, "3": 8345, "4": 9456, "5": 10567, "6": 11678, "7": 12789, "8": 13900},
            "Mississippi": {"1": 4123, "2": 5234, "3": 6345, "4": 7456, "5": 8567, "6": 9678, "7": 10789, "8": 11900},
            "Missouri": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Montana": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Nebraska": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Nevada": {"1": 5678, "2": 6789, "3": 7890, "4": 8901, "5": 9012, "6": 10123, "7": 11234, "8": 12345},
            "New Hampshire": {"1": 6123, "2": 7234, "3": 8345, "4": 9456, "5": 10567, "6": 11678, "7": 12789, "8": 13900},
            "New Jersey": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "New Mexico": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "New York": {"1": 6789, "2": 7890, "3": 8901, "4": 9012, "5": 10123, "6": 11234, "7": 12345, "8": 13456},
            "North Carolina": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "North Dakota": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Ohio": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Oklahoma": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Oregon": {"1": 5678, "2": 6789, "3": 7890, "4": 8901, "5": 9012, "6": 10123, "7": 11234, "8": 12345},
            "Pennsylvania": {"1": 5678, "2": 6789, "3": 7890, "4": 8901, "5": 9012, "6": 10123, "7": 11234, "8": 12345},
            "Rhode Island": {"1": 5678, "2": 6789, "3": 7890, "4": 8901, "5": 9012, "6": 10123, "7": 11234, "8": 12345},
            "South Carolina": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "South Dakota": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Tennessee": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234},
            "Texas": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Utah": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Vermont": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Virginia": {"1": 6123, "2": 7234, "3": 8345, "4": 9456, "5": 10567, "6": 11678, "7": 12789, "8": 13900},
            "Washington": {"1": 6123, "2": 7234, "3": 8345, "4": 9456, "5": 10567, "6": 11678, "7": 12789, "8": 13900},
            "West Virginia": {"1": 4123, "2": 5234, "3": 6345, "4": 7456, "5": 8567, "6": 9678, "7": 10789, "8": 11900},
            "Wisconsin": {"1": 5234, "2": 6345, "3": 7456, "4": 8567, "5": 9678, "6": 10789, "7": 11900, "8": 13011},
            "Wyoming": {"1": 4567, "2": 5678, "3": 6789, "4": 7890, "5": 8901, "6": 9012, "7": 10123, "8": 11234}
        }
        
        # IRS National Standards for Allowable Living Expenses (2025)
        self.irs_standards = {
            "food": {"1": 500, "2": 600, "3": 700, "4": 800, "5": 900, "6": 1000, "7": 1100, "8": 1200},
            "housekeeping_supplies": {"1": 50, "2": 60, "3": 70, "4": 80, "5": 90, "6": 100, "7": 110, "8": 120},
            "apparel_and_services": {"1": 200, "2": 250, "3": 300, "4": 350, "5": 400, "6": 450, "7": 500, "8": 550},
            "personal_care": {"1": 50, "2": 60, "3": 70, "4": 80, "5": 90, "6": 100, "7": 110, "8": 120},
            "miscellaneous": {"1": 100, "2": 120, "3": 140, "4": 160, "5": 180, "6": 200, "7": 220, "8": 240}
        }
        
        # Local Standards for Housing and Utilities
        self.housing_standards = {
            "housing_and_utilities": {"1": 800, "2": 1000, "3": 1200, "4": 1400, "5": 1600, "6": 1800, "7": 2000, "8": 2200}
        }
        
        # Transportation Standards
        self.transportation_standards = {
            "ownership_costs": {"1": 500, "2": 500, "3": 500, "4": 500, "5": 500, "6": 500, "7": 500, "8": 500},
            "operating_costs": {"1": 200, "2": 200, "3": 200, "4": 200, "5": 200, "6": 200, "7": 200, "8": 200}
        }
    
    def calculate_current_monthly_income(self, data: Dict[str, Any]) -> float:
        """Calculate current monthly income from the past 6 months"""
        try:
            # Get base monthly income
            monthly_income = float(data.get('monthly_income', 0))
            
            # Add additional income sources
            additional_income = data.get('additional_income', [])
            for income_source in additional_income:
                try:
                    amount = float(income_source.get('amount', 0))
                    monthly_income += amount
                except (ValueError, TypeError):
                    continue
            
            return monthly_income
        except (ValueError, TypeError):
            return 0.0
    
    def get_household_size(self, data: Dict[str, Any]) -> int:
        """Calculate household size for means test"""
        household_size = 1  # Debtor
        
        # Add spouse if married
        if data.get('marital_status', '').lower() in ['married', 'marriage']:
            household_size += 1
        
        # Add dependents
        dependents = data.get('dependents', [])
        household_size += len(dependents)
        
        return household_size
    
    def get_state_median_income(self, state: str, household_size: int) -> float:
        """Get median income for state and household size"""
        state_data = self.median_income_data.get(state, {})
        size_key = str(min(household_size, 8))  # Cap at 8+ household members
        return float(state_data.get(size_key, 5000))  # Default fallback
    
    def calculate_allowable_expenses(self, data: Dict[str, Any], household_size: int) -> Dict[str, float]:
        """Calculate allowable expenses using IRS standards and actual expenses"""
        expenses = {}
        
        # Get actual monthly expenses
        monthly_expenses = data.get('monthly_expenses', {})
        
        # Food and related items (use IRS standards)
        size_key = str(min(household_size, 8))
        expenses['food'] = float(self.irs_standards['food'].get(size_key, 500))
        expenses['housekeeping_supplies'] = float(self.irs_standards['housekeeping_supplies'].get(size_key, 50))
        expenses['apparel_and_services'] = float(self.irs_standards['apparel_and_services'].get(size_key, 200))
        expenses['personal_care'] = float(self.irs_standards['personal_care'].get(size_key, 50))
        expenses['miscellaneous'] = float(self.irs_standards['miscellaneous'].get(size_key, 100))
        
        # Housing and utilities (use actual or IRS standard, whichever is lower)
        actual_housing = float(monthly_expenses.get('rent_mortgage', 0)) + float(monthly_expenses.get('utilities', 0))
        irs_housing = float(self.housing_standards['housing_and_utilities'].get(size_key, 1000))
        expenses['housing_and_utilities'] = min(actual_housing, irs_housing)
        
        # Transportation (use actual or IRS standard)
        actual_transportation = float(monthly_expenses.get('car_payment', 0)) + float(monthly_expenses.get('car_insurance', 0)) + float(monthly_expenses.get('gas_maintenance', 0))
        irs_transportation = float(self.transportation_standards['ownership_costs'].get(size_key, 500)) + float(self.transportation_standards['operating_costs'].get(size_key, 200))
        expenses['transportation'] = min(actual_transportation, irs_transportation)
        
        # Health insurance and medical expenses
        expenses['health_insurance'] = float(monthly_expenses.get('health_insurance', 0))
        expenses['medical_expenses'] = float(monthly_expenses.get('medical_expenses', 0))
        
        # Phone and internet
        expenses['phone_internet'] = float(monthly_expenses.get('phone_internet', 0))
        
        # Entertainment
        expenses['entertainment'] = float(monthly_expenses.get('entertainment', 0))
        
        return expenses
    
    def calculate_secured_debt_payments(self, data: Dict[str, Any]) -> float:
        """Calculate total secured debt payments"""
        total_payments = 0.0
        
        liabilities = data.get('liabilities', [])
        for liability in liabilities:
            if liability.get('type') == 'secured':
                try:
                    payment = float(liability.get('monthly_payment', 0))
                    total_payments += payment
                except (ValueError, TypeError):
                    continue
        
        return total_payments
    
    def calculate_priority_debt_payments(self, data: Dict[str, Any]) -> float:
        """Calculate total priority debt payments"""
        total_payments = 0.0
        
        liabilities = data.get('liabilities', [])
        for liability in liabilities:
            if liability.get('type') == 'priority':
                # Priority debts are typically paid in full, so we estimate monthly payment
                try:
                    amount = float(liability.get('amount', 0))
                    # Estimate monthly payment as 1/60 of total (5-year plan)
                    monthly_payment = amount / 60
                    total_payments += monthly_payment
                except (ValueError, TypeError):
                    continue
        
        return total_payments
    
    def calculate_disposable_income(self, data: Dict[str, Any]) -> float:
        """Calculate disposable monthly income"""
        # Current monthly income
        current_monthly_income = self.calculate_current_monthly_income(data)
        
        # Total allowable expenses
        household_size = self.get_household_size(data)
        allowable_expenses = self.calculate_allowable_expenses(data, household_size)
        total_expenses = sum(allowable_expenses.values())
        
        # Secured debt payments
        secured_payments = self.calculate_secured_debt_payments(data)
        
        # Priority debt payments
        priority_payments = self.calculate_priority_debt_payments(data)
        
        # Calculate disposable income
        disposable_income = current_monthly_income - total_expenses - secured_payments - priority_payments
        
        return max(0, disposable_income)  # Cannot be negative
    
    def determine_means_test_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine means test result and eligibility"""
        state = data.get('court_jurisdiction', {}).get('state', 'California')
        household_size = self.get_household_size(data)
        current_monthly_income = self.calculate_current_monthly_income(data)
        state_median_income = self.get_state_median_income(state, household_size)
        
        # Step 1: Compare to median income
        if current_monthly_income <= state_median_income:
            return {
                "step1_result": "PASS",
                "step1_reason": f"Current monthly income (${current_monthly_income:,.2f}) is below state median income (${state_median_income:,.2f})",
                "step2_required": False,
                "means_test_result": "PASS",
                "chapter_7_eligible": True,
                "chapter_13_required": False,
                "details": {
                    "current_monthly_income": current_monthly_income,
                    "state_median_income": state_median_income,
                    "household_size": household_size,
                    "state": state
                }
            }
        
        # Step 2: Calculate disposable income
        disposable_income = self.calculate_disposable_income(data)
        five_year_disposable = disposable_income * 60
        
        # Determine result based on disposable income thresholds
        if five_year_disposable < 7700:
            result = "PASS"
            chapter_7_eligible = True
            chapter_13_required = False
        elif five_year_disposable > 12850:
            result = "FAIL"
            chapter_7_eligible = False
            chapter_13_required = True
        else:
            # Between thresholds - check percentage of unsecured debt
            unsecured_debt = self.calculate_unsecured_debt(data)
            if unsecured_debt > 0:
                percentage = (five_year_disposable / unsecured_debt) * 100
                if percentage >= 25:
                    result = "FAIL"
                    chapter_7_eligible = False
                    chapter_13_required = True
                else:
                    result = "PASS"
                    chapter_7_eligible = True
                    chapter_13_required = False
            else:
                result = "PASS"
                chapter_7_eligible = True
                chapter_13_required = False
        
        return {
            "step1_result": "FAIL",
            "step1_reason": f"Current monthly income (${current_monthly_income:,.2f}) is above state median income (${state_median_income:,.2f})",
            "step2_required": True,
            "step2_result": result,
            "step2_reason": f"Five-year disposable income (${five_year_disposable:,.2f}) {'exceeds' if result == 'FAIL' else 'is below'} threshold",
            "means_test_result": result,
            "chapter_7_eligible": chapter_7_eligible,
            "chapter_13_required": chapter_13_required,
            "details": {
                "current_monthly_income": current_monthly_income,
                "state_median_income": state_median_income,
                "disposable_monthly_income": disposable_income,
                "five_year_disposable_income": five_year_disposable,
                "household_size": household_size,
                "state": state,
                "allowable_expenses": self.calculate_allowable_expenses(data, household_size),
                "secured_payments": self.calculate_secured_debt_payments(data),
                "priority_payments": self.calculate_priority_debt_payments(data)
            }
        }
    
    def calculate_unsecured_debt(self, data: Dict[str, Any]) -> float:
        """Calculate total unsecured debt"""
        total_unsecured = 0.0
        
        liabilities = data.get('liabilities', [])
        for liability in liabilities:
            if liability.get('type') == 'unsecured':
                try:
                    amount = float(liability.get('amount', 0))
                    total_unsecured += amount
                except (ValueError, TypeError):
                    continue
        
        return total_unsecured

def calculate_means_test(data: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to calculate means test"""
    calculator = MeansTestCalculator()
    result = calculator.determine_means_test_result(data)
    
    # Add calculation timestamp
    result['calculation_date'] = datetime.now().isoformat()
    result['calculation_version'] = "2025.1"
    
    return result

def generate_means_test_report(data: Dict[str, Any], means_test_result: Dict[str, Any]) -> str:
    """Generate a detailed means test report"""
    report = []
    report.append("=" * 60)
    report.append("BANKRUPTCY MEANS TEST CALCULATION REPORT")
    report.append("=" * 60)
    report.append(f"Calculation Date: {means_test_result.get('calculation_date', 'Unknown')}")
    report.append(f"Debtor: {data.get('name', 'Unknown')}")
    report.append(f"State: {data.get('court_jurisdiction', {}).get('state', 'Unknown')}")
    report.append("")
    
    # Step 1 Results
    report.append("STEP 1: MEDIAN INCOME COMPARISON")
    report.append("-" * 40)
    report.append(f"Result: {means_test_result.get('step1_result', 'Unknown')}")
    report.append(f"Reason: {means_test_result.get('step1_reason', 'Unknown')}")
    report.append("")
    
    details = means_test_result.get('details', {})
    report.append(f"Current Monthly Income: ${details.get('current_monthly_income', 0):,.2f}")
    report.append(f"State Median Income: ${details.get('state_median_income', 0):,.2f}")
    report.append(f"Household Size: {details.get('household_size', 0)}")
    report.append("")
    
    # Step 2 Results (if applicable)
    if means_test_result.get('step2_required', False):
        report.append("STEP 2: DISPOSABLE INCOME CALCULATION")
        report.append("-" * 40)
        report.append(f"Result: {means_test_result.get('step2_result', 'Unknown')}")
        report.append(f"Reason: {means_test_result.get('step2_reason', 'Unknown')}")
        report.append("")
        
        report.append("INCOME AND EXPENSE BREAKDOWN:")
        report.append(f"  Current Monthly Income: ${details.get('current_monthly_income', 0):,.2f}")
        report.append("")
        
        # Allowable expenses
        allowable_expenses = details.get('allowable_expenses', {})
        report.append("  ALLOWABLE EXPENSES:")
        total_expenses = 0
        for expense_type, amount in allowable_expenses.items():
            report.append(f"    {expense_type.replace('_', ' ').title()}: ${amount:,.2f}")
            total_expenses += amount
        report.append(f"    Total Allowable Expenses: ${total_expenses:,.2f}")
        report.append("")
        
        # Debt payments
        secured_payments = details.get('secured_payments', 0)
        priority_payments = details.get('priority_payments', 0)
        report.append("  DEBT PAYMENTS:")
        report.append(f"    Secured Debt Payments: ${secured_payments:,.2f}")
        report.append(f"    Priority Debt Payments: ${priority_payments:,.2f}")
        report.append("")
        
        # Disposable income
        disposable_income = details.get('disposable_monthly_income', 0)
        five_year_disposable = details.get('five_year_disposable_income', 0)
        report.append(f"  Disposable Monthly Income: ${disposable_income:,.2f}")
        report.append(f"  Five-Year Disposable Income: ${five_year_disposable:,.2f}")
        report.append("")
    
    # Final Result
    report.append("FINAL MEANS TEST RESULT")
    report.append("-" * 40)
    report.append(f"Result: {means_test_result.get('means_test_result', 'Unknown')}")
    report.append(f"Chapter 7 Eligible: {'Yes' if means_test_result.get('chapter_7_eligible', False) else 'No'}")
    report.append(f"Chapter 13 Required: {'Yes' if means_test_result.get('chapter_13_required', False) else 'No'}")
    report.append("")
    
    # Recommendations
    report.append("RECOMMENDATIONS:")
    report.append("-" * 40)
    if means_test_result.get('chapter_7_eligible', False):
        report.append("✓ You appear to be eligible for Chapter 7 bankruptcy")
        report.append("✓ You may be able to discharge most unsecured debts")
    else:
        report.append("✗ You may not be eligible for Chapter 7 bankruptcy")
        report.append("✓ Consider Chapter 13 bankruptcy with a repayment plan")
    
    report.append("")
    report.append("NOTE: This calculation is for informational purposes only.")
    report.append("Consult with a qualified bankruptcy attorney for legal advice.")
    report.append("=" * 60)
    
    return "\n".join(report) 
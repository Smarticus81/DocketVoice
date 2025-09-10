"""
Comprehensive Question Bank for Bankruptcy Form Completion
Natural conversation flow for gathering all required bankruptcy information
"""

from typing import Dict, List, Optional
from enum import Enum

class QuestionCategory(str, Enum):
    PERSONAL_INFO = "personal_info"
    FINANCIAL_INFO = "financial_info"
    DEBTS_LIABILITIES = "debts_liabilities"
    ASSETS_PROPERTY = "assets_property"
    INCOME_EMPLOYMENT = "income_employment"
    EXPENSES = "expenses"
    LEGAL_HISTORY = "legal_history"
    PREFERENCES = "preferences"

# Comprehensive question bank with multiple phrasings for natural conversation
QUESTION_BANK = {
    # PERSONAL INFORMATION (B101, B106)
    "DebtorInfo.first_name": [
        "What's your first name?",
        "Could you tell me your first name please?",
        "Let's start with your first name - what should I call you?",
        "What first name appears on your official documents?"
    ],
    
    "DebtorInfo.middle_name": [
        "Do you have a middle name?",
        "What's your middle name, or do you not use one?",
        "Is there a middle name on your official documents?",
        "Any middle name or middle initial I should include?"
    ],
    
    "DebtorInfo.last_name": [
        "And your last name?",
        "What's your family name or surname?",
        "What last name should I use for your case?",
        "What's your last name as it appears on your ID?"
    ],
    
    "DebtorInfo.address_line_1": [
        "What's your current home address?",
        "Where do you live right now? I'll need the street address.",
        "What address should I use as your primary residence?",
        "Can you give me your current street address?"
    ],
    
    "DebtorInfo.city": [
        "What city is that in?",
        "And which city?",
        "What's the city for that address?",
        "Which city do you live in?"
    ],
    
    "DebtorInfo.state": [
        "What state?",
        "Which state is that?",
        "What state do you reside in?",
        "And the state?"
    ],
    
    "DebtorInfo.zip_code": [
        "What's your zip code?",
        "And the zip code?",
        "What's the postal code for that address?",
        "Can you give me the zip code?"
    ],
    
    "DebtorInfo.phone_home": [
        "What's your home phone number?",
        "Do you have a home phone I can list?",
        "What's a good phone number to reach you at home?",
        "Home phone number?"
    ],
    
    "DebtorInfo.phone_cell": [
        "What about your cell phone?",
        "What's your mobile number?",
        "Do you have a cell phone number?",
        "What's your cell phone number?"
    ],
    
    "DebtorInfo.email": [
        "What's your email address?",
        "Do you have an email I can use?",
        "What email address should I include?",
        "Can you give me your email?"
    ],
    
    "DebtorInfo.ssn_last_4": [
        "I'll need the last 4 digits of your Social Security number for the forms.",
        "What are the last four digits of your SSN?",
        "Can you provide the last 4 digits of your Social Security number?",
        "For security, just the last 4 digits of your Social Security number please."
    ],
    
    # MARITAL STATUS AND SPOUSE INFO
    "B101.marital_status": [
        "What's your current marital status?",
        "Are you married, single, divorced, separated, or widowed?",
        "What's your marital status?",
        "Are you currently married?"
    ],
    
    "SpouseInfo.first_name": [
        "What's your spouse's first name?",
        "What should I call your spouse?",
        "Your spouse's first name?",
        "What's your husband's/wife's first name?"
    ],
    
    "SpouseInfo.last_name": [
        "And your spouse's last name?",
        "What's your spouse's last name?",
        "Your spouse's family name?",
        "What last name does your spouse use?"
    ],
    
    # FILING TYPE AND BANKRUPTCY DETAILS
    "B101.filing_type": [
        "Are you looking to file Chapter 7 or Chapter 13 bankruptcy?",
        "Do you want to file under Chapter 7 or Chapter 13?",
        "Which chapter of bankruptcy - 7 or 13?",
        "Are you interested in Chapter 7 liquidation or Chapter 13 repayment plan?"
    ],
    
    "B101.joint_petition": [
        "Will your spouse be filing with you as a joint petition?",
        "Is this a joint filing with your spouse?",
        "Are you and your spouse filing together?",
        "Will your spouse be included in this bankruptcy filing?"
    ],
    
    "B101.previous_bankruptcy_filed": [
        "Have you filed for bankruptcy before?",
        "Is this your first bankruptcy filing?",
        "Have you ever filed bankruptcy in the past?",
        "Any previous bankruptcy cases?"
    ],
    
    # INCOME INFORMATION (B121, B122, B107)
    "MonthlyIncome.employment_income": [
        "What's your monthly income from employment?",
        "How much do you make per month from your job?",
        "What's your monthly take-home pay?",
        "What do you earn monthly from work?"
    ],
    
    "MonthlyIncome.unemployment_compensation": [
        "Are you receiving any unemployment benefits?",
        "Do you get unemployment compensation?",
        "Any monthly unemployment income?",
        "Are you collecting unemployment?"
    ],
    
    "MonthlyIncome.social_security": [
        "Do you receive Social Security benefits?",
        "Any Social Security income?",
        "Are you getting Social Security payments?",
        "Do you have Social Security benefits coming in?"
    ],
    
    "MonthlyIncome.retirement_income": [
        "Do you have any retirement income?",
        "Are you receiving pension or retirement benefits?",
        "Any income from retirement accounts or pensions?",
        "Do you get retirement payments?"
    ],
    
    "MonthlyIncome.child_support": [
        "Do you receive child support?",
        "Any child support payments coming in?",
        "Are you getting child support from an ex-spouse?",
        "Do you receive support payments for children?"
    ],
    
    "MonthlyIncome.other_income": [
        "Do you have any other sources of income?",
        "Any other money coming in monthly?",
        "Are there other income sources I should know about?",
        "Any additional income from investments, side jobs, or other sources?"
    ],
    
    # EMPLOYMENT INFORMATION
    "Employment.employer_name": [
        "Who do you work for?",
        "What's your employer's name?",
        "What company do you work for?",
        "Who's your current employer?"
    ],
    
    "Employment.job_title": [
        "What's your job title?",
        "What do you do for work?",
        "What's your position called?",
        "What kind of work do you do?"
    ],
    
    "Employment.employment_status": [
        "Are you currently employed full-time, part-time, or not working?",
        "What's your employment status?",
        "Are you working right now?",
        "Are you employed, unemployed, retired, or disabled?"
    ],
    
    # MONTHLY EXPENSES (B121)
    "MonthlyExpenses.rent_mortgage": [
        "What do you pay monthly for housing - rent or mortgage?",
        "How much is your monthly rent or mortgage payment?",
        "What's your monthly housing cost?",
        "How much do you pay for your home each month?"
    ],
    
    "MonthlyExpenses.utilities": [
        "What do you spend on utilities each month?",
        "How much are your monthly utility bills?",
        "What do you pay for electricity, gas, water, etc.?",
        "What's your average monthly utility cost?"
    ],
    
    "MonthlyExpenses.food": [
        "How much do you spend on food and groceries monthly?",
        "What's your monthly food budget?",
        "How much do you spend eating and grocery shopping?",
        "What do you typically spend on food each month?"
    ],
    
    "MonthlyExpenses.transportation": [
        "What are your monthly transportation costs?",
        "How much do you spend on car payments, gas, insurance?",
        "What do you pay for transportation each month?",
        "Any monthly costs for getting around - car, bus, gas?"
    ],
    
    "MonthlyExpenses.healthcare": [
        "What do you spend on healthcare and medical expenses?",
        "Any monthly medical costs or health insurance?",
        "How much do you pay for healthcare each month?",
        "What are your monthly medical expenses?"
    ],
    
    "MonthlyExpenses.insurance": [
        "What do you pay monthly for insurance?",
        "Any insurance premiums - health, life, auto?",
        "How much are your monthly insurance costs?",
        "What insurance do you pay for monthly?"
    ],
    
    # ASSETS AND PROPERTY (B109)
    "Assets.real_property_value": [
        "Do you own any real estate? What's it worth?",
        "Do you own your home? What's its current value?",
        "Any real estate or property you own?",
        "What real property do you have and what's it worth?"
    ],
    
    "Assets.vehicle_value": [
        "Do you own any vehicles? What are they worth?",
        "What cars, trucks, or other vehicles do you own?",
        "Any vehicles and their current values?",
        "Do you have cars or other vehicles? What are they worth?"
    ],
    
    "Assets.bank_accounts": [
        "What do you have in bank accounts right now?",
        "How much money is in your checking and savings?",
        "What's the total in all your bank accounts?",
        "How much cash do you have in the bank?"
    ],
    
    "Assets.retirement_accounts": [
        "Do you have any retirement accounts like 401k or IRA?",
        "Any retirement savings or pension accounts?",
        "What's in your retirement accounts?",
        "Do you have 401k, IRA, or other retirement funds?"
    ],
    
    # DEBTS AND LIABILITIES (B107, B108)
    "Debts.credit_card_debt": [
        "How much do you owe on credit cards total?",
        "What's your total credit card debt?",
        "How much credit card debt do you have?",
        "What do you owe on all your credit cards combined?"
    ],
    
    "Debts.mortgage_debt": [
        "How much do you still owe on your mortgage?",
        "What's the remaining balance on your home loan?",
        "How much is left on your mortgage?",
        "What do you owe on your house?"
    ],
    
    "Debts.auto_loans": [
        "Do you have any car loans? How much do you owe?",
        "Any auto loans and their balances?",
        "What do you owe on vehicle loans?",
        "How much is left on your car payments?"
    ],
    
    "Debts.medical_debt": [
        "Do you have medical bills or medical debt?",
        "Any unpaid medical expenses?",
        "How much do you owe in medical bills?",
        "Any hospital bills or medical debt?"
    ],
    
    "Debts.student_loans": [
        "Do you have student loans? How much?",
        "Any educational debt or student loans?",
        "What do you owe on student loans?",
        "Any college or school loans?"
    ],
    
    "Debts.other_debts": [
        "Are there any other debts I should know about?",
        "Any other money you owe to anyone?",
        "Other loans, debts, or amounts owed?",
        "Any additional debts not mentioned yet?"
    ],
    
    # LEGAL AND FINANCIAL HISTORY (B107)
    "Legal.lawsuits": [
        "Are you involved in any lawsuits right now?",
        "Any current legal cases or lawsuits?",
        "Are you suing anyone or is anyone suing you?",
        "Any ongoing legal proceedings?"
    ],
    
    "Legal.property_transfers": [
        "Have you sold or given away any property in the last 10 years?",
        "Any major property transfers or sales recently?",
        "Have you transferred any assets to family or friends?",
        "Did you sell or give away anything valuable in recent years?"
    ],
    
    "Financial.closed_accounts": [
        "Have you closed any bank accounts in the past year?",
        "Any financial accounts closed recently?",
        "Did you close any checking or savings accounts lately?",
        "Any bank accounts you've closed in the last 12 months?"
    ],
    
    # PREFERENCES AND INTENTIONS (B108)
    "Intention.keep_house": [
        "Do you want to keep your house?",
        "Are you planning to stay in your home?",
        "Do you want to keep making mortgage payments?",
        "Would you like to keep your house and continue paying for it?"
    ],
    
    "Intention.keep_car": [
        "Do you want to keep your car?",
        "Are you planning to keep your vehicle?",
        "Do you want to continue making car payments?",
        "Would you like to keep your car and keep paying for it?"
    ],
    
    "Intention.reaffirm_debts": [
        "Are there any debts you want to keep paying after bankruptcy?",
        "Any loans you want to reaffirm and continue paying?",
        "Do you want to keep any debts and continue making payments?",
        "Are there debts you don't want to discharge in bankruptcy?"
    ],
    
    # HOUSEHOLD AND FAMILY
    "Household.household_size": [
        "How many people live in your household?",
        "Who all lives with you?",
        "How many people are in your family that you support?",
        "What's your household size including yourself?"
    ],
    
    "Household.dependents": [
        "Do you have any dependents or children you support?",
        "How many children do you claim as dependents?",
        "Any kids or other people you financially support?",
        "Who depends on you financially?"
    ],
    
    # COURSE COMPLETION (B123)
    "B123.course_completion": [
        "Have you completed the required credit counseling course?",
        "Did you finish the bankruptcy counseling course yet?",
        "Have you done the mandatory financial counseling?",
        "Did you complete the required bankruptcy education course?"
    ],
    
    "B123.course_provider": [
        "Which company provided your credit counseling course?",
        "Who did you take the counseling course with?",
        "What was the name of your course provider?",
        "Which organization gave you the counseling certificate?"
    ],
    
    "B123.certificate_number": [
        "What's your certificate number from the course?",
        "Do you have the certificate number from counseling?",
        "What number is on your counseling certificate?",
        "Can you give me the certificate or confirmation number?"
    ]
}

# Follow-up questions for unclear or incomplete answers
FOLLOW_UP_QUESTIONS = {
    "unclear_amount": [
        "Could you give me a more specific dollar amount?",
        "About how much would you estimate?",
        "Can you give me a rough number?",
        "What would be your best guess on the amount?"
    ],
    
    "need_more_detail": [
        "Can you tell me a bit more about that?",
        "Could you give me some more details?",
        "Can you explain that a little more?",
        "I'd like to understand that better - can you elaborate?"
    ],
    
    "confirm_zero": [
        "So that would be zero, correct?",
        "Just to confirm, you don't have any of that?",
        "So nothing in that category?",
        "That would be none, right?"
    ],
    
    "confirm_understanding": [
        "Let me make sure I understand - you're saying...",
        "Just to confirm, you mean...",
        "So if I understand correctly...",
        "Let me repeat that back to make sure I got it right..."
    ]
}

# Transition phrases to keep conversation natural
TRANSITION_PHRASES = [
    "Great, now let's talk about...",
    "Perfect. Moving on to...",
    "Thanks for that information. Next, I need to know about...",
    "Okay, got it. Now let's discuss...",
    "Excellent. The next thing I need to understand is...",
    "Thank you. Now, regarding...",
    "That's helpful. Let's move on to...",
    "I appreciate that detail. Now about..."
]

# Encouragement and empathy phrases
EMPATHY_PHRASES = [
    "I understand this can be overwhelming, but you're doing great.",
    "I know this is a lot of information, but we're making good progress.",
    "These are difficult questions, but you're handling them well.",
    "I appreciate your patience with all these details.",
    "You're doing really well providing this information.",
    "I know this isn't easy, but you're giving me exactly what I need.",
    "Thank you for being so thorough with your answers."
]

def get_questions_for_category(category: QuestionCategory) -> Dict[str, List[str]]:
    """Get all questions for a specific category"""
    category_questions = {}
    
    category_mapping = {
        QuestionCategory.PERSONAL_INFO: ['DebtorInfo.', 'SpouseInfo.'],
        QuestionCategory.FINANCIAL_INFO: ['MonthlyIncome.', 'B122.'],
        QuestionCategory.DEBTS_LIABILITIES: ['Debts.'],
        QuestionCategory.ASSETS_PROPERTY: ['Assets.'],
        QuestionCategory.INCOME_EMPLOYMENT: ['MonthlyIncome.', 'Employment.'],
        QuestionCategory.EXPENSES: ['MonthlyExpenses.'],
        QuestionCategory.LEGAL_HISTORY: ['Legal.', 'Financial.'],
        QuestionCategory.PREFERENCES: ['Intention.', 'B123.']
    }
    
    prefixes = category_mapping.get(category, [])
    
    for key, questions in QUESTION_BANK.items():
        for prefix in prefixes:
            if key.startswith(prefix):
                category_questions[key] = questions
                break
    
    return category_questions

def get_random_question(field_key: str) -> Optional[str]:
    """Get a random question for a specific field"""
    import random
    questions = QUESTION_BANK.get(field_key)
    if questions:
        return random.choice(questions)
    return None

def get_follow_up_question(situation: str) -> Optional[str]:
    """Get an appropriate follow-up question"""
    import random
    questions = FOLLOW_UP_QUESTIONS.get(situation)
    if questions:
        return random.choice(questions)
    return None

def get_transition_phrase() -> str:
    """Get a random transition phrase"""
    import random
    return random.choice(TRANSITION_PHRASES)

def get_empathy_phrase() -> str:
    """Get a random empathy phrase"""
    import random
    return random.choice(EMPATHY_PHRASES)

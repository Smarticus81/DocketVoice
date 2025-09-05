import os
import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import openai
from dataclasses import dataclass
from enum import Enum

load_dotenv()

class BankruptcyContext(Enum):
    """Bankruptcy law context types"""
    CHAPTER_7 = "chapter_7"
    CHAPTER_13 = "chapter_13"
    MEANS_TEST = "means_test"
    ASSET_ANALYSIS = "asset_analysis"
    LIABILITY_ANALYSIS = "liability_analysis"
    EXPENSE_ANALYSIS = "expense_analysis"
    LEGAL_ANALYSIS = "legal_analysis"

class LegalGuardrail(Enum):
    """Legal guardrail types"""
    NO_LEGAL_ADVICE = "no_legal_advice"
    NO_ELIGIBILITY_GUARANTEE = "no_eligibility_guarantee"
    NO_COURT_FILING = "no_court_filing"
    CONSULT_ATTORNEY = "consult_attorney"
    INFORMATIONAL_ONLY = "informational_only"

@dataclass
class BankruptcyLawContext:
    """Bankruptcy law context and knowledge base"""
    
    # Federal Bankruptcy Code sections
    bankruptcy_code_sections = {
        "chapter_7": ["701", "702", "703", "704", "705", "706", "707"],
        "chapter_13": ["1301", "1302", "1303", "1304", "1305", "1306", "1307", "1308", "1309", "1310", "1311", "1312", "1313", "1314", "1315", "1316", "1317", "1318", "1319", "1320", "1321", "1322", "1323", "1324", "1325", "1326", "1327", "1328", "1329", "1330"],
        "means_test": ["707(b)", "1325(b)"],
        "exemptions": ["522"],
        "automatic_stay": ["362"],
        "discharge": ["523", "524", "727", "1328"]
    }
    
    # Federal Rules of Bankruptcy Procedure
    bankruptcy_rules = {
        "filing": ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009"],
        "schedules": ["1007", "1019"],
        "means_test": ["1007(b)", "1015"],
        "creditor_claims": ["3001", "3002", "3003", "3004", "3005", "3006", "3007", "3008", "3009", "3010", "3011", "3012", "3013", "3014", "3015", "3016", "3017", "3018", "3019", "3020", "3021", "3022", "3023", "3024", "3025"],
        "341_meeting": ["2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
    }
    
    # Official Bankruptcy Forms
    official_forms = {
        "voluntary_petition": "Form 101",
        "schedules": ["Form 106A/B", "Form 106C", "Form 106D", "Form 106E/F", "Form 106G", "Form 106H", "Form 106I", "Form 106J"],
        "statement_of_financial_affairs": "Form 107",
        "means_test": ["Form 122A-1", "Form 122A-2", "Form 122C-1", "Form 122C-2"],
        "social_security": "Form 121"
    }
    
    # State-specific bankruptcy exemptions
    state_exemptions = {
        "homestead": ["Florida", "Texas", "Iowa", "Kansas", "South Dakota"],
        "wildcard": ["California", "New York", "Illinois", "Pennsylvania"],
        "vehicle": ["All states have vehicle exemptions"],
        "retirement": ["401(k)", "IRA", "Pension", "Social Security"]
    }
    
    # Common bankruptcy mistakes to avoid
    common_mistakes = [
        "Failing to list all assets and liabilities",
        "Incorrect means test calculations",
        "Missing required forms or schedules",
        "Incomplete creditor matrix",
        "Failure to attend 341 meeting",
        "Not completing credit counseling",
        "Incorrect exemption claims",
        "Missing tax returns"
    ]
    
    # Legal disclaimers and warnings
    legal_disclaimers = [
        "This is not legal advice",
        "Consult with a qualified bankruptcy attorney",
        "Information is for educational purposes only",
        "No attorney-client relationship is created",
        "Bankruptcy laws vary by jurisdiction",
        "Individual circumstances may affect eligibility"
    ]

class BankruptcyLLM:
    """Specialized bankruptcy law LLM with legal reasoning and guardrails using latest reasoning models"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for AI analysis features")
        
        self.openai_client = openai.OpenAI(api_key=api_key)
        self.context = BankruptcyLawContext()
        self.conversation_history = []
        self.legal_guardrails = []
        
        # Initialize with bankruptcy law expertise
        self._initialize_bankruptcy_expertise()
        
        # Model selection based on latest research
        self.primary_model = "gpt-4o"  # Latest reasoning model
        self.vision_model = "gpt-4o"   # Latest vision model
        self.fallback_model = "gpt-4-turbo"  # Fallback for complex reasoning
    
    def _initialize_bankruptcy_expertise(self):
        """Initialize the LLM with bankruptcy law expertise"""
        system_prompt = self._create_bankruptcy_expertise_prompt()
        
        # Store the expertise prompt for context
        self.expertise_context = system_prompt
    
    def _create_bankruptcy_expertise_prompt(self) -> str:
        """Create comprehensive bankruptcy law expertise prompt"""
        return f"""
        You are a specialized bankruptcy law AI assistant with deep expertise in U.S. bankruptcy law and procedure. You have the following knowledge and capabilities:

        BANKRUPTCY CODE EXPERTISE:
        - Chapter 7 (Liquidation): Sections {', '.join(self.context.bankruptcy_code_sections['chapter_7'])}
        - Chapter 13 (Repayment Plan): Sections {', '.join(self.context.bankruptcy_code_sections['chapter_13'])}
        - Means Testing: Sections {', '.join(self.context.bankruptcy_code_sections['means_test'])}
        - Exemptions: Section {self.context.bankruptcy_code_sections['exemptions'][0]}
        - Automatic Stay: Section {self.context.bankruptcy_code_sections['automatic_stay'][0]}
        - Discharge: Sections {', '.join(self.context.bankruptcy_code_sections['discharge'])}

        FEDERAL RULES OF BANKRUPTCY PROCEDURE:
        - Filing Requirements: Rules {', '.join(self.context.bankruptcy_rules['filing'])}
        - Schedule Requirements: Rules {', '.join(self.context.bankruptcy_rules['schedules'])}
        - Means Test Rules: Rules {', '.join(self.context.bankruptcy_rules['means_test'])}
        - Creditor Claims: Rules {', '.join(self.context.bankruptcy_rules['creditor_claims'])}
        - 341 Meeting: Rules {', '.join(self.context.bankruptcy_rules['341_meeting'])}

        OFFICIAL FORMS:
        - Voluntary Petition: {self.context.official_forms['voluntary_petition']}
        - Required Schedules: {', '.join(self.context.official_forms['schedules'])}
        - Statement of Financial Affairs: {self.context.official_forms['statement_of_financial_affairs']}
        - Means Test Forms: {', '.join(self.context.official_forms['means_test'])}
        - Social Security Statement: {self.context.official_forms['social_security']}

        STATE-SPECIFIC KNOWLEDGE:
        - Homestead Exemptions: {', '.join(self.context.state_exemptions['homestead'])}
        - Wildcard Exemptions: {', '.join(self.context.state_exemptions['wildcard'])}
        - Vehicle Exemptions: {self.context.state_exemptions['vehicle'][0]}
        - Retirement Protections: {', '.join(self.context.state_exemptions['retirement'])}

        LEGAL REASONING CAPABILITIES:
        - Analyze financial documents for bankruptcy relevance
        - Determine appropriate bankruptcy chapter eligibility
        - Calculate means test requirements
        - Identify required forms and schedules
        - Assess exemption eligibility
        - Recognize common filing mistakes
        - Provide procedural guidance

        CRITICAL GUARDRAILS:
        - NEVER provide legal advice
        - NEVER guarantee bankruptcy eligibility
        - ALWAYS recommend consulting an attorney
        - ALWAYS provide legal disclaimers
        - NEVER suggest specific legal strategies
        - ALWAYS cite relevant bankruptcy code sections
        - ALWAYS explain procedural requirements

        Your responses must be:
        1. Accurate to current bankruptcy law
        2. Educational and informative
        3. Procedural rather than advisory
        4. Properly disclaimed
        5. Based on federal bankruptcy code and rules
        """
    
    def analyze_document_with_legal_context(self, file_path: str, file_type: str, bankruptcy_context: BankruptcyContext) -> Dict[str, Any]:
        """Analyze document with specialized bankruptcy law context using latest reasoning models"""
        
        # Create context-specific prompt
        context_prompt = self._create_context_specific_prompt(bankruptcy_context)
        
        # Read and encode document
        with open(file_path, "rb") as file:
            file_content = file.read()
            base64_content = base64.b64encode(file_content).decode('utf-8')
        
        # Create comprehensive analysis prompt
        analysis_prompt = f"""
        {self.expertise_context}
        
        {context_prompt}
        
        Analyze this {file_type} document for bankruptcy filing purposes. Focus on:
        1. Extracting relevant financial and legal information
        2. Mapping information to appropriate bankruptcy schedules
        3. Identifying potential issues or missing information
        4. Providing procedural guidance (not legal advice)
        
        IMPORTANT: 
        - This is for educational purposes only
        - Do not provide legal advice
        - Always recommend consulting an attorney
        - Cite relevant bankruptcy code sections when applicable
        """
        
        try:
            if file_type.lower() in ['pdf', 'image', 'jpg', 'png']:
                # Use latest GPT-4o vision model for document analysis
                response = self.openai_client.chat.completions.create(
                    model=self.vision_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": analysis_prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{file_type};base64,{base64_content}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=4000,  # Increased for complex reasoning
                    temperature=0.1,   # Low temperature for legal accuracy
                    response_format={"type": "json_object"}  # Ensure structured output
                )
            else:
                # For text-based documents, use latest reasoning model
                text_content = file_content.decode('utf-8', errors='ignore')
                response = self.openai_client.chat.completions.create(
                    model=self.primary_model,
                    messages=[
                        {"role": "system", "content": analysis_prompt},
                        {"role": "user", "content": f"Document content:\n{text_content[:8000]}"}  # Increased context
                    ],
                    max_tokens=4000,  # Increased for complex reasoning
                    temperature=0.1,   # Low temperature for legal accuracy
                    response_format={"type": "json_object"}  # Ensure structured output
                )
            
            # Extract and validate response
            extracted_info = self._parse_and_validate_response(response.choices[0].message.content, bankruptcy_context)
            
            # Add legal guardrails
            extracted_info = self._apply_legal_guardrails(extracted_info, bankruptcy_context)
            
            # Store in conversation history
            self.conversation_history.append({
                "context": bankruptcy_context.value,
                "file_path": file_path,
                "extracted_info": extracted_info,
                "timestamp": self._get_timestamp(),
                "model_used": self.primary_model if file_type.lower() not in ['pdf', 'image', 'jpg', 'png'] else self.vision_model
            })
            
            return extracted_info
            
        except Exception as e:
            return self._create_error_response(str(e), bankruptcy_context)
    
    def _create_context_specific_prompt(self, context: BankruptcyContext) -> str:
        """Create context-specific analysis prompt"""
        context_prompts = {
            BankruptcyContext.CHAPTER_7: """
            Focus on Chapter 7 liquidation bankruptcy requirements:
            - Asset analysis and exemption eligibility
            - Income qualification and means test
            - Discharge eligibility factors
            - Required schedules and forms
            - 341 meeting preparation
            """,
            
            BankruptcyContext.CHAPTER_13: """
            Focus on Chapter 13 repayment plan requirements:
            - Disposable income calculation
            - Repayment plan feasibility
            - Priority debt treatment
            - Secured debt handling
            - Plan confirmation requirements
            """,
            
            BankruptcyContext.MEANS_TEST: """
            Focus on bankruptcy means test analysis:
            - Current monthly income calculation
            - State median income comparison
            - Allowable expense deductions
            - Disposable income determination
            - Chapter 7 vs Chapter 13 eligibility
            """,
            
            BankruptcyContext.ASSET_ANALYSIS: """
            Focus on asset analysis for bankruptcy:
            - Property identification and valuation
            - Exemption eligibility assessment
            - Secured vs unsecured property
            - Asset protection strategies
            - Required disclosure requirements
            """,
            
            BankruptcyContext.LIABILITY_ANALYSIS: """
            Focus on liability analysis for bankruptcy:
            - Creditor identification and claims
            - Secured vs unsecured debt classification
            - Priority debt identification
            - Debt discharge eligibility
            - Creditor notification requirements
            """,
            
            BankruptcyContext.EXPENSE_ANALYSIS: """
            Focus on expense analysis for bankruptcy:
            - Monthly living expense calculation
            - IRS standard expense allowances
            - Actual vs standard expense comparison
            - Means test expense deductions
            - Budget planning for Chapter 13
            """,
            
            BankruptcyContext.LEGAL_ANALYSIS: """
            Focus on legal analysis for bankruptcy:
            - Previous bankruptcy filing history
            - Pending legal actions and judgments
            - Tax obligations and filing status
            - Legal compliance requirements
            - Procedural rule adherence
            """
        }
        
        return context_prompts.get(context, "")
    
    def _parse_and_validate_response(self, response: str, context: BankruptcyContext) -> Dict[str, Any]:
        """Parse and validate LLM response with legal accuracy checks"""
        try:
            # Parse JSON response (ensured by response_format)
            parsed_data = json.loads(response)
            
            # Validate legal accuracy
            validated_data = self._validate_legal_accuracy(parsed_data, context)
            
            return validated_data
                
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return self._create_structured_data_from_text(response, context)
    
    def _validate_legal_accuracy(self, data: Dict[str, Any], context: BankruptcyContext) -> Dict[str, Any]:
        """Validate legal accuracy of extracted information"""
        validated_data = data.copy()
        
        # Add validation metadata
        validated_data['legal_validation'] = {
            'validation_timestamp': self._get_timestamp(),
            'context': context.value,
            'bankruptcy_code_sections': self._identify_relevant_sections(data, context),
            'legal_disclaimers': self.context.legal_disclaimers,
            'common_mistakes': self._identify_potential_mistakes(data, context)
        }
        
        # Add confidence scoring
        validated_data['confidence_scoring'] = self._calculate_confidence_score(data, context)
        
        return validated_data
    
    def _identify_relevant_sections(self, data: Dict[str, Any], context: BankruptcyContext) -> List[str]:
        """Identify relevant bankruptcy code sections for the data"""
        relevant_sections = []
        
        if context == BankruptcyContext.MEANS_TEST:
            relevant_sections.extend(self.context.bankruptcy_code_sections['means_test'])
        
        if context in [BankruptcyContext.CHAPTER_7, BankruptcyContext.CHAPTER_13]:
            relevant_sections.extend(self.context.bankruptcy_code_sections[context.value])
        
        if 'assets' in data:
            relevant_sections.append(self.context.bankruptcy_code_sections['exemptions'][0])
        
        return relevant_sections
    
    def _identify_potential_mistakes(self, data: Dict[str, Any], context: BankruptcyContext) -> List[str]:
        """Identify potential bankruptcy filing mistakes"""
        potential_mistakes = []
        
        # Check for common issues
        if not data.get('personal_info', {}).get('ssn'):
            potential_mistakes.append("Missing Social Security Number")
        
        if not data.get('assets'):
            potential_mistakes.append("No assets listed - may indicate incomplete disclosure")
        
        if not data.get('liabilities'):
            potential_mistakes.append("No liabilities listed - may indicate incomplete disclosure")
        
        if context == BankruptcyContext.MEANS_TEST and not data.get('income'):
            potential_mistakes.append("Missing income information for means test")
        
        return potential_mistakes
    
    def _calculate_confidence_score(self, data: Dict[str, Any], context: BankruptcyContext) -> Dict[str, Any]:
        """Calculate confidence score for extracted information"""
        confidence_factors = {
            'completeness': 0.0,
            'accuracy': 0.0,
            'legal_compliance': 0.0,
            'overall_score': 0.0
        }
        
        # Calculate completeness score
        required_fields = self._get_required_fields_for_context(context)
        present_fields = sum(1 for field in required_fields if self._field_present(data, field))
        confidence_factors['completeness'] = present_fields / len(required_fields) if required_fields else 0.0
        
        # Calculate accuracy score (based on data consistency)
        confidence_factors['accuracy'] = self._assess_data_consistency(data)
        
        # Calculate legal compliance score
        confidence_factors['legal_compliance'] = self._assess_legal_compliance(data, context)
        
        # Calculate overall score
        confidence_factors['overall_score'] = (
            confidence_factors['completeness'] * 0.4 +
            confidence_factors['accuracy'] * 0.3 +
            confidence_factors['legal_compliance'] * 0.3
        )
        
        return confidence_factors
    
    def _get_required_fields_for_context(self, context: BankruptcyContext) -> List[str]:
        """Get required fields for specific bankruptcy context"""
        field_mappings = {
            BankruptcyContext.CHAPTER_7: ['personal_info', 'income', 'assets', 'liabilities', 'expenses'],
            BankruptcyContext.CHAPTER_13: ['personal_info', 'income', 'assets', 'liabilities', 'expenses', 'disposable_income'],
            BankruptcyContext.MEANS_TEST: ['income', 'household_size', 'expenses', 'secured_debts'],
            BankruptcyContext.ASSET_ANALYSIS: ['assets', 'property_values', 'exemption_claims'],
            BankruptcyContext.LIABILITY_ANALYSIS: ['liabilities', 'creditor_info', 'debt_amounts'],
            BankruptcyContext.EXPENSE_ANALYSIS: ['expenses', 'monthly_costs', 'income'],
            BankruptcyContext.LEGAL_ANALYSIS: ['legal_history', 'tax_status', 'court_actions']
        }
        
        return field_mappings.get(context, [])
    
    def _field_present(self, data: Dict[str, Any], field: str) -> bool:
        """Check if a field is present and has meaningful data"""
        if field not in data:
            return False
        
        field_data = data[field]
        
        if isinstance(field_data, dict):
            return len(field_data) > 0
        elif isinstance(field_data, list):
            return len(field_data) > 0
        elif isinstance(field_data, str):
            return len(field_data.strip()) > 0
        elif isinstance(field_data, (int, float)):
            return field_data > 0
        
        return False
    
    def _assess_data_consistency(self, data: Dict[str, Any]) -> float:
        """Assess consistency of extracted data"""
        consistency_score = 1.0
        
        # Check for logical inconsistencies
        if 'income' in data and 'expenses' in data:
            income = float(data.get('income', 0))
            expenses = float(data.get('expenses', 0))
            
            if income > 0 and expenses > income * 2:
                consistency_score *= 0.8  # High expenses relative to income
        
        if 'assets' in data and 'liabilities' in data:
            assets = sum(float(asset.get('value', 0)) for asset in data.get('assets', []))
            liabilities = sum(float(liability.get('amount', 0)) for liability in data.get('liabilities', []))
            
            if assets > 0 and liabilities > assets * 10:
                consistency_score *= 0.9  # Very high debt-to-asset ratio
        
        return consistency_score
    
    def _assess_legal_compliance(self, data: Dict[str, Any], context: BankruptcyContext) -> float:
        """Assess legal compliance of extracted data"""
        compliance_score = 1.0
        
        # Check for required bankruptcy information
        if context in [BankruptcyContext.CHAPTER_7, BankruptcyContext.CHAPTER_13]:
            if not data.get('personal_info'):
                compliance_score *= 0.8
            
            if not data.get('assets'):
                compliance_score *= 0.7
            
            if not data.get('liabilities'):
                compliance_score *= 0.7
        
        # Check for means test compliance
        if context == BankruptcyContext.MEANS_TEST:
            if not data.get('income'):
                compliance_score *= 0.6
            
            if not data.get('household_size'):
                compliance_score *= 0.8
        
        return compliance_score
    
    def _apply_legal_guardrails(self, data: Dict[str, Any], context: BankruptcyContext) -> Dict[str, Any]:
        """Apply legal guardrails to extracted information"""
        guarded_data = data.copy()
        
        # Add legal disclaimers
        guarded_data['legal_disclaimers'] = {
            'no_legal_advice': "This analysis is for educational purposes only and does not constitute legal advice",
            'consult_attorney': "Always consult with a qualified bankruptcy attorney before filing",
            'no_guarantees': "No guarantee of bankruptcy eligibility or discharge",
            'informational_only': "Information provided is for bankruptcy filing preparation only"
        }
        
        # Add procedural guidance (not legal advice)
        guarded_data['procedural_guidance'] = self._generate_procedural_guidance(context)
        
        # Add required forms and schedules
        guarded_data['required_forms'] = self._identify_required_forms(context)
        
        return guarded_data
    
    def _generate_procedural_guidance(self, context: BankruptcyContext) -> Dict[str, Any]:
        """Generate procedural guidance for bankruptcy filing"""
        guidance = {
            'next_steps': [],
            'required_actions': [],
            'timeline': {},
            'warnings': []
        }
        
        if context == BankruptcyContext.CHAPTER_7:
            guidance['next_steps'] = [
                "Complete credit counseling course",
                "Gather all financial documents",
                "Prepare bankruptcy petition and schedules",
                "File with bankruptcy court",
                "Attend 341 meeting of creditors"
            ]
            
            guidance['required_actions'] = [
                "File Form 101 (Voluntary Petition)",
                "Complete all required schedules",
                "File Form 122A-1 (Means Test)",
                "Provide creditor matrix",
                "Pay filing fee or request waiver"
            ]
            
            guidance['timeline'] = {
                'credit_counseling': "Must complete before filing",
                'filing': "Immediate effect of automatic stay",
                '341_meeting': "20-40 days after filing",
                'discharge': "60-90 days after 341 meeting"
            }
        
        elif context == BankruptcyContext.CHAPTER_13:
            guidance['next_steps'] = [
                "Complete credit counseling course",
                "Prepare Chapter 13 repayment plan",
                "File bankruptcy petition and schedules",
                "Attend 341 meeting",
                "Attend confirmation hearing"
            ]
            
            guidance['required_actions'] = [
                "File Form 101 (Voluntary Petition)",
                "Complete all required schedules",
                "File Form 122C-1 (Chapter 13 Means Test)",
                "File Form 122C-2 (Disposable Income)",
                "Submit repayment plan"
            ]
            
            guidance['timeline'] = {
                'credit_counseling': "Must complete before filing",
                'filing': "Immediate effect of automatic stay",
                '341_meeting': "20-40 days after filing",
                'confirmation_hearing': "45-90 days after filing",
                'plan_completion': "3-5 years"
            }
        
        guidance['warnings'] = [
            "Bankruptcy has serious long-term consequences",
            "Consult with qualified bankruptcy attorney",
            "Provide complete and accurate information",
            "Attend all required court hearings",
            "Complete required debtor education course"
        ]
        
        return guidance
    
    def _identify_required_forms(self, context: BankruptcyContext) -> List[str]:
        """Identify required bankruptcy forms for specific context"""
        base_forms = [
            self.context.official_forms['voluntary_petition'],
            self.context.official_forms['social_security']
        ]
        
        if context == BankruptcyContext.CHAPTER_7:
            base_forms.extend([
                "Form 122A-1 (Statement of Current Monthly Income)",
                "Form 122A-2 (Means Test Calculation)"
            ])
        
        elif context == BankruptcyContext.CHAPTER_13:
            base_forms.extend([
                "Form 122C-1 (Chapter 13 Statement of Current Monthly Income)",
                "Form 122C-2 (Chapter 13 Calculation of Disposable Income)"
            ])
        
        # All contexts require these forms
        base_forms.extend([
            "Form 106A/B (Property)",
            "Form 106C (Exemptions)",
            "Form 106D (Secured Claims)",
            "Form 106E/F (Unsecured Claims)",
            "Form 106G (Executory Contracts)",
            "Form 106H (Codebtors)",
            "Form 106I (Income)",
            "Form 106J (Expenses)",
            "Form 107 (Statement of Financial Affairs)"
        ])
        
        return base_forms
    
    def _create_structured_data_from_text(self, text: str, context: BankruptcyContext) -> Dict[str, Any]:
        """Create structured data from text response when JSON parsing fails"""
        structured_data = {
            "extraction_method": "text_parsing_fallback",
            "context": context.value,
            "raw_text": text,
            "personal_info": {},
            "employment": {},
            "income": {},
            "assets": [],
            "liabilities": [],
            "expenses": {},
            "legal_actions": [],
            "tax_info": {},
            "bankruptcy_history": {}
        }
        
        # Simple text parsing logic
        lines = text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect categories
            if 'personal' in line.lower() or 'name' in line.lower() or 'ssn' in line.lower():
                current_category = 'personal_info'
            elif 'employment' in line.lower() or 'employer' in line.lower():
                current_category = 'employment'
            elif 'income' in line.lower() or 'salary' in line.lower() or 'wages' in line.lower():
                current_category = 'income'
            elif 'asset' in line.lower() or 'property' in line.lower() or 'vehicle' in line.lower():
                current_category = 'assets'
            elif 'debt' in line.lower() or 'liability' in line.lower() or 'creditor' in line.lower():
                current_category = 'liabilities'
            elif 'expense' in line.lower() or 'payment' in line.lower():
                current_category = 'expenses'
            elif 'legal' in line.lower() or 'judgment' in line.lower() or 'lawsuit' in line.lower():
                current_category = 'legal_actions'
            elif 'tax' in line.lower():
                current_category = 'tax_info'
            elif 'bankruptcy' in line.lower():
                current_category = 'bankruptcy_history'
            
            # Extract information based on category
            if current_category and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if current_category in ['assets', 'liabilities', 'legal_actions']:
                    structured_data[current_category].append({key: value})
                else:
                    structured_data[current_category][key] = value
        
        return structured_data
    
    def _create_error_response(self, error_message: str, context: BankruptcyContext) -> Dict[str, Any]:
        """Create error response when document analysis fails"""
        return {
            "error": True,
            "error_message": error_message,
            "context": context.value,
            "extraction_method": "error_fallback",
            "legal_disclaimers": self.context.legal_disclaimers,
            "recommendation": "Manual review of document required. Consult with bankruptcy attorney for assistance."
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history for audit purposes"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def generate_bankruptcy_summary(self, all_extracted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive bankruptcy filing summary using latest reasoning model"""
        summary = {
            "filing_summary": {},
            "missing_information": [],
            "required_forms": [],
            "procedural_checklist": [],
            "legal_warnings": [],
            "next_steps": []
        }
        
        # Consolidate all extracted information
        consolidated_data = self._consolidate_extracted_data(all_extracted_data)
        
        # Generate filing summary
        summary['filing_summary'] = self._generate_filing_summary(consolidated_data)
        
        # Identify missing information
        summary['missing_information'] = self._identify_missing_information(consolidated_data)
        
        # Determine required forms
        summary['required_forms'] = self._determine_required_forms(consolidated_data)
        
        # Generate procedural checklist
        summary['procedural_checklist'] = self._generate_procedural_checklist(consolidated_data)
        
        # Add legal warnings
        summary['legal_warnings'] = self.context.legal_disclaimers
        
        # Generate next steps
        summary['next_steps'] = self._generate_next_steps(consolidated_data)
        
        return summary
    
    def _consolidate_extracted_data(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate all extracted data into unified structure"""
        consolidated = {
            "personal_info": {},
            "employment": {},
            "income": {},
            "assets": [],
            "liabilities": [],
            "expenses": {},
            "legal_actions": [],
            "tax_info": {},
            "bankruptcy_history": {}
        }
        
        for data in all_data:
            if not data.get('error'):
                for category, category_data in data.items():
                    if category in consolidated and isinstance(category_data, dict):
                        consolidated[category].update(category_data)
                    elif category in consolidated and isinstance(category_data, list):
                        consolidated[category].extend(category_data)
        
        return consolidated
    
    def _generate_filing_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate bankruptcy filing summary"""
        return {
            "case_type_recommendation": self._determine_case_type_recommendation(data),
            "means_test_eligibility": self._assess_means_test_eligibility(data),
            "asset_summary": self._generate_asset_summary(data),
            "liability_summary": self._generate_liability_summary(data),
            "income_summary": self._generate_income_summary(data),
            "expense_summary": self._generate_expense_summary(data)
        }
    
    def _determine_case_type_recommendation(self, data: Dict[str, Any]) -> str:
        """Determine recommended bankruptcy chapter based on data"""
        # This is a simplified recommendation - actual determination requires legal analysis
        income = float(data.get('income', {}).get('monthly_amount', 0))
        assets = len(data.get('assets', []))
        liabilities = len(data.get('liabilities', []))
        
        if income < 3000 and assets < 5 and liabilities > 10:
            return "Chapter 7 may be appropriate (consult attorney)"
        elif income > 5000 or assets > 10:
            return "Chapter 13 may be required (consult attorney)"
        else:
            return "Case type determination requires legal analysis"
    
    def _assess_means_test_eligibility(self, data: Dict[str, Any]) -> str:
        """Assess means test eligibility"""
        income = float(data.get('income', {}).get('monthly_amount', 0))
        
        if income == 0:
            return "Income information required for means test"
        elif income < 3000:
            return "Likely below median income (consult attorney)"
        else:
            return "Means test calculation required (consult attorney)"
    
    def _generate_asset_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate asset summary"""
        assets = data.get('assets', [])
        total_value = sum(float(asset.get('value', 0)) for asset in assets)
        
        return {
            "total_assets": len(assets),
            "total_value": total_value,
            "asset_types": list(set(asset.get('type', 'unknown') for asset in assets)),
            "exemption_considerations": "Consult attorney for exemption planning"
        }
    
    def _generate_liability_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate liability summary"""
        liabilities = data.get('liabilities', [])
        total_debt = sum(float(liability.get('amount', 0)) for liability in liabilities)
        
        secured_count = len([l for l in liabilities if l.get('type') == 'secured'])
        unsecured_count = len([l for l in liabilities if l.get('type') == 'unsecured'])
        
        return {
            "total_liabilities": len(liabilities),
            "total_debt": total_debt,
            "secured_debts": secured_count,
            "unsecured_debts": unsecured_count,
            "priority_debts": len([l for l in liabilities if l.get('type') == 'priority'])
        }
    
    def _generate_income_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate income summary"""
        income_data = data.get('income', {})
        
        return {
            "primary_income": income_data.get('monthly_amount', 'Not provided'),
            "additional_sources": len(income_data.get('additional_sources', [])),
            "income_stability": "Assessment required",
            "means_test_ready": bool(income_data.get('monthly_amount'))
        }
    
    def _generate_expense_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate expense summary"""
        expenses = data.get('expenses', {})
        
        return {
            "expense_categories": len(expenses),
            "total_monthly_expenses": sum(float(expenses.get(key, 0)) for key in expenses if isinstance(expenses.get(key), (int, float))),
            "expense_analysis_ready": len(expenses) > 5
        }
    
    def _identify_missing_information(self, data: Dict[str, Any]) -> List[str]:
        """Identify missing information needed for bankruptcy filing"""
        missing = []
        
        if not data.get('personal_info'):
            missing.append("Complete personal identification information")
        
        if not data.get('income'):
            missing.append("Income information for means test")
        
        if not data.get('assets'):
            missing.append("Asset and property information")
        
        if not data.get('liabilities'):
            missing.append("Debt and creditor information")
        
        if not data.get('expenses'):
            missing.append("Monthly expense information")
        
        return missing
    
    def _determine_required_forms(self, data: Dict[str, Any]) -> List[str]:
        """Determine required bankruptcy forms"""
        base_forms = [
            "Form 101 (Voluntary Petition)",
            "Form 121 (Social Security Statement)",
            "Form 106A/B (Property)",
            "Form 106C (Exemptions)",
            "Form 106D (Secured Claims)",
            "Form 106E/F (Unsecured Claims)",
            "Form 106G (Executory Contracts)",
            "Form 106H (Codebtors)",
            "Form 106I (Income)",
            "Form 106J (Expenses)",
            "Form 107 (Statement of Financial Affairs)"
        ]
        
        # Add means test forms
        if data.get('income'):
            base_forms.extend([
                "Form 122A-1 (Means Test - Chapter 7)",
                "Form 122C-1 (Means Test - Chapter 13)"
            ])
        
        return base_forms
    
    def _generate_procedural_checklist(self, data: Dict[str, Any]) -> List[str]:
        """Generate procedural checklist for bankruptcy filing"""
        checklist = [
            "Complete credit counseling course",
            "Gather all financial documents",
            "Prepare bankruptcy petition",
            "Complete all required schedules",
            "File with bankruptcy court",
            "Pay filing fee or request waiver",
            "Attend 341 meeting of creditors",
            "Complete debtor education course"
        ]
        
        return checklist
    
    def _generate_next_steps(self, data: Dict[str, Any]) -> List[str]:
        """Generate next steps for bankruptcy filing"""
        next_steps = [
            "Consult with qualified bankruptcy attorney",
            "Complete credit counseling requirement",
            "Organize financial documents",
            "Prepare bankruptcy petition",
            "File bankruptcy case",
            "Attend required court hearings"
        ]
        
        return next_steps 
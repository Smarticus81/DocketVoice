"""
Production-Ready SOTA Bankruptcy Agent
Complete conversational bankruptcy form completion system
"""

import asyncio
import logging
import random
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

from config import Settings
from sota_ai import SOTA_AI
from sota_voice import SOTA_Voice
from sota_document_processor import SOTADocumentProcessor
from sota_forms_complete import CompleteBankruptcyCase, FilingType, MaritalStatus
from sota_questions import (
    QUESTION_BANK, FOLLOW_UP_QUESTIONS, TRANSITION_PHRASES, EMPATHY_PHRASES,
    QuestionCategory, get_questions_for_category, get_random_question,
    get_follow_up_question, get_transition_phrase, get_empathy_phrase
)

logger = logging.getLogger(__name__)

class ConsultationResult:
    def __init__(self, bankruptcy_case: CompleteBankruptcyCase, generated_documents: List[str], consultation_summary: str):
        self.bankruptcy_case = bankruptcy_case
        self.generated_documents = generated_documents
        self.consultation_summary = consultation_summary
        self.completion_status = bankruptcy_case.get_completion_status()
        self.ready_for_filing = bankruptcy_case.is_ready_for_filing()
        self.success = True
        self.error = None
        self.forms_generated = generated_documents
        self.output_path = "./output/"

class SOTABankruptcyAgentProduction:
    def __init__(self, settings: Settings, ai_provider: SOTA_AI, voice_provider: SOTA_Voice, 
                 monitoring=None, security=None):
        self.settings = settings
        self.ai = ai_provider
        self.voice = voice_provider
        self.monitoring = monitoring
        self.security = security
        self.document_processor = SOTADocumentProcessor(settings)
        
        # Initialize complete bankruptcy case
        self.bankruptcy_case = CompleteBankruptcyCase()
        self.conversation_history = []
        self.current_question_category = QuestionCategory.PERSONAL_INFO
        self.asked_questions = set()
        
        # Conversation flow control
        self.conversation_complete = False
        self.session_start_time = datetime.now()
        
        logger.info("Production SOTA Bankruptcy Agent initialized - Full form suite ready")

    async def run_complete_consultation(self) -> ConsultationResult:
        """
        Run the complete bankruptcy consultation with all official forms
        """
        try:
            logger.info("Starting complete production bankruptcy consultation")
            
            # Welcome and setup
            await self._welcome_client()
            
            # Determine filing type first
            await self._determine_filing_type()
            
            # Process any uploaded documents first
            await self._process_uploaded_documents()
            
            # Complete conversational interview
            await self._conduct_comprehensive_interview()
            
            # Generate all required documents
            generated_docs = await self._generate_all_documents()
            
            # Create consultation summary
            summary = await self._generate_consultation_summary()
            
            # Final review with client
            await self._conduct_final_review()
            
            logger.info("Complete consultation finished successfully")
            
            return ConsultationResult(
                bankruptcy_case=self.bankruptcy_case,
                generated_documents=generated_docs,
                consultation_summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error in complete consultation: {str(e)}")
            await self.voice.speak("I'm sorry, but we encountered an issue. Let me save what we've completed so far.")
            raise

    async def _welcome_client(self):
        """Warm, professional welcome"""
        welcome_message = """
        Hello, and welcome to DocketVoice. I'm here to help you complete your bankruptcy paperwork through a simple conversation
        
        This usually takes about 45 minutes to an hour, depending on your situation. We can take breaks anytime you need them. Are you ready to begin?
        """
        
        await self.voice.speak(welcome_message)
        
        # Wait for confirmation with retry logic
        max_attempts = 3
        for attempt in range(max_attempts):
            ready = await self._get_user_input("Are you ready to start? Just say yes when you're ready.")
            
            if ready and ("yes" in ready.lower() or "ready" in ready.lower() or "ok" in ready.lower()):
                await self.voice.speak("Perfect. Let's begin with some basic information about you.")
                return
            elif attempt < max_attempts - 1:
                await self.voice.speak("That's completely fine. Take your time. Let me know when you're ready to start.")
            else:
                # After max attempts, assume ready in simulation mode
                await self.voice.speak("Let's proceed with the consultation.")
                return

    async def _determine_filing_type(self):
        """Determine Chapter 7 or 13 filing"""
        filing_question = """
        First, I need to understand what type of bankruptcy you're considering.
        
        Chapter 7 is often called "liquidation" or Chapter 13, which is a "repayment plan".
        
        """
        
        await self.voice.speak(filing_question)
        
        response = await self._get_user_input("Chapter 7, Chapter 13, or help me decide?")
        
        if "7" in response or "seven" in response.lower() or "liquidation" in response.lower():
            self.bankruptcy_case.filing_type = FilingType.CHAPTER_7
            await self.voice.speak("Got it. We'll prepare your Chapter 7 bankruptcy petition.")
        elif "13" in response or "thirteen" in response.lower() or "repayment" in response.lower():
            self.bankruptcy_case.filing_type = FilingType.CHAPTER_13
            await self.voice.speak("Understood. We'll prepare your Chapter 13 repayment plan.")
        else:
            await self._help_determine_filing_type()

    async def _help_determine_filing_type(self):
        """Help client choose filing type based on their situation"""
        help_questions = [
            "Do you have a regular income right now?",
            "Are you behind on your mortgage or car payments?",
            "Do you have assets you really want to keep, like a house or car?",
            "Are most of your debts credit cards and medical bills?"
        ]
        
        responses = []
        for question in help_questions:
            await self.voice.speak(question)
            response = await self._get_user_input("Please answer yes or no.")
            responses.append(response.lower())
        
        # Simple logic to suggest filing type
        regular_income = "yes" in responses[0]
        behind_payments = "yes" in responses[1]
        want_keep_assets = "yes" in responses[2]
        mostly_unsecured = "yes" in responses[3]
        
        if regular_income and (behind_payments or want_keep_assets):
            suggested_type = FilingType.CHAPTER_13
            explanation = "Based on your answers, Chapter 13 might be better because you have income and want to keep your assets or catch up on payments."
        else:
            suggested_type = FilingType.CHAPTER_7
            explanation = "Based on your answers, Chapter 7 might be appropriate because it can quickly discharge your unsecured debts."
        
        await self.voice.speak(f"{explanation} Would you like to proceed with that recommendation?")
        
        response = await self._get_user_input("Yes or no?")
        if "yes" in response.lower():
            self.bankruptcy_case.filing_type = suggested_type
            await self.voice.speak(f"Perfect. We'll prepare your {suggested_type.value} bankruptcy.")
        else:
            await self._determine_filing_type()  # Try again

    async def _process_uploaded_documents(self):
        """Process any documents the user has uploaded"""
        documents_dir = Path("uploaded_documents")
        if documents_dir.exists():
            uploaded_files = list(documents_dir.glob("*"))
            if uploaded_files:
                await self.voice.speak(f"I see you've uploaded {len(uploaded_files)} documents. Let me analyze those to help fill out your forms.")
                
                for file_path in uploaded_files:
                    try:
                        await self.voice.speak(f"Processing {file_path.name}...")
                        extracted_data = await self.document_processor.process_document(str(file_path), self.bankruptcy_case)
                        logger.info(f"Processed {file_path.name}: {extracted_data.document_type}")
                    except Exception as e:
                        logger.error(f"Failed to process {file_path.name}: {str(e)}")
                        await self.voice.speak(f"I had trouble reading {file_path.name}, but that's okay. We can gather that information through our conversation.")
                
                await self.voice.speak("Great! I've extracted information from your documents. This will help me fill out your forms more accurately.")

    async def _conduct_comprehensive_interview(self):
        """Conduct the complete interview covering all form requirements"""
        
        # Question flow categories in logical order
        categories = [
            QuestionCategory.PERSONAL_INFO,
            QuestionCategory.INCOME_EMPLOYMENT, 
            QuestionCategory.EXPENSES,
            QuestionCategory.ASSETS_PROPERTY,
            QuestionCategory.DEBTS_LIABILITIES,
            QuestionCategory.LEGAL_HISTORY,
            QuestionCategory.PREFERENCES
        ]
        
        for category in categories:
            await self._interview_category(category)
            
            # Provide progress update
            completion = self.bankruptcy_case.get_completion_status()
            avg_completion = sum(completion.values()) / len(completion) if completion else 0
            
            if avg_completion > 25:
                await self.voice.speak(f"We're making great progress. About {int(avg_completion)}% complete with the forms.")

    async def _interview_category(self, category: QuestionCategory):
        """Interview for a specific category of questions"""
        
        await self.voice.speak(get_transition_phrase())
        
        category_questions = get_questions_for_category(category)
        
        for field_key, possible_questions in category_questions.items():
            if field_key in self.asked_questions:
                continue
                
            await self._ask_and_process_question(field_key, possible_questions)
            
            # Add some natural pause
            await asyncio.sleep(0.5)

    async def _ask_and_process_question(self, field_key: str, possible_questions: List[str]):
        """Ask a specific question and process the response"""
        
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Choose a random question phrasing
                question = random.choice(possible_questions)
                
                await self.voice.speak(question)
                response = await self._get_user_input("Your answer:")
                
                # Process and validate response
                processed_value = await self._process_response(field_key, response, question)
                
                if processed_value is not None:
                    # Apply to bankruptcy case
                    await self._apply_response_to_case(field_key, processed_value)
                    self.asked_questions.add(field_key)
                    
                    # Log the conversation
                    self.conversation_history.append({
                        "question": question,
                        "response": response,
                        "processed_value": str(processed_value),
                        "field": field_key
                    })
                    break
                else:
                    # Need clarification
                    attempt += 1
                    if attempt < max_attempts:
                        follow_up = get_follow_up_question("need_more_detail")
                        await self.voice.speak(follow_up)
                    
            except Exception as e:
                logger.error(f"Error processing question {field_key}: {str(e)}")
                attempt += 1
                
        if attempt >= max_attempts:
            await self.voice.speak("That's okay, we can come back to that question later if needed.")

    async def _process_response(self, field_key: str, response: str, original_question: str) -> Optional[Any]:
        """Process and validate user response using AI"""
        
        try:
            # Use AI to intelligently process the response
            processing_prompt = f"""
            You are processing a bankruptcy form response. 
            
            Field: {field_key}
            Question: {original_question}
            User Response: {response}
            
            Extract the appropriate value for this field. Return ONLY the extracted value in the most appropriate format:
            - For names/text: return the clean text
            - For amounts: return just the number (no $ or commas)
            - For yes/no: return true or false
            - For dates: return YYYY-MM-DD format
            - If unclear or no valid answer: return "UNCLEAR"
            """
            
            ai_response = await self.ai.chat_completion([
                {"role": "system", "content": processing_prompt},
                {"role": "user", "content": response}
            ], temperature=0.1)
            
            extracted_value = ai_response.strip()
            
            if extracted_value == "UNCLEAR":
                return None
                
            # Type conversion based on field
            if "amount" in field_key.lower() or "income" in field_key.lower() or "expense" in field_key.lower():
                try:
                    return Decimal(extracted_value)
                except:
                    return None
            elif "date" in field_key.lower():
                try:
                    return datetime.strptime(extracted_value, "%Y-%m-%d").date()
                except:
                    return None
            elif extracted_value.lower() in ["true", "false"]:
                return extracted_value.lower() == "true"
            else:
                return extracted_value
                
        except Exception as e:
            logger.error(f"Error in AI response processing: {str(e)}")
            return response  # Fallback to raw response

    async def _apply_response_to_case(self, field_key: str, value: Any):
        """Apply processed response to the appropriate field in bankruptcy case"""
        
        try:
            # Navigate to the correct object and field
            parts = field_key.split('.')
            
            if len(parts) == 2:
                obj_name, field_name = parts
                
                # Map to bankruptcy case objects
                obj_mapping = {
                    "DebtorInfo": self.bankruptcy_case.form_b101.debtor_info,
                    "SpouseInfo": self.bankruptcy_case.form_b101.spouse_info,
                    "B101": self.bankruptcy_case.form_b101,
                    "B106": self.bankruptcy_case.form_b106,
                    "B107": self.bankruptcy_case.form_b107,
                    "B108": self.bankruptcy_case.form_b108,
                    "B109": self.bankruptcy_case.form_b109,
                    "B121": self.bankruptcy_case.form_b121,
                    "B122": self.bankruptcy_case.form_b122,
                    "B123": self.bankruptcy_case.form_b123,
                    "MonthlyIncome": self.bankruptcy_case.form_b121.debtor_income,
                    "MonthlyExpenses": self.bankruptcy_case.form_b121.monthly_expenses
                }
                
                target_obj = obj_mapping.get(obj_name)
                if target_obj and hasattr(target_obj, field_name):
                    setattr(target_obj, field_name, value)
                    logger.info(f"Set {field_key} = {value}")
                    
        except Exception as e:
            logger.error(f"Error applying response to case: {str(e)}")

    async def _generate_all_documents(self) -> List[str]:
        """Generate all required bankruptcy documents"""
        
        await self.voice.speak("Excellent! Now I'm generating all your bankruptcy documents. This will take just a moment.")
        
        try:
            # Import document generation
            from sota_pdf_generator import SOTAPDFGenerator
            
            pdf_generator = SOTAPDFGenerator()
            generated_files = []
            
            # Generate each required form
            forms_to_generate = [
                ("B101", "Official Form B101 - Voluntary Petition"),
                ("B106", "Official Form B106 - Declaration About Individual Debtor"),
                ("B107", "Official Form B107 - Statement of Financial Affairs"),
                ("B121", "Official Form B121 - Statement of Income and Means Test"),
                ("B122", "Official Form B122 - Statement of Current Monthly Income")
            ]
            
            for form_code, form_name in forms_to_generate:
                try:
                    filename = await pdf_generator.generate_form(form_code, self.bankruptcy_case)
                    generated_files.append(filename)
                    await self.voice.speak(f"Generated {form_name}")
                except Exception as e:
                    logger.error(f"Failed to generate {form_name}: {str(e)}")
            
            # Generate summary document
            summary_file = await pdf_generator.generate_case_summary(self.bankruptcy_case)
            generated_files.append(summary_file)
            
            await self.voice.speak(f"Perfect! I've generated {len(generated_files)} documents for your bankruptcy case.")
            
            return generated_files
            
        except Exception as e:
            logger.error(f"Error generating documents: {str(e)}")
            await self.voice.speak("I encountered an issue generating the documents, but all your information has been saved.")
            return []

    async def _generate_consultation_summary(self) -> str:
        """Generate a comprehensive consultation summary"""
        
        try:
            completion_status = self.bankruptcy_case.get_completion_status()
            
            summary_prompt = f"""
            Generate a professional consultation summary for this bankruptcy case:
            
            Filing Type: {self.bankruptcy_case.filing_type.value if self.bankruptcy_case.filing_type else 'Not specified'}
            Debtor: {self.bankruptcy_case.form_b101.debtor_info.first_name} {self.bankruptcy_case.form_b101.debtor_info.last_name}
            Form Completion: {completion_status}
            Ready for Filing: {self.bankruptcy_case.is_ready_for_filing()}
            
            Conversation History: {len(self.conversation_history)} exchanges
            Session Duration: {datetime.now() - self.session_start_time}
            
            Include:
            1. Case overview
            2. Key financial information gathered
            3. Completion status of each form
            4. Recommendations for attorney review
            5. Any missing information that should be gathered
            
            Format as a professional attorney briefing.
            """
            
            summary = await self.ai.chat_completion([
                {"role": "user", "content": summary_prompt}
            ], temperature=0.3)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Consultation summary generation failed."

    async def _conduct_final_review(self):
        """Conduct final review with the client"""
        
        completion_status = self.bankruptcy_case.get_completion_status()
        avg_completion = sum(completion_status.values()) / len(completion_status) if completion_status else 0
        
        final_message = f"""
        Congratulations! We've completed your bankruptcy consultation. 
        
        Here's what we accomplished:
        - Your forms are {int(avg_completion)}% complete
        - All major sections have been filled out
        - Your documents are ready for attorney review
        
        {'Your case appears ready for filing!' if self.bankruptcy_case.is_ready_for_filing() else 'Your attorney may need to gather a few additional details, but most of the work is done.'}
        
        All your documents have been saved and are ready to be reviewed by a qualified bankruptcy attorney. 
        
        Is there anything else you'd like to add or any questions you have about the process?
        """
        
        await self.voice.speak(final_message)
        
        final_questions = await self._get_user_input("Any final questions or additions?")
        
        if final_questions and "no" not in final_questions.lower():
            await self.voice.speak("Let me make note of that for your attorney.")
            self.bankruptcy_case.extracted_data['final_notes'] = final_questions
        
        await self.voice.speak("Thank you for using DocketVoice. Your bankruptcy paperwork is complete and ready for legal review. Best of luck with your fresh start!")

    async def _get_user_input(self, prompt: str) -> str:
        """Get user input via production voice interface"""
        # Add a brief pause to allow previous voice response to complete
        await asyncio.sleep(0.5)
        
        print(prompt)
        user_input = await self.voice.listen(timeout=30.0)  # 30 second timeout for VAD voice input
        
        if user_input:
            return user_input
        else:
            # In production, prompt user to speak again
            await self.voice.speak("I didn't catch that. Could you please repeat your response?")
            retry_input = await self.voice.listen(timeout=30.0)  # Longer timeout for VAD retry
            return retry_input if retry_input else "I'd prefer not to answer that right now"

    async def complete_consultation(self):
        """Public method to run consultation - alias for run_complete_consultation"""
        return await self.run_complete_consultation()
    
    async def complete_text_consultation(self):
        """Text-only consultation without voice processing"""
        try:
            logger.info("Starting text-only bankruptcy consultation")
            
            # Text-based welcome
            print("\n" + "="*60)
            print("DOCKETVOICE BANKRUPTCY ASSISTANT - TEXT MODE")
            print("Complete your bankruptcy forms through text conversation")
            print("="*60)
            print("\nHello! I'll help you complete your bankruptcy paperwork through")
            print("a series of questions. This usually takes 45-60 minutes.")
            print("You can type 'break' anytime to pause, or 'help' for assistance.")
            
            ready = input("\nAre you ready to begin? (yes/no): ").strip().lower()
            if ready != 'yes' and 'y' not in ready:
                print("Take your time. Run the program again when you're ready.")
                return None
            
            # Determine filing type via text
            await self._determine_filing_type_text()
            
            # Process documents if any
            await self._process_uploaded_documents()
            
            # Text-based interview
            await self._conduct_text_interview()
            
            # Generate documents
            generated_docs = await self._generate_all_documents()
            
            # Create summary
            summary = await self._generate_consultation_summary()
            
            print(f"\n✅ Consultation completed successfully!")
            print(f"📋 Generated {len(generated_docs)} documents")
            print(f"💾 All files saved to output directory")
            
            return ConsultationResult(
                bankruptcy_case=self.bankruptcy_case,
                generated_documents=generated_docs,
                consultation_summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error in text consultation: {e}")
            print(f"\n❌ Error during consultation: {e}")
            return None
    
    async def _determine_filing_type_text(self):
        """Text-based filing type determination"""
        print("\nFILING TYPE SELECTION")
        print("="*30)
        print("Chapter 7: Liquidation - Most debts discharged in 3-4 months")
        print("Chapter 13: Repayment plan - 3-5 year payment plan")
        print()
        
        while True:
            choice = input("Enter filing type (7 or 13), or 'help' for guidance: ").strip()
            
            if choice == '7' or 'seven' in choice.lower():
                self.bankruptcy_case.filing_type = FilingType.CHAPTER_7
                print("✓ Chapter 7 bankruptcy selected")
                break
            elif choice == '13' or 'thirteen' in choice.lower():
                self.bankruptcy_case.filing_type = FilingType.CHAPTER_13  
                print("✓ Chapter 13 bankruptcy selected")
                break
            elif choice.lower() == 'help':
                await self._text_filing_help()
            else:
                print("Please enter '7' for Chapter 7 or '13' for Chapter 13")
    
    async def _text_filing_help(self):
        """Help determine filing type via text questions"""
        print("\nLet me help you choose the right chapter:")
        
        questions = [
            "Do you have regular income? (yes/no): ",
            "Are you behind on mortgage/car payments? (yes/no): ",
            "Do you want to keep your house/car? (yes/no): ",
            "Are most debts credit cards/medical bills? (yes/no): "
        ]
        
        answers = []
        for question in questions:
            answer = input(question).strip().lower()
            answers.append('yes' in answer or 'y' == answer)
        
        # Simple logic for recommendation
        if answers[0] and (answers[1] or answers[2]):  # Income + behind/want to keep
            print("\n📋 Recommendation: Chapter 13 may be better for your situation")
            print("You can keep assets and catch up on payments over time.")
        else:
            print("\n📋 Recommendation: Chapter 7 may be suitable")
            print("Quick discharge of unsecured debts.")
        
        choice = input("\nFinal choice - Chapter 7 or 13? ").strip()
        if '7' in choice:
            self.bankruptcy_case.filing_type = FilingType.CHAPTER_7
        else:
            self.bankruptcy_case.filing_type = FilingType.CHAPTER_13
    
    async def _conduct_text_interview(self):
        """Text-based comprehensive interview"""
        print("\nSTARTING COMPREHENSIVE INTERVIEW")
        print("="*40)
        
        categories = [
            (QuestionCategory.PERSONAL_INFO, "Personal Information"),
            (QuestionCategory.FINANCIAL_SITUATION, "Financial Situation"), 
            (QuestionCategory.DEBTS, "Debts and Obligations"),
            (QuestionCategory.ASSETS, "Assets and Property"),
            (QuestionCategory.EMPLOYMENT, "Employment History"),
            (QuestionCategory.LEGAL, "Legal Information")
        ]
        
        for category, name in categories:
            print(f"\n--- {name} ---")
            await self._process_text_category(category)
            
            completion = self.bankruptcy_case.get_completion_status()
            avg_completion = sum(completion.values()) / len(completion) if completion else 0
            print(f"Overall completion: {int(avg_completion)}%")
    
    async def _process_text_category(self, category: QuestionCategory):
        """Process a category of questions via text"""
        questions = get_questions_for_category(category)
        
        for i, question in enumerate(questions[:5]):  # Limit questions per category
            if question in self.asked_questions:
                continue
                
            print(f"\nQ{i+1}: {question}")
            answer = input("Your answer: ").strip()
            
            if answer.lower() in ['break', 'pause']:
                print("Taking a break... type anything to continue")
                input()
                continue
            elif answer.lower() == 'help':
                print("Just answer as naturally as possible. Be honest and complete.")
                answer = input("Your answer: ").strip()
            
            if answer:
                # Process answer with AI
                await self._process_answer_with_ai(question, answer)
                self.asked_questions.add(question)
                
                # Store in conversation history
                self.conversation_history.append({
                    'question': question,
                    'answer': answer,
                    'category': category.value,
                    'timestamp': datetime.now().isoformat()
                })

    async def shutdown(self):
        """Cleanup resources"""
        logger.info("Production SOTA Bankruptcy Agent shutting down")
        await self.document_processor.shutdown()
        await asyncio.sleep(0)

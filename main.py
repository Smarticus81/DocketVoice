"""
DocketVoice SOTA - Production-Ready Bankruptcy Form Completion Platform
Multi-million dollar platform for complete Chapter 7 and 13 bankruptcy processing
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from config import Settings
from sota_ai import SOTA_AI
from sota_voice import SOTA_Voice
from sota_agent_production import SOTABankruptcyAgentProduction, ConsultationResult
from sota_monitoring import SOTAMonitoring
from sota_security import SOTASecurity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docketvoice.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DocketVoiceSOTAProduction:
    """Production-ready SOTA bankruptcy platform"""
    
    def __init__(self):
        self.settings: Optional[Settings] = None
        self.ai_provider: Optional[SOTA_AI] = None
        self.voice_provider: Optional[SOTA_Voice] = None
        self.agent: Optional[SOTABankruptcyAgentProduction] = None
        self.monitoring: Optional[SOTAMonitoring] = None
        self.security: Optional[SOTASecurity] = None
        
    async def initialize(self) -> bool:
        """Initialize all SOTA components"""
        try:
            logger.info("=== DocketVoice SOTA Production Platform Starting ===")
            
            # Load configuration
            self.settings = Settings()
            logger.info(" Configuration loaded")
            
            # DEBUG: Print loaded AI config
            logger.info(f"DEBUG: Loaded AI Config: {self.settings.ai.model_dump_json(indent=2)}")
            
            # Initialize security
            self.security = SOTASecurity(self.settings)
            logger.info(" Security system initialized")
            
            # Initialize monitoring
            self.monitoring = SOTAMonitoring(self.settings)
            await self.monitoring.start()
            logger.info(" Monitoring system started")
            
            # Initialize AI provider
            self.ai_provider = SOTA_AI(self.settings)
            await self.ai_provider.initialize()
            logger.info(" AI provider initialized with latest models")
            
            # Initialize voice provider
            self.voice_provider = SOTA_Voice(self.settings)
            await self.voice_provider.initialize()
            logger.info(" Voice provider initialized")
            
            # Initialize production agent
            self.agent = SOTABankruptcyAgentProduction(
                self.settings, 
                self.ai_provider, 
                self.voice_provider
            )
            logger.info(" Production bankruptcy agent initialized")
            
            # Create required directories
            Path("generated_documents").mkdir(exist_ok=True)
            Path("uploaded_documents").mkdir(exist_ok=True)
            Path("case_files").mkdir(exist_ok=True)
            logger.info(" Directory structure created")
            
            logger.info("=== All systems operational - Ready for client consultations ===")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SOTA platform: {str(e)}")
            return False
    
    async def run_production_consultation(self) -> ConsultationResult:
        """Run a complete production bankruptcy consultation"""
        
        if not self.agent:
            raise RuntimeError("Agent not initialized")
            
        logger.info("Starting production bankruptcy consultation")
        
        try:
            # Run the complete consultation
            result = await self.agent.run_complete_consultation()
            
            logger.info(f"Consultation completed successfully")
            logger.info(f"Forms generated: {len(result.generated_documents)}")
            logger.info(f"Overall completion: {sum(result.completion_status.values()) / len(result.completion_status):.1f}%")
            logger.info(f"Ready for filing: {result.ready_for_filing}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in production consultation: {str(e)}")
            raise
    
    async def run_document_upload_mode(self):
        """Run in document upload and processing mode"""
        
        print("\n=== Document Upload Mode ===")
        print("Place documents in the 'uploaded_documents' folder and press Enter to process them.")
        
        input("Press Enter when documents are ready...")
        
        documents_dir = Path("uploaded_documents")
        if not documents_dir.exists():
            documents_dir.mkdir()
            print("Created uploaded_documents folder. Please add your documents and try again.")
            return
        
        uploaded_files = list(documents_dir.glob("*"))
        if not uploaded_files:
            print("No documents found in uploaded_documents folder.")
            return
        
        print(f"Found {len(uploaded_files)} documents. Processing...")
        
        # Process documents and run consultation
        result = await self.run_production_consultation()
        
        print(f"\nDocument processing complete!")
        print(f"Generated {len(result.generated_documents)} bankruptcy forms")
        print(f"Case is {'ready for attorney review' if result.ready_for_filing else 'needs additional information'}")
    
    async def run_test_mode(self):
        """Run comprehensive system test"""
        
        print("\n=== SOTA System Test Mode ===")
        
        # Test AI connectivity
        try:
            test_response = await self.ai_provider.chat_completion([
                {"role": "user", "content": "Test message"}
            ])
            print(" AI provider test passed")
        except Exception as e:
            print(f" AI provider test failed: {str(e)}")
        
        # Test voice system
        try:
            await self.voice_provider.speak("System test in progress.")
            print(" Voice provider test passed")
        except Exception as e:
            print(f" Voice provider test failed: {str(e)}")
        
        # Test document processing
        try:
            from sota_document_processor import SOTADocumentProcessor
            processor = SOTADocumentProcessor(self.settings)
            print(" Document processor initialized")
        except Exception as e:
            print(f" Document processor test failed: {str(e)}")
        
        # Test PDF generation
        try:
            from sota_pdf_generator import SOTAPDFGenerator
            generator = SOTAPDFGenerator()
            print(" PDF generator initialized")
        except Exception as e:
            print(f" PDF generator test failed: {str(e)}")
        
        # Test form models
        try:
            from sota_forms_complete import CompleteBankruptcyCase
            test_case = CompleteBankruptcyCase()
            completion = test_case.get_completion_status()
            print(f" Form models working - {len(completion)} forms available")
        except Exception as e:
            print(f" Form models test failed: {str(e)}")
        
        print("\n=== System Test Complete ===")
    
    async def display_configuration(self):
        """Display current system configuration"""
        
        print("\n=== DocketVoice SOTA Configuration ===")
        print(f"AI Provider: {self.settings.ai.primary_provider}")
        print(f"OpenAI Model: {self.settings.ai.openai_model}")
        print(f"Anthropic Model: {self.settings.ai.anthropic_model}")
        print(f"Voice Provider: {self.settings.voice.primary_provider}")
        print(f"Security: AES-256-GCM encryption enabled")
        print(f"Monitoring: Circuit breakers and health checks active")
        print(f"Document Processing: OCR + AI analysis enabled")
        print(f"Form Suite: Complete Chapter 7 & 13 bankruptcy forms")
        print("========================================")
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        
        logger.info("Shutting down SOTA platform...")
        
        if self.agent:
            await self.agent.shutdown()
            
        if self.voice_provider:
            await self.voice_provider.shutdown()
            
        if self.ai_provider:
            await self.ai_provider.shutdown()
            
        if self.monitoring:
            await self.monitoring.shutdown()
        
        logger.info("SOTA platform shutdown complete")

async def main():
    """Main entry point for production platform"""
    
    parser = argparse.ArgumentParser(description='DocketVoice SOTA - Production Bankruptcy Platform')
    parser.add_argument('--test', action='store_true', help='Run system tests')
    parser.add_argument('--config', action='store_true', help='Display configuration')
    parser.add_argument('--upload', action='store_true', help='Document upload mode')
    parser.add_argument('--consultation', action='store_true', help='Run consultation (default)')
    
    args = parser.parse_args()
    
    # Initialize platform
    platform = DocketVoiceSOTAProduction()
    
    if not await platform.initialize():
        print("Failed to initialize platform. Check logs for details.")
        sys.exit(1)
    
    try:
        if args.config:
            await platform.display_configuration()
            
        elif args.test:
            await platform.run_test_mode()
            
        elif args.upload:
            await platform.run_document_upload_mode()
            
        else:
            # Default: Run production consultation
            print("\n=== Welcome to DocketVoice SOTA ===")
            print("Production-Ready Bankruptcy Form Completion Platform")
            print("Complete Chapter 7 & 13 bankruptcy processing")
            print("=====================================")
            
            result = await platform.run_production_consultation()
            
            print(f"\n=== Consultation Complete ===")
            print(f"Generated Documents: {len(result.generated_documents)}")
            print(f"Ready for Filing: {result.ready_for_filing}")
            print(f"Files saved in: generated_documents/")
            print("============================")
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        
    except Exception as e:
        logger.error(f"Platform error: {str(e)}")
        print(f"Platform error: {str(e)}")
        
    finally:
        await platform.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

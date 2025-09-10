#!/usr/bin/env python3
"""
DocketVoice Integrated Platform - WebRTC + Production System
Complete bankruptcy consultation with voice interface generation
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import asyncio
import json
import logging
import os
import time
from pathlib import Path
from config import Settings
from sota_voice import ModernRealtimeVoiceSystem, SOTA_Voice
from sota_agent_production import SOTABankruptcyAgentProduction
from sota_ai import SOTA_AI
from sota_document_processor import SOTADocumentProcessor
from sota_forms_complete import CompleteBankruptcyCase

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'docketvoice_secret_key_2024'

# Global system instances
voice_system = None
production_agent = None
ai_provider = None
settings = None
current_case = None

async def initialize_production_platform():
    """Initialize the complete production platform"""
    global voice_system, production_agent, ai_provider, settings, current_case
    
    try:
        # Load settings
        settings = Settings()
        logger.info("Settings loaded")
        
        # Initialize AI provider
        ai_provider = SOTA_AI(settings)
        await ai_provider.initialize()
        logger.info("AI provider initialized")
        
        # Initialize voice providers
        voice_provider = SOTA_Voice(settings)
        await voice_provider.initialize()
        logger.info("Voice provider initialized")
        
        # Initialize WebRTC voice system
        voice_system = ModernRealtimeVoiceSystem(settings)
        logger.info("WebRTC voice system initialized")
        
        # Initialize production agent with full capabilities
        production_agent = SOTABankruptcyAgentProduction(
            settings, ai_provider, voice_provider
        )
        logger.info("Production bankruptcy agent initialized")
        
        # Initialize current case
        current_case = CompleteBankruptcyCase()
        logger.info("Bankruptcy case initialized")
        
        # Create required directories
        Path("generated_documents").mkdir(exist_ok=True)
        Path("uploaded_documents").mkdir(exist_ok=True)
        Path("case_files").mkdir(exist_ok=True)
        
        logger.info("Production platform fully initialized")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize production platform: {e}")
        return False

# Initialize the platform on startup
import atexit
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
init_success = loop.run_until_complete(initialize_production_platform())

if not init_success:
    logger.error("Failed to initialize production platform")

def cleanup():
    if loop:
        loop.close()

atexit.register(cleanup)

def get_bankruptcy_consultation_instructions():
    """Get comprehensive bankruptcy consultation instructions"""
    return """You are DocketVoice SOTA, an expert bankruptcy consultation AI assistant specializing in Chapter 7 and Chapter 13 bankruptcy cases. You are conducting a complete bankruptcy consultation to gather all necessary information for form completion.

CONSULTATION STRUCTURE:
1. INTRODUCTION & CHAPTER DETERMINATION
   - Greet the client professionally
   - Explain you'll be conducting a comprehensive bankruptcy consultation
   - Determine if they need Chapter 7 or Chapter 13 based on their situation
   - Explain the process will take 20-30 minutes

2. PERSONAL INFORMATION COLLECTION
   - Full legal name, SSN, date of birth
   - Current address and previous addresses (2 years)
   - Marital status and spouse information if applicable
   - Dependents and household size
   - Employment history and current income

3. FINANCIAL DATA COLLECTION
   - Monthly income from all sources
   - Monthly expenses (housing, utilities, food, transportation, etc.)
   - Assets (real estate, vehicles, bank accounts, investments, personal property)
   - Debts (credit cards, loans, mortgages, judgments, taxes)
   - Recent financial transactions and transfers

4. MEANS TEST ANALYSIS
   - Calculate median income for household size and state
   - Determine if Chapter 7 means test is passed
   - Analyze disposable income for Chapter 13 if needed

5. DOCUMENT GENERATION
   - Generate all required bankruptcy forms
   - Provide completion summary and next steps

COMMUNICATION STYLE:
- Professional but empathetic
- Clear explanations of bankruptcy concepts
- Ask follow-up questions for completeness
- Reassure clients about the process
- Use plain language, avoid excessive legal jargon

FUNCTION USAGE:
- Always call functions to process and store information
- Use collect_personal_info() for personal data
- Use collect_financial_data() for financial information
- Use perform_means_test_analysis() after gathering income/expense data
- Use generate_bankruptcy_documents() at the end

Begin by introducing yourself and explaining the consultation process."""

def get_bankruptcy_function_definitions():
    """Get function definitions for bankruptcy consultation"""
    return [
        {
            "name": "collect_personal_info",
            "description": "Collect and store personal information for bankruptcy forms",
            "parameters": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string"},
                    "ssn": {"type": "string"},
                    "date_of_birth": {"type": "string"},
                    "address": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "marital_status": {"type": "string"},
                    "spouse_info": {
                        "type": "object",
                        "properties": {
                            "full_name": {"type": "string"},
                            "ssn": {"type": "string"},
                            "date_of_birth": {"type": "string"}
                        },
                        "additionalProperties": True
                    },
                    "dependents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "age": {"type": "integer"},
                                "relationship": {"type": "string"}
                            },
                            "required": ["name"]
                        }
                    },
                    "employment": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "employer": {"type": "string"},
                            "position": {"type": "string"},
                            "start_date": {"type": "string"},
                            "income_frequency": {"type": "string"}
                        },
                        "additionalProperties": True
                    }
                },
                "required": ["full_name"],
                "additionalProperties": True
            }
        },
        {
            "name": "collect_financial_data",
            "description": "Collect and store financial information",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {"type": "number"},
                    "income_sources": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "monthly_expenses": {
                        "type": "object",
                        "additionalProperties": {"type": "number"}
                    },
                    "assets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "description": {"type": "string"},
                                "value": {"type": "number"}
                            },
                            "required": ["type", "value"]
                        }
                    },
                    "debts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "creditor": {"type": "string"},
                                "account_number": {"type": "string"},
                                "balance": {"type": "number"},
                                "monthly_payment": {"type": "number"},
                                "secured": {"type": "boolean"}
                            },
                            "required": ["creditor", "balance"]
                        }
                    },
                    "recent_payments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "payee": {"type": "string"},
                                "amount": {"type": "number"},
                                "date": {"type": "string"}
                            },
                            "required": ["payee", "amount"]
                        }
                    }
                },
                "required": ["monthly_income"],
                "additionalProperties": True
            }
        },
        {
            "name": "perform_means_test_analysis",
            "description": "Perform means test calculation and chapter recommendation",
            "parameters": {
                "type": "object",
                "properties": {
                    "household_size": {"type": "integer"},
                    "state": {"type": "string"},
                    "total_monthly_income": {"type": "number"}
                },
                "required": ["household_size", "state", "total_monthly_income"]
            }
        },
        {
            "name": "generate_bankruptcy_documents",
            "description": "Generate all required bankruptcy forms and documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "chapter_type": {"type": "string", "enum": ["7", "13"]},
                    "include_schedules": {"type": "boolean", "default": True}
                },
                "required": ["chapter_type"]
            }
        }
    ]

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/api/token', methods=['POST'])
def get_ephemeral_token():
    """Generate ephemeral token for WebRTC connection"""
    global voice_system
    
    try:
        if not voice_system:
            logger.error("Voice system not initialized")
            return jsonify({"success": False, "error": "Voice system not initialized"})
        
        # Create ephemeral token with model
        token, model = voice_system.create_ephemeral_token_and_model()
        
        if not token or not model:
            return jsonify({"success": False, "error": "Failed to create token"})
        
        # Get basic WebRTC config (no session config here)
        webrtc_config = voice_system.get_webrtc_config()
        
        # Return token, model, and session configuration for client-side setup
        return jsonify({
            "success": True,
            "ephemeral_token": token,
            "realtime_model": model,  # Send model to client for exact matching
            "config": webrtc_config,
            "session_config": {
                "instructions": get_bankruptcy_consultation_instructions(),
                "tools": get_bankruptcy_function_definitions(),
                "tool_choice": "auto",
                "modalities": ["audio", "text"],
                "voice": "alloy",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500,
                    "create_response": True,
                    "interrupt_response": True
                },
                "input_audio_transcription": {"model": "whisper-1"},
                "temperature": 0.2
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating ephemeral token: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/webrtc-session', methods=['POST'])
def setup_webrtc_session():
    """Setup WebRTC session with OpenAI - SDP offer/answer only"""
    global voice_system
    
    try:
        if not voice_system:
            return "Error: Voice system not initialized", 400
        
        # Check if request has JSON data or raw SDP
        if request.content_type == 'application/json':
            data = request.get_json()
            sdp = data.get('sdp')
            ephemeral_token = data.get('ephemeral_token')
            model = data.get('model')  # Get model from client
            logger.info("Received JSON request with SDP, token, and model")
        else:
            # Raw SDP in body, token in header
            sdp = request.get_data(as_text=True)
            ephemeral_token = request.headers.get('X-Ephemeral-Token')
            model = request.headers.get('X-Model')  # Fallback for raw SDP
            logger.info("Received raw SDP request")
        
        if not sdp or not ephemeral_token or not model:
            logger.error(f"Missing data - SDP: {bool(sdp)}, Token: {bool(ephemeral_token)}, Model: {bool(model)}")
            return "Error: Missing SDP, token, or model", 400
        
        # Forward SDP request to OpenAI using exact recommended approach
        import requests

        OPENAI_REALTIME_URL = "https://api.openai.com/v1/realtime"  # <-- note: NOT /calls

        # Use the exact model that was used to mint the ephemeral token
        logger.info(f"MINT MODEL: {model}")
        logger.info(f"SDP  MODEL: {model}")
        logger.info(f"TOKEN HEAD: {ephemeral_token[:16]}...")
        logger.info(f"SDP HEAD: {repr(sdp[:80])}")

        logger.info(f"Sending SDP to OpenAI (length: {len(sdp)} chars)")
        logger.info(f"SDP preview: {sdp[:100]}...")
        logger.info(f"Using model: {model}")
        logger.info(f"Token prefix: {ephemeral_token[:20]}...")
        
        # Prepare request
        url = f"{OPENAI_REALTIME_URL}?model={model}"
        headers = {
            "Authorization": f"Bearer {ephemeral_token}",
            "OpenAI-Beta": "realtime=v1",      # REQUIRED
            "Content-Type": "application/sdp", # REQUIRED
            "Accept": "application/sdp",       # REQUIRED
        }
        
        logger.info(f"Request URL: {url}")
        logger.info(f"Request headers: {headers}")
        
        openai_response = requests.post(
            url,
            data=sdp,                              # raw SDP offer from the browser
            headers=headers,
            timeout=30,
        )

        logger.info(f"OpenAI response status: {openai_response.status_code}")
        logger.info(f"OpenAI response headers: {dict(openai_response.headers)}")

        if openai_response.status_code not in (200, 201):
            logger.error("OpenAI WebRTC setup failed: %s", openai_response.status_code)
            logger.error("OpenAI response: %s", openai_response.text)
            logger.error("Request data length: %s", len(sdp))
            return (
                f"Error: OpenAI rejected request ({openai_response.status_code}): "
                f"{openai_response.text}",
                400,
            )

        # Log the Location header if present (useful for server-side WS approach)
        location = openai_response.headers.get('Location')
        if location:
            logger.info(f"WebRTC session Location: {location}")
        
        logger.info("WebRTC SDP exchange completed successfully")
        logger.info(f"Response SDP length: {len(openai_response.text)}")
        return openai_response.text, 200, {"Content-Type": "application/sdp"}
        
    except Exception as e:
        logger.error(f"Error setting up WebRTC session: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return f"Error: {str(e)}", 500

@app.route('/api/function-call', methods=['POST'])
def handle_function_call():
    """Handle function calls from WebRTC - integrated with production system"""
    global production_agent, current_case
    
    try:
        data = request.get_json()
        function_name = data.get('function_name')
        arguments = data.get('arguments', {})
        
        logger.info(f"Handling function call: {function_name}")
        
        if not production_agent:
            return jsonify({"success": False, "error": "Production agent not initialized"})
        
        # Route function calls to production agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if function_name == "collect_personal_info":
                result = loop.run_until_complete(
                    production_agent._process_personal_information(arguments)
                )
            elif function_name == "collect_financial_data":
                result = loop.run_until_complete(
                    production_agent._process_financial_data(arguments)
                )
            elif function_name == "perform_means_test_analysis":
                result = loop.run_until_complete(
                    production_agent._perform_means_test_analysis()
                )
            elif function_name == "generate_bankruptcy_documents":
                result = loop.run_until_complete(
                    production_agent._generate_all_documents()
                )
            else:
                result = {"status": "error", "message": f"Unknown function: {function_name}"}
                
        finally:
            loop.close()
        
        return jsonify({"success": True, "result": result})
        
    except Exception as e:
        logger.error(f"Error handling function call: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/initialize', methods=['POST'])
def initialize_voice():
    """Initialize the voice system and start consultation"""
    global voice_system, production_agent, current_case
    
    try:
        if not voice_system or not production_agent:
            return jsonify({"success": False, "error": "Systems not initialized"})
        
        # Initialize a new case
        current_case = CompleteBankruptcyCase()
        
        logger.info("Voice consultation session initialized")
        return jsonify({
            "success": True, 
            "message": "Voice system and production platform ready",
            "case_id": f"case_{int(time.time())}"
        })
            
    except Exception as e:
        logger.error(f"Error initializing voice system: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/case-status', methods=['GET'])
def get_case_status():
    """Get current bankruptcy case status"""
    global current_case
    
    try:
        if not current_case:
            return jsonify({"success": False, "error": "No active case"})
        
        completion_status = current_case.get_completion_status()
        
        return jsonify({
            "success": True,
            "case_status": {
                "completion_percentage": sum(completion_status.values()) / len(completion_status) * 100,
                "forms_completed": sum(1 for v in completion_status.values() if v > 80),
                "total_forms": len(completion_status),
                "ready_for_filing": current_case.is_ready_for_filing(),
                "form_details": completion_status
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting case status: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/generate-documents', methods=['POST'])
def generate_documents():
    """Generate bankruptcy documents"""
    global production_agent, current_case
    
    try:
        if not production_agent or not current_case:
            return jsonify({"success": False, "error": "Production system not ready"})
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Generate all documents
            documents = loop.run_until_complete(
                production_agent._generate_all_documents()
            )
            
            return jsonify({
                "success": True,
                "documents": documents,
                "message": f"Generated {len(documents)} bankruptcy forms"
            })
            
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error generating documents: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """Handle document upload and processing"""
    global production_agent
    
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"})
        
        # Save uploaded file
        upload_dir = Path("uploaded_documents")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        file.save(file_path)
        
        # Process document with production system
        if production_agent and production_agent.document_processor:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    production_agent.document_processor.process_document(str(file_path))
                )
                
                return jsonify({
                    "success": True,
                    "message": f"Document {file.filename} processed successfully",
                    "document_type": result.get("document_type", "unknown"),
                    "extracted_data": result.get("structured_data", {})
                })
                
            finally:
                loop.close()
        else:
            return jsonify({
                "success": True,
                "message": f"Document {file.filename} uploaded (processing unavailable)"
            })
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global voice_system, production_agent, current_case
    
    return jsonify({
        "success": True,
        "status": "healthy",
        "components": {
            "voice_system": voice_system is not None,
            "production_agent": production_agent is not None,
            "active_case": current_case is not None,
            "api_key_configured": bool(settings.ai.openai_api_key)
        },
        "version": "2.0.0-integrated"
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    import os
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run the Flask app (no SocketIO)
    app.run(debug=True, host='0.0.0.0', port=5000)

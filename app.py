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
        
        # Create ephemeral token
        token = voice_system.create_ephemeral_token()
        
        if not token:
            return jsonify({"success": False, "error": "Failed to create token"})
        
        return jsonify({
            "success": True,
            "ephemeral_token": token,
            "config": voice_system.get_webrtc_config()
        })
        
    except Exception as e:
        logger.error(f"Error creating ephemeral token: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/webrtc-session', methods=['POST'])
def setup_webrtc_session():
    """Setup WebRTC session with OpenAI"""
    global voice_system
    
    try:
        if not voice_system:
            return "Error: Voice system not initialized", 400
        
        data = request.get_json()
        sdp = data.get('sdp')
        ephemeral_token = data.get('ephemeral_token')
        
        if not sdp or not ephemeral_token:
            return "Error: Missing SDP or token", 400
        
        # Forward request to OpenAI using correct WebRTC endpoint
        import requests
        
        logger.info(f"Forwarding WebRTC request to OpenAI with ephemeral token: {ephemeral_token[:10]}...")
        logger.info(f"SDP offer length: {len(sdp)} characters")
        
        base_url = "https://api.openai.com/v1/realtime/calls"
        model = "gpt-4o-realtime-preview-2024-10-01"
        logger.info(f"Making request to: {base_url}?model={model}")
        
        openai_response = requests.post(
            f'{base_url}?model={model}',
            data=sdp,
            headers={
                'Authorization': f'Bearer {ephemeral_token}',
                'Content-Type': 'application/sdp'
            }
        )
        
        logger.info(f"OpenAI response status: {openai_response.status_code}")
        logger.info(f"OpenAI response headers: {dict(openai_response.headers)}")
        
        if openai_response.status_code not in [200, 201]:
            logger.error(f"OpenAI WebRTC setup failed: {openai_response.status_code}")
            logger.error(f"OpenAI response: {openai_response.text}")
            return f"Error: OpenAI rejected request ({openai_response.status_code})", 400
        
        logger.info("WebRTC session established successfully")
        logger.info(f"Answer SDP length: {len(openai_response.text)} characters")
        # Return the answer SDP
        return openai_response.text, 200, {'Content-Type': 'application/sdp'}
        
    except Exception as e:
        logger.error(f"Error setting up WebRTC session: {e}")
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

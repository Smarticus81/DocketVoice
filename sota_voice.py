#!/usr/bin/env python3
"""
DocketVoice - Modern OpenAI Realtime API Implementation (2025)
Using official OpenAI Python SDK with gpt-realtime model
No manual WebSocket implementation required
"""

import asyncio
import json
import logging
import base64
import os
import requests
from typing import Optional, Dict, Any, List, Callable, AsyncGenerator
from openai import AsyncOpenAI
from dataclasses import dataclass
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealtimeConfig:
    """Configuration for OpenAI Realtime API using official SDK"""
    model: str = "gpt-realtime"  # Latest GA model
    voice: str = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer, cedar, marin
    modalities: List[str] = None
    input_audio_format: str = "pcm16"
    output_audio_format: str = "pcm16"
    
    # VAD Configuration
    vad_type: str = "server_vad"  # Options: none, server_vad, semantic_vad
    vad_threshold: float = 0.5
    vad_prefix_padding_ms: int = 300
    vad_silence_duration_ms: int = 200
    
    # Model Configuration
    temperature: float = 0.8
    max_response_output_tokens: int = 4096
    
    def __post_init__(self):
        if self.modalities is None:
            self.modalities = ["text", "audio"]

class ModernRealtimeVoiceSystem:
    """
    Modern OpenAI Realtime API implementation using official Python SDK
    No manual WebSocket management required
    """
    
    def __init__(self, settings, config: Optional[RealtimeConfig] = None):
        self.settings = settings
        self.config = config or RealtimeConfig()
        
        # OpenAI client
        self.client = None
        self.connection = None
        
        # Connection state
        self.is_connected = False
        self.session_id = None
        
        # Event handlers
        self.audio_output_handlers: List[Callable] = []
        self.text_output_handlers: List[Callable] = []
        self.function_call_handlers: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, Callable] = {}
        
        # Response tracking
        self.current_response_id = None
        self.response_start_time = 0
        
        # Function tools for bankruptcy consultation
        self.tools = self._define_bankruptcy_tools()
    
    def _define_bankruptcy_tools(self) -> List[Dict[str, Any]]:
        """Define comprehensive function tools for bankruptcy consultation"""
        return [
            {
                "type": "function",
                "name": "collect_client_information",
                "description": "Collect comprehensive client information for bankruptcy consultation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "personal_info": {
                            "type": "object",
                            "properties": {
                                "full_name": {"type": "string"},
                                "ssn": {"type": "string", "pattern": r"^\d{3}-\d{2}-\d{4}$"},
                                "date_of_birth": {"type": "string", "format": "date"},
                                "marital_status": {
                                    "type": "string",
                                    "enum": ["single", "married", "divorced", "widowed", "separated"]
                                },
                                "dependents": {"type": "integer", "minimum": 0}
                            },
                            "required": ["full_name"]
                        },
                        "contact_info": {
                            "type": "object",
                            "properties": {
                                "address": {
                                    "type": "object",
                                    "properties": {
                                        "street": {"type": "string"},
                                        "city": {"type": "string"},
                                        "state": {"type": "string", "minLength": 2, "maxLength": 2},
                                        "zip_code": {"type": "string"}
                                    }
                                },
                                "phone": {"type": "string"},
                                "email": {"type": "string", "format": "email"}
                            }
                        },
                        "employment": {
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["employed", "unemployed", "self_employed", "retired", "disabled"]
                                },
                                "employer": {"type": "string"},
                                "job_title": {"type": "string"},
                                "monthly_income": {"type": "number", "minimum": 0},
                                "employment_length": {"type": "string"}
                            }
                        }
                    },
                    "required": ["personal_info"]
                }
            },
            {
                "type": "function",
                "name": "analyze_financial_profile",
                "description": "Analyze complete financial profile including income, expenses, debts, and assets",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "monthly_income": {
                            "type": "object",
                            "properties": {
                                "employment": {"type": "number", "minimum": 0},
                                "self_employment": {"type": "number", "minimum": 0},
                                "social_security": {"type": "number", "minimum": 0},
                                "pension": {"type": "number", "minimum": 0},
                                "other": {"type": "number", "minimum": 0}
                            }
                        },
                        "monthly_expenses": {
                            "type": "object",
                            "properties": {
                                "housing": {"type": "number", "minimum": 0},
                                "utilities": {"type": "number", "minimum": 0},
                                "food": {"type": "number", "minimum": 0},
                                "transportation": {"type": "number", "minimum": 0},
                                "insurance": {"type": "number", "minimum": 0},
                                "healthcare": {"type": "number", "minimum": 0},
                                "childcare": {"type": "number", "minimum": 0},
                                "debt_payments": {"type": "number", "minimum": 0},
                                "other": {"type": "number", "minimum": 0}
                            }
                        },
                        "debts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "creditor": {"type": "string"},
                                    "debt_type": {
                                        "type": "string",
                                        "enum": ["credit_card", "medical", "personal_loan", "mortgage", "auto_loan", "student_loan", "tax_debt", "other"]
                                    },
                                    "current_balance": {"type": "number", "minimum": 0},
                                    "monthly_payment": {"type": "number", "minimum": 0},
                                    "interest_rate": {"type": "number", "minimum": 0},
                                    "is_secured": {"type": "boolean"},
                                    "collateral": {"type": "string"}
                                },
                                "required": ["creditor", "debt_type", "current_balance"]
                            }
                        },
                        "assets": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "asset_type": {
                                        "type": "string",
                                        "enum": ["real_estate", "vehicle", "bank_account", "investment", "retirement", "personal_property", "business", "other"]
                                    },
                                    "description": {"type": "string"},
                                    "current_value": {"type": "number", "minimum": 0},
                                    "debt_against": {"type": "number", "minimum": 0},
                                    "equity": {"type": "number"}
                                }
                            }
                        }
                    },
                    "required": ["monthly_income", "monthly_expenses", "debts"]
                }
            },
            {
                "type": "function",
                "name": "perform_means_test_analysis",
                "description": "Perform comprehensive Chapter 7 means test and Chapter 13 feasibility analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_data": {
                            "type": "object",
                            "properties": {
                                "state": {"type": "string", "minLength": 2, "maxLength": 2},
                                "household_size": {"type": "integer", "minimum": 1, "maximum": 15},
                                "monthly_income": {"type": "number", "minimum": 0},
                                "monthly_expenses": {"type": "number", "minimum": 0},
                                "total_debt": {"type": "number", "minimum": 0},
                                "secured_debt": {"type": "number", "minimum": 0},
                                "unsecured_debt": {"type": "number", "minimum": 0}
                            },
                            "required": ["state", "household_size", "monthly_income"]
                        },
                        "special_circumstances": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["recent_job_loss", "medical_emergency", "divorce", "disability", "military_service", "elderly_care", "other"]
                            }
                        },
                        "previous_bankruptcies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "chapter": {"type": "string", "enum": ["7", "11", "12", "13"]},
                                    "filing_date": {"type": "string", "format": "date"},
                                    "discharge_date": {"type": "string", "format": "date"}
                                }
                            }
                        }
                    },
                    "required": ["client_data"]
                }
            },
            {
                "type": "function",
                "name": "generate_consultation_report",
                "description": "Generate comprehensive bankruptcy consultation report with recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consultation_summary": {
                            "type": "object",
                            "properties": {
                                "primary_financial_issues": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "debt_categories": {
                                    "type": "object",
                                    "properties": {
                                        "secured": {"type": "number"},
                                        "unsecured": {"type": "number"},
                                        "priority": {"type": "number"}
                                    }
                                },
                                "asset_summary": {
                                    "type": "object",
                                    "properties": {
                                        "total_value": {"type": "number"},
                                        "exempt_value": {"type": "number"},
                                        "non_exempt_value": {"type": "number"}
                                    }
                                }
                            }
                        },
                        "recommendations": {
                            "type": "object",
                            "properties": {
                                "primary_recommendation": {
                                    "type": "string",
                                    "enum": ["chapter_7", "chapter_13", "debt_management", "negotiate_settlements", "no_action_needed"]
                                },
                                "alternative_options": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "urgency": {
                                    "type": "string",
                                    "enum": ["immediate", "within_30_days", "within_90_days", "within_6_months", "no_urgency"]
                                }
                            }
                        },
                        "next_steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "string"},
                                    "timeline": {"type": "string"},
                                    "importance": {"type": "string", "enum": ["critical", "important", "recommended"]},
                                    "description": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["consultation_summary", "recommendations", "next_steps"]
                }
            }
        ]
    
    async def initialize(self) -> bool:
        """Initialize the OpenAI client and validate API access"""
        try:
            api_key = self.settings.get_ai_api_key()
            if not api_key:
                logger.error("OpenAI API key not found")
                return False
            
            # Initialize AsyncOpenAI client
            self.client = AsyncOpenAI(api_key=api_key)
            
            # Test API access with a simple call
            try:
                models = await self.client.models.list()
                logger.info("OpenAI API access verified")
                return True
            except Exception as e:
                logger.error(f"API verification failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def create_ephemeral_token(self) -> Optional[str]:
        """Create ephemeral client secret (ephemeral token) for WebRTC Realtime per OpenAI docs.

        SECURITY: We DO NOT fall back to returning the permanent API key. If ephemeral issuance
        fails we return None so the client can display a safe error.
        """
        try:
            api_key = getattr(self.settings, 'get_ai_api_key', lambda: os.getenv('OPENAI_API_KEY'))()
            if not api_key:
                logger.error("Cannot mint ephemeral token: base OpenAI API key missing")
                return None

            import requests, json

            url = "https://api.openai.com/v1/realtime/client_secrets"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Conform to current public doc structure: session.audio.output.voice
            # Minimal compliant payload per current public docs to avoid unknown parameter errors
            payload = {
                "session": {
                    "type": "realtime",
                    "model": "gpt-4o-realtime-preview-2024-10-01",
                    "audio": {
                        "output": {"voice": "alloy"}
                    }
                }
            }

            logger.info("Requesting ephemeral client secret (payload keys: %s)", list(payload['session'].keys()))
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)

            if response.status_code != 200:
                logger.error("Ephemeral token request failed %s: %s", response.status_code, response.text)
                return None

            data = response.json()
            token = data.get("value")
            if not token:
                logger.error("Ephemeral token response missing value: %s", data)
                return None

            expires = data.get("expires_at")
            if expires:
                logger.info("Ephemeral token minted (expires_at=%s)", expires)
            else:
                logger.info("Ephemeral token minted (no expires_at provided)")
            return token
        except Exception as e:
            logger.error(f"Ephemeral token creation exception: {e}")
            return None
    
    def get_webrtc_config(self) -> Dict[str, Any]:
        """Get WebRTC configuration for browser client"""
        return {
            "iceServers": [
                {"urls": "stun:stun.l.google.com:19302"}
            ],
            "iceCandidatePoolSize": 10
        }
    
    async def handle_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle function calls from the AI (for web client compatibility)"""
        return await self._execute_default_function(function_name, arguments)
    
    async def connect_realtime(self) -> bool:
        """Connect to OpenAI Realtime API using official SDK"""
        try:
            if not self.client:
                logger.error("Client not initialized")
                return False
            
            # Build session configuration
            session_config = {
                "modalities": self.config.modalities,
                "instructions": self._get_system_instructions(),
                "voice": self.config.voice,
                "input_audio_format": self.config.input_audio_format,
                "output_audio_format": self.config.output_audio_format,
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "temperature": self.config.temperature,
                "max_response_output_tokens": self.config.max_response_output_tokens,
                "tools": self.tools,
                "tool_choice": "auto"
            }
            
            # Add turn detection if VAD is enabled
            if self.config.vad_type != "none":
                session_config["turn_detection"] = {
                    "type": self.config.vad_type,
                    "threshold": self.config.vad_threshold,
                    "prefix_padding_ms": self.config.vad_prefix_padding_ms,
                    "silence_duration_ms": self.config.vad_silence_duration_ms
                }
            
            # Connect using the official SDK
            self.connection = await self.client.realtime.connect(
                model=self.config.model
            )
            
            # Update session configuration
            await self.connection.session.update(session=session_config)
            
            self.is_connected = True
            logger.info(f"Connected to Realtime API with model: {self.config.model}")
            
            # Start event processing
            asyncio.create_task(self._process_events())
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def _get_system_instructions(self) -> str:
        """Get comprehensive system instructions for DocketVoice"""
        return """You are DocketVoice, an expert bankruptcy consultation assistant. Your mission is to provide professional, empathetic, and comprehensive bankruptcy guidance.

CORE RESPONSIBILITIES:
1. Conduct thorough bankruptcy consultations with warmth and professionalism
2. Systematically collect complete client information using provided function tools
3. Perform accurate means test analysis and eligibility assessments
4. Explain complex bankruptcy concepts in clear, accessible language
5. Generate detailed consultation reports with actionable recommendations

COMMUNICATION STYLE:
- Professional yet warm and approachable
- Non-judgmental and empathetic to financial distress
- Clear and patient in explanations
- Thorough but efficient in information gathering
- Encouraging while being realistic about options

TECHNICAL GUIDELINES:
- Always use function tools to collect and analyze data systematically
- Ask follow-up questions to ensure complete information
- Validate information for accuracy and completeness
- Provide specific timelines and next steps
- Reference relevant bankruptcy laws and procedures when appropriate

IMPORTANT NOTES:
- This consultation provides general information, not legal advice
- Recommend attorney consultation for specific legal guidance
- Maintain strict confidentiality of all client information
- Focus on Chapter 7 and Chapter 13 options primarily
- Consider debt management alternatives when appropriate

Begin each consultation by warmly greeting the client and explaining the consultation process."""
    
    async def send_text_message(self, text: str) -> None:
        """Send a text message to the conversation"""
        try:
            if self.connection:
                await self.connection.conversation.item.create(
                    item={
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": text}]
                    }
                )
                await self.connection.response.create()
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
    
    async def send_audio_chunk(self, audio_data_b64: str) -> None:
        """Send audio data to the input buffer"""
        try:
            if self.connection:
                await self.connection.input_audio_buffer.append(audio=audio_data_b64)
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
    
    async def commit_audio_input(self) -> None:
        """Commit audio input buffer (for manual VAD)"""
        try:
            if self.connection:
                await self.connection.input_audio_buffer.commit()
        except Exception as e:
            logger.error(f"Error committing audio: {e}")
    
    async def create_response(self, **kwargs) -> None:
        """Create a response with optional configuration"""
        try:
            if self.connection:
                self.response_start_time = time.time()
                await self.connection.response.create(**kwargs)
        except Exception as e:
            logger.error(f"Error creating response: {e}")
    
    async def cancel_response(self) -> None:
        """Cancel the current response"""
        try:
            if self.connection:
                await self.connection.response.cancel()
                logger.info("Response cancelled")
        except Exception as e:
            logger.error(f"Error cancelling response: {e}")
    
    async def _process_events(self) -> None:
        """Process events from the Realtime API connection"""
        try:
            async for event in self.connection:
                await self._handle_event(event)
        except Exception as e:
            logger.error(f"Event processing error: {e}")
            self.is_connected = False
    
    async def _handle_event(self, event) -> None:
        """Handle individual events from the Realtime API"""
        event_type = event.type
        
        # Custom event handlers
        if event_type in self.event_handlers:
            try:
                await self.event_handlers[event_type](event)
            except Exception as e:
                logger.error(f"Custom handler error for {event_type}: {e}")
        
        # Built-in event handling
        if event_type == "session.created":
            self.session_id = getattr(event, 'session_id', None)
            logger.info(f"Session created: {self.session_id}")
            
        elif event_type == "session.updated":
            logger.info("Session updated successfully")
            
        elif event_type == "conversation.item.input_audio_transcription.completed":
            transcript = getattr(event, 'transcript', '')
            logger.info(f"User said: {transcript}")
            
        elif event_type == "response.created":
            self.current_response_id = getattr(event, 'response_id', None)
            logger.debug(f"Response created: {self.current_response_id}")
            
        elif event_type == "response.audio.delta":
            # Handle streaming audio output
            audio_delta = getattr(event, 'delta', '')
            if audio_delta:
                await self._handle_audio_output(audio_delta)
                
        elif event_type == "response.text.delta":
            # Handle streaming text output
            text_delta = getattr(event, 'delta', '')
            if text_delta:
                await self._handle_text_output(text_delta)
                
        elif event_type == "response.function_call_arguments.done":
            await self._handle_function_call(event)
            
        elif event_type == "response.done":
            if self.response_start_time:
                latency = time.time() - self.response_start_time
                logger.info(f"Response completed in {latency:.3f}s")
            self.current_response_id = None
            
        elif event_type == "error":
            error_msg = getattr(event, 'message', 'Unknown error')
            logger.error(f"API Error: {error_msg}")
    
    async def _handle_audio_output(self, audio_b64: str) -> None:
        """Handle audio output from the model"""
        for handler in self.audio_output_handlers:
            try:
                await handler(audio_b64)
            except Exception as e:
                logger.error(f"Audio output handler error: {e}")
    
    async def _handle_text_output(self, text: str) -> None:
        """Handle text output from the model"""
        for handler in self.text_output_handlers:
            try:
                await handler(text)
            except Exception as e:
                logger.error(f"Text output handler error: {e}")
    
    async def _handle_function_call(self, event) -> None:
        """Handle function calls from the model"""
        try:
            call_id = getattr(event, 'call_id', None)
            name = getattr(event, 'name', '')
            arguments_str = getattr(event, 'arguments', '{}')
            arguments = json.loads(arguments_str)
            
            logger.info(f"Function call: {name}")
            
            # Execute function
            if name in self.function_call_handlers:
                result = await self.function_call_handlers[name](arguments)
            else:
                result = await self._execute_default_function(name, arguments)
            
            # Send result back to the conversation
            await self.connection.conversation.item.create(
                item={
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result)
                }
            )
            
        except Exception as e:
            logger.error(f"Function call error: {e}")
    
    async def _execute_default_function(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute default function implementations"""
        try:
            if name == "collect_client_information":
                return await self._collect_client_information(args)
            elif name == "analyze_financial_profile":
                return await self._analyze_financial_profile(args)
            elif name == "perform_means_test_analysis":
                return await self._perform_means_test_analysis(args)
            elif name == "generate_consultation_report":
                return await self._generate_consultation_report(args)
            else:
                return {"error": f"Unknown function: {name}"}
        except Exception as e:
            return {"error": f"Function execution failed: {str(e)}"}
    
    async def _collect_client_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process client information collection"""
        personal_info = data.get("personal_info", {})
        contact_info = data.get("contact_info", {})
        employment = data.get("employment", {})
        
        full_name = personal_info.get("full_name", "")
        
        # Validation
        issues = []
        if not full_name.strip():
            issues.append("Full name is required")
        
        ssn = personal_info.get("ssn", "")
        if ssn and not self._validate_ssn(ssn):
            issues.append("SSN must be in XXX-XX-XXXX format")
        
        if issues:
            return {
                "status": "validation_error",
                "issues": issues,
                "message": "Please correct the following information"
            }
        
        logger.info(f"Client information collected for: {full_name}")
        
        return {
            "status": "success",
            "message": f"Information collected for {full_name}",
            "data_collected": {
                "personal_info": bool(personal_info),
                "contact_info": bool(contact_info),
                "employment": bool(employment)
            },
            "next_step": "financial_analysis"
        }
    
    async def _analyze_financial_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze comprehensive financial profile"""
        monthly_income = data.get("monthly_income", {})
        monthly_expenses = data.get("monthly_expenses", {})
        debts = data.get("debts", [])
        assets = data.get("assets", [])
        
        # Calculate totals
        total_income = sum(monthly_income.values())
        total_expenses = sum(monthly_expenses.values())
        total_debt = sum(debt.get("current_balance", 0) for debt in debts)
        total_assets = sum(asset.get("current_value", 0) for asset in assets)
        
        # Categorize debts
        secured_debt = sum(debt.get("current_balance", 0) for debt in debts if debt.get("is_secured", False))
        unsecured_debt = total_debt - secured_debt
        
        # Calculate key ratios
        disposable_income = total_income - total_expenses
        debt_to_income = (total_debt / (total_income * 12)) if total_income > 0 else float('inf')
        
        # Financial stress assessment
        stress_indicators = []
        if disposable_income < 0:
            stress_indicators.append("Negative cash flow")
        if debt_to_income > 0.4:
            stress_indicators.append("High debt-to-income ratio")
        if unsecured_debt > total_income * 6:
            stress_indicators.append("Excessive unsecured debt")
        
        analysis = {
            "income_analysis": {
                "total_monthly": total_income,
                "primary_sources": list(monthly_income.keys())
            },
            "expense_analysis": {
                "total_monthly": total_expenses,
                "largest_categories": sorted(monthly_expenses.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            "debt_analysis": {
                "total_debt": total_debt,
                "secured_debt": secured_debt,
                "unsecured_debt": unsecured_debt,
                "monthly_payments": sum(debt.get("monthly_payment", 0) for debt in debts)
            },
            "cash_flow": {
                "disposable_income": disposable_income,
                "debt_to_income_ratio": debt_to_income
            },
            "stress_assessment": {
                "level": "critical" if len(stress_indicators) >= 3 else "high" if len(stress_indicators) >= 2 else "moderate" if len(stress_indicators) >= 1 else "low",
                "indicators": stress_indicators
            }
        }
        
        return {
            "status": "success",
            "message": "Financial profile analysis completed",
            "analysis": analysis,
            "next_step": "means_test_analysis"
        }
    
    async def _perform_means_test_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive means test analysis"""
        client_data = data.get("client_data", {})
        special_circumstances = data.get("special_circumstances", [])
        previous_bankruptcies = data.get("previous_bankruptcies", [])
        
        state = client_data.get("state", "").upper()
        household_size = client_data.get("household_size", 1)
        monthly_income = client_data.get("monthly_income", 0)
        
        # Current median income data (simplified - use real data in production)
        median_incomes_2025 = {
            1: 4847, 2: 6318, 3: 7326, 4: 8750, 5: 9844, 6: 10938, 7: 12032, 8: 13126
        }
        
        state_median = median_incomes_2025.get(household_size, 13126 + (household_size - 8) * 1094)
        income_percentage = (monthly_income / state_median * 100) if state_median > 0 else 0
        
        # Check previous bankruptcy restrictions
        bankruptcy_restrictions = self._check_bankruptcy_restrictions(previous_bankruptcies)
        
        # Determine eligibility
        if bankruptcy_restrictions:
            eligibility = "restricted"
            explanation = f"Previous bankruptcy restrictions apply: {bankruptcy_restrictions}"
        elif income_percentage < 100:
            eligibility = "chapter_7_presumed"
            explanation = "Income below state median - presumptively eligible for Chapter 7"
        elif income_percentage < 125:
            eligibility = "chapter_7_possible"
            explanation = "Income above median but below 125% - may still qualify for Chapter 7 with additional calculations"
        else:
            eligibility = "chapter_13_required"
            explanation = "Income above 125% of median - Chapter 13 payment plan required"
        
        # Chapter 13 feasibility
        total_debt = client_data.get("total_debt", 0)
        if total_debt > 2750000:  # Current Chapter 13 debt limits
            chapter_13_feasible = False
            chapter_13_note = "Total debt exceeds Chapter 13 limits"
        else:
            chapter_13_feasible = True
            chapter_13_note = "Debt within Chapter 13 limits"
        
        return {
            "status": "success",
            "analysis": {
                "means_test": {
                    "eligibility": eligibility,
                    "explanation": explanation,
                    "income_percentage_of_median": round(income_percentage, 1),
                    "state_median": state_median
                },
                "chapter_13_feasibility": {
                    "feasible": chapter_13_feasible,
                    "note": chapter_13_note
                },
                "special_circumstances": special_circumstances
            },
            "next_step": "consultation_report"
        }
    
    def _check_bankruptcy_restrictions(self, previous_bankruptcies: List[Dict]) -> str:
        """Check for time restrictions based on previous bankruptcies"""
        if not previous_bankruptcies:
            return ""
        
        # Simplified restriction check - implement full logic in production
        most_recent = max(previous_bankruptcies, key=lambda x: x.get('discharge_date', ''))
        chapter = most_recent.get('chapter', '')
        
        if chapter == '7':
            return "Must wait 8 years from previous Chapter 7 discharge"
        elif chapter == '13':
            return "Must wait 2 years from previous Chapter 13 discharge"
        
        return ""
    
    def _validate_ssn(self, ssn: str) -> bool:
        """Validate SSN format"""
        import re
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        return bool(re.match(pattern, ssn))
    
    async def _generate_consultation_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive consultation report"""
        client_name = data.get("client_name", "Client")
        
        return {
            "status": "success",
            "message": f"Consultation report generated for {client_name}",
            "report": {
                "summary": "Comprehensive bankruptcy consultation completed",
                "recommendations": ["Consult with bankruptcy attorney", "Gather required documents"],
                "next_steps": ["Complete credit counseling", "File appropriate chapter"]
            }
        }
    
    def get_webrtc_config(self) -> Dict[str, Any]:
        """Get WebRTC configuration for client"""
        return {
            "iceServers": [
                {"urls": "stun:stun.l.google.com:19302"}
            ],
            "audio": {
                "sampleRate": 24000,
                "channelCount": 1,
                "echoCancellation": True,
                "noiseSuppression": True,
                "autoGainControl": True
            }
        }


# Legacy compatibility class for existing main.py and production code
class SOTA_Voice:
    """Legacy compatibility wrapper for production system"""

    def __init__(self, settings):
        self.settings = settings
        self.voice_system = ModernRealtimeVoiceSystem(settings)
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Initialize the voice system"""
        try:
            success = await self.voice_system.initialize()
            self.is_initialized = success
            if success:
                logger.info("SOTA Voice system initialized successfully")
            return success
        except Exception as e:
            logger.error(f"Failed to initialize SOTA Voice: {e}")
            return False

    async def speak(self, text: str) -> bool:
        """Speak text using the voice system"""
        try:
            logger.info(f"SOTA_Voice speaking: {text}")
            # For production mode, we'll log the speech instead of actual TTS
            # since the main consultation uses WebRTC
            return True
        except Exception as e:
            logger.error(f"Failed to speak: {e}")
            return False

    async def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """Listen for voice input (placeholder for WebRTC mode)"""
        logger.info("Voice listening mode (WebRTC handles actual audio)")
        return None

    async def start_conversation(self) -> bool:
        """Start the voice conversation"""
        if not self.is_initialized:
            await self.initialize()

        # Start with a welcome message
        return await self.speak("Hello! Welcome to DocketVoice. I'm here to help you complete your bankruptcy paperwork through a simple conversation. Are you ready to begin?")

    def get_conversation_history(self) -> list:
        """Get conversation history"""
        return []

    async def interrupt(self):
        """Interrupt current response"""
        logger.info("Voice response interrupted")

    async def shutdown(self):
        """Shutdown voice system"""
        logger.info("SOTA Voice system shutdown")


# Export both classes for compatibility
__all__ = ['ModernRealtimeVoiceSystem', 'SOTA_Voice', 'RealtimeConfig']
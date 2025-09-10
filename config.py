"""
SOTA Configuration Management
Modern configuration system with validation, environment handling, and secrets management
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings
from enum import Enum

class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class VoiceProvider(str, Enum):
    """Voice service providers"""
    ELEVENLABS = "elevenlabs"
    AZURE = "azure"
    OPENAI = "openai"
    DEEPGRAM = "deepgram"

class AIProvider(str, Enum):
    """AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"

class VoiceConfig(BaseSettings):
    """Voice service configuration"""
    
    # Primary voice provider
    primary_provider: VoiceProvider = VoiceProvider.ELEVENLABS
    fallback_provider: VoiceProvider = VoiceProvider.AZURE
    
    # ElevenLabs
    elevenlabs_api_key: Optional[SecretStr] = None
    elevenlabs_voice_id: str = "Rachel"
    
    # Azure Speech
    azure_speech_key: Optional[SecretStr] = None
    azure_speech_region: str = "eastus"
    
    # OpenAI TTS
    openai_tts_model: str = "tts-1-hd"
    
    # Deepgram
    deepgram_api_key: Optional[SecretStr] = None
    
    class Config:
        env_prefix = "VOICE_"
        case_sensitive = False

class AIConfig(BaseSettings):
    """AI service configuration"""
    
    # Primary AI provider
    primary_provider: AIProvider = AIProvider.OPENAI
    fallback_provider: AIProvider = AIProvider.ANTHROPIC
    
    # OpenAI
    openai_api_key: Optional[SecretStr] = Field(default=None, env='OPENAI_API_KEY')
    openai_base_url: str = "https://api.openai.com/v1"
    
    # Models (Updated September 2025)
    openai_reasoning_model: str = "gpt-4o-mini"
    openai_mini_reasoning_model: str = "gpt-4o-mini"
    openai_chat_model: str = "gpt-4o-mini"
    
    # Anthropic (Updated September 2025)
    anthropic_api_key: Optional[SecretStr] = Field(default=None, env='ANTHROPIC_API_KEY')
    anthropic_model: str = "claude-3.5-sonnet-20240620"
    
    # Generation parameters
    temperature: float = 0.1  # Low for legal accuracy
    max_tokens: int = 8192 # Increased for modern models
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

class SecurityConfig(BaseSettings):
    """Security and privacy configuration"""
    
    # Encryption
    encryption_key: Optional[SecretStr] = None
    data_encryption_enabled: bool = True
    
    class Config:
        env_prefix = "SECURITY_"
        case_sensitive = False

class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration"""
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "MONITORING_"
        case_sensitive = False

class DocumentsConfig(BaseSettings):
    """Document processing configuration"""
    
    # Processing settings
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "txt", "docx"]
    
    class Config:
        env_prefix = "DOCUMENTS_"
        case_sensitive = False

class BankruptcyConfig(BaseSettings):
    """Bankruptcy-specific configuration"""
    
    # Forms and schedules
    forms_output_dir: str = "./output/forms"
    
    class Config:
        env_prefix = "BANKRUPTCY_"
        case_sensitive = False

class AgentConfig(BaseSettings):
    """Agent configuration"""
    
    # Agent settings
    max_conversation_length: int = 100
    enable_voice: bool = True
    
    class Config:
        env_prefix = "AGENT_"
        case_sensitive = False

class Settings(BaseSettings):
    """Main application settings"""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Application
    app_name: str = "DocketVoice - SOTA Bankruptcy Assistant"
    app_version: str = "2.0.0"
    
    # Sub-configurations
    voice: VoiceConfig = VoiceConfig()
    ai: AIConfig = AIConfig()
    security: SecurityConfig = SecurityConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    documents: DocumentsConfig = DocumentsConfig()
    bankruptcy: BankruptcyConfig = BankruptcyConfig()
    agent: AgentConfig = AgentConfig()
    
    def get_ai_api_key(self) -> Optional[str]:
        """Get the primary AI API key"""
        if self.ai.primary_provider == AIProvider.OPENAI:
            if self.ai.openai_api_key:
                return self.ai.openai_api_key.get_secret_value()
            # Fallback to environment variable
            return os.getenv('OPENAI_API_KEY')
        elif self.ai.primary_provider == AIProvider.ANTHROPIC:
            if self.ai.anthropic_api_key:
                return self.ai.anthropic_api_key.get_secret_value()
            # Fallback to environment variable  
            return os.getenv('ANTHROPIC_API_KEY')
        return None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra fields to be ignored instead of raising errors
        case_sensitive = False
        
def load_settings() -> Settings:
    """Load and validate settings"""
    return Settings()

# DocketVoiceConfig class for compatibility
class DocketVoiceConfig:
    def __init__(self):
        self.settings = load_settings()
    
    def get_ai_api_key(self) -> str:
        """Get OpenAI API key from environment or settings"""
        return self.settings.get_ai_api_key()
    
    @staticmethod
    def load_config(config_path: Optional[str] = None):
        return load_settings()


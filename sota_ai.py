"""
SOTA AI Provider - Multi-provider AI system with latest models
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from config import Settings

logger = logging.getLogger(__name__)

class SOTA_AI:
    """State-of-the-art AI provider with multiple backends"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.openai_client = None
        self.anthropic_client = None
        
    async def initialize(self):
        """Initialize AI providers"""
        try:
            if self.settings.ai.openai_api_key:
                # The OpenAI library automatically looks for the OPENAI_API_KEY env var.
                # Set it here to ensure the client is initialized correctly.
                api_key = self.settings.ai.openai_api_key.get_secret_value()
                os.environ["OPENAI_API_KEY"] = api_key
                self.openai_client = AsyncOpenAI()
                logger.info("OpenAI client initialized")
                
            if self.settings.ai.anthropic_api_key:
                self.anthropic_client = AsyncAnthropic(api_key=self.settings.ai.anthropic_api_key.get_secret_value())
                logger.info("Anthropic client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI providers: {str(e)}")
            raise
    
    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, model: Optional[str] = None) -> str:
        """Generate chat completion using primary provider"""
        
        try:
            if self.settings.ai.primary_provider == "openai" and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=model or self.settings.ai.openai_chat_model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content
                
            elif self.settings.ai.primary_provider == "anthropic" and self.anthropic_client:
                # Convert messages format for Anthropic
                system_message = ""
                user_messages = []
                
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        user_messages.append(msg)
                
                response = await self.anthropic_client.messages.create(
                    model=model or self.settings.ai.anthropic_model,
                    max_tokens=4000,
                    temperature=temperature,
                    system=system_message,
                    messages=user_messages
                )
                return response.content[0].text
                
            else:
                raise Exception("No AI provider available")
                
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            # Fallback to mock response for testing
            return "AI response not available - check API configuration"
    
    async def shutdown(self):
        """Cleanup AI resources"""
        logger.info("SOTA AI shutting down")
        await asyncio.sleep(0)

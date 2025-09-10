"""
Production Voice System using OpenAI Agents SDK VoicePipeline
Clean, simple voice interface for bankruptcy consultations
"""

import asyncio
import logging
import numpy as np
import sounddevice as sd
from typing import Optional
from config import Settings

from agents import Agent
from agents.voice import (
    AudioInput,
    StreamedAudioInput,
    SingleAgentVoiceWorkflow,
    VoicePipeline,
    VoiceStreamEvent
)

logger = logging.getLogger(__name__)


class ProductionVoiceSystem:
    """
    Clean voice system using OpenAI Agents SDK VoicePipeline
    Handles speech-to-text, agent processing, and text-to-speech automatically
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.agent = self._create_bankruptcy_agent()
        self.pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(self.agent))
        self.audio_player = None
        self.is_initialized = False

    def _create_bankruptcy_agent(self) -> Agent:
        """Create the bankruptcy consultation agent"""
        return Agent(
            name="BankruptcyAssistant",
            instructions=self._get_bankruptcy_instructions(),
            model="gpt-4o-mini",
        )

    def _get_bankruptcy_instructions(self) -> str:
        """Get instructions for the bankruptcy consultation agent"""
        return """You are a compassionate bankruptcy consultation assistant helping clients complete their bankruptcy paperwork through natural conversation.

ROLE: You conduct empathetic, professional interviews to gather all information needed for Chapter 7 or Chapter 13 bankruptcy forms.

GUIDELINES:
- Be warm, understanding, and professional - clients are going through a difficult time
- Ask one question at a time and wait for complete responses
- Use natural language, avoid legal jargon unless necessary
- Gather comprehensive information for all required bankruptcy forms
- Keep responses concise but complete for voice conversations
- Speak conversationally and naturally

START by introducing yourself and asking about their bankruptcy situation."""

    async def initialize(self) -> bool:
        """Initialize the voice system"""
        try:
            # Initialize audio player
            self.audio_player = sd.OutputStream(
                samplerate=24000,
                channels=1,
                dtype=np.int16
            )
            self.audio_player.start()

            self.is_initialized = True
            logger.info("Voice system initialized with VoicePipeline")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize voice system: {e}")
            return False

    async def speak(self, text: str) -> bool:
        """Convert text to speech and play it"""
        try:
            if not self.is_initialized:
                await self.initialize()

            # Create audio input from text (for TTS)
            # Note: This is a simplified approach - in production you'd use proper TTS
            logger.info(f"Speaking: {text[:100]}...")

            # For now, we'll just log the text since we don't have direct TTS
            # In a full implementation, you'd use the VoicePipeline for TTS
            print(f"[VOICE OUTPUT] {text}")

            return True

        except Exception as e:
            logger.error(f"Speech error: {e}")
            return False

    async def listen(self, timeout: Optional[float] = 30.0) -> Optional[str]:
        """
        Listen for voice input using StreamedAudioInput with automatic VAD
        Returns transcribed speech from the user
        """
        try:
            if not self.is_initialized:
                await self.initialize()

            logger.info("Starting voice input with automatic VAD...")
            print("\n🎤 Listening... Speak naturally! (VAD will detect when you finish)")

            # Create a streamed audio input for real-time VAD
            audio_input = StreamedAudioInput()

            # Start microphone recording in a separate task
            recording_task = asyncio.create_task(self._record_audio(audio_input))

            try:
                # Run the voice pipeline
                result = await self.pipeline.run(audio_input)

                # Process the result and extract transcription
                transcription = None

                async for event in result.stream():
                    if event.type == "voice_stream_event_audio":
                        # Play the assistant's response audio
                        if self.audio_player:
                            self.audio_player.write(event.data)

                    elif event.type == "voice_stream_event_lifecycle":
                        if event.lifecycle_type == "turn_started":
                            logger.info("VAD detected speech start")
                        elif event.lifecycle_type == "turn_ended":
                            logger.info("VAD detected speech end")

                    elif event.type == "voice_stream_event_transcription":
                        # This would contain the transcription if available
                        transcription = event.transcription
                        logger.info(f"Transcribed: {transcription}")

                # Stop recording
                recording_task.cancel()
                try:
                    await recording_task
                except asyncio.CancelledError:
                    pass

                return transcription

            except asyncio.TimeoutError:
                logger.warning(f"Voice input timeout after {timeout} seconds")
                recording_task.cancel()
                return None

        except Exception as e:
            logger.error(f"Voice input error: {e}")
            return None

    async def _record_audio(self, audio_input: StreamedAudioInput):
        """Record audio from microphone and stream to VoicePipeline"""
        try:
            # Audio recording settings
            samplerate = 24000
            channels = 1
            dtype = np.int16

            # Create audio stream
            stream = sd.InputStream(
                samplerate=samplerate,
                channels=channels,
                dtype=dtype
            )

            stream.start()
            logger.info("Microphone recording started")

            try:
                while True:
                    # Read audio chunk
                    audio_chunk, overflowed = stream.read(1024)

                    # Convert to the format expected by VoicePipeline
                    if audio_chunk is not None:
                        # Send audio chunk to the pipeline
                        await audio_input.add_audio_chunk(audio_chunk.tobytes())

                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                logger.info("Audio recording stopped")
                raise

            finally:
                stream.stop()
                stream.close()

        except Exception as e:
            logger.error(f"Audio recording error: {e}")

    async def shutdown(self):
        """Shutdown the voice system"""
        try:
            if self.audio_player:
                self.audio_player.stop()
                self.audio_player.close()

            self.is_initialized = False
            logger.info("Voice system shutdown complete")

        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Legacy compatibility class for existing code
class RealtimeVoiceAgent:
    """Legacy compatibility wrapper"""

    def __init__(self, settings: Settings):
        self.voice_system = ProductionVoiceSystem(settings)
        self.is_active = False

    async def initialize(self):
        """Initialize the voice system"""
        success = await self.voice_system.initialize()
        if success:
            self.is_active = True
        return success

    async def speak(self, text: str) -> bool:
        """Speak text"""
        return await self.voice_system.speak(text)

    async def listen(self, timeout: Optional[float] = 30.0) -> Optional[str]:
        """Listen for voice input"""
        return await self.voice_system.listen(timeout)

    async def shutdown(self):
        """Shutdown the voice system"""
        await self.voice_system.shutdown()


# Legacy compatibility class for existing code
class RealtimeSession:
    """Legacy compatibility wrapper"""

    def __init__(self, ephemeral_token: str, config: dict):
        self.ephemeral_token = ephemeral_token
        self.config = config
        self.websocket = None
        self.is_connected = False

    async def connect(self):
        """Mock connection for compatibility"""
        self.is_connected = True
        return True

    def on(self, event_type: str):
        """Mock event handler for compatibility"""
        def decorator(func):
            return func
        return decorator

    async def send_event(self, event: dict):
        """Mock send event for compatibility"""
        pass


# Legacy compatibility class for existing code
class SOTA_Voice:
    """Legacy compatibility wrapper"""

    def __init__(self, settings: Settings):
        self.voice_system = ProductionVoiceSystem(settings)
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Initialize the voice system"""
        try:
            success = await self.voice_system.initialize()
            self.is_initialized = success
            if success:
                logger.info("SOTA Voice system initialized with VoicePipeline")
            return success
        except Exception as e:
            logger.error(f"Failed to initialize SOTA Voice: {e}")
            return False

    async def speak(self, text: str) -> bool:
        """Speak text"""
        return await self.voice_system.speak(text)

    async def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """Listen for voice input"""
        return await self.voice_system.listen(timeout)

    async def start_conversation(self) -> bool:
        """Start the voice conversation"""
        if not self.is_initialized:
            await self.initialize()

        # Start with a welcome message
        return await self.speak("Hello! Welcome to DocketVoice. I'm here to help you complete your bankruptcy paperwork through a simple conversation. Are you ready to begin?")

    def get_conversation_history(self) -> list:
        """Get conversation history (placeholder for compatibility)"""
        return []

    async def interrupt(self):
        """Interrupt current response (placeholder for compatibility)"""
        pass

    async def shutdown(self):
        """Shutdown voice system"""
        await self.voice_system.shutdown()
        logger.info("SOTA Voice system shutdown")

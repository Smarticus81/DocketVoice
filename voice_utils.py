from dotenv import load_dotenv
import os
# Load .env at the very start and override
load_dotenv(override=True)

import asyncio
import threading
import tempfile
import time
import queue
import pyaudio
import numpy as np
from elevenlabs import ElevenLabs
import pygame
from aiortc import RTCPeerConnection, RTCConfiguration, RTCIceServer, RTCSessionDescription
from aiortc.contrib.media import MediaRelay
import json
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webrtc-voice")

# Create clients
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
openai_client = None  # We'll use direct WebRTC connection

# Voice settings
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Rachel")

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000  # 24kHz for Realtime API
CHUNK = 1024

# Global state
audio_queue = queue.Queue()
response_queue = queue.Queue()
is_listening = False
is_speaking = False
conversation_active = False

# Initialize PyAudio
audio = pyaudio.PyAudio()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Check your .env file.")

class WebRTCVoiceManager:
    def __init__(self):
        self.pc = None
        self.audio_stream = None
        self.data_channel = None
        self.is_connected = False
        self.conversation_state = "idle"
        self.audio_buffer = []
        self.ephemeral_key = None
        self.model = "gpt-realtime"
        # Create a dedicated asyncio event loop running in a background thread
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_coro(self, coro):
        """Schedule a coroutine on the background event loop."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    async def get_ephemeral_key(self):
        """Get ephemeral API key for WebRTC connection"""
        try:
            session_config = {
                "session": {
                    "type": "realtime",
                    "model": self.model,
                    "instructions": "You are a bankruptcy petition assistant. Help users fill out Chapter 7 or Chapter 13 bankruptcy forms through natural conversation. Ask questions one at a time and be conversational.",
                    "audio": {
                        "output": {
                            "voice": "marin"
                        }
                    }
                }
            }

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai_client.post(
                    "https://api.openai.com/v1/realtime/client_secrets",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=session_config,
                    timeout=20
                )
            )

            if response.status_code == 200:
                data = response.json()
                self.ephemeral_key = data.get("value")
                logger.info("✅ Ephemeral key obtained")
                return True
            else:
                logger.error(f"❌ Failed to get ephemeral key: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Ephemeral key error: {e}")
            return False

    async def setup_webrtc_connection(self):
        """Set up WebRTC peer connection"""
        try:
            # Create peer connection
            config = RTCConfiguration(
                iceServers=[
                    RTCIceServer(urls="stun:stun.l.google.com:19302")
                ]
            )
            self.pc = RTCPeerConnection(configuration=config)

            # Set up audio handling
            @self.pc.on("track")
            def on_track(track):
                if track.kind == "audio":
                    logger.info("🎵 Audio track received")
                    # Handle incoming audio from OpenAI
                    asyncio.create_task(self.handle_audio_track(track))

            # Set up data channel for events
            self.data_channel = self.pc.createDataChannel("oai-events")

            @self.data_channel.on("open")
            def on_open():
                logger.info("📡 Data channel opened")
                self.is_connected = True

            @self.data_channel.on("message")
            def on_message(message):
                asyncio.create_task(self.handle_data_message(message))

            # Add local audio track (microphone)
            # Note: In a real implementation, you'd add the microphone track here
            # For now, we'll handle audio separately

            return True

        except Exception as e:
            logger.error(f"❌ WebRTC setup error: {e}")
            return False

    async def connect_realtime(self):
        """Connect to OpenAI Realtime API via WebRTC"""
        try:
            # Get ephemeral key
            if not await self.get_ephemeral_key():
                return False

            # Set up WebRTC connection
            if not await self.setup_webrtc_connection():
                return False

            # Create offer
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)

            # Send offer to OpenAI
            sdp_url = f"https://api.openai.com/v1/realtime/calls?model={self.model}"
            sdp_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai_client.post(
                    sdp_url,
                    headers={
                        "Authorization": f"Bearer {self.ephemeral_key}",
                        "Content-Type": "application/sdp"
                    },
                    data=offer.sdp,
                    timeout=20
                )
            )

            if sdp_response.status_code == 200:
                answer_sdp = sdp_response.text
                # Use RTCSessionDescription for aiortc
                answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
                await self.pc.setRemoteDescription(answer)
                logger.info("🎤 WebRTC connection established")
                return True
            else:
                logger.error(f"❌ SDP exchange failed: {sdp_response.status_code} - {sdp_response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ WebRTC connection error: {e}")
            return False

    async def handle_audio_track(self, track):
        """Handle incoming audio from OpenAI"""
        try:
            while True:
                frame = await track.recv()
                if frame:
                    # Convert audio frame to bytes
                    audio_data = frame.to_bytes()
                    self.audio_buffer.append(audio_data)

        except Exception as e:
            logger.error(f"❌ Audio track error: {e}")

    async def handle_data_message(self, message):
        """Handle data channel messages"""
        try:
            event = json.loads(message)

            if event["type"] == "conversation.item.input_audio_transcription.completed":
                # User speech transcribed
                transcript = event.get("transcript", "")
                if transcript:
                    print(f"🎤 User: {transcript}")
                    response_queue.put(transcript)

            elif event["type"] == "response.text.delta":
                # Handle text response
                if event.get("delta"):
                    print(f"🤖 Agent: {event['delta']}", end="", flush=True)

            elif event["type"] == "response.audio.done":
                # Audio response complete
                if self.audio_buffer:
                    self.play_audio_response()
                    self.audio_buffer = []

            elif event["type"] == "error":
                logger.error(f"❌ Realtime API error: {event}")

        except Exception as e:
            logger.error(f"❌ Data message error: {e}")

    def play_audio_response(self):
        """Play the accumulated audio response"""
        global is_speaking
        if not self.audio_buffer:
            return

        is_speaking = True
        try:
            # Combine audio chunks
            combined_audio = b''.join(self.audio_buffer)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                # Convert PCM16 to WAV
                import wave
                with wave.open(temp_file, 'wb') as wav_file:
                    wav_file.setnchannels(CHANNELS)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(RATE)
                    wav_file.writeframes(combined_audio)

                temp_file_path = temp_file.name

            # Play using pygame
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

            # Clean up
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"❌ Audio playback error: {e}")
        finally:
            is_speaking = False
            self.audio_buffer = []

    async def send_audio_chunk(self, audio_data):
        """Send audio chunk to Realtime API"""
        if not self.is_connected or not self.data_channel:
            return

        try:
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')

            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_b64
            }

            self.data_channel.send(json.dumps(event))

        except Exception as e:
            logger.error(f"❌ Failed to send audio chunk: {e}")

    async def commit_audio(self):
        """Commit the current audio buffer for processing"""
        if not self.is_connected or not self.data_channel:
            return

        try:
            event = {
                "type": "input_audio_buffer.commit"
            }
            self.data_channel.send(json.dumps(event))

        except Exception as e:
            logger.error(f"❌ Failed to commit audio: {e}")

    def start_conversation(self):
        """Start the voice conversation"""
        global conversation_active, is_listening
        conversation_active = True
        is_listening = True
        self.conversation_state = "listening"

        # Start WebRTC connection on background event loop
        self.run_coro(self.connect_realtime())

        # Start audio capture
        audio_thread = threading.Thread(target=self.audio_capture_loop, daemon=True)
        audio_thread.start()

        print("🎤 Voice conversation started - WebRTC Realtime API active")

    def end_conversation(self):
        """End the voice conversation"""
        global conversation_active, is_listening
        conversation_active = False
        is_listening = False
        self.conversation_state = "idle"

        if self.pc:
            self.run_coro(self.pc.close())
            self.pc = None
            self.is_connected = False

        print("🎤 Voice conversation ended")

    def audio_capture_loop(self):
        """Continuously capture audio from microphone"""
        self.audio_stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("🎤 Audio capture started...")

        while is_listening:
            try:
                data = self.audio_stream.read(CHUNK, exception_on_overflow=False)

                # Send audio chunk to Realtime API (schedule on loop)
                if self.is_connected:
                    self.run_coro(self.send_audio_chunk(data))

            except Exception as e:
                logger.error(f"❌ Audio capture error: {e}")
                break

        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        print("🎤 Audio capture stopped")

    async def send_text_message(self, text):
        """Send a text message to the Realtime API"""
        if not self.is_connected or not self.data_channel:
            return

        try:
            event = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            }

            self.data_channel.send(json.dumps(event))

            # Create response
            response_event = {
                "type": "response.create"
            }

            self.data_channel.send(json.dumps(response_event))

        except Exception as e:
            logger.error(f"❌ Failed to send text message: {e}")

# Global WebRTC manager
webrtc_manager = WebRTCVoiceManager()

# Initialize OpenAI client for REST API calls
import requests
openai_client = requests.Session()

# Legacy TTS function for compatibility
def elevenlabs_tts(text):
    """Text-to-speech using ElevenLabs (fallback)"""
    audio_response = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2"
    )

    # Handle the audio response
    if hasattr(audio_response, 'content'):
        audio_data = audio_response.content
    elif hasattr(audio_response, '__iter__'):
        audio_data = b''.join(audio_response)
    else:
        audio_data = bytes(audio_response)

    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        temp_file.write(audio_data)
        temp_file_path = temp_file.name

    # Play using pygame
    pygame.mixer.music.load(temp_file_path)
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)

    # Stop music and unload to free the file
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    # Small additional delay to ensure file is released
    pygame.time.wait(200)

    # Clean up
    try:
        os.unlink(temp_file_path)
    except PermissionError:
        pass

# Enhanced voice prompt for conversational flow
def voice_prompt(prompt_text, timeout=10):
    """Enhanced voice prompt with WebRTC Realtime API"""
    # Send the prompt as text message via background loop
    webrtc_manager.run_coro(webrtc_manager.send_text_message(prompt_text))

    # Wait for user response
    try:
        user_input = response_queue.get(timeout=timeout)
        return user_input.strip()
    except queue.Empty:
        # Timeout - try again
        webrtc_manager.run_coro(webrtc_manager.send_text_message("I didn't catch that. Could you please repeat?"))
        return voice_prompt(prompt_text, timeout)

# Functions for managing conversation state
def start_voice_conversation():
    """Start the continuous voice conversation"""
    webrtc_manager.start_conversation()

def end_voice_conversation():
    """End the continuous voice conversation"""
    webrtc_manager.end_conversation()

def is_conversation_active():
    """Check if conversation is active"""
    return conversation_active

# Legacy function for backward compatibility
def listen_stt():
    """Legacy function - use voice_prompt instead"""
    try:
        return response_queue.get(timeout=5)
    except queue.Empty:
        return ""

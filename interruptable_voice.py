import os
import signal
import threading
import time
from typing import Optional, Callable, Any, List
from voice_utils import (
    elevenlabs_tts, listen_stt, start_realtime_listening, stop_realtime_listening,
    set_voice_context, register_voice_command, register_voice_interrupt,
    get_voice_commands, is_voice_command_available, realtime_listener
)

class InterruptableVoiceSystem:
    """
    Interruptable voice system that allows pausing, resuming, and graceful exit
    Based on threading.Event and signal handling for responsive control
    Now integrated with real-time voice listening for immediate response
    """
    
    def __init__(self):
        # Control events
        self.pause_event = threading.Event()
        self.resume_event = threading.Event()
        self.quit_event = threading.Event()
        self.interrupt_detected = threading.Event()
        
        # State tracking
        self.is_paused = False
        self.is_running = True
        self.current_operation = None
        
        # Signal handling
        self.original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._handle_sigint)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize real-time voice listening
        self._setup_voice_commands()
        self._setup_voice_interrupts()
    
    def _setup_voice_commands(self):
        """Setup voice command handlers"""
        # Navigation commands
        register_voice_command("help", self._handle_help_command)
        register_voice_command("pause", self._handle_pause_command)
        register_voice_command("resume", self._handle_resume_command)
        register_voice_command("quit", self._handle_quit_command)
        register_voice_command("go_back", self._handle_go_back_command)
        register_voice_command("skip", self._handle_skip_command)
        register_voice_command("repeat", self._handle_repeat_command)
        
        # Bankruptcy specific commands
        register_voice_command("start_over", self._handle_start_over_command)
        register_voice_command("save", self._handle_save_command)
        register_voice_command("review", self._handle_review_command)
        register_voice_command("analyze_documents", self._handle_analyze_documents_command)
        register_voice_command("means_test", self._handle_means_test_command)
        register_voice_command("generate_petition", self._handle_generate_petition_command)
        
        # Information commands
        register_voice_command("personal_info", self._handle_personal_info_command)
        register_voice_command("income_info", self._handle_income_info_command)
        register_voice_command("expense_info", self._handle_expense_info_command)
        register_voice_command("asset_info", self._handle_asset_info_command)
        register_voice_command("debt_info", self._handle_debt_info_command)
    
    def _setup_voice_interrupts(self):
        """Setup voice interrupt handlers"""
        # High-priority interrupt commands
        register_voice_interrupt("pause", self._handle_pause_command)
        register_voice_interrupt("stop", self._handle_pause_command)
        register_voice_interrupt("quit", self._handle_quit_command)
        register_voice_interrupt("exit", self._handle_quit_command)
        register_voice_interrupt("emergency", self._handle_emergency_command)
        register_voice_interrupt("cancel", self._handle_cancel_command)
    
    def _handle_help_command(self, intent_result):
        """Handle help command"""
        self._show_voice_help()
    
    def _handle_pause_command(self, intent_result):
        """Handle pause command"""
        print("[VOICE COMMAND] Pause requested")
        self.interrupt_detected.set()
        self.pause_event.set()
        self.is_paused = True
        elevenlabs_tts("Application paused. Say continue to resume, quit to exit, or help for options.")
    
    def _handle_resume_command(self, intent_result):
        """Handle resume command"""
        print("[VOICE COMMAND] Resume requested")
        self.resume()
    
    def _handle_quit_command(self, intent_result):
        """Handle quit command"""
        print("[VOICE COMMAND] Quit requested")
        if voice_confirm("Are you sure you want to quit?"):
            self.quit()
    
    def _handle_go_back_command(self, intent_result):
        """Handle go back command"""
        print("[VOICE COMMAND] Go back requested")
        elevenlabs_tts("Going back to previous step.")
        # Implementation would depend on application state
    
    def _handle_skip_command(self, intent_result):
        """Handle skip command"""
        print("[VOICE COMMAND] Skip requested")
        elevenlabs_tts("Skipping current step.")
        # Implementation would depend on application state
    
    def _handle_repeat_command(self, intent_result):
        """Handle repeat command"""
        print("[VOICE COMMAND] Repeat requested")
        if self.current_operation:
            elevenlabs_tts(f"Currently working on: {self.current_operation}")
        else:
            elevenlabs_tts("No current operation in progress.")
    
    def _handle_start_over_command(self, intent_result):
        """Handle start over command"""
        print("[VOICE COMMAND] Start over requested")
        if voice_confirm("Are you sure you want to start over? This will clear all data."):
            elevenlabs_tts("Starting over. All data cleared.")
            # Implementation would depend on application state
    
    def _handle_save_command(self, intent_result):
        """Handle save command"""
        print("[VOICE COMMAND] Save requested")
        elevenlabs_tts("Saving current progress.")
        # Implementation would depend on application state
    
    def _handle_review_command(self, intent_result):
        """Handle review command"""
        print("[VOICE COMMAND] Review requested")
        elevenlabs_tts("Reviewing collected information.")
        # Implementation would depend on application state
    
    def _handle_analyze_documents_command(self, intent_result):
        """Handle analyze documents command"""
        print("[VOICE COMMAND] Analyze documents requested")
        elevenlabs_tts("Starting document analysis.")
        # Implementation would depend on application state
    
    def _handle_means_test_command(self, intent_result):
        """Handle means test command"""
        print("[VOICE COMMAND] Means test requested")
        elevenlabs_tts("Starting means test calculation.")
        # Implementation would depend on application state
    
    def _handle_generate_petition_command(self, intent_result):
        """Handle generate petition command"""
        print("[VOICE COMMAND] Generate petition requested")
        elevenlabs_tts("Generating bankruptcy petition.")
        # Implementation would depend on application state
    
    def _handle_personal_info_command(self, intent_result):
        """Handle personal info command"""
        print("[VOICE COMMAND] Personal info requested")
        elevenlabs_tts("Showing personal information section.")
        # Implementation would depend on application state
    
    def _handle_income_info_command(self, intent_result):
        """Handle income info command"""
        print("[VOICE COMMAND] Income info requested")
        elevenlabs_tts("Showing income information section.")
        # Implementation would depend on application state
    
    def _handle_expense_info_command(self, intent_result):
        """Handle expense info command"""
        print("[VOICE COMMAND] Expense info requested")
        elevenlabs_tts("Showing expense information section.")
        # Implementation would depend on application state
    
    def _handle_asset_info_command(self, intent_result):
        """Handle asset info command"""
        print("[VOICE COMMAND] Asset info requested")
        elevenlabs_tts("Showing asset information section.")
        # Implementation would depend on application state
    
    def _handle_debt_info_command(self, intent_result):
        """Handle debt info command"""
        print("[VOICE COMMAND] Debt info requested")
        elevenlabs_tts("Showing debt information section.")
        # Implementation would depend on application state
    
    def _handle_emergency_command(self, intent_result):
        """Handle emergency command"""
        print("[VOICE COMMAND] Emergency requested")
        elevenlabs_tts("Emergency mode activated. What do you need help with?")
        # Implementation would depend on application state
    
    def _handle_cancel_command(self, intent_result):
        """Handle cancel command"""
        print("[VOICE COMMAND] Cancel requested")
        elevenlabs_tts("Cancelling current operation.")
        # Implementation would depend on application state
    
    def _handle_sigint(self, signo, frame):
        """Handle Ctrl+C interrupt"""
        with self._lock:
            if not self.is_paused:
                self.interrupt_detected.set()
                self.pause_event.set()
                self.resume_event.clear()
                self.is_paused = True
                print("\n[INTERRUPT] Application paused. Enter 'c' to continue, 'q' to quit, or 'h' for help.")
                elevenlabs_tts("Application paused. Say continue to resume, quit to exit, or help for options.")
            else:
                # Force quit if already paused
                self.quit_event.set()
                self.is_running = False
                print("\n[FORCE QUIT] Exiting immediately...")
    
    def pause_menu(self) -> bool:
        """Interactive pause menu - returns True to continue, False to quit"""
        while self.is_paused and self.is_running:
            try:
                # Voice input for pause menu
                response = listen_stt(timeout=5, phrase_time_limit=10)
                if not response:
                    continue
                
                response_lower = response.lower()
                
                if any(word in response_lower for word in ['continue', 'resume', 'c', 'go', 'start']):
                    print("[RESUME] Resuming application...")
                    elevenlabs_tts("Resuming application.")
                    return True
                    
                elif any(word in response_lower for word in ['quit', 'exit', 'stop', 'q', 'end']):
                    print("[QUIT] User requested to quit.")
                    elevenlabs_tts("Quitting application.")
                    return False
                    
                elif any(word in response_lower for word in ['help', 'h', 'options', 'what']):
                    self._show_pause_help()
                    
                elif any(word in response_lower for word in ['status', 'where', 'progress']):
                    self._show_current_status()
                    
                else:
                    elevenlabs_tts("I didn't understand that. Say continue to resume, quit to exit, or help for options.")
                    
            except Exception as e:
                print(f"[PAUSE MENU ERROR] {e}")
                continue
        
        return False
    
    def _show_pause_help(self):
        """Show available pause menu options"""
        help_text = """
        Available commands:
        - 'continue' or 'resume': Resume the application
        - 'quit' or 'exit': Exit the application
        - 'help': Show this help message
        - 'status': Show current progress
        """
        print(help_text)
        elevenlabs_tts("Available commands: continue to resume, quit to exit, help for options, status for progress.")
    
    def _show_current_status(self):
        """Show current application status"""
        if self.current_operation:
            status_text = f"Currently working on: {self.current_operation}"
            print(f"[STATUS] {status_text}")
            elevenlabs_tts(status_text)
        else:
            print("[STATUS] No current operation")
            elevenlabs_tts("No current operation in progress.")
    
    def _show_voice_help(self):
        """Show voice navigation help"""
        help_text = """
        Voice Commands:
        - 'help': Show this help
        - 'pause' or 'stop': Pause the application
        - 'continue' or 'resume': Resume after pause
        - 'quit' or 'exit': Exit the application
        - 'start over': Restart the process
        - 'save': Save current progress
        - 'review': Review collected information
        - 'analyze documents': Process uploaded documents
        - 'means test': Calculate bankruptcy eligibility
        - 'generate petition': Create bankruptcy forms
        """
        print(help_text)
        elevenlabs_tts("Voice commands: help for options, pause to stop, continue to resume, quit to exit, and many more bankruptcy-specific commands.")
    
    def resume(self):
        """Resume the application"""
        with self._lock:
            self.is_paused = False
            self.pause_event.clear()
            self.resume_event.set()
            self.interrupt_detected.clear()
            print("[RESUME] Application resumed.")
    
    def quit(self):
        """Gracefully quit the application"""
        with self._lock:
            self.is_running = False
            self.quit_event.set()
            self.pause_event.set()
            self.resume_event.set()
            print("[QUIT] Application quitting...")
    
    def check_interrupt(self) -> bool:
        """Check if interrupt was detected - non-blocking"""
        return self.interrupt_detected.is_set()
    
    def wait_for_resume(self, timeout: Optional[float] = None) -> bool:
        """Wait for resume signal - returns True if resumed, False if quit"""
        if self.quit_event.is_set():
            return False
        
        # Wait for resume or quit
        if timeout:
            resumed = self.resume_event.wait(timeout)
            if not resumed and self.quit_event.is_set():
                return False
        else:
            self.resume_event.wait()
            if self.quit_event.is_set():
                return False
        
        return True
    
    def interruptable_operation(self, operation_name: str, operation_func: Callable, *args, **kwargs) -> Any:
        """Execute an operation with interrupt handling"""
        self.current_operation = operation_name
        
        try:
            # Check for interrupt before starting
            if self.check_interrupt():
                self.pause_menu()
                if not self.is_running:
                    return None
            
            # Execute operation with periodic interrupt checks
            result = self._execute_with_interrupt_checks(operation_func, *args, **kwargs)
            
            # Check for interrupt after completion
            if self.check_interrupt():
                self.pause_menu()
                if not self.is_running:
                    return None
            
            return result
            
        finally:
            self.current_operation = None
    
    def _execute_with_interrupt_checks(self, operation_func: Callable, *args, **kwargs) -> Any:
        """Execute function with periodic interrupt checks"""
        # For long-running operations, we need to check interrupts periodically
        # This is a simplified version - in practice, you'd want to integrate
        # this with the specific operation's progress tracking
        
        # Start operation in a separate thread to allow interruption
        result_container = {'result': None, 'exception': None, 'completed': False}
        
        def run_operation():
            try:
                result_container['result'] = operation_func(*args, **kwargs)
                result_container['completed'] = True
            except Exception as e:
                result_container['exception'] = e
                result_container['completed'] = True
        
        operation_thread = threading.Thread(target=run_operation)
        operation_thread.daemon = True
        operation_thread.start()
        
        # Monitor operation with interrupt checks
        while not result_container['completed'] and self.is_running:
            if self.check_interrupt():
                # Wait for user decision
                if not self.pause_menu():
                    return None
                if not self.is_running:
                    return None
                self.resume()
            
            time.sleep(0.1)  # Small delay to prevent busy waiting
        
        # Wait for operation to complete
        operation_thread.join(timeout=1.0)
        
        if result_container['exception']:
            raise result_container['exception']
        
        return result_container['result']
    
    def interruptable_sleep(self, seconds: float) -> bool:
        """Sleep with interrupt handling - returns True if completed, False if interrupted"""
        if self.quit_event.is_set():
            return False
        
        # Use events for interruptable sleep
        if self.pause_event.wait(seconds):
            # Interrupted during sleep
            if self.quit_event.is_set():
                return False
            
            # Wait for resume
            return self.wait_for_resume()
        
        return True
    
    def interruptable_voice_prompt(self, prompt_text: str, allow_navigation: bool = True) -> Optional[str]:
        """Voice prompt with interrupt handling"""
        while self.is_running:
            # Check for interrupt before prompting
            if self.check_interrupt():
                if not self.pause_menu():
                    return None
                if not self.is_running:
                    return None
                self.resume()
            
            # Give the prompt
            elevenlabs_tts(prompt_text)
            print(f"🎤 {prompt_text}")
            
            # Listen for response with interrupt checking
            response = self._interruptable_listen()
            if response is None:  # Interrupted
                continue
            
            if not response:
                continue
            
            # Handle navigation commands
            if allow_navigation:
                if "help" in response.lower():
                    self._show_voice_help()
                    continue
                elif "pause" in response.lower() or "stop" in response.lower():
                    self.interrupt_detected.set()
                    self.pause_event.set()
                    if not self.pause_menu():
                        return None
                    if not self.is_running:
                        return None
                    self.resume()
                    continue
            
            return response.strip()
        
        return None
    
    def _interruptable_listen(self) -> Optional[str]:
        """Listen for speech with interrupt handling"""
        try:
            # Use a shorter timeout for more responsive interruption
            response = listen_stt(timeout=5, phrase_time_limit=10)
            
            # Check for interrupt after listening
            if self.check_interrupt():
                return None
            
            return response
            
        except Exception as e:
            print(f"[LISTEN ERROR] {e}")
            return None
    
    def start_voice_listening(self):
        """Start real-time voice listening"""
        start_realtime_listening()
        print("[VOICE] Real-time voice listening started")
    
    def stop_voice_listening(self):
        """Stop real-time voice listening"""
        stop_realtime_listening()
        print("[VOICE] Real-time voice listening stopped")
    
    def set_voice_context(self, context: str):
        """Set voice context for better intent recognition"""
        set_voice_context(context)
        print(f"[VOICE] Context set to: {context}")
    
    def cleanup(self):
        """Clean up resources and restore original signal handler"""
        signal.signal(signal.SIGINT, self.original_sigint)
        self.stop_voice_listening()
        self.quit()
    
    def __enter__(self):
        """Context manager entry"""
        self.start_voice_listening()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Global instance for easy access
voice_system = InterruptableVoiceSystem()

# Convenience functions
def interruptable_tts(text: str, wait_for_completion: bool = True) -> bool:
    """Interruptable text-to-speech"""
    if voice_system.check_interrupt():
        if not voice_system.pause_menu():
            return False
        if not voice_system.is_running:
            return False
        voice_system.resume()
    
    elevenlabs_tts(text, wait_for_completion)
    return True

def interruptable_listen(timeout: int = 10, phrase_time_limit: int = 15) -> Optional[str]:
    """Interruptable speech recognition"""
    return voice_system._interruptable_listen()

def check_and_handle_interrupt() -> bool:
    """Check for interrupt and handle pause menu - returns True if should continue"""
    if voice_system.check_interrupt():
        return voice_system.pause_menu()
    return True

def start_voice_system():
    """Start the voice system with real-time listening"""
    voice_system.start_voice_listening()

def stop_voice_system():
    """Stop the voice system"""
    voice_system.stop_voice_listening()

def get_available_voice_commands() -> List[str]:
    """Get list of available voice commands"""
    return get_voice_commands()

def is_voice_system_active() -> bool:
    """Check if voice system is active"""
    return is_voice_command_available() 
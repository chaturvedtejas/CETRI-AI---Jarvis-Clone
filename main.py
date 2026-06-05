import speech_recognition as sr
import pyttsx3
import whisper
import threading
import os
import sys
import json
import logging
import time
import re
import difflib
import platform
import psutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import webbrowser
import math
import random
from typing import Dict, List, Optional, Tuple, Any
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for colored console output
colorama.init(autoreset=True)

class CETRIConfig:
    """Configuration management for CETRI"""
    def __init__(self):
        self.config_file = Path.home() / ".cetri" / "config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            print(f"[!] Config load error: {e}")
            self.config = self.get_default_config()

    def get_default_config(self):
        """Get default configuration"""
        return {
            "voice": {
                "enabled": True,
                "rate": 180,
                "volume": 0.8,
                "voice_id": 0
            },
            "speech_recognition": {
                "enabled": True,
                "timeout": 10,
                "phrase_time_limit": 10,
                "energy_threshold": 300
            },
            "whisper": {
                "model": "base",
                "language": "en"
            },
            "interface": {
                "colors": True,
                "verbose": True,
                "auto_save": True
            },
            "logging": {
                "level": "INFO",
                "file_logging": True
            },
            "commands": {
                "fuzzy_matching": True,
                "confidence_threshold": 0.6
            }
        }

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[!] Config save error: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

class CETRILogger:
    """Advanced logging system for CETRI"""
    def __init__(self, config):
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('logging.level', 'INFO').upper())

        # Create logger
        self.logger = logging.getLogger('CETRI')
        self.logger.setLevel(log_level)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - '
            f'{Fore.GREEN}%(name)s{Style.RESET_ALL} - '
            f'{Fore.YELLOW}%(levelname)s{Style.RESET_ALL} - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler if enabled
        if self.config.get('logging.file_logging', True):
            log_file = Path.home() / ".cetri" / "cetri.log"
            log_file.parent.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log(self, level, message, *args, **kwargs):
        """Log a message"""
        getattr(self.logger, level)(message, *args, **kwargs)

class CETRI:
    """Advanced CETRI AI Assistant"""

    def __init__(self):
        self.config = CETRIConfig()
        self.logger = CETRILogger(self.config)

        # Initialize components
        self.engine = None
        self.model = None
        self.recognizer = None
        self.microphone = None

        # Session management
        self.session_start = datetime.now()
        self.command_history = []
        self.conversation_memory = []
        self.last_command_time = None

        # Command patterns and responses
        self.command_patterns = self.load_command_patterns()

        # System status
        self.system_info = self.get_system_info()

        # Initialize interface
        self.clear_screen()
        self.show_welcome()

        # Initialize components
        self.initialize_components()

        # Start main interface
        self.show_main_menu()

    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_welcome(self):
        """Show welcome screen"""
        print(f"""
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
{Fore.YELLOW}{' '*20}🎯 CETRI AI ASSISTANT v2.0{Style.RESET_ALL}
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
{Fore.GREEN}[AI] Inspired by JARVIS - Advanced Voice & Command Interface{Style.RESET_ALL}
{Fore.BLUE}⚡ Features: Voice I/O • Natural Language • Context Awareness{Style.RESET_ALL}
{Fore.MAGENTA}🔧 System: {self.get_system_info()['os']} • Python {sys.version.split()[0]}{Style.RESET_ALL}
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
        """)

    def get_system_info(self):
        """Get system information"""
        try:
            return {
                'os': f"{platform.system()} {platform.release()}",
                'cpu': f"{psutil.cpu_count()} cores",
                'memory': f"{round(psutil.virtual_memory().total / (1024**3), 1)}GB RAM",
                'python': sys.version.split()[0]
            }
        except:
            return {'os': 'Unknown', 'cpu': 'Unknown', 'memory': 'Unknown', 'python': 'Unknown'}

    def initialize_components(self):
        """Initialize all CETRI components with error handling"""
        print(f"\n{Fore.BLUE}🔧 Initializing CETRI Components...{Style.RESET_ALL}")

        # Initialize Text-to-Speech
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[self.config.get('voice.voice_id', 0)].id)
            self.engine.setProperty('rate', self.config.get('voice.rate', 180))
            self.engine.setProperty('volume', self.config.get('voice.volume', 0.8))
            print(f"{Fore.GREEN}✓ Text-to-Speech initialized{Style.RESET_ALL}")
            self.logger.log('info', 'TTS initialized successfully')
        except Exception as e:
            print(f"{Fore.RED}✗ TTS Error: {e}{Style.RESET_ALL}")
            self.engine = None
            self.logger.log('error', f'TTS initialization failed: {e}')

        # Initialize Whisper Model
        try:
            model_name = self.config.get('whisper.model', 'base')
            print(f"{Fore.BLUE}⏳ Loading Whisper model '{model_name}'...{Style.RESET_ALL}")
            self.model = whisper.load_model(model_name)
            print(f"{Fore.GREEN}✓ Whisper model loaded{Style.RESET_ALL}")
            self.logger.log('info', f'Whisper model {model_name} loaded successfully')
        except Exception as e:
            print(f"{Fore.RED}✗ Whisper Error: {e}{Style.RESET_ALL}")
            self.model = None
            self.logger.log('error', f'Whisper initialization failed: {e}')

        # Initialize Speech Recognition
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.config.get('speech_recognition.energy_threshold', 300)
            self.microphone = sr.Microphone()
            print(f"{Fore.GREEN}✓ Speech Recognition initialized{Style.RESET_ALL}")
            self.logger.log('info', 'Speech recognition initialized successfully')
        except Exception as e:
            print(f"{Fore.RED}✗ Speech Recognition Error: {e}{Style.RESET_ALL}")
            self.recognizer = None
            self.microphone = None
            self.logger.log('error', f'Speech recognition initialization failed: {e}')

        print(f"\n{Fore.GREEN}🎯 CETRI initialization complete!{Style.RESET_ALL}")
        self.speak("CETRI online and ready for your commands.")
        time.sleep(1)

    def load_command_patterns(self):
        """Load command patterns and responses"""
        return {
            'greetings': {
                'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings'],
                'responses': ['Hello! How can I assist you today?', 'Hi there! What can I do for you?', 'Greetings! How may I help you?']
            },
            'time': {
                'patterns': ['time', 'what time', 'current time', 'clock', 'tell me the time'],
                'responses': ['The current time is {time}', 'It\'s {time} right now', 'The time is currently {time}']
            },
            'date': {
                'patterns': ['date', 'what date', 'today', 'current date', 'what day'],
                'responses': ['Today is {date}', 'The date is {date}', 'It\'s {date} today']
            },
            'help': {
                'patterns': ['help', 'commands', 'what can you do', 'assist', 'guide'],
                'responses': ['I can help with various tasks. Try asking about time, files, system info, or calculations.']
            },
            'quit': {
                'patterns': ['quit', 'exit', 'shutdown', 'bye', 'goodbye', 'stop'],
                'responses': ['Shutting down. Goodbye!', 'Goodbye! Have a great day!', 'CETRI shutting down...']
            },
            'file_operations': {
                'create': ['create file', 'new file', 'make file'],
                'open': ['open file', 'show files', 'file explorer'],
                'list': ['list files', 'show directory', 'files in folder']
            },
            'system_info': {
                'patterns': ['system info', 'computer info', 'specs', 'system specs'],
                'responses': ['System Information: {info}']
            },
            'calculations': {
                'patterns': ['calculate', 'math', 'compute', 'solve'],
                'responses': ['The result is: {result}']
            }
        }

    def speak(self, text, force=False):
        """Enhanced text-to-speech with error handling"""
        if not self.config.get('voice.enabled', True) and not force:
            return

        if self.engine:
            try:
                print(f"{Fore.CYAN}[AUDIO] {text}{Style.RESET_ALL}")
                self.engine.say(text)
                self.engine.runAndWait()
                self.logger.log('debug', f'Speech output: {text}')
            except Exception as e:
                print(f"{Fore.RED}[WARNING] Speech Error: {e}{Style.RESET_ALL}")
                self.logger.log('error', f'Speech error: {e}')
        else:
            print(f"{Fore.YELLOW}[MUTED] {text}{Style.RESET_ALL}")

    def listen_once(self):
        """Enhanced voice input with better error handling"""
        if not self.recognizer or not self.microphone:
            print(f"{Fore.YELLOW}[MICROPHONE] Microphone not available. Using text input.{Style.RESET_ALL}")
            user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip()
            return user_input

        try:
            print(f"{Fore.BLUE}[MIC] Listening... (speak now or press Ctrl+C to cancel){Style.RESET_ALL}")

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                timeout = self.config.get('speech_recognition.timeout', 10)

                try:
                    audio = self.recognizer.listen(source, timeout=timeout)
                except sr.WaitTimeoutError:
                    print(f"{Fore.YELLOW}[TIMEOUT] No speech detected within {timeout} seconds.{Style.RESET_ALL}")
                    return None

            print(f"{Fore.BLUE}[PROCESSING] Processing audio...{Style.RESET_ALL}")

            # Save audio temporarily
            temp_file = Path.home() / ".cetri" / "temp_audio.wav"
            temp_file.parent.mkdir(exist_ok=True)

            try:
                with open(temp_file, 'wb') as f:
                    f.write(audio.get_wav_data())

                # Transcribe with Whisper
                if self.model:
                    result = self.model.transcribe(str(temp_file))
                    user_input = result['text'].strip()
                    confidence = result.get('confidence', 0.8)

                    if confidence < 0.5:
                        print(f"{Fore.YELLOW}[WARNING] Low confidence in speech recognition ({confidence:.2f}){Style.RESET_ALL}")

                    self.logger.log('info', f'Voice input: "{user_input}" (confidence: {confidence:.2f})')
                else:
                    print(f"{Fore.RED}[ERROR] Whisper model not available{Style.RESET_ALL}")
                    user_input = ""

            finally:
                # Clean up temp file
                if temp_file.exists():
                    temp_file.unlink()

            return user_input

        except sr.UnknownValueError:
            print(f"{Fore.YELLOW}[ERROR] Could not understand audio. Please try again.{Style.RESET_ALL}")
            return None
        except KeyboardInterrupt:
            print(f"{Fore.CYAN}[CANCELLED] Voice input cancelled.{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Voice recognition error: {e}{Style.RESET_ALL}")
            self.logger.log('error', f'Voice recognition error: {e}')
            return None

    def fuzzy_match(self, input_text, patterns, threshold=0.6):
        """Fuzzy string matching for command recognition"""
        if not self.config.get('commands.fuzzy_matching', True):
            return None

        input_lower = input_text.lower()
        best_match = None
        best_score = 0

        for pattern in patterns:
            # Exact match gets highest score
            if pattern.lower() in input_lower:
                return pattern

            # Fuzzy matching
            score = difflib.SequenceMatcher(None, input_lower, pattern.lower()).ratio()
            if score > best_score and score >= threshold:
                best_match = pattern
                best_score = score

        return best_match if best_score >= threshold else None

    def extract_intent(self, command):
        """Extract intent from natural language command"""
        command_lower = command.lower()

        # Check each command category
        for category, data in self.command_patterns.items():
            if 'patterns' in data:
                match = self.fuzzy_match(command, data['patterns'])
                if match:
                    return category, match

        # Check file operations
        if 'file_operations' in self.command_patterns:
            for operation, patterns in self.command_patterns['file_operations'].items():
                match = self.fuzzy_match(command, patterns)
                if match:
                    return f'file_{operation}', match

        return 'unknown', command

    def process_command(self, command):
        """Advanced command processing with natural language understanding"""
        if not command or not command.strip():
            return "I didn't catch that. Could you please repeat?"

        command = command.strip()
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now(),
            'intent': None,
            'response': None
        })

        # Extract intent
        intent, matched_pattern = self.extract_intent(command)
        self.command_history[-1]['intent'] = intent

        # Process based on intent
        response = self.handle_intent(intent, command, matched_pattern)
        self.command_history[-1]['response'] = response

        # Update conversation memory
        self.conversation_memory.append({
            'input': command,
            'intent': intent,
            'response': response,
            'timestamp': datetime.now()
        })

        # Keep memory limited
        if len(self.conversation_memory) > 50:
            self.conversation_memory = self.conversation_memory[-50:]

        return response

    def handle_intent(self, intent, command, matched_pattern):
        """Handle different intents"""
        try:
            if intent == 'greetings':
                responses = self.command_patterns['greetings']['responses']
                return random.choice(responses)

            elif intent == 'time':
                current_time = datetime.now().strftime("%I:%M %p")
                responses = self.command_patterns['time']['responses']
                return random.choice(responses).format(time=current_time)

            elif intent == 'date':
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                responses = self.command_patterns['date']['responses']
                return random.choice(responses).format(date=current_date)

            elif intent == 'help':
                return self.show_help_menu()

            elif intent == 'quit':
                responses = self.command_patterns['quit']['responses']
                return random.choice(responses)

            elif intent == 'file_create':
                return self.handle_file_create(command)

            elif intent == 'file_open':
                return self.handle_file_open(command)

            elif intent == 'file_list':
                return self.handle_file_list(command)

            elif intent == 'system_info':
                return self.handle_system_info()

            elif intent == 'calculations':
                return self.handle_calculation(command)

            else:
                # Try to understand the command better
                return self.handle_unknown_command(command)

        except Exception as e:
            self.logger.log('error', f'Error handling intent {intent}: {e}')
            return f"Sorry, I encountered an error processing your request: {e}"

    def handle_file_create(self, command):
        """Handle file creation commands"""
        try:
            # Extract filename from command
            filename_match = re.search(r'create\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?["\']?([^"\']+)["\']?', command, re.IGNORECASE)
            if filename_match:
                filename = filename_match.group(1).strip()
            else:
                filename = f"cetri_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            # Ensure safe filename
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            if not filename.endswith('.txt'):
                filename += '.txt'

            filepath = Path.cwd() / filename
            content = f"File created by CETRI AI Assistant on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"[OK] File '{filename}' created successfully at {filepath}"

        except Exception as e:
            return f"[ERROR] Error creating file: {e}"

    def handle_file_open(self, command):
        """Handle file opening commands"""
        try:
            if 'explorer' in command.lower() or 'folder' in command.lower():
                os.startfile('.')
                return "[OK] Opening file explorer..."
            else:
                # Try to open current directory
                os.startfile('.')
                return "[OK] Opening current directory..."

        except Exception as e:
            return f"[ERROR] Error opening file explorer: {e}"

    def handle_file_list(self, command):
        """Handle file listing commands"""
        try:
            files = list(Path.cwd().iterdir())
            if not files:
                return "[DIR] Current directory is empty."

            file_list = []
            for file in sorted(files)[:20]:  # Limit to 20 files
                if file.is_file():
                    size = file.stat().st_size
                    size_str = self.format_file_size(size)
                    file_list.append(f"[FILE] {file.name} ({size_str})")
                elif file.is_dir():
                    file_list.append(f"[DIR] {file.name}/")

            if len(files) > 20:
                file_list.append(f"... and {len(files) - 20} more items")

            return "[DIR] Current directory contents:\n" + "\n".join(file_list)

        except Exception as e:
            return f"❌ Error listing files: {e}"

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"

    def handle_system_info(self):
        """Handle system information requests"""
        try:
            info_lines = [
                f"🖥️  Operating System: {self.system_info['os']}",
                f"[CPU] CPU: {self.system_info['cpu']}",
                f"💾 Memory: {self.system_info['memory']}",
                f"🐍 Python: {self.system_info['python']}",
                f"⏰ Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}",
                f"📊 Commands Processed: {len(self.command_history)}"
            ]

            return "💻 System Information:\n" + "\n".join(info_lines)

        except Exception as e:
            return f"❌ Error getting system info: {e}"

    def handle_calculation(self, command):
        """Handle mathematical calculations"""
        try:
            # Extract mathematical expression
            expr_match = re.search(r'(?:calculate|compute|what is|what\'s)\s+(.+?)(?:\?|(?:\s+equals?)?$)', command, re.IGNORECASE)
            if not expr_match:
                return "❓ Please provide a mathematical expression to calculate."

            expr = expr_match.group(1).strip()

            # Basic security check - only allow safe operations
            if not re.match(r'^[0-9+\-*/().\s]+$', expr):
                return "❌ Sorry, I can only perform basic arithmetic calculations."

            # Evaluate expression safely
            result = eval(expr, {"__builtins__": {}}, {})

            return f"[RESULT] {expr} = {result}"

        except ZeroDivisionError:
            return "❌ Division by zero is not allowed."
        except Exception as e:
            return f"❌ Error in calculation: {e}"

    def handle_unknown_command(self, command):
        """Handle unknown commands with suggestions"""
        suggestions = []

        # Check for typos in known commands
        all_patterns = []
        for category, data in self.command_patterns.items():
            if 'patterns' in data:
                all_patterns.extend(data['patterns'])
            if category == 'file_operations':
                for op_patterns in data.values():
                    if isinstance(op_patterns, list):
                        all_patterns.extend(op_patterns)

        # Find close matches
        close_matches = difflib.get_close_matches(command.lower(), all_patterns, n=3, cutoff=0.4)
        if close_matches:
            suggestions = [f"📝 Did you mean: '{match}'?" for match in close_matches]

        response = f'❓ I\'m not sure how to handle: "{command}"'
        if suggestions:
            response += "\n" + "\n".join(suggestions)

        response += "\n💡 Try 'help' to see available commands."

        return response

    def show_help_menu(self):
        """Show comprehensive help menu"""
        help_text = f"""
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
{Fore.YELLOW}[HELP] CETRI AI ASSISTANT - HELP MENU{Style.RESET_ALL}
{Fore.CYAN}{'='*60}{Style.RESET_ALL}

{Fore.GREEN}[VOICE] VOICE COMMANDS:{Style.RESET_ALL}
• "Hello" or "Hi" - Greeting
• "What time is it?" - Current time
• "What's today's date?" - Current date
• "Create a file" - Create new file
• "Open file explorer" - Open file browser
• "List files" - Show directory contents
• "System info" - Show computer specs
• "Calculate 2 + 2" - Math calculations
• "Help" - Show this menu
• "Quit" or "Goodbye" - Exit CETRI

{Fore.BLUE}[KEYBOARD] TEXT COMMANDS:{Style.RESET_ALL}
• Type any command or press Enter for voice input
• Commands are case-insensitive
• Natural language supported (e.g., "tell me the time")

{Fore.MAGENTA}[FEATURES] FEATURES:{Style.RESET_ALL}
• Voice input/output with Whisper AI
• Fuzzy command matching
• Conversation memory
• Error recovery
• System monitoring
• File operations
• Mathematical calculations

{Fore.RED}[TROUBLESHOOTING] Help & Troubleshooting:{Style.RESET_ALL}
• If voice doesn't work: Check microphone permissions
• If TTS doesn't work: Voice settings may need adjustment
• For errors: Check logs in ~/.cetri/cetri.log

{Fore.CYAN}{'='*60}{Style.RESET_ALL}
        """
        print(help_text)
        return "Help menu displayed above. How can I assist you?"

    def show_main_menu(self):
        """Show main interaction menu"""
        print(f"\n{Fore.GREEN}[READY] CETRI Ready! Choose your input method:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}1. [VOICE] Voice Input (Press Enter)")
        print(f"2. [KEYBOARD] Text Input (Type command)")
        print(f"3. [HELP] Help (Type 'help')")
        print(f"4. [EXIT] Quit (Type 'quit'){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")

    def run(self):
        """Main CETRI loop with enhanced error handling"""
        try:
            while True:
                try:
                    print(f"\n{Fore.GREEN}CETRI>{Style.RESET_ALL} ", end="")
                    user_input = input().strip()

                    if not user_input:
                        # Voice mode
                        user_input = self.listen_once()

                    if user_input:
                        if user_input.lower() in ['quit', 'exit', 'shutdown', 'bye', 'goodbye']:
                            response = self.process_command(user_input)
                            print(f"\n{Fore.CYAN}CETRI: {response}{Style.RESET_ALL}")
                            self.speak(response)
                            break

                        print(f"\n{Fore.GREEN}You: {user_input}{Style.RESET_ALL}")
                        response = self.process_command(user_input)
                        print(f"{Fore.CYAN}CETRI: {response}{Style.RESET_ALL}")
                        self.speak(response)

                        # Update last command time
                        self.last_command_time = datetime.now()

                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}⚠️  Operation cancelled by user.{Style.RESET_ALL}")
                    continue
                except EOFError:
                    print(f"\n{Fore.YELLOW}⚠️  Input stream ended.{Style.RESET_ALL}")
                    break
                except Exception as e:
                    print(f"\n{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
                    self.logger.log('error', f'Unexpected error in main loop: {e}')
                    continue

        except Exception as e:
            print(f"\n{Fore.RED}💥 Critical error: {e}{Style.RESET_ALL}")
            self.logger.log('critical', f'Critical error in run loop: {e}')
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        print(f"\n{Fore.BLUE}[CLEANUP] Cleaning up CETRI resources...{Style.RESET_ALL}")

        # Save configuration if auto-save enabled
        if self.config.get('interface.auto_save', True):
            self.config.save_config()

        # Save command history
        try:
            history_file = Path.home() / ".cetri" / "history.json"
            history_file.parent.mkdir(exist_ok=True)

            with open(history_file, 'w') as f:
                # Convert datetime objects to strings for JSON
                history_data = []
                for item in self.command_history[-100:]:  # Keep last 100 commands
                    history_item = item.copy()
                    history_item['timestamp'] = item['timestamp'].isoformat()
                    history_data.append(history_item)

                json.dump(history_data, f, indent=2)

        except Exception as e:
            self.logger.log('error', f'Error saving command history: {e}')

        print(f"{Fore.GREEN}✅ CETRI shutdown complete.{Style.RESET_ALL}")

def main():
    """Main entry point with error handling"""
    try:
        cetri = CETRI()
        cetri.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 CETRI interrupted by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}💥 CETRI crashed: {e}{Style.RESET_ALL}")
        logging.critical(f'CETRI crashed: {e}', exc_info=True)
    finally:
        sys.exit(0)

if __name__ == '__main__':
    main()
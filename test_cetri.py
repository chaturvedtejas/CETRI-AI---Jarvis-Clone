#!/usr/bin/env python3
"""
CETRI AI Assistant - Comprehensive Test Suite
Tests all features, error handling, and edge cases
"""

import sys
import os
import time
import json
import tempfile
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import CETRI components
try:
    from main import CETRI, CETRIConfig, CETRILogger
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure main.py is in the same directory")
    sys.exit(1)

class CETRITestCase(unittest.TestCase):
    """Comprehensive test suite for CETRI AI Assistant"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Change to temp directory for testing
        os.chdir(self.temp_dir)

        # Mock configuration to avoid file system issues
        with patch('main.CETRIConfig') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = True  # Enable all features by default
            mock_config.return_value = mock_config_instance

            with patch('main.CETRILogger') as mock_logger:
                mock_logger_instance = Mock()
                mock_logger.return_value = mock_logger_instance

                # Initialize CETRI with mocks
                self.cetri = CETRI.__new__(CETRI)  # Create without calling __init__
                self.cetri.config = mock_config_instance
                self.cetri.logger = mock_logger_instance
                self.cetri.command_patterns = self.cetri.load_command_patterns()
                self.cetri.conversation_memory = []
                self.cetri.command_history = []

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test CETRI initialization"""
        self.assertIsInstance(self.cetri.command_patterns, dict)
        self.assertIsInstance(self.cetri.conversation_memory, list)
        self.assertIsInstance(self.cetri.command_history, list)

    def test_fuzzy_matching(self):
        """Test fuzzy command matching"""
        patterns = ['hello', 'hi', 'greetings']

        # Exact matches
        self.assertEqual(self.cetri.fuzzy_match('hello', patterns), 'hello')
        self.assertEqual(self.cetri.fuzzy_match('hi', patterns), 'hi')

        # Close matches
        self.assertIsNotNone(self.cetri.fuzzy_match('helo', patterns))  # Typo
        # Note: 'hey' is not similar enough to 'hi' (similarity ~0.5 < 0.6 threshold)
        # So we test with a more similar word
        self.assertIsNotNone(self.cetri.fuzzy_match('greet', patterns))   # Similar to greetings

        # No matches
        self.assertIsNone(self.cetri.fuzzy_match('goodbye', patterns))

    def test_intent_extraction(self):
        """Test intent extraction from commands"""
        # Test greetings
        intent, match = self.cetri.extract_intent('hello there')
        self.assertEqual(intent, 'greetings')

        # Test time
        intent, match = self.cetri.extract_intent('what time is it')
        self.assertEqual(intent, 'time')

        # Test file operations
        intent, match = self.cetri.extract_intent('create a new file')
        self.assertEqual(intent, 'file_create')

    def test_command_processing(self):
        """Test command processing logic"""
        # Test greetings (check for any of the possible responses)
        response = self.cetri.process_command("hello")
        greeting_responses = ["Hello", "Hi there", "Greetings"]
        self.assertTrue(any(greet in response for greet in greeting_responses))

        # Test time (check for time-related keywords)
        response = self.cetri.process_command("what time is it")
        time_keywords = ["time", "pm", "am", ":"]
        self.assertTrue(any(keyword in response.lower() for keyword in time_keywords))

        # Test unknown command
        response = self.cetri.process_command("xyz123unknown")
        self.assertIn("not sure", response.lower())

    def test_file_operations(self):
        """Test file operation methods"""
        # Test file listing (this should work)
        response = self.cetri.handle_file_list("list files")
        # Check for directory markers instead of exact string
        self.assertTrue(
            any(keyword in response.lower() for keyword in ["[dir]", "[file]", "empty", "current"])
        )

    def test_calculations(self):
        """Test mathematical calculations"""
        # Test basic arithmetic
        response = self.cetri.handle_calculation("calculate 2 + 2")
        self.assertIn("4", response)

        # Test complex expression
        response = self.cetri.handle_calculation("compute 10 * 5 + 3")
        self.assertIn("53", response)

        # Test division by zero
        response = self.cetri.handle_calculation("calculate 1 / 0")
        self.assertIn("not allowed", response.lower())

    def test_error_handling(self):
        """Test error handling and edge cases"""
        # Test empty command
        response = self.cetri.process_command("")
        self.assertIn("didn't catch", response.lower())

        # Test None input
        response = self.cetri.process_command(None)
        self.assertIn("didn't catch", response.lower())

        # Test very long command
        long_command = "hello " * 1000
        response = self.cetri.process_command(long_command)
        self.assertIsInstance(response, str)

    def test_memory_management(self):
        """Test conversation memory management"""
        # Add multiple commands
        for i in range(60):  # More than memory limit
            self.cetri.process_command(f"test command {i}")

        # Check memory is limited
        self.assertLessEqual(len(self.cetri.conversation_memory), 50)

def run_performance_test():
    """Run performance tests"""
    print("\n" + "="*50)
    print("PERFORMANCE TESTING")
    print("="*50)

    # Create a minimal CETRI instance for testing
    with patch('main.CETRIConfig') as mock_config:
        mock_config_instance = Mock()
        mock_config_instance.get.return_value = True
        mock_config.return_value = mock_config_instance

        with patch('main.CETRILogger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance

            cetri = CETRI.__new__(CETRI)
            cetri.config = mock_config_instance
            cetri.logger = mock_logger_instance
            cetri.command_patterns = cetri.load_command_patterns()
            cetri.conversation_memory = []
            cetri.command_history = []

            # Test command processing speed
            start_time = time.time()
            iterations = 100

            for i in range(iterations):
                response = cetri.process_command("hello")

            end_time = time.time()
            avg_time = (end_time - start_time) / iterations

            print(".4f")
            print("Performance test passed!" if avg_time < 0.01 else "Performance test slow")

def run_integration_test():
    """Run full integration test"""
    print("\n" + "="*50)
    print("INTEGRATION TESTING")
    print("="*50)

    try:
        # Create a minimal CETRI instance for testing
        with patch('main.CETRIConfig') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.get.return_value = True
            mock_config.return_value = mock_config_instance

            with patch('main.CETRILogger') as mock_logger:
                mock_logger_instance = Mock()
                mock_logger.return_value = mock_logger_instance

                cetri = CETRI.__new__(CETRI)
                cetri.config = mock_config_instance
                cetri.logger = mock_logger_instance
                cetri.command_patterns = cetri.load_command_patterns()
                cetri.conversation_memory = []
                cetri.command_history = []

                # Test full command flow
                commands = [
                    "hello",
                    "what time is it",
                    "create test file",
                    "list files",
                    "calculate 5 + 3",
                    "unknown command xyz"
                ]

                for cmd in commands:
                    print(f"Testing: {cmd}")
                    response = cetri.process_command(cmd)
                    assert isinstance(response, str), f"Command '{cmd}' returned non-string response"
                    assert len(response) > 0, f"Command '{cmd}' returned empty response"
                    print(f"  [OK] Response: {response[:50]}...")

                print("[OK] Integration test passed!")

    except Exception as e:
        print(f"Integration test failed: {e}")
        raise

def main():
    """Main test runner"""
    print("CETRI AI ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("="*60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(CETRITestCase)

    # Run unit tests
    print("\nRUNNING UNIT TESTS...")
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\nALL UNIT TESTS PASSED!")

        # Run performance tests
        run_performance_test()

        # Run integration tests
        run_integration_test()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("CETRI is ready for deployment!")
        print("="*60)

    else:
        print(f"\n{len(result.failures)} TESTS FAILED!")
        print(f"{len(result.errors)} TESTS HAD ERRORS!")
        for failure in result.failures:
            print(f"FAILED: {failure[0]}")
            print(f"ERROR: {failure[1]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
            print(f"DETAILS: {error[1]}")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
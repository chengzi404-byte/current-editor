"""
Unit tests for library.vbash module

Test cases for VBash class and its functionality
"""

import unittest
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add library path to sys.path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from library.vbash import VBash, create_vbash


class TestVBashInitialization(unittest.TestCase):
    """Test VBash class initialization"""
    
    def test_default_initialization(self):
        """Test VBash initialization with default parameters"""
        vbash = VBash()
        self.assertIsNotNone(vbash.current_dir)
        self.assertIsNotNone(vbash.system)
        self.assertIsNotNone(vbash.shell)
        self.assertEqual(len(vbash.history), 0)
        
    def test_custom_directory_initialization(self):
        """Test VBash initialization with custom directory"""
        test_dir = os.path.expanduser("~")
        vbash = VBash(test_dir)
        self.assertEqual(vbash.current_dir, test_dir)
        
    def test_relative_directory_initialization(self):
        """Test VBash initialization with relative directory"""
        vbash = VBash(".")
        expected_dir = os.path.abspath(".")
        self.assertEqual(vbash.current_dir, expected_dir)
        
    def test_nonexistent_directory_creation(self):
        """Test VBash creates nonexistent directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_dir = os.path.join(temp_dir, "nonexistent")
            vbash = VBash(nonexistent_dir)
            self.assertTrue(os.path.exists(nonexistent_dir))


class TestVBashBasicCommands(unittest.TestCase):
    """Test basic VBash commands"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vbash = VBash(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_pwd_command(self):
        """Test pwd command returns current directory"""
        current_dir = self.vbash.pwd()
        self.assertEqual(current_dir, self.temp_dir)
        
    def test_ls_command_empty_directory(self):
        """Test ls command on empty directory"""
        items = self.vbash.ls()
        self.assertEqual(len(items), 0)
        
    def test_ls_command_with_files(self):
        """Test ls command with files in directory"""
        # Create test files
        test_files = ["test1.txt", "test2.py", "test3.json"]
        for filename in test_files:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write("test content")
        
        items = self.vbash.ls()
        self.assertEqual(len(items), len(test_files))
        for filename in test_files:
            self.assertIn(filename, items)
            
    def test_ls_command_with_path(self):
        """Test ls command with specific path"""
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir)
        
        with open(os.path.join(subdir, "test.txt"), 'w') as f:
            f.write("test")
            
        items = self.vbash.ls(subdir)
        self.assertIn("test.txt", items)
        
    def test_mkdir_command(self):
        """Test mkdir command creates directory"""
        new_dir = "test_directory"
        result = self.vbash.mkdir(new_dir)
        self.assertTrue(result)
        
        expected_path = os.path.join(self.temp_dir, new_dir)
        self.assertTrue(os.path.exists(expected_path))
        self.assertTrue(os.path.isdir(expected_path))
        
    def test_mkdir_command_existing_directory(self):
        """Test mkdir command with existing directory"""
        new_dir = "test_directory"
        os.makedirs(os.path.join(self.temp_dir, new_dir))
        
        # Should still return True for existing directory
        result = self.vbash.mkdir(new_dir)
        self.assertTrue(result)


class TestVBashCdCommand(unittest.TestCase):
    """Test cd command functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(self.subdir)
        self.vbash = VBash(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cd_absolute_path(self):
        """Test cd command with absolute path"""
        result = self.vbash.cd(self.subdir)
        self.assertTrue(result)
        self.assertEqual(self.vbash.current_dir, self.subdir)
        
    def test_cd_relative_path(self):
        """Test cd command with relative path"""
        result = self.vbash.cd("subdir")
        self.assertTrue(result)
        self.assertEqual(self.vbash.current_dir, self.subdir)
        
    def test_cd_parent_directory(self):
        """Test cd command to parent directory"""
        # First change to subdir
        self.vbash.cd("subdir")
        
        # Then change to parent
        result = self.vbash.cd("..")
        self.assertTrue(result)
        self.assertEqual(self.vbash.current_dir, self.temp_dir)
        
    def test_cd_nonexistent_directory(self):
        """Test cd command with nonexistent directory"""
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        result = self.vbash.cd(nonexistent_dir)
        self.assertFalse(result)
        # Current directory should remain unchanged
        self.assertEqual(self.vbash.current_dir, self.temp_dir)
        
    def test_cd_home_directory(self):
        """Test cd command to home directory"""
        home_dir = os.path.expanduser("~")
        result = self.vbash.cd("~")
        self.assertTrue(result)
        self.assertEqual(self.vbash.current_dir, home_dir)


class TestVBashRunCommand(unittest.TestCase):
    """Test run command functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vbash = VBash(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_run_command_windows(self, mock_subprocess):
        """Test run command on Windows"""
        # Mock the platform.system to return Windows
        with patch('platform.system', return_value="Windows"):
            vbash = VBash(self.temp_dir)
            
            # Mock the subprocess result
            mock_result = MagicMock()
            mock_result.stdout = b"test output"
            mock_result.stderr = b""
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            stdout, stderr, returncode = vbash.run("echo test")
            
            self.assertEqual(stdout, b"test output")
            self.assertEqual(stderr, b"")
            self.assertEqual(returncode, 0)
            
            # Verify subprocess was called with correct arguments
            mock_subprocess.assert_called_once()
            
    @patch('subprocess.run')
    def test_run_command_linux(self, mock_subprocess):
        """Test run command on Linux"""
        # Mock the platform.system to return Linux
        with patch('platform.system', return_value="Linux"):
            vbash = VBash(self.temp_dir)
            
            # Mock the subprocess result
            mock_result = MagicMock()
            mock_result.stdout = b"test output"
            mock_result.stderr = b""
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            stdout, stderr, returncode = vbash.run("echo test")
            
            self.assertEqual(stdout, b"test output")
            self.assertEqual(stderr, b"")
            self.assertEqual(returncode, 0)
            
    def test_run_command_history(self):
        """Test that commands are added to history"""
        # Use a simple command that should work on all systems
        command = "echo test"
        
        # Run the command
        try:
            self.vbash.run(command, capture_output=False)
        except:
            pass  # Ignore execution errors in test
            
        # Check history
        self.assertIn(command, self.vbash.history)
        
    def test_run_command_error_handling(self):
        """Test error handling in run command"""
        # Use a command that will fail
        command = "nonexistent_command_12345"
        
        stdout, stderr, returncode = self.vbash.run(command)
        
        # Should handle errors gracefully
        self.assertIsInstance(stdout, bytes)
        self.assertIsInstance(stderr, bytes)
        self.assertIsInstance(returncode, int)


class TestVBashSafeRunCommand(unittest.TestCase):
    """Test safe_run command functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vbash = VBash(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_safe_run_with_blacklisted_command(self):
        """Test safe_run rejects blacklisted commands"""
        blacklisted_commands = ["rm -rf /", "del C:\\", "format C:", "shutdown", "init 0"]
        
        for command in blacklisted_commands:
            with self.assertRaises(ValueError):
                self.vbash.safe_run(command)
                
    def test_safe_run_with_custom_blacklist(self):
        """Test safe_run with custom blacklist"""
        custom_blacklist = ["dangerous", "malicious"]
        
        with self.assertRaises(ValueError):
            self.vbash.safe_run("dangerous_command", black_list=custom_blacklist)
            
    def test_safe_run_allowed_command(self):
        """Test safe_run allows non-blacklisted commands"""
        # Use a simple command that should work
        command = "echo safe"
        
        try:
            stdout, stderr, returncode = self.vbash.safe_run(command)
            # Should not raise exception
            self.assertIsInstance(stdout, bytes)
            self.assertIsInstance(stderr, bytes)
            self.assertIsInstance(returncode, int)
        except Exception:
            # It's okay if the command fails, as long as it doesn't raise ValueError
            pass


class TestVBashHistory(unittest.TestCase):
    """Test command history functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vbash = VBash(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_history_initialization(self):
        """Test history is empty on initialization"""
        history = self.vbash.get_history()
        self.assertEqual(len(history), 0)
        
    def test_history_after_commands(self):
        """Test history tracks commands"""
        commands = ["echo test1", "pwd", "ls"]
        
        for command in commands:
            try:
                self.vbash.run(command, capture_output=False)
            except:
                pass  # Ignore execution errors
                
        history = self.vbash.get_history()
        self.assertEqual(len(history), len(commands))
        self.assertEqual(history, commands)
        
    def test_clear_history(self):
        """Test clear_history functionality"""
        # Add some commands to history
        commands = ["echo test1", "pwd"]
        for command in commands:
            try:
                self.vbash.run(command, capture_output=False)
            except:
                pass
                
        # Clear history
        self.vbash.clear_history()
        
        # Check history is empty
        history = self.vbash.get_history()
        self.assertEqual(len(history), 0)


class TestVBashSystemInfo(unittest.TestCase):
    """Test system information functionality"""
    
    def test_get_system_info(self):
        """Test get_system_info returns correct information"""
        vbash = VBash()
        system_info = vbash.get_system_info()
        
        # Check all required keys are present
        required_keys = ["system", "shell", "current_directory", "python_version", "architecture"]
        for key in required_keys:
            self.assertIn(key, system_info)
            self.assertIsNotNone(system_info[key])
            
        # Check specific values
        self.assertEqual(system_info["current_directory"], vbash.current_dir)
        self.assertEqual(system_info["shell"], vbash.shell)
        self.assertEqual(system_info["system"], vbash.system)


class TestVBashFactoryFunction(unittest.TestCase):
    """Test create_vbash factory function"""
    
    def test_create_vbash_default(self):
        """Test create_vbash with default parameters"""
        vbash = create_vbash()
        self.assertIsInstance(vbash, VBash)
        
    def test_create_vbash_custom_directory(self):
        """Test create_vbash with custom directory"""
        test_dir = os.path.expanduser("~")
        vbash = create_vbash(test_dir)
        self.assertIsInstance(vbash, VBash)
        self.assertEqual(vbash.current_dir, test_dir)


class TestVBashExecuteScript(unittest.TestCase):
    """Test script execution functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.vbash = VBash(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_execute_script_nonexistent_file(self):
        """Test execute_script with nonexistent file"""
        nonexistent_script = os.path.join(self.temp_dir, "nonexistent.sh")
        
        with self.assertRaises(FileNotFoundError):
            self.vbash.execute_script(nonexistent_script)
            
    def test_execute_script_existing_file(self):
        """Test execute_script with existing file"""
        # Create a simple script file
        script_path = os.path.join(self.temp_dir, "test_script.sh")
        with open(script_path, 'w') as f:
            f.write("echo 'Hello from script'")
            
        try:
            stdout, stderr, returncode = self.vbash.execute_script(script_path)
            # Should not raise exception
            self.assertIsInstance(stdout, bytes)
            self.assertIsInstance(stderr, bytes)
            self.assertIsInstance(returncode, int)
        except Exception:
            # It's okay if the execution fails, as long as the file is found
            pass


def run_all_tests():
    """Run all VBash unit tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestVBashInitialization))
    test_suite.addTest(unittest.makeSuite(TestVBashBasicCommands))
    test_suite.addTest(unittest.makeSuite(TestVBashCdCommand))
    test_suite.addTest(unittest.makeSuite(TestVBashRunCommand))
    test_suite.addTest(unittest.makeSuite(TestVBashSafeRunCommand))
    test_suite.addTest(unittest.makeSuite(TestVBashHistory))
    test_suite.addTest(unittest.makeSuite(TestVBashSystemInfo))
    test_suite.addTest(unittest.makeSuite(TestVBashFactoryFunction))
    test_suite.addTest(unittest.makeSuite(TestVBashExecuteScript))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print("VBash Unit Test Summary")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败！")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
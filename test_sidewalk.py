import unittest
from unittest.mock import patch
from io import StringIO
import os
import json
import shutil
from sidewalk import Sidewalk, CommandBase

class TestSidewalk(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(__file__)
        self.commands_dir = os.path.join(self.test_dir, "commands")
        self.logs_dir = os.path.join(self.test_dir, "logs")
        self.manifest_path = os.path.join(self.test_dir, "manifest.json")

        # Clean up previous runs
        if os.path.exists(self.commands_dir):
            shutil.rmtree(self.commands_dir)
        if os.path.exists(self.logs_dir):
            shutil.rmtree(self.logs_dir)
        if os.path.exists(self.manifest_path):
            os.remove(self.manifest_path)

        os.makedirs(self.commands_dir, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump({"commands": {}}, f)

    def tearDown(self):
        if os.path.exists(self.commands_dir):
            shutil.rmtree(self.commands_dir)
        if os.path.exists(self.logs_dir):
            shutil.rmtree(self.logs_dir)
        if os.path.exists(self.manifest_path):
            os.remove(self.manifest_path)

    def test_register_command_with_corrupted_manifest(self):
        """
        Test that register_command() handles a corrupted manifest.json gracefully.
        """
        # Create a corrupted manifest file
        with open(self.manifest_path, "w") as f:
            f.write("invalid json")

        # Create a dummy command file
        command_file_path = os.path.join(self.commands_dir, "test_command.py")
        with open(command_file_path, "w") as f:
            f.write("""
class TestCommand(CommandBase):
    def short_help(self): return "test command"
    def help(self): return "test command help"
    def execute(self, args): return 0
""")

        sidewalk = Sidewalk()
        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.assertTrue(sidewalk.register_command("test", "test_command.py"))

if __name__ == "__main__":
    unittest.main()

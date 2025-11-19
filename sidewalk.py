#!/usr/bin/env python3
"""
Sidewalk CLI - A pluggable command-line interface framework
"""

import sys
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Type


class CommandBase:
    """Base class that all commands must inherit from"""

    def short_help(self) -> str:
        """Return a brief one-line description of this command"""
        raise NotImplementedError("Command must implement short_help() method")

    def help(self) -> str:
        """Return detailed help message for this command"""
        raise NotImplementedError("Command must implement help() method")

    def execute(self, args: list) -> int:
        """Execute the command with given arguments"""
        raise NotImplementedError("Command must implement execute() method")


class Sidewalk:
    """Main Sidewalk CLI manager"""

    MANIFEST_FILE = "manifest.json"
    COMMANDS_DIR = "commands"
    LOGS_DIR = "logs"

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.commands_dir = self.base_dir / self.COMMANDS_DIR
        self.logs_dir = self.base_dir / self.LOGS_DIR
        self.manifest_path = self.base_dir / self.MANIFEST_FILE

        # Create necessary directories
        self.commands_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # Setup central logging
        self._setup_logging()

        # Load registered commands
        self.commands: Dict[str, Type[CommandBase]] = {}
        self._load_commands()

    def _setup_logging(self):
        """Setup centralized logging system"""
        main_log = self.logs_dir / "sidewalk.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(main_log),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger("Sidewalk")
        self.logger.info("Sidewalk initialized")

    def get_command_logger(self, command_name: str) -> logging.Logger:
        """Get or create a logger for a specific command"""
        logger = logging.getLogger(f"Command.{command_name}")

        if not logger.handlers:
            log_file = self.logs_dir / f"{command_name}.log"
            handler = logging.FileHandler(log_file)
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def _load_commands(self):
        """Load all registered commands from manifest"""
        if not self.manifest_path.exists():
            self.logger.warning("Manifest file not found. No commands registered.")
            self._create_empty_manifest()
            return

        try:
            with open(self.manifest_path, 'r') as f:
                manifest = json.load(f)

            for cmd_name, cmd_file in manifest.get("commands", {}).items():
                self._load_command(cmd_name, cmd_file)

        except json.JSONDecodeError:
            self.logger.error("Invalid manifest file format")
            self._create_empty_manifest()

    def _create_empty_manifest(self):
        """Create an empty manifest file"""
        with open(self.manifest_path, 'w') as f:
            json.dump({"commands": {}}, f, indent=2)

    def _load_command(self, cmd_name: str, cmd_file: str):
        """Dynamically load a command from a Python file"""
        cmd_path = self.commands_dir / cmd_file

        if not cmd_path.exists():
            self.logger.error(f"Command file not found: {cmd_path}")
            return

        try:
            spec = importlib.util.spec_from_file_location(cmd_name, cmd_path)
            module = importlib.util.module_from_spec(spec)
            module.CommandBase = CommandBase
            spec.loader.exec_module(module)

            # Find command class
            cmd_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, CommandBase) and
                    attr is not CommandBase):
                    cmd_class = attr
                    break

            if cmd_class is None:
                self.logger.error(f"No CommandBase subclass found in {cmd_file}")
                return

            # Verify required methods
            if not hasattr(cmd_class, 'short_help') or not hasattr(cmd_class, 'help') or not hasattr(cmd_class, 'execute'):
                self.logger.error(f"Command {cmd_name} missing required methods")
                return

            self.commands[cmd_name] = cmd_class
            self.logger.info(f"Loaded command: {cmd_name}")

        except Exception as e:
            self.logger.error(f"Failed to load command {cmd_name}: {e}")

    def register_command(self, cmd_name: str, cmd_file: str) -> bool:
        """Register a new command in the manifest"""
        cmd_path = self.commands_dir / cmd_file

        if not cmd_path.exists():
            self.logger.error(f"Command file not found: {cmd_path}")
            print(f"Error: Command file '{cmd_file}' not found in commands directory")
            return False

        try:
            spec = importlib.util.spec_from_file_location(cmd_name, cmd_path)
            module = importlib.util.module_from_spec(spec)
            module.CommandBase = CommandBase
            spec.loader.exec_module(module)

            # Find command class
            cmd_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, CommandBase) and
                    attr is not CommandBase):
                    cmd_class = attr
                    break

            if cmd_class is None:
                print(f"Error: No CommandBase subclass found in {cmd_file}")
                return False

            # Verify required methods
            if not callable(getattr(cmd_class, 'short_help', None)):
                print(f"Error: Command missing 'short_help()' method")
                return False

            if not callable(getattr(cmd_class, 'help', None)):
                print(f"Error: Command missing 'help()' method")
                return False

            if not callable(getattr(cmd_class, 'execute', None)):
                print(f"Error: Command missing 'execute()' method")
                return False

        except Exception as e:
            print(f"Error: Failed to validate command: {e}")
            return False

        # Update manifest
        try:
            manifest = {"commands": {}}
            if self.manifest_path.exists():
                with open(self.manifest_path, 'r') as f:
                    manifest = json.load(f)

            manifest["commands"][cmd_name] = cmd_file

            with open(self.manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            self.logger.info(f"Registered command: {cmd_name}")
            print(f"Successfully registered command '{cmd_name}'")

            self._load_command(cmd_name, cmd_file)

            return True

        except Exception as e:
            self.logger.error(f"Failed to register command: {e}")
            print(f"Error: Failed to update manifest: {e}")
            return False

    def show_help(self):
        """Display Sidewalk help and list of available commands"""
        help_text = """
Sidewalk CLI - A pluggable command-line interface framework

Usage: sidewalk <command> [parameters]
       sidewalk --help | -h

Options:
  --help, -h    Show this help message

Available Commands:
"""
        print(help_text)

        if not self.commands:
            print("  No commands registered yet.")
            print("\nTo register a command:")
            print("  sidewalk register <command_name> <command_file.py>")
        else:
            max_cmd_length = max(len(cmd_name) for cmd_name in self.commands.keys())

            for cmd_name in sorted(self.commands.keys()):
                try:
                    cmd_instance = self.commands[cmd_name]()
                    short_desc = cmd_instance.short_help()
                    print(f"  {cmd_name:<{max_cmd_length}}    {short_desc}")
                except Exception:
                    print(f"  {cmd_name:<{max_cmd_length}}    (description unavailable)")

            print("\nFor command-specific help:")
            print("  sidewalk <command> --help")

    def run(self, args: list):
        """Main entry point for Sidewalk"""
        if len(args) == 0 or args[0] in ['--help', '-h']:
            self.show_help()
            return 0

        cmd_name = args[0]
        cmd_args = args[1:]

        # Check for help flag
        if cmd_args and cmd_args[0] in ['--help', '-h']:
            if cmd_name in self.commands:
                cmd_instance = self.commands[cmd_name]()
                print(f"\nCommand: {cmd_name}")
                print(cmd_instance.help())
                return 0
            else:
                print(f"Error: Unknown command '{cmd_name}'")
                print("Run 'sidewalk --help' to see available commands")
                return 1

        # Built-in register command
        if cmd_name == "register":
            if len(cmd_args) < 2:
                print("Usage: sidewalk register <command_name> <command_file.py>")
                print("Example: sidewalk register hello hello.py")
                return 1

            return 0 if self.register_command(cmd_args[0], cmd_args[1]) else 1

        # Execute registered command
        if cmd_name in self.commands:
            try:
                cmd_class = self.commands[cmd_name]
                cmd_instance = cmd_class()

                if hasattr(cmd_instance, 'set_sidewalk'):
                    cmd_instance.set_sidewalk(self)

                self.logger.info(f"Executing command: {cmd_name}")
                return cmd_instance.execute(cmd_args)

            except Exception as e:
                self.logger.error(f"Command execution failed: {e}")
                print(f"Error: Command execution failed: {e}")
                return 1
        else:
            print(f"Error: Unknown command '{cmd_name}'")
            print("Run 'sidewalk --help' to see available commands")
            return 1


def main():
    """Entry point for the CLI"""
    sidewalk = Sidewalk()
    exit_code = sidewalk.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

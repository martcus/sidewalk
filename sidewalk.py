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

import click


class CommandBase:
    """Base class that all commands must inherit from"""

    def get_click_command(self) -> click.Command:
        """Return a configured click.Command for this command"""
        raise NotImplementedError("Command must implement get_click_command() method")


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

        self.commands_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        self._setup_logging()

        self.commands: Dict[str, Type[CommandBase]] = {}
        self._load_commands()

    def _setup_logging(self):
        """Setup centralized logging to file only"""
        main_log = self.logs_dir / "sidewalk.log"
        self.logger = logging.getLogger("Sidewalk")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(main_log)
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)
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

    def _create_empty_manifest(self):
        """Create an empty manifest file"""
        with open(self.manifest_path, 'w') as f:
            json.dump({"commands": {}}, f, indent=2)

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

            if not callable(getattr(cmd_class, 'get_click_command', None)):
                self.logger.error(f"Command {cmd_name} missing get_click_command() method")
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
            click.echo(f"Error: Command file '{cmd_file}' not found in commands directory", err=True)
            return False

        try:
            spec = importlib.util.spec_from_file_location(cmd_name, cmd_path)
            module = importlib.util.module_from_spec(spec)
            module.CommandBase = CommandBase
            spec.loader.exec_module(module)

            cmd_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                        issubclass(attr, CommandBase) and
                        attr is not CommandBase):
                    cmd_class = attr
                    break

            if cmd_class is None:
                click.echo(f"Error: No CommandBase subclass found in {cmd_file}", err=True)
                return False

            if not callable(getattr(cmd_class, 'get_click_command', None)):
                click.echo("Error: Command missing 'get_click_command()' method", err=True)
                return False

        except Exception as e:
            click.echo(f"Error: Failed to validate command: {e}", err=True)
            return False

        try:
            manifest = {"commands": {}}
            if self.manifest_path.exists():
                with open(self.manifest_path, 'r') as f:
                    manifest = json.load(f)

            manifest["commands"][cmd_name] = cmd_file
            with open(self.manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            self.logger.info(f"Registered command: {cmd_name}")
            click.echo(f"Successfully registered command '{cmd_name}'")
            self._load_command(cmd_name, cmd_file)
            return True

        except Exception as e:
            self.logger.error(f"Failed to register command: {e}")
            click.echo(f"Error: Failed to update manifest: {e}", err=True)
            return False

    def build_cli(self) -> click.Group:
        """Build and return the Click CLI group with all registered commands"""
        sidewalk_ref = self

        @click.group()
        def cli():
            """Sidewalk CLI - A pluggable command-line interface framework"""
            pass

        @cli.command()
        @click.argument('cmd_name')
        @click.argument('cmd_file')
        def register(cmd_name, cmd_file):
            """Register a new command in the manifest"""
            success = sidewalk_ref.register_command(cmd_name, cmd_file)
            if not success:
                raise click.exceptions.Exit(1)

        for cmd_name, cmd_class in self.commands.items():
            cmd_instance = cmd_class()
            if hasattr(cmd_instance, 'set_sidewalk'):
                cmd_instance.set_sidewalk(sidewalk_ref)
            cli.add_command(cmd_instance.get_click_command(), name=cmd_name)

        return cli


def main():
    """Entry point for the CLI"""
    sidewalk = Sidewalk()
    cli = sidewalk.build_cli()
    cli()


if __name__ == "__main__":
    main()

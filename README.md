# Sidewalk - Pluggable Command Framework

A Python-based CLI framework with pluggable command architecture, built on [Click](https://click.palletsprojects.com/).

## Project Structure

```
sidewalk/
├── sidewalk.py          # Main CLI framework
├── manifest.json        # Command registry (auto-generated)
├── commands/            # Directory for command modules
│   └── hello.py        # Example command
└── logs/               # Log files (auto-generated)
    ├── sidewalk.log     # Central sidewalk log
    └── hello.log        # Command-specific logs
```

## Installation

1. (Recommended) Create and activate a virtual environment:
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify the installation:
```bash
python sidewalk.py --help
```

## Usage

### Show Help
```bash
python sidewalk.py --help
```

Output example:
```
Usage: sidewalk.py [OPTIONS] COMMAND [ARGS]...

  Sidewalk CLI - A pluggable command-line interface framework

Options:
  --help  Show this message and exit.

Commands:
  hello     Prints a greeting message
  register  Register a new command in the manifest
```

### Register a Command
```bash
python sidewalk.py register hello hello.py
```

This will:
- Validate the command file exists in `commands/` directory
- Verify the command implements `get_click_command()`
- Add it to `manifest.json`
- Make it available for execution

### Execute a Command
```bash
# Basic usage
python sidewalk.py hello
# Output: Hello, World!

# With short flag
python sidewalk.py hello -n Alice
# Output: Hello, Alice!

# With long flag
python sidewalk.py hello --name Bob
# Output: Hello, Bob!

# Multiple flags
python sidewalk.py hello -n Charlie -u
# Output: HELLO, CHARLIE!

# With count
python sidewalk.py hello --name Diana --count 3
# Output:
# Hello, Diana!
# Hello, Diana!
# Hello, Diana!
```

### Get Command-Specific Help
```bash
python sidewalk.py hello --help
```

Output:
```
Usage: sidewalk.py hello [OPTIONS]

  Prints a greeting message

Options:
  -n, --name TEXT        Name to greet  [default: World]
  -u, --uppercase        Display greeting in uppercase
  -c, --count INTEGER RANGE
                         Number of times to repeat the greeting  [default: 1;
                         x>=1]
  --help                 Show this message and exit.
```

## Creating a New Command

1. Create a new Python file in the `commands/` directory
2. Inherit from `CommandBase` (injected automatically by sidewalk — do NOT import it)
3. Import `click` directly in your command file
4. Implement `get_click_command()` returning a `click.Command`
5. Register the command using sidewalk

### Example Command Template

```python
"""
MyCommand - Description of what this command does

CommandBase will be injected at runtime by sidewalk.
Do not import anything from sidewalk.
"""

import click


class MyCommand(CommandBase):

    def __init__(self):
        self.sidewalk = None
        self.logger = None

    def set_sidewalk(self, sidewalk):
        """Set sidewalk instance for accessing logging"""
        self.sidewalk = sidewalk
        self.logger = sidewalk.get_command_logger("mycommand")

    def get_click_command(self) -> click.Command:
        instance = self

        @click.command(help="Brief description of what this command does")
        @click.option('-f', '--flag', default='default_value', show_default=True,
                      help='Description of flag')
        @click.option('-v', '--verbose', is_flag=True,
                      help='Enable verbose mode')
        def mycommand(flag, verbose):
            if instance.logger:
                instance.logger.info("MyCommand started")

            # Your command logic here
            click.echo("Command executed successfully!")

            if instance.logger:
                instance.logger.info("MyCommand completed")

        return mycommand
```

### Register Your New Command

```bash
python sidewalk.py register mycommand mycommand.py
```

## Features

### Pluggable Architecture
- Add new commands without modifying core code
- Commands are loaded dynamically from the manifest
- Each command is a separate Python module
- `CommandBase` and `click` are the only tools needed in a command file

### Centralized Logging
- Main sidewalk log: `logs/sidewalk.log`
- Command-specific logs: `logs/<command_name>.log`
- Logging writes to file only — stdout is reserved for Click output

### Command Validation
- Automatic verification that `get_click_command()` is implemented
- Runtime validation when registering new commands

### Built-in Help System
Provided entirely by Click:
- `sidewalk --help` — lists all commands with brief descriptions
- `sidewalk <command> --help` — shows full option list for a command

### Command Registry
- Commands stored in `manifest.json`
- Simple JSON format, version-controllable
- Auto-created if missing

## Command Requirements

Every command must:
1. Be a Python file in the `commands/` directory
2. Contain a class that inherits from `CommandBase` (no import needed — it is injected)
3. Implement `get_click_command()` returning a `click.Command`
4. Optionally implement `set_sidewalk(sidewalk)` to receive a per-command logger

**Important**: Do NOT import `CommandBase` or anything from `sidewalk.py`. `CommandBase` is automatically injected into your command's namespace at runtime. You may freely import `click` and any other third-party libraries.

## Logging

### Central Log
Framework operations are logged to `logs/sidewalk.log`:
- Command registration and loading
- Execution start/end
- Errors and warnings

### Command Logs
Each command gets its own log file at `logs/<command_name>.log`. Access it in your command class:

```python
def set_sidewalk(self, sidewalk):
    self.logger = sidewalk.get_command_logger("mycommand")
```

Then use it in your Click callback via closure:

```python
def get_click_command(self):
    instance = self

    @click.command(help="...")
    def mycommand():
        if instance.logger:
            instance.logger.info("Starting")
            instance.logger.error("Something went wrong")

    return mycommand
```

## Click Option Types

Common Click option patterns used in commands:

```python
# String option with default
@click.option('-n', '--name', default='World', show_default=True, help='...')

# Boolean flag
@click.option('-v', '--verbose', is_flag=True, help='...')

# Integer with minimum value constraint
@click.option('-c', '--count', default=1, type=click.IntRange(min=1), help='...')

# Required option (no default)
@click.option('-f', '--file', required=True, help='...')

# Choice from a list
@click.option('--format', type=click.Choice(['json', 'csv', 'text']), default='text', help='...')
```

## Advanced Usage

### Command Aliases
Edit `manifest.json` to add multiple entries pointing to the same file:
```json
{
  "commands": {
    "hello": "hello.py",
    "hi": "hello.py",
    "greet": "hello.py"
  }
}
```

## License

This is a framework template for educational purposes.

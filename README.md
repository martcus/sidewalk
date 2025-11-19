# Sidewalk - Pluggable Command Framework

A Python-based CLI framework with pluggable command architecture.

## Project Structure

```
sidewalk/
├── sidewalk.py          # Main CLI framework
├── manifest.json       # Command registry (auto-generated)
├── commands/           # Directory for command modules
│   └── hello.py       # Example command
└── logs/              # Log files (auto-generated)
    ├── sidewalk.log    # Central sidewalk log
    └── hello.log      # Command-specific logs
```

## Installation

1. Create the project directory structure:
```bash
mkdir -p sidewalk/commands sidewalk/logs
cd sidewalk
```

2. Save `sidewalk.py` as the main file
3. Save `hello.py` in the `commands/` directory
4. Make sidewalk.py executable (optional):
```bash
chmod +x sidewalk.py
```

## Usage

### Show Help
```bash
python sidewalk.py --help
# or
python sidewalk.py -h
```

Output example:
```
sidewalk CLI - A pluggable command-line interface framework

Usage: sidewalk <command> [parameters]
       sidewalk --help | -h

Options:
  --help, -h    Show this help message

Available Commands:

  hello    Prints a greeting message

For command-specific help:
  sidewalk <command> --help
```

### Register a Command
```bash
python sidewalk.py register hello hello.py
```

This will:
- Validate the command file exists in `commands/` directory
- Verify the command has required `short_help()`, `help()` and `execute()` methods
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

# All flags combined
python sidewalk.py hello -n Eve -u -c 2
# Output:
# HELLO, EVE!
# HELLO, EVE!
```

### Get Command-Specific Help
```bash
python sidewalk.py hello --help
```

Output:
```
Command: hello

Hello Command - Prints a greeting message

Usage: sidewalk hello [options]

Options:
  -n, --name <name>      Name to greet (default: World)
  -u, --uppercase        Display greeting in uppercase
  -c, --count <number>   Number of times to repeat the greeting (default: 1)

Examples:
  sidewalk hello
  sidewalk hello -n Alice
  sidewalk hello --name Bob --uppercase
  sidewalk hello -n Charlie -c 3
  sidewalk hello --help
```

## Creating a New Command

1. Create a new Python file in the `commands/` directory
2. Inherit from `CommandBase` (injected automatically by sidewalk)
3. Implement required methods: `short_help()`, `help()` and `execute()`
4. Register the command using the sidewalk

### Example Command Template

```python
"""
MyCommand - Description of what this command does

CommandBase will be injected at runtime by the sidewalk.
Do not import anything from sidewalk.
"""


class MyCommand(CommandBase):
    """Description of the command"""

    def __init__(self):
        self.sidewalk = None
        self.logger = None

    def set_sidewalk(self, sidewalk):
        """Set sidewalk instance for accessing logging"""
        self.sidewalk = sidewalk
        self.logger = sidewalk.get_command_logger("mycommand")

    def short_help(self) -> str:
        """Return a brief one-line description"""
        return "Brief description of what this command does"

    def help(self) -> str:
        """Return detailed help message"""
        return """
MyCommand - Does something useful

Usage: sidewalk mycommand [options]

Options:
  -f, --flag <value>    Description of flag
  -v, --verbose         Enable verbose mode

Examples:
  sidewalk mycommand
  sidewalk mycommand -f value
  sidewalk mycommand --flag value --verbose
"""

    def _parse_args(self, args: list) -> dict:
        """Parse command line arguments and flags"""
        params = {
            'flag': 'default_value',
            'verbose': False
        }

        i = 0
        while i < len(args):
            arg = args[i]

            # Handle flag with value
            if arg in ['-f', '--flag']:
                if i + 1 < len(args):
                    params['flag'] = args[i + 1]
                    i += 2
                    continue
                else:
                    raise ValueError(f"Flag '{arg}' requires a value")

            # Handle boolean flag
            elif arg in ['-v', '--verbose']:
                params['verbose'] = True
                i += 1
                continue

            # Unknown flag
            elif arg.startswith('-'):
                raise ValueError(f"Unknown flag: {arg}")

            # Positional argument
            else:
                # Handle positional arguments as needed
                i += 1

        return params

    def execute(self, args: list) -> int:
        """Execute the command"""
        if self.logger:
            self.logger.info("MyCommand started")

        try:
            # Parse arguments
            params = self._parse_args(args)

            if self.logger:
                self.logger.info(f"Parsed parameters: {params}")

            # Your command logic here
            print("Command executed successfully!")

            if self.logger:
                self.logger.info("MyCommand completed")

            return 0  # Return 0 for success

        except ValueError as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            print("Use 'sidewalk mycommand --help' for usage information")

            if self.logger:
                self.logger.error(error_msg)

            return 1  # Return non-zero for errors

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)

            if self.logger:
                self.logger.error(error_msg)

            return 1
```

### Register Your New Command

```bash
python sidewalk.py register mycommand mycommand.py
```

## Features

### 1. Pluggable Architecture
- Add new commands without modifying core code
- Commands are loaded dynamically from the manifest
- Each command is a separate Python module
- CommandBase is automatically injected into each command's namespace

### 2. Centralized Logging
- Main sidewalk log: `logs/sidewalk.log`
- Command-specific logs: `logs/<command_name>.log`
- All logging uses Python's built-in logging module
- Automatic log file creation for each command

### 3. Command Validation
- Automatic verification of required methods (`short_help()`, `help()` and `execute()`)
- Runtime validation when registering new commands
- Clear error messages for invalid commands

### 4. Built-in Help System
- Global help: `sidewalk --help` (shows all commands with brief descriptions)
- Command-specific help: `sidewalk <command> --help` (shows detailed help)
- Two-tier help system:
  - `short_help()` - One-line description shown in command list
  - `help()` - Detailed help shown when requested for specific command

### 5. Command Registry
- Commands stored in `manifest.json`
- Easy to backup, share, or version control
- Automatic creation if missing
- Simple JSON format

### 6. Flag and Parameter Handling
- Support for both short (`-n`) and long (`--name`) flags
- Boolean flags (no value required)
- Flags with required values
- Positional arguments support
- Comprehensive error handling for invalid flags

## Command Requirements

Every command must:
1. Be a Python file in the `commands/` directory
2. Contain a class that inherits from `CommandBase` (no import needed)
3. Implement `short_help()` method returning a brief string (one line, ~60-80 chars)
4. Implement `help()` method returning a detailed help string
5. Implement `execute(args: list)` method returning an integer (0 = success, non-zero = error)
6. Optionally implement `set_sidewalk(sidewalk)` for logging access

**Important**: Do NOT import `CommandBase` or anything from `sidewalk.py`. The `CommandBase` class is automatically injected into your command's namespace at runtime.

## Logging

### Central Log
All sidewalk operations are logged to `logs/sidewalk.log`:
- Command registration
- Command loading
- Execution start/end
- Errors and warnings

### Command Logs
Each command gets its own log file in `logs/<command_name>.log`:
- Access via `self.logger` in command class
- Automatically created when command is executed
- Separate from central log for easier debugging

### Using Logger in Commands

```python
def execute(self, args: list) -> int:
    if self.logger:
        self.logger.info("Starting execution")
        self.logger.debug("Debug information")
        self.logger.warning("Warning message")
        self.logger.error("Error message")

    return 0
```

## Flag Parsing Pattern

The recommended pattern for parsing flags:

```python
def _parse_args(self, args: list) -> dict:
    """Parse command line arguments and flags"""
    params = {
        'param1': 'default_value',
        'flag1': False,
        'count': 1
    }

    i = 0
    while i < len(args):
        arg = args[i]

        # Flag with value
        if arg in ['-p', '--param1']:
            if i + 1 < len(args):
                params['param1'] = args[i + 1]
                i += 2
                continue
            else:
                raise ValueError(f"Flag '{arg}' requires a value")

        # Boolean flag
        elif arg in ['-f', '--flag1']:
            params['flag1'] = True
            i += 1
            continue

        # Unknown flag
        elif arg.startswith('-'):
            raise ValueError(f"Unknown flag: {arg}")

        # Positional argument
        else:
            # Handle as needed
            i += 1

    return params
```

## Error Handling

Commands should return appropriate exit codes:
- `0` - Success
- `1` - General error
- `2+` - Specific error conditions (optional)

Example:
```python
def execute(self, args: list) -> int:
    try:
        # Command logic
        return 0
    except ValueError as e:
        self.logger.error(f"Value error: {e}")
        print(f"Error: {e}")
        return 1
    except FileNotFoundError:
        self.logger.error("File not found")
        print("Error: Required file not found")
        return 2
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        return 1
```

## Advanced Usage

### Creating Command Aliases
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

### Complex Flag Combinations
Commands can handle multiple flags in any order:
```bash
python sidewalk.py hello -n Alice -u -c 3
python sidewalk.py hello --uppercase --name Bob --count 2
python sidewalk.py hello -u -c 2 -n Charlie
```

## Troubleshooting

### Command Not Found
- Ensure the command file is in the `commands/` directory
- Check that the command is registered in `manifest.json`
- Verify the command name matches exactly
- Run `python sidewalk.py --help` to see registered commands

### Command Won't Load
- Check `logs/sidewalk.log` for error messages
- Ensure command inherits from `CommandBase`
- Verify all three methods are implemented: `short_help()`, `help()`, `execute()`
- Do NOT import `CommandBase` - it's injected automatically

### Logging Not Working
- Ensure `logs/` directory exists (created automatically)
- Check file permissions
- Verify `set_sidewalk()` method is implemented in command

### Flag Parsing Issues
- Ensure flags have values when required
- Check for typos in flag names
- Use `--help` to see available flags
- Check command logs for parsing errors

## Examples

### List All Commands with Descriptions
```bash
python sidewalk.py --help
```

### Register and Run Hello Command
```bash
python sidewalk.py register hello hello.py
python sidewalk.py hello
python sidewalk.py hello -n "Your Name"
```

### Create Custom Timestamp Command
```bash
# 1. Create command file
cat > commands/timestamp.py << 'EOF'
"""
Timestamp Command - Displays current date and time
"""

from datetime import datetime


class TimestampCommand(CommandBase):

    def __init__(self):
        self.sidewalk = None
        self.logger = None

    def set_sidewalk(self, sidewalk):
        self.sidewalk = sidewalk
        self.logger = sidewalk.get_command_logger("timestamp")

    def short_help(self):
        return "Displays current date and time"

    def help(self):
        return """
Timestamp Command - Displays current date and time

Usage: sidewalk timestamp [options]

Options:
  -f, --format <fmt>    Format string (iso, short, long)

Examples:
  sidewalk timestamp
  sidewalk timestamp -f iso
  sidewalk timestamp --format long
"""

    def _parse_args(self, args):
        params = {'format': 'iso'}
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ['-f', '--format']:
                if i + 1 < len(args):
                    params['format'] = args[i + 1]
                    i += 2
                    continue
                else:
                    raise ValueError(f"Flag '{arg}' requires a value")
            elif arg.startswith('-'):
                raise ValueError(f"Unknown flag: {arg}")
            else:
                i += 1
        return params

    def execute(self, args):
        if self.logger:
            self.logger.info("Timestamp command started")

        try:
            params = self._parse_args(args)
            now = datetime.now()

            if params['format'] == 'iso':
                print(now.isoformat())
            elif params['format'] == 'short':
                print(now.strftime("%Y-%m-%d %H:%M:%S"))
            elif params['format'] == 'long':
                print(now.strftime("%A, %B %d, %Y at %I:%M:%S %p"))
            else:
                print(f"Unknown format: {params['format']}")
                return 1

            if self.logger:
                self.logger.info("Timestamp command completed")
            return 0

        except Exception as e:
            print(f"Error: {e}")
            if self.logger:
                self.logger.error(f"Error: {e}")
            return 1
EOF

# 2. Register it
python sidewalk.py register timestamp timestamp.py

# 3. Use it
python sidewalk.py timestamp
python sidewalk.py timestamp -f long
```

## Best Practices

1. **Short Help**: Keep it concise (60-80 characters max)
   - ✅ "Prints a greeting message"
   - ❌ "This command prints a customizable greeting message to the console with optional formatting"

2. **Detailed Help**: Include all information users need
   - Usage syntax
   - All flags with descriptions
   - Examples of common use cases

3. **Flag Names**: Use clear, descriptive names
   - Short: single letter (`-n`, `-v`, `-f`)
   - Long: descriptive word (`--name`, `--verbose`, `--format`)

4. **Error Messages**: Be specific and helpful
   - ✅ "Error: Flag '-n' requires a value"
   - ❌ "Error"

5. **Logging**: Log important operations
   - Command start/end
   - Parameter values
   - Errors and warnings
   - Don't log sensitive information

6. **Return Codes**: Use meaningful exit codes
   - 0 for success
   - 1 for general errors
   - 2+ for specific error types (optional)

## License

This is a framework template for educational purposes.

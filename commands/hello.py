"""
Hello Command - Example command that prints "Hello, World!"

This command demonstrates how to handle command-line flags and parameters.
CommandBase will be injected at runtime by the toolkit.
"""


class HelloCommand(CommandBase):
    """A simple example command that prints a greeting"""

    def __init__(self):
        self.toolkit = None
        self.logger = None

    def set_toolkit(self, toolkit):
        """Set toolkit instance for accessing logging"""
        self.toolkit = toolkit
        self.logger = toolkit.get_command_logger("hello")

    def short_help(self) -> str:
        """Return a brief one-line description"""
        return "Prints a greeting message"

    def help(self) -> str:
        """Return help message for this command"""
        return """
Hello Command - Prints a greeting message

Usage: toolkit hello [options]

Options:
  -n, --name <name>       Name to greet (default: World)
  -u, --uppercase         Display greeting in uppercase
  -c, --count <number>    Number of times to repeat the greeting (default: 1)

Examples:
  toolkit hello
  toolkit hello -n Alice
  toolkit hello --name Bob --uppercase
  toolkit hello -n Charlie -c 3
  toolkit hello --help
"""

    def _parse_args(self, args: list) -> dict:
        """Parse command line arguments and flags"""
        params = {
            'name': 'World',
            'uppercase': False,
            'count': 1
        }

        i = 0
        while i < len(args):
            arg = args[i]

            # Handle name flag
            if arg in ['-n', '--name']:
                if i + 1 < len(args):
                    params['name'] = args[i + 1]
                    i += 2
                    continue
                else:
                    raise ValueError(f"Flag '{arg}' requires a value")

            # Handle uppercase flag
            elif arg in ['-u', '--uppercase']:
                params['uppercase'] = True
                i += 1
                continue

            # Handle count flag
            elif arg in ['-c', '--count']:
                if i + 1 < len(args):
                    try:
                        params['count'] = int(args[i + 1])
                        if params['count'] < 1:
                            raise ValueError("Count must be at least 1")
                    except ValueError as e:
                        raise ValueError(f"Invalid count value: {args[i + 1]}")
                    i += 2
                    continue
                else:
                    raise ValueError(f"Flag '{arg}' requires a value")

            # Unknown flag
            elif arg.startswith('-'):
                raise ValueError(f"Unknown flag: {arg}")

            # Positional argument (treat as name if no -n/--name was used)
            else:
                if params['name'] == 'World':  # Only if not already set by flag
                    params['name'] = arg
                i += 1

        return params

    def execute(self, args: list) -> int:
        """Execute the hello command"""
        if self.logger:
            self.logger.info("Hello command started")
            self.logger.debug(f"Arguments: {args}")

        try:
            # Parse arguments
            params = self._parse_args(args)

            if self.logger:
                self.logger.info(f"Parsed parameters: {params}")

            # Build greeting message
            message = f"Hello, {params['name']}!"

            # Apply uppercase if requested
            if params['uppercase']:
                message = message.upper()

            # Print greeting the specified number of times
            for i in range(params['count']):
                print(message)

            if self.logger:
                self.logger.info(f"Printed greeting: {message} (x{params['count']})")
                self.logger.info("Hello command completed successfully")

            return 0

        except ValueError as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            print("Use 'toolkit hello --help' for usage information")

            if self.logger:
                self.logger.error(error_msg)

            return 1

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)

            if self.logger:
                self.logger.error(error_msg)

            return 1

"""
Hello Command - Example command that prints "Hello, World!"

CommandBase will be injected at runtime by sidewalk.
Do not import anything from sidewalk.
"""

import click


class HelloCommand(CommandBase):
    """A simple example command that prints a greeting"""

    def __init__(self):
        self.sidewalk = None
        self.logger = None

    def set_sidewalk(self, sidewalk):
        """Set sidewalk instance for accessing logging"""
        self.sidewalk = sidewalk
        self.logger = sidewalk.get_command_logger("hello")

    def get_click_command(self) -> click.Command:
        instance = self

        @click.command(help="Prints a greeting message")
        @click.option('-n', '--name', default='World', show_default=True,
                      help='Name to greet')
        @click.option('-u', '--uppercase', is_flag=True,
                      help='Display greeting in uppercase')
        @click.option('-c', '--count', default=1, show_default=True,
                      type=click.IntRange(min=1),
                      help='Number of times to repeat the greeting')
        def hello(name, uppercase, count):
            if instance.logger:
                instance.logger.info("Hello command started")

            message = f"Hello, {name}!"
            if uppercase:
                message = message.upper()

            for _ in range(count):
                click.echo(message)

            if instance.logger:
                instance.logger.info(f"Printed greeting: {message} (x{count})")
                instance.logger.info("Hello command completed successfully")

        return hello

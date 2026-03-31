# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the CLI
python sidewalk.py --help
python sidewalk.py <command> [args]
python sidewalk.py <command> --help

# Register a new command
python sidewalk.py register <command_name> <command_file.py>

# Example: run the built-in hello command
python sidewalk.py hello
python sidewalk.py hello -n Alice --uppercase --count 3
```

There is no build step, test suite, or package installation required — this is a pure Python project invoked directly.

## Architecture

**sidewalk.py** is the entire framework. It defines two classes:

- `CommandBase` — abstract base all commands must subclass. Requires `short_help()`, `help()`, and `execute(args) -> int`.
- `Sidewalk` — loads `manifest.json`, dynamically imports command modules via `importlib`, injects `CommandBase` into each module's namespace at load time (so commands must NOT import it), and dispatches execution.

**manifest.json** maps command names to filenames inside `commands/`. It is auto-created if missing and updated by `sidewalk register`.

**commands/** holds one Python file per command. Each file defines exactly one `CommandBase` subclass. The class is discovered by iterating `dir(module)` looking for a `CommandBase` subclass.

**logs/** is auto-created. `logs/sidewalk.log` captures framework-level events. Each command gets `logs/<command_name>.log` via `sidewalk.get_command_logger(name)`.

## Creating a Command

1. Create `commands/<name>.py` — do NOT import `CommandBase`, it is injected at runtime.
2. Subclass `CommandBase` and implement `short_help()`, `help()`, and `execute(args: list) -> int`.
3. Optionally implement `set_sidewalk(sidewalk)` to receive a logger: `self.logger = sidewalk.get_command_logger("<name>")`.
4. Register: `python sidewalk.py register <name> <name>.py`

Flag parsing is done manually with a `while i < len(args)` loop (no argparse). Return `0` for success, non-zero for errors.

Command aliases are supported by adding multiple entries in `manifest.json` pointing to the same file.

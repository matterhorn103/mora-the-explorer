import logging
import sys

from ..explorer import app, Config, Explorer


class TerminalProgress:
    def __init__(self):
        self._value = 0
        self._max = 0

    def setValue(self, value):
        self._value = value
        self.print_progress()
    
    def setMaximum(self, max):
        self._max = max
    
    def maximum(self):
        return self._max
    
    def print_progress(self):
        try:
            print(f"Progress: {int((self._value / self._max) * 100)}%")
        except ZeroDivisionError:
            print(f"Progress: 100%")


def setup_command_line_explorer(rsrc_dir):
    # Load configuration - Explorer needs it
    logging.info(f"Program resources located at {rsrc_dir}")
    logging.info("Loading program settings...")
    config = Config(rsrc_dir / "config.toml")
    logging.info("...complete")

    # Create instance of Explorer (back-end)
    logging.info("Initializing explorer...")
    explorer = Explorer(config)
    logging.info("...complete")

    logging.info("Initialization complete")

    return explorer


def cli_completion_handler(explorer, copied_list, prog_bar):
    """The handler for a completed check."""
    
    explorer.queued_checks -= 1
    if len(copied_list) > 1:
        # At least one spectrum was found
        if copied_list[1][:5] == "Spect":
            copied_list.pop(0)
    # Display output
    for entry in copied_list:
        print(entry)
    # Task is complete only if all queued checks have finished
    if explorer.queued_checks == 0:
        prog_bar.setValue(prog_bar.maximum())
        logging.info("Task complete")
        app().exit(0)

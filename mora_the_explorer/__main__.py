"""The main entry point when mora_the_explorer is used on the command line."""

import logging
import sys
from pathlib import Path

from .app import App
from .explorer.config import Config
from .explorer.explorer import Explorer

# Always create an instance of the "app", even if imported for use as package or via CLI
# Otherwise some Qt things don't work properly
logging.info("Initializing app...")
app = App(sys.argv)
logging.info("...complete")


def setup_command_line_explorer(rsrc_dir):
    # Load configuration - Explorer needs it
    logging.info(f"Program resources located at {rsrc_dir}")
    logging.info("Loading program settings...")
    config = Config(rsrc_dir / "config.toml")
    logging.info("...complete")

    # Create instance of Explorer (back-end)
    logging.info("Initializing explorer...")
    explorer = Explorer(rsrc_dir, config)
    logging.info("...complete")

    logging.info("Initialization complete")

    return explorer


if __name__ == "__main__":
    """Run Mora the Explorer as an executable."""
    rsrc_dir = Path.cwd() / "../config.toml"
    explorer = setup_command_line_explorer(rsrc_dir)
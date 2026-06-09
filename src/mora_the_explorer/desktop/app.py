from PySide6.QtGui import QIcon
from typing import cast
import logging
from pathlib import Path

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtWidgets import QApplication

from .. import LOG_FILE, get_rsrc_dir
from .. import resources  # noqa: F401
from ..core.config import Config, USER_CONFIG_PATH
from .controller import Controller


def load_resource(path: str) -> bytes:
    f = QFile(path)
    if not f.open(QIODevice.OpenModeFlag.ReadOnly):
        raise RuntimeError(f"Could not open resource: {path}")
    try:
        data = cast(bytes, f.readAll().data())
    finally:
        f.close()
    return data


def load_compiled_app_config() -> bytes:
    """Load the app config that is compiled into the Qt resources file."""
    app_config_file = load_resource(":/config.toml")
    return app_config_file


class App:
    """A wrapper for a `Controller` and the actual `QApplication`."""

    def __init__(
        self,
        app_config_file: Path | bytes | str | None = None,
        user_config_file: Path = USER_CONFIG_PATH,
    ):
        """Create a Mora the Explorer desktop application with a GUI, but don't run it yet."""

        self.app = QApplication()
        rsrc_dir = get_rsrc_dir()
        self.app.setWindowIcon(QIcon(str(rsrc_dir / "explorer.ico")))

        logging.basicConfig(
            filename=LOG_FILE,
            filemode="w",
            format="%(asctime)s %(message)s",
            encoding="utf-8",
            level=logging.INFO,
        )

        logging.info("Loading program settings…")
        if app_config_file is None:
            app_config_file = load_compiled_app_config()
        config = Config(app_config_file, user_config_file)
        logging.info("…complete")

        # Create singleton instance of `Controller` to handle the various components
        self.controller = Controller(config)

        logging.info("Initialization complete")

    def run(self) -> int:
        """Run the Mora the Explorer desktop application.

        Returns the error code produced by `QApplication.exec()`.
        """

        return self.app.exec()

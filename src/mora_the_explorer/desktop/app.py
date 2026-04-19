import logging
import platform

import darkdetect

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtWidgets import QApplication

from .. import LOG_FILE, get_rsrc_dir
from ..config import Config
from .controller import Controller


class App:
    """A wrapper for a `Controller` and the actual `QApplication`."""

    def __init__(self, config: Config | None = None):
        """Create a Mora the Explorer desktop application with a GUI, but don't run it yet."""

        self.app = QApplication()

        logging.basicConfig(
            filename=LOG_FILE,
            filemode="w",
            format="%(asctime)s %(message)s",
            encoding="utf-8",
            level=logging.INFO,
        )

        rsrc_dir = get_rsrc_dir()
        # Load configuration if none passed – Controller needs it
        if config is None:
            logging.info(f"Program resources located at {rsrc_dir}")
            logging.info("Loading program settings...")
            config = Config(rsrc_dir / "config.toml")
            logging.info("...complete")

        # Load the version header
        with open(rsrc_dir / "version.txt", encoding="utf-8") as f:
            version_header = f.read()

        # Create singleton instance of `Controller` to handle the various components
        self.controller = Controller(config, version_header)

        if darkdetect.isDark() is True and platform.system() == "Windows":
            self.set_dark_mode()

        self.app.setWindowIcon(QIcon(str(rsrc_dir / "explorer.ico")))

        logging.info("Initialization complete")

    def set_dark_mode(self):
        """Manually set a dark mode (intended for use on Windows).

        Make dark mode less black than Windows default dark mode because it looks bad.
        """

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.black)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.app.setStyle("Fusion")
        self.app.setPalette(dark_palette)

    def run(self) -> int:
        """Run the Mora the Explorer desktop application.

        Returns the error code produced by `QApplication.exec()`.
        """

        return self.app.exec()

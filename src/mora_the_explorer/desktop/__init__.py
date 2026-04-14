import logging
import platform
from pathlib import Path

import darkdetect

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtWidgets import QApplication

from .. import LOG_FILE
from ..config import Config
from ..explorer import Explorer
from .controller import Controller
from .ui.main_window import MainWindow


def set_dark_mode(app: QApplication):
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
    app.setStyle("Fusion")
    app.setPalette(dark_palette)


def run_desktop_app(rsrc_dir: Path):
    """Run Mora the Explorer as a desktop application with a GUI."""

    app = QApplication()

    logging.basicConfig(
        filename=LOG_FILE,
        filemode="w",
        format="%(asctime)s %(message)s",
        encoding="utf-8",
        level=logging.INFO,
    )

    # Load configuration - both MainWindow and Explorer need it
    logging.info(f"Program resources located at {rsrc_dir}")
    logging.info("Loading program settings...")
    config = Config(rsrc_dir / "config.toml")
    logging.info("...complete")

    # Create instance of MainWindow (front-end), then show it
    logging.info("Initializing user interface...")
    window = MainWindow(rsrc_dir, config)
    window.show()
    logging.info("...complete")

    if darkdetect.isDark() is True and platform.system() == "Windows":
        set_dark_mode(app)

    # Create instance of Explorer (back-end)
    logging.info("Initializing explorer...")
    explorer = Explorer(config)
    logging.info("...complete")

    # Create instance of Controller to handle communication between the two
    _controller = Controller(explorer, window, rsrc_dir, config)

    app.get().setWindowIcon(QIcon(str(rsrc_dir / "explorer.ico")))

    logging.info("Initialization complete")
    app.exec()

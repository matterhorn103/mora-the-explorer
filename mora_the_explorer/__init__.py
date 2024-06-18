"""
Mora the Explorer checks for new NMR spectra at the Organic Chemistry department at the University of Münster.
Copyright (C) 2023 Matthew J. Milner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import platform
import sys
from pathlib import Path

import darkdetect
import platformdirs

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QIcon
from PySide6.QtWidgets import QApplication

from .explorer import Config, Explorer
from .desktop import Controller, MainWindow


class App(QApplication):
    """The overall Mora the Explorer graphical application class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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
        self.setStyle("Fusion")
        self.setPalette(dark_palette)


# Always create an instance of the "app", even if imported for use as package or via CLI
# Otherwise some Qt things don't work properly
app = App(sys.argv)


def run_desktop_app(rsrc_dir: Path, explorer: Explorer | None = None):
    """Run Mora the Explorer as a desktop application with a GUI."""

    # Logs should be saved to:
    # Windows:  c:/Users/<user>/AppData/Local/mora_the_explorer/log.log
    # macOS:    /Users/<user>/Library/Logs/mora_the_explorer/log.log
    # Linux:    /home/<user>/.local/state/mora_the_explorer/log.log
    log = Path(
        platformdirs.user_log_dir(
            "mora_the_explorer",
            opinion=False,
            ensure_exists=True,
        )
    ) / "log.log"

    logging.basicConfig(
        filename=log,
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
        app.set_dark_mode()

    # Create instance of Explorer (back-end), unless we were passed an existing one
    if explorer is None:
        logging.info("Initializing explorer...")
        explorer = Explorer(config)
        logging.info("...complete")

    # Create instance of Controller to handle communication between the two
    controller = Controller(explorer, window, rsrc_dir, config)

    app.setWindowIcon(QIcon(str(rsrc_dir / "explorer.ico")))

    logging.info("Initialization complete")
    app.exec()

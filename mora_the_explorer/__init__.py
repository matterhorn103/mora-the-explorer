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

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPalette, QColor
from PySide6.QtWidgets import QApplication

from .config import Config
from .explorer import Explorer
from .ui.main_window import MainWindow


def set_dark_mode(app):
    """Manually set a dark mode in Windows.

    Make dark mode less black than default because Windows dark mode looks bad."""
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


def run(rsrc_dir):
    """Run Mora the Explorer."""

    # Load configuration
    logging.info(f"Program resources located at {rsrc_dir}")
    logging.info("Loading program settings...")
    config = Config(rsrc_dir)
    logging.info("...complete")

    logging.info("Initializing program...")
    app = QApplication(sys.argv)

    if darkdetect.isDark() is True and platform.system() == "Windows":
        set_dark_mode(app)

    # Create instance of MainWindow (front-end), then show it
    logging.info("Initializing user interface...")
    window = MainWindow(rsrc_dir, config)
    window.show()
    logging.info("...complete")

    # Create instance of Explorer (back-end)
    # Give it our MainWindow so it can read things directly from the UI
    logging.info("Initializing explorer...")
    explorer = Explorer(window, rsrc_dir, config)
    logging.info("...complete")

    app.setWindowIcon(QIcon(str(rsrc_dir / "explorer.ico")))

    logging.info("Initialization complete")
    app.exec()

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

from PySide6.QtGui import QIcon

from .app import App
from .desktop.controller import Controller
from .desktop.ui.main_window import MainWindow
from .explorer.config import Config
from .explorer.explorer import Explorer


def run_desktop_app(rsrc_dir: Path):
    """Run Mora the Explorer as a desktop application with a GUI."""

    # Load configuration - both MainWindow and Explorer need it
    logging.info(f"Program resources located at {rsrc_dir}")
    logging.info("Loading program settings...")
    config = Config(rsrc_dir / "config.toml")
    logging.info("...complete")

    # Create a QApplication instance
    logging.info("Initializing app...")
    app = App(sys.argv)
    logging.info("...complete")

    # Create instance of MainWindow (front-end), then show it
    logging.info("Initializing user interface...")
    window = MainWindow(rsrc_dir, config)
    window.show()
    logging.info("...complete")

    if darkdetect.isDark() is True and platform.system() == "Windows":
        app.set_dark_mode()

    # Create instance of Explorer (back-end)
    logging.info("Initializing explorer...")
    explorer = Explorer(rsrc_dir, config)
    logging.info("...complete")

    # Create instance of Controller to handle communication between the two
    controller = Controller(explorer, window, rsrc_dir, config)

    app.setWindowIcon(QIcon(str(rsrc_dir / "explorer.ico")))

    logging.info("Initialization complete")
    app.exec()

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

from config import Config
from main_window import MainWindow


def get_rsrc_dir():
    """Gets the location of the program's resources, which is platform-dependent."""
    # For whatever reason __file__ doesn't give the right location on a mac when a .app has
    # been generated with pyinstaller
    if platform.system() == "Darwin" and getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent


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


if __name__ == "__main__":
    # Assign directory containing the various supporting files to a variable so we can pass
    # it to our MainWindow and use it whenever necessary.
    rsrc_dir = get_rsrc_dir()

    # Set up logging
    log = rsrc_dir / "log.log"
    logging.basicConfig(
        filename=log,
        filemode="w",
        format="%(asctime)s %(message)s",
        encoding="utf-8",
        level=logging.INFO,
    )

    # Load configuration
    config = Config(rsrc_dir)

    logging.info("Initializing program")
    app = QApplication(sys.argv)

    if darkdetect.isDark() is True and platform.system() == "Windows":
        set_dark_mode(app)

    # Create instance of MainWindow, then show it
    window = MainWindow(rsrc_dir, config)
    window.show()


    app.setWindowIcon(QIcon("explorer.ico"))
    app.exec()

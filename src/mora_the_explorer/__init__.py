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

from pathlib import Path
import sys

import platformdirs

from .core import Config as Config, Explorer as Explorer, USER_CONFIG_PATH as USER_CONFIG_PATH


#: Logs should be saved to:
#: - Windows:  c:/Users/<user>/AppData/Local/mora_the_explorer/log.log
#: - macOS:    /Users/<user>/Library/Logs/mora_the_explorer/log.log
#: - Linux:    /home/<user>/.local/state/mora_the_explorer/log.log
LOG_FILE = (
    Path(
        platformdirs.user_log_dir(
            "mora_the_explorer",
            opinion=False,
            ensure_exists=True,
        )
    )
    / "log.log"
)

# Set up default logging for the whole package
# (no instances of any classes have been instantiated yet, so there haven't
# been any missed logging calls during the imports)
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",
    format="%(asctime)s %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def get_rsrc_dir():
    """Gets the location of the program's resources, which is platform-dependent."""
    # __file__ doesn't give the right location on a mac when a .app has
    # been generated with pyinstaller
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent

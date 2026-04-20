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

import sys

from mora_the_explorer.desktop import App

if __name__ == "__main__":
    app = App()
    sys.exit(app.run())

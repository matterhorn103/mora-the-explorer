# mora_the_explorer

A small program written for use at the Organic Chemistry department at the University of Münster.
Mora the Explorer checks the central server for NMR data matching the user's details and automatically saves any new ones to a folder of the user's choosing (e.g. personal analytics folder).

The app is written in Python (v3.12) using the PySide6 bindings for the Qt6 framework.

The app can be "compiled" to an `.exe` Windows executable using `pyinstaller` (installable via `pip install pyinstaller`). For this a `.spec` file is provided, so all settings have been taken care of and the app bundle can be prepared just by executing the command `pyinstaller .\mora_the_explorer.spec` within the directory of the files (once the necessary dependencies listed in `pyproject.toml` have been installed, naturally).


## Features

**Advantages** over the `NMRCheck` program used until now include:
* Can find spectra from both Bruker and Agilent spectrometers, including the department's high-field 500/600 MHz spectrometers
* Fast! Doesn't check the whole server every time, and Python caches the parts that it has checked, so it takes only seconds to check for new spectra
* Crashes much less frequently than `NMRCheck`
* Has a progress bar to show progress and a spinner to show that a check is running
* Looks (and is) much more modern, in particular making option selection much less ambiguous (it is clear which has been selected), improving the UX
* Looks native to the system, and supports dark mode
* Checks for spectra from any chosen date, but only from this date, so won't download hundreds of spectra at once
* At the same time, the option exists to check a range of dates in one go
* Can be used to get spectra even months or years after measurement
* Can identify if previously copied spectra are missing files and add the new ones (useful if some error occurred or e.g. when only the proton spectrum of a sample submitted on the high-field spectra was completed on the last check but carbon, COSY etc. have been measured since)
* Whether spectra are copied depends on whether one with the same name exists in the target folder, not on whether they were measured before/after the last check
* Saves spectra with a sensible name including experiment (proton, 13C etc) so you don't have to rename them yourself - I save directly to my analytics NMR folder
* Can save with solvent in name if desired
* System notifications when spectra are found
* Option to keep checking every few minutes like `NMRCheck`, but doesn't have to - this saves resources vs `NMRCheck`
* Frequency for repeated check can be set
* Configuration saved to a config file which follows the user across different Windows PCs within the uni
* Has a better name (possibly most important)


## Installation

Ready-to-use versions for Windows, macOS, and Linux (in the form of executable binaries prepared with PyInstaller) are available on the Organic Chemistry department's central NMR server at `\\mora\nmr\mora_the_explorer\`.

The same binaries can also be downloaded from this repository's [releases page](https://github.com/matterhorn103/mora-the-explorer/releases).

Alternatively, the code can be downloaded and run directly with Python.
All necessary packages to run the desktop app are listed in `pyproject.toml` and can be installed in the usual way using `pip` or any other package manager (our preferred option is [`uv`](https://github.com/astral-sh/uv)).
Running `python3 mora_the_explorer.py` from the command line will then open the desktop app.

Alternatively, Mora the Explorer can be itself installed as a Python package (either system-wide or into a Python virtual environment) by executing e.g. `pip install .` from within the project's folder.
After this, the app can be run from the command line with `mora-the-explorer`.


## Usage

### NMR sample submission

The first step is of course to actually measure the NMR spectra.
Mora the Explorer expects the "title" field of submitted measurements to have been filled out according to the department's rules for sample/measurement names:

1. Sample names must begin with the group's abbreviation, followed by the user's three-letter abbreviation, followed by a sample code, separated by spaces
2. The abbreviations must be typed in lowercase

If these two rules are followed, spectra will be found by Mora the Explorer. Additionally, the NMR department has the rule that:

3. Sample codes should consist of the reaction number followed by a sample number, separated by a hyphen; samples should be simply numbered sequentially (`-1`, `-2` etc.)
4. Extra letters are allowed only when they occur as part of the actual reaction number e.g. to indicate a student on placement/Praktikum

This results in sample names of the form `stu mjm 301-2`, or `stu mjm al-12-1` for reactions run as part of Praktika.

Though the program will successfully find and copy any spectra featuring that match the first two rules, sample numbers are expected in the prescribed format. For example, extra hyphens e.g. `"stu mjm-301-2"` will result in the automatic formatting working less well.


### Desktop app

Usage is fairly self-explanatory within the app.
The NMR department has also made a guide available on their [website](https://www.uni-muenster.de/imperia/md/content/organisch_chemisches_institut2/nmr/readme_mora_the_explorer.pdf), though the information may not be completely up-to-date.

To set up the search options:

1. Type your insitute-wide three-letter initialism into the `initials` field.
2. Select your research group from the options.
    - If your group is not shown, select "other" and find your group in the drop-down list that appears.
3. Type or copy-and-paste the location you wish to save copies of the spectra to into the `save in` field.
    - The location given can be opened in your system's file explorer at any time by clicking the "go to" button or using the shortcut <kbd>Ctrl</kbd>+<kbd>G</kbd>
4. Next to `include:`, check or uncheck the boxes as desired to determine which extra information should be included in the name of the copied spectrum's folder.
    - The experiment name (`proton`, `carbon256`, `dept90` etc.) is always included.
    - For example, a $^1$H spectrum measured in CDCl$_3$ with the provided title `stu mjm 301-2` will be saved as `301-2-proton` by default, and as `mjm-301-2-proton-CDCl3` if both "initials" and "solvent" are checked.
    - The "use comprehensive (NMRCheck) style" option is provided to use folder name formatting as close as possible to the syntax used by the previous app, NMRCheck. This is provided for compatibility only, and its use should be avoided by new users. It results in unwieldy folder names like `mjm_301-2_neo400c_Jul02-2024_240-proton`.
5. Select the spectrometer that should be checked.
    - Note that the availability of some options can be affected by the choice of spectrometer.
6. If desired, the app can automatically run a new check at the user-specified interval by checking the box next to `repeat:`.
7. After any changes have been made to the above options, the selection can be saved as the default settings by clicking the appropriate button.
    - Your user configuration is stored in the appropriate place for your operating system:
        - ![image](https://commons.wikimedia.org/wiki/File:Windows_logo_-_2021.svg#/media/File:Windows_logo_-_2021.svg) `%USERPROFILE%\AppData\Roaming\mora_the_explorer\config.toml`
        - ![image](https://commons.wikimedia.org/wiki/File:Apple_logo_grey.svg) `~/Library/Application Support/mora_the_explorer/config.toml`
        - ![image](https://upload.wikimedia.org/wikipedia/commons/6/64/Tux_Classic_flat_look_v1.1.svg) `$XDG_CONFIG_HOME/mora_the_explorer` or `~/.config/mora_the_explorer/config.toml`

To run a search:

1. Select the date to search in the box.
    - Each part of the date can be selected individually and adjusted using the arrows or replaced by typing.
    - 
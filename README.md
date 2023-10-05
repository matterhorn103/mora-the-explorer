# mora_the_explorer
This is a fresh public version of the formerly private repo, without the commit history.

A small GUI program written for use at the Organic Chemistry department at the WWU Münster.
Mora the Explorer checks the central \\mora server for NMR data matching the user's details and automatically saves any new ones to a folder of the user's choosing (e.g. personal analytics folder).

The app is written in Python (v3.12.0) using the PySide6 bindings for the Qt6 framework (PyQt6 bindings until v1.3).

The app can be compiled to an .exe Windows executable using pyinstaller (installable via `pip install pyinstaller`). For this a .spec file is provided, and thus it is only required to use the command `pyinstaller .\mora_the_explorer.spec` within the directory of the files, and everything will be taken care of automatically.

**Advantages** over the NMRCheck program used until now include:
* Can find spectra not just on the Studer group spectrometer but also on the service 400 MHz and high-field 500/600 MHz spectrometers
* Fast! Doesn't check the whole server every time, so it takes barely a second to check for new spectra
* Crashes much less frequently than NMRCheck
* Has a progress bar to show progress
* Looks (and is) much more modern, which makes option selection much less ambiguous (it is clear which has been selected), improving the UX. Also supports dark mode
* Can check for spectra from any chosen date, and only from this date, so won't download hundreds of spectra at once
* Saves spectra with a sensible name including experiment (proton, 13C etc) so you don't have to rename them yourself - I save directly to my analytics NMR folder
* Can save with solvent in name if desired
* Option to keep checking every few minutes like NMRCheck, but doesn't have to - this saves resources vs NMRCheck
* Frequency for repeated check can be set
* Has a better name (possibly most important)

Usage is fairly self-explanatory within the app. When submitting samples to the NMR spectrometers it is important to stick to the rules for naming spectra: firstly, only if the user's initalism is typed in lowercase will Mora the Explorer find the spectra; secondly, though the program will successfully find and copy any spectra featuring the user's initials, sample names are expected in the format "stu mjm 301-2" and extra hyphens e.g. "stu mjm-301-2" will result in the automatic formatting working less well.


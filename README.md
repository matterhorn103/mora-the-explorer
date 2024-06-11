# mora_the_explorer

A small GUI program written for use at the Organic Chemistry department at the University of Münster.
Mora the Explorer checks the central `\\mora` server for NMR data matching the user's details and automatically saves any new ones to a folder of the user's choosing (e.g. personal analytics folder).

The app is written in Python (v3.12) using the PySide6 bindings for the Qt6 framework.

The app can be "compiled" to an `.exe` Windows executable using `pyinstaller` (installable via `pip install pyinstaller`). For this a `.spec` file is provided, so all settings have been taken care of and the app bundle can be prepared just by executing the command `pyinstaller .\mora_the_explorer.spec` within the directory of the files (once the necessary dependencies listed in `pyproject.toml` have been installed, naturally).

**Advantages** over the `NMRCheck` program used until now include:
* Can find spectra not just on the Studer group spectrometer but also on the service 400 MHz and high-field 500/600 MHz spectrometers
* Fast! Doesn't check the whole server every time, so it takes barely a second to check for new spectra
* Crashes much less frequently than `NMRCheck`
* Has a progress bar to show progress
* Looks (and is) much more modern, which makes option selection much less ambiguous (it is clear which has been selected), improving the UX. Also supports dark mode
* Can check for spectra from any chosen date, and only from this date, so won't download hundreds of spectra at once
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

Usage is fairly self-explanatory within the app. When submitting samples to the NMR spectrometers it is important to stick to the rules for naming spectra:

1. Sample names must begin with the group's initialism, followed by the user's, separated by a space
2. The initialisms must be typed in lowercase

If these are followed, the spectrum will be found by Mora the Explorer. Additionally, the NMR department has the rule that:

3. Sample codes should consist of the reaction number followed by a sample number, separated by a hyphen; samples should be simply numbered sequentially
4. Extra letters are allowed only when they occur at the start of the reaction number e.g. to indicate a student on placement/Praktikum

This results in sample names of the form `stu mjm 301-2`, or `stu mjm al-12-1` for reactions run as part of Praktika.

Though the program will successfully find and copy any spectra featuring that match the first two rules, sample numbers are expected in the prescribed format. For example, extra hyphens e.g. `"stu mjm-301-2"` will result in the automatic formatting working less well.


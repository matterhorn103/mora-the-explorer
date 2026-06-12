# mora-the-explorer

A small program written for use at the Organic Chemistry department at the University of Münster.
Mora the Explorer checks a central server for NMR data matching the user's details and automatically saves any new ones to a folder of the user's choosing (e.g. a personal analytics folder).

Bugs can be reported on the [issues tracker](https://github.com/matterhorn103/mora-the-explorer/issues) or by sending an email using the link in the desktop app.

The application is by default configured for use in Münster according to the local conventions, but can easily be reconfigured – see [Configuration](#configuration).

## Features

**Advantages** over the `NMRCheck` program used previously include:
* Can find spectra from both Bruker and Agilent spectrometers, including the department's high-field 500/600 MHz spectrometers
* Fast! Doesn't check the whole server every time
* Checks for spectra from any chosen date, but only from this date, so won't download hundreds of spectra at once
* At the same time, the option exists to check a range of dates in one go
* Can be used to get spectra even months or years after measurement
* Option to keep checking every few minutes (configurable) like `NMRCheck`, but doesn't have to – this saves resources vs `NMRCheck`; the interval is also configurable
* Has a progress bar to show progress and a spinner to show that a check is running
* Looks (and is) much more modern, in particular making option selection much less ambiguous (it is clear which has been selected), improving the UX
* Looks native to the system, and supports dark mode
* Locations are selected using the system file explorer
* Can identify if previously copied spectra are missing files and add the new ones (useful if some error occurred or e.g. when only the proton spectrum of a sample submitted on the high-field spectra was completed on the last check but carbon, COSY etc. have been measured since)
* Whether spectra are copied depends on whether one with the same name exists in the destination, not on whether they were measured before/after the last check
* Extracts key measurement metadata and saves them in a TOML file for easy reading and processing
* Collects Bruker spectra into a single folder per sample, just like Agilent spectra (and Bruker and Agilent measurements for the same sample go into the same folder too)
* Saves spectra with a sensible name including key metadata such as the experiment (proton, 13C etc) so you don't have to rename them yourself – I save directly to my analytics NMR folder
* Configuration saved to a config file which follows the user across different Windows PCs within the uni
* Crashes much less frequently than `NMRCheck`
* Has a better name (possibly most important)


## Installation

Ready-to-use versions for Windows, macOS, and Linux (in the form of executables prepared with PyInstaller or `pyside6-deploy`) are available from this repository's [releases page](https://github.com/matterhorn103/mora-the-explorer/releases) or on the Organic Chemistry department's central NMR server.

If desired, the source code can be downloaded and either run directly with Python or installed.
Our preferred and recommended tool for this is [`uv`](https://github.com/astral-sh/uv).
If uv is installed, using the program is very simple and can be done in a number of ways:

1. The desktop app can be started from the command line using the `launch` command:
   ```bash
   $ uv run mora_the_explorer launch
   ```

2. Checks can be run from the command line using the `check` command:
   ```bash
   $ uv run mora_the_explorer check
   ```
   Use the `--help` option to get more information on command line usage, or see the guide below.

3. Finally, an executable can be prepared from the source code in the same way as is used to create those for the releases page by using `pyinstaller`:
   ```bash
   $ uv sync
   $ uv run pyinstaller install/mora_the_explorer.spec
   ```
   or using `pyside6-deploy`:
   ```bash
   $ uv sync
   $ uv run pyside6-deploy -c install/linux.spec
   ```

If not using uv, it is easiest to install Mora the Explorer as a package (either system-wide or into a Python virtual environment) in the normal way e.g. using `pip`:
```bash
$ pip install .
```
After this, the app can be run from the command line with the `mora-the-explorer` command in a similar way to above e.g.
```bash
$ mora-the-explorer launch
$ mora-the-explorer check
```

## Usage at the university

### NMR sample submission

The first step is of course to actually measure the NMR spectra.
For user-submitted samples measured on the Bruker instruments, Mora the Explorer expects the "title" field of submitted measurements to have been filled out according to the department's rules for sample/measurement names:

1. Sample names must begin with the group's initialism, followed by the user's three-letter initialism, optionally followed by a second user initialism (generally two letters), followed by a sample code, all separated by spaces
2. Sample codes should consist of the reaction number followed by a sample number, separated by a hyphen or a space; samples should be simply numbered sequentially (`-1`, `-2` etc.)

This results in sample names of the forms `stu mjm 301-2`, or `stu mjm 301 2`, or `stu mjm al 12-1` for reactions run as part of Praktika.

The program is fairly tolerant and can account for a variety of common deviations from this scheme, but not abiding by the rules will result in the automatic formatting working less well.


### Initial setup

A connection to the central NMR server should be established as described on the [NMR department's webpage](https://www.uni-muenster.de/Chemie.oc/en/nmr/nmr-service.html).
The app will not work without an active connection to the server and suitable access permissions, so you must be either within the university's intranet or connected to it via a VPN.

Under Windows, the default server location looked for is a Samba address `//samba.public.os.wwu.de/usershare/projects/q_nmr-oc/nmr`, which should resolve automatically when in the university network.

Under macOS and Linux, by default Mora the Explorer expects the server to be accessible at `/Volumes/usershare/projects/q_nmr-oc/nmr` and `~/usershare/projects/q_nmr-oc/nmr` respectively.

If the location on the system is different, it can be changed within the app or in the user configuration file.


### Desktop app

Usage is fairly self-explanatory within the app.
The NMR department has also made a more visual guide available on their [website](https://www.uni-muenster.de/imperia/md/content/organisch_chemisches_institut2/nmr/readme_mora_the_explorer.pdf).

Getting started is simple: open the app, then enter your acronym, select your group, and choose a destination folder (**Save in**) for spectra to be saved to.
Save the options as the defaults so that you don’t have to enter them next time.
Then, after selecting the spectrometer(s) and date(s) to check, start a check using the **Start check now** button.

When a spectrum is found that matches the Query, the app checks in the destination folder to see if the same spectrum has already been copied.
If not, or the existing copy is incomplete, a copy of it will be saved.

#### App options

Note that some options are only available in Advanced Mode (accessed by <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>A</kbd>).

##### Locations
- **NMR server**: Tell the app where to find the connected NMR network drive.

  On Windows this should be automatically set correctly and shouldn’t need to be changed. To change it, click the folder icon.

- **Save in**: Tell the app where to copy spectra to on your PC.

  Click the folder icon to browse to the folder you want to use. Click the **go to** button at any time (or use the shortcut <kbd>Ctrl</kbd>+<kbd>G</kbd>) to quickly open the folder in File Explorer/Finder/etc. to see all your spectra.

##### Search Scope
- **Instrument**: Choose which spectrometers you would like to check.

  “Routine NMR” checks the Bruker instruments, “High-field spectrometers” checks the Agilent ones. The Studer and Naesborg groups have an additional option to check just their own 300 MHz spectrometer, which is faster than checking all the 300 and 400 MHz instruments.

  Note that the availability of some options is deliberately affected by the choice of spectrometer.

- **Date**: Select the date to check.

  The **today** option will always check the current date and changes automatically at midnight. The **only** option allows you to check a single date, specified in the box to the right; the **since** option lets you check every day between the specified date and the current date. Pressing the **refresh** button to the right will set the date back to today’s date.

  Each part of the date can be selected individually and adjusted using the arrows or replaced by typing.

  This should be the date on which the sample was queued for measurement (note that samples placed on a spectrometer on, for example, Monday evening but measured Tuesday morning are therefore considered as belonging to Monday!). 

  The **since** option is designed to allow you to do a one-off check every now and again to make sure you did not forget to download any spectra, but is time-consuming and should not be used regularly.

  Note that when searching the high-field spectrometers only the year must be provided, which will be checked in full, so the exact date of submission is unimportant. Only the year to be checked must be specified.

##### Query
- **Group**: Select your group.

  If you do not see your group, select **other** and then choose your group from the drop-down list below it.

- **Group name**: *Advanced mode only.* Normally, the group name is set automatically based on **Group**. In Advanced Mode, it can be set separately. For convenience, when the identifier of a known group is put into the **Group** field, **Group name** is changed automatically to the corresponding name.

- **User**: Enter your institute-wide user identifier.

- **Sample ID**: *Advanced mode only.* Enter a specific sample to search for.

  Note that sample IDs are normalized by the app before saving, but matches are checked using the original, pre-normalization value, so it must match the string used at submission time.

*Tip for advanced users:* Each of the free text entry fields is processed as regex, so `.*` can be used as a wildcard.
The special extension syntax `\_` can be used to represent any separator character, corresponding to `[\s_-]`

##### Matching Patterns
*Advanced mode only.*

These fields allow an advanced user to specify the regex pattern that measurements should be matched against to determine hits and extract variables.
They are interpreted as normal regex, with two custom extensions:
1. The special extension syntax `\_` can be used to represent any separator character, corresponding to `[\s_-]`
2. Variable names surrounded by angle brackets `<var>` are replaced by named capture groups `(?P<var>…)`, and can be used in the patterns as follows:
   - `<user>` – some value for `user` is expected here and should be extracted;
     becomes a wildcard `(?P<user>\S+)`
   - `<user!>` – adding a `!` *inside* the brackets indicates that the user-specified value of `user` is expected here and is required for a hit; if `user = "abc"`, `<user!>` becomes `(?P<user>abc)`
   - `<user2>?` — everything *outside* the brackets has the usual regex meaning, so adding the `?` indicates that `user2` may or may not be present; becomes `(?P<user2>\S+)?`
   - `<user2!>?` – `!` and `?` in combination like this indicates that the variable may or may not be present, but if it is, it must match; becomes e.g. `(?P<user2>xy)?`

See [Metadata](#metadata) for the available metadata fields that can be used as variables.

Either one or two patterns can be customized in the desktop app (and specified for the spectrometer profile in the configuration file):

- **Sample**: *Advanced mode only.* Only relevant for Agilent spectrometers, that save the spectra organized by sample; this pattern is matched against the sample folder name.
- **Measurement**: *Advanced mode only.* On Agilent spectrometers, this pattern is matched against the measurement folder name. On Bruker spectrometers, it is matched against the "title" that the measurement was submitted with (see [NMR sample submission](#nmr-sample-submission))

##### Scheduling
- **Repeat**: Choose whether to automatically repeat the search at regular intervals.

  For the routine, low-field Bruker spectrometers there is the option to repeat the check automatically at regular intervals. After pressing start, the program will check once and then again every time the specified number of minutes has elapsed. This is somewhat unnecessary, but some users may prefer it.

  This option is not available on the Agilent high-field spectrometers.

##### Buttons
- **Save options as defaults for next time**: Save the current settings to the user configuration file. (See [Configuration](#configuration) for its location.)

  This button only appears after changes have been made to the settings and is otherwise hidden. Clicking it saves the chosen settings so that they are loaded the next time you launch the app.

  Note that the date is not saved; it is always set to the current date by default.

- **Start check now**: Begin a check with the current settings.

  During the check, this button is replaced by a status and progress bar. When the repeat check option is enabled, this button becomes a cancel button between checks.

#### Running a search

1. Click **Start check now** to begin a check.
   - A spinner appears to show you that the app is busy, and a progress bar indicates how many of the current date's spectra have been checked for matches.
   - Any spectrum that matches **Query** (and **Matching Pattern**) will be recognized, but will only actually be copied to the destination folder if there is no spectrum already there with the **same name**.
   - In the very rare case that multiple spectra would have the same generated name, but are truly different, they will be copied but with an additional appended number to distinguish them.
   - Spectra that have been copied before but are incomplete will be supplemented with any additional files found.
   - Spectra folders without an `.fid` file, or whose `.fid` file is empty (smaller than 1 kB) will not be copied.

2. The outcome of the search is shown in the panel underneath. All new spectra found are listed.
   - A green banner will appear to alert you of new spectra, which will remain until dismissed with a click.

3. If the option to repeat the check was selected, another search will be triggered after the specified time has elapsed. The scheduled check can be cancelled by clicking on the red button.


### Command line interface

From the command line, Mora the Explorer can be instructed to carry out a check using:

```bash
mora-the-explorer check [OPTIONS] <group> <user> [<sample>]
```

To get an overview of usage, use `mora-the-explorer check --help`.

For the most part, the same options are available as for the desktop app:
- Locations can be specified using `--remote` and `--dest`
- The instrument/spectrometer group can be specified using `--spec`
- The date to check can be specified using `--date` (defaults to today's date)
- A range of dates can be checked using `--multi`
- The group and user identifiers are specified as required positional arguments
- The sample ID can be specified as an optional positional argument (defaults otherwise to a wildcard)

Like in the desktop app, `group`, `user`, and `sample` are interpreted as regex patterns.

The same user config file (see [Configuration](#configuration)) is used as for the desktop app, so options can be specified there instead.
An alternative config file from another location can be passed to the program using the `--config <path>` option.

Options passed on the command line override any in the config file.

Note that there is no repeat check functionality available via the CLI.

The desktop app can also be started from the command line using `mora-the-explorer launch`.


### Python API

If desired, checks can be set up programmatically from Python relatively easily:

```python
from datetime import date
from pathlib import Path
from mora_the_explorer import Config, Explorer

# Specify a config file containing details of the spectrometers etc.
app_config = Path("./some_config_file.toml")

# Use the default config bundled with the app (requires `pyside6`)
from mora_the_explorer.app import load_compiled_app_config
app_config = load_compiled_app_config()

conf = Config(app_config)  # Load settings for the program
explorer = Explorer(conf)  # Set up the check queuer based on the loaded settings

# Further change config options on the fly if desired
explorer.config.options.group = "stu"
explorer.config.options.user = "mjm"
explorer.config.options.spec = "av300"
explorer.config.options.naming.sample_format = "{user}-{sample_id}-{solvent}"
# Two options are not set in the config files, so they are only ever set temporarily
# and are set programmatically via the `temp` dictionary
explorer.config.options.temp["group_name"] = "mustermann"
explorer.config.options.temp["sample_id"] = r"201-.*"

check_date = date.fromisoformat("2024-07-03")

# Run the check
explorer.single_check(check_date)

# Run a check using a `PrintingReporter` created by default (the argument can
# be omitted as above) and access information on the outcome of the search
reporter = explorer.single_check(check_date, reporter=None)
print(reporter.copied())
print(reporter.messages())
print(reporter.errors())

# The default `PrintingReporter` prints status updates and progress to stdout
# To customize how they are handled, write a custom class that inherits from the
# `Reporter` ABC and pass it to the `Explorer`
from mora_the_explorer.core import Reporter

class CustomReporter(Reporter):
    ...

reporter = CustomReporter()
explorer.single_check(check_date, reporter=reporter)

```

## Configuration

The package/app is configured using a file in TOML format with the following tables:

```toml
[options]
[options.naming]
[appearance]
[paths]
[admin]
[groups]
[groups.other]
[spectrometers.xxx]
[spectrometers.yyy]  # etc. for each spectrometer
```

See the default app config file at `src/mora_the_explorer/config.toml` for an example.

At runtime, two files are consulted:
1. The "app config": `config.toml`, bundled with the app itself, containing default settings
2. The "user config": `config.toml`, in the user's personal data folder, containing personal settings

The app config file is loaded first and is expected to contain a default configuration in full.
The app config generally specifies all the details for how the app should work, e.g. the information about the available groups and spectrometers, as well as a set of default user options.

The user config file is loaded second.
If no user config exists yet on the system, it is first created as a copy of the defaults from the app config.
The user config specifies the options the user sets, such as the user details, the search options, and the save destination.
Most of them can be set in the GUI; a few can only be set in the config file, but are still user-configurable (the naming and appearance options).

The contents of the two files are merged as follows:

The user config usually only contains the `[options]`, `[appearance]`, and `[paths]` tables.
Values specified in these tables take precendence over those in the app config, and override them at launch.

The user config may optionally also contain `[groups]` and `[spectrometers]` tables, though.
Any entries there will *supplement* (rather than replace) those in the app config.

Importantly, the `[admin]` table is only ever read from the app config file.

### The app config file

If you want to configure Mora the Explorer for use at another institution, it is this file that should be changed.

The app config file is located within the source code at `./src/mora_the_explorer/config.toml`, and when running the app from the source code (i.e. with `uv run mora-the-explorer`) this TOML file is directly referenced.

The bundled and compiled versions of the app do not include the TOML file itself, but instead a transpiled version that makes use of Qt's `QResource` system.
Thus, if you make changes to the app config file and want to regenerate the executable versions of the app for distribution, it is crucial to first re-transpile the config by running:

```bash
uv run pyside6-rcc ./src/mora_the_explorer/resources.qrc -o ./src/mora_the_explorer/resources.py
```

### The user config file

The user configuration is stored in the appropriate place for the operating system:
- Windows: `%USERPROFILE%\AppData\Roaming\mora_the_explorer\config.toml`
- macOS: `~/Library/Application Support/mora_the_explorer/config.toml`
- Linux: `$XDG_CONFIG_HOME/mora_the_explorer/config.toml`, defaulting to `~/.config/mora_the_explorer/config.toml`

### Available options

The following key/value pairs can be defined.
All values should be strings unless indicated otherwise.

Note that some options only affect the behaviour of the GUI desktop app.

---

`version` – The config file version (`integer`); if the user config version doesn't match the app config, it is deleted and created afresh

#### `[options]`

`options.user` – The user identifier

`options.group` – The group identifier

`options.spec` – The instrument/spectrometer identifier

Two options only affect the behaviour of the GUI desktop app:

`options.repeat_switch` – Whether to repeat the check (`boolean`)

`options.repeat_delay` – The time that should elapse between repeated checks, in minutes (`integer`)

##### `[options.naming]`
These are `string`s, used to specify the way that the spectra folder names should be formatted when saved in the destination.

`options.naming.sample_format` – The format for the parent folder when organizing by sample

`options.naming.measurement_format` – The format for the spectrum folder

Either can be set separately for Bruker and Agilent spectra, e.g.

`options.naming.measurement_format.bruker`

`options.naming.measurement_format.agilent`

Values of metadata fields are inserted into the names wherever they are enclosed in curly brackets.
For example, the default value for `sample_format` is `"{user}-{user2}-{sample_id}"`

See [Metadata](#metadata) for the available fields.

The names are generated using Python's `str.format()` method, meaning that any format specification from Python's ["format specification mini-language"](https://docs.python.org/3/library/string.html#format-specification-mini-language) can be used. For example, a formatted version of the completion time could be included using `{completion_time:%y%m%d}`

If a requested metadata field is missing, it is omitted.

After substitution of the metadata field values, any spaces are normalized by replacement with underscores.
Additionally, all non-ASCII, non-alphanumerical characters are normalized by replacing them with the Unicode code point prefixed with an `"x"`.

#### `[appearance]`

`appearance.start_button_colour` – The colour to use for the **Start check now** button, as a hex code.

#### `[paths]`

`paths.windows` – The path of the NMR server in the filesystem on Windows

`paths.darwin` – The path of the NMR server in the filesystem on macOS

`paths.linux` – The path of the NMR server in the filesystem on Linux

`paths.src` – The root directory of a copy of Mora the Explorer's source code, relative to the server root; this is referenced when checking for updates

`paths.save` — The location that spectra should be copied to; empty by default, and then if a check is started without a location specified, the user is prompted to select one

#### `[admin]`

`admin.pattern_separator` – This defines the meaning of `\_` in the places where regex is allowed (see [Query](#query) and [Match Patterns](#match-patterns)), and is by default `'[\s_-]'`; it is recommended to use single quotes here, which in TOML is syntax for a literal string, so that backslashes do not need to be escaped

`admin.version` – The version of the app; should not be changed independently, and must always be the same as the value in `pyproject.toml`

`admin.email` – The email address that an email should be sent to for bug reports, used by the **Report a bug** link in the app

`admin.changelog` – Release notes for the current version, which are shown to the user when a new version of the app is found on the server during startup

#### `[groups]`

This specifies the available groups as a table of key/value pairs in the style `group = group_name`.

In Münster:
- `group` is the standard identifier used for each group's experiments and data institute-wide and is used in the search for Bruker spectra (where it must be included in the measurement title)
- `group_name` is the full name, used for directories of the group's spectra on the server e.g. for the high-field spectrometers

The groups specified here appear as dedicated radio buttons in the app.

##### `[groups.other]`

This is another table of `group = group_name` pairs, but these groups do not receive dedicated radio buttons of their own; instead, they are listed in the overflow drop-down list available by choosing **other**.

#### `[spectrometers]`

This is a table of tables, where each sub-table specifies a "spectrometer profile".
A profile indicates to the app how the data of a spectrometer or set of spectrometers should be handled when searching through it.
The set of profiles is then the set of options available for the user to choose from in the app under [Search Scope](#search-scope).

The key of a sub-table is an identifier that is used to refer to the spectrometer(s) in the CLI and within the Python code, but it is not exposed to the user in the GUI at all.
It can be any arbitrary string, but it must be unique within `[spectrometers]`.

An example spectrometer profile:

```toml
[spectrometers.hf]
manufacturer = "agilent"
display_name = "High-field spectrometers (500 && 600 MHz)"
sample_pattern = '<user!><user2!>?<sample_id!>'
measurement_pattern = '<user!><user2!>?<sample_id!>_(\d{6})_<temperature>k_<experiment>_<measurement_no>\.fid'
date_entry = "yyyy"
check_paths = [
    "500-600er/{group_name}/{date:%Y}",
]
archives = [
    "archiv/500-600er/{group_name}/{date:%Y}",
]
single_check_only = true
```

The following key/value pairs can be specified in each sub-table (`id` would be replaced by the spectrometer profile's identifier):

`spectrometers.id.manufacturer` – *Required.* The manufacturer of the spectrometer(s), either `"agilent"` or `"bruker"`

`spectrometers.id.display_name` – *Required.* The text to show next to the profile's radio button in the desktop app (note that as a quirk of Qt, ampersands must be escaped, so write `&&` to get &)

`spectrometers.id.sample_pattern` — *Required for Agilent; optional for Bruker* The expected fields in the sample folder name as regex (Agilent only); see [Match Patterns](#match-patterns) for details

`spectrometers.id.measurement_pattern` – *Required.* The expected fields in the measurement title (Bruker) or measurement folder name (Agilent); see [Match Patterns](#match-patterns) for details

`spectrometers.id.date_entry` – *Required.* The format for the date selection box in the desktop app (see [the Qt documentation](https://doc.qt.io/qt-6/qdatetimeedit.html#displayFormat-prop) for details); for example, if the user should select the full date use `"dd MMM yyyy"`, if just the year then `"yyyy"`

`spectrometers.id.check_paths` – *Required.* A list of paths, relative to the root of the server, that should be searched for new spectra when this spectrometer profile is selected; see [below](#check-and-archive-syntax) for syntax details 

`spectrometers.id.archives` – *Optional.* A list of additional paths that should supplement `check_paths` when checking years prior to the current year; see [below](#check-and-archive-syntax) for syntax details

`spectrometers.id.include` – *Optional.* A list of identifiers of other spectrometer profiles which should also be searched whenever this profile is chosen

`spectrometers.id.restrict_to` – *Optional.* A list of `group` identifiers for groups that should be able to see and choose the spectrometer profile in the GUI; if this key is not specified, the spectrometer will be visible to all groups

`spectrometers.id.admin_only` – *Optional.* (`boolean`) Whether the spectrometer should only be visible and chooseable in advanced mode

`spectrometers.id.single_check_only` – *Optional.* (`boolean`) Whether users are restricted to single day, non-repeating checks, or whether they may use multiday and repeat checks with this spectrometer profile


##### Check and archive path syntax

When specifying (as strings) the paths containing the spectra for a spectrometer profile, the values of a few variables can be used.

Values of the variables are interpolated into the paths wherever they are enclosed in curly brackets, with the following variables available:

- `date` – The date requested by the user to be checked, which in Münster corresponds to the submission date (not the completion date)
- `group` – The identifier of the group specified by the user
- `group_name` – The corresponding full name of the group specified by the user

The replacement is done using Python's `str.format()` method, meaning that any format specification from Python's ["format specification mini-language"](https://docs.python.org/3/library/string.html#format-specification-mini-language) can be used.
For example, the year component of the date can be included using `{date:%Y}`


## Metadata

The following metadata fields are extracted currently:

``` python
METADATA_DTYPES = {
    "path": str,  # The full path in the filesystem and therefore system-specific
    "folder_name": str,
    "manufacturer": Manufacturer,  # "agilent" or "bruker"
    "submission_time": datetime.datetime,  # Written to file in ISO format
    "completion_time": datetime.datetime,  # Written to file in ISO format
    "title": str,
    "sample_id": str,
    "user": str,
    "user2": str,
    "user_name": str,
    "group": str,
    "group_name": str,
    "experiment": str,
    "instrument": str,
    "frequency": float,
    "solvent": str,
    "temperature": int,  # In kelvin
    "measurement_no": int,  # `expno` for Bruker spectra, a disambiguating serial number for Agilent spectra
}
```

Note that not all metadata is extracted on all spectrometers, and may not always be available for use in folder names (in which case, it is simply left out).

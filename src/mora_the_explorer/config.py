from dataclasses import dataclass
import dataclasses
import json
import logging
from pathlib import Path
import tomllib
import tomli_w
import platformdirs

from .spec import Manufacturer, Spectrometer


# Dataclasses that hold the configuration in a structured fashion

@dataclass
class UserOptions:
    user: str
    user_name: str
    group: str
    inc_user: bool
    inc_solv: bool
    inc_path: bool
    spec: str
    repeat_switch: bool
    repeat_delay: int

@dataclass
class Appearance:
    start_button_colour: str

@dataclass
class Paths:
    windows: str
    darwin: str
    linux: str
    update: str  # Relative to the server paths
    save: str

@dataclass
class Groups:
    groups: dict[str, str]  # A dict of `group: group_name` pairs (where `group` is the group's ID)
    overflow: list[str]  # Those groups that should be put into an overflow menu

class Config:
    """A container for the combined app and user configuration data.

    The configuration files are TOML files with the following tables of key/value pairs:

    ```toml
    [options]
    [appearance]
    [paths]
    [groups]
    [groups.other]
    [spectrometers.xxx]
    [spectrometers.yyy]  # etc. for each spectrometer
    ```

    At runtime, two files are consulted:
    1. The "app config": a `config.toml` in the app's resources directory, with default settings
    2. The "user config": a `config.toml` in the user's personal data folder, with personal settings

    The contents of the two files are merged upon loading, with anything in the
    user config taking priority over the app config.

    The user config usually only has the tables containing the options the user
    sets, such as search options and save destination. It may contain any of the
    above tables, though.

    The app config generally specifies all the other details for how the app should
    work, e.g. the information about the available groups and spectrometers, as well
    as the default user options.

    Calling `Config.save()` saves the `[options]`, `[appearance]`, and `[paths]`
    tables to the user config file (while also retaining anything else that was
    already present in the file).

    At program start, both the app config and user config are loaded from their
    files, and the user config is saved once so that anything present in `[options]`
    in the app config but missing in the user config is added to the user config
    file.
    """

    def __init__(self, app_config_file: Path, user_config_file: Path | None = None):
        # Load app config from config.toml
        self.app_config = self.load_config_toml(app_config_file)
        logging.info(f"App configuration loaded from: {app_config_file}")

        # Load or create user config
        # By default check the place appropriate to the os for the config file, which
        # should be:
        # Windows:  c:/Users/<user>/AppData/Roaming/mora_the_explorer/config.toml
        # macOS:    /Users/<user>/Library/Application Support/mora_the_explorer/config.toml
        # Linux:    /home/<user>/.config/mora_the_explorer/config.toml
        if user_config_file is None:
            self.user_config_file = (
                Path(
                    platformdirs.user_config_dir(
                        "mora_the_explorer",
                        roaming=True,
                        ensure_exists=True,
                    )
                )
                / "config.toml"
            )
        else:
            self.user_config_file = user_config_file

        # Extract the parts of the configuration from the app config
        self.options = UserOptions(**(self.app_config["options"]))
        self.appearance = Appearance(**(self.app_config["appearance"]))
        self.paths = Paths(**(self.app_config["paths"]))
        # Flatten the list of groups
        all_groups: dict = self.app_config["groups"].copy()
        if "other" in all_groups:
            other = all_groups.pop("other")
            all_groups.update(other)
        self.groups = Groups(all_groups, other.keys())
        specs = self.app_config["spectrometers"].copy()
        for spec in specs:
            specs[spec]["manufacturer"] = Manufacturer.from_str(specs[spec]["manufacturer"])
        self.specs = {k: Spectrometer(**v) for k, v in specs.items()}

        # Load user config from config.toml in user's config directory
        if self.user_config_file.exists():
            self.user_config = self.load_config_toml(self.user_config_file)
            logging.info(f"User configuration loaded from: {self.user_config_file}")
        # User options used to be stored in config.json pre v1.7, so also check for it
        elif self.user_config_file.with_name("config.json").exists():
            self.user_config = self.load_user_config_json(
                self.user_config_file.with_name("config.json")
            )
            logging.info("Old config.json found, read, and converted to config.toml")
        else:
            self.user_config = {}

        # Merge anything in the user config in, takes priority over app config
        for k, v in self.user_config.get("options", {}).items():
            setattr(self.options, k, v)
        for k, v in self.user_config.get("appearance", {}).items():
            setattr(self.options, k, v)
        for k, v in self.user_config.get("paths", {}).items():
            setattr(self.options, k, v)
        # Groups is extended, with no support for an "other" subcategory
        self.groups.groups.update(self.user_config.get("groups", {}))
        # Spectrometer selection is also simply updated
        self.specs.update(self.user_config.get("spectrometers", {}))

        # Save the user config to file
        self.user_config_file.parent.mkdir(parents=True, exist_ok=True)
        self.save()

    def load_config_toml(self, path: Path):
        """Load a config from a TOML file."""
        with open(path, "rb") as f:
            config = tomllib.load(f)
        return config

    def load_user_config_json(self, path: Path):
        """Load a user's config from a JSON file."""
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
        return config

    def save(self, path: Path | None = None):
        """Save the user config to file.

        The following parts are always included: options, appearance, paths
        These are saved to be identical to the overall config, i.e. after the
        app and user configs have been merged.

        Other parts are not supplemented by the current config, but they are
        preserved if they were already in the file.

        If no path is provided, it defaults to the current value of `user_config_file`.
        """
        if path is None:
            path = self.user_config_file
        current_config = {
            "options": dataclasses.asdict(self.options),
            "appearance": dataclasses.asdict(self.appearance),
            "paths": dataclasses.asdict(self.paths),
        }
        # Make a new dict, with the originally loaded config as its basis, updated
        # with values from the current merged config
        to_save: dict[str, dict] = self.user_config | current_config

        # Catch some obsolete things
        for old_option in [
            "dest_path",  # Is now `paths.save`
            "initials",  # Is now `options.user`
        ]:
            to_save["options"].pop(old_option, None)
        for old_path in [
            "Windows",  # Is now `paths.windows`
            "Darwin",  # Is now `paths.darwin`
            "Linux",  # Is now `paths.linux`
        ]:
            to_save["paths"].pop(old_path, None)

        with open(path, "wb") as f:
            tomli_w.dump(to_save, f)
        
        logging.info(f"The following user options were saved to {path}:")
        logging.info(self.user_config)

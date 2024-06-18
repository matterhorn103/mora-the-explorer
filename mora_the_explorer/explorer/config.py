from copy import copy
import json
import logging
from pathlib import Path
import tomllib
import tomli_w
import platformdirs


class Config:
    """Returns a container for the combined app and user configuration data.
    
    A Config object contains two kinds of config: a `user_config` and an `app_config`.

    Both are Python dictionaries with the same structures as `config.toml`, which
    currently has the following tables of key/value pairs:

    ```toml
    [options]  # or [default_options] in the defaults file
    [paths]
    [groups]
    [groups.other]
    [spectrometers.xxx]
    [spectrometers.yyy]  # etc. for each spectrometer
    ```

    The app's resources directory contains a `config.toml` holding all the default app
    settings, and a second `config.toml` gets saved to a sensible location on the user's
    system to store their personal choices.

    The `user_config` usually only has the `[options]` table from `config.toml`,
    containing the options the user sets, such as search options and save
    destination. It may contain any of the above tables, though. Any missing entries in
    the `[options]` table are filled from the `[default_options]` table in the defaults
    `config.toml` file.

    The `app_config` specifies the other details for how the app should work, e.g. the
    information about the available groups and spectrometers, as well as the default
    user options.

    At program start, both the app config and user config are loaded from their files,
    anything in `user_config` is put into `app_config`, overwriting where appropriate,
    and anything missing from `user_config["options"]` is filled from
    `app_config["default_options"]`. After this, there is no further interaction
    between the two configs; only `user_config` changes during runtime due to the user's
    actions, while `app_config` stays static.

    Calling `Config.save()` saves `user_config` to file, not the `app_config`.
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
            self.user_config_file = Path(platformdirs.user_config_dir(
                    "mora_the_explorer",
                    roaming=True,
                    ensure_exists=True,
                )
            ) / "config.toml"
        else:
            self.user_config_file = user_config_file

        # Load user config from config.toml in user's config directory
        if self.user_config_file.exists() is True:
            self.user_config = self.load_config_toml(self.user_config_file)
            logging.info(f"User configuration loaded from: {self.user_config_file}")
            self.extend_user_config(self.user_config, self.app_config)
            # Update any app settings specified in the user config
            self.update_app_config(self.user_config)

        # User options used to be stored in config.json pre v1.7, so also check for it
        elif self.user_config_file.with_name("config.json").exists() is True:
            self.user_config = self.load_user_config_json(
                self.user_config_file.with_name("config.json")
            )
            logging.info("Old config.json found, read, and converted to config.toml")
            self.extend_user_config(self.user_config, self.app_config)
        
        # If no user config file exists, make one and save it
        else:
            self.user_config = {"options": {}}
            self.extend_user_config(self.user_config, self.app_config)
            logging.info("New default user config created with default options")
            self.user_config_file.parent.mkdir(parents=True, exist_ok=True)
            self.save()

        # Expose some parts of user and app configs at top level
        self.options = self.user_config["options"]
        self.paths = self.app_config["paths"]
        self.groups = self.app_config["groups"]
        self.specs = self.app_config["spectrometers"]


    def load_config_toml(self, path: Path):
        """Load a config from a TOML file."""

        with open(path, "rb") as f:
            config = tomllib.load(f)
        return config


    def load_user_config_json(self, path: Path):
        """Load a user's config from a JSON file and replace it with a TOML."""

        with open(path, encoding="utf-8") as f:
            old_options = json.load(f)
        # Add new options
        config = {
            "options": old_options,
            "paths": {"linux": "overwrite with default mount point"},
        }
        with open(self.user_config_file, "wb") as f:
            tomli_w.dump(config, f)
        # Remove old json to avoid confusion
        path.unlink()
        return config


    def extend_user_config(self, user_config, app_config):
        """Make sure the user's config contains everything it needs to by default."""

        # First just anything in the default options table
        for option in app_config["default_options"]:
            if option not in user_config["options"]:
                user_config["options"][option] = app_config["default_options"][option]
        # Then anything from other tables that needs to be present i.e. anything for
        # which it should be made obvious to the user that it can be configured
        if "paths" in user_config:
            if "linux" in user_config["paths"]:
                pass
        else:
            user_config["paths"] = {}
            user_config["paths"]["linux"] = "overwrite with default mount point"

    
    def update_app_config(self, config: dict):
        """Overwrite any app config settings that are specified in the given config."""
        # NOTE: Only works properly for a couple of nesting levels
        for table in config:
            if table in self.app_config:
                for k, v in config[table].items():
                    logging.info(
                        f"Updating default app config option `[{table}] {k} = {repr(self.app_config[table].get(k))}` with value {repr(v)} from provided config.toml"
                    )
                    # Make sure tables within tables are only updated, not overwritten
                    if isinstance(v, dict):
                        self.app_config[table][k].update(v)
                    else:
                        self.app_config[table][k] = v


    def save(self, path: Path | None = None):
        """Save user config to file.
        
        If no path is provided, it defaults to the current value of `user_config_file`.
        """
        if path is None:
            path = self.user_config_file
        with open(path, "wb") as f:
            tomli_w.dump(self.user_config, f)
        logging.info(
            f"The following user options were saved to {path}:"
        )
        logging.info(self.user_config)

from copy import copy
import json
import logging
from pathlib import Path
import tomllib
import tomli_w
import platformdirs


class Config:
    """Returns a container for the combined app and user configuration data."""

    def __init__(self, resource_directory):
        self.rsrc_dir = resource_directory

        # Load app config from config.toml
        with open(self.rsrc_dir / "config.toml", "rb") as f:
            self.app_config = tomllib.load(f)
            logging.info(
                f"App configuration loaded from: {self.rsrc_dir / "config.toml"}"
            )

        # Load user config from config.toml in user's config directory
        # Make one if it doesn't exist yet

        # Config should be saved to:
        # Windows:  c:/Users/<user>/AppData/Roaming/mora_the_explorer/config.toml
        # macOS:    /Users/<user>/Library/Application Support/mora_the_explorer/config.toml
        # Linux:    /home/<user>/.config/mora_the_explorer/config.toml

        # User options used to be stored in config.json pre v1.7, so also check for that
        # platformdirs automatically saves the config file in the place appropriate to the os
        self.user_config_file = Path(platformdirs.user_config_dir(
                "mora_the_explorer",
                roaming=True,
                ensure_exists=True,
            )
        ) / "config.toml"
        user_config_json = self.user_config_file.with_name("config.json")
        if self.user_config_file.exists() is True:
            with open(self.user_config_file, "rb") as f:
                self.user_config = tomllib.load(f)
            logging.info(f"User configuration loaded from: {self.user_config_file}")
        elif user_config_json.exists() is True:
            # Load json, save as toml instead, remove old json to avoid confusion
            with open(user_config_json, encoding="utf-8") as f:
                old_options = json.load(f)
            # Add new options
            self.user_config = {
                "options": old_options,
                "paths": {"Linux": "overwrite with default mount point"},
            }
            with open(self.user_config_file, "wb") as f:
                tomli_w.dump(self.user_config, f)
            user_config_json.unlink()
            logging.info("Old config.json found, read, and converted to config.toml")
        else:
            # Create config containing only options and any other things that should be made
            # obvious to the user that they can be configured
            self.user_config = {
                "options": copy(self.app_config["default_options"]),
                "paths": {"Linux": "overwrite with default mount point"},
            }
            self.user_config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_config_file, "wb") as f:
                tomli_w.dump(self.user_config, f)
            logging.info("New default user config created with default options")

        # Overwrite any app config settings that have been specified in the user config
        # Only works properly for a couple of nesting levels
        for table in self.user_config.keys():
            if table in self.app_config:
                for k, v in self.user_config[table].items():
                    logging.info(
                        f"Updating default app_config option `[{table}] {k} = {repr(self.app_config[table][k])}` with value {repr(v)} from user's config.toml"
                    )
                    # Make sure tables within tables are only updated, not overwritten
                    if isinstance(v, dict):
                        self.app_config[table][k].update(v)
                    else:
                        self.app_config[table][k] = v

        # Expose some parts of user and app configs at top level
        self.options = self.user_config["options"]
        self.paths = self.app_config["paths"]
        self.groups = self.app_config["groups"]
        self.specs = self.app_config["spectrometers"]

    def save(self):
        # Save user config to file
        with open(self.user_config_file, "wb") as f:
            tomli_w.dump(self.user_config, f)
        logging.info(
            f"The following user options were saved to {self.user_config_file}:"
        )
        logging.info(self.user_config)

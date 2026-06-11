"""The main entry point when mora_the_explorer is used on the command line."""

import argparse
import logging
from datetime import date
from pathlib import Path
import sys

from . import LOG_FILE, USER_CONFIG_PATH, Config, Explorer, get_rsrc_dir


def main():
    """Run Mora the Explorer as a CLI program."""

    app_config_file = get_rsrc_dir() / "config.toml"
    default_config = Config(app_config_file, USER_CONFIG_PATH)

    parser = argparse.ArgumentParser(
        prog="mora_the_explorer",
        description=f"user config is being loaded automatically from {USER_CONFIG_PATH}",
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")

    check_parser = subparsers.add_parser(
        "check",
        help="run a check from the command line",
        description=f"user defaults are being loaded automatically from {USER_CONFIG_PATH}",
        epilog="options and flags passed on the command line override the user config",
    )
    interactive_parser = subparsers.add_parser(
        "launch",
        help="launch the desktop app",
    )

    parser.add_argument(
        "-c",
        "--config",
        action="store",
        help="reconfigure with a provided TOML file CONFIG",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=f"print log entries to stderr (as well as {LOG_FILE})",
    )

    interactive_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=f"print log entries to stderr (as well as {LOG_FILE})",
    )

    check_parser.add_argument(
        "group",
        action="store",
        help=f"the group initialism (supports regex) {{{', '.join(default_config.groups.all.keys())}}}",
    )
    check_parser.add_argument(
        "user",
        action="store",
        help="the user's initialism (supports regex)",
    )
    check_parser.add_argument(
        "sample",
        action="store",
        nargs="?",
        default=r"\d.*",
        help=r"a specific sample to search for (supports regex) (optional, default is a '\d.*' wildcard)",
    )
    check_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=f"print log entries to stderr (as well as {LOG_FILE})",
    )
    check_parser.add_argument(
        "-c",
        "--config",
        action="store",
        help="configure with a provided TOML file CONFIG",
    )
    check_parser.add_argument(
        "-d",
        "--date",
        action="store",
        default=date.today().isoformat(),
        help=f"check DATE (default is today's date: {date.today()})",
    )
    check_parser.add_argument(
        "-m",
        "--multi",
        action="store",
        help="check all dates from MULTI to DATE inclusive",
    )
    check_parser.add_argument(
        "-s",
        "--spec",
        action="store",
        help=f"check spectrometer SPEC {{{', '.join(default_config.specs.keys())}}}",
    )
    check_parser.add_argument(
        "--remote",
        action="store",
        help="search server at REMOTE for spectra",
    )
    check_parser.add_argument(
        "--dest",
        action="store",
        help="copy spectra to DEST",
    )

    args = parser.parse_args()

    if args.verbose:
        # Logs should be additionally printed directly to stderr
        logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))

    # Launch desktop app if requested
    if args.command == "launch":
        logging.info("Launching GUI from command line")
        from .desktop import App

        if args.config:
            app = App(app_config_file, args.config)
        else:
            app = App(app_config_file)
        app.run()
        # Event loop will continue until the program is closed
        return
    elif args.command == "check":
        logging.info("Running check from command line")
        if args.config:
            # Load provided config
            config = Config(app_config_file, Path(args.config))
        else:
            config = default_config
    else:
        parser.print_help()
        return

    # Group and user are mandatory fields
    config.options.group = args.group
    config.options.user = args.user

    # Sample always has at least a default value
    config.options.temp["sample_id"] = args.sample

    # Overwrite options if provided
    if args.remote:
        config.paths.set_server(args.remote)
    if args.dest:
        config.paths.save = args.dest
    if args.spec:
        config.options.spec = args.spec

    explorer = Explorer(config)

    if args.multi:
        explorer.multiday_check(
            initial_date=date.fromisoformat(args.multi), final_date=date.fromisoformat(args.date)
        )
    else:
        explorer.single_check(date=date.fromisoformat(args.date))


if __name__ == "__main__":
    main()

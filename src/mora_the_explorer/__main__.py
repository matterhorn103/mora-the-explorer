"""The main entry point when mora_the_explorer is used on the command line."""

import argparse
import logging
from datetime import date
from pathlib import Path
import sys

from . import LOG_FILE, USER_CONFIG_PATH, Config, Explorer, get_rsrc_dir


def main():
    """Run Mora the Explorer as a CLI program."""

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
        help=f"print log entries to stdout instead of {LOG_FILE}"
    )

    interactive_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=f"print log entries to stdout instead of {LOG_FILE}"
    )

    check_parser.add_argument(
        "group",
        action="store",
        help="the group initialism",
    )
    check_parser.add_argument(
        "user",
        action="store",
        help="the user's initialism",
    )
    check_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=f"print log entries to stdout instead of {LOG_FILE}"
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
        help=f"check DATE (default is today's date: {date.today()})",
    )
    check_parser.add_argument(
        "-m",
        "--multi",
        action="store",
        help="check all dates since MULTI; if this option is passed, --date is ignored",
    )
    check_parser.add_argument(
        "-s",
        "--spec",
        action="store",
        help="check spectrometer SPEC",
    )
    check_parser.add_argument(
        "--dest",
        action="store",
        help="copy spectra to DEST",
    )
    check_parser.add_argument(
        "-u",
        "--inc-user",
        action="store_true",
        help="include user initials in copied folder name",
    )
    check_parser.add_argument(
        "--no-user",
        action="store_true",
        help="do NOT include user initials in copied folder name",
    )
    check_parser.add_argument(
        "-l",
        "--inc-solvent",
        action="store_true",
        help="include solvent in copied folder name",
    )
    check_parser.add_argument(
        "--no-solvent",
        action="store_true",
        help="do NOT include solvent in copied folder name",
    )

    args = parser.parse_args()

    if args.verbose:
        # Logs should be printed directly to stdout
        logging.basicConfig(
            stream=sys.stdout,
            format="%(asctime)s %(message)s",
            encoding="utf-8",
            level=logging.INFO,
        )
    else:
        logging.basicConfig(
            filename=LOG_FILE,
            filemode="w",
            format="%(asctime)s %(message)s",
            encoding="utf-8",
            level=logging.INFO,
        )
    
    app_config = get_rsrc_dir() / "config.toml"
    if args.config:
        # Load provided config
        config = Config(app_config, Path(args.config))
    else:
        config = Config(app_config, USER_CONFIG_PATH)

    # Launch desktop app if requested
    if args.command == "launch":
        logging.info("Launching GUI from command line")
        from .desktop import App
        app = App(config)
        app.run()
        # Event loop will continue until the program is closed
        return
    elif args.command == "check":
        pass
    else:
        parser.print_help()
        return

    # Group and user are mandatory fields
    # Let user use wild group
    if args.group == "*":
        config.options.group = ""
    else:
        config.options.group = args.group
    
    if args.user == "*":
        config.options.user = ""
    else:
        config.options.user = args.user

    # Overwrite options if provided
    if args.dest:
        config.paths.save = args.dest
    if args.spec:
        config.options.spec = args.spec
    if args.inc_user:
        config.options.inc_user = True
    if args.no_user:
        config.options.inc_user = False
    if args.inc_solvent:
        config.options.inc_solv = True
    if args.no_solvent:
        config.options.inc_solv = False

    explorer = Explorer(config)

    if args.multi:
        explorer.multiday_check(initial_date=date.fromisoformat(args.multi))
    elif args.date:
        explorer.single_check(date=date.fromisoformat(args.date))
    else:
        explorer.single_check(date=date.today())


if __name__ == "__main__":
    main()

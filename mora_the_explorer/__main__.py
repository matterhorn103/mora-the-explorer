"""The main entry point when mora_the_explorer is used on the command line."""

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

from . import cli
from .explorer import app


def main():
    """Run Mora the Explorer as a CLI program."""

    # Logs should be printed directly to stdout
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s %(message)s",
        encoding="utf-8",
        level=logging.INFO,
    )

    rsrc_dir = Path.cwd()
    explorer = cli.setup_command_line_explorer(rsrc_dir)
    prog_bar = cli.TerminalProgress()

    parser = argparse.ArgumentParser(
        prog="mora_the_explorer",
        description=f"user config is being loaded automatically from {explorer.config.user_config_file}",
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")

    check_parser = subparsers.add_parser(
        "check",
        help="run a check from the command line",
        description=f"user defaults are being loaded automatically from {explorer.config.user_config_file}",
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
        help=f"check only spectrometer SPEC (user default: {explorer.config.options["spec"]})",
    )
    check_parser.add_argument(
        "--dest",
        action="store",
        help=f"copy spectra to DEST (user default: {explorer.config.options["dest_path"]})",
    )
    check_parser.add_argument(
        "--initials",
        action="store_true",
        help=f"include initials in copied folder name (user default: {explorer.config.options["inc_init"]})",
    )
    check_parser.add_argument(
        "--no-initials",
        action="store_true",
        help="do NOT include initials in copied folder name",
    )
    check_parser.add_argument(
        "--solvent",
        action="store_true",
        help=f"include solvent in copied folder name (user default: {explorer.config.options["inc_solv"]})",
    )
    check_parser.add_argument(
        "--no-solvent",
        action="store_true",
        help="do NOT include solvent in copied folder name",
    )

    args = parser.parse_args()

    if args.config:
        # Replace previously loaded user config with provided one
        explorer.config.user_config = explorer.config.load_config_toml(Path(args.config))
        # Overwrite any app settings
        explorer.config.update_app_config(explorer.config.user_config)
        # Make sure the Explorer is appropriately configured as a result
        explorer.reload_config()
    
    # Launch desktop app if requested
    if args.command == "launch":
        logging.info("Launching GUI from command line")
        from . import run_desktop_app
        run_desktop_app(rsrc_dir, explorer)
    
    elif args.command == "check":
        args = parser.parse_args()

        # Group and user are mandatory fields
        explorer.config.options["group"] = args.group
        # Let user use wild group
        if args.user[:2] == "*":
            explorer.config.options["initials"] = args.user[1:].lstrip()
            wild_group = True
        else:
            explorer.config.options["initials"] = args.user
            wild_group = False

        # Overwrite options if provided
        if args.spec:
            explorer.config.options["spec"] = args.spec
        if args.dest:
            explorer.config.options["dest_path"] = args.dest
        if args.initials:
            explorer.config.options["inc_init"] = True
        if args.no_initials:
            explorer.config.options["inc_init"] = False
        if args.solvent:
            explorer.config.options["inc_solv"] = True
        if args.no_solvent:
            explorer.config.options["inc_solv"] = False

        # Have to make sure explorer is passed as an argument to the handler even though
        # the completed signal only sends one argument (copied_list)
        # Also pass progress bar so it can be set to 100% on completion
        if args.multi:
            explorer.multiday_check(
                initial_date=date.fromisoformat(args.multi),
                wild_group=wild_group,
                prog_bar=prog_bar,
                completion_handler=lambda copied_list: cli.cli_completion_handler(explorer, copied_list, prog_bar),
            )
        elif args.date:
            explorer.single_check(
                date=date.fromisoformat(args.date),
                wild_group=wild_group,
                prog_bar=prog_bar,
                completion_handler=lambda copied_list: cli.cli_completion_handler(explorer, copied_list, prog_bar),
            )
        else:
            explorer.single_check(
                date=date.today(),
                wild_group=wild_group,
                prog_bar=prog_bar,
                completion_handler=lambda copied_list: cli.cli_completion_handler(explorer, copied_list, prog_bar),
            )
        
        app().exec()


if __name__ == "__main__":
    main()

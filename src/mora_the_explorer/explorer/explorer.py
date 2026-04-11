import logging
import platform
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import QThreadPool

from .appmanager import app
from ..config import Config
from .worker import Worker
from ..check import get_check_paths, Manufacturer, check_nmr, MetadataRules


class Explorer:
    """Launches checks based on a given `Config` object.

    Serves as a task queuer as well as an interpreter between a configuration and the
    `check_nmr` function.
    """

    def __init__(self, config: Config | None = None):
        if config:
            self.configure(config)
        else:
            self.config = None
            self.server_path = None
            self.specs = None
            self.all_groups = None

        # Set up multithreading; MaxThreadCount limited to 1 as checks don't run
        # properly if multiple run concurrently
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        # Initialize number of queued checks
        self.queued_checks = 0

    def configure(self, config: Config):
        """Configure the Explorer with the provided `Config` object."""
        self.config = config
        self.reload_config()

    def reload_config(self):
        """Refresh the Explorer's attributes to match the current config.

        This should not generally be necessary during runtime, as the attributes
        concerned are things that are on the whole constant.
        Changes to user options are picked up on automatically and do not require a
        reload.
        """
        # Set path to server
        self.server_path = Path(self.config.paths[platform.system().lower()])

        # Load group and spectrometer info
        # Need to flatten groups dict (as some are in e.g. an "other" subdict)
        self.all_groups = {}
        for k, v in self.config.groups.items():
            if isinstance(v, str):
                self.all_groups[k] = v
            elif isinstance(v, dict):
                self.all_groups.update(v)
        self.specs = self.config.specs

    def generate_rules(self) -> MetadataRules:
        """Generate metadata handling rules based on the curent configuration."""
        options = self.config.options
        selected_spec = options["spec"]
        spec_info = self.specs[selected_spec]
        # Put together the way the folder names should be formatted
        if options["inc_init"]:
            name_format = ["user", "sample_info", "experiment"]
        else:
            name_format = ["sample_info", "experiment"]
        if options["inc_solv"]:
            name_format.append("solvent")
        if options["inc_path"]:
            name_format.append("folder_name")
        # Always include the frequency info too if it's available
        name_format.append("frequency")
        rules = MetadataRules(
            src_fields=spec_info.title_format,
            conditions={
                "user": options["user"],
                "group": options["group"],
            },
            dest_fields=name_format,
        )
        return rules

    def single_check(
        self,
        date: date,
        prog_bar=None,
        status_bar=None,
        completion_handler: callable | None = None,
    ):
        """Conduct a check of a single date."""
        if status_bar is not None:
            # Hide start button, show status bar
            status_bar.show_status()

        # Handlers for updating progress and status
        def update_progress(prog_state):
            if prog_bar:
                prog_bar.setValue(prog_state)
            else:
                print(prog_state)

        def set_max_progress(max_prog):
            if prog_bar:
                prog_bar.setMaximum(max_prog)

        def update_status(status):
            if status_bar:
                status_bar.setText(status)
            else:
                print(status)

        paths = get_check_paths(
            specs_info=self.specs,
            spec=self.config.options["spec"],
            server_path=self.server_path,
            check_date=date,
            groups=self.all_groups,
        )

        # Default to using own built-in handler for completion
        if completion_handler is None:
            completion_handler = self.completion_handler
        # Start main checking function in worker thread
        options = self.config.options
        rules = self.generate_rules()
        worker = Worker(
            check_nmr,
            src=paths,
            dest=options["dest_path"],
            rules=rules,
            manufacturer=Manufacturer.from_str(self.specs[options["spec"]]),
            date=date,
        )
        worker.reporter.signals.update_progress.connect(update_progress)
        worker.reporter.signals.set_max_progress.connect(set_max_progress)
        worker.reporter.signals.set_status.connect(update_status)
        worker.reporter.signals.completed.connect(completion_handler)
        self.threadpool.start(worker)
        self.queued_checks += 1

    def multiday_check(
        self,
        initial_date: date,
        prog_bar=None,
        status_bar=None,
        completion_handler: callable | None = None,
    ):
        """Check multiple days in sequence."""

        end_date = date.today() + timedelta(days=1)
        date_to_check = initial_date
        while date_to_check != end_date:
            self.single_check(
                date_to_check,
                prog_bar,
                status_bar,
                completion_handler,
            )
            date_to_check += timedelta(days=1)

    def completion_handler(self, copied_list):
        """The default handler for a completed check."""

        self.queued_checks -= 1
        # Display output
        for entry in copied_list:
            print(entry)
        # Task is complete only if all queued checks have finished
        if self.queued_checks == 0:
            print("Task complete")
            logging.info("Task complete")
            app().exit(0)

    def explore(self):
        """Execute the app and in doing so process the results of all run checks."""

        app().exec()

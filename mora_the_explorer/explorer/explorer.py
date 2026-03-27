import logging
import platform
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import QThreadPool

from .appmanager import app
from .checknmr import Manufacturer, check_nmr, Reporter
from .config import Config
from .worker import Worker
from .paths import get_check_paths



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
        self.server_path = Path(self.config.paths[platform.system()])

        # Load group and spectrometer info
        # Need to flatten groups dict (as some are in e.g. an "other" subdict)
        self.all_groups = {}
        for k, v in self.config.groups.items():
            if isinstance(v, str):
                self.all_groups[k] = v
            elif isinstance(v, dict):
                self.all_groups.update(v)
        self.specs = self.config.specs

    def single_check(
        self,
        reporter: Reporter,
        date,
        wild_group=False,
        completion_handler=None,
    ):
        """Conduct a check of a single date."""
        if hasattr(reporter, "status_bar"):
            # Hide start button, show status bar
            reporter.status_bar.show_status()

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
        worker = Worker(
            check_nmr,
            reporter=reporter,
            server_path=self.server_path,
            check_paths=paths,
            dest_path=options["dest_path"],
            manufacturer=Manufacturer.from_str(self.specs[self.config.options["spec"]]),
            initials=options["initials"],
            group=options["group"],
            inc_init=options["inc_init"],
            inc_solv=options["inc_solv"],
            inc_path=options["inc_path"],
            #nmrcheck_compat_mode=options[""]
        )
        worker.signals.progress.connect(update_progress)
        worker.signals.status.connect(update_status)
        worker.signals.completed.connect(completion_handler)
        self.threadpool.start(worker)
        self.queued_checks += 1

    def multiday_check(
        self,
        initial_date,
        wild_group,
        prog_bar=None,
        status_bar=None,
        completion_handler=None,
    ):
        """Check multiple days in sequence."""

        end_date = date.today() + timedelta(days=1)
        date_to_check = initial_date
        while date_to_check != end_date:
            self.single_check(
                date_to_check,
                wild_group,
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

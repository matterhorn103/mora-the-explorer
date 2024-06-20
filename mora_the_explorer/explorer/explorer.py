import logging
import platform
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import QThreadPool

from .appmanager import app
from .checknmr import check_nmr
from .config import Config
from .worker import Worker


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
        date,
        wild_group,
        prog_bar=None,
        status_bar=None,
        completion_handler=None,
    ):
        """Conduct a check of a single date."""
        if status_bar:
            # Hide start button, show status bar
            status_bar.show_status()

        # Handlers for updating progress and status
        def update_progress(prog_state):
            if prog_bar:
                prog_bar.setValue(prog_state)
            else:
                print(prog_state)

        def update_status(status):
            if status_bar:
                status_bar.setText(status)
            else:
                print(status)

        # Default to using own built-in handler for completion
        if completion_handler is None:
            completion_handler = self.completion_handler
        # Start main checking function in worker thread
        worker = Worker(
            check_nmr,
            fed_options=self.config.options,
            server_path=self.server_path,
            specs_info=self.specs,
            check_date=date,
            groups=self.all_groups,
            wild_group=wild_group,
            prog_bar=prog_bar,
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

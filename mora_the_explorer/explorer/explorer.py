import logging
import platform
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import  QThreadPool, QUrl
from PySide6.QtGui import QDesktopServices

from .worker import Worker
from .checknmr import check_nmr
from .config import Config


class Explorer:
    def __init__(self, config: Config):
        self.config = config

        # Set up multithreading; MaxThreadCount limited to 1 as checks don't run properly if multiple run concurrently
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        # Set path to mora
        self.mora_path = Path(config.paths[platform.system()])

        # Load group and spectrometer info
        # Need to flatten groups dict (as some are in an "other" subdict)
        self.all_groups = {k: v for k, v in config.groups.items() if isinstance(v, str)}
        self.all_groups.update({k: v for k, v in config.groups["other"].items()})
        self.specs = config.specs

        # Initialize number of queued checks
        self.queued_checks = 0


    def open_destination(self):
        """Show the destination folder for spectra in the system file browser."""
        if Path(self.config.options["dest_path"]).exists() is True:
            url = QUrl.fromLocalFile(self.config.options["dest_path"])
            QDesktopServices.openUrl(url)

    def single_check(
            self,
            date,
            wild_group,
            prog_bar=None,
            status_bar=None,
            completion_handler=None,
        ):
        if prog_bar:
            self.prog_bar = prog_bar
        if status_bar:
            self.status_bar = status_bar
        try:
            # Hide start button, show status bar
            self.status_bar.show_status()
        except AttributeError:
            pass
        # Default to using own built-in handler for completion
        if completion_handler is None:
            completion_handler = self.completion_handler
        # Start main checking function in worker thread
        worker = Worker(
            check_nmr,
            fed_options=self.config.options,
            mora_path=self.mora_path,
            specs_info=self.specs,
            check_date=date,
            groups=self.all_groups,
            wild_group=wild_group,
            prog_bar=self.prog_bar,
        )
        worker.signals.progress.connect(self.update_progress)
        worker.signals.status.connect(self.update_status)
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

    def update_progress(self, prog_state):
        self.prog_bar.setValue(prog_state)
    
    def update_status(self, status):
        self.status_bar.setText(status)

    def completion_handler(self, copied_list):
        self.queued_checks -= 1
        # Display output
        for entry in copied_list:
            print(entry)
        # Task is complete only if all queued checks have finished
        if self.queued_checks == 0:
            print("Task complete")
            logging.info("Task complete")


from copy import copy
import logging
from datetime import date, timedelta
from pathlib import Path
import platform

from PySide6.QtCore import QThreadPool

from ..config import Config
from ..spec import Spectrometer
from ..check import get_check_paths, check_nmr, MetadataRules
from .worker import PrintingReporter


class Explorer:
    """Launches checks based on a given `Config` object.

    Serves as a task queuer as well as an interpreter between a configuration and the
    `check_nmr` function.
    """

    def __init__(self, config: Config):
        self.config = config

        # Set up multithreading; MaxThreadCount limited to 1 as checks don't run
        # properly if multiple run concurrently
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        # Initialize number of queued checks
        self.queued_checks = 0

    def generate_rules(self) -> MetadataRules:
        """Generate metadata handling rules based on the curent configuration."""
        options = self.config.options
        spec_info = self.config.specs[options.spec]
        # Put together the way the folder names should be formatted
        if options.inc_user:
            name_format = ["user", "sample_info", "experiment"]
        else:
            name_format = ["sample_info", "experiment"]
        if options.inc_solv:
            name_format.append("solvent")
        if options.inc_path:
            name_format.append("folder_name")
        # Always include the frequency info too if it's available
        name_format.append("frequency")
        rules = MetadataRules(
            src_fields=spec_info.title_format,
            conditions={
                "user": options.user,
                "user_name": options.user_name,
                "group": options.group,
                "group_name": self.config.groups.all[options.group],
            },
            dest_fields=name_format,
        )
        return rules

    def single_check(
        self,
        date: date,
    ) -> list[str]:
        """Conduct a check of a single date."""

        spec: Spectrometer = self.config.specs[self.config.options.spec]
        # If there's any spectrometer that ought to be included, sub the actual
        # definitions in for the strings if it hasn't already been done
        for i, s in enumerate(spec.include):
            if isinstance(s, str):
                spec.include[i] = self.config.specs[s]

        # Get platform dependent server path
        server_path = Path(
            getattr(self.config.paths, platform.system().lower())
        )

        # If a specific group hasn't been selected, check all groups i.e. treat as wild
        # An empty string and `None` both mean that nothing has been selected
        if not self.config.options.group:
            groups = self.config.groups.all
        else:
            groups = {k: v for k, v in self.config.groups.all.items() if k == self.config.options.group}

        paths = get_check_paths(
            spec_info=spec,
            server_path=server_path,
            check_date=date,
            groups=groups,
        )

        # Start main checking function
        options = self.config.options
        rules = self.generate_rules()
        #worker = Worker(
        #    check_nmr,
        #    src=paths,
        #    dest=self.config.paths.save,
        #    rules=rules,
        #    manufacturer=self.config.specs[options.spec].manufacturer,
        #    date=date,
        #)
        spec = self.config.specs[options.spec]
        reporter = PrintingReporter()
        check_nmr(
            src=paths,
            dest=self.config.paths.save,
            rules=rules,
            manufacturer=spec.manufacturer,
            reporter=reporter,
            date=date,
        )
        #worker.reporter.signals.update_progress.connect(update_progress)
        #worker.reporter.signals.set_max_progress.connect(set_max_progress)
        #worker.reporter.signals.set_status.connect(update_status)
        #worker.reporter.signals.completed.connect(completion_handler)
        #self.threadpool.start(worker)
        #self.queued_checks += 1
        return reporter.output

    def multiday_check(
        self,
        initial_date: date,
        #prog_bar=None,
        #status_bar=None,
        #completion_handler: Callable | None = None,
    ) -> list[str]:
        """Check multiple days in sequence."""

        end_date = date.today() + timedelta(days=1)
        date_to_check = initial_date
        output = []
        while date_to_check != end_date:
            partial_output = self.single_check(
                date_to_check,
                #prog_bar,
                #status_bar,
                #completion_handler,
            )
            date_to_check += timedelta(days=1)
            output.extend(partial_output)
        return output

    def completion_handler(self, copied_list):
        """The default handler for a completed check."""

        self.queued_checks -= 1
        # Display output
        for entry in copied_list:
            print(entry)
        self.all_output.extend(copied_list)
        self.app.quit()
        # Task is complete only if all queued checks have finished
        if self.queued_checks == 0:
            print("Task complete")
            logging.info("Task complete")
            self.app.exit(0)

    def explore(self):
        """Execute the app and in doing so process the results of all run checks."""
        self.app.exec()

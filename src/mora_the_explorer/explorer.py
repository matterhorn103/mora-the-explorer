import datetime
from pathlib import Path
import platform
import sys

from .config import Config
from .spec import Spectrometer
from .check import get_check_paths, check_nmr, MetadataRules, Reporter


class PrintingReporter(Reporter):
    """A basic Reporter that just prints all status updates, progress etc. to stdout."""
    def __init__(self):
        self._progress = 0
        self._max_progress = 0
        self._status = ""
        self._messages = []
        self._copied = []
        self._errors = []

    def status(self) -> str:
        return self._status

    def set_status(self, message):
        self._status = message
        print(message)

    def progress(self) -> int:
        return self._progress
    
    def report_progress(self):
        # If there's nothing to check anyway then obviously we're already finished
        # Not guarding here causes a divide-by-zero error when no server or folder on it is found
        if self._max_progress == 0:
            print(f"Progress: {100}%", end="\r")
        else:
            print(f"Progress: {round((self._progress / self._max_progress) * 100)}%", end="\r")

    def reset_progress(self):
        self._progress = 0
        #self.report_progress()

    def increment_progress(self, increment: int = 1):
        self._progress += increment
        self.report_progress()

    def max_progress(self) -> int:
        return self._max_progress

    def set_max_progress(self, max: int):
        self._max_progress = max
        #print(f"New max progress: {max}")

    def messages(self) -> list[str]:
        return self._messages

    def add_message(self, message: str):
        self._messages.append(message)
        print(message)

    def copied(self) -> list[str]:
        return self._copied

    def add_copied(self, name: str):
        self._copied.append(name)
        self.add_message(f"Spectrum found: {name}")

    def errors(self) -> list[str]:
        return self._errors

    def add_error(self, error: str):
        self._errors.append(error)
        print(error, file=sys.stderr)

    def finish(self, completion_message: str):
        self._progress = self._max_progress
        self.report_progress()
        self._messages.append(completion_message)
        print(completion_message)


class Explorer:
    """Launches checks based on a given `Config` object.

    Serves as an interpreter between a configuration and the `check_nmr` function.
    """

    def __init__(self, config: Config):
        self.config = config

        # Set up multithreading; MaxThreadCount limited to 1 as checks don't run
        # properly if multiple run concurrently
        #self.threadpool = QThreadPool()
        #self.threadpool.setMaxThreadCount(1)

        # Initialize number of queued checks
        self.queued_checks = 0

    def generate_rules(self) -> MetadataRules:
        """Generate metadata handling rules based on the curent configuration."""
        options = self.config.options
        spec_info = self.config.specs[options.spec]
        # Put together the way the folder names should be formatted
        if options.inc_user:
            # The duplication is OK because only the one that is actually in
            # the measurement title will be included (so it might actually be both)
            name_format = ["user_name", "user", "sample_info", "experiment"]
        else:
            name_format = ["sample_info", "experiment"]
        if options.inc_solvent:
            name_format.append("solvent")
        if options.inc_frequency:
            name_format.append("frequency")
        if options.inc_original:
            name_format.append("folder_name")
        # The group name might have been set explicitly, but normally we get it
        # from the groups table
        if hasattr(options, "group_name"):
            group_name = options.group_name
        else:
            group_name = self.config.groups.all[options.group]
        rules = MetadataRules(
            src_fields=spec_info.title_format,
            conditions={
                "user": options.user,
                "user_name": options.user_name,
                "group": options.group,
                "group_name": group_name,
            },
            dest_fields=name_format,
        )
        return rules

    def single_check(self, date: datetime.date, reporter: Reporter | None = None) -> Reporter:
        """Conduct a check of a single date.
        
        Returns the `Reporter` it was passed, or the default `PrintingReporter`
        that was created if none was passed.
        """

        # If the caller didn't provide a reporter, just create a basic one
        reporter = reporter if reporter else PrintingReporter()

        spec: Spectrometer = self.config.specs[self.config.options.spec]
        # If there's any spectrometer that ought to be included, sub the actual
        # definitions in for the strings if it hasn't already been done
        for i, s in enumerate(spec.include):
            if isinstance(s, str):
                spec.include[i] = self.config.specs[s]

        # Get platform dependent server path
        server_path = Path(
            getattr(self.config.paths, platform.system().lower())
        ).expanduser()
        dest_path = Path(self.config.paths.save).expanduser()

        # If a specific group hasn't been selected, check all groups i.e. treat as wild
        # An empty string and `None` both mean that nothing has been selected
        if not self.config.options.group:
            groups = self.config.groups.all
        else:
            groups = {k: v for k, v in self.config.groups.all.items() if k == self.config.options.group}

        check_paths = get_check_paths(
            spec_info=spec,
            server_path=server_path,
            check_date=date,
            groups=groups,
        )

        # Start main checking function
        options = self.config.options
        rules = self.generate_rules()
        spec = self.config.specs[options.spec]
        
        check_nmr(
            src=check_paths,
            dest=dest_path,
            rules=rules,
            manufacturer=spec.manufacturer,
            reporter=reporter,
            date=date,
        )

        return reporter

    def multiday_check(
        self, initial_date: datetime.date, reporter: Reporter | None = None,
    ) -> Reporter:
        """Check multiple days in sequence.
        
        Uses a single `Reporter` for all days – either the passed one or a simple
        `PrintingReporter` created by default.
        """

        # If the caller didn't provide a reporter, just create a basic one
        reporter = reporter if reporter else PrintingReporter()

        end_date = datetime.date.today() + datetime.timedelta(days=1)
        date_to_check = initial_date
        while date_to_check != end_date:
            self.single_check(date_to_check, reporter)
            date_to_check += datetime.timedelta(days=1)

        return reporter

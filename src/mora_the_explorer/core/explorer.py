import datetime
from pathlib import Path
import platform
import sys

from .config import Config
from .spec import Spectrometer
from . import get_check_paths, check_nmr, MetadataRules, Reporter, MatchValues, SpectraSorting


class PrintingReporter(Reporter):
    """A basic Reporter that just prints all status updates, progress etc. to stdout."""

    def __init__(self):
        self._progress = 0
        self._max_progress = 0
        self._status = ""
        self._messages = []
        self._copied = []
        self._errors = []

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
        # self.report_progress()

    def increment_progress(self, increment: int = 1):
        self._progress += increment
        self.report_progress()

    def max_progress(self) -> int:
        return self._max_progress

    def set_max_progress(self, max: int):
        self._max_progress = max
        # print(f"New max progress: {max}")

    def messages(self) -> list[str]:
        return self._messages

    def add_message(self, message: str):
        self._messages.append(message)
        print(message)

    def copied(self) -> list[str]:
        return self._copied

    def add_copied(self, name: str):
        self._copied.append(name)
        self._messages.append(f"Spectrum found: {name}")
        print(f"Spectrum found: {name}")

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

    def generate_rules(self) -> MetadataRules:
        """Generate metadata handling rules based on the curent configuration."""
        options = self.config.options
        spec_info = self.config.specs[options.spec]

        # Put together the conditions required for a match to be found
        # The group name might have been set explicitly, but normally we get it
        # from the groups table
        if hasattr(options, "group_name"):
            group_name = options.group_name
        else:
            group_name = self.config.groups.all[options.group]
        substitutions = MatchValues(
            user=options.user,
            user_name=options.user_name,
            group=options.group,
            group_name=group_name,
            sample_id="",  # TODO use the actual value once it exists
        )

        # Put together the way the folder names should be formatted
        # We create the sample folder format too even if it's only relevant when
        # the user wants to sort by sample 
        sample_format = []
        measurement_format = []

        # Sample-specific metadata fields go in both
        if options.naming.group:
            # Treat group name and group as mutually exclusive, prioritise the group
            sample_format.append(["group", "group_name"])
            measurement_format.append(["group", "group_name"])
        if options.naming.user:
            # Treat user name and user as mutually exclusive, prioritise the user
            sample_format.append(["user", "user_name"])
            measurement_format.append(["user", "user_name"])
        # Always include the sample info
        sample_format.append("sample_id")
        measurement_format.append("sample_id")
        if options.naming.solvent:
            sample_format.append("solvent")
            measurement_format.append("solvent")

        # The instrument isn't actually sample specific, but the app offers the
        # ability to sort by it, and in the case that `SpectraSorting.SAMPLE_AND_SPEC`
        # is chosen, it is treated as sample specific (i.e. a sample is treated as
        # if it is a different sample when measured on different instruments)
        if options.naming.instrument:
            if options.sort is SpectraSorting.SAMPLE_AND_SPEC:
                sample_format.append("instrument")
                # TODO consider not including it in the measurement title to avoid
                # duplication - this would then be handled differently to every
                # other field though, which seems like it'd be unexpected
                measurement_format.append("instrument")
            else:
                measurement_format.append("instrument")
        if options.naming.frequency:
            # This option is no longer available in the GUI so is unimportant, but
            # is preserved in case anyone finds it useful (it can be set in config.toml)
            measurement_format.append("frequency")
        # Spectrum-specific metadata fields only go in the measurement name
        if options.naming.experiment:
            measurement_format.append("experiment")
        if options.naming.original:
            measurement_format.append("folder_name")

        rules = MetadataRules(
            values=substitutions,
            sample_pattern=spec_info.sample_pattern,
            measurement_pattern=spec_info.measurement_pattern,
            sample_format=sample_format,
            measurement_format=measurement_format,
            pattern_sep=self.config.admin.pattern_separator,
        )
        return rules
    
    def get_check_paths(self, date: datetime.date) -> list[Path]:
        """Generate the paths to check based on the current configuration."""
        
        spec: Spectrometer = self.config.specs[self.config.options.spec]
        # If there's any spectrometer that ought to be included, sub the actual
        # definitions in for the strings if it hasn't already been done
        for i, s in enumerate(spec.include):
            if isinstance(s, str):
                spec.include[i] = self.config.specs[s]

        # Get platform dependent server path
        server_path = Path(getattr(self.config.paths, platform.system().lower())).expanduser()

        # If a specific group hasn't been selected, check all groups i.e. treat as wild
        # An empty string and `None` both mean that nothing has been selected
        if not self.config.options.group:
            groups = self.config.groups.all
        else:
            groups = {
                k: v for k, v in self.config.groups.all.items() if k == self.config.options.group
            }

        check_paths = get_check_paths(
            spec_info=spec,
            server_path=server_path,
            date=date,
            groups=groups,
        )

        return check_paths


    def single_check(self, date: datetime.date, reporter: Reporter | None = None) -> Reporter:
        """Conduct a check of a single date.

        Returns the `Reporter` it was passed, or the default `PrintingReporter`
        that was created if none was passed.
        """

        # If the caller didn't provide a reporter, just create a basic one
        reporter = reporter if reporter else PrintingReporter()

        # Work out what paths to check
        check_paths = self.get_check_paths(date)

        # Start main checking function
        options = self.config.options
        rules = self.generate_rules()
        spec = self.config.specs[options.spec]
        dest_path = Path(self.config.paths.save).expanduser()

        check_nmr(
            src=check_paths,
            dest=dest_path,
            rules=rules,
            manufacturer=spec.manufacturer,
            reporter=reporter,
            date=date,
            sort=self.config.options.sort,
        )

        return reporter

    def multiday_check(
        self,
        initial_date: datetime.date,
        reporter: Reporter | None = None,
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

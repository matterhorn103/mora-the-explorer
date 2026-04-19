import logging
import platform
from copy import deepcopy
import datetime
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from ..check.checknmr import Reporter
from ..config import Config
from ..explorer import Explorer
from .ui.main_window import MainWindow


class ReporterSignals(QObject):
    """The collected signals for a `QtReporter`.
    
    This is necessary because `QtReporter` can't inherit from both `Reporter` and
    `QObject`, but signals need to be class attributes.
    """
    status_set = Signal(str)
    progress_set = Signal(int)
    max_progress_set = Signal(int)
    message_sent = Signal(str)
    folder_copied = Signal(str)
    error_reported = Signal(str)
    finished = Signal(str)


class QtReporter(Reporter):
    """A Reporter that emits Qt signals in response to events, making it suitable
    for reporting back from a background thread."""

    def __init__(self):
        super().__init__()
        self._progress = 0
        self._max_progress = 0
        self._messages = []
        self._copied = []
        self._errors = []
        self.signals = ReporterSignals()

    def set_status(self, message: str):
        self.signals.status_set.emit(message)

    def progress(self) -> int:
        return self._progress
    
    def reset_progress(self):
        self.signals.progress_set.emit(0)
    
    def increment_progress(self, increment: int = 1):
        self._progress += increment
        self.signals.progress_set.emit(self._progress)

    def max_progress(self) -> int:
        return self._max_progress
    
    def set_max_progress(self, max: int):
        self._max_progress = max
        self.signals.max_progress_set.emit(max)

    def messages(self) -> list[str]:
        return self._messages
    
    def add_message(self, message: str):
        self._messages.append(message)
        self.signals.message_sent.emit(message)

    def copied(self) -> list[str]:
        return self._copied
    
    def add_copied(self, name: str):
        self._copied.append(name)
        self.signals.folder_copied.emit(name)

    def errors(self) -> list[str]:
        return self._errors
    
    def add_error(self, error: str):
        self._errors.append(error)
        self.signals.error_reported.emit(error)

    def finish(self, completion_message: str):
        self._progress = self._max_progress
        self.signals.progress_set.emit(self._max_progress)
        self._messages.append(completion_message)
        self.signals.finished.emit(completion_message)


class Controller:
    """The bridge between the desktop app's interface and the searching backend.
    
    A `Controller` coordinates the creation of, and interaction between, all the
    components necessary to run the GUI app and run searches.
    It has an associated `MainWindow` which holds and owns the `Config` that is
    passed at instantiation.

    When a search is run, an `Explorer` instance is created using a copy of the
    current config of the `MainWindow`, so that subsequent changes in the GUI
    thread don't affect the search.
    The `Explorer` search method is then launched in a second thread, to avoid
    freezing the GUI.
    """

    timer: QTimer

    def __init__(self, config: Config, version_header: str):
        """Create a new `Controller` along with a new associated `MainWindow`
        instance.
        
        `version_header` has two functions:
        1. The first five lines are displayed to the user at the top of the app,
           providing information about the version, author, license etc.
        2. The contents are compared to the same file that is deposited on the
           server to see if updates are available.
        """
        self.version_header = version_header

        # Create instance of `MainWindow` (front-end), then show it
        logging.info("Initializing user interface...")
        self.main_window = MainWindow(config, version_header, admin_mode=False)
        self.main_window.show()
        logging.info("...complete")

        ## Check for updates
        #self.update_check(self.update_path)

        # Connect the key signals
        self.main_window.started.connect(self.start_check)
        self.main_window.cancelled.connect(self.cancel_scheduled_check)

    def new_reporter(self) -> QtReporter:
        """Get a new QtReporter with its signals connected to the appropriate slots in the UI."""

        reporter = QtReporter()

        # Connect the signals
        reporter.signals.status_set.connect(self.main_window.status_bar.set_status)
        reporter.signals.progress_set.connect(self.main_window.prog_bar.setValue)
        reporter.signals.max_progress_set.connect(self.main_window.prog_bar.setMaximum)
        reporter.signals.message_sent.connect(self.main_window.display.add_entry)
        reporter.signals.folder_copied.connect(self.main_window.display.add_entry)
        reporter.signals.error_reported.connect(self.main_window.display.add_entry)
        # Send the completion message to the display on finish
        reporter.signals.finished.connect(self.main_window.display.add_entry)
        # Also trigger the completion handler
        reporter.signals.finished.connect(self.check_ended)

        return reporter

    @Slot()
    def start_check(self):
        self.main_window.status_bar.set_status("Initializing…")
        self.main_window.status_bar.show_status()

        # Create instance of Explorer (back-end)
        logging.info("Initializing new explorer...")
        self.explorer = Explorer(deepcopy(self.main_window.config))
        logging.info("...complete")

        self.reporter = self.new_reporter()

        if not self.main_window.date_selector.multiday():
            self.explorer.single_check(
                self.main_window.date_selector.date(),
                self.reporter,
            )
        else:
            self.explorer.multiday_check(
                self.main_window.date_selector.date(),
                self.reporter,
            )
    
    @Slot()
    def check_ended(self):
        # Send a notification if there was an error or if new spectra were found
        if self.reporter.errors():
            combined_error_message = "\n".join(self.reporter.errors())
            self.main_window.notify_error(combined_error_message)
        elif self.reporter.copied():
            self.main_window.notify_spectra()
        # Otherwise no notification

        # Behaviour for repeat check function
        # Should only be `True` if it was allowed to be, as the config passed to the
        # explorer should have captured the UI state at the time the check was started
        if self.explorer.config.options.repeat_switch:
            self.main_window.status_bar.show_cancel()
            # Start new timer that will trigger start_check() once it runs out
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.start_check)
            # Could have used the current value in the UI here, shouldn't really matter
            self.timer.start(self.explorer.config.options.repeat_delay * 60 * 1000)
            logging.info(f"Timer started for next check, scheduled to begin in {self.explorer.config.options.repeat_delay} min")
        else:
            self.main_window.status_bar.show_start()
            logging.info("Task complete")

    @Slot()
    def cancel_scheduled_check(self):
        self.timer.stop()
        self.main_window.status_bar.show_start()
        logging.info("Scheduled check cancelled")

#    def update_check(self, update_path: Path):
#        """Check for updates at location specified."""
#
#        logging.info(f"Checking for updates at: {update_path}")
#        update_path_version_file = update_path / "version.txt"
#        with open(self.rsrc_dir / "version.txt", encoding="utf-8") as f:
#            version_no = f.readlines()[2].rstrip()
#            logging.info(f"Current version: {version_no}")
#        try:
#            if update_path_version_file.exists() is True:
#                with open(update_path_version_file, encoding="utf-8") as f:
#                    version_file_info = f.readlines()
#                    newest_version_no = version_file_info[2].rstrip()
#                    changelog = "".join(version_file_info[5:]).rstrip()
#                if version_no != newest_version_no:
#                    self.main_window.notify_update(
#                        version_no, newest_version_no, changelog, self.update_path
#                    )
#        except PermissionError:
#            self.main_window.notify_failed_permissions()

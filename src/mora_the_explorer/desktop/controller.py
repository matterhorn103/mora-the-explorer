import datetime
import logging
from copy import deepcopy
import tomllib
from packaging.version import Version
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal, Slot, QThread
from PySide6.QtWidgets import QApplication

from ..core.checknmr import Reporter
from ..core.config import Config
from ..core.explorer import Explorer
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
    day_checked = Signal(str)


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
        self.signals.folder_copied.emit(f"Spectrum found: {name}")

    def errors(self) -> list[str]:
        return self._errors

    def add_error(self, error: str):
        self._errors.append(error)
        self.signals.error_reported.emit(error)

    def finish(self, completion_message: str):
        self._progress = self._max_progress
        self.signals.progress_set.emit(self._max_progress)
        self._messages.append(completion_message)
        self.signals.day_checked.emit(completion_message)


class QtExplorer(Explorer, QObject):
    """An `Explorer` that can be run in a separate `QThread`.

    Effectively what Qt documentation would usually refer to as a "Worker".

    Has a slot to begin checks (both single- and multi-day) from a different thread,
    and a signal that indicates that the check has finished and the `QtExplorer`
    can be moved back to the main thread.

    Note that the reporter used for the check stays in its thread (i.e. the main
    GUI thread) and it is not necessary for it to be moved.
    """

    check_finished = Signal()

    def __init__(self, config: Config):
        QObject.__init__(self)
        Explorer.__init__(self, config)

    @Slot()
    def start_check(self, multiday: bool, date: datetime.date, reporter: QtReporter):
        if multiday:
            self.multiday_check(date, reporter=reporter)
        else:
            self.single_check(date, reporter=reporter)
        # Signal completion
        self.check_finished.emit()


class Controller(QObject):
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

    # A signal used to trigger a QtExplorer in a separate thread to start its check
    start_check = Signal(bool, datetime.date, QtReporter)

    timer: QTimer
    explorer: QtExplorer | None

    def __init__(self, config: Config, admin_mode: bool = False):
        """Create a new `Controller` along with a new associated `MainWindow` instance."""
        super().__init__()
        self.version = Version(config.admin.version)

        # Create instance of `MainWindow` (front-end)
        logging.info("Initializing user interface…")
        self.main_window = MainWindow(config, admin_mode)
        # Connect the key signals
        self.main_window.started.connect(self.check_requested)
        self.main_window.cancelled.connect(self.cancel_scheduled_check)
        self.main_window.admin_mode_toggled.connect(self.toggle_admin_mode)
        # Show it
        self.main_window.show()
        logging.info("…complete")

        # Check for updates
        update_path = Path(config.paths.server()) / config.paths.src
        self.update_check(update_path)

        # To begin with there's no active explorer
        self.explorer = None
        # Create a separate background thread to run checks in (necessary to avoid
        # the GUI freezing during a check)
        self.explorer_thread = QThread()
        # We need to make sure that it gets quit at the same time as the app
        instance = QApplication.instance()
        if instance:
            instance.aboutToQuit.connect(self.cleanup)

    def update_check(self, update_path: Path):
        """Check for updates at the specified location.

        The directory at `update_path` must be the root directory of a copy of
        the source code of Mora the Explorer. The `config.toml` file within the
        source code (i.e. at `<update_path>/src/mora_the_explorer/config.toml`)
        is then checked and compare to the local one to see if a newer version
        has been released.
        """

        logging.info(f"Checking for updates at: {update_path}")
        remote_config_file = update_path / "src/mora_the_explorer/config.toml"
        try:
            if remote_config_file.exists() is True:
                with open(remote_config_file, "rb", encoding="utf-8") as f:
                    remote_config = tomllib.load(f)
            else:
                logging.info(f"No remote version information found at {remote_config_file}")
                return
        except PermissionError:
            logging.info("The user does not have the required permissions to access the server!")
            return
        except Exception as e:
            logging.info("The following exception occurred while checking for updates:")
            logging.info(e)
            return
        remote_version = Version(remote_config["admin"]["version"])
        if self.version < remote_version:
            changelog = (
                "What's new in version "
                + str(remote_version)
                + ":\n"
                + remote_config["admin"]["changelog"]
            )
            self.main_window.notify_update(self.version, remote_version, changelog, update_path)

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
        # Send the completion message to the display when a single day's check finishes
        reporter.signals.day_checked.connect(self.main_window.display.add_entry)
        # We don't actually want to trigger `self.check_ended` yet though,
        # because a multi-day check "finishes" several individual checks using
        # the same QtReporter
        # Instead the Controller will look for a signal from the QtExplorer

        return reporter

    @Slot()
    def check_requested(self):
        # Make sure a destination path has been specified
        if not self.main_window.config.paths.save:
            self.main_window.dest_entry.pick_path("Choose where to save spectra!")
        self.main_window.status_bar.set_status("Initializing…")
        self.main_window.status_bar.show_status()

        # Create instance of QtExplorer (back-end)
        logging.info("Initializing new explorer…")
        self.explorer = QtExplorer(deepcopy(self.main_window.config))
        # Move it to the background thread
        self.explorer.moveToThread(self.explorer_thread)
        # Connect up the signals
        self.start_check.connect(self.explorer.start_check)
        self.explorer.check_finished.connect(self.check_ended)
        self.explorer_thread.start()
        logging.info("…complete")

        # Create a fresh reporter
        self.reporter = self.new_reporter()
        # Then actually trigger the explorer to start a check via our signal
        self.start_check.emit(
            (self.main_window.date_selector.mode() == "multi"),
            # This always gets the current date right now in "current" mode
            self.main_window.date_selector.date(),
            self.reporter,
        )

    @Slot()
    def check_ended(self):
        # This method should only ever be called when there's an existing Explorer
        assert self.explorer is not None

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
            # Start new timer that will request a (completely) new check once it runs out
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.check_requested)
            # Could have used the current value in the UI here, shouldn't really matter
            self.timer.start(self.explorer.config.options.repeat_delay * 60 * 1000)
            logging.info(
                f"Timer started for next check, scheduled to begin in {self.explorer.config.options.repeat_delay} min"
            )
        else:
            self.main_window.status_bar.show_start()
            logging.info("Task complete")

        # Destroy the explorer
        self.explorer.deleteLater()
        self.explorer = None

    @Slot()
    def cancel_scheduled_check(self):
        self.timer.stop()
        self.main_window.status_bar.show_start()
        logging.info("Scheduled check cancelled")

    @Slot()
    def cleanup(self):
        self.explorer_thread.quit()  # Tells it to stop
        self.explorer_thread.wait()  # Waits until it has actually done so

    @Slot()
    def toggle_admin_mode(self):
        logging.info("Admin mode toggled – reinitializing user interface…")
        current_config = self.main_window.config
        currently_admin = self.main_window.admin_mode
        # Close old window
        self.main_window.close()
        self.main_window.deleteLater()  # So that the Qt reference is dropped and it's destroyed
        # Build new window in opposite mode
        self.main_window = MainWindow(current_config, not currently_admin)
        # Reconnect the key signals
        self.main_window.started.connect(self.check_requested)
        self.main_window.cancelled.connect(self.cancel_scheduled_check)
        self.main_window.admin_mode_toggled.connect(self.toggle_admin_mode)
        self.main_window.show()
        logging.info("…complete")

import logging
import platform
from copy import deepcopy
import datetime
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import QTimer, QUrl, Slot
from PySide6.QtGui import QDesktopServices

from ..config import Config
from ..explorer import Explorer
from .ui.main_window import MainWindow


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

        ## Timer for repeat check, starts checking function when timer runs out
        #self.timer = QTimer()
        #self.timer.setSingleShot(True)
        #self.timer.timeout.connect(self.started)

        ## Check for updates
        #self.update_check(self.update_path)

        # Connect the key signals
        self.main_window.started.connect(self.start_check)

    @Slot()
    def start_check(self):
        # Create instance of Explorer (back-end)
        logging.info("Initializing new explorer...")
        self.explorer = Explorer(deepcopy(self.main_window.config))
        logging.info("...complete")

        if not self.main_window.date_selector.multiday():
            reporter = self.explorer.single_check(
                self.main_window.date_selector.date(),
                reporter=None, # TODO Make a reporter that passes output back to the GUI
            )
        else:
            reporter = self.explorer.multiday_check(
                self.main_window.date_selector.date(),
                reporter=None, # TODO Make a reporter that passes output back to the GUI
            )
        for message in reporter.messages():
            self.main_window.display.add_entry(message)
        if reporter.errors():
            combined_error_message = "\n".join(reporter.errors())
            self.main_window.notify_error(combined_error_message)

#
#    def started(self):
#        self.explorer.queued_checks = 0
#        if (
#            self.opts.only_button.isChecked() is True
#            or self.specs[self.config.options["spec"]]["single_check_only"] is True
#        ):
#            self.explorer.single_check(
#                self.date_selected,
#                self.wild_group,
#                prog_bar=self.ui.prog_bar,
#                status_bar=self.ui.status_bar,
#                completion_handler=self.check_ended,
#            )
#        elif self.opts.since_button.isChecked() is True:
#            self.explorer.multiday_check(
#                self.date_selected,
#                self.wild_group,
#                prog_bar=self.ui.prog_bar,
#                status_bar=self.ui.status_bar,
#                completion_handler=self.check_ended,
#            )

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
#
#    def check_ended(self, copied_list):
#        self.explorer.queued_checks -= 1
#        # Set progress to 100% just in case it didn't reach it for whatever reason
#        self.ui.prog_bar.setMaximum(1)
#        self.ui.prog_bar.setValue(1)
#        # Will only not be true if an unknown error occurred
#        # In all other cases len will be at least 2
#        if len(copied_list) > 1:
#            # At least one spectrum was found
#            if copied_list[1][:5] == "Spect":
#                copied_list.pop(0)
#                self.main_window.notify_spectra(copied_list)
#            # No spectra were found but check completed successfully
#            elif copied_list[1][:5] == "Check":
#                pass
#            # Some exception was raised
#            elif copied_list[0] == "Exception":
#                copied_list.pop(0)
#                self.main_window.notify_error(copied_list)
#            # Known error occurred
#            else:
#                copied_list.pop(0)
#                self.main_window.notify_error(copied_list)
#        else:
#            # Unknown error occurred but exception wasn't raised, output of check
#            # function was returned without appending anything to copied_list
#            copied_list.pop(0)
#            self.main_window.notify_error(copied_list)
#        # Display output
#        for entry in copied_list:
#            self.ui.display.add_entry(entry)
#        # Behaviour for repeat check function, deactivate for hf spectrometer
#        # See also self.timer in init function
#        if (self.config.options["repeat_switch"] is True) and (
#            self.specs[self.config.options["spec"]]["single_check_only"] is False
#        ):
#            self.explorer.queued_checks += 1
#            self.ui.status_bar.show_cancel()
#            # Start new timer that will trigger started() once it runs out
#            self.timer.start(int(self.config.options["repeat_delay"]) * 60 * 1000)
#        # Enable start check button again, but only if all queued checks have finished
#        if self.explorer.queued_checks == 0:
#            self.ui.status_bar.show_start()
#            logging.info("Task complete")
#
#    def interrupted(self):
#        self.timer.stop()
#        self.ui.status_bar.show_start()

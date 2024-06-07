import logging
import platform
from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import QTimer, QThreadPool, QUrl
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QDesktopServices

from .worker import Worker
from .checknmr import check_nmr
from .config import Config
from .ui.main_window import MainWindow


class Explorer:
    def __init__(
        self, main_window: MainWindow, resource_directory: Path, config: Config
    ):
        self.main_window = main_window
        self.rsrc_dir = resource_directory
        self.config = config

        # Make it easier to access elements of the UI
        self.ui = self.main_window.ui
        self.opts = self.main_window.ui.opts

        # Set up multithreading; MaxThreadCount limited to 1 as checks don't run properly if multiple run concurrently
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        # Initialize some variables for later
        self.wild_group = False
        self.copied_list = []
        self.date_selected = date.today()

        # Set path to mora
        self.mora_path = Path(config.paths[platform.system()])
        self.update_path = Path(config.paths["update"])

        # Load group and spectrometer info
        self.all_groups = (
            {k: v for k, v in config.groups.items() if isinstance(v, str)}
            .update({k: v for k, v in config.groups["other"].items()})
        )
        self.specs = config.specs

        # Check for updates
        self.update_check(Path(config.paths["update"]))

        # Timer for repeat check, starts checking function when timer runs out
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.started)

        self.connect_signals()

    def update_check(self, update_path):
        """Check for updates at location specified."""

        logging.info(f"Checking for updates at: {update_path}")
        update_path_version_file = update_path / "version.txt"
        with open(self.rsrc_dir / "version.txt", encoding="utf-8") as f:
            version_no = f.readlines()[2].rstrip()
            logging.info(f"Current version: {version_no}")
        try:
            if update_path_version_file.exists() is True:
                with open(update_path_version_file, encoding="utf-8") as f:
                    version_file_info = f.readlines()
                    newest_version_no = version_file_info[2].rstrip()
                    changelog = "".join(version_file_info[5:]).rstrip()
                if version_no != newest_version_no:
                    self.main_window.notify_update(
                        version_no, newest_version_no, changelog, self.update_path
                    )
        except PermissionError:
            self.main_window.notify_failed_permissions()

    def connect_signals(self):
        """Connect all the signals from the UI elements to the various handlers.

        As much as possible, when the effects are only relevant for the UI, the handlers
        are defined as methods of MainWindow, while those that are relevant for the
        backend logic and searching are defined here as methods of Explorer.

        To allow a reasonable overview, however, all signals are connected here.
        """
        # Remember that self.ui = self.main_window.ui
        # and self.opts = self.main_window.ui.opts
        self.opts.initials_entry.textChanged.connect(self.initials_changed)
        self.opts.group_buttons.buttonClicked.connect(self.group_changed)
        self.opts.other_box.currentTextChanged.connect(self.group_changed)
        self.opts.dest_path_input.textChanged.connect(
            self.main_window.dest_path_changed
        )
        self.opts.open_button.clicked.connect(self.open_destination)
        self.opts.inc_init_checkbox.stateChanged.connect(
            self.main_window.inc_init_switched
        )
        self.opts.inc_solv_checkbox.stateChanged.connect(
            self.main_window.inc_solv_switched
        )
        self.opts.nmrcheck_style_checkbox.stateChanged.connect(
            self.main_window.nmrcheck_style_switched
        )
        self.opts.spec_buttons.buttonClicked.connect(self.main_window.spec_changed)
        self.opts.repeat_check_checkbox.stateChanged.connect(
            self.main_window.repeat_switched
        )
        self.opts.repeat_interval.valueChanged.connect(
            self.main_window.repeat_delay_changed
        )
        self.opts.save_button.clicked.connect(self.main_window.save)
        self.opts.since_button.toggled.connect(
            self.main_window.since_function_activated
        )
        self.opts.date_selector.dateChanged.connect(self.date_changed)
        self.opts.today_button.clicked.connect(self.main_window.set_date_as_today)
        self.ui.start_check_button.clicked.connect(self.started)
        self.ui.interrupt_button.clicked.connect(self.interrupted)
        self.ui.notification.clicked.connect(self.main_window.notification_clicked)

    def initials_changed(self, new_initials):
        """Make necessary adjustments after the user types something in `initials`.

        The main effect is simply that the new initials should be saved in the config
        and the save button should be activated.

        The `nmr` group has the ability to use a wildcard `*` followed by a space in the
        initials box to indicate that all groups should be matched for the following
        user's initials e.g. `* mjm` will search for spectra of MJM everywhere, not just
        in the Studer group's folders.
        As a result the maximum length of the initials entry needs to be increased when
        the wildcard is used.
        """
        if len(new_initials) == 0:
            # Just reset the max length
            self.opts.initials_entry.setMaxLength(3)
        else:
            if (new_initials[0] == "*") and (self.config.options["group"] == "nmr"):
                self.opts.initials_entry.setMaxLength(5)
                self.wild_group = True
                try:
                    new_initials = new_initials.split()[1]
                except IndexError:
                    new_initials = ""
            self.config.options["initials"] = new_initials
            self.opts.save_button.setEnabled(True)

    def group_changed(self):
        self.main_window.group_changed()
        self.adapt_paths_to_group(self.config.options["group"])

    def adapt_paths_to_group(self, group):
        if group != "nmr":
            # Make sure wild option is turned off for normal users
            self.wild_group = False

    def open_destination(self):
        """Show the destination folder for spectra in the system file browser."""
        if Path(self.config.options["dest_path"]).exists() is True:
            url = QUrl.fromLocalFile(self.config.options["dest_path"])
            QDesktopServices.openUrl(url)

    def date_changed(self):
        self.date_selected = self.opts.date_selector.date().toPython()

    def started(self):
        self.queued_checks = 0
        if (
            self.opts.only_button.isChecked() is True
            or self.specs[self.config.options["spec"]]["single_check_only"] is True
        ):
            self.single_check(self.date_selected)
        elif self.opts.since_button.isChecked() is True:
            self.multiday_check(self.date_selected)

    def single_check(self, date):
        # Hide start button, show status bar
        self.ui.status_bar.show_status()
        # Start main checking function in worker thread
        worker = Worker(
            check_nmr,
            fed_options=self.config.options,
            mora_path=self.mora_path,
            specs_info=self.specs,
            check_date=date,
            wild_group=self.wild_group,
            prog_bar=self.ui.prog_bar,
        )
        worker.signals.progress.connect(self.update_progress)
        worker.signals.status.connect(self.update_status)
        worker.signals.result.connect(self.handle_output)
        worker.signals.completed.connect(self.check_ended)
        self.threadpool.start(worker)
        self.queued_checks += 1

    def multiday_check(self, initial_date):
        end_date = date.today() + timedelta(days=1)
        date_to_check = initial_date
        while date_to_check != end_date:
            self.single_check(date_to_check)
            date_to_check += timedelta(days=1)

    def update_progress(self, prog_state):
        self.ui.prog_bar.setValue(prog_state)
    
    def update_status(self, status):
        self.ui.status_bar.setText(status)

    def handle_output(self, final_output):
        self.copied_list = final_output

    def check_ended(self):
        self.queued_checks -= 1
        # Stop showing checking status
        self.ui.status_bar.show_start()
        # Set progress to 100% just in case it didn't reach it for whatever reason
        self.ui.prog_bar.setMaximum(1)
        self.ui.prog_bar.setValue(1)
        # Will only not be true if an unknown error occurred
        # In all other cases len will be at least 2
        if len(self.copied_list) > 1:
            # At least one spectrum was found
            if self.copied_list[1][:5] == "spect":
                self.copied_list.pop(0)
                self.main_window.notify_spectra(self.copied_list)
            # No spectra were found but check completed successfully
            elif self.copied_list[1][:5] == "check":
                pass
            # Known error occurred
            else:
                self.copied_list.pop(0)
                self.main_window.notify_spectra(self.copied_list)
        else:
            # Unknown error occurred, output of check function was returned without
            # appending anything to copied_list
            self.copied_list.pop(0)
            self.main_window.notify_spectra(self.copied_list)
        # Display output
        for entry in self.copied_list:
            entry_label = QLabel(entry)
            self.ui.display.add_entry(entry_label)
        # Behaviour for repeat check function, deactivate for hf spectrometer
        # See also self.timer in init function
        if (self.config.options["repeat_switch"] is True) and (
            self.specs[self.config.options["spec"]]["single_check_only"] is False
        ):
            self.queued_checks += 1
            self.ui.status_bar.show_cancel()
            # Start new timer that will trigger started() once it runs out
            self.timer.start(int(self.config.options["repeat_delay"]) * 60 * 1000)
        # Enable start check button again, but only if all queued checks have finished
        if self.queued_checks == 0:
            self.ui.status_bar.show_start()
            logging.info("Task complete")

    def interrupted(self):
        self.timer.stop()
        self.ui.status_bar.show_start()

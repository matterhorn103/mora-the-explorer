import logging
import os
import platform
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import plyer

from PySide6.QtCore import QSize, QTimer, QRunnable, Signal, Slot, QThreadPool, QObject
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QWidget,
    QMessageBox,
)

from worker import Worker
from checknmr import check_nmr
from config import Config
from ui.main_window import MainWindow


class Explorer:
    def __init__(self, main_window: MainWindow, resource_directory: Path, config: Config):

        self.main_window = main_window
        self.rsrc_dir = resource_directory
        self.config = config

        # Make it easier to access elements of the UI
        self.ui = self.main_window.ui
        self.opts = self.main_window.ui.opts
        
        # Set up multithreading; MaxThreadCount limited to 1 as checks don't run properly if multiple run concurrently
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        # Set path to mora
        self.mora_path = Path(config.paths[platform.system()])
        self.update_path = Path(config.paths["update"])

        # Define paths to spectrometers based on loaded mora_path
        self.path_300er = self.mora_path / "300er"
        self.path_400er = self.mora_path / "400er"
        self.spectrometer_paths = {
            "300er": self.path_300er,
            "400er": self.path_400er,
        }

        # Check for updates
        self.update_check(Path(config.paths["update"]))

        # Initialize some other variables for later
        self.wild_group = False
        self.copied_list = []
        self.date_selected = date.today()

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
                    self.notify_update(version_no, newest_version_no, changelog)
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
        self.opts.AK_buttons.buttonClicked.connect(self.group_changed)
        self.opts.other_box.currentTextChanged.connect(self.group_changed)
        self.opts.dest_path_input.textChanged.connect(self.main_window.dest_path_changed)
        self.opts.open_button.clicked.connect(self.open_path)
        self.opts.inc_init_checkbox.stateChanged.connect(self.main_window.inc_init_switched)
        self.opts.inc_solv_checkbox.stateChanged.connect(self.main_window.inc_solv_switched)
        self.opts.nmrcheck_style_checkbox.stateChanged.connect(self.main_window.nmrcheck_style_switched)
        self.opts.spec_buttons.buttonClicked.connect(self.main_window.spec_changed)
        self.opts.repeat_check_checkbox.stateChanged.connect(self.main_window.repeat_switched)
        self.opts.repeat_interval.valueChanged.connect(self.main_window.repeat_delay_changed)
        self.opts.save_button.clicked.connect(self.main_window.save)
        self.opts.since_button.toggled.connect(self.main_window.since_function_activated)
        self.opts.date_selector.dateChanged.connect(self.date_changed)
        self.opts.today_button.clicked.connect(self.main_window.set_date_as_today)
        self.opts.hf_date_selector.dateChanged.connect(self.hf_date_changed)
        self.ui.start_check_button.clicked.connect(self.started)
        self.ui.interrupt_button.clicked.connect(self.interrupted)
        self.ui.notification.clicked.connect(self.main_window.notification_clicked)


    def initials_changed(self, new_initials):
        # Allow initials entry to take five characters total if the nmr group is chosen
        # and the wild group option is invoked
        if len(new_initials) > 0:
            if (new_initials.split()[0] == "*") and (self.config.options["group"] == "nmr"):
                self.opts.initials_entry.setMaxLength(5)
                if len(new_initials.split()) > 1:
                    self.wild_group = True
                    self.config.options["initials"] = new_initials.split()[1]
                else:
                    self.config.options["initials"] = ""
            else:
                self.config.options["initials"] = new_initials
        else:
            self.opts.initials_entry.setMaxLength(3)
            self.config.options["initials"] = new_initials
        self.opts.save_button.setEnabled(True)


    def group_changed(self):
        self.main_window.group_changed()
        self.adapt_paths_to_group(self.config.options["group"])


    def adapt_paths_to_group(self, group):
        if group in self.config.groups["other"]:
            path_hf = (
                self.mora_path / "500-600er" / self.config.groups["other"][group]
            )
        else:
            path_hf = self.mora_path / "500-600er" / self.config.groups[group]
        self.spectrometer_paths["hf"] = path_hf
        # If nmr group has been selected, disable the naming option checkboxes as they will be treated as selected anyway
        if group != "nmr":
            # Make sure wild option is turned off for normal users
            self.wild_group = False


    def open_path(self):
        if Path(self.config.options["dest_path"]).exists() is True:
            if platform.system() == "Windows":
                # Extra quotes necessary because cmd.exe can't handle spaces in path names otherwise
                os.system(f'start "" "{self.config.options["dest_path"]}"')
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.config.options["dest_path"]])
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", self.config.options["dest_path"]])


    def date_changed(self):
        self.date_selected = self.opts.date_selector.date().toPython()


    def hf_date_changed(self):
        self.date_selected = self.opts.hf_date_selector.date().toPython()


    def format_date(self, input_date):
        """Convert Python datetime.date object to the same format used in the folder names on Mora."""
        if self.config.options["spec"] == "hf":
            formatted_date = input_date.strftime("%Y")
        else:
            formatted_date = input_date.strftime("%b%d-%Y")
        return formatted_date


    def started(self):
        self.queued_checks = 0
        if self.opts.only_button.isChecked() is True or self.config.options["spec"] == "hf":
            self.single_check(self.date_selected)
        elif self.opts.since_button.isChecked() is True:
            self.multiday_check(self.date_selected)


    def single_check(self, date):
        self.ui.start_check_button.setEnabled(False)
        formatted_date = self.format_date(date)
        # Start main checking function in worker thread
        worker = Worker(
            check_nmr,
            self.config.options,
            formatted_date,
            self.mora_path,
            self.spectrometer_paths,
            self.wild_group,
            self.ui.prog_bar,
        )
        worker.signals.progress.connect(self.update_progress)
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


    def handle_output(self, final_output):
        self.copied_list = final_output


    def check_ended(self):
        # Set progress to 100% just in case it didn't reach it for whatever reason
        self.ui.prog_bar.setMaximum(1)
        self.ui.prog_bar.setValue(1)
        # Will only not be true if an unknown error occurred, in all cases len will be at least 2
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
            # Unknown error occurred, output of check function was returned without appending anything to copied_list
            self.copied_list.pop(0)
            self.main_window.notify_spectra(self.copied_list)
        # Display output
        for entry in self.copied_list:
            entry_label = QLabel(entry)
            self.ui.display.add_entry(entry_label)
        # Behaviour for repeat check function. Deactivate for hf spectrometer. See also self.timer in init function
        if (self.config.options["repeat_switch"] is True) and (self.config.options["spec"] != "hf"):
            self.ui.start_check_button.hide()
            self.ui.interrupt_button.show()
            self.timer.start(int(self.config.options["repeat_delay"]) * 60 * 1000)
        # Enable start check button again, but only if all queued checks have finished
        self.queued_checks -= 1
        if self.queued_checks == 0:
            self.ui.start_check_button.setEnabled(True)
            logging.info("Task complete")


    def interrupted(self):
        self.timer.stop()
        self.ui.start_check_button.show()
        self.ui.interrupt_button.hide()


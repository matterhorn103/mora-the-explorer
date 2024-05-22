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
from ui.layout import Layout


class MainWindow(QMainWindow):
    def __init__(self, resource_directory: Path, config: Config):
        super().__init__()

        self.rsrc_dir = resource_directory
        self.config = config
        
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

        # Timer for repeat check, starts checking function when timer runs out
        self.timer = QTimer().setSingleShot(True)
        self.timer.timeout.connect(self.started)

        # Setup UI
        self.setup_ui()
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
            logging.info("Permission to access server denied")
            failed_permission_dialog = QMessageBox(self)
            failed_permission_dialog.setWindowTitle("Access to mora server denied")
            failed_permission_dialog.setText(
                """
You have been denied permission to access the mora server.
Check the connection and your authentication details and try again.
The program will now close.
            """
            )
            failed_permission_dialog.exec()
            sys.exit()


    def notify_update(self, current, available, changelog):
        """Spawn popup to notify user that an update is available, with version info."""

        update_dialog = QMessageBox(self)
        update_dialog.setWindowTitle("Update available")
        update_dialog.setText(f"There appears to be a new update available at:\n{self.update_path}")
        update_dialog.setInformativeText(
            f"Your version is {current}\nThe version on the server is {available}\n{changelog}"
        )
        update_dialog.setStandardButtons(QMessageBox.Ignore | QMessageBox.Open)
        update_dialog.setDefaultButton(QMessageBox.Ignore)
        choice = update_dialog.exec()
        if choice == QMessageBox.Open:
            if self.update_path.exists() is True:
                # Extra quotes necessary because cmd.exe can't handle spaces in path names otherwise
                os.system(f'start "" "{self.update_path}"')


    def setup_ui(self):
        """Setup main layout, which is a simple vertical stack."""

        self.ui = Layout()
        # Add central widget and give it main layout
        layout_widget = QWidget()
        layout_widget.setLayout(self.ui)
        self.setCentralWidget(layout_widget)

        # Trigger function to adapt available options and spectrometers to the user's group
        self.adapt_to_group()
        # Trigger functions to adapt date selector and naming options to the selected spectrometer
        self.adapt_to_spec()

        # Set up window. macos spaces things out more than Windows so give it a bigger window
        if platform.system() == "Windows":
            self.setMinimumSize(QSize(420, 680))
        else:
            self.setMinimumSize(QSize(450, 780))
        
        # Make options easily accessible, as they are frequently accessed
        self.opts = self.ui.opts


    def connect_signals(self):
        """Connect all the signals from the UI elements to the various handlers."""

        self.ui.opts.initials_entry.textChanged.connect(self.initials_changed)
        self.ui.opts.AK_buttons.buttonClicked.connect(self.group_changed)
        self.ui.opts.other_box.currentTextChanged.connect(self.group_changed)
        self.ui.opts.dest_path_input.textChanged.connect(self.dest_path_changed)
        self.ui.opts.open_button.clicked.connect(self.open_path)
        self.ui.opts.inc_init_checkbox.stateChanged.connect(self.inc_init_switched)
        self.ui.opts.inc_solv_checkbox.stateChanged.connect(self.inc_solv_switched)
        self.ui.opts.nmrcheck_style_checkbox.stateChanged.connect(self.nmrcheck_style_switched)
        self.ui.opts.spec_buttons.buttonClicked.connect(self.spec_changed)
        self.ui.opts.repeat_check_checkbox.stateChanged.connect(self.repeat_switched)
        self.ui.opts.repeat_interval.valueChanged.connect(self.repeat_delay_changed)
        self.ui.opts.save_button.clicked.connect(self.save)
        self.ui.opts.since_button.toggled.connect(self.since_function_activated)
        self.ui.opts.date_selector.dateChanged.connect(self.date_changed)
        self.ui.opts.today_button.clicked.connect(self.set_date_as_today)
        self.ui.opts.hf_date_selector.dateChanged.connect(self.hf_date_changed)
        self.ui.start_check_button.clicked.connect(self.started)
        self.ui.interrupt_button.clicked.connect(self.interrupted)
        self.ui.notification.clicked.connect(self.notification_clicked)


    def since_function_activated(self):
        """Spawn popup dialog that dissuades user from using the "since" function regularly."""

        since_message = """
The function to check multiple days at a time should not be used on a regular basis.
Please switch back to a single-day check once your search is finished.
The repeat function is also disabled as long as this option is selected.
            """
        if self.opts.since_button.isChecked() is True and self.config.options["group"] != "nmr":
            QMessageBox.warning(self, "Warning", since_message)
            self.opts.repeat_check_checkbox.setEnabled(False)
            self.config.options["repeat_switch"] = False
        else:
            self.opts.repeat_check_checkbox.setEnabled(True)
            self.config.options["repeat_switch"] = self.repeat_check_checkbox.isChecked()


    def initials_changed(self, new_initials):
        # Allow initials entry to take five characters total if the nmr group is chosen and the wild group option is invoked
        if len(new_initials) > 0:
            if (self.config.options["group"] == "nmr") and (new_initials.split()[0] == "*"):
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
        if self.opts.AK_buttons.checkedButton().text() == "other":
            self.config.options["group"] = self.opts.other_box.currentText()
        else:
            self.config.options["group"] = self.opts.AK_buttons.checkedButton().text()
        self.adapt_to_group()
        self.opts.save_button.setEnabled(True)
    

    def adapt_to_group(self):
        if self.config.options["group"] in self.config.groups["other"]:
            self.opts.other_box.show()
            path_hf = (
                self.mora_path / "500-600er" / self.config.groups["other"][self.config.options["group"]]
            )
        else:
            self.opts.other_box.hide()
            path_hf = self.mora_path / "500-600er" / self.config.groups[self.config.options["group"]]
        self.spectrometer_paths["hf"] = path_hf
        # If nmr group has been selected, disable the naming option checkboxes as they will be treated as selected anyway
        if self.config.options["group"] == "nmr":
            self.opts.inc_init_checkbox.setEnabled(False)
            self.opts.nmrcheck_style_checkbox.setEnabled(False)
        else:
            # Only enable initials checkbox if nmrcheck_style option is not selected, disable otherwise
            self.opts.inc_init_checkbox.setEnabled(not self.config.options["nmrcheck_style"])
            self.opts.nmrcheck_style_checkbox.setEnabled(True)
            # Make sure wild option is turned off for normal users
            self.wild_group = False
        if self.config.options["group"] == "nmr" or self.config.options["spec"] == "hf":
            self.opts.inc_solv_checkbox.setEnabled(False)
        else:
            self.opts.inc_solv_checkbox.setEnabled(True)
        self.refresh_visible_specs()


    def dest_path_changed(self, new_path):
        formatted_path = new_path
        # Best way to ensure cross-platform compatibility is to avoid use of backslashes and then let pathlib.Path take care of formatting
        if "\\" in formatted_path:
            formatted_path = formatted_path.replace("\\", "/")
        # If the option "copy path" is used in Windows Explorer and then pasted into the box, the path will be surrounded by quotes, so remove them if there
        if formatted_path[0] == '"':
            formatted_path = formatted_path.replace('"', "")
        self.config.options["dest_path"] = formatted_path
        self.opts.open_button.show()
        self.opts.save_button.setEnabled(True)


    def open_path(self):
        if Path(self.config.options["dest_path"]).exists() is True:
            if platform.system() == "Windows":
                # Extra quotes necessary because cmd.exe can't handle spaces in path names otherwise
                os.system(f'start "" "{self.config.options["dest_path"]}"')
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.config.options["dest_path"]])
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", self.config.options["dest_path"]])


    def inc_init_switched(self):
        self.config.options["inc_init"] = self.opts.inc_init_checkbox.isChecked()
        self.opts.save_button.setEnabled(True)


    def inc_solv_switched(self):
        self.config.options["inc_solv"] = self.opts.inc_solv_checkbox.isChecked()
        self.opts.save_button.setEnabled(True)


    def nmrcheck_style_switched(self):
        self.config.options["nmrcheck_style"] = self.opts.nmrcheck_style_checkbox.isChecked()
        self.opts.save_button.setEnabled(True)
        self.opts.inc_init_checkbox.setEnabled(not self.opts.nmrcheck_style_checkbox.isChecked())
        self.adapt_to_spec()


    def refresh_visible_specs(self):
        if self.config.options["group"] in ["stu", "nae", "nmr"]:
            self.opts.spec_buttons.buttons["300er"].show()
        else:
            self.opts.spec_buttons.buttons["300er"].hide()


    def spec_changed(self):
        self.config.options["spec"] = self.opts.spec_buttons.checkedButton().name
        self.adapt_to_spec()
        self.opts.save_button.setEnabled(True)


    def adapt_to_spec(self):
        if self.config.options["spec"] == "hf":
            # Including the solvent in the title is not supported for high-field measurements so disable option
            self.opts.inc_solv_checkbox.setEnabled(False)
            self.opts.repeat_check_checkbox.setEnabled(False)
            self.opts.date_selector.hide()
            self.opts.today_button.setEnabled(False)
            self.opts.hf_date_selector.show()
        else:
            if self.config.options["group"] != "nmr" and self.config.options["nmrcheck_style"] is False:
                self.opts.inc_solv_checkbox.setEnabled(True)
            self.opts.repeat_check_checkbox.setEnabled(True)
            self.opts.hf_date_selector.hide()
            self.opts.date_selector.show()
            self.opts.today_button.setEnabled(True)


    def repeat_switched(self):
        self.config.options["repeat_switch"] = self.opts.repeat_check_checkbox.isChecked()
        self.opts.save_button.setEnabled(True)


    def repeat_delay_changed(self, new_delay):
        self.config.options["repeat_delay"] = new_delay
        self.opts.save_button.setEnabled(True)


    def save(self):
        self.config.save()
        self.opts.save_button.setEnabled(False)


    def date_changed(self):
        self.date_selected = self.opts.date_selector.date().toPython()


    def hf_date_changed(self):
        self.date_selected = self.opts.hf_date_selector.date().toPython()


    def set_date_as_today(self):
        self.opts.date_selector.setDate(date.today())


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
        self.opts.start_check_button.setEnabled(False)
        formatted_date = self.format_date(date)
        # Start main checking function in worker thread
        worker = Worker(
            check_nmr,
            self.config.options,
            formatted_date,
            self.mora_path,
            self.spectrometer_paths,
            self.wild_group,
            self.prog_bar,
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
                self.notify(self.copied_list)
            # No spectra were found but check completed successfully
            elif self.copied_list[1][:5] == "check":
                pass
            # Known error occurred
            else:
                self.copied_list.pop(0)
                self.notify(self.copied_list)
        else:
            # Unknown error occurred, output of check function was returned without appending anything to copied_list
            self.copied_list.pop(0)
            self.notify(self.copied_list)
        # Display output
        for entry in self.copied_list:
            entry_label = QLabel(entry)
            self.ui.display.add_entry(entry_label)
            # Move scroll area so that the user sees immediately which spectra were found or what the error was - but only the first time this happens (haven't been able to make this work)
            # if entry == self.copied_list[0] and self.copied_list[0][:5] != "check":
            # QApplication.processEvents()
            # self.display_scroll.ensureWidgetVisible(entry_label, ymargin=50)
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


    def notify(self, copied_list):
        # If spectra were found, the list will have len > 1, if a known error occurred, the list will have len 1, if an unknown error occurred, the list will be empty
        if len(copied_list) > 1:
            notification_text = "Spectra have been found!"
            self.ui.notification.setText(notification_text + " Ctrl+G to go to. Click to dismiss")
            self.ui.notification.setStyleSheet("background-color : limegreen")
        else:
            self.ui.notification.setStyleSheet("background-color : #cc0010; color : white")
            try:
                notification_text = "Error: " + copied_list[0]
            except:
                notification_text = "Unknown error occurred."
            self.ui.notification.setText(notification_text + " Click to dismiss")
        self.ui.notification.show()
        if self.since_button.isChecked() is False and platform.system() != "Darwin":
            # Display system notification - doesn't seem to be implemented for macOS currently
            # Only if a single date is checked, because with the since function the system notifications get annoying
            try:
                plyer.notification.notify(
                    title="Hola!",
                    message=notification_text,
                    app_name="Mora the Explorer",
                    timeout=2,
                )
            except:
                pass


    def notification_clicked(self):
        self.ui.notification.hide()

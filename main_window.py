"""
Mora the Explorer checks for new NMR spectra at the Organic Chemistry department at the University of Münster.
Copyright (C) 2023 Matthew J. Milner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import logging
import os
import platform
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import plyer

from PySide6.QtCore import QSize, QTimer, Qt, QRunnable, Signal, Slot, QThreadPool, QObject
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QLabel,
    QLineEdit,
    QDateEdit,
    QCheckBox,
    QSpinBox,
    QProgressBar,
    QScrollArea,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QMessageBox,
)

from checknmr import check_nmr
from config import Config


class WorkerSignals(QObject):
    progress = Signal(int)
    result = Signal(object)
    completed = Signal()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Pass function itself, along with provided arguments, to new function within the Checker instance
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        # Give the Checker signals
        self.signals = WorkerSignals()
        # Add the callback to kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        # Run the Worker function with passed args, kwargs, including progress_callback
        output = self.fn(*self.args, **self.kwargs)
        # Emit the output of the function as the result signal so that it can be picked up
        self.signals.result.emit(output)
        self.signals.completed.emit()


class MainWindow(QMainWindow):
    def __init__(self, resource_directory: Path, config: Config):
        super().__init__()

        self.rsrc_dir = resource_directory
        self.config = config
        self.options = config.options
        
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

        # Title and version info header
        self.setWindowTitle("Mora the Explorer")
        with open(self.rsrc_dir / "version.txt", encoding="utf-8") as f:
            version_info = "".join(f.readlines()[:5])
        version_box = QLabel(version_info)
        version_box.setAlignment(Qt.AlignHCenter)

        # Setup layouts
        layout = QVBoxLayout()
        layout.addWidget(version_box)
        options_layout = QGridLayout()
        groups_layout = QHBoxLayout()
        groups_overflow = QHBoxLayout()
        spec_layout = QVBoxLayout()
        options_layout.addLayout(groups_layout, 1, 1)
        options_layout.addLayout(groups_overflow, 2, 1)
        options_layout.addLayout(spec_layout, 6, 1, 1, 2)
        layout.addLayout(options_layout)
        # Add central widget and give it parent layout
        layout_widget = QWidget()
        layout_widget.setLayout(layout)
        self.setCentralWidget(layout_widget)

        # Initials entry box
        initials_label = QLabel("initials:")
        initials_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(initials_label, 0, 0)

        self.initials_entry = QLineEdit()
        self.initials_entry.setMaxLength(3)
        self.initials_entry.setText(self.options["initials"])
        # Initialize wild option for later (see initials_changed function)
        self.wild_group = False
        self.initials_entry.textChanged.connect(self.initials_changed)
        options_layout.addWidget(self.initials_entry, 0, 1)

        initials_hint = QLabel("(lowercase!)")
        initials_hint.setAlignment(Qt.AlignCenter)
        options_layout.addWidget(initials_hint, 0, 2)

        # Research group selection buttons
        group_label = QLabel("group:")
        group_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(group_label, 1, 0)

        # Add radio button for each group in config.groups (loaded earlier)
        self.AKlist = list(self.config.groups.keys())
        self.AK_button_group = QButtonGroup(layout_widget)
        self.button_list = []
        for AK in self.AKlist:
            AKbutton = QRadioButton(AK)
            self.button_list.append(AKbutton)
            if (AK == self.options["group"]) or (
                AK == "other" and self.AK_button_group.checkedButton() is None
            ):
                AKbutton.setChecked(True)
            self.AK_button_group.addButton(AKbutton)
            if len(self.AKlist) <= 4 or self.AKlist.index(AK) < (len(self.AKlist) / 2):
                groups_layout.addWidget(AKbutton)
            elif len(self.AKlist) > 4 and self.AKlist.index(AK) >= (len(self.AKlist) / 2):
                groups_overflow.addWidget(AKbutton)
        self.AK_button_group.buttonClicked.connect(self.group_changed)

        # Drop down list for further options that appears only when "other" radio button is clicked
        self.AKlist_other = list(self.config.groups["other"].values())
        self.other_box = QComboBox()
        self.other_box.addItems(self.AKlist_other)
        if self.options["group"] in self.AKlist_other:
            self.other_box.setCurrentText(self.options["group"])
        else:
            self.other_box.hide()
        self.other_box.currentTextChanged.connect(self.group_changed)
        options_layout.addWidget(self.other_box, 2, 2)

        # Destination path entry box
        dest_path_label = QLabel("save in:")
        dest_path_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(dest_path_label, 3, 0)

        dest_path_input = QLineEdit()
        dest_path_input.setText(self.options["dest_path"])
        dest_path_input.textChanged.connect(self.dest_path_changed)
        options_layout.addWidget(dest_path_input, 3, 1)

        self.open_button = QPushButton("go to")
        self.open_button.clicked.connect(self.open_path)
        self.open_button.setShortcut("Ctrl+G")
        options_layout.addWidget(self.open_button, 3, 2)
        # Disable button if path hasn't yet been specified to stop new users thinking it should be used to select a folder
        if self.options["dest_path"] == "copy full path here":
            self.open_button.hide()

        # File naming options
        file_naming_layout = QHBoxLayout()

        include_label = QLabel("include:")
        include_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(include_label, 4, 0)

        self.inc_init_checkbox = QCheckBox("initials")
        self.inc_init_checkbox.setChecked(self.options["inc_init"])
        self.inc_init_checkbox.stateChanged.connect(self.inc_init_switched)
        if self.options["nmrcheck_style"] is True:
            self.inc_init_checkbox.setEnabled(False)
        file_naming_layout.addWidget(self.inc_init_checkbox)

        self.inc_solv_checkbox = QCheckBox("solvent")
        self.inc_solv_checkbox.setChecked(self.options["inc_solv"])
        self.inc_solv_checkbox.stateChanged.connect(self.inc_solv_switched)
        if self.options["spec"] == "hf":
            self.inc_solv_checkbox.setEnabled(False)
        file_naming_layout.addWidget(self.inc_solv_checkbox)

        options_layout.addLayout(file_naming_layout, 4, 1)

        in_filename_label = QLabel("...in filename")
        in_filename_label.setAlignment(Qt.AlignCenter)
        options_layout.addWidget(in_filename_label, 4, 2)

        # Option to use NMRCheck-style formatting of folder names
        self.nmrcheck_style_checkbox = QCheckBox("use comprehensive (NMRCheck) style")
        self.nmrcheck_style_checkbox.setChecked(self.options["nmrcheck_style"])
        self.nmrcheck_style_checkbox.stateChanged.connect(self.nmrcheck_style_switched)
        options_layout.addWidget(self.nmrcheck_style_checkbox, 5, 1, 1, 2)

        # Spectrometer selection buttons
        spec_label = QLabel("search:")
        spec_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        options_layout.addWidget(spec_label, 6, 0)

        self.spectrometer_text = {
            "300er": "Studer group NMR only (300 MHz)",
            "400er": "routine NMR (300 && 400 MHz)",
            "hf": "high-field spectrometers (500 && 600 MHz)",
        }
        self.spec_list = list(self.spectrometer_text.keys())
        self.spec_button_group = QButtonGroup(layout_widget)
        self.spec_button_dict = {}
        self.spec_button_list = []
        for spec in self.spec_list:
            spec_button = QRadioButton(self.spectrometer_text[spec])
            if self.options["spec"] == spec:
                spec_button.setChecked(True)
            self.spec_button_group.addButton(spec_button)
            self.spec_button_dict[spec_button] = spec
            self.spec_button_list.append(spec_button)
            spec_button.toggled.connect(self.spec_changed)
            spec_layout.addWidget(spec_button)

        # Checkbox to instruct to repeat after chosen interval
        repeat_layout = QHBoxLayout()

        repeat_label = QLabel("repeat:")
        repeat_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(repeat_label, 7, 0)

        self.repeat_check_checkbox = QCheckBox("check every")
        self.repeat_check_checkbox.setChecked(self.options["repeat_switch"])
        self.repeat_check_checkbox.stateChanged.connect(self.repeat_switched)
        repeat_layout.addWidget(self.repeat_check_checkbox)

        repeat_interval = QSpinBox()
        repeat_interval.setMinimum(1)
        repeat_interval.setValue(self.options["repeat_delay"])
        repeat_interval.valueChanged.connect(self.repeat_delay_changed)
        repeat_layout.addWidget(repeat_interval)

        repeat_mins = QLabel("mins")
        repeat_layout.addWidget(repeat_mins)

        options_layout.addLayout(repeat_layout, 7, 1)

        # Button to save all options for future
        self.save_button = QPushButton("save options as defaults for next time")
        self.save_button.clicked.connect(self.save)
        options_layout.addWidget(self.save_button, 8, 0, 1, 3)
        self.save_button.setEnabled(False)

        # Initialize date variable
        self.date_selected = date.today()

        # Date selection tool for 300er and 400er
        date_label = QLabel("when?")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(date_label, 9, 0)

        date_layout = QHBoxLayout()
        options_layout.addLayout(date_layout, 9, 1)
        self.only_button = QRadioButton("only")
        self.since_button = QRadioButton("since")
        date_layout.addWidget(self.only_button, 0)
        date_layout.addWidget(self.since_button, 1)
        self.date_button_group = QButtonGroup(layout_widget)
        self.date_button_group.addButton(self.only_button)
        self.date_button_group.addButton(self.since_button)
        self.date_button_list = [self.only_button, self.since_button]
        self.since_button.toggled.connect(self.since_function_activated)
        self.only_button.setChecked(True)

        self.date_selector = QDateEdit()
        self.date_selector.setDisplayFormat("dd MMM yyyy")
        self.date_selector.setDate(date.today())
        self.date_selector.dateChanged.connect(self.date_changed)
        date_layout.addWidget(self.date_selector, 2)

        self.today_button = QPushButton("today")
        options_layout.addWidget(self.today_button, 9, 2)
        self.today_button.clicked.connect(self.set_date_as_today)

        # Date selection tool for hf (only needs year)
        self.hf_date_selector = QDateEdit()
        self.hf_date_selector.setDisplayFormat("yyyy")
        self.hf_date_selector.setDate(date.today())
        self.hf_date_selector.dateChanged.connect(self.hf_date_changed)
        options_layout.addWidget(self.hf_date_selector, 9, 1)

        # Button to begin check
        self.start_check_button = QPushButton("start check now")
        self.start_check_button.setStyleSheet("background-color : #b88cce")
        layout.addWidget(self.start_check_button)
        self.start_check_button.clicked.connect(self.started)

        # Button to cancel pending repeat check
        self.interrupt_button = QPushButton("cancel repeat check")
        self.interrupt_button.setStyleSheet("background-color : #cc0010; color : white")
        layout.addWidget(self.interrupt_button)
        self.interrupt_button.clicked.connect(self.interrupted)
        self.interrupt_button.hide()

        # Timer for repeat check, starts checking function when timer runs out
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.started)

        # Progress bar for check
        self.prog_bar = QProgressBar()
        self.prog_bar.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        layout.addWidget(self.prog_bar)

        # Box to display output of check function (list of copied spectra)
        self.copied_list = []
        self.display_layout = QVBoxLayout()
        self.display = QWidget()
        self.display.setLayout(self.display_layout)
        self.display_scroll = QScrollArea()
        self.display_scroll.setWidgetResizable(True)
        self.display_scroll.setWidget(self.display)
        layout.addWidget(self.display_scroll)

        # Extra notification that spectra have been found, dismissable
        self.notification = QPushButton()
        layout.addWidget(self.notification)
        self.notification.clicked.connect(self.notification_clicked)
        self.notification.hide()

        # Trigger function to adapt available options and spectrometers to the user's group
        self.adapt_to_group()
        # Trigger functions to adapt date selector and naming options to the selected spectrometer
        self.adapt_to_spec()

        # Set up window. macos spaces things out more than windows so give it a bigger window
        if platform.system() == "Windows":
            self.setMinimumSize(QSize(380, 650))
        else:
            self.setMinimumSize(QSize(450, 780))

    # Now come all the other functions

    # Define function to check for updates at location specified
    def update_check(self, update_path):
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
                if version_no == "v1.6.0" and not (self.rsrc_dir / "notified.txt").exists():
                    self.notify_changelog(changelog)
                    with open((self.rsrc_dir / "notified.txt"), "w") as f:
                        # Save empty file so that the user is not notified next time
                        pass
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

    # Popup to notify user that an update is available, with version info
    def notify_update(self, current, available, changelog):
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

    # Popup to show changelog for current version upon upgrade to v1.6.0
    def notify_changelog(self, changelog):
        QMessageBox.information(self, "Changes in v1.6.0", changelog)

    # Spawn popup dialog that dissuades user from using the "since" function regularly, unless the nmr group has been selected
    def since_function_activated(self):
        since_message = """
The function to check multiple days at a time should not be used on a regular basis.
Please switch back to a single-day check once your search is finished.
The repeat function is also disabled as long as this option is selected.
            """
        if self.since_button.isChecked() is True and self.options["group"] != "nmr":
            QMessageBox.warning(self, "Warning", since_message)
            self.repeat_check_checkbox.setEnabled(False)
            self.options["repeat_switch"] = False
        else:
            self.repeat_check_checkbox.setEnabled(True)
            self.options["repeat_switch"] = self.repeat_check_checkbox.isChecked()

    def initials_changed(self, new_initials):
        # Allow initials entry to take five characters total if the nmr group is chosen and the wild group option is invoked
        if len(new_initials) > 0:
            if (self.options["group"] == "nmr") and (new_initials.split()[0] == "*"):
                self.initials_entry.setMaxLength(5)
                if len(new_initials.split()) > 1:
                    self.wild_group = True
                    self.options["initials"] = new_initials.split()[1]
                else:
                    self.options["initials"] = ""
            else:
                self.options["initials"] = new_initials
        else:
            self.initials_entry.setMaxLength(3)
            self.options["initials"] = new_initials
        self.save_button.setEnabled(True)

    def group_changed(self):
        if self.AK_button_group.checkedButton().text() == "other":
            self.options["group"] = self.other_box.currentText()
        else:
            self.options["group"] = self.AK_button_group.checkedButton().text()
        self.adapt_to_group()
        self.save_button.setEnabled(True)
    
    def adapt_to_group(self):
        if self.options["group"] in self.config.groups["other"]:
            self.other_box.show()
            path_hf = (
                self.mora_path / "500-600er" / self.config.groups["other"][self.options["group"]]
            )
        else:
            self.other_box.hide()
            path_hf = self.mora_path / "500-600er" / self.config.groups[self.options["group"]]
        self.spectrometer_paths["hf"] = path_hf
        # If nmr group has been selected, disable the naming option checkboxes as they will be treated as selected anyway
        if self.options["group"] == "nmr":
            self.inc_init_checkbox.setEnabled(False)
            self.nmrcheck_style_checkbox.setEnabled(False)
        else:
            # Only enable initials checkbox if nmrcheck_style option is not selected, disable otherwise
            self.inc_init_checkbox.setEnabled(not self.options["nmrcheck_style"])
            self.nmrcheck_style_checkbox.setEnabled(True)
            # Make sure wild option is turned off for normal users
            self.wild_group = False
        if self.options["group"] == "nmr" or self.options["spec"] == "hf":
            self.inc_solv_checkbox.setEnabled(False)
        else:
            self.inc_solv_checkbox.setEnabled(True)
        self.refresh_visible_specs()

    def dest_path_changed(self, new_path):
        formatted_path = new_path
        # Best way to ensure cross-platform compatibility is to avoid use of backslashes and then let pathlib.Path take care of formatting
        if "\\" in formatted_path:
            formatted_path = formatted_path.replace("\\", "/")
        # If the option "copy path" is used in Windows Explorer and then pasted into the box, the path will be surrounded by quotes, so remove them if there
        if formatted_path[0] == '"':
            formatted_path = formatted_path.replace('"', "")
        self.options["dest_path"] = formatted_path
        self.open_button.show()
        self.save_button.setEnabled(True)

    def open_path(self):
        if Path(self.options["dest_path"]).exists() is True:
            if platform.system() == "Windows":
                # Extra quotes necessary because cmd.exe can't handle spaces in path names otherwise
                os.system(f'start "" "{self.options["dest_path"]}"')
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.options["dest_path"]])
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", self.options["dest_path"]])

    def inc_init_switched(self):
        self.options["inc_init"] = self.inc_init_checkbox.isChecked()
        self.save_button.setEnabled(True)

    def inc_solv_switched(self):
        self.options["inc_solv"] = self.inc_solv_checkbox.isChecked()
        self.save_button.setEnabled(True)

    def nmrcheck_style_switched(self):
        self.options["nmrcheck_style"] = self.nmrcheck_style_checkbox.isChecked()
        self.save_button.setEnabled(True)
        self.inc_init_checkbox.setEnabled(not self.nmrcheck_style_checkbox.isChecked())
        self.adapt_to_spec()

    def refresh_visible_specs(self):
        if self.options["group"] in ["stu", "nae", "nmr"]:
            self.spec_button_list[0].show()
        else:
            self.spec_button_list[0].hide()

    def spec_changed(self):
        self.options["spec"] = self.spec_button_dict[self.spec_button_group.checkedButton()]
        self.adapt_to_spec()
        self.save_button.setEnabled(True)

    def adapt_to_spec(self):
        if self.options["spec"] == "hf":
            # Including the solvent in the title is not supported for high-field measurements so disable option
            self.inc_solv_checkbox.setEnabled(False)
            self.repeat_check_checkbox.setEnabled(False)
            self.date_selector.hide()
            self.today_button.setEnabled(False)
            self.hf_date_selector.show()
        else:
            if self.options["group"] != "nmr" and self.options["nmrcheck_style"] is False:
                self.inc_solv_checkbox.setEnabled(True)
            self.repeat_check_checkbox.setEnabled(True)
            self.hf_date_selector.hide()
            self.date_selector.show()
            self.today_button.setEnabled(True)

    def repeat_switched(self):
        self.options["repeat_switch"] = self.repeat_check_checkbox.isChecked()
        self.save_button.setEnabled(True)

    def repeat_delay_changed(self, new_delay):
        self.options["repeat_delay"] = new_delay
        self.save_button.setEnabled(True)

    def save(self):
        self.config.save()
        self.save_button.setEnabled(False)

    def date_changed(self):
        self.date_selected = self.date_selector.date().toPython()

    def hf_date_changed(self):
        self.date_selected = self.hf_date_selector.date().toPython()

    def set_date_as_today(self):
        self.date_selector.setDate(date.today())

    # Converts Python datetime.date object to the same format used in the folder names on Mora
    def format_date(self, input_date):
        if self.options["spec"] == "hf":
            formatted_date = input_date.strftime("%Y")
        else:
            formatted_date = input_date.strftime("%b%d-%Y")
        return formatted_date

    def started(self):
        self.queued_checks = 0
        if self.only_button.isChecked() is True or self.options["spec"] == "hf":
            self.single_check(self.date_selected)
        elif self.since_button.isChecked() is True:
            self.multiday_check(self.date_selected)

    def single_check(self, date):
        self.start_check_button.setEnabled(False)
        formatted_date = self.format_date(date)
        # Start main checking function in worker thread
        worker = Worker(
            check_nmr,
            self.options,
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
        self.prog_bar.setValue(prog_state)

    def handle_output(self, final_output):
        self.copied_list = final_output

    def check_ended(self):
        # Set progress to 100% just in case it didn't reach it for whatever reason
        self.prog_bar.setMaximum(1)
        self.prog_bar.setValue(1)
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
            self.display_layout.addWidget(entry_label)
            # Move scroll area so that the user sees immediately which spectra were found or what the error was - but only the first time this happens (haven't been able to make this work)
            # if entry == self.copied_list[0] and self.copied_list[0][:5] != "check":
            # QApplication.processEvents()
            # self.display_scroll.ensureWidgetVisible(entry_label, ymargin=50)
        # Behaviour for repeat check function. Deactivate for hf spectrometer. See also self.timer in init function
        if (self.options["repeat_switch"] is True) and (self.options["spec"] != "hf"):
            self.start_check_button.hide()
            self.interrupt_button.show()
            self.timer.start(int(self.options["repeat_delay"]) * 60 * 1000)
        # Enable start check button again, but only if all queued checks have finished
        self.queued_checks -= 1
        if self.queued_checks == 0:
            self.start_check_button.setEnabled(True)
            logging.info("Task complete")

    def interrupted(self):
        self.timer.stop()
        self.start_check_button.show()
        self.interrupt_button.hide()

    def notify(self, copied_list):
        # If spectra were found, the list will have len > 1, if a known error occurred, the list will have len 1, if an unknown error occurred, the list will be empty
        if len(copied_list) > 1:
            notification_text = "Spectra have been found!"
            self.notification.setText(notification_text + " Ctrl+G to go to. Click to dismiss")
            self.notification.setStyleSheet("background-color : limegreen")
        else:
            self.notification.setStyleSheet("background-color : #cc0010; color : white")
            try:
                notification_text = "Error: " + copied_list[0]
            except:
                notification_text = "Unknown error occurred."
            self.notification.setText(notification_text + " Click to dismiss")
        self.notification.show()
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
        self.notification.hide()

import logging
import os
import platform
import sys
from datetime import date
from pathlib import Path

import plyer

from PySide6.QtCore import QSize, QUrl
from PySide6.QtWidgets import QMainWindow, QWidget, QMessageBox
from PySide6.QtGui import QDesktopServices

from ...explorer.config import Config
from .layout import Layout


class MainWindow(QMainWindow):
    def __init__(self, resource_directory: Path, config: Config):
        super().__init__()

        self.rsrc_dir = resource_directory
        self.config = config

        # self.mora_path = Path(config.paths[platform.system()])
        # self.update_path = Path(config.paths["update"])

        # Setup UI
        self.setWindowTitle("Mora the Explorer")
        self.setup_ui()

    def setup_ui(self):
        """Setup main layout, which is a simple vertical stack."""

        self.ui = Layout(self.rsrc_dir, self.config)

        # Make options easily accessible, as they are frequently accessed
        self.opts = self.ui.opts

        # Add central widget and give it main layout
        layout_widget = QWidget()
        layout_widget.setLayout(self.ui)
        self.setCentralWidget(layout_widget)

        # Generate group and spectrometer buttons
        self.opts.add_group_buttons(self.config.groups, self.config.options["group"])
        self.opts.add_spec_buttons(self.config.specs, self.config.options["spec"])

        # Trigger function to adapt available options and spectrometers to the user's group
        self.adapt_to_group(self.config.options["group"])
        # Trigger functions to adapt date selector and naming options to the selected spectrometer
        self.adapt_to_spec(self.config.options["spec"])

        # Set up window. macos spaces things out more than Windows so give it a bigger window
        if platform.system() == "Windows":
            self.setMinimumSize(QSize(420, 680))
        else:
            self.setMinimumSize(QSize(450, 780))

    def notify_spectra(self, copied_list):
        """Tell the user that spectra were found, both in the app and with a system toast."""
        notification_text = "Spectra have been found!"
        self.ui.notification.setText(
            notification_text + " Ctrl+G to go to. Click to dismiss"
        )
        self.ui.notification.setStyleSheet("background-color : limegreen")
        self.ui.notification.show()
        self.send_toast(notification_text)

    def notify_error(self, copied_list):
        """Tell the user that an error occurred, both in the app and with a system toast."""
        self.ui.notification.setStyleSheet(
            "background-color : #cc0010; color : white"
        )
        try:
            if "Error" in copied_list[0]:
                notification_text = "Error: Python " + copied_list[0]
            else:
                notification_text = "Error: " + copied_list[0]
        except IndexError:
            notification_text = "Unknown error occurred."
        self.ui.notification.setText(notification_text + " Click to dismiss")
        self.ui.notification.show()
        self.send_toast(notification_text)

    def send_toast(self, text):
        """Spawn a system toast notification."""
        if (
            self.opts.since_button.isChecked() is False
            and platform.system() != "Darwin"
        ):
            # Display system notification - doesn't seem to be implemented for macOS
            # Only if a single date is checked, because with the since function the
            # system notifications get annoying
            try:
                plyer.notification.notify(
                    title="Hola!",
                    message=text,
                    app_name="Mora the Explorer",
                    timeout=2,
                )
            except:
                pass

    def notification_clicked(self):
        self.ui.notification.hide()

    def notify_update(self, current, available, changelog, path):
        """Spawn popup to notify user that an update is available, with version info."""

        update_dialog = QMessageBox(self)
        update_dialog.setWindowTitle("Update available")
        update_dialog.setText(
            f"There appears to be a new update available at:\n{path}"
        )
        update_dialog.setInformativeText(
            f"Your version is {current}\nThe version on the server is {available}\n{changelog}"
        )
        update_dialog.setStandardButtons(QMessageBox.Ignore | QMessageBox.Open)
        update_dialog.setDefaultButton(QMessageBox.Ignore)
        choice = update_dialog.exec()
        if choice == QMessageBox.Open:
            if path.exists() is True:
                # Extra quotes necessary because cmd.exe can't handle spaces in path names otherwise
                url = QUrl.fromLocalFile(path)
                QDesktopServices.openUrl(url)

    def notify_failed_permissions(self):
        """Spawn popup to notify user that accessing the mora server failed."""

        logging.info("Permission to access server denied")
        failed_permission_dialog = QMessageBox(self)
        failed_permission_dialog.setWindowTitle("Access to mora server denied")
        failed_permission_dialog.setText("""
You have been denied permission to access the mora server.
Check the connection and your authentication details and try again.
The program will now close.""")
        failed_permission_dialog.exec()
        sys.exit()

    def warn_since_function(self):
        """Spawn popup dialog that dissuades user from using the "since" function regularly."""

        since_message = """
The function to check multiple days at a time should not be used on a regular basis.
Please switch back to a single-day check once your search is finished.
The repeat function is also disabled as long as this option is selected.
            """
        QMessageBox.warning(self, "Warning", since_message)

    def group_changed(self):
        """Find out what the new group is, save it to config, make necessary adjustments."""
        if self.opts.group_buttons.checkedButton().text() == "other":
            new_group = self.opts.other_box.currentText()
        else:
            new_group = self.opts.group_buttons.checkedButton().text()
        self.config.options["group"] = new_group
        self.adapt_to_group(new_group)
        self.opts.save_button.setEnabled(True)

    def adapt_to_group(self, group=None):
        if group is None:
            group = self.config.options["group"]
        if group in self.config.groups["other"]:
            self.opts.other_box.show()
        else:
            self.opts.other_box.hide()
        # If nmr group has been selected, disable the initials/solvent naming option
        # checkboxes as they will be treated as selected anyway, and show the options
        # for prepending/appending the path
        if group == "nmr":
            self.opts.inc_init_checkbox.setEnabled(False)
            self.opts.nmrcheck_style_checkbox.hide()
            self.opts.inc_path_checkbox.show()
            self.opts.inc_path_box.show()
        else:
            # Only enable initials checkbox if nmrcheck_style option is not selected,
            # disable otherwise
            self.opts.inc_init_checkbox.setEnabled(
                not self.config.options["nmrcheck_style"]
            )
            self.opts.nmrcheck_style_checkbox.show()
            self.opts.inc_path_checkbox.hide()
            self.opts.inc_path_box.hide()
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

    def inc_init_switched(self):
        self.config.options["inc_init"] = self.opts.inc_init_checkbox.isChecked()
        self.opts.save_button.setEnabled(True)

    def inc_solv_switched(self):
        self.config.options["inc_solv"] = self.opts.inc_solv_checkbox.isChecked()
        self.opts.save_button.setEnabled(True)

    def inc_path_changed(self):
        if self.opts.inc_path_checkbox.isChecked():
            self.config.options["inc_path"] = self.opts.inc_path_box.currentText()
        else:
            self.config.options["inc_path"] = False

    def nmrcheck_style_switched(self):
        self.config.options["nmrcheck_style"] = (
            self.opts.nmrcheck_style_checkbox.isChecked()
        )
        self.opts.save_button.setEnabled(True)
        self.opts.inc_init_checkbox.setEnabled(
            not self.opts.nmrcheck_style_checkbox.isChecked()
        )
        self.adapt_to_spec(self.config.options["spec"])

    def refresh_visible_specs(self):
        for spec in self.config.specs.keys():
            allowed = self.config.specs[spec].get("restrict_to")
            if allowed is None:
                # No list of groups provided in config so will always be shown to all
                continue
            elif self.config.options["group"] in allowed:
                self.opts.spec_buttons.buttons[spec].show()
            else:
                self.opts.spec_buttons.buttons[spec].hide()

    def spec_changed(self):
        self.config.options["spec"] = self.opts.spec_buttons.checkedButton().name
        self.adapt_to_spec(self.config.options["spec"])
        self.opts.save_button.setEnabled(True)

    def adapt_to_spec(self, spec: str):
        self.opts.inc_solv_checkbox.setEnabled(self.config.specs[spec]["allow_solvent"])
        self.opts.repeat_check_checkbox.setEnabled(
            not self.config.specs[spec]["single_check_only"]
        )
        self.opts.date_selector.setDisplayFormat(self.config.specs[spec]["date_entry"])
        if self.config.specs[spec]["single_check_only"]:
            self.opts.only_button.hide()
            self.opts.since_button.hide()
        else:
            self.opts.only_button.show()
            self.opts.since_button.show()

    def repeat_switched(self):
        self.config.options["repeat_switch"] = (
            self.opts.repeat_check_checkbox.isChecked()
        )
        self.opts.save_button.setEnabled(True)

    def repeat_delay_changed(self, new_delay):
        self.config.options["repeat_delay"] = new_delay
        self.opts.save_button.setEnabled(True)

    def save(self):
        self.config.save()
        self.opts.save_button.setEnabled(False)

    def since_function_activated(self):
        if (
            self.opts.since_button.isChecked() is True
            and self.config.options["group"] != "nmr"
        ):
            self.warn_since_function()
            self.opts.repeat_check_checkbox.setEnabled(False)
            self.config.options["repeat_switch"] = False
        else:
            self.opts.repeat_check_checkbox.setEnabled(True)
            self.config.options["repeat_switch"] = (
                self.opts.repeat_check_checkbox.isChecked()
            )

    def set_date_as_today(self):
        self.opts.date_selector.setDate(date.today())

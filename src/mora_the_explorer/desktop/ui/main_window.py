import logging
import platform
from urllib.parse import quote

from PySide6.QtCore import Qt, QSize, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QMessageBox,
)

from ...config import Config
from . import rows
from .display import Display
from .status import StatusBar


def create_version_label(version_header: str) -> QLabel:
    version_info = version_header.splitlines()[:5]
    # Turn into html
    version_info = f'<p style="line-height: 1.1;">{"<br>".join(version_info)}</p>'
    version_label = QLabel(version_info)
    version_label.setAlignment(Qt.AlignHCenter)
    return version_label


class MainWindow(QMainWindow):
    """The main window of the QtWidgets user interface.
    
    The main window is the parent of all the widgets and layouts, and holds all the
    row components.
    It connects all the wiring of the intra-UI logic e.g. responses to user
    interaction.

    The main window stores and maintains a `Config` object that represents the
    current state of the UI and the user's choices.

    A signal is emitted when a check should be launched, which can be intercepted by
    e.g. a `Controller`.
    """

    # A couple of signals we can emit for a Controller to intercept
    started = Signal()
    cancelled = Signal()

    def __init__(self, config: Config, version_header: str, admin_mode: bool):
        super().__init__()

        self.config = config
        self.admin_mode = admin_mode

        self.setWindowTitle("Mora the Explorer")

        if platform.system() == "Windows":
            self.setMinimumSize(QSize(420, 680))
        else:
            # macOS and Linux space things out more than Windows
            self.setMinimumSize(QSize(450, 780))

        # As always with Qt, have to set a central widget and give that widget a
        # layout, but we won't actually need to access the central widget
        central_widget = QWidget()
        self.grid = QGridLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Compose UI
        # First put in a plate with the version information
        self.version_info = create_version_label(version_header)
        self.grid.addWidget(self.version_info, 0, 0, 1, 3)

        # User initials entry
        self.user_entry = rows.FreeEntryField("user:", "(initials)")
        self.user_entry.set_text(config.options.user)
        self.user_entry.add_to_grid(self.grid, 1)

        # User name entry
        self.name_entry = rows.FreeEntryField("name:", None)
        self.name_entry.set_text(config.options.user_name)
        self.name_entry.add_to_grid(self.grid, 2)
        # If config says this should only be active in admin mode, and we aren't
        # in admin mode, then hide it
        if config.admin.user_name_is_admin_only and not admin_mode:
            self.name_entry.hide()

        if not admin_mode:
            # Group entry from an allowed selection, for normal usage
            self.group_entry = rows.OverflowSelector(
                "group:",
                list(config.groups.filter_overflow(False)),
                list(config.groups.filter_overflow(True)),
            )
            self.group_entry.set_selected(config.options.group)
            self.group_entry.add_to_grid(self.grid, 3)
        else:
            # Group entry via free-form entry boxes, for admin usage
            self.group_entry = rows.FreeEntryField("group:", None)
            self.group_entry.set_text(config.options.group)
            self.group_entry.add_to_grid(self.grid, 3)
            self.group_name_entry = rows.FreeEntryField("group name:", None)
            self.group_name_entry.set_text(config.groups.all.get(config.options.group, ""))
            self.group_name_entry.add_to_grid(self.grid, 4)

        # Server path
        self.server_entry = rows.DirSelector("server:")
        self.server_entry.set_path(config.paths.server())
        self.server_entry.add_to_grid(self.grid, 5)

        # Destination path
        self.dest_entry = rows.DirSelector("save in:", "Ctrl+G")
        self.dest_entry.set_path(config.paths.save)
        self.dest_entry.add_to_grid(self.grid, 6)

        # Folder name options
        self.folder_name_options = rows.FolderNameOptions()
        self.folder_name_options.set_checked(
            config.options.inc_user,
            config.options.inc_solvent,
            config.options.inc_frequency,
            config.options.inc_original,
        )
        self.folder_name_options.add_to_grid(self.grid, 7)

        # Spectrometer selection
        self.spec_selector = rows.SpectrometerSelector(config.specs)
        self.refresh_visible_specs()
        self.spec_selector.set_selected(config.options.spec)
        self.spec_selector.add_to_grid(self.grid, 8)

        # Repeat options
        self.repeat_options = rows.RepeatSelector()
        self.repeat_options.set_repeat_checked(config.options.repeat_switch)
        self.repeat_options.set_interval(config.options.repeat_delay)
        self.repeat_options.add_to_grid(self.grid, 9)

        # Save button
        self.save_button = QPushButton("save options as defaults for next time")
        # Remains disabled until the config is changed
        self.save_button.setEnabled(False)
        self.grid.addWidget(self.save_button, 10, 0, 1, 3)

        # Date selection
        self.date_selector = rows.DateSelector()
        self.date_selector.set_multiday(False)
        self.date_selector.add_to_grid(self.grid, 11)

        # Status bar to start and cancel a check, as well as show the status
        # during a check
        self.status_bar = StatusBar()
        self.status_bar.set_colour(config.appearance.start_button_colour)
        self.grid.addWidget(self.status_bar, 12, 0, 1, 3)

        # Progress bar for check
        self.prog_bar = QProgressBar()
        self.prog_bar.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        if platform.system() == "Windows" and platform.release() == "11":
            # Looks bad (with initial Qt Win11 theme at least) so disable text
            self.prog_bar.setTextVisible(False)
        self.grid.addWidget(self.prog_bar, 13, 0, 1, 3)

        # Box to display output of check function (list of copied spectra)
        self.display = Display()
        self.grid.addWidget(self.display, 14, 0, 1, 3)

        # In-app notification that spectra have been found, dismissable
        self.notification = QPushButton()
        self.notification.hide()
        self.grid.addWidget(self.notification, 15, 0, 1, 3)

        # Connect all the signals and slots
        self.version_info.linkActivated.connect(self._on_bug_report_link_clicked)
        self.user_entry.entry_field.textEdited.connect(self._on_user_changed)
        if admin_mode:
            self.group_entry.entry_field.textEdited.connect(self._on_group_changed)
            self.group_name_entry.entry_field.textEdited.connect(self._on_group_name_changed)
        else:
            self.group_entry.buttons.buttonClicked.connect(self._on_group_changed)
            self.group_entry.dropdown.currentIndexChanged.connect(self._on_group_changed)
        self.server_entry.entry_field.textChanged.connect(self._on_server_path_changed)
        self.dest_entry.entry_field.textChanged.connect(self._on_dest_path_changed)
        self.folder_name_options.user_box.toggled.connect(self._on_inc_user_toggled)
        self.folder_name_options.solvent_box.toggled.connect(self._on_inc_solvent_toggled)
        self.folder_name_options.frequency_box.toggled.connect(self._on_inc_frequency_toggled)
        self.folder_name_options.original_box.toggled.connect(self._on_inc_original_toggled)
        self.spec_selector.buttons.buttonClicked.connect(self._on_spec_changed)
        self.repeat_options.repeat_box.toggled.connect(self._on_repeat_toggled)
        self.repeat_options.interval_box.valueChanged.connect(self._on_repeat_delay_changed)
        self.save_button.clicked.connect(self._on_save_button_clicked)
        self.date_selector.date_button_group.buttonClicked.connect(self._on_multiday_toggled)
        #self.date_selector.date_selector.userDateChanged.connect(self._on_date_changed)
        self.notification.clicked.connect(self._on_notification_clicked)
        # Connect the start/cancel buttons directly to the main window's own signals
        self.status_bar.start_button.clicked.connect(self.started)
        self.status_bar.cancel_button.clicked.connect(self.cancelled)

    def refresh_visible_specs(self):
        """Make sure the available spectrometers reflect what's allowed for the current group."""
        for spec, spec_info in self.config.specs.items():
            if self.admin_mode:
                # All should be available, always
                self.spec_selector.set_visible(spec, True)
            elif spec_info.admin_only:
                self.spec_selector.set_visible(spec, False)
            # This means an empty list for `restrict_to` means visible to all
            elif spec_info.restrict_to and self.config.options.group not in spec_info.restrict_to:
                self.spec_selector.set_visible(spec, False)
            else:
                self.spec_selector.set_visible(spec, True)

    def adapt_to_spec(self):
        """Make sure the available options reflect what's allowed for the current spectrometer."""
        current_spec = self.spec_selector.selected()
        spec_info = self.config.specs[current_spec]
        self.repeat_options.set_repeat_enabled(not spec_info.single_check_only)
        self.date_selector.set_multiday_enabled(not spec_info.single_check_only)
        self.date_selector.set_format(spec_info.date_entry)

    def notify_spectra(self):
        """Tell the user that spectra were found, both in the app and with a system toast."""
        notification_text = "Spectra have been found!"
        self.notification.setText(
            notification_text + " Ctrl+G to go to. Click to dismiss"
        )
        self.notification.setStyleSheet("background-color : limegreen")
        self.notification.show()
        #self.send_toast(notification_text)

    def notify_error(self, error: str | None):
        """Tell the user that an error occurred, both in the app and with a system toast."""
        self.notification.setStyleSheet("background-color : #cc0010; color : white")
        if error:
            notification_text = "Error: Python " + error
        else:
            notification_text = "Unknown error occurred."
        self.notification.setText(notification_text + " Click to dismiss")
        self.notification.show()
        #self.send_toast(notification_text)

    #def send_toast(self, text: str):
    #    """Spawn a system toast notification."""
    #    if (
    #        self.opts.since_button.isChecked() is False
    #        and platform.system() != "Darwin"
    #    ):
    #        # Display system notification - doesn't seem to be implemented for macOS
    #        # Only if a single date is checked, because with the since function the
    #        # system notifications get annoying
    #        try:
    #            plyer.notification.notify(
    #                title="Hola!",
    #                message=text,
    #                app_name="Mora the Explorer",
    #                timeout=2,
    #            )
    #        except Exception:
    #            pass

    def notify_update(self, current, available, changelog, path):
        """Spawn popup to notify user that an update is available, with version info."""

        update_dialog = QMessageBox(self)
        update_dialog.setWindowTitle("Update available")
        update_dialog.setText(f"There appears to be a new update available at:\n{path}")
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

    # Slots
    @Slot()
    def _on_bug_report_link_clicked(self, mailto_link: str):
        """Open a draft email containing some basic information."""

        # Get version number
        with open(self.rsrc_dir / "version.txt", encoding="utf-8") as f:
            version_no = f.readlines()[2].strip().replace("<br>", "")
        # Get system info
        os_info = platform.uname()
        # Get path to log
        log_location = str(logging.getLogger().handlers[0].baseFilename)
        email_info = "\n".join([
            f"Version: {version_no}",
            f"System: {os_info.system} {os_info.release}, {os_info.machine}",
            "Description: (please describe your bug)",
            f"Log: (please insert the contents of your log here, found at {log_location})",
        ])
        escaped_info = quote(email_info)
        url = QUrl(
            f"{mailto_link}?subject=Mora%20the%20Explorer%20bug&body={escaped_info}"
        )
        QDesktopServices.openUrl(url)

    @Slot()
    def _on_user_changed(self):
        self.config.options.user = self.user_entry.text()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_name_changed(self):
        self.config.options.user_name = self.name_entry.text()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_group_changed(self):
        if self.admin_mode:
            group = self.group_entry.text()
            self.config.options.group = group
            # If the group is a known one, fill the group name box automatically
            if group in self.config.groups.all:
                self.group_name_entry.set_text(self.config.groups.all[group])
        else:
            self.config.options.group = self.group_entry.selected()
            self.refresh_visible_specs()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_group_name_changed(self):
        self.config.options.group_name = self.group_name_entry.text()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_server_path_changed(self):
        self.config.paths.set_server(self.server_entry.path())
        self.save_button.setEnabled(True)

    @Slot()
    def _on_dest_path_changed(self):
        self.config.paths.save = self.dest_entry.path()
        self.save_button.setEnabled(True)

    #def _on_dest_path_changed(self, new_path):
    #    formatted_path = new_path
    #    # Best way to ensure cross-platform compatibility is to avoid use of backslashes
    #    # and then let pathlib.Path take care of formatting
    #    if "\\" in formatted_path:
    #        formatted_path = formatted_path.replace("\\", "/")
    #    # If the option "copy path" is used in Windows Explorer and then pasted into the
    #    # box, the path will be surrounded by quotes, so remove them if there
    #    if formatted_path[0] == '"':
    #        formatted_path = formatted_path.replace('"', "")
    #    self.config.options["dest_path"] = formatted_path
    #    self.opts.open_button.show()
    #    self.save_button.setEnabled(True)

    @Slot()
    def _on_inc_user_toggled(self):
        self.config.options.inc_user = self.folder_name_options.inc_user()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_inc_solvent_toggled(self):
        self.config.options.inc_solvent = self.folder_name_options.inc_solvent()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_inc_frequency_toggled(self):
        self.config.options.inc_frequency = self.folder_name_options.inc_frequency()
        self.save_button.setEnabled(True)
    
    @Slot()
    def _on_inc_original_toggled(self):
        self.config.options.inc_original = self.folder_name_options.inc_original()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_spec_changed(self):
        self.config.options.spec = self.spec_selector.selected()
        self.adapt_to_spec()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_repeat_toggled(self):
        self.config.options.repeat_switch = self.repeat_options.repeat()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_repeat_delay_changed(self):
        self.config.options.repeat_delay = self.repeat_options.interval()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_save_button_clicked(self):
        self.config.save()
        self.save_button.setEnabled(False)

    @Slot()
    def _on_multiday_toggled(self):
        if self.date_selector.multiday():
            self.repeat_options.set_repeat_enabled(False)
        else:
            self.adapt_to_spec()

    @Slot()
    def _on_notification_clicked(self):
        self.notification.hide()

#    def notify_failed_permissions(self):
#        """Spawn popup to notify user that accessing the mora server failed."""
#
#        logging.info("Permission to access server denied")
#        failed_permission_dialog = QMessageBox(self)
#        failed_permission_dialog.setWindowTitle("Access to mora server denied")
#        failed_permission_dialog.setText("""
#You have been denied permission to access the mora server.
#Check the connection and your authentication details and try again.
#The program will now close.""")
#        failed_permission_dialog.exec()
#        sys.exit()
#
#    def warn_since_function(self):
#        """Spawn popup dialog that dissuades user from using the "since" function regularly."""
#
#        since_message = """
#The function to check multiple days at a time should not be used on a regular basis.
#Please switch back to a single-day check once your search is finished.
#The repeat function is also disabled as long as this option is selected.
#            """
#        QMessageBox.warning(self, "Warning", since_message)

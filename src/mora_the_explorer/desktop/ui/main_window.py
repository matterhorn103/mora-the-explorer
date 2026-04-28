from dataclasses import asdict
import logging
import platform
from packaging.version import Version
from urllib.parse import quote

from PySide6.QtCore import Qt, QSize, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QMessageBox,
)

from ...core.config import Config
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
    admin_mode_toggled = Signal()

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
        self.version = Version(version_header.splitlines()[2])
        self.version_info = create_version_label(version_header)
        self.grid.addWidget(self.version_info, 0, 0, 1, 2)

        # Initialize the row counter
        # We already have one thing in the grid (the version info) so start at 1
        self._row_count = 1

        # User initials entry
        self.user_entry = rows.FreeEntryField("User:", "(initials)")
        self.user_entry.set_text(config.options.user)
        self.add_row(self.user_entry)

        # User name entry
        self.name_entry = rows.FreeEntryField("User name:", None)
        self.name_entry.set_text(config.options.user_name)
        self.add_row(self.name_entry)
        # If config says this should only be active in admin mode, and we aren't
        # in admin mode, then hide it
        if config.admin.user_name_is_admin_only and not admin_mode:
            self.name_entry.hide()

        if not admin_mode:
            # Group entry from an allowed selection, for normal usage
            self.group_entry = rows.OverflowSelector(
                "Group:",
                list(config.groups.filter_overflow(False)),
                list(config.groups.filter_overflow(True)),
            )
            self.group_entry.set_selected(config.options.group)
            self.add_row(self.group_entry)
        else:
            # Group entry via free-form entry boxes, for admin use
            self.group_entry = rows.FreeEntryField("Group:", None)
            self.group_entry.set_text(config.options.group)
            self.add_row(self.group_entry)
            self.group_name_entry = rows.FreeEntryField("Group name:", None)
            self.group_name_entry.set_text(config.groups.all.get(config.options.group, ""))
            self.add_row(self.group_name_entry)

        # Server path
        self.server_entry = rows.DirSelector("Server:", False)
        self.server_entry.set_path(config.paths.server())
        self.add_row(self.server_entry)

        # Destination path
        self.dest_entry = rows.DirSelector("Save in:", True, "Ctrl+G")
        self.dest_entry.set_path(config.paths.save)
        self.add_row(self.dest_entry)

        # Folder name options
        self.folder_name_options = rows.FolderNameOptions()
        # Each option `user`, `solvent` etc. has a corresponding flag in the config
        self.folder_name_options.set_checked(**(asdict(config.options.naming)))
        self.add_row(self.folder_name_options)

        # Preview of the result of the user's choices
        self.folder_name_preview = rows.FolderNamePreview(config)
        self.add_row(self.folder_name_preview)

        # Spectrometer selection
        self.spec_selector = rows.SpectrometerSelector(config.specs)
        self.refresh_visible_specs()
        self.spec_selector.set_selected(config.options.spec)
        self.add_row(self.spec_selector)

        # Match pattern customization via a free-form entry box, for admin use
        if admin_mode:
            from PySide6.QtGui import QFontDatabase
            self.pattern_entry = rows.FreeEntryField("Pattern:", "(to match)")
            # Pattern is regex
            self.pattern_entry.set_text(config.specs[config.options.spec].measurement_pattern)
            self.pattern_entry.entry_field.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
            self.add_row(self.pattern_entry)

        # Repeat options
        self.repeat_options = rows.RepeatSelector()
        self.repeat_options.set_repeat_checked(config.options.repeat_switch)
        self.repeat_options.set_interval(config.options.repeat_delay)
        self.add_row(self.repeat_options)

        # Save button
        self.save_button = QPushButton("Save options as defaults for next time")
        # Remains disabled until the config is changed
        self.save_button.setEnabled(False)
        self.grid.addWidget(self.save_button, self.next_row(), 0, 1, 2)

        # Date selection
        self.date_selector = rows.DateSelector()
        self.date_selector.set_mode("current")
        self.add_row(self.date_selector)

        # Status bar to start and cancel a check, as well as show the status
        # during a check
        self.status_bar = StatusBar()
        self.status_bar.set_colour(config.appearance.start_button_colour)
        self.grid.addWidget(self.status_bar, self.next_row(), 0, 1, 2)

        # Progress bar for check
        self.prog_bar = QProgressBar()
        self.prog_bar.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        if platform.system() == "Windows" and platform.release() == "11":
            # Looks bad (with initial Qt Win11 theme at least) so disable text
            self.prog_bar.setTextVisible(False)
        self.grid.addWidget(self.prog_bar, self.next_row(), 0, 1, 2)

        # Box to display output of check function (list of copied spectra)
        self.display = Display()
        self.grid.addWidget(self.display, self.next_row(), 0, 1, 2)

        # In-app notification that spectra have been found, dismissable
        self.notification = QPushButton()
        self.notification.hide()
        self.grid.addWidget(self.notification, self.next_row(), 0, 1, 2)

        # Connect all the signals and slots
        self.version_info.linkActivated.connect(self._on_bug_report_link_clicked)
        self.user_entry.changed.connect(self._on_user_changed)
        self.group_entry.changed.connect(self._on_group_changed)
        if admin_mode:
            self.group_name_entry.changed.connect(self._on_group_name_changed)
            self.pattern_entry.changed.connect(self._on_pattern_changed)
        self.server_entry.changed.connect(self._on_server_path_changed)
        self.dest_entry.changed.connect(self._on_dest_path_changed)
        self.folder_name_options.changed.connect(self._on_folder_name_options_changed)
        self.spec_selector.changed.connect(self._on_spec_changed)
        self.repeat_options.changed.connect(self._on_repeat_changed)
        self.save_button.clicked.connect(self._on_save_button_clicked)
        # Connect specifically to the buttons not the overall changed signal
        # because we don't need to do anything when the date is changed
        self.date_selector.date_button_group.buttonClicked.connect(self._on_date_mode_changed)
        # self.date_selector.date_selector.userDateChanged.connect(self._on_date_changed)
        self.notification.clicked.connect(self._on_notification_clicked)
        # Connect the start/cancel buttons directly to the main window's own signals
        self.status_bar.start_button.clicked.connect(self.started)
        self.status_bar.cancel_button.clicked.connect(self.cancelled)
        # When a new check is started also hide any notification
        self.status_bar.start_button.clicked.connect(self.notification.hide)

        # A shortcut to switch to and from admin mode
        admin_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        admin_shortcut.activated.connect(self.admin_mode_toggled)

    def add_row(self, row: rows.RowComponent):
        """Adds a row component to the next row in the grid."""
        row.add_to_grid(self.grid, self._row_count)
        self._row_count += 1

    def next_row(self) -> int:
        """Get the index of the next row and iterate it."""
        row = self._row_count
        self._row_count += 1
        return row

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
        if self.admin_mode:
            self.pattern_entry.set_text(spec_info.measurement_pattern)

    def notify_spectra(self):
        """Inform the user that spectra were found."""
        notification_text = "Spectra have been found!"
        self.notification.setText(notification_text + " Ctrl+G to go to. Click to dismiss")
        self.notification.setStyleSheet("background-color : limegreen")
        self.notification.show()

    def notify_error(self, error: str | None):
        """Inform the user that an error occurred."""
        self.notification.setStyleSheet("background-color : #cc0010; color : white")
        if error:
            notification_text = "Error: Python " + error
        else:
            notification_text = "Unknown error occurred."
        self.notification.setText(notification_text + " Click to dismiss")
        self.notification.show()

    # def send_toast(self, text: str):
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

        # Get system info
        os_info = platform.uname()
        # Get path to log
        log_location = str(logging.getLogger().handlers[0].baseFilename)
        email_info = "\n".join(
            [
                f"Version: {self.version}",
                f"System: {os_info.system} {os_info.release}, {os_info.machine}",
                "Description: (please describe your bug)",
                f"Log: (please attach or insert the contents of your log here, found at {log_location})",
            ]
        )
        escaped_info = quote(email_info)
        url = QUrl(f"{mailto_link}?subject=Mora%20the%20Explorer%20bug&body={escaped_info}")
        QDesktopServices.openUrl(url)

    @Slot()
    def _on_user_changed(self):
        self.config.options.user = self.user_entry.text()
        self.folder_name_preview.regenerate_preview()
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
        self.folder_name_preview.regenerate_preview()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_group_name_changed(self):
        self.config.options.group_name = self.group_name_entry.text()
        self.folder_name_preview.regenerate_preview()
        self.save_button.setEnabled(True)
    
    @Slot()
    def _on_pattern_changed(self):
        # Changes the spectrometer configuration object itself, but that's OK,
        # since we don't save the changes to file
        self.config.specs[self.config.options.spec].measurement_pattern = self.pattern_entry.text()

    @Slot()
    def _on_server_path_changed(self):
        self.config.paths.set_server(self.server_entry.path())
        # Don't bother with this so long as we don't offer the ability to include the path
        #self.folder_name_preview.regenerate_preview()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_dest_path_changed(self):
        self.config.paths.save = str(self.dest_entry.path())
        self.save_button.setEnabled(True)

    @Slot()
    def _on_folder_name_options_changed(self):
        # Returns {"user": True, "experiment": False, ...}
        for k, v in self.folder_name_options.checked().items():
            setattr(self.config.options.naming, k, v)
        self.folder_name_preview.regenerate_preview()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_spec_changed(self):
        self.config.options.spec = self.spec_selector.selected()
        self.adapt_to_spec()
        self.folder_name_preview.regenerate_preview()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_repeat_changed(self):
        self.config.options.repeat_switch = self.repeat_options.repeat()
        self.config.options.repeat_delay = self.repeat_options.interval()
        self.save_button.setEnabled(True)

    @Slot()
    def _on_save_button_clicked(self):
        self.config.save()
        self.save_button.setEnabled(False)

    @Slot()
    def _on_date_mode_changed(self):
        if self.date_selector.mode() == "multi":
            self.repeat_options.set_repeat_enabled(False)
        else:
            self.adapt_to_spec()

    @Slot()
    def _on_notification_clicked(self):
        self.notification.hide()

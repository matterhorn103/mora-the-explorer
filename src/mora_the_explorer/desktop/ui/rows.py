"""Components for the rows of the interface."""

import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QLabel,
    QLineEdit,
    QDateEdit,
    QCheckBox,
    QSizePolicy,
    QSpinBox,
    QHBoxLayout,
    QStyle,
    QVBoxLayout,
    QGridLayout,
    QFileDialog,
)

from mora_the_explorer.core.config import Config, NamingOptions
from mora_the_explorer.core.explorer import Explorer
from mora_the_explorer.core.metadata import MeasurementMetadata, MetadataRules

from ...core.spec import Manufacturer, Spectrometer


class RowComponent(QObject):
    """A logical grouping of widgets that take up one, or in some cases two, rows
    in the UI, and together set a single option or kind of option."""

    def __init__(self):
        super().__init__()

    def add_to_grid(self, grid: QGridLayout, row: int):
        """Add the row's widgets and layouts to the row specified of `grid`.

        This method should be overridden by subclasses.
        """
        raise NotImplementedError


class DirSelector(RowComponent):
    """A component for selecting a directory."""

    changed = Signal()

    def __init__(self, title: str, go_button: bool = False, go_shortcut: str | None = None):
        super().__init__()

        # Store the path as a Path object
        self._path: Path = None

        # Groups two items - a title string and a path field, and two buttons
        self.title = QLabel(title)
        # The path field consists of a button to click to select a folder, the
        # entry field itself, and (optionally) a button to go to the folder
        self.path_layout = QHBoxLayout()
        self.pick_button = QPushButton("")
        self.entry_field = QLineEdit()
        self.go_button = QPushButton("go to")
        self.path_layout.addWidget(self.pick_button)
        self.path_layout.addWidget(self.entry_field)
        self.path_layout.addWidget(self.go_button)

        # We want no gap between the entry field and the buttons
        self.path_layout.setSpacing(0)
        # However, the entry field is disabled to prevent accidental changes, so
        # that changes have to be made using the pick button
        self.entry_field.setEnabled(False)

        # Give the pick button the appropriate icon, make it square
        pick_icon = self.pick_button.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        self.pick_button.setIcon(pick_icon)
        self.pick_button.setFixedSize(24, 24)
        #self.pick_button.setIconSize(24)

        # Right align the title
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Set the method that is called when the buttons are pressed
        self.pick_button.clicked.connect(self.pick_path)
        self.go_button.clicked.connect(self.go_to)

        # If no go button was requested, we still generate it (to make logic simpler),
        # we just don't show it
        if not go_button:
            self.go_button.hide()

        # Set a shortcut for the "go to" button, if desired
        if go_shortcut:
            self.go_shortcut = QShortcut(QKeySequence(go_shortcut), self.go_button)
            self.go_shortcut.activated.connect(self.go_to)

        # Connect a change in the field to the instance's signal
        self.entry_field.textChanged.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addLayout(self.path_layout, row, 1)

    def path(self) -> Path:
        """Get the current path in the entry field."""
        return self._path

    def set_path(self, path: str | Path):
        """Set the path in the entry field."""
        self._path = Path(path)
        self.entry_field.setText(str(path))

    @Slot()
    def pick_path(self):
        """Open a file dialog for the user to select a directory on the system.

        The file dialog is shown centred over the `parent` window.
        """
        choice = QFileDialog.getExistingDirectory(
            self.pick_button, "Select Folder", str(self.path().expanduser().parent),
        )
        if choice:
            self.set_path(choice)

    @Slot()
    def go_to(self):
        """Opens the path in the system file explorer."""

        target = self.path().expanduser()
        if target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(target))


class FreeEntryField(RowComponent):
    """A component for entering free text."""

    changed = Signal()

    def __init__(self, title: str, comment: str | None):
        super().__init__()

        # Groups three widgets - a title string, an entry field, then a trailing comment
        self.title = QLabel(title)
        # Entry field and comment distributed within a sub-layout
        self.field_layout = QHBoxLayout()
        self.entry_field = QLineEdit()
        self.field_layout.addWidget(self.entry_field)
        if comment is not None:
            self.comment = QLabel(comment)
            # Centre the comment in both directions
            self.comment.setAlignment(Qt.AlignCenter)
            self.comment.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
            self.field_layout.addWidget(self.comment)
        else:
            self.comment = None

        # Right align the title (but centre vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Connect a change in the field to the instance's signal
        # Use textEdited so that setting it programmatically doesn't trigger it,
        # only changes made by the user
        self.entry_field.textEdited.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addLayout(self.field_layout, row, 1)

    def text(self) -> str:
        """Get the current text in the entry field."""
        return self.entry_field.text()

    def set_text(self, text: str):
        """Set the text in the entry field."""
        self.entry_field.setText(text)

    def show(self):
        """Show all the widgets associated with this component."""
        self.title.show()
        self.entry_field.show()
        if self.comment:
            self.comment.show()

    def hide(self):
        """Hide all the widgets associated with this component."""
        self.title.hide()
        self.entry_field.hide()
        if self.comment:
            self.comment.hide()


class OverflowSelector(RowComponent):
    """A component that allows selection via a combination of radio buttons
    for main options and a drop-down list for overflow options."""

    # A signal to indicate when the choice has changed, regardless of whether the
    # change was in the buttons or the drop-down
    changed = Signal()

    def __init__(self, title: str, main: list[str], overflow: list[str]):
        super().__init__()

        # Store the lists of items
        self.main = main
        self.overflow = overflow

        # A button group to handle the logic of the buttons as one set even if
        # they are split over multiple lines
        self.buttons = QButtonGroup()

        # Groups three items - a title string, a stack of two rows of buttons,
        # and a stack of a radio button over a drop-down list
        self.title = QLabel(title)
        self.button_stack = QVBoxLayout()
        self.overflow_stack = QVBoxLayout()

        # Two rows of buttons
        self.button_row1 = QHBoxLayout()
        self.button_row2 = QHBoxLayout()
        self.button_stack.addLayout(self.button_row1)
        self.button_stack.addLayout(self.button_row2)

        # Overflow button and list
        # An "Other" option that, when selected, causes the overflow drop-down to be shown
        self.other_button = QRadioButton("other")
        self.buttons.addButton(self.other_button, 100)
        self.dropdown = QComboBox()
        self.overflow_stack.addWidget(self.other_button)
        self.overflow_stack.addWidget(self.dropdown)

        # But actually, we group the two stacks together in the central column
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addLayout(self.button_stack)
        self.buttons_layout.addLayout(self.overflow_stack)

        # Make the dropdown as small as possible
        self.dropdown.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        # Right align the title (but centre vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignTop)

        # Add radio buttons to the main options section
        for i, label in enumerate(main):
            button = QRadioButton(label)
            # Use the index in the provided list as the ID within the button group
            self.buttons.addButton(button, i)
            # Add to the appropriate row
            if i < len(main) / 2:
                self.button_row1.addWidget(button)
            else:
                self.button_row2.addWidget(button)

        # Add other options to the overflow drop-down
        self.dropdown.addItems(overflow)

        # Have the overflow drop-down be shown when appropriate
        self.buttons.idClicked.connect(self._on_button_click)

        # Connect a change in either the buttons or the drop-down to the instance's signal
        self.buttons.buttonClicked.connect(self.changed)
        self.dropdown.currentIndexChanged.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addLayout(self.buttons_layout, row, 1)

    def selected(self) -> str:
        """Get the selected option."""
        if self.buttons.checkedId() == 100:
            # This means the "other" button is checked
            return self.dropdown.currentText()
        else:
            return self.main[self.buttons.checkedId()]

    def set_selected(self, option: str):
        """Set the selected option."""
        if option in self.main:
            i = self.main.index(option)
            self.buttons.button(i).setChecked(True)
            self.dropdown.setEnabled(False)
        elif option in self.overflow:
            self.buttons.button(100).setChecked(True)
            self.dropdown.setCurrentText(option)
            self.dropdown.setEnabled(True)
        else:
            raise ValueError(f"{option} does not have a corresponding button!")

    @Slot()
    def _on_button_click(self, id: int):
        """Adapt to a change in the checked button."""
        if id == 100:
            # This means the "other" button is checked
            self.dropdown.setEnabled(True)
        else:
            self.dropdown.setEnabled(False)


# The classes above are abstract really, whereas the below are specific to their
# context and have more stuff hard-coded


class FolderNameOptions(RowComponent):
    """The component for choices relating to folder name customization."""

    # A signal emitted whenever any of the options are toggled
    changed = Signal()

    def __init__(self):
        super().__init__()

        # Three widgets
        self.title = QLabel("Include:")
        self.box_grid = QGridLayout()
        # self.comment = QLabel("…in folder name")

        # Right align the title (but top align vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignTop)
        # Centre the comment (but top align vertically)
        # self.comment.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # The set of options and the labels that should go next to the checkboxes
        # `Config` contains a flag for each option with an `inc_` prefix e.g. inc_user
        self.options = {
            "group": "group",
            "user": "user",
            "solvent": "solvent",
            "frequency": "frequency",
            "experiment": "experiment",
            "original": "original name",
        }
        self.boxes = {}

        # Create the checkboxes, add them to the rows, connect up the signals
        # Fill the first row until half or more of the boxes have been added
        # First item in new row is thus the item with i == (n + 1) // 2
        first_i_in_row2 = (len(self.options) + 1) // 2
        for i, (option, label) in enumerate(self.options.items()):
            box = QCheckBox(label)
            self.boxes[option] = box
            if i < first_i_in_row2:
                self.box_grid.addWidget(box, 0, i)
            else:
                self.box_grid.addWidget(box, 1, i - first_i_in_row2)
            box.toggled.connect(self.changed)
        
        # Add an additional checkbox for the "sample ID" that is a dummy, can't
        # be deselected, and doesn't feature in any of the other logic - it's
        # there just to make it clearer how the names are generated (as everything
        # that's in the generated names then has a corresponding checkbox)
        id_checkbox = QCheckBox("sample ID")
        id_checkbox.setChecked(True)
        id_checkbox.setEnabled(False)
        self.box_grid.addWidget(id_checkbox, 0, first_i_in_row2)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        # Up to six options fit within the central column
        #if len(self.options) <= 6:
        grid.addLayout(self.box_grid, row, 1)
        # More than that and we need to expand into the third column
        #else:
        #grid.addLayout(self.box_grid, row, 1, 1, 2)
        # grid.addWidget(self.comment, row, 2)

    def checked(self) -> dict[str, bool]:
        """Get the status of all the checkboxes."""
        return {k: self.boxes[k].isChecked() for k in self.options.keys()}

    def set_checked(self, **kwargs: bool):
        """Set the status of all the checkboxes."""
        for k, v in kwargs.items():
            self.boxes[k].setChecked(v)


class FolderNamePreview(RowComponent):
    """A component to show the user the result of their selected naming options."""

    def __init__(self, config: Config):
        # Maintains its own explorer instance in order to regenerate the rules
        # The explorer doesn't need to be recreated anew every time something
        # changes, and it doesn't need its own config, it just shares the main
        # window's
        self.config = config
        self.explorer = Explorer(config)

        # Some demo metadata that include the user's own initials and group and
        # example values of the other fields
        # Keep a single copy hanging around, just replace the user/group if they change
        # Some strings start off empty because they are generated in a call to
        # regenerate_preview() in a second anyway
        self.metadata = MeasurementMetadata(
            path="",
            folder_name="170",
            manufacturer=Manufacturer.BRUKER,
            date=datetime.date.today(),
            user="",
            group="",
            experiment="proton",
            frequency=300.26,
            solvent="CDCl3",
            sample_id="389-1",
        )

        # Container groups two items: a title and a text label
        self.title = QLabel("Preview:")
        self.preview = QLabel()

        # Centre-align the preview within the column
        self.preview.setAlignment(Qt.AlignCenter)

        self.regenerate_preview()

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addWidget(self.preview, row, 1)

    @Slot()
    def regenerate_preview(self):
        """Update the preview based on the current config."""

        # Update the demo metadata first
        self.metadata.user = self.config.options.user
        self.metadata.group = self.config.options.group
        self.metadata.manufacturer = self.config.specs[self.config.options.spec].manufacturer
        if self.metadata.manufacturer == Manufacturer.BRUKER:
            self.metadata.folder_name = "170"
            self.metadata.instrument = "av300"
        else:
            self.metadata.folder_name = self.config.options.user + self.metadata.sample_id
            self.metadata.instrument = "v500"
        # Don't bother with this so long as we don't offer the ability to include the path
        #self.metadata.path = self.explorer.get_check_paths(datetime.date.today())[0] / self.metadata.folder_name
        
        preview = self.metadata.generate_folder_name(self.explorer.generate_rules(), drop_missing=False)
        self.preview.setText(preview)


class SpectrometerSelector(RowComponent):
    """The component for choosing the spectrometer to search."""

    changed = Signal()

    def __init__(self, specs: dict[str, Spectrometer]):
        super().__init__()

        # Store the items
        self.specs = list(specs.keys())

        # A button group to make the buttons mutually exclusive
        self.buttons = QButtonGroup()

        # Container groups two items: a title and a stack of the buttons
        self.title = QLabel("Search:")
        self.button_stack = QVBoxLayout()

        for i, spec in enumerate(self.specs):
            spec_info = specs[spec]
            button = QRadioButton(spec_info.display_name)
            # Use the index in the stored list as the ID within the button group
            self.buttons.addButton(button, i)
            # Add to the stack
            self.button_stack.addWidget(button)

        # Right align the title (but top align vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.buttons.buttonClicked.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addLayout(self.button_stack, row, 1)

    def selected(self) -> str:
        """Get the selected option."""
        return self.specs[self.buttons.checkedId()]

    def set_selected(self, spec: str):
        """Set the selected option."""
        if spec in self.specs:
            i = self.specs.index(spec)
            self.buttons.button(i).setChecked(True)
        else:
            raise ValueError(f"{spec} is not a spectrometer with a corresponding button!")

    def set_visible(self, spec: str, visible: bool):
        """Sets the `visible` property on the corresponding button for `spec`."""
        if spec in self.specs:
            i = self.specs.index(spec)
            self.buttons.button(i).setVisible(visible)
        else:
            raise ValueError(f"{spec} is not a spectrometer with a corresponding button!")


class RepeatSelector(RowComponent):
    """The component used to instruct to repeat the search after a chosen interval."""

    changed = Signal()

    def __init__(self):
        super().__init__()

        # Groups two items: a title and a row of mixed widgets
        self.title = QLabel("Repeat:")
        self.repeat_row = QHBoxLayout()

        # Repeat row layout contains an interactive sentence consisting of
        # a checkbox, a spinbox, and a label
        self.repeat_box = QCheckBox("check every")
        self.interval_box = QSpinBox()
        self.mins_label = QLabel("min")

        self.repeat_row.addWidget(self.repeat_box)
        self.repeat_row.addWidget(self.interval_box)
        self.repeat_row.addWidget(self.mins_label)

        # Right align the title (but centre vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # A delay of 0 or a negative value would be meaningless
        self.interval_box.setMinimum(1)

        # Emit signal whenever either the status is toggled or the interval is changed
        self.repeat_box.toggled.connect(self.changed)
        self.interval_box.valueChanged.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addLayout(self.repeat_row, row, 1)

    def repeat(self) -> bool:
        """Whether the repeat function is activated."""
        return self.repeat_box.isChecked()

    def set_repeat_checked(self, repeat: bool):
        """Set the repeat function box to be checked or unchecked."""
        self.repeat_box.setChecked(repeat)

    def set_repeat_enabled(self, enabled: bool):
        """Set the checkbox and interval spinbox to be enabled or disabled."""
        if not enabled:
            self.repeat_box.setChecked(False)
        self.repeat_box.setEnabled(enabled)
        self.interval_box.setEnabled(enabled)

    def interval(self) -> int:
        """Get the current repeat interval."""
        return self.interval_box.value()

    def set_interval(self, interval: int):
        """Set the value shown in the repeat interval box."""
        self.interval_box.setValue(interval)


class DateSelector(RowComponent):
    """The component used to select the date to be checked and to specify single
    or multi-day check mode."""

    changed = Signal()

    def __init__(self):
        super().__init__()

        # Groups two items: a title, and a row of mixed widgets
        self.title = QLabel("When?")
        self.date_row = QHBoxLayout()

        # Date row layout contains an interactive sentence consisting of
        # three radio buttons, a date entry box, and a reset button

        # Mutually exclusive radio buttons to choose between single and multiple days
        self.date_button_group = QButtonGroup()
        self.today_button = QRadioButton("today")
        self.only_button = QRadioButton("only")
        self.since_button = QRadioButton("since")

        self.date_button_group.addButton(self.today_button)
        self.date_button_group.addButton(self.only_button)
        self.date_button_group.addButton(self.since_button)

        # Date editor with initial value set to today's date
        self.date_selector = QDateEdit(datetime.date.today())
        self.date_selector.setDisplayFormat("dd MMM yyyy")
        #self.date_selector.setMinimumWidth(200)
        self.date_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # A button to reset the date to the current day
        self.reset_button = QPushButton("")

        # Give the reset button an icon
        reset_icon = self.reset_button.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.reset_button.setIcon(reset_icon)
        self.reset_button.setFixedSize(24, 24)

        # We don't want a gap between the date selector and the reset button, so
        # add a nested layout
        self.date_selector_layout = QHBoxLayout()
        self.date_selector_layout.setSpacing(0)
        self.date_selector_layout.addWidget(self.date_selector)
        self.date_selector_layout.addWidget(self.reset_button)

        self.date_row.addWidget(self.today_button)
        self.date_row.addWidget(self.only_button)
        self.date_row.addWidget(self.since_button)
        self.date_row.addLayout(self.date_selector_layout)

        # When the reset button is pressed, set the current date to today's date
        self.reset_button.clicked.connect(self.reset_date)

        # Right align the title (but centre vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.date_button_group.buttonClicked.connect(self.changed)
        self.date_button_group.buttonClicked.connect(self._adjust_for_mode)
        self.date_selector.userDateChanged.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addLayout(self.date_row, row, 1)

    def date(self) -> datetime.date:
        if self.mode() == "current":
            return datetime.date.today()
        else:
            return self.date_selector.date().toPython()

    def set_date(self, date: datetime.date):
        self.date_selector.setDate(date)

    @Slot()
    def reset_date(self):
        self.set_date(datetime.date.today())

    def set_format(self, format: str):
        """Set the display format of the date."""
        self.date_selector.setDisplayFormat(format)

    def mode(self) -> str:
        """Which mode ("current", "single", or "multi") is currently active."""
        if self.date_button_group.checkedButton() is self.today_button:
            return "current"
        elif self.date_button_group.checkedButton() is self.only_button:
            return "single"
        else:  # mode == "multi"
            return "multi"
        
    @Slot()
    def _adjust_for_mode(self):
        mode = self.mode()
        if mode == "current":
            self.reset_date()
            self.date_selector.setEnabled(False)
        elif mode == "single":
            self.date_selector.setEnabled(True)
        else:  # mode == "multi"
            self.date_selector.setEnabled(True)

    def set_mode(self, mode: str):
        """Set the mode to "current", "single", or "multi"."""
        if mode == "current":
            self.today_button.setChecked(True)
        elif mode == "single":
            self.only_button.setChecked(True)
        else:  # mode == "multi"
            self.since_button.setChecked(True)
        self._adjust_for_mode()

    def set_multiday_enabled(self, enabled: bool):
        """Set the multiday mode to be available or not."""
        self.since_button.setEnabled(enabled)
        if self.mode() == "multi" and not enabled:
            self.set_mode("single")

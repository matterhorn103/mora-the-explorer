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
    QSpinBox,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QFileDialog,
)

from ...core.spec import Spectrometer


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

    def __init__(self, title: str, go_shortcut: str | None = None):
        super().__init__()

        # Groups four widgets - a title string, an entry field, then two buttons
        self.title = QLabel(title)
        self.entry_field = QLineEdit()
        self.pick_button = QPushButton("Pick")
        # self.go_button = QPushButton("go to")
        # self.go_button.hide()

        # Right align the title
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Set the method that is called when the buttons are pressed
        self.pick_button.clicked.connect(self.pick_path)
        # self.go_button.clicked.connect(self.go_to)

        # Set a shortcut for the "go to" button, if desired
        if go_shortcut:
            self.go_shortcut = QShortcut(QKeySequence(go_shortcut), self.entry_field)
            self.go_shortcut.activated.connect(self.go_to)

        # Connect a change in the field to the instance's signal
        self.entry_field.textChanged.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addWidget(self.entry_field, row, 1)
        grid.addWidget(self.pick_button, row, 2)
        # grid.addWidget(self.go_button, row, 2)

    def path(self) -> str:
        """Get the current path (as a string) in the entry field."""
        return self.entry_field.text()

    def set_path(self, path: str | Path):
        """Set the path in the entry field."""
        self.entry_field.setText(str(path))

    @Slot()
    def pick_path(self):
        """Open a file dialog for the user to select a directory on the system.

        The file dialog is shown centred over the `parent` window.
        """
        choice = QFileDialog.getExistingDirectory(
            self.pick_button, "Select Folder", str(Path.home())
        )
        self.set_path(choice)

    @Slot()
    def go_to(self):
        """Opens the path in the system file explorer."""

        target = Path(self.path()).expanduser()
        if target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(target))


class FreeEntryField(RowComponent):
    """A component for entering free text."""

    changed = Signal()

    def __init__(self, title: str, comment: str | None):
        super().__init__()

        # Groups three widgets - a title string, an entry field, then a trailing comment
        self.title = QLabel(title)
        self.entry_field = QLineEdit()
        if comment is not None:
            self.comment = QLabel(comment)
            # Centre the comment in both directions
            self.comment.setAlignment(Qt.AlignCenter)
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
        grid.addWidget(self.entry_field, row, 1)
        if self.comment:
            grid.addWidget(self.comment, row, 2)

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
        grid.addLayout(self.button_stack, row, 1)
        grid.addLayout(self.overflow_stack, row, 2)

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
            "user": "user",
            "experiment": "experiment",
            "solvent": "solvent",
            "frequency": "frequency",
            "original": "original name",
        }
        self.boxes = {}

        # Create the checkboxes, add them to the rows, connect up the signals
        for i, (option, label) in enumerate(self.options.items()):
            box = QCheckBox(label)
            self.boxes[option] = box
            # Fill the first row until half or more of the boxes have been added
            # First item in new row is thus the item with i == (n + 1) // 2
            first_i_in_row2 = (len(self.options) + 1) // 2
            if i < first_i_in_row2:
                self.box_grid.addWidget(box, 0, i)
            else:
                self.box_grid.addWidget(box, 1, i - first_i_in_row2)
            box.toggled.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        # Up to six options fit within the central column
        if len(self.options) <= 6:
            grid.addLayout(self.box_grid, row, 1)
        # More than that and we need to expand into the third column
        else:
            grid.addLayout(self.box_grid, row, 1, 1, 2)
        # grid.addWidget(self.comment, row, 2)

    def checked(self) -> dict[str, bool]:
        """Get the status of all the checkboxes."""
        return {k: self.boxes[k].isChecked() for k in self.options.keys()}

    def set_checked(self, **kwargs: bool):
        """Set the status of all the checkboxes."""
        for k, v in kwargs.items():
            self.boxes[k].setChecked(v)


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
        grid.addLayout(self.button_stack, row, 1, 1, 2)

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

        # Groups three items: a title, a row of mixed widgets, and a button to
        # set the date to the current day
        self.title = QLabel("When?")
        self.date_row = QHBoxLayout()
        self.today_button = QPushButton("Today")

        # Date row layout contains an interactive sentence consisting of
        # two radio buttons and a date entry box

        # Mutually exclusive radio buttons to choose between single and multiple days
        self.date_button_group = QButtonGroup()
        self.only_button = QRadioButton("only")
        self.since_button = QRadioButton("since")

        self.date_button_group.addButton(self.only_button)
        self.date_button_group.addButton(self.since_button)

        # Date editor with initial value set to today's date
        self.date_selector = QDateEdit(datetime.date.today())
        self.date_selector.setDisplayFormat("dd MMM yyyy")

        self.date_row.addWidget(self.only_button, 0)
        self.date_row.addWidget(self.since_button, 1)
        self.date_row.addWidget(self.date_selector, 2)

        # When the today button is pressed, set the current date to today's date
        self.today_button.clicked.connect(self.set_to_today)

        # Right align the title (but centre vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.date_button_group.buttonClicked.connect(self.changed)
        self.date_selector.userDateChanged.connect(self.changed)

    def add_to_grid(self, grid: QGridLayout, row: int):
        grid.addWidget(self.title, row, 0)
        grid.addLayout(self.date_row, row, 1)
        grid.addWidget(self.today_button, row, 2)

    def date(self) -> datetime.date:
        return self.date_selector.date().toPython()

    def set_date(self, date: datetime.date):
        self.date_selector.setDate(date)

    @Slot()
    def set_to_today(self):
        self.set_date(datetime.date.today())

    def set_format(self, format: str):
        """Set the display format of the date."""
        self.date_selector.setDisplayFormat(format)

    def multiday(self) -> bool:
        """Whether the since function is activated."""
        return self.date_button_group.checkedButton() is self.since_button

    def set_multiday(self, multiday: bool):
        """Set the mode to be multi or single day."""
        if multiday:
            self.since_button.setChecked(True)
        else:
            self.only_button.setChecked(True)

    def set_multiday_enabled(self, enabled: bool):
        """Set the multiday mode to be available or not."""
        self.only_button.setEnabled(enabled)
        self.since_button.setEnabled(enabled)
        if not enabled:
            self.only_button.setChecked(True)

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget,
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
    QProgressBar,
    QFileDialog,
)

class DirSelector:
    """A component for selecting a directory."""

    def __init__(self, title: str, go_shortcut: str | None = None):

        # Groups four widgets - a title string, an entry field, then two buttons
        self.title = QLabel(title)
        self.entry_field = QLineEdit()
        self.pick_button = QPushButton("pick")
        self.go_button = QPushButton("go to")

        # Right align the title
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Set the method that is called when the buttons are pressed
        self.pick_button.clicked.connect(self.pick_path())
        self.go_button.clicked.connect(self.go_to())

        # Set a shortcut for the "go to" button, if desired
        if go_shortcut:
            self.go_button.setShortcut(go_shortcut)

    def widgets(self) -> tuple[QLabel, QLineEdit, QPushButton, QPushButton]:
        """Return the `QWidget`s of the component, in the order they should be arranged in the UI."""
        return (self.title, self.entry_field, self.pick_button, self.go_button)

    def path(self) -> str:
        """Get the current path (as a string) in the entry field."""
        return self.entry_field.text()

    def set_path(self, path: str | Path):
        """Set the path in the entry field."""
        self.entry_field.setText(str(path))

    def pick_path(self):
        """Open a file dialog for the user to select a directory on the system.
        
        The file dialog is shown centred over the `parent` widget.
        """
        choice = QFileDialog.getExistingDirectory(self.parent, "Select Folder", str(Path.home()))
        self.set_path(choice)

    def go_to(self):
        """Opens the path in the system file explorer."""

        target = Path(self.path())
        if target.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(target))

        #self.dest_path_label = QLabel("save in:")
#
        #self.dest_path_input = 
        #self.dest_path_input.setText(dest_path)
#
        #self.open_button = QPushButton("go to")
        #self.open_button.setShortcut("Ctrl+G")
        ## Disable button if path hasn't yet been specified to stop new users thinking it
        ## should be used to select a folder
        #if dest_path == "copy full path here":
        #    self.open_button.hide()


class FreeEntryField:
    """A component for entering free text."""

    def __init__(self, title: str, comment: str):

        # Groups three widgets - a title string, an entry field, then a trailing comment
        self.title = QLabel(title)
        self.entry_field = QLineEdit()
        self.comment = QLabel(comment)

        # Right align the title (but centre vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # Centre the comment in both directions
        self.comment.setAlignment(Qt.AlignCenter)

    def widgets(self) -> tuple[QLabel, QLineEdit, QLabel]:
        """Return the `QWidget`s of the component, in the order they should be arranged in the UI."""
        return (self.title, self.entry_field, self.comment)
    
    def text(self) -> str:
        """Get the current text in the entry field."""
        return self.entry_field.text()
    
    def set_text(self, text: str):
        """Set the text in the entry field."""
        self.entry_field.setText(text)


class OverflowSelector:
    """A component that allows selection via a combination of radio buttons
    for main options and a drop-down list for overflow options."""

    def __init__(self, title: str, main: list[str], overflow: list[str]):

        # Store the lists of items
        self.main = main
        self.overflow = overflow
        
        # A button group to handle the logic of the buttons as one set even if
        # they are split over multiple lines
        self.buttons = QButtonGroup()

        # Groups four items - a title string, two rows of buttons, and a drop-down list
        self.title = QLabel(title)
        self.button_row1: list[QRadioButton] = []
        self.button_row2: list[QRadioButton] = []
        self.dropdown = QComboBox()

        # Right align the title (but centre vertically)
        self.title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Add radio buttons to the main options section
        for i, label in enumerate(main):
            button = QRadioButton(label)
            # Use the index in the provided list as the ID within the button group
            self.buttons.addButton(button, i)
            # Add to the appropriate row
            if i < len(main) / 2:
                self.button_row1.append(button)
            else:
                self.button_row2.append(button)

        # Add an "Other" option that, when selected, causes the overflow drop-down to be shown
        self.buttons.addButton(QRadioButton("other"), 100)
        
        # Add other options to the overflow drop-down
        self.dropdown.addItems(overflow)

    def widgets(self) -> tuple[QLabel, list[QRadioButton], list[QRadioButton], QComboBox]:
        return self.title, self.button_row1, self.button_row2, self.dropdown

    def selected(self) -> str:
        """Get the selected option."""
        if self.buttons.checkedId() == 100:
            # This means the "other" button is checked
            return self.dropdown.currentText()
        else:
            return self.main[self.buttons.checkedId()]

    def set_selected(self, button: str):
        """Set the selected option."""
        if button in self.main:
            i = self.main.index(button)
            self.buttons.button(i).setChecked(True)
            self.dropdown.hide()
        elif button in self.overflow:
            self.buttons.button(100).setChecked(True)
            self.dropdown.setCurrentText(button)
            self.dropdown.show()
        else:
            raise ValueError(f"{button} is not a group with a corresponding button!")


# The classes above are abstract really, whereas the below are specific to their
# context and have more stuff hard-coded

class FolderNameOptions:
    """The component for choices relating to folder name customization."""

    def __init__(self):

        # Four widgets
        self.title = QLabel("include:")
        self.user_box = QCheckBox("user")
        self.solvent_box = QCheckBox("solvent")
        self.original_box = QCheckBox("original folder name")

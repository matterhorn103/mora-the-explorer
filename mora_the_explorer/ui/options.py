from datetime import date

from PySide6.QtCore import Qt
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
)


class GroupButtons(QButtonGroup):
    def __init__(self, parent, group_list, selected_group):
        super().__init__(parent)

        self.main_layout = QHBoxLayout()
        self.overflow_layout = QHBoxLayout()
        self.button_list = []
        for group in group_list:
            group_button = QRadioButton(group)
            self.button_list.append(group_button)
            if (group == selected_group) or (group == "other" and self.checkedButton() is None):
                group_button.setChecked(True)
            self.addButton(group_button)
            if len(group_list) <= 4 or group_list.index(group) < (len(group_list) / 2):
                self.main_layout.addWidget(group_button)
            elif len(group_list) > 4 and group_list.index(group) >= (len(group_list) / 2):
                self.overflow_layout.addWidget(group_button)


class SpecButton(QRadioButton):
    """Just like a normal QRadioButton except we can assign it a name."""

    def __init__(self, text, name):
        super().__init__(text)
        self.name = name


class SpecButtons(QButtonGroup):
    def __init__(self, parent, specs, selected_spec):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.buttons = {}

        for spec in specs:
            button = SpecButton(specs[spec]["display_name"], spec)
            self.buttons[spec] = button
            if spec == selected_spec:
                button.setChecked(True)
            self.addButton(button)
            self.layout.addWidget(button)


class OptionsLayout(QGridLayout):
    """Layout containing all user-configurable options.

    Widgets with more complicated code are defined in custom classes, while simple ones
    are defined in-line.

    We define the layout, content, and appearance here, but not the behaviour (e.g. what
    happens when something is clicked or changed.)
    """

    def __init__(self, config):
        super().__init__()

        # Row 0, initials entry box
        self.initials_label = QLabel("initials:")
        self.initials_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.initials_entry = QLineEdit()
        self.initials_entry.setMaxLength(3)
        self.initials_entry.setText(config.options["initials"])

        self.initials_hint = QLabel("(lowercase!)")
        self.initials_hint.setAlignment(Qt.AlignCenter)

        self.addWidget(self.initials_label, 0, 0)
        self.addWidget(self.initials_entry, 0, 1)
        self.addWidget(self.initials_hint, 0, 2)

        # Rows 1 and 2, group selection (most gets generated by `add_group_buttons()`)
        self.group_label = QLabel("group:")
        self.group_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.addWidget(self.group_label, 1, 0)

        # Row 3, destination path entry box
        self.dest_path_label = QLabel("save in:")
        self.dest_path_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.dest_path_input = QLineEdit()
        self.dest_path_input.setText(config.options["dest_path"])

        self.open_button = QPushButton("go to")
        self.open_button.setShortcut("Ctrl+G")
        # Disable button if path hasn't yet been specified to stop new users thinking it
        # should be used to select a folder
        if config.options["dest_path"] == "copy full path here":
            self.open_button.hide()

        self.addWidget(self.dest_path_label, 3, 0)
        self.addWidget(self.dest_path_input, 3, 1)
        self.addWidget(self.open_button, 3, 2)

        # Rows 4 (and 5), file naming options
        self.include_label = QLabel("include:")
        self.include_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inc_init_checkbox = QCheckBox("initials")
        self.inc_init_checkbox.setChecked(config.options["inc_init"])
        if config.options["nmrcheck_style"] is True:
            self.inc_init_checkbox.setEnabled(False)

        self.inc_solv_checkbox = QCheckBox("solvent")
        self.inc_solv_checkbox.setChecked(config.options["inc_solv"])
        if config.specs[config.options["spec"]]["allow_solvent"] is False:
            self.inc_solv_checkbox.setEnabled(False)

        self.in_filename_label = QLabel("...in filename")
        self.in_filename_label.setAlignment(Qt.AlignCenter)

        # Option to use NMRCheck-style formatting of folder names
        self.nmrcheck_style_checkbox = QCheckBox("use comprehensive (NMRCheck) style")
        self.nmrcheck_style_checkbox.setChecked(config.options["nmrcheck_style"])

        # Or, for nmr group, the choice of where to put the path
        self.inc_path_checkbox = QCheckBox("path")
        self.inc_path_checkbox.setChecked(bool(config.options["inc_path"]))

        self.inc_path_box = QComboBox()
        inc_path_options = ["before", "after"]
        self.inc_path_box.addItems(inc_path_options)
        
        if config.options["inc_path"] in inc_path_options:
            self.inc_path_box.setCurrentText(config.options["inc_path"])
        else:
            self.inc_path_box.setCurrentText("after")

        inc_path_layout = QHBoxLayout()
        inc_path_layout.addWidget(self.inc_path_checkbox)
        inc_path_layout.addWidget(self.inc_path_box)
        inc_path_layout.addWidget(QLabel())

        filename_layout = QGridLayout()
        filename_layout.addWidget(self.inc_init_checkbox, 0, 0)
        filename_layout.addWidget(self.inc_solv_checkbox, 0, 1)
        filename_layout.addWidget(self.nmrcheck_style_checkbox, 1, 0, 1, 2)
        filename_layout.addLayout(inc_path_layout, 1, 0)

        self.addWidget(self.include_label, 4, 0)
        self.addLayout(filename_layout, 4, 1, 2, 1)
        self.addWidget(self.in_filename_label, 4, 2)

        # Row 6, spectrometer selection (most gets generated by `add_spec_buttons()`)
        self.spec_label = QLabel("search:")
        self.spec_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.addWidget(self.spec_label, 6, 0)

        # Row 7, checkbox to instruct to repeat after chosen interval
        self.repeat_label = QLabel("repeat:")
        self.repeat_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.repeat_check_checkbox = QCheckBox("check every")
        self.repeat_check_checkbox.setChecked(config.options["repeat_switch"])

        self.repeat_interval = QSpinBox()
        self.repeat_interval.setMinimum(1)
        self.repeat_interval.setValue(config.options["repeat_delay"])

        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(self.repeat_check_checkbox)
        repeat_layout.addWidget(self.repeat_interval)
        repeat_layout.addWidget(QLabel("mins"))

        self.addWidget(self.repeat_label, 7, 0)
        self.addLayout(repeat_layout, 7, 1)

        # Row 8, button to save all options for future
        self.save_button = QPushButton("save options as defaults for next time")
        self.save_button.setEnabled(False)

        self.addWidget(self.save_button, 8, 0, 1, 3)

        # Row 9, date selection tool
        self.date_label = QLabel("when?")
        self.date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.today_button = QPushButton("today")

        self.addWidget(self.date_label, 9, 0)
        self.addWidget(self.today_button, 9, 2)

        # Date selection tool
        self.only_button = QRadioButton("only")
        self.only_button.setChecked(True)

        self.since_button = QRadioButton("since")

        self.date_button_group = QButtonGroup(self)
        self.date_button_group.addButton(self.only_button)
        self.date_button_group.addButton(self.since_button)

        self.date_selector = QDateEdit()
        self.date_selector.setDisplayFormat("dd MMM yyyy")
        self.date_selector.setDate(date.today())

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.only_button, 0)
        date_layout.addWidget(self.since_button, 1)
        date_layout.addWidget(self.date_selector, 2)

        self.addLayout(date_layout, 9, 1)
    

    def add_group_buttons(self, groups: dict, initial_group: str):
        """Add the group buttons to rows 1 and 2.
         
        Takes a groups dict containing the information in the `[groups]` table in the
        the main `config.toml`, of the form:
        `{group_initials: group_name, ... , other: {group_initials: group_name, ... }}`
        From this it generates:
          1) the research group selection buttons
          2) a drop down list for further options that appears when "other" is selected
        """

        self.group_buttons = GroupButtons(
            self, list(groups.keys()), initial_group
        )
        
        self.addLayout(self.group_buttons.main_layout, 1, 1)
        self.addLayout(self.group_buttons.overflow_layout, 2, 1)

        self.other_box = QComboBox()
        self.other_box.addItems(groups["other"].values())
        if initial_group in groups["other"].values():
            self.other_box.setCurrentText(initial_group)
        else:
            self.other_box.hide()

        self.addWidget(self.other_box, 2, 2)


    def add_spec_buttons(self, specs: dict, initial_spec: str):
        """Add the spectrometer selection buttons to row 6.
        
        Takes a specs dict containing the information in the `[spectrometers]` table in
        the main `config.toml`.
        """

        self.spec_buttons = SpecButtons(self, specs, initial_spec)
        self.addLayout(self.spec_buttons.layout, 6, 1, 1, 2)
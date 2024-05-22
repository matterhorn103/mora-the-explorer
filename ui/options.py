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

class AKButtons(QButtonGroup):
    def __init__(self, parent, ak_list, selected_ak):
        super().__init__(parent)

        self.main_layout = QHBoxLayout()
        self.overflow_layout = QHBoxLayout()
        self.button_list = []
        for ak in ak_list:
            ak_button = QRadioButton(ak)
            self.button_list.append(ak_button)
            if (ak == selected_ak) or (
                ak == "other" and self.checkedButton() is None
            ):
                ak_button.setChecked(True)
            self.addButton(ak_button)
            if len(ak_list) <= 4 or ak_list.index(ak) < (len(ak_list) / 2):
                self.main_layout.addWidget(ak_button)
            elif len(ak_list) > 4 and ak_list.index(ak) >= (len(ak_list) / 2):
                self.overflow_layout.addWidget(ak_button)


class SpecButton(QRadioButton):
    """Just like a normal QRadioButton except we can assign it a name."""

    def __init__(self, text, name):
        super().__init__(text)
        self.name = name


class SpecButtons(QButtonGroup):
    def __init__(self, parent, selected_spec):
        super().__init__(parent)

        self.layout = QVBoxLayout()

        self.spec_text = {
            "300er": "Studer group NMR only (300 MHz)",
            "400er": "routine NMR (300 && 400 MHz)",
            "hf": "high-field spectrometers (500 && 600 MHz)",
        }

        self.buttons = {}

        for spec in self.specs.keys():
            button = SpecButton(self.spec_text[spec], spec)
            self.buttons[spec] = button
            if spec == selected_spec:
                button.setChecked(True)
            self.addButton(button)
            self.layout.addWidget(button)


class OptionsLayout(QGridLayout):
    """Layout containing all user-configurable options.
    
    Widgets with more complicated code are defined in custom classes, while simple ones
    are defined in-line.
    """
    def __init__(self, config):
        super().__init__()

        # Row 0, initials entry box
        self.initials_label = QLabel("initials:").setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.initials_entry = QLineEdit().setMaxLength(3).setText(self.options["initials"])
        self.initials_hint = QLabel("(lowercase!)").setAlignment(Qt.AlignCenter)

        self.addWidget(self.initials_label, 0, 0)
        self.addWidget(self.initials_entry, 0, 1)
        self.addWidget(self.initials_hint, 0, 2)
        
        
        # Row 1, research group selection buttons
        self.group_label = QLabel("group:").setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.AK_buttons = AKButtons(self, list(config.groups.keys()), config.options["group"])

        self.addWidget(self.group_label, 1, 0)
        self.addLayout(self.AK_buttons.main_layout, 1, 1)
        self.addLayout(self.AK_buttons.overflow_layout, 2, 1)


        # Row 2, drop down list for further options that appears only when "other"
        # radio button is clicked
        self.other_box = QComboBox().addItems(config.groups["other"].values())
        if config.options["group"] in config.groups["other"].values():
            self.other_box.setCurrentText(config.options["group"])
        else:
            self.other_box.hide()

        self.addWidget(self.other_box, 2, 2)


        # Row 3, destination path entry box
        self.dest_path_label = QLabel("save in:").setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.dest_path_input = QLineEdit().setText(config.options["dest_path"])
        self.open_button = QPushButton("go to").setShortcut("Ctrl+G")
        # Disable button if path hasn't yet been specified to stop new users thinking it should be used to select a folder
        if config.options["dest_path"] == "copy full path here":
            self.open_button.hide()
        
        self.addWidget(self.dest_path_label, 3, 0)
        self.addWidget(self.dest_path_input, 3, 1)
        self.addWidget(self.open_button, 3, 2)


        # Row 4, file naming options
        self.include_label = QLabel("include:").setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.inc_init_checkbox = QCheckBox("initials").setChecked(config.options["inc_init"])
        if config.options["nmrcheck_style"] is True:
            self.inc_init_checkbox.setEnabled(False)
        self.inc_solv_checkbox = QCheckBox("solvent").setChecked(config.options["inc_solv"])
        if config.options["spec"] == "hf":
            self.inc_solv_checkbox.setEnabled(False)
        self.in_filename_label = QLabel("...in filename").setAlignment(Qt.AlignCenter)
        
        self.addWidget(self.include_label, 4, 0)
        self.addLayout(QHBoxLayout().addWidget(self.inc_init_checkbox).addWidget(self.inc_solv_checkbox), 4, 1)
        self.addWidget(self.in_filename_label, 4, 2)


        # Row 5, option to use NMRCheck-style formatting of folder names
        self.nmrcheck_style_checkbox = QCheckBox("use comprehensive (NMRCheck) style").setChecked(config.options["nmrcheck_style"])
        
        self.addWidget(self.nmrcheck_style_checkbox, 5, 1, 1, 2)


        # Row 6, spectrometer selection buttons
        self.spec_label = QLabel("search:").setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.spec_buttons = SpecButtons(self, config.options["spec"])

        self.addWidget(self.spec_label, 6, 0)
        self.addLayout(self.spec_buttons.layout, 6, 1, 1, 2)


        # Row 7, checkbox to instruct to repeat after chosen interval
        self.repeat_label = QLabel("repeat:").setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.repeat_check_checkbox = QCheckBox("check every").setChecked(self.options["repeat_switch"])
        self.repeat_interval = QSpinBox().setMinimum(1).setValue(self.options["repeat_delay"])

        self.addWidget(self.repeat_label, 7, 0)
        self.addLayout(QHBoxLayout().addWidget(self.repeat_check_checkbox).addWidget(self.repeat_interval).addWidget(QLabel("mins")), 7, 1)


        # Row 8, button to save all options for future
        self.save_button = QPushButton("save options as defaults for next time").setEnabled(False)

        self.addWidget(self.save_button, 8, 0, 1, 3)


        # Row 9, date selection tool
        self.date_label = QLabel("when?").setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.today_button = QPushButton("today")

        self.addWidget(self.date_label, 9, 0)
        self.addWidget(self.today_button, 9, 2)

        # Date selection tool for 300er and 400er
        self.only_button = QRadioButton("only").setChecked(True)
        self.since_button = QRadioButton("since")
        self.date_button_group = QButtonGroup(self).addButton(self.only_button).addButton(self.        since_button)
        self.date_selector = QDateEdit().setDisplayFormat("dd MMM yyyy").setDate(date.today())

        self.addLayout(QHBoxLayout().addWidget(self.only_button, 0).addWidget(self.since_button, 1).addWidget(self.date_selector, 2), 9, 1)
        
        # Date selection tool for hf (only needs year)
        self.hf_date_selector = QDateEdit().setDisplayFormat("yyyy").setDate(date.today())

        # Add to same part of layout as the normal date selector -
        # only one is shown at a time
        self.addWidget(self.hf_date_selector, 9, 1)

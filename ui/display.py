from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QLabel,
    QSizePolicy,
)

class Display(QScrollArea):
    """Box to display output of check function (list of copied spectra)"""

    def __init__(self):
        super().__init__()

        self.setWidgetResizable(True)
        self.layout = QVBoxLayout()
        self.display = QWidget()
        self.display.setLayout(self.layout)
        self.setWidget(self.display)

        # Make each label only take up a single line of space rather than spreading
        # across the box, so that they stack nicely
        self.display.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        # Connect scrollbar so that it scrolls down whenever the list gets longer
        self.scrollbar = self.verticalScrollBar()
        self.scrollbar.rangeChanged.connect(self.scroll_down)

        # Find out how tall a single line of text is and set step sizes accordingly
        # TODO get a better estimate somehow - currently gives about 1.3 times the
        # height of a "given destination not found!" label
        line_height = QLabel("ABCabcdefghijklmnopJKP!").sizeHint().height()
        self.scrollbar.setSingleStep(line_height)
        self.scrollbar.setPageStep(3 * line_height)

    def add_entry(self, entry):
        self.layout.addWidget(entry, alignment=Qt.AlignTop)

    def scroll_down(self):
        self.scrollbar.setSliderPosition(self.scrollbar.maximum())

from PySide6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

class Display(QScrollArea):
    """Box to display output of check function (list of copied spectra)"""

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.layout = QVBoxLayout()
        self.display = QWidget().setLayout(self.layout)
        self.setWidget(self.display)

    def add_entry(self, entry):
        self.layout.addWidget(entry)

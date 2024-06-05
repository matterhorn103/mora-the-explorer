from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from .spinner import WaitingSpinner


class StatusBar(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel("checking...")
        self.spinner = WaitingSpinner(
            self,
            roundness=100.0,
            opacity=3.141592653589793,
            fade=80.0,
            radius=5,
            lines=20,
            line_length=10,
            line_width=2,
            speed=1.5707963267948966,
            color=QColor(184, 140, 206)
        )
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinner)

    def setText(self, text):
        self.label.setText(text)

    def hide(self):
        super().hide()
        self.label.hide()
        self.spinner.hide()
        self.spinner.stop()

    def show(self):
        super().show()
        self.label.show()
        self.spinner.show()
        self.spinner.start()


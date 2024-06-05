from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton

from .spinner import WaitingSpinner


class StatusBar(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Button to begin check
        self.start_button = QPushButton("start check now")
        self.start_button.setStyleSheet("background-color : #b88cce")
        self.layout.addWidget(self.start_button, 0, 0)
        # Make sure the whole status bar stays the same size as the button
        # even when the button isn't visible
        start_button_size_policy = self.start_button.sizePolicy()
        start_button_size_policy.setRetainSizeWhenHidden(True)
        self.start_button.setSizePolicy(start_button_size_policy)

        # Information for when check is in progress
        self.label = QLabel("checking...")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.layout.addWidget(self.label, 0, 0)

        self.spinner = WaitingSpinner(
            self.label,
            center_on_parent=True,
            roundness=100.0,
            opacity=3.141592653589793,
            fade=80.0,
            radius=3,
            lines=20,
            line_length=5,
            line_width=2,
            speed=1.5707963267948966,
            color=QColor(184, 140, 206)
        )
        #self.layout.addWidget(self.spinner)

        # Button to cancel pending repeat check
        self.cancel_button = QPushButton("cancel repeat check")
        self.cancel_button.setStyleSheet("background-color : #cc0010; color : white")
        self.layout.addWidget(self.cancel_button, 0, 0)

        self.show_start()

    def setText(self, text):
        self.label.setText(text)

    def show_start(self):
        self.start_button.show()
        self.label.hide()
        self.spinner.hide()
        self.spinner.stop()
        self.cancel_button.hide()
    
    def show_status(self):
        self.start_button.hide()
        self.label.show()
        self.spinner.show()
        self.spinner.start()
        self.cancel_button.hide()

    def show_cancel(self):
        self.start_button.hide()
        self.label.hide()
        self.spinner.hide()
        self.spinner.stop()
        self.cancel_button.show()

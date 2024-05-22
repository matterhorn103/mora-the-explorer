import platform

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QPushButton,
    QLabel,
    QProgressBar,
    QVBoxLayout,
)

from ui.options import OptionsLayout
from ui.display import Display

class Layout(QVBoxLayout):
    """Main layout, which is a simple vertical stack."""

    def __init__(self, config):
        super().__init__()
        self.add_elements(config)


    def add_elements(self, config):
        # Title and version info header
        self.setWindowTitle("Mora the Explorer")
        with open(self.rsrc_dir / "version.txt", encoding="utf-8") as f:
            version_info = "".join(f.readlines()[:5])
        version_box = QLabel(version_info).setAlignment(Qt.AlignHCenter)
        self.addWidget(version_box)

        # All the user-configurable options
        self.opts = OptionsLayout(config)
        self.addLayout(self.opts)

        # Button to begin check
        self.start_check_button = QPushButton("start check now").setStyleSheet("background-color : #b88cce")
        self.addWidget(self.start_check_button)

        # Button to cancel pending repeat check
        self.interrupt_button = QPushButton("cancel repeat check").setStyleSheet("background-color : #cc0010; color : white")
        self.addWidget(self.interrupt_button).hide()

        # Progress bar for check
        self.prog_bar = QProgressBar().setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        if platform.system() == "Windows" and platform.release() == "11":
            # Looks bad (with initial Qt Win11 theme at least) so disable text
            self.prog_bar.setTextVisible(False)
        self.addWidget(self.prog_bar)

        # Box to display output of check function (list of copied spectra)
        self.display = Display()
        self.addWidget(self.display)

        # Extra notification that spectra have been found, dismissable
        self.notification = QPushButton().hide()
        self.addWidget(self.notification)

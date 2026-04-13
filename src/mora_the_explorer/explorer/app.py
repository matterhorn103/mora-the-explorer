import sys

from PySide6.QtCore import QCoreApplication

# Various things in the explorer module won't work without an instance of
# QCoreApplication or one of its subclasses
# So if there isn't an existing app singleton, create one
# Otherwise just provides access to the currently running Qt app
class App:

    _instance = None

    def __init__(self, core_only: bool = False):
        if App._instance is not None:
            pass
        elif core_only:
            App._instance = QCoreApplication()
        else:
            from PySide6.QtWidgets import QApplication
            App._instance = QApplication()

    def get(self):
        return App._instance

    def change(self, application_class):
        App._instance.shutdown()
        App._instance = application_class()

    def exec(self):
        sys.exit(App._instance.exec())

    def exit(self, exit_code: int):
        App._instance.exit(exit_code)

    def has_gui(self) -> bool:
        from PySide6.QtWidgets import QApplication
        if isinstance(App._instance, QApplication):
            return True
        else:
            return False

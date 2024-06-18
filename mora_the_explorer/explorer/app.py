from PySide6.QtCore import QCoreApplication


# Various things in the explorer module won't work without an instance of
# QCoreApplication or one of its subclasses
# So if there isn't an existing app singleton, create one
# Otherwise just provides access to the currently running Qt app
if QCoreApplication.instance() is None:
    app = QCoreApplication()
else:
    app = QCoreApplication.instance()
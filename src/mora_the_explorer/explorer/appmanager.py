from PySide6.QtCore import QCoreApplication


# Various things in the explorer module won't work without an instance of
# QCoreApplication or one of its subclasses
# So if there isn't an existing app singleton, create one
# Otherwise just provides access to the currently running Qt app
class AppManager:
    _instance = QCoreApplication()

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def change_instance(cls, application_class):
        cls._instance.shutdown()
        cls._instance = application_class()


def app():
    return QCoreApplication.instance()

import logging

from PySide6.QtCore import QRunnable, Signal, Slot, QObject


class WorkerSignals(QObject):
    progress = Signal(int)
    status = Signal(str)
    completed = Signal(list)


class Worker(QRunnable):
    """A container for a function to make it executable in a thread from a QThreadPool."""
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # The function and the args and kwargs to be passed need to saved as attributes
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        # Give the worker signals
        self.signals = WorkerSignals()
        # Add the progress and status signals to kwargs so they are available within and
        # can be emitted from the function scope
        self.kwargs["progress_callback"] = self.signals.progress
        self.kwargs["status_callback"] = self.signals.status

    @Slot()
    def run(self):
        # Run the Worker's function with passed args, kwargs, including the callbacks
        try:
            output = self.fn(*self.args, **self.kwargs)
            # After completion of the function, emit the output as the result signal so that
            # it can be picked up by anything connected to the signal
            self.signals.completed.emit(output)
        except Exception as error:
            logging.exception("Exception raised by check_nmr")
            self.signals.completed.emit([
                "Exception",
                type(error).__name__,
                *(error.args),
                "See log file at:",
                str(logging.getLogger().handlers[0].baseFilename),
                "for further details",
            ])

from PySide6.QtCore import QRunnable, Signal, Slot, QObject


class WorkerSignals(QObject):
    progress = Signal(int)
    status = Signal(str)
    result = Signal(object)
    completed = Signal()


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
        output = self.fn(*self.args, **self.kwargs)
        # After completion of the function, emit the output as the result signal so that
        # it can be picked up by anything connected to the signal
        self.signals.result.emit(output)
        self.signals.completed.emit()

from PySide6.QtCore import QRunnable, Signal, Slot, QObject


class WorkerSignals(QObject):
    progress = Signal(int)
    result = Signal(object)
    completed = Signal()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Pass function itself, along with provided arguments, to new function within the Checker instance
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        # Give the Checker signals
        self.signals = WorkerSignals()
        # Add the callback to kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @Slot()
    def run(self):
        # Run the Worker function with passed args, kwargs, including progress_callback
        output = self.fn(*self.args, **self.kwargs)
        # Emit the output of the function as the result signal so that it can be picked up
        self.signals.result.emit(output)
        self.signals.completed.emit()

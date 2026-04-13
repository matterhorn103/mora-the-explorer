from datetime import datetime
import logging

from PySide6.QtCore import QRunnable, Signal, Slot, QObject

from ..check import Reporter


class PrintingReporter(Reporter):
    def __init__(self):
        self._progress = 0
        self._max_progress = 0
        self._status = ""
        self.output = []

    def set_status(self, message):
        self._status = message
        print(message)

    def progress(self) -> int:
        return self._progress
    
    def report_progress(self):
        print(f"Progress: {round((self._progress / self._max_progress) * 100)}%")

    def reset_progress(self):
        self._progress = 0
        self.report_progress()

    def increment_progress(self, increment: int = 1):
        self._progress += increment
        self.report_progress()

    def max_progress(self) -> int:
        return self._max_progress

    def set_max_progress(self, max: int):
        self._max_progress = max
        #print(f"New max progress: {max}")

    def append_output(self, line: str):
        self.output.append(line)
        print(line)

    def finish(self, completion_message: str):
        self._progress = self._max_progress
        self.report_progress()
        self.output.append(completion_message)
        print(completion_message)


class QtReporter(Reporter):
    def __init__(self):
        self._progress = 0
        self._max_progress = 0
        self.signals = WorkerSignals()
        self.output = []

    def set_status(self, message):
        self.signals.set_status.emit(message)

    def progress(self) -> int:
        return self._progress

    def reset_progress(self):
        self._progress = 0
        self.signals.update_progress.emit(0)

    def increment_progress(self, increment: int = 1):
        self._progress += increment
        self.signals.update_progress.emit(self._progress)

    def max_progress(self) -> int:
        return self._max_progress

    def set_max_progress(self, max: int):
        self._max_progress = max
        self.signals.set_max_progress.emit(max)

    def append_output(self, line: str):
        self.output.append(line)

    def finish(self, completion_message: str):
        self.output.append(completion_message)
        self.signals.completed.emit(self.output)


class WorkerSignals(QObject):
    update_progress = Signal(int)
    set_max_progress = Signal(int)
    set_status = Signal(str)
    completed = Signal(list)


class Worker(QRunnable):
    """A container for a function to make it executable in a thread from a QThreadPool."""

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # The function and the args and kwargs to be passed need to saved as attributes
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        ## Give the worker signals
        #self.signals = WorkerSignals()
        ## Add the progress and status signals to kwargs so they are available within and
        ## can be emitted from the function scope
        #self.kwargs["progress_callback"] = self.signals.progress
        #self.kwargs["status_callback"] = self.signals.status

        # New approach - give the worker a reporter
        # The reporter will process all the feedback that the checking function sends
        # and emit the relevant signals
        self.reporter = QtReporter()

    @Slot()
    def run(self):
        # Run the Worker's function with passed args, kwargs, including the callbacks
        try:
            self.fn(*self.args, **self.kwargs, reporter=self.reporter)
        except Exception as e:
            logging.exception(f"{type(e).__name__} raised by check_nmr")
            logging.exception(repr(*(e.args)))
            message_lines = [
                "Exception",
                type(e).__name__,
                *(e.args),
                "See log file at:",
                str(logging.getLogger().handlers[0].baseFilename),
                "for further details",
            ]
            # Since the function won't have finished, wrap it up ourselves
            self.reporter.output.extend(message_lines)
            now = datetime.now().strftime("%H:%M:%S")
            completed_statement = f"Check terminated with error at {now}"
            self.reporter.finish(completed_statement)

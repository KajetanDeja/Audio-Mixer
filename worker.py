import traceback
from PySide6 import QtCore
from audio_utils import full_pipeline

class Worker(QtCore.QObject):
    progress = QtCore.Signal(int)
    log      = QtCore.Signal(str)
    finished = QtCore.Signal()
    error    = QtCore.Signal(str)

    def __init__(self, in_vid: str, out_vid: str, vol: float):
        super().__init__()
        self.in_vid, self.out_vid, self.vol = in_vid, out_vid, vol

    @QtCore.Slot()
    def run(self):
        try:
            full_pipeline(
                self.in_vid,
                self.out_vid,
                self.vol,
                logger_signal=self.log.emit,
                progress_signal=self.progress.emit
            )
            self.finished.emit()
        except Exception as e:
            tb = traceback.format_exc()
            self.log.emit(tb)
            self.error.emit(str(e))
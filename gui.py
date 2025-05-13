import os
import time
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt, QThread, Slot
from worker import Worker


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Mixer")
        self.resize(1000, 700)
        self._build_ui()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_v = QtWidgets.QVBoxLayout(central)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)

        # — HEADER —
        header = QtWidgets.QFrame(objectName="Header")
        header.setFixedHeight(60)
        h_layout = QtWidgets.QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)
        title = QtWidgets.QLabel("Audio Mixer", objectName="AppTitle")
        h_layout.addStretch()
        h_layout.addWidget(title, alignment=Qt.AlignCenter)
        h_layout.addStretch()
        main_v.addWidget(header)

        # — CONTENT —
        content = QtWidgets.QWidget()
        c_layout = QtWidgets.QVBoxLayout(content)
        c_layout.setContentsMargins(40, 20, 40, 20)
        c_layout.setSpacing(30)

        io_group = QtWidgets.QGroupBox("Wejście i wyjście")
        io_layout = QtWidgets.QHBoxLayout(io_group)
        io_layout.setSpacing(20)

        self.in_path = QtWidgets.QLineEdit(placeholderText="Wybierz plik wideo…")
        in_btn = QtWidgets.QPushButton("Browse", objectName="PrimaryButton")
        in_btn.clicked.connect(lambda: self._choose(self.in_path, False))
        io_layout.addWidget(self.in_path, 3)
        io_layout.addWidget(in_btn, 1)

        self.out_path = QtWidgets.QLineEdit(placeholderText="Gdzie zapisać wynik…")
        out_btn = QtWidgets.QPushButton("Save As", objectName="PrimaryButton")
        out_btn.clicked.connect(lambda: self._choose(self.out_path, True))
        io_layout.addWidget(self.out_path, 3)
        io_layout.addWidget(out_btn, 1)

        c_layout.addWidget(io_group)

        vol_group = QtWidgets.QGroupBox("Poziom muzyki")
        vol_layout = QtWidgets.QHBoxLayout(vol_group)
        self.volume = QtWidgets.QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(30)
        vol_layout.addWidget(self.volume)
        c_layout.addWidget(vol_group)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        c_layout.addWidget(self.progress)

        self.eta_label = QtWidgets.QLabel("ETA: --:--")
        self.eta_label.setAlignment(Qt.AlignRight)
        c_layout.addWidget(self.eta_label)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setFixedHeight(160)
        c_layout.addWidget(self.log)

        main_v.addWidget(content, 1)

        footer = QtWidgets.QFrame()
        f_layout = QtWidgets.QHBoxLayout(footer)
        f_layout.setContentsMargins(0, 0, 0, 20)
        f_layout.addStretch()

        self.start_btn = QtWidgets.QPushButton("▶️ Start", objectName="PrimaryButton")
        self.start_btn.setFixedSize(140, 40)
        self.start_btn.clicked.connect(self._on_start)
        f_layout.addWidget(self.start_btn)

        exit_btn = QtWidgets.QPushButton("⏹️ Exit", objectName="SecondaryButton")
        exit_btn.setFixedSize(140, 40)
        exit_btn.clicked.connect(self.close)
        f_layout.addWidget(exit_btn)

        f_layout.addStretch()
        main_v.addWidget(footer)

    def _choose(self, edit: QtWidgets.QLineEdit, save: bool):
        fn = QtWidgets.QFileDialog.getSaveFileName if save else QtWidgets.QFileDialog.getOpenFileName
        path, _ = fn(self, "Select file", os.getcwd(), "MP4 (*.mp4)")
        if path:
            edit.setText(path)

    @Slot()
    def _on_start(self):
        in_f, out_f = self.in_path.text().strip(), self.out_path.text().strip()
        if not in_f or not out_f:
            QtWidgets.QMessageBox.warning(self, "Błąd", "Wskaż oba pliki!")
            return

        self.start_time = time.time()
        self.progress.setValue(0)
        self.eta_label.setText("ETA: --:--")
        self.log.clear()
        self.start_btn.setEnabled(False)

        self.thread = QThread()
        self.worker = Worker(in_f, out_f, self.volume.value() / 100.0)
        self.worker.moveToThread(self.thread)

        self.worker.progress.connect(self._update_progress)
        self.worker.log.connect(self.log.appendPlainText)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_finished)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    @Slot(int)
    def _update_progress(self, val: int):
        self.progress.setValue(val)
        elapsed = time.time() - self.start_time
        if 0 < val < 100:
            total_est = elapsed * 100.0 / val
            remain = total_est - elapsed
            m, s = divmod(int(remain), 60)
            self.eta_label.setText(f"ETA: {m:02d}:{s:02d}")
        elif val >= 100:
            self.eta_label.setText("ETA: 00:00")
        else:
            self.eta_label.setText("ETA: --:--")

    @Slot(str)
    def _on_error(self, msg: str):
        QtWidgets.QMessageBox.critical(self, "Błąd", msg)
        self.start_btn.setEnabled(True)
        if hasattr(self, "thread"):
            self.thread.quit()

    @Slot()
    def _on_finished(self):
        QtWidgets.QMessageBox.information(self, "Sukces", "Operacja zakończona pomyślnie!")
        self.start_btn.setEnabled(True)
        self.eta_label.setText("ETA: 00:00")

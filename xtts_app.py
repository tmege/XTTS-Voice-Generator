import sys
import os

# Patch torch.load before any TTS import
import torch
_original_load = torch.load
def patched_load(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)
torch.load = patched_load

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Dev/xtts_output")
CUSTOM_VOICES_DIR = os.path.expanduser("~/Dev/xtts_voices")

# Sentinel values for voice combo
VOICE_RANDOM = "__random__"
VOICE_BROWSE = "__browse__"
VOICE_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg"}

# All built-in XTTS v2 speakers
XTTS_SPEAKERS = [
    "Claribel Dervla", "Daisy Studious", "Gracie Wise", "Tammie Ema",
    "Alison Dietlinde", "Ana Florence", "Annmarie Nele", "Asya Anara",
    "Brenda Stern", "Gitta Nikolina", "Henriette Usha", "Sofia Hellen",
    "Tammy Grit", "Tanja Adelina", "Vjollca Johnnie",
    "Andrew Chipper", "Badr Odhiambo", "Dionisio Schuyler", "Royston Min",
    "Viktor Eka", "Abrahan Mack", "Adde Michal", "Baldur Sanjin",
    "Craig Gutsy", "Damien Black", "Gilberto Mathias", "Ilkin Urbano",
    "Kazuhiko Atallah", "Ludvig Milivoj", "Suad Qasim", "Torcull Diarmuid",
    "Viktor Menelaos", "Zacharie Aimilios", "Nova Hogarth", "Maja Ruoho",
    "Uta Obando", "Lidiya Szekeres", "Chandra MacFarland", "Szofi Granger",
    "Camilla Holmström", "Lilya Stainthorpe", "Zofija Kendrick", "Narelle Moon",
    "Barbora MacLean", "Alexandra Hisakawa", "Alma María", "Rosemary Okafor",
    "Ige Behringer", "Filip Traverse", "Damjan Chapman", "Wulf Carlevaro",
    "Aaron Dreschner", "Kumar Dahl", "Eugenio Mataracı", "Ferran Simen",
    "Xavier Hayasaka", "Luis Moray", "Marcos Rudaski",
]


class TTSWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, text, language, speaker_name, speaker_wav, output_path):
        super().__init__()
        self.text = text
        self.language = language
        self.speaker_name = speaker_name
        self.speaker_wav = speaker_wav
        self.output_path = output_path
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            from TTS.api import TTS
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            if self._cancel:
                self.cancelled.emit()
                return
            kwargs = {
                "text": self.text,
                "file_path": self.output_path,
                "language": self.language,
            }
            if self.speaker_wav:
                kwargs["speaker_wav"] = self.speaker_wav
            elif self.speaker_name:
                kwargs["speaker"] = self.speaker_name
            else:
                kwargs["speaker"] = "random"
            tts.tts_to_file(**kwargs)
            if self._cancel:
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
                self.cancelled.emit()
                return
            self.finished.emit(self.output_path)
        except Exception as e:
            if self._cancel:
                self.cancelled.emit()
            else:
                self.error.emit(str(e))


class XTTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XTTS Voice Generator")
        self.setMinimumWidth(600)
        self.worker = None
        self.last_output = None
        self._generating = False
        os.makedirs(CUSTOM_VOICES_DIR, exist_ok=True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Text input
        layout.addWidget(QLabel("Text to synthesize:"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter your text here...")
        self.text_edit.setMaximumHeight(120)
        layout.addWidget(self.text_edit)

        # Language selector
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["fr", "en", "es", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "ko", "hu"])
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        # Voice selector (custom voices + built-in speakers + browse)
        voice_row = QHBoxLayout()
        voice_row.addWidget(QLabel("Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.voice_combo.setMinimumWidth(300)
        self._populate_voices()
        self.voice_combo.showPopup = self._voice_show_popup
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        voice_row.addWidget(self.voice_combo)
        open_voices_btn = QPushButton("Open voices folder")
        open_voices_btn.clicked.connect(self._open_voices_folder)
        voice_row.addWidget(open_voices_btn)
        voice_row.addStretch()
        layout.addLayout(voice_row)

        # Output directory
        outdir_row = QHBoxLayout()
        outdir_row.addWidget(QLabel("Output folder:"))
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.outdir_label = QLineEdit(self.output_dir)
        self.outdir_label.setReadOnly(True)
        outdir_row.addWidget(self.outdir_label)
        outdir_btn = QPushButton("Change")
        outdir_btn.clicked.connect(self._browse_output_dir)
        outdir_row.addWidget(outdir_btn)
        layout.addLayout(outdir_row)

        # Output filename
        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("File name:"))
        self.out_name = QLineEdit("output.wav")
        out_row.addWidget(self.out_name)
        layout.addLayout(out_row)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Button
        btn_row = QHBoxLayout()
        self.gen_btn = QPushButton("Generate")
        self.gen_btn.clicked.connect(self._on_btn_click)
        btn_row.addWidget(self.gen_btn)
        layout.addLayout(btn_row)

        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _scan_custom_voices(self):
        voices = []
        if os.path.isdir(CUSTOM_VOICES_DIR):
            for f in sorted(os.listdir(CUSTOM_VOICES_DIR)):
                if os.path.isfile(os.path.join(CUSTOM_VOICES_DIR, f)) and os.path.splitext(f)[1].lower() in VOICE_EXTENSIONS:
                    voices.append(f)
        return voices

    def _populate_voices(self):
        current_data = self.voice_combo.currentData() if self.voice_combo.count() > 0 else None
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        # Random
        self.voice_combo.addItem("Random", VOICE_RANDOM)
        # Custom voices from ~/Dev/xtts_voices/
        custom = self._scan_custom_voices()
        if custom:
            self.voice_combo.insertSeparator(self.voice_combo.count())
            for f in custom:
                label = os.path.splitext(f)[0]
                path = os.path.join(CUSTOM_VOICES_DIR, f)
                self.voice_combo.addItem(f"~ {label}", f"file:{path}")
        # Built-in XTTS speakers
        self.voice_combo.insertSeparator(self.voice_combo.count())
        for name in XTTS_SPEAKERS:
            self.voice_combo.addItem(name, f"speaker:{name}")
        # Browse for external file
        self.voice_combo.insertSeparator(self.voice_combo.count())
        self.voice_combo.addItem("External file...", VOICE_BROWSE)
        # Restore selection
        if current_data:
            idx = self.voice_combo.findData(current_data)
            if idx >= 0:
                self.voice_combo.setCurrentIndex(idx)
        self.voice_combo.blockSignals(False)

    def _voice_show_popup(self):
        self._populate_voices()
        QComboBox.showPopup(self.voice_combo)

    def _on_voice_changed(self, index):
        if self.voice_combo.currentData() == VOICE_BROWSE:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select a reference voice", "",
                "Audio (*.wav *.mp3 *.flac *.ogg);;All (*)"
            )
            if path:
                label = os.path.splitext(os.path.basename(path))[0]
                insert_idx = self.voice_combo.count() - 1
                self.voice_combo.blockSignals(True)
                self.voice_combo.insertItem(insert_idx, f"{label} (file)", f"file:{path}")
                self.voice_combo.setCurrentIndex(insert_idx)
                self.voice_combo.blockSignals(False)
            else:
                self.voice_combo.blockSignals(True)
                self.voice_combo.setCurrentIndex(0)
                self.voice_combo.blockSignals(False)

    def _open_voices_folder(self):
        os.makedirs(CUSTOM_VOICES_DIR, exist_ok=True)
        import subprocess
        subprocess.Popen(["open", CUSTOM_VOICES_DIR])
        self.status_label.setText(f"Drop audio files in {CUSTOM_VOICES_DIR}")

    def _browse_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choose output folder", self.output_dir)
        if d:
            self.output_dir = d
            self.outdir_label.setText(d)

    def _on_btn_click(self):
        if self._generating:
            self._cancel_generation()
        else:
            self._generate()

    def _generate(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Error", "Please enter some text.")
            return

        filename = self.out_name.text().strip()
        if not filename:
            filename = "output.wav"
        if not filename.endswith(".wav"):
            filename += ".wav"

        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, filename)

        voice_data = self.voice_combo.currentData()
        speaker_name = None
        speaker_wav = None
        if voice_data == VOICE_RANDOM:
            pass
        elif voice_data.startswith("speaker:"):
            speaker_name = voice_data[len("speaker:"):]
        elif voice_data.startswith("file:"):
            speaker_wav = voice_data[len("file:"):]

        self._generating = True
        self.gen_btn.setText("Cancel")
        self.gen_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        self.progress.setVisible(True)
        self.status_label.setText("Generating...")

        self.worker = TTSWorker(text, self.lang_combo.currentText(), speaker_name, speaker_wav, output_path)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.cancelled.connect(self._on_cancelled)
        self.worker.start()

    def _cancel_generation(self):
        if self.worker:
            self.worker.cancel()
            self.status_label.setText("Cancelling...")
            self.gen_btn.setEnabled(False)
            self.worker.terminate()
            self.worker.wait(3000)
            self._reset_ui()
            self.status_label.setText("Generation cancelled.")

    def _on_finished(self, path):
        self._reset_ui()
        self.last_output = path
        self.status_label.setText(f"File generated: {path}")

    def _on_error(self, msg):
        self._reset_ui()
        self.status_label.setText("Error")
        QMessageBox.critical(self, "Generation error", msg)

    def _on_cancelled(self):
        self._reset_ui()
        self.status_label.setText("Generation cancelled.")

    def _reset_ui(self):
        self._generating = False
        self.gen_btn.setText("Generate")
        self.gen_btn.setStyleSheet("")
        self.gen_btn.setEnabled(True)
        self.progress.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XTTSApp()
    window.show()
    sys.exit(app.exec_())

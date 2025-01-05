import sys
import os
import re
import math
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtGui import QFont
from pydub import AudioSegment
import speech_recognition as sr
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract
from yt_dlp import YoutubeDL
import uuid

class SplitThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, folder, filename):
        super().__init__()
        self.folder = folder
        self.filename = filename

    def run(self):
        filepath = os.path.join(self.folder, self.filename)
        split_folder = os.path.join(self.folder, "splits")
        os.makedirs(split_folder, exist_ok=True)

        try:
            audio = AudioSegment.from_wav(filepath)
            total_mins = math.ceil(len(audio) / (60 * 1000))
            for i in range(total_mins):
                t1 = i * 60 * 1000
                t2 = (i + 1) * 60 * 1000
                split_audio = audio[t1:t2]
                split_filename = os.path.join(split_folder, f"{i}_{os.path.splitext(self.filename)[0]}.wav")
                split_audio.export(split_filename, format="wav")
                progress = int(((i + 1) / total_mins) * 100)
                self.progress_signal.emit(progress)
            self.finished_signal.emit()
        except Exception as e:
            print(f"Error during splitting: {e}")

class ConversionThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, folder, filename, file_input=None):
        super().__init__()
        self.folder = folder
        self.filename = filename
        self.file_input = file_input

    def run(self):
        filepath = os.path.join(self.folder, self.filename)
        try:
            if self.filename.endswith('.mp3'):
                mp3_path = filepath
                wav_path = os.path.splitext(mp3_path)[0] + '.wav'
                self.progress_signal.emit("Converting MP3 to WAV...")
                audio = AudioSegment.from_mp3(mp3_path+".mp3")
                audio.export(wav_path, format="wav")
                self.progress_signal.emit("Conversion complete.")
                if self.file_input:
                    self.file_input.setText(wav_path)
                self.finished_signal.emit(wav_path)
            else:
                self.finished_signal.emit(filepath)
        except Exception as e:
            self.progress_signal.emit(f"Error during conversion: {e}")

class TranscriptionThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, folder):
        super().__init__()
        self.folder = folder

    def run(self):
        transcript = []
        segments_folder = os.path.join(self.folder, "splits")
        files = sorted_alphanumeric(os.listdir(segments_folder))
        for file in files:
            if file.endswith(".wav"):
                file_path = os.path.join(segments_folder, file)
                try:
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(file_path) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data, language='fr-FR')
                        transcript.append(text)
                        self.update_signal.emit(text)
                except Exception as e:
                    print(f"Error transcribing {file}: {e}")
        combined_transcript = " ".join(transcript)
        self.finished_signal.emit(combined_transcript)

class YouTubeSummaryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Audio and YouTube Processing")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel("Select Audio File (WAV) or Enter YouTube URL:")
        layout.addWidget(self.label)

        self.file_input = QLineEdit()
        layout.addWidget(self.file_input)

        self.browse_button = QPushButton("Browse Audio File")
        self.browse_button.clicked.connect(self.browse_file)
        layout.addWidget(self.browse_button)

        self.youtube_button = QPushButton("Get YouTube Summary")
        self.youtube_button.clicked.connect(self.get_youtube_summary)
        layout.addWidget(self.youtube_button)

        self.process_button = QPushButton("Process Audio")
        self.process_button.clicked.connect(self.process_audio)
        layout.addWidget(self.process_button)

        self.result_label = QLabel("Result:")
        layout.addWidget(self.result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Times New Roman", 12))
        layout.addWidget(self.result_text)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.session_folder = self.create_session_folder()

    def create_session_folder(self):
        session_folder = os.path.join(os.getcwd(), f"session_{uuid.uuid4().hex[:8]}")
        os.makedirs(session_folder, exist_ok=True)
        return session_folder

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav; *.mp3)")
        if file_path:
            self.file_input.setText(file_path)

    def get_youtube_summary(self):
        url = self.file_input.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL.")
            return

        try:
            video_id = extract.video_id(url)
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr'])
            combined_transcript = " ".join([entry['text'] for entry in transcript])
            self.result_text.setText(combined_transcript)
        except Exception as e:
            print(f"Transcript unavailable: {e}. Attempting audio conversion...")
            audio_file = os.path.join(self.session_folder, "output.mp3")
            self.conversion_audio(url, audio_file)

    def conversion_audio(self, url, nom_fichier_sortie):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': nom_fichier_sortie,  # Spécifie le nom du fichier de sortie
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'keepvideo': True  # Empêche la suppression automatique des fichiers originaux
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Audio downloaded and saved as {nom_fichier_sortie}")
            self.file_input.setText(nom_fichier_sortie)
            self.process_audio()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download audio: {e}")

    def process_audio(self):
        file_path = self.file_input.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select an audio file or enter a YouTube URL.")
            return

        folder = self.session_folder
        filename = os.path.basename(file_path)

        self.conversion_thread = ConversionThread(folder, filename, file_input=self.file_input)
        #self.conversion_thread.progress_signal.connect(self.update_progress)
        self.conversion_thread.finished_signal.connect(self.start_split)
        self.conversion_thread.start()

    def start_split(self, wav_path):
        filename = os.path.basename(wav_path)
        self.split_thread = SplitThread(self.session_folder, filename)
        self.split_thread.progress_signal.connect(self.update_progress)
        self.split_thread.finished_signal.connect(self.start_transcription)
        self.split_thread.start()
    def start_transcription(self):
            self.transcription_thread = TranscriptionThread(self.session_folder)
            self.transcription_thread.update_signal.connect(self.update_live_transcription)
            self.transcription_thread.finished_signal.connect(self.finish_processing)
            self.transcription_thread.start()
    def update_progress(self, message_or_value):
        if isinstance(message_or_value, str):
            self.result_text.append(message_or_value)
        else:
            self.progress_bar.setValue(message_or_value)
    def update_live_transcription(self, text):
        current_text = self.result_text.toPlainText()
        self.result_text.setText(current_text + (" " if current_text else "") + text)
        self.result_text.moveCursor(self.result_text.textCursor().End)

    def finish_processing(self, combined_transcript):
        output_file = os.path.join(self.session_folder, "transcription.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(combined_transcript)
        QMessageBox.information(self, "Success", "Audio processed and transcription saved.")
        self.progress_bar.setValue(0)

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = YouTubeSummaryApp()
    main_window.show()
    sys.exit(app.exec_())

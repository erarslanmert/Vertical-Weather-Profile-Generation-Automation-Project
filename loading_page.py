import sys
import threading
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QMovie

class Communicate(QObject):
    close_signal = pyqtSignal()

class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set window flags to remove title bar and make the background transparent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()

        # Load the loading GIF
        self.loading_label = QLabel()
        self.loading_movie = QMovie("Images\loading.gif")  # Replace "loading.gif" with your actual file path
        self.loading_label.setMovie(self.loading_movie)
        self.loading_movie.start()

        layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.communicate = Communicate()
        self.communicate.close_signal.connect(self.close)

    def closeEvent(self, event):
        self.communicate.close_signal.emit()

class LoadingThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.app = None
        self.loading_dialog = None
        self.running = True

    def run(self):
        self.app = QApplication(sys.argv)
        self.loading_dialog = LoadingDialog()
        self.loading_dialog.show()
        self.app.exec()
        self.running = False

def start_loading_dialog_thread():
    global loading_thread
    loading_thread = LoadingThread()
    loading_thread.start()

def close_loading_dialog():
    if loading_thread.running:
        loading_thread.communicate.close_signal.emit()
        loading_thread.join()

# Example usage:
# In your main application script:
# loading_page.start_loading_dialog_thread()
# profilegenerator.start_reading_gfs()
# loading_page.close_loading_dialog()

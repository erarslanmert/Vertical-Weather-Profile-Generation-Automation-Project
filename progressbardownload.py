import sys
import requests
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QProgressBar, QLabel, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6 import QtGui
from time import time

set_url = ""
file_name = ""
list_url = []
class DownloadThread(QThread):
    progress_updated = pyqtSignal(int, int, int, int)

    def __init__(self, url, destination):
        super().__init__()
        self.url = url
        self.destination = destination

    def run(self):
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        t_start = time()
        with open(self.destination, 'wb') as file:
            downloaded_size = 0
            for data in response.iter_content(block_size):
                file.write(data)
                downloaded_size += len(data)
                progress_percentage = int((downloaded_size / total_size) * 100)
                elapsed_time = int(time() - t_start)/60

                if downloaded_size > 0:
                    try:
                        estimated_time_remaining = (total_size - downloaded_size) / (downloaded_size / elapsed_time)
                    except ZeroDivisionError:
                        pass
                else:
                    estimated_time_remaining = 0
                try:
                    self.progress_updated.emit(progress_percentage, downloaded_size, total_size, estimated_time_remaining)
                except UnboundLocalError:
                    pass

        t_end = time()
        elapsed_time = t_end - t_start
        elapsed_time = int(elapsed_time/60)
        


class ProgressBarWindow(QDialog):
    def __init__(self, url, destination):
        super().__init__()

        self.setWindowTitle("File Download Progress")
        self.setGeometry(200, 200, 400, 100)
        self.setWindowIcon(QtGui.QIcon("Images\M.png"))

        self.layout = QVBoxLayout(self)

        self.size_label = QLabel("Size: 0 / 0 MB")
        self.layout.addWidget(self.size_label)

        self.estimated_time_label = QLabel("Estimated Time Remaining: Calculating...")
        self.layout.addWidget(self.estimated_time_label)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)

        self.download_thread = DownloadThread(url, destination)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def closeEvent(self, event):
        self.download_thread.cancel_download()
        super().closeEvent(event)


    def update_progress(self, progress_percentage, downloaded_size, total_size, estimated_time_remaining):
        self.progress_bar.setValue(progress_percentage)

        total_size_mb = total_size / (1024 * 1024)
        downloaded_size_mb = downloaded_size / (1024 * 1024)

        self.size_label.setText(f"Size: {downloaded_size_mb:.2f} / {total_size_mb:.2f} MB")

        if downloaded_size > 0:
            self.estimated_time_label.setText(f"File in progress: {file_name} ")
        else:
            self.estimated_time_label.setText("Estimated Time Remaining: Calculating...")

    def download_finished(self):
        self.accept()
        ProgressBarWindow.close()
    
    def cancel_download(self):
        self.reject()


class FileManagerDialog(QDialog):
    def __init__(self):
        global set_url, file_name
        super().__init__()

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            self.selected_directory = dialog.selectedFiles()[0]
            print(f"Selected Directory: {self.selected_directory}")
            
            file_url = set_url
            destination_file = f"{self.selected_directory}/{file_name}"

            progress_bar_window = ProgressBarWindow(file_url, destination_file)
            result = progress_bar_window.exec()

            if result == QDialog.DialogCode.Accepted:
                print("Download completed.")
            else:
                print("Download canceled.")


def start_download():
    app = QApplication(sys.argv)
    dialog = FileManagerDialog()
    dialog.exec()
    sys.exit(app.exec())






    
import sys
import requests
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QProgressBar, QLabel, QFileDialog, \
    QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6 import QtGui
from time import time

set_url = []
file_names = []
list_url = []
directories = []
finished_flag = 0

class DownloadThread(QThread):
    progress_updated = pyqtSignal(int, int, int, int)
    def __init__(self, url, destination):
        super().__init__()
        self.url = url
        self.destination = destination
        self.cancelled = False

    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte

            t_start = time()
            with open(self.destination, 'wb') as file:
                downloaded_size = 0
                for data in response.iter_content(block_size):
                    if self.cancelled:
                        print(f"Download cancelled for {self.url}")
                        return

                    file.write(data)
                    downloaded_size += len(data)
                    progress_percentage = int((downloaded_size / total_size) * 100)
                    elapsed_time = time() - t_start

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
        except requests.exceptions.ChunkedEncodingError:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Icon.Critical)
            error_box.setWindowIcon(QIcon("Images\warning.png"))
            error_box.setWindowTitle("Error")
            error_box.setText("An error occurred:")
            error_box.setInformativeText('Internet connection is lost. Please check your connection and try again. In order to avoid incomplete or broken files, please check out the partially donwloaded files in the selected directory.')
            error_box.exec()

        t_end = time()
        elapsed_time = t_end - t_start
        elapsed_time = int(elapsed_time/60)

    def cancel_download(self):
        self.cancelled = True


class ProgressBarWindow(QDialog):
    def __init__(self, urls, destinations):
        super().__init__()
        self.setWindowTitle("File Download Progress")
        self.setGeometry(200, 200, 800, 200)
        self.setWindowIcon(QtGui.QIcon("Images\M.png"))

        self.layout = QVBoxLayout(self)

        self.progress_bars = []
        self.size_labels = []
        self.download_threads = []

        for url, destination in zip(urls, destinations):
            print(url)
            label = QLabel(f"Download in progress: {destination}")
            self.layout.addWidget(label)

            size_label = QLabel("Downloaded Size: 0 / 0 MB")
            self.layout.addWidget(size_label)

            progress_bar = QProgressBar(self)
            self.layout.addWidget(progress_bar)

            self.progress_bars.append(progress_bar)
            self.size_labels.append(size_label)

            download_thread = DownloadThread(url, destination)
            download_thread.progress_updated.connect(self.update_progress)
            self.download_threads.append(download_thread)
            download_thread.start()

    def closeEvent(self, event):
        global set_url, file_names, list_url
        # Cancel all download threads when closing the window
        if all(bar.value() == 100 for bar in self.progress_bars):
            for thread in self.download_threads:
                thread.cancel_download()
                thread.wait()  # Wait for the thread to finish gracefully
                print('Thread is closed')
            event.accept()
            set_url = []
            file_names = []
            list_url = []
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("You are interrupting the download process. This may cause incomplete or broken files in your stated directory. Please check for file compatibility in case you continue to analysis. Are you sure to interrupt download process?")
            msg.setWindowTitle("Warning")
            msg.setWindowIcon(QIcon("Images\warning.png"))
            # Add buttons to the message box
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

            # Execute the message box and get the user's response
            response = msg.exec()

            # Process the user's response
            if response == QMessageBox.StandardButton.Ok:
                msg.close()
                for thread in self.download_threads:
                    thread.cancel_download()
                    thread.wait()  # Wait for the thread to finish gracefully
                    print('Thread is closed')
                event.accept()
                set_url = []
                file_names = []
                list_url = []
                # Add your logic here for handling the OK button click
            else:
                event.ignore()
                # Add your logic here for handling the Cancel button click

    def update_progress(self, progress_percentage, downloaded_size, total_size, estimated_time_remaining):
        global finished_flag
        sender = self.sender()
        index = self.download_threads.index(sender)
        self.progress_bars[index].setValue(progress_percentage)

        total_size_mb = total_size / (1024 * 1024)
        downloaded_size_mb = downloaded_size / (1024 * 1024)

        size_label = self.size_labels[index]  # Get the size label corresponding to this progress bar
        size_label.setText(f"Downloaded Size: {downloaded_size_mb:.2f} / {total_size_mb:.2f} MB")

        # Check if any progress bar is not at 100%
        all_finished = all(bar.value() == 100 for bar in self.progress_bars)
        if all_finished:
            finished_flag = 1
            self.close()
        else:
            finished_flag = 0
            pass

class FileManagerDialog(QDialog):
    def __init__(self):
        global set_url, file_names, directories
        super().__init__()
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            self.selected_directory = dialog.selectedFiles()[0]
            print(f"Selected Directory: {self.selected_directory}")
            destinations = [f"{self.selected_directory}/{file_name}" for file_name in file_names]
            progress_bar_window = ProgressBarWindow(set_url, destinations)
            progress_bar_window.exec()
            directories = destinations
        else:
            set_url = []
            file_names = []
            directories = []
            pass

def start_download():
    FileManagerDialog()










    
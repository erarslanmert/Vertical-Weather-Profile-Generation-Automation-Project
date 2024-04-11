import os
import re
import socket
import threading
import utm
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QDateTimeEdit, QDialog, QFileDialog, QWidget, QVBoxLayout, \
    QLabel, QPushButton, QLineEdit, QMessageBox, QTextEdit, QScrollArea, QGridLayout, QStyledItemDelegate
from PyQt6.QtGui import QDoubleValidator, QPainter, QRegion, QPainterPath, QPixmap, QColor, QIcon, QMovie, QFont
from PyQt6.QtCore import QDateTime, Qt, QLocale, QThread, pyqtSignal, QTimer, QPropertyAnimation, QPoint, QRect, \
    QEasingCurve, QProcess
import sys
import loading_page
import notification_popups
import time_zone_finder, createURL, progressbardownload
from datetime import datetime, timedelta
import time
import profilegenerator, dashboard

selected_time_zone = ''
selected_time_interval = []
selected_location = []
download_time_interval = []
file_dir_list = []
browsed_files = []
state_1 = 0
input_validator_1 = False
input_validator_2 = False
input_validator_3 = False
input_validator_4 = False

class WorkerThread(QThread):
    text_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.text1 = ""
        self.text2 = ""

    def run(self):
        while True:
            # Simulating some heavy computation or processing
            # Replace this with your actual computation or processing
            time.sleep(0.1)

            try:
                download_time_interval = []
                selected_location = []
                selected_time_interval = []
                selected_location.append(float(self.text1))
                selected_location.append(float(self.text2))
                start_datetime = QDateTimeEdit().dateTime()
                end_datetime = QDateTimeEdit().dateTime()
                string_start_date = start_datetime.toString("dd/MM/yy hh:mm:ss")
                string_end_date = end_datetime.toString("dd/MM/yy hh:mm:ss")
                selected_time_interval.append(string_start_date)
                selected_time_interval.append(string_end_date)
                time_zone_finder.get_utc_time_from_coordinates(selected_location)
                selected_time_zone = time_zone_finder.utc_time_zone
                self.text_changed.emit(f"Selected Zone: {selected_time_zone}")
            except ValueError:
                self.text_changed.emit(f"Selected Zone: None")

    def update_texts(self, text1, text2):
        self.text1 = text1
        self.text2 = text2

class FileManagerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.open_file_dialog()

    def open_file_dialog(self):
        global browsed_files, selected_location, selected_time_interval
        try:
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # Allow selecting multiple files

            # Set file filter to show only .gfs files
            dialog.setNameFilter("GFS Files (*.f???)")
            dialog.setDefaultSuffix("gfs")

            if dialog.exec() == QFileDialog.DialogCode.Accepted:
                selected_files = dialog.selectedFiles()
                browsed_files = selected_files
                if selected_files:
                    print("Selected Files:")
                    for file_path in selected_files:
                        print(file_path)
            else:
                browsed_files = []
                selected_location = []
                selected_time_interval = []
                pass

        except OSError:
            pass


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(366, 410)
        MainWindow.setWindowIcon(QtGui.QIcon("Images/M.png"))
        MainWindow.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(110, 20, 131, 16))
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(110, 80, 131, 16))
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")

        self.label_4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(110, 180, 131, 16))
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")

        self.label_5 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(110, 240, 131, 16))
        self.label_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_5.setObjectName("label_5")

        self.dateTimeEdit = QtWidgets.QDateTimeEdit(parent=self.centralwidget)
        self.dateTimeEdit.setGeometry(QtCore.QRect(80, 40, 211, 21))
        self.dateTimeEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime())
        maxDateTime = QDateTime.currentDateTime().addSecs(358 * 3600)
        self.dateTimeEdit.setMaximumDateTime(maxDateTime)

        self.dateTimeEdit_2 = QtWidgets.QDateTimeEdit(parent=self.centralwidget)
        self.dateTimeEdit_2.setGeometry(QtCore.QRect(80, 100, 211, 21))
        self.dateTimeEdit_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.dateTimeEdit_2.setObjectName("dateTimeEdit_2")
        self.dateTimeEdit_2.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_2.setMinimumDateTime(QDateTime.currentDateTime())
        maxDateTime = QDateTime.currentDateTime().addSecs(358 * 3600)
        self.dateTimeEdit_2.setMaximumDateTime(maxDateTime)

        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(80, 200, 211, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(80, 260, 211, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(80, 220, 211, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lineEdit_4 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_4.setGeometry(QtCore.QRect(150, 240, 71, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")

        font = QFont()
        font.setBold(True)
        font.setPointSize(7)
        font.setUnderline(True)

        self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(82, 215, 31, 21))
        self.label_6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.label_6.setFont(font)

        self.label_7 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(112, 215, 41, 21))
        self.label_7.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.label_7.setFont(font)

        self.label_8 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(160, 215, 51, 21))
        self.label_8.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.label_8.setFont(font)

        self.label_9 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(220, 215, 71, 21))
        self.label_9.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.label_9.setFont(font)

        self.lineEdit_5 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_5.setGeometry(QtCore.QRect(220, 240, 71, 20))
        self.lineEdit_5.setObjectName("lineEdit_5")

        self.comboBox_2 = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(117, 240, 31, 21))
        self.comboBox_2.setObjectName("comboBox_2")

        self.spinBox = QtWidgets.QSpinBox(parent=self.centralwidget)
        self.spinBox.setGeometry(QtCore.QRect(81, 240, 35, 21))
        self.spinBox.setObjectName("spinBox")

        self.lineEdit_3.setDisabled(True)
        self.lineEdit_4.setDisabled(True)
        self.lineEdit_3.hide()
        self.lineEdit_4.hide()
        self.lineEdit_5.hide()
        self.comboBox_2.hide()
        self.spinBox.hide()
        self.label_6.hide()
        self.label_7.hide()
        self.label_8.hide()
        self.label_9.hide()

       # Create a QDoubleValidator to restrict input to numbers and a decimal point
        double_validator = QDoubleValidator()
        double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)  # Set standard notation
        double_validator.setDecimals(10)  # Set the number of decimal places allowed
        double_validator.setLocale(QLocale('en_US'))

        # Set the validator for the QLineEdit
        self.lineEdit.setValidator(double_validator)
        self.lineEdit_2.setValidator(double_validator)

        self.buttonBox = QtWidgets.QDialogButtonBox(parent=self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(50, 340, 260, 23))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        browse_button = self.buttonBox.addButton("Browse...", QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)


        # Change the text of the "Ok" button to "Download"
        self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("Download")

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 300, 301, 20))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")

        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(80, 140, 211, 22))
        self.comboBox.setObjectName("comboBox")

        self.comboBox.addItems(['                      Lat-Long', '              MGRS Coordinates', '                UTM Coordinates'])


        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.buttonBox.accepted.connect(self.okay_clicked)
        self.buttonBox.rejected.connect(loading_page.open_loading)

        self.lineEdit.setText('51.987327')
        self.lineEdit_2.setText('5.933481')

        self.lineEdit.textChanged.connect(self.update_thread_texts)
        self.lineEdit_2.textChanged.connect(self.update_thread_texts)
        self.lineEdit.textChanged.connect(self.validate_latitude)
        self.lineEdit_2.textChanged.connect(self.validate_longitude)
        self.lineEdit_3.textChanged.connect(self.validate_mgrs)
        self.lineEdit_4.textChanged.connect(self.validate_utm)

        self.worker_thread = WorkerThread()
        self.worker_thread.text_changed.connect(self.update_label)
        self.worker_thread.start()

        self.t1 = threading.Thread(target=self.is_internet_available)
        self.t1.start()

        browse_button.clicked.connect(lambda: self.browse_files())
        self.comboBox.currentIndexChanged.connect(self.combo_changed)

        self.comboBox.setCurrentIndex(0)

        self.t2 = threading.Thread(target=self.check_inputs)
        self.t2.start()

    def check_inputs(self):
        while True:
            if input_validator_1 == 1 and input_validator_2 == 1 or input_validator_3 == 1 or input_validator_4 == 1:
                self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            else:
                self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setDisabled(True)


    def combo_changed(self):
        if self.comboBox.currentIndex() == 1:
            self.lineEdit.hide()
            self.lineEdit_3.show()
            self.lineEdit_3.setEnabled(True)
            self.lineEdit.setDisabled(True)
            self.lineEdit_2.setDisabled(True)
            self.lineEdit_4.setDisabled(True)
            self.lineEdit_5.setDisabled(True)
            self.lineEdit_2.hide()
            self.lineEdit_4.hide()
            self.lineEdit_5.hide()
            self.comboBox_2.hide()
            self.spinBox.hide()
            self.label_6.hide()
            self.label_7.hide()
            self.label_8.hide()
            self.label_9.hide()
            self.lineEdit.clear()
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            self.lineEdit_5.clear()
            self.label_4.setText('MGRS Coordinate')
            self.label_5.clear()
        elif self.comboBox.currentIndex() == 2:
            self.lineEdit.hide()
            self.lineEdit_2.hide()
            self.lineEdit_4.show()
            self.lineEdit_5.show()
            self.comboBox_2.show()
            self.spinBox.show()
            self.label_6.show()
            self.label_7.show()
            self.label_8.show()
            self.label_9.show()
            self.lineEdit_4.setEnabled(True)
            self.lineEdit_5.setEnabled(True)
            self.lineEdit.setDisabled(True)
            self.lineEdit_2.setDisabled(True)
            self.lineEdit_3.setDisabled(True)
            self.lineEdit_3.hide()
            self.lineEdit.clear()
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            self.label_4.setText('UTM Coordinate')
            self.label_5.clear()
        else:
            self.lineEdit.show()
            self.lineEdit_4.hide()
            self.lineEdit_5.hide()
            self.lineEdit_5.clear()
            self.comboBox_2.hide()
            self.spinBox.hide()
            self.label_6.hide()
            self.label_7.hide()
            self.label_8.hide()
            self.label_9.hide()
            self.lineEdit_4.setDisabled(True)
            self.lineEdit_5.setDisabled(True)
            self.lineEdit.setEnabled(True)
            self.lineEdit_2.setEnabled(True)
            self.lineEdit_3.setDisabled(True)
            self.lineEdit_3.hide()
            self.lineEdit.clear()
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            self.lineEdit_4.clear()
            self.label_4.setText('Latitude')
            self.label_5.setText('Longitude')


    def validate_mgrs(self):
        global input_validator_3
        text = self.lineEdit_3.text()
        # Regular expression to validate MGRS format
        mgrs_pattern = re.compile(r"^[0-9]{1,2}[C-X][A-Z]{2}[0-9]+\s*$")
        if mgrs_pattern.match(text):
            self.lineEdit_3setStyleSheet("color: black;")  # Valid input, set color to black
            input_validator_3 = 1
        else:
            self.lineEdit_3.setStyleSheet("color: red;")  # Invalid input, set color to red
            input_validator_3 = 0

    def validate_utm(self):
        global input_validator_4
        text = self.lineEdit_4.text()
        # Regular expression to validate UTM format
        utm_pattern = re.compile(r"^[0-9]+ [0-9]+ [0-9]+ [NS]$")
        if utm_pattern.match(text):
            self.lineEdit_4.setStyleSheet("color: black;")
            input_validator_4 = 1
        else:
            self.lineEdit_4.setStyleSheet("color: red;")
            input_validator_4 = 0

    def validate_latitude(self):
        global input_validator_1
        text = self.lineEdit.text()
        # Regular expression to validate latitude format
        latitude_pattern = re.compile(r"^([-+]?\d{1,2}(?:\.\d+)?)$")
        try:
            latitude_value = float(text)
        except ValueError:
            pass
        if latitude_pattern.match(text) and -90.00000000 <= latitude_value <= 90.00000000:
            self.lineEdit.setStyleSheet("color: black;")
            input_validator_1 = 1
        else:
            self.lineEdit.setStyleSheet("color: red;")
            input_validator_1 = 0

    def validate_longitude(self):
        global input_validator_2
        text = self.lineEdit_2.text()
        # Regular expression to validate longitude format
        longitude_pattern = re.compile(r"^([-+]?\d{1,3}(?:\.\d+)?)$")
        try:
            longitude_value = float(text)
        except ValueError:
            pass
        if longitude_pattern.match(text) and -180.00000000 <= longitude_value <= 180.00000000:
            self.lineEdit_2.setStyleSheet("color: black;")
            input_validator_2 = 1
        else:
            self.lineEdit_2.setStyleSheet("color: red;")
            input_validator_2 = 0

    def mgrs_to_latlon(self,mgrs_coordinate):
        try:
            latlon = utm.to_latlon(*utm.from_mgrs(mgrs_coordinate))
            return [str(latlon[0]), str(latlon[1])]
        except Exception as e:
            return [f"Error: {e}"]

    def utm_to_latlon(self,zone, easting, northing, northern_hemisphere=True):
        try:
            latlon = utm.to_latlon(easting, northing, zone, northern_hemisphere=northern_hemisphere)
            return [str(latlon[0]), str(latlon[1])]
        except Exception as e:
            return [f"Error: {e}"]

    def is_internet_available(self):
        while True:
            try:
                # Attempt to connect to a well-known website
                socket.create_connection(("www.google.com", 80))
                self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                print('<Online>')
            except OSError:
                self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setDisabled(True)
                print('<Offline>')
            if not MainWindow.isVisible():
                self.t2.join()
                self.t1.join()
                sys.exit()
                break
            time.sleep(5)


    def update_thread_texts(self):
        text1 = self.lineEdit.text()
        text2 = self.lineEdit_2.text()
        self.worker_thread.update_texts(text1, text2)

    def update_label(self, text):
        self.label.setText(text)

    def okay_clicked(self):
        global selected_location, selected_time_interval, download_time_interval, file_dir_list
        download_time_interval = []
        selected_location = []
        selected_time_interval = []
        selected_location.append(float(self.lineEdit.text()))
        selected_location.append(float(self.lineEdit_2.text()))
        start_datetime = self.dateTimeEdit.dateTime()
        end_datetime = self.dateTimeEdit_2.dateTime()
        string_start_date = start_datetime.toString("dd/MM/yy hh:mm:ss")
        string_end_date = end_datetime.toString("dd/MM/yy hh:mm:ss")
        selected_time_interval.append(string_start_date)
        selected_time_interval.append(string_end_date)
        time_zone_finder.get_utc_time_from_coordinates(selected_location)
        selected_time_zone = time_zone_finder.utc_time_zone
        offset_part = selected_time_zone.split(' ')
        offset_involved = ' '.join(offset_part[1:])
        utc_start_time = time_zone_finder.convert_to_utc_with_offset(selected_time_interval[0], offset_involved)
        utc_end_time = time_zone_finder.convert_to_utc_with_offset(selected_time_interval[-1], offset_involved)
        download_time_interval.append(utc_start_time)
        download_time_interval.append(utc_end_time)
        date_interval_list = self.create_date_list(utc_start_time,utc_end_time)
        for file_date in date_interval_list:
            hour_url = createURL.create_url(file_date)
            progressbardownload.set_url.append(hour_url)
            temp_file_name = hour_url.split('/')
            progressbardownload.file_names.append(temp_file_name[-1])
        progressbardownload.start_download()
        if progressbardownload.finished_flag == 1:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            profilegenerator.input_dir = sorted(progressbardownload.directories)
            profilegenerator.output_dir = current_directory
            profilegenerator.input_lat = float(selected_location[0])
            profilegenerator.input_lon = float(selected_location[-1])
            profilegenerator.input_date = string_start_date
            profilegenerator.input_wrf_time = str(start_datetime.time())
            profilegenerator.start_reading_gfs()
            dashboard.open_dialog()
        else:
            pass



    def browse_files(self):
        global browsed_files
        try:
            FileManagerDialog()
            print(browsed_files)
            download_time_interval = []
            selected_location = []
            selected_time_interval = []
            selected_location.append(float(self.lineEdit.text()))
            selected_location.append(float(self.lineEdit_2.text()))
            start_datetime = self.dateTimeEdit.dateTime()
            end_datetime = self.dateTimeEdit_2.dateTime()
            string_start_date = start_datetime.toString("dd/MM/yy hh:mm:ss")
            string_end_date = end_datetime.toString("dd/MM/yy hh:mm:ss")
            selected_time_interval.append(string_start_date)
            selected_time_interval.append(string_end_date)
            time_zone_finder.get_utc_time_from_coordinates(selected_location)
            selected_time_zone = time_zone_finder.utc_time_zone
            offset_part = selected_time_zone.split(' ')
            offset_involved = ' '.join(offset_part[1:])
            utc_start_time = time_zone_finder.convert_to_utc_with_offset(selected_time_interval[0], offset_involved)
            utc_end_time = time_zone_finder.convert_to_utc_with_offset(selected_time_interval[-1], offset_involved)
            download_time_interval.append(utc_start_time)
            download_time_interval.append(utc_end_time)
            current_directory = os.path.dirname(os.path.realpath(__file__))
            profilegenerator.input_dir = sorted(browsed_files)
            profilegenerator.output_dir = current_directory
            profilegenerator.input_lat = float(selected_location[0])
            profilegenerator.input_lon = float(selected_location[-1])
            profilegenerator.input_date = string_start_date
            profilegenerator.input_wrf_time = str(start_datetime.time())
            profilegenerator.start_reading_gfs()
            dashboard.open_dialog()
        except OSError:
            print('Browsing cancelled.')
            pass



    def create_date_list(self, start_date_str, end_date_str):
        date_format = "%d/%m/%y %H:%M:%S"

        # Convert start_date_str and end_date_str to datetime objects
        start_date = datetime.strptime(start_date_str, date_format)
        end_date = datetime.strptime(end_date_str, date_format)

        # Initialize an empty list to store the datetime objects as strings
        date_list = []

        # Iterate through the range of hours between start_date and end_date
        current_date = start_date
        while current_date <= end_date:
            # Convert the current datetime object to a string in the desired format
            date_str = current_date.strftime(date_format)
            # Append the formatted string to the list
            date_list.append(date_str)
            current_date += timedelta(hours=1)

        return date_list


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "METCM Generator"))
        self.label.setText(_translate("MainWindow", "Time Zone:"))
        self.label_2.setText(_translate("MainWindow", "Operation Start Time"))
        self.label_3.setText(_translate("MainWindow", "Operation End Time"))
        self.label_4.setText(_translate("MainWindow", "Latitude"))
        self.label_5.setText(_translate("MainWindow", "Longitude"))
        self.label_6.setText(_translate("MainWindow", "|Zone|"))
        self.label_7.setText(_translate("MainWindow", "|Band|"))
        self.label_8.setText(_translate("MainWindow", "|Easting|"))
        self.label_9.setText(_translate("MainWindow", "|Northing|"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    app.exec()
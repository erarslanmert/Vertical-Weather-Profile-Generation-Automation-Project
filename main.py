import os
import re
import socket
import threading
import mgrs
import utm
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QDateTimeEdit, QDialog, QFileDialog, QMessageBox
from PyQt6.QtGui import QDoubleValidator, QFont, QCloseEvent, QIcon
from PyQt6.QtCore import QDateTime, Qt, QLocale, QThread, pyqtSignal
import sys
import loading_page
import time_zone_finder, createURL, progressbardownload
from datetime import datetime, timedelta
import time
import profilegenerator
import dashboard


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)




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
input_validator_5 = False
latlon = ()
thread_flag_1 = 0
source_flag = 0


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
            time.sleep(0.01)

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
        MainWindow.resize(366, 430)
        MainWindow.setWindowIcon(QtGui.QIcon("Images/M.png"))
        MainWindow.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.source_button = QtWidgets.QPushButton("Source", parent=MainWindow)
        self.source_button.setGeometry(QtCore.QRect(60,380,60,20))

        self.source_name = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.source_name.setGeometry(QtCore.QRect(121, 380, 202, 20))
        self.source_name.setObjectName("source_name")
        self.source_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.source_name.setText('https://nomads.ncep.noaa.gov')
        self.source_name.setDisabled(True)

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

        self.spinBox.setRange(1,60)
        self.spinBox.setValue(30)
        self.comboBox_2.addItems(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X'])
        self.comboBox_2.setCurrentIndex(0)

        font_2 = QFont()
        font_2.setPointSize(8)

        self.spinBox.setFont(font_2)
        self.comboBox_2.setFont(font_2)
        self.lineEdit.setFont(font_2)
        self.lineEdit_2.setFont(font_2)
        self.lineEdit_3.setFont(font_2)
        self.lineEdit_4.setFont(font_2)
        self.lineEdit_5.setFont(font_2)

        self.lineEdit.setText('0')
        self.lineEdit_2.setText('0')



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
        self.browse_button = self.buttonBox.addButton("Browse...", QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)


        # Change the text of the "Ok" button to "Download"
        self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("Download")

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(35, 300, 301, 20))
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



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MET Message Generator"))
        self.label.setText(_translate("MainWindow", "Time Zone:"))
        self.label_2.setText(_translate("MainWindow", "Operation Start Time"))
        self.label_3.setText(_translate("MainWindow", "Operation End Time"))
        self.label_4.setText(_translate("MainWindow", "Latitude"))
        self.label_5.setText(_translate("MainWindow", "Longitude"))
        self.label_6.setText(_translate("MainWindow", "|Zone|"))
        self.label_7.setText(_translate("MainWindow", "|Band|"))
        self.label_8.setText(_translate("MainWindow", "|Easting|"))
        self.label_9.setText(_translate("MainWindow", "|Northing|"))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.okay_clicked)

        self.lineEdit.textChanged.connect(self.update_thread_texts)
        self.lineEdit_2.textChanged.connect(self.update_thread_texts)
        self.lineEdit.textChanged.connect(self.validate_latitude)
        self.lineEdit_2.textChanged.connect(self.validate_longitude)
        self.lineEdit_3.textChanged.connect(self.validate_mgrs)
        self.lineEdit_4.textChanged.connect(self.validate_utm)
        self.lineEdit_5.textChanged.connect(self.validate_utm)
        self.spinBox.textChanged.connect(self.validate_utm)
        self.comboBox_2.currentTextChanged.connect(self.validate_utm)
        self.lineEdit_4.textChanged.connect(self.update_thread_texts)
        self.lineEdit_5.textChanged.connect(self.update_thread_texts)
        self.spinBox.textChanged.connect(self.update_thread_texts)
        self.comboBox_2.currentTextChanged.connect(self.update_thread_texts)

        self.worker_thread = WorkerThread()
        self.worker_thread.text_changed.connect(self.update_label)
        self.worker_thread.start()

        self.t1 = threading.Thread(target=self.is_internet_available)
        self.t1.start()

        self.browse_button.clicked.connect(lambda: self.browse_files())
        self.comboBox.currentIndexChanged.connect(self.combo_changed)

        self.comboBox.setCurrentIndex(0)

        self.t2 = threading.Thread(target=self.check_inputs)
        self.t2.start()

        self.source_button.clicked.connect(self.soruce_change)

        def close_window():
            MainWindow.close()
            self.close_chain()

        self.buttonBox.rejected.connect(close_window)

    def soruce_change(self):
        global source_flag
        if source_flag == 0:
            self.source_name.setEnabled(True)
            source_flag = 1
            self.source_button.setText('Set')
            self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setDisabled(True)
        else:
            self.source_name.setDisabled(True)
            createURL.main_base = self.source_name.text()
            source_flag = 0
            self.source_button.setText('Source')
            self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)


    def closeEvent(self, event):
        global thread_flag_1
        thread_flag_1 = 1
        print('Closed')
        self.t1.join()
        self.t2.join()
        event.accept()

    def close_chain(self):
        global thread_flag_1
        thread_flag_1 = 1
        print('Closed')
        self.t1.join()
        self.t2.join()

    def check_inputs(self):
        while True:
            if thread_flag_1 == 1:
                break
            else:
                if input_validator_1 == 1 and input_validator_2 == 1:
                    self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                    self.browse_button.setEnabled(True)
                else:
                    self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setDisabled(True)
                    self.browse_button.setDisabled(True)

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
            self.label_4.setText('MGRS - 5 Digid Precision')
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
            self.lineEdit_2.show()
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

        self.update_thread_texts()

    def validate_mgrs(self):
        global input_validator_3, latlon
        text = self.lineEdit_3.text()
        # Regular expression to validate MGRS format
        mgrs_pattern = re.compile("^[0-9]{1,2}[C-X][A-Z]{2}[0-9]{5}[0-9]{5}$")
        if mgrs_pattern.match(text):
            self.lineEdit_3.setStyleSheet("color: black;")  # Valid input, set color to black
            input_validator_3 = 1
            latlon = self.mgrs_to_latlon(text)
            self.lineEdit.setText(f"{latlon[0]:.6f}")
            self.lineEdit_2.setText(f"{latlon[-1]:.6f}")
            print(self.lineEdit.text())
            print(self.lineEdit_2.text())
        else:
            self.lineEdit_3.setStyleSheet("color: red;")  # Invalid input, set color to red
            input_validator_3 = 0
        self.update_thread_texts()

    def validate_utm(self):
        global input_validator_4, input_validator_5, latlon
        # Regular expression to validate UTM format
        zone = self.spinBox.value()
        band = self.comboBox_2.currentText()
        easting = 0
        northing = 0
        try:
            easting = int(self.lineEdit_4.text())
            northing = int(self.lineEdit_5.text())
            utm_pattern = re.compile(r"^\d{6,10}$")
        except ValueError:
            pass

        try:
            if utm_pattern.match(str(easting)) and utm_pattern.match(str(northing)):
                self.lineEdit_4.setStyleSheet("color: black;")
                self.lineEdit_5.setStyleSheet("color: black;")
                input_validator_4 = 1
                input_validator_5 = 1
                latlon = self.utm_to_latlon(zone, band, easting, northing)
                if latlon is not None:  # Check if latlong is not None
                    self.lineEdit.setText(f"{latlon[0]:.6f}")
                    self.lineEdit_2.setText(f"{latlon[-1]:.6f}")
                    print(self.lineEdit.text())
                    print(self.lineEdit_2.text())
                else:
                    print("Failed to convert UTM to latlon")
            else:
                self.lineEdit_4.setStyleSheet("color: red;")
                self.lineEdit_5.setStyleSheet("color: red;")
                input_validator_4 = 0
                input_validator_5 = 0
        except:
            pass
        self.update_thread_texts()

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

    def mgrs_to_latlon(self, mgrs_coord):
        try:
            m = mgrs.MGRS()
            d = m.toLatLon(mgrs_coord)
            # Convert MGRS coordinate string to latitude and longitude
            return d
        except:
            pass

    def utm_to_latlon(self, zone, band, easting, northing):
        try:
            latitude, longitude = utm.to_latlon(easting, northing, zone, band)
            return latitude, longitude
        except:
            pass

    def is_internet_available(self):
        while True:
            if thread_flag_1 == 1:
                break

            else:
                try:
                    # Attempt to connect to a well-known website
                    socket.create_connection(("www.google.com", 80))
                    self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                    print('<Online>')

                except OSError:
                    self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setDisabled(True)
                    print('<Offline>')
                time.sleep(10)

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
        date_interval_list = self.create_date_list(utc_start_time, utc_end_time)
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
            loading_page.open_loading()
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
            loading_page.open_loading()


        except OSError:
            print('Browsing cancelled.')
            pass
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(
                "The coordinates don't match with requirements of the dataset in order to perform a successful interpolation.")
            msg.setWindowTitle("Warning")
            msg.setWindowIcon(QIcon("Images/warning.png"))
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)

            # To display the message box
            print('Invalid Coordinates')
            msg.exec()
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.setStyle(QtWidgets.QStyleFactory.create("WindowsVista"))
    MainWindow.show()
    app.exec()
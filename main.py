from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import QDateTime, Qt, QLocale
import sys
import time_zone_finder, createURL, progressbardownload
from datetime import datetime, timedelta
import threading
import time

selected_time_zone = ''
selected_time_interval = []
selected_location = []
download_time_interval = []


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(366, 367)
        MainWindow.setWindowIcon(QtGui.QIcon("Images\M.png"))

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
        self.label_4.setGeometry(QtCore.QRect(140, 140, 71, 16))
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")

        self.label_5 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(140, 200, 71, 16))
        self.label_5.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_5.setObjectName("label_5")

        self.dateTimeEdit = QtWidgets.QDateTimeEdit(parent=self.centralwidget)
        self.dateTimeEdit.setGeometry(QtCore.QRect(80, 40, 211, 21))
        self.dateTimeEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        self.dateTimeEdit_2 = QtWidgets.QDateTimeEdit(parent=self.centralwidget)
        self.dateTimeEdit_2.setGeometry(QtCore.QRect(80, 100, 211, 21))
        self.dateTimeEdit_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.dateTimeEdit_2.setObjectName("dateTimeEdit_2")
        self.dateTimeEdit_2.setDateTime(QDateTime.currentDateTime())

        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(80, 160, 211, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(80, 220, 211, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

       # Create a QDoubleValidator to restrict input to numbers and a decimal point
        double_validator = QDoubleValidator()
        double_validator.setNotation(QDoubleValidator.Notation.StandardNotation)  # Set standard notation
        double_validator.setDecimals(10)  # Set the number of decimal places allowed
        double_validator.setLocale(QLocale('en_US'))

        # Set the validator for the QLineEdit
        self.lineEdit.setValidator(double_validator)
        self.lineEdit_2.setValidator(double_validator)

        self.buttonBox = QtWidgets.QDialogButtonBox(parent=self.centralwidget)
        self.buttonBox.setGeometry(QtCore.QRect(100, 300, 156, 23))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(60, 260, 250, 20))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.buttonBox.accepted.connect(self.okay_clicked)
        self.buttonBox.rejected.connect(MainWindow.close)

        self.lineEdit.setText('51.987327')
        self.lineEdit_2.setText('5.933481')

        self.lineEdit.textChanged.connect(self.update_utc_location)
        self.lineEdit_2.textChanged.connect(self.update_utc_location)
        
        self.thread = threading.Thread(target = self.update_utc_location)
        self.thread.start()

    def update_utc_location(self):
        global selected_location, selected_time_interval, download_time_interval
        try:
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
            self.label.setText(f"Selected Zone: {selected_time_zone}")
        except ValueError:
            self.label.setText(f"Selected Zone: None")
        time.sleep(0.1)
    
    def okay_clicked(self):
        global selected_location, selected_time_interval, download_time_interval
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
        print(selected_time_zone)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
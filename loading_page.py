import sys
import threading
import time

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QObject, pyqtSignal

import dashboard
import profilegenerator


class StreamRedirect(QObject):
    messageWritten = pyqtSignal(str)

    def write(self, text):
        self.messageWritten.emit(str(text))

class Ui_Dialog(object):

    def __init__(self):
        self.dialog = None
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(829, 593)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/M.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setToolTipDuration(0)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 30, 51, 51))
        self.label.setScaledContents(True)
        self.movie = QtGui.QMovie("Images/loading.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(100, 30, 131, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(40, 90, 751, 421))
        self.textEdit.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setReadOnly(True)
        self.pushButton = QtWidgets.QPushButton(Dialog, clicked = lambda: Dialog.close())
        self.pushButton.setGeometry(QtCore.QRect(674, 533, 91, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setDisabled(True)

        self.stdout_redirect = StreamRedirect()
        self.stderr_redirect = StreamRedirect()

        sys.stdout = self.stdout_redirect
        sys.stderr = self.stderr_redirect

        self.stdout_redirect.messageWritten.connect(self.append_text)
        self.stderr_redirect.messageWritten.connect(self.append_text)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.t3 = threading.Thread(target=profilegenerator.start_reading_gfs)
        self.t3.start()


    def append_text(self, text):
        self.textEdit.append(text.strip())
        if "<II> Done" in text:
            # Close the dialog
            self.pushButton.setEnabled(True)
            print('Please check dashboard interface to generate MET messages!')
            self.movie.stop()
            self.label.hide()
            self.label_2.setText('Ready!')
            dashboard.open_dialog()


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Preparing Data Set"))
        self.label_2.setText(_translate("Dialog", "Loading..."))
        self.pushButton.setText(_translate("Dialog", "Close"))


def open_loading():
    Dialog = QtWidgets.QDialog()
    Dialog.setStyle(QtWidgets.QStyleFactory.create("Windows Vista"))
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    Dialog.exec()














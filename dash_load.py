import sys
import threading
import time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QObject, pyqtSignal, Qt
import profilegenerator
import dashboard


class Ui_Dialog(object):

    def __init__(self):
        self.dialog = None
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(200, 200)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/M.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setToolTipDuration(0)
        Dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        Dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        Dialog.setWindowOpacity(0.8)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(0, 0, 200, 200))
        self.label.setScaledContents(True)
        self.movie = QtGui.QMovie("Images/loading.gif")
        self.label.setMovie(self.movie)
        self.movie.start()
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.t3 = threading.Thread(target=profilegenerator.start_reading_gfs)
        self.t3.start()





    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Preparing Data Set"))


def open_dashload():
    Dialog = QtWidgets.QDialog()
    Dialog.setStyle(QtWidgets.QStyleFactory.create("Windows Vista"))
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    Dialog.exec()

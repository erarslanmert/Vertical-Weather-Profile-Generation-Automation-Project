# Form implementation generated from reading ui file 'dashboard.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget, QTableWidget, QFrame, QPushButton, \
    QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec



df: ''


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setGeometry(0, 0, 1200, 900)
        Dialog.setWindowIcon(QtGui.QIcon("Images/M.png"))
        Dialog.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, True)
        Dialog.setWindowFlag(QtCore.Qt.WindowType.WindowMinimizeButtonHint, True)
        # Layout for the main window
        main_layout = QVBoxLayout(Dialog)
        button_layout = QHBoxLayout()
        # Create a stacked widget to switch between table and graph
        self.stacked_widget = QStackedWidget()

        # Table Widget Page
        self.table_page = QWidget()
        table_layout = QVBoxLayout(self.table_page)
        self.tableWidget = QTableWidget(parent=self.table_page)
        table_layout.addWidget(self.tableWidget)
        self.stacked_widget.addWidget(self.table_page)

        # Graph Page
        self.graph_page = QWidget()
        graph_layout = QVBoxLayout(self.graph_page)
        self.frame = QFrame(parent=self.graph_page)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        graph_layout.addWidget(self.frame)
        self.stacked_widget.addWidget(self.graph_page)

        # Button Box
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok)


        # Add navigation buttons
        self.prev_button = QPushButton("<", parent=Dialog)
        self.next_button = QPushButton(">", parent=Dialog)
        self.prev_button.setFixedSize(100, 20)
        self.next_button.setFixedSize(100, 20)

        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        # Set up table widget
        self.setup_table(df)

        # Set up graph
        self.setup_graph(df)

        # Connect page change signals to slots
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

    def prev_page(self):
        current_index = self.stacked_widget.currentIndex()
        new_index = (current_index - 1) % self.stacked_widget.count()
        self.stacked_widget.setCurrentIndex(new_index)
        self.stacked_widget.repaint()

    def next_page(self):
        current_index = self.stacked_widget.currentIndex()
        new_index = (current_index + 1) % self.stacked_widget.count()
        self.stacked_widget.setCurrentIndex(new_index)
        self.stacked_widget.repaint()

    def setup_table(self, df):
        # Set the number of rows and columns in the QTableWidget
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])

        # Set the headers
        self.tableWidget.setHorizontalHeaderLabels(df.columns)

        # Iterate over the DataFrame and set the data in the QTableWidget
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QtWidgets.QTableWidgetItem(str(df.iloc[i, j]))
                self.tableWidget.setItem(i, j, item)

    def setup_graph(self, df):
        # Create a Matplotlib figure and canvas
        self.figure = Figure(figsize=(12, 8), dpi=100)  # Larger figure size for better visibility
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.frame)
        layout.addWidget(self.canvas)

        # Plot the graph
        self.plot(df)

    def plot(self, df):
        # Filter columns to plot (excluding specified columns)
        columns_to_plot = [col for col in df.columns if col not in ['HeightMSL', 'Lat', 'Lon', 'Elapsed time']]

        num_plots = len(columns_to_plot)
        gs = gridspec.GridSpec(2, 4)  # Define a 2x4 grid for 2 horizontal and 4 vertical plots

        for i, column in enumerate(columns_to_plot):
            row = i // 4  # Determine row index
            col = i % 4   # Determine column index
            ax = self.figure.add_subplot(gs[row, col])  # Specify the grid location for each subplot
            ax.plot(df[column], df['HeightMSL'], label=column)
            ax.set_xlabel(column)
            ax.set_ylabel('HeightMSL')
            ax.set_title(f"{column} vs. HeightMSL")  # Add title to each subplot
            ax.legend(loc='upper right')  # Place legend at upper right corner

        gs.tight_layout(self.figure, h_pad=2.0, w_pad=2.0)
        self.figure.subplots_adjust(hspace=0.5, wspace=0.3)# Adjust layout with equal padding
        self.canvas.draw()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Vertical Weather Profile"))

def open_dialog():
    Dialog = QtWidgets.QDialog()
    Dialog.setStyle(QtWidgets.QStyleFactory.create("Windows Vista"))
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    Dialog.exec()

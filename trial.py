import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QFrame
from PyQt6.QtGui import QIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Matplotlib Graph")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("Images/M.png"))

        layout = QVBoxLayout(self)

        # Create a Matplotlib figure and canvas
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Load sample data (replace this with your DataFrame)
        self.df = pd.DataFrame({
            'HeightMSL': [10, 20, 30, 40, 50],
            'Column1': [5, 10, 15, 20, 25],
            'Column2': [15, 25, 20, 30, 35],
            'Column3': [10, 15, 25, 30, 20]
        })

        # Plot the graph
        self.plot()

    def plot(self):
        ax = self.figure.add_subplot(111)
        x = self.df.index  # Using DataFrame index as x-axis
        for column in self.df.columns:
            if column != 'HeightMSL':
                ax.plot(x, self.df[column], label=column)  # Plot each column with a different color
        ax.set_xlabel('Index')
        ax.set_ylabel('HeightMSL')
        ax.legend()  # Show legend
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
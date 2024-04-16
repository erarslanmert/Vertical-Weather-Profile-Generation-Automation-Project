import time
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QTimer


class CustomDialog(QWidget):
    def __init__(self):
        super().__init__()

        # Load image
        self.image_path = "Images/bubble_1.png"
        self.image = QPixmap(self.image_path)

        # Create QLabel for image
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.image)
        self.image_label.setScaledContents(True)

        # Set dialog attributes
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set mask to the image's alpha channel
        self.setMask(self.image.createMaskFromColor(QColor("transparent")))

        # Set initial opacity to 0
        self.opacity = 0
        self.setWindowOpacity(self.opacity)

        # Timer for gradually increasing opacity
        self.fade_in_timer = QTimer(self)
        self.fade_in_timer.timeout.connect(self.fadeIn)

        # Timer for fading out
        self.fade_out_timer = QTimer(self)
        self.fade_out_timer.timeout.connect(self.fadeOut)

        # Show the dialog and start the fade in timer
        self.show()
        self.fade_in_timer.start(50)  # Change the interval as needed

        self.text_label = QLabel("Hello, World!", self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setFixedSize(50, 50)

        # Create layout and add image label and close button
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.text_label.raise_()

        self.setGeometry(100, 100, self.image.width(), self.image.height())

    def fadeIn(self):
        # Increase opacity gradually
        self.opacity += 0.025  # Adjust the step as needed
        self.setWindowOpacity(self.opacity)
        if self.opacity >= 1:
            self.fade_in_timer.stop()
            self.fade_out_timer.start(50)
            time.sleep(3)# Start the fade out timer after 5 seconds (5000 ms)

    def fadeOut(self):
        # Decrease opacity gradually
        self.opacity -= 0.025  # Adjust the step as needed
        self.setWindowOpacity(self.opacity)
        if self.opacity <= 0:
            self.fade_out_timer.stop()
            self.close()


def notify_user():
    dialog = CustomDialog()
    dialog.show()





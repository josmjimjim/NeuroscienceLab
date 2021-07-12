from PyQt5.QtWidgets import QMdiSubWindow, QLabel, QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize


class MdiSubwindowPlot(QMdiSubWindow):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image
        self.setBaseSize(QSize(660,563))
        self.initializeUI()

    def initializeUI(self):
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        try:
            plot_image = QLabel()
            pixmap = QPixmap(self.image)
            pixmap = pixmap.scaled(620, 523, Qt.KeepAspectRatio)
            plot_image.setPixmap(pixmap)

        except Exception:
            plot_image = QLabel(self, 'Image not found')
            plot_image.setFont(QFont('Helvetica', 26))

        layout.addWidget(plot_image)
        widget.setLayout(layout)

        # Set Widget on subWindow
        self.setWidget(widget)


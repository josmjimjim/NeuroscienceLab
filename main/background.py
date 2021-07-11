import sys, os
from PyQt5.QtWidgets import QApplication, QMdiArea
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSlot


class Background (QMdiArea):
    def __init__(self, parent=None):
        # Initialize QMdiArea and set up parent: MainWindow
        super().__init__(parent)
        self.tileSubWindows()
    # Define paintEvent to display background image
    @pyqtSlot()
    def paintEvent(self, event):
        # Paint event is a method from QMdiArea
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        file = os.getcwd()
        pixmap, control = self.loadImage(file + '/main/assets/neuroscience.png')
        if control:
            painter.drawPixmap(self.rect(), pixmap)
        else:
            painter.setPen(QColor(168, 34, 3))
            painter.setFont(QFont('Helvetica', 26))
            painter.drawText(self.rect(), Qt.AlignCenter, pixmap)

    @staticmethod
    def loadImage(path2Image):
        # Static Method to load background image
        # and return it and control variable
        try:
            with open(path2Image):
                pixmap = QPixmap(path2Image)
                control = True
        except FileNotFoundError:
            pixmap = 'Error image not found !'
            control = False
        return pixmap, control


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Background()
    sys.exit(app.exec_())
import sys, os
from PyQt5.QtWidgets import (QApplication, QWidget, QListWidget,
    QVBoxLayout, QListWidgetItem, QGridLayout, QGroupBox, QLineEdit, QLabel,
    QPushButton, QMessageBox, QFileDialog, QCheckBox)
from PyQt5.QtCore import QSize, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor
from singleton import Singleton
from stylesheet import ddstyle, abstyle


class DisplayFileFinder(QWidget):
    __slots__ = ['dragcsv', 'dragmp4', 'file', 'url_link',]

    accept_signal = pyqtSignal(str, bool)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setGeometry(340, 100, 720, 600)
        self.setFixedSize(QSize(720,600))
        #Create url signal
        self.url_link = True
        # Create instances of object to call in initializeUI
        self.dragcsv = DragandDropFiles('.csv', self)
        self.dragmp4 = DragandDropFiles(['.mp4', '.avi'], self)
        self.file = FileDirectorySystem(self)
        # Conect the signal and slot
        self.dragcsv.file_directory.connect(self.file.recibecsvData)
        self.dragmp4.file_directory.connect(self.file.recibemp4Data)
        self.file.file_directory.connect(self.dragcsv.updateIcon)
        self.file.file_directory.connect(self.dragmp4.updateIcon)
        #Initialize and display window
        self.initializeUI()

    def initializeUI(self):
        # Create vertical main layout
        v_box = QVBoxLayout()

        # Create buttons
        self.accept = QPushButton('&Accept', self)
        self.accept.setStyleSheet(abstyle)
        self.accept.clicked.connect(self.buttonAccept)

        self.cancel = QPushButton('&Cancel', self)
        self.cancel.clicked.connect(self.buttonCancel)

        # Create group for the file directory drop
        group_csv = QGroupBox("Drop the .csv here", self)
        group_mp4 = QGroupBox("Drop the multimedia here", self)

        layout_csvbox = QVBoxLayout(group_csv)
        layout_mp4box = QVBoxLayout(group_mp4)

        layout_csvbox.addWidget(self.dragcsv)
        layout_mp4box.addWidget(self.dragmp4)

        group_csv.setLayout(layout_csvbox)
        group_mp4.setLayout(layout_mp4box)

        # Create grid layout for drag and drop
        grid_box = QGridLayout()
        grid_box.addWidget(group_csv, 0, 0)
        grid_box.addWidget(group_mp4, 0, 1)
        grid_box.addWidget(self.cancel, 1, 0)
        grid_box.addWidget(self.accept, 1, 1)

        # Create trigger check box
        check_button = QCheckBox('Does the file have tigger signal?', self)
        check_button.toggle()
        check_button.stateChanged.connect(self.recognizeState)

        # Define main Layout
        v_box.addWidget(self.file)
        v_box.addWidget(check_button)
        v_box.addLayout(grid_box)

        self.setLayout(v_box)

    def buttonAccept (self):
        if self.file.file_csv.text():
            url = self.file.file_mp4.text()
            self.close()  # close windows class and del
            self.accept_signal.emit(self.file.file_csv.text(), self.url_link)
            if url:
                Singleton().loadUrl(url)
        else:
            QMessageBox().warning(self, "", "Error, file path is empty!",
                                          QMessageBox.Ok, QMessageBox.Ok)

    def buttonCancel (self):
        self.close()  # close windows class and del

    def recognizeState(self, state):
        if state == Qt.Checked:
            self.url_link = True
        else:
            self.url_link = False

class DragandDropFiles(QListWidget):
    __slots__ = ['file_path', 'extension', 'painter',]

    file_directory = pyqtSignal(str)

    def __init__(self, extension, parent = None):
        super().__init__(parent)
        self.file_path = None
        self.extension = extension
        self.setAcceptDrops(True)
        self.setStyleSheet(ddstyle)
        self.setViewMode(QListWidget.IconMode)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        if data.hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        if data.hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        # Check if data has urls and it is local url
        if data.hasUrls and data.urls() and data.urls()[0].isLocalFile():
            url = data.urls()[0].toLocalFile()
            # Check if it is the correct extension and display icon
            if os.path.splitext(url)[1].lower() in self.extension:
                event.setDropAction(Qt.CopyAction)
                event.accept()
                self.file_path = url
                self.clear()
                self.displayIcons()
                # Emit signal to display url text in file directory system
                self.file_directory.emit(url)
            else:
                QMessageBox().warning(self, "",
                    "Error, the file extension is not valid",
                            QMessageBox.Ok, QMessageBox.Ok)
                event.ignore()
        else:
            event.ignore()

    def displayIcons(self):
        # Set icon size and description text
        self.setIconSize(QSize(50, 50))
        icon = QListWidgetItem()
        icon.setText(self.file_path.split("/")[-1])
        file = os.getcwd()
        # Check file extension
        if '.csv' in self.extension:
            icon.setIcon(QIcon(file + '/main/assets/csv_icon.svg'))
            self.addItem(icon)
        else:
            icon.setIcon(QIcon(file + '/main/assets/video_icon.png'))
            self.addItem(icon)

    @pyqtSlot()
    def paintEvent(self, event):
        # Paint event to set up background help text
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setPen(QColor(171, 178, 185))
        painter.setFont(QFont('Helvetica', 14))
        # Check file extension
        if type(self.extension) == list:
            file_extension = 'multimedia'
        else:
            file_extension = '.csv'
        painter.drawText(self.rect(), Qt.AlignCenter,'Please drop '+
                             file_extension+' here!')

    @pyqtSlot(str)
    def updateIcon(self, url):
        if os.path.splitext(url)[1].lower() in self.extension:
            self.file_path = url
            self.displayIcons()
        else:
            pass

class FileDirectorySystem(QWidget):
    __slots__ = ['file_csv', 'file_mp4', 'directory', ]

    file_directory = pyqtSignal(str)

    def __init__(self,  parent = None):
        super().__init__(parent)
        self.displayFileBox()

    def displayFileBox(self):
        # Create group to the file directory
        group_csv = QGroupBox('CSV File directory')
        group_mp4 = QGroupBox('Multimedia File directory')

         # Create label to the file directory
        label_csv = QLabel("Please enter the .csv location", self)
        label_mp4 = QLabel("Please enter the multimedia location", self)

        # Create the text box to append file path and button directory
        self.file_csv = QLineEdit(self)
        self.file_mp4 = QLineEdit(self)

        # Create push button to open directory finder
        dir_csvbutton = QPushButton('...')
        dir_csvbutton.setToolTip("Select csv file directory.")
        dir_csvbutton.clicked.connect(self.setDirectory)

        dir_mp4button = QPushButton('...')
        dir_mp4button.setToolTip("Select multimedia file directory.")
        dir_mp4button.clicked.connect(self.setDirectory)

        # Create layout for group
        layout_csvbox = QVBoxLayout()
        layout_mp4box = QVBoxLayout()

        # Organize widget in grid layout
        gridcsv = QGridLayout()
        gridcsv.addWidget(self.file_csv, 0, 0)
        gridcsv.addWidget(dir_csvbutton, 0, 1)

        gridmp4 = QGridLayout()
        gridmp4.addWidget(self.file_mp4, 0, 0)
        gridmp4.addWidget(dir_mp4button, 0, 1)

        # Add grid layout  and label to group layout
        layout_csvbox.addLayout(gridcsv)
        layout_csvbox.addStretch()
        layout_csvbox.addWidget(label_csv)

        layout_mp4box.addLayout(gridmp4)
        layout_mp4box.addStretch()
        layout_mp4box.addWidget(label_mp4)

        # Set layouts to groups
        group_csv.setLayout(layout_csvbox)
        group_mp4.setLayout(layout_mp4box)

        # Widget Layout
        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(group_csv)
        optionsLayout.addWidget(group_mp4)
        self.setLayout(optionsLayout)

    @pyqtSlot(str)
    def recibecsvData(self, data):
        # Slot for recibing data from drag and drop
        self.file_csv.setText(data)

    @pyqtSlot(str)
    def recibemp4Data(self, data):
        # Slot for recibing data from drag and drop
        self.file_mp4.setText(data)

    def setDirectory(self):
        # Display file dialog
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        # Display directory in open mode
        self.directory, _ = file_dialog.getOpenFileName(self, 'Open File', '~',
                                                        "All Files (*);;")

        # Check file extension
        if self.directory:
            if os.path.splitext(self.directory)[1].lower() == '.csv':
                self.file_csv.setText(self.directory)
                self.file_directory.emit(self.directory)
            elif os.path.splitext(self.directory)[1].lower() in ['.mp4','.avi']:
                self.file_mp4.setText(self.directory)
                self.file_directory.emit(self.directory)
            else:
                QMessageBox().warning(self, "",
                        "Error, the file cannot be open because its extension is not valid",
                        QMessageBox.Ok, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DisplayFileFinder()
    window.show()
    sys.exit(app.exec_())
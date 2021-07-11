import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QRadioButton, QButtonGroup, QGroupBox, QMessageBox,
                             QCheckBox, QLabel, QSpinBox, QGridLayout, QLineEdit, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from singleton import Singleton
from stylesheet import abstyle

class PlotKindsOptions(QWidget):
    __slots__ = ['names', 'options', 'options_list', 'url_link',
                 'time', 'interval', 'file', 'directory']

    accept_signal = pyqtSignal(list, bool, int, str)

    def __init__(self, trigger, parent = None):
        super().__init__(parent)
        self.url_link = False
        self.directory = None
        self.interval = 0
        if trigger:
            self.names = ('Lineal Plot Time', 'Pie',
                      'Box Plot', 'Histogram', 'Gaussian Histogram',
                      'Bar Plot', 'Horizontal Bar Plot', 'Violin')
        else:
            self.names = ('Lineal Plot Time', 'Pie',
                          'Bar Plot', 'Horizontal Bar Plot')
        self.displayOptions()
        optionsLayout = QVBoxLayout()
        optionsLayout.addWidget(self.options)
        self.setGeometry(340, 200, 560, 420)
        self.setLayout(optionsLayout)
        self.setStyleSheet(abstyle)
        self.show()

    def displayOptions(self):
        self.options = QGroupBox('Please, select plot types to display',self)
        self.options_list = QButtonGroup(self)
        layout_box = QVBoxLayout(self)

        # Define check option for time int plot
        self.file = QLineEdit(self)
        dir_button = QPushButton('...')
        dir_button.setToolTip("Select directory to save.")
        dir_button.clicked.connect(self.setDirectory)
        layout_dirbox = QVBoxLayout()

        layout_box.addLayout(layout_dirbox)

        grid = QGridLayout()
        grid.addWidget(self.file, 0, 0)
        grid.addWidget(dir_button, 0, 1)
        layout_dirbox.addLayout(grid)

        for opt in self.names:
            nms = QRadioButton(opt)
            layout_box.addWidget(nms)
            self.options_list.addButton(nms)

        # Define check option for time int plot
        label = QLabel('Insert time interval to plot', self)
        self.time = QSpinBox()
        self.time.setRange(0,100)
        grid_time = QGridLayout()
        grid_time.addWidget(label,0,0)
        grid_time.addWidget(self.time,0,1)
        layout_box.addLayout(grid_time)
        self.time.valueChanged.connect(self.recognizeState2)

        # Define check option for video display
        if Singleton().hasUrl():
            check_button = QCheckBox('Do you want to display the video file?',self)
            layout_box.addStretch()
            layout_box.addWidget(check_button)
            check_button.stateChanged.connect(self.recognizeState)

        # Define accept button and add to layout
        accept_button = QPushButton('&Accept',self)
        accept_button.clicked.connect(self.buttonAccept)
        layout_box.addWidget(accept_button)

        # Define the user alert
        label_alert = QLabel("Please remain here until window closes,"
                             " after press accept button!!", self)
        layout_box.addWidget(label_alert)

        self.options_list.setExclusive(False)
        self.options.setLayout(layout_box)


    def buttonAccept(self):
        '''
        Close the window and show results.
        '''
        options_selected = [button.text() for i, button in enumerate(self.
                    options_list.buttons()) if button.isChecked()]
        self.directory = self.file.text()

        if options_selected and self.directory:

            self.accept_signal.emit(options_selected, self.url_link, self.interval, self.directory)
            self.close()  # close windows class

        else:
            QMessageBox().warning(self, "", "Error, options selections are empty!\n"
                                            "Please select one at least! or select path",
                                          QMessageBox.Ok, QMessageBox.Ok)

    def recognizeState(self, state):
        if state == Qt.Checked:
            self.url_link = True
        else:
            self.url_link = False

    def recognizeState2(self):
        self.interval = self.time.value()

    def setDirectory(self):
        """
        Choose the directory.
        """
        file_dialog = QFileDialog(self)
        #file_dialog.setFileMode(QFileDialog.Directory)
        self.directory = file_dialog.getExistingDirectory(self, "Select Directory")

        if self.directory:
            self.file.setText(self.directory)
        else:
            QMessageBox().warning(self, "",
                    "Error, please select a path folder",
                                      QMessageBox.Ok, QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PlotKindsOptions()
    sys.exit(app.exec_())
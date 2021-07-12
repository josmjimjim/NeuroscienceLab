import sys, os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QTableView, QVBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSignal
from singleton import Singleton
from stylesheet import abstyle

class BuildModel(QStandardItemModel):
    # Define slots for fast access and save memory
    __slots__ = ['file', 'df','emotions', 'trigger',]

    def __init__(self, file_path, emotions, trigger, parent = None):
        super().__init__(parent)
        self.file = file_path
        self.emotions = emotions
        self.trigger = trigger
        # Set initial row and column values
        self.setRowCount(0)
        self.setColumnCount(0)
        # Load data from csv and fix them
        self.loadCSVFile()

    def loadCSVFile(self):

        # Create DataFrame with time
        try:
            self.df = pd.DataFrame(data={'time':
                self.file[self.emotions[1]].str.split(expand=True, pat="-")[0]}).astype(float).round(2)

            for col in self.emotions[1::1]:  # Nombre de las columnas
                self.df[col] = self.file[col].str.split(expand=True, pat="\d-")[1].astype(float).round(2)

            nrows, ncols = self.df.shape
            header = self.df.columns

            for col in range(len(self.emotions)):
                items = [QStandardItem(str(item)) for item in self.df[header[col]].tolist()]
                self.insertColumn(col, items)

            dfs = self.meanOperations(self.df, self.trigger)
            Singleton().loadData(self.df, dfs)

            self.setHorizontalHeaderLabels(header)

            del items, header

        except:
            QMessageBox().warning(self,"", "Error, an exception occurred!",
                                          QMessageBox.Ok, QMessageBox.Ok)

    @staticmethod
    def meanOperations(df, trigger):
        if trigger:
            dfs = pd.DataFrame(columns=df.columns)
            ind = df['trigger'][df['trigger'] > 0].index
            j = 0
            end = len(ind)
            for i in range(end - 1):
                list_ind = [*range(ind[i], ind[i + 1])]
                dfs = dfs.append(df.iloc[list_ind].mean(axis=0), ignore_index=True)
                dfs.at[j, 'time'] = j
                dfs.at[j, 'trigger'] = j
                j += 1
            dfs = dfs.drop('time', axis=1)
        else:
            dfs = df.mean(axis=0).drop(labels = ['time'])

        return dfs


class DisplayCSVData(QWidget):

    accept_signal = pyqtSignal(bool)

    __slots__ = ['file','model','trigger_sig']  # Define slots for fast access and save memory

    def __init__(self, file_path, trigger_sig, parent = None):
        super().__init__(parent)
        self.file = file_path
        self.trigger_sig = trigger_sig
        self.initializeUI()

    def initializeUI(self):
        """
        Initialize the window and display its contents to the screen.
        """
        self.setStyleSheet(abstyle)
        self.setGeometry(140, 100, 860, 484)
        self.setWindowTitle('Emotions Data View')
        self.setupModelView()

    def setupModelView(self):

        # Header tuple of csv file
        emotions = ('angry', 'disgust', 'fear', 'happy', 'sad',
                    'surprise', 'neutral', 'trigger')
        try:
            # Load csv file and delete the firs column if has Unnamed
            file_name = pd.read_csv(self.file, header=0)
            if file_name.shape[1] == 1: raise Exception
        except:
            # Load csv file and delete the firs column
            file_name = pd.read_csv(self.file, delimiter=';',header=0)

        header_csv = file_name.columns.to_list()
        index, col_head = [], []

        # Check if emotions are in header
        for j in emotions:
            index.extend([i for i in header_csv if j in i])
            col_head.extend([j for i in header_csv if j in i])
        index = [x for x in index if x]
        col_head = [x for x in col_head if x]

        # Check user trigger
        if 'trigger' in index[-1] and not self.trigger_sig:
            self.trigger_sig = True
            QMessageBox().warning(self, "", "Error, the file has trigger!",
                                  QMessageBox.Ok, QMessageBox.Ok)
        elif 'trigger' not in index[-1] and self.trigger_sig:
            self.trigger_sig = False
            QMessageBox().warning(self, "", "Error, the file does not have trigger!",
                                  QMessageBox.Ok, QMessageBox.Ok)

        # Call display function
        self.displayTable(file_name, col_head, index)

    def displayTable (self, file_name, col_head, index):
        file_name = file_name[index]
        file_name.columns = col_head
        file_name = file_name.dropna(axis = 0)
        # Set up standard item model and table view.
        table_view = QTableView()
        # From QAbstractItemView.ExtendedSelection = 3
        table_view.SelectionMode(3)
        self.model = BuildModel(file_name, col_head, self.trigger_sig, self)
        table_view.setModel(self.model)

        accept_button = QPushButton('&Accept',self)
        accept_button.clicked.connect(self.buttonAccept)

        v_box = QVBoxLayout()
        v_box.addWidget(table_view)
        v_box.addWidget(accept_button)
        self.setLayout(v_box)

    def buttonAccept(self):
        '''
        Close the csv window when button is clicked
        and open plot window.
        '''
        self.accept_signal.emit(self.trigger_sig)
        self.close()  # close windows class


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DisplayCSVData('assets/data copia.csv', False)
    window.show()
    sys.exit(app.exec_())
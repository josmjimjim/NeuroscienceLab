import sys, glob
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5.QtCore import pyqtSlot, QThreadPool, Qt
from background import Background
from filedirectory import DisplayFileFinder
from datawindow import DisplayCSVData
from plotoptions import PlotKindsOptions
from subwindowscreator import MdiSubwindowPlot
from videoplayer import MediaPlayer
from singleton import Singleton
from externalplotprocess import ExternalProcess
from multithreading import Worker

class MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        # Call main initialize method to display contents
        self.initializeUI()

    def initializeUI(self):
        # Initialize backgroud and set up it as child
        self.background = Background(self)
        # Set window title
        self.setWindowTitle('Neuroscience Lab')
        # Set background as central widget
        self.setCentralWidget(self.background)
        # Display menu bar and MainWindow with show method
        self.displayMenuBar()
        self.show()

    def displayMenuBar(self):
        # Create actions for file menu
        self.open_act = QAction("Open", self)
        self.open_act.setShortcut('Ctrl+O')
        self.open_act.setStatusTip('Open a new file')
        self.open_act.triggered.connect(self.openFile)

        self.exit_act = QAction('Exit', self)
        self.exit_act.setShortcut('Ctrl+Q')
        self.open_act.setStatusTip('Quit program')
        self.exit_act.triggered.connect(self.closeWindows)

        # Create menubar
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        # Create file menu and add actions
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(self.open_act)
        file_menu.addSeparator()
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

    def closeWindows(self):
        # Close the window when button is clicked
        self.close()

    def openFile(self):
        '''
        Open the window file directory when button is clicked
        '''
        self.directory = DisplayFileFinder()
        self.directory.accept_signal.connect(self.dataView)
        self.directory.show()

    @pyqtSlot(str, bool)
    def dataView(self, data, trigger):
        self.data_window = DisplayCSVData(data, trigger)
        self.data_window.show()
        self.data_window.accept_signal.connect(self.optionsView)

    @pyqtSlot(bool)
    def optionsView(self, trigger):
        self.trigger = trigger
        self.options_window = PlotKindsOptions(trigger)
        self.options_window.show()
        self.options_window.accept_signal.connect(self.resultsView)


    @pyqtSlot(list, bool, int, str)
    def resultsView(self, option_list, sig, interval, path):
        self.sig = sig
        self.threadpool = QThreadPool()
        obj, objs = Singleton().getData()
        vid_check = Singleton().hasUrl()
        obj.to_excel(path+"/emotion.xlsx")
        obj.to_csv(path + "/emotion.csv")
        objs.to_excel(path + "/emotion_mean.xlsx")
        self.work = ExternalProcess(option_list, interval, path, self.trigger, vid_check)
        self.work.path_sender.connect(self.subwindowAdd)
        self.work.show()
        worker = Worker(self.work.plot_function)
        worker.signals.finished.connect(self.work.process_finishedplot)
        worker.signals.progress.connect(self.work.progress_fcnplot)
        self.threadpool.start(worker)

    def subwindowAdd(self, path):
        self.subwindowClose()
        image_list = glob.glob(path+'/*.png')
        for i in image_list:
            obj = MdiSubwindowPlot(i,self.background)
            obj.setAttribute(Qt.WA_DeleteOnClose)
            self.background.addSubWindow(obj)
            obj.show()

        if self.sig:
            url = Singleton().getUrl()
            player_window = MediaPlayer(url, self)
            self.background.addSubWindow(player_window)
            player_window.show()

    def subwindowClose(self):
        self.background.closeAllSubWindows()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
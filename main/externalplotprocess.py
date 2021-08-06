import sys, os, glob
from PyQt5.QtCore import QProcess, pyqtSignal, QTimer, QProcessEnvironment
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPlainTextEdit, QProgressBar)
from plotresults import MdiSubwindowPlot, MdiSubwindowPlotSpecial
from singleton import Singleton
import re
from ctypes import cdll

class ExternalProcess(QWidget):

    path_sender = pyqtSignal(str)

    def __init__(self, kind , interval, path, trigger, video,parent = None):
        super().__init__(parent)
        # Define vairiable
        self.path =  path
        self.trigger = trigger
        self.option_list = kind
        self.interval = interval
        self.video = video
        # Check codec if window try and mac os, unix except
        try:
            self.codec = 'cp' + str(cdll.kernel32.GetACP())
        except:
            self.codec = 'utf-8'
        # Set up Qprocces and Qthreadpool
        self.p = None  # Default empty value.

        # Ceate text box to display progress
        self.textvideo = QPlainTextEdit()
        self.textvideo.setReadOnly(True)
        self.textplot = QPlainTextEdit()
        self.textplot.setReadOnly(True)

        #Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)

        # Create window layout
        l = QVBoxLayout()
        l.addWidget(QLabel('Plotting process',self))
        l.addWidget(self.textplot)
        l.addStretch()
        l.addWidget(QLabel('Video process', self))
        l.addWidget(self.progress)
        l.addWidget(self.textvideo)

        # Set layout
        self.setLayout(l)

        if self.video:
            self.start_processvideo()
        else:
            self.process_finishednotvideo()

    def plot_function(self, progress_callback):
        files = glob.glob(self.path + '/*.png')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))

        obj, objs  = Singleton().getData()

        if self.trigger:
            d = objs.shape[0]
        else:
            d = 1

        for i in self.option_list:
            if i == 'Pie' or i == 'Bar Plot' or i == 'Horizontal Bar Plot':
                for j in range(d):
                    if self.trigger:
                        a = objs.loc[j].to_frame()
                    else:
                        a = objs.to_frame()

                    a = a.T
                    MdiSubwindowPlotSpecial(a, i, j, self.path, self.trigger)
                    progress_callback.emit(i + ' plot: ' + str(j))
            else:
                MdiSubwindowPlot(obj,objs, i, self.interval,
                                                self.path, self.trigger)
                progress_callback.emit(i + ' plot ')


    def messageplot(self, s):
        self.textplot.appendPlainText(s)

    def messagevideo(self, s):
        self.textvideo.appendPlainText(s)

    def start_processvideo(self):
        url = Singleton().getUrl()
        if self.trigger:
            ctrl = '1'
        else:
            ctrl = '0'

        if self.p is None:  # No process running.
            self.messagevideo("Executing process")
            self.p = QProcess()
            env = QProcessEnvironment.systemEnvironment()
            new_env = self.read_env()
            env.insert("PYTHONPATH", new_env)
            self.p.setProcessEnvironment(env)
            self.p.setProcessChannelMode(QProcess.MergedChannels)
            #self.__add_openocd_to_env()
            self.p.finished.connect(self.process_finishedvideo)  # Clean up once complete.
            self.p.stateChanged.connect(self.handle_state)
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            file = os.getcwd()
            file = file + '/main/videoprocess.py'
            self.p.start("python", [file, url, self.path, ctrl])
    @staticmethod
    def read_env():
        dir_path = os.getcwd()
        try:
            with open(dir_path + '/main/assets/venv.txt', 'r') as f:
                venv_dir = f.read()
                f.close()
        except Exception:
            win = os.path.normpath('/main/assets/venv.txt')
            with open(dir_path + win, 'r') as f:
                venv_dir = f.read()
                f.close()
        return  venv_dir

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.messagevideo(f"State changed: {state_name}")

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode(self.codec)
        # Extract progress if it is in the data.
        self.messagevideo(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode(self.codec)
        progress = self.simple_percent_parser(stdout)
        if progress:
            self.progress.setValue(progress)
        self.messagevideo(stdout)

    def process_finishedvideo(self):
        self.messagevideo("Process finished.")
        self.p = None
        QTimer.singleShot(3000, self.close)

    def process_finishedplot(self):
        self.messageplot("Process finished.")
        self.path_sender.emit(self.path)
        if not self.video:
            QTimer.singleShot(3000, self.close)

    def progress_fcnplot(self, perc):
        self.messageplot(perc + " done.....")

    @staticmethod
    def simple_percent_parser(output):
        """
        Matches lines using the progress_re regex,
        returning a single integer for the % progress.
        """
        progress_re = re.compile("Total completed: (\d+)%")
        m = progress_re.search(output)
        if m:
            pc_complete = m.group(1)
            return int(pc_complete)

    def process_finishednotvideo(self):
        self.messagevideo("Process finished. \n Not video detected!! \n System exit()")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExternalProcess('pie' , 2, 'Desktop/', True, parent = None)
    window.show()
    sys.exit(app.exec_())

import sys, os
import matplotlib.pyplot
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
matplotlib.pyplot.switch_backend('Agg')
import seaborn as sns
sns.set_theme(style="darkgrid")

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4,
                 dpi=100, title=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set(title = title)
        super().__init__(fig)


class MdiSubwindowPlot:
    def __init__(self, data, data_mod, kind, interval, path, trigger):
        if trigger:
            self.df = data.drop('trigger', axis = 1)
            self.dfs = data_mod.drop('trigger', axis = 1)
        else:
            self.df = data
            self.dfs = data_mod.to_frame().T

        self.kind = kind
        self.path = os.path.join(path, kind + '.png')
        self.interval = interval
        self.trigger = trigger
        self.displayPlot()

    def displayPlot(self):
        self.graph =  MplCanvas(self, width=5, height=4, dpi=100,
                                title= self.kind)
        self.typePlot()

    def typePlot(self):

        data = self.df
        data_mod = self.dfs
        ax = self.graph.axes
        opts = self.kind

        if opts == 'Lineal Plot Time':
            try:
                end_point = data.shape[0] - 1
                t_end = data.at[end_point, 'time']
                if self.interval == 0: i = 1
                else: i = int(end_point*self.interval//t_end)
                if i >= end_point: i = end_point
                d = data[0:end_point:i]
                d = d.melt('time', var_name='cols', value_name='vals')
                fig = sns.lineplot(data=d, x='time', y="vals", hue='cols', ax=ax)
                ax.legend(loc = 'best')
                ax.set_xlabel('Time')
                ax.set_ylabel('Percentage')
                fig.figure.savefig(self.path, dpi=300, bbox_inches = 'tight')
                del d, end_point, i, t_end
            except Exception:
                raise Exception

        elif opts == 'Box Plot':
            try:
                fig = sns.boxplot(data=data_mod, ax=ax)
                fig.figure.savefig(self.path, dpi=300, bbox_inches = 'tight')
            except Exception:
                raise Exception

        elif opts == 'Histogram':
            try:
                fig = sns.histplot(data = data_mod, ax=ax)
                fig.figure.savefig(self.path, dpi=300, bbox_inches = 'tight')
            except Exception:
                raise Exception

        elif opts == 'Gaussian Histogram':
            try:
                fig = sns.histplot(data=data_mod, ax = ax, element="poly", multiple="stack")
                fig.figure.savefig(self.path, dpi=300, bbox_inches = 'tight')
            except Exception:
                raise Exception

        elif opts == 'Violin':
            try:
                sns.despine(left=True, bottom=True)
                fig = sns.violinplot(data=data_mod, inner="quart",
                           ax = ax, scale = 'width')
                fig.figure.savefig(self.path, dpi=300, bbox_inches = 'tight')
            except Exception:
                raise Exception


class MdiSubwindowPlotSpecial:
    def __init__(self, data_mod, kind, number, path, trigger):
        self.dfs = data_mod
        self.kind = kind
        self.number = number
        self.trigger = trigger
        self.path = os.path.join(path, kind + 'Trigger' + str(number)+'.png')
        self.displayPlot()

    def displayPlot(self):
        if self.trigger:
            self.graph = MplCanvas(self, width=5, height=4, dpi=100,
                               title= self.kind + ' Trigger: ' + str(self.number))
        else:
            self.graph = MplCanvas(self, width=5, height=4, dpi=100,
                               title=self.kind)
        self.typePlot()

    def typePlot(self):

        data_mod = self.dfs
        ax = self.graph.axes
        opts = self.kind
        if self.trigger:
            d = data_mod.drop('trigger', axis = 1)
        else:
            d = data_mod

        if opts == 'Pie':
            average = d.to_numpy() * 100
            average = np.round(average, 2)
            average = average.flatten()
            labels = d.columns.to_numpy()
            index = (average > 0)

            fig, texts, autotexts = ax.pie(average[index], autopct='%1.1f%%', startangle=90)
            ax.legend(fig, labels[index],
                      title="Emotions",
                      loc="upper left",
                      bbox_to_anchor=(-0.3,-0.2, 0, 1))

            ax.figure.savefig(self.path, dpi=300, bbox_inches = 'tight')
            del d

        elif opts == 'Bar Plot':
            fig = sns.barplot(data=d, ax=ax)
            ax.set_ylabel('Percentage')
            fig.figure.savefig(self.path, dpi=300, bbox_inches = 'tight')
            del d

        elif opts == 'Horizontal Bar Plot':
            fig = sns.barplot(data=d, ax=ax, orient='h')
            ax.set_xlabel('Percentage')
            fig.figure.savefig(self.path, dpi = 300, bbox_inches = 'tight')
            del d


if __name__ == '__main__':
    import pandas as pd
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df = pd.DataFrame(data=d)



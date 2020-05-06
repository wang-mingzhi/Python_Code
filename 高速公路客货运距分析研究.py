# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:29:46 2020
高速公路客货运距分析研究-以宁夏回族自治区为例
@author: 18120900
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
from scipy.interpolate import make_interp_spline
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from minepy import MINE


class SeabornFig2Grid:

    def __init__(self, seaborngrid, fig, subplot_spec):
        self.fig = fig
        self.sg = seaborngrid
        self.subplot = subplot_spec
        if isinstance(self.sg, sns.axisgrid.FacetGrid) or isinstance(self.sg, sns.axisgrid.PairGrid):
            self._movegrid()
        elif isinstance(self.sg, sns.axisgrid.JointGrid):
            self._movejointgrid()
        self._finalize()

    def _movegrid(self):
        """ Move PairGrid or Facetgrid """
        self._resize()
        n = self.sg.axes.shape[0]
        m = self.sg.axes.shape[1]
        self.subgrid = gridspec.GridSpecFromSubplotSpec(n, m, subplot_spec=self.subplot)
        for i in range(n):
            for j in range(m):
                self._moveaxes(self.sg.axes[i, j], self.subgrid[i, j])

    def _movejointgrid(self):
        """ Move Jointgrid """
        h = self.sg.ax_joint.get_position().height
        h2 = self.sg.ax_marg_x.get_position().height
        r = int(np.round(h / h2))
        self._resize()
        self.subgrid = gridspec.GridSpecFromSubplotSpec(r + 1, r + 1, subplot_spec=self.subplot)

        self._moveaxes(self.sg.ax_joint, self.subgrid[1:, :-1])
        self._moveaxes(self.sg.ax_marg_x, self.subgrid[0, :-1])
        self._moveaxes(self.sg.ax_marg_y, self.subgrid[1:, -1])

    def _moveaxes(self, ax, gs):
        # https://stackoverflow.com/a/46906599/4124317
        ax.remove()
        ax.figure = self.fig
        self.fig.axes.append(ax)
        self.fig.add_axes(ax)
        ax._subplotspec = gs
        ax.set_position(gs.get_position(self.fig))
        ax.set_subplotspec(gs)

    def _finalize(self):
        plt.close(self.sg.fig)
        self.fig.canvas.mpl_connect("resize_event", self._resize)
        self.fig.canvas.draw()

    def _resize(self, evt=None):
        self.sg.fig.set_size_inches(self.fig.get_size_inches())


def dealdata(data, groupby, index):
    d = data.groupby(groupby).sum().reset_index()
    d['avgmiles'] = d['totalmiles'] / d['count']
    pivot_data = d.pivot_table(values='avgmiles', index=index, columns=['veh'], aggfunc=np.mean).reset_index()
    return pivot_data


def drawyeartrendgram(data, lblname):
    f, axes = plt.subplots(3, 3, sharex='all', sharey='all', figsize=(5.5, 4))
    plt.subplots_adjust(0.07, 0.07, 0.98, 0.98, 0, 0)
    for i in range(len(lblname)):
        y = data.iloc[i, 2:]
        y = (y - y.min()) / (y.max() - y.min())
        axes[i // 3, i % 3].plot(data.columns[2:], y, '.-', label=lblname[i])
        axes[i // 3, i % 3].legend(prop=fontdict, loc='upper right')
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
    plt.legend(prop=fontdict, loc='upper right')


def drawhourtrendgram(pivot_data, lblname):
    plt.figure(figsize=(5, 2.5))
    plt.subplots_adjust(0.11, 0.18, 0.98, 0.98, 0.2, 0.32)
    x = pivot_data.iloc[:, 0]
    x_new = np.linspace(x.min(), x.max(), 300)
    for i in range(len(lblname)):
        y = pivot_data.iloc[:, i + 1]
        y_smooth = make_interp_spline(x, y)(x_new)
        plt.plot(x_new, y_smooth, linewidth=1, label=lblname[i])
    plt.xlabel('Hour', fontdict=fontdict)
    plt.ylabel('Miles', fontdict=fontdict)
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
    plt.legend(prop=fontdict, loc='upper right')


def hourlineplot(data, vehtype):
    if vehtype == 'car':
        data['veh'] = data['veh'].replace([1, 2, 3, 4], ['Car-I', 'Car-II', 'Car-III', 'Car-IV'])
    elif vehtype == 'truck':
        data['veh'] = data['veh'].replace([2, 3, 4, 5, 6], ['Axis-II', 'Axis-III', 'Axis-IV', 'Axis-V', 'Axis-VI'])
    data['avgmiles'] = data['totalmiles'] / data['count']
    plt.figure(figsize=(5, 2.5))
    plt.subplots_adjust(0.11, 0.18, 0.98, 0.98, 0.2, 0.32)
    sns.lineplot('time', 'avgmiles', hue='veh', palette="muted", data=data)
    plt.xlabel('Hour', fontdict=fontdict)
    plt.ylabel('Miles', fontdict=fontdict)
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
    plt.legend(prop=fontdict, loc='upper right')


def drawfig(pivot_data, lblname):
    f, axes = plt.subplots(2, 1, figsize=(5.5, 4))
    plt.subplots_adjust(0.125, 0.125, 0.98, 0.98, 0.2, 0.32)
    for i in range(len(lblname)):
        y = pivot_data.iloc[:, i + 1]
        sns.lineplot(pivot_data.iloc[:, 0], y, linewidth=1, ax=axes[0])
        sns.distplot(y, hist=False, kde_kws={"shade": True}, ax=axes[1], label=lblname[i])
    axes[0].set_xlabel('Date', fontdict=fontdict)
    axes[0].set_ylabel('Miles(km)', fontdict=fontdict)
    axes[1].set_xlabel('Miles(km)', fontdict=fontdict)
    axes[1].set_ylabel('Percentage(%)', fontdict=fontdict)
    # axes[0].legend(prop=fontdict)
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)
    plt.legend(prop=fontdict, loc='upper right')


def drawKDEfig(data, lblname):
    fig = plt.figure(figsize=(5.5, 4.5))
    gs = gridspec.GridSpec(2, 3, None, 0.08, 0.1, 0.98, 0.98, 0.2, 0.3)
    for i in range(len(lblname)):
        temp_data = data if i == 0 else data[data.veh == i + 1]
        x = temp_data.iloc[:, 1]
        y = temp_data.iloc[:, 2]
        axes = sns.jointplot(x, y, kind="kde", height=4, space=0)
        axes.set_axis_labels(lblname[i], '', fontdict=fontdict)
        SeabornFig2Grid(axes, fig, gs[i])
    plt.xticks(fontproperties='Times New Roman', size=10)
    plt.yticks(fontproperties='Times New Roman', size=10)


def calMIC(data):
    for i in range(5):
        mine = MINE(alpha=0.6, c=15)
        mine.compute_score(data[data.veh == (i + 2)].iloc[:, 1], data[data.veh == (i + 2)].iloc[:, 2])
        print("Without noise:", "MIC", mine.mic())


def correlationanalysis(data):
    f, axes = plt.subplots(2, len(data.columns)-1, sharex='all', sharey='all', figsize=(5.5, 4))
    plt.subplots_adjust(0.12, 0.07, 0.97, 0.97, 0, 0)
    for i in range(len(data.columns)-1):
        plot_acf(data.iloc[:, i + 1], ax=axes[0, i], title='')
        plot_pacf(data.iloc[:, i + 1], ax=axes[1, i], title='')
    axes[0, 0].set_ylabel('ACF', fontdict=fontdict)
    axes[1, 0].set_ylabel('PACF', fontdict=fontdict)


if __name__ == "__main__":
    # 中文字体设置-黑体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决保存图像是负号'-'显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False
    fontdict = {'family': 'Times New Roman', 'weight': 'normal', 'size': 10}
    label = ['Car-I', 'Car-II', 'Car-III', 'Car-IV']
    label.extend(['Axis-II', 'Axis-III', 'Axis-IV', 'Axis-V', 'Axis-VI'])
    datafilepath = r"F:\18120900\桌面\高速公路货运距分析研究-以宁夏自治区为例\Data.xlsx"
    sheet = pd.read_excel(datafilepath, [0, 1, 2, 3])

    # 画各个车型从2014到2018的变化趋势图
    drawyeartrendgram(sheet[0], label)
    # 画客车各个车型年度变化趋势图、平均运距直方图
    drawfig(dealdata(sheet[1], ['date', 'veh'], ['date']), label[:4])
    # 画客车各个车型小时变化趋势图
    drawhourtrendgram(dealdata(sheet[1], ['time', 'veh'], ['time']), label[:4])  # 平滑曲线
    hourlineplot(sheet[1], 'car')  # 含有置信区间
    # 画货车各个车型年度变化趋势图、平均运距直方图
    drawfig(dealdata(sheet[2], ['date', 'veh'], ['date']), label[4:])
    # 画货车各个车型小时变化趋势图
    drawhourtrendgram(dealdata(sheet[2], ['time', 'veh'], ['time']), label[4:])  # 平滑曲线
    hourlineplot(sheet[2], 'truck')  # 含有置信区间
    # 画货车平均运距与载重的kde图
    drawKDEfig(sheet[3], ['All Truck', 'Axis-II', 'Axis-III', 'Axis-IV', 'Axis-V', 'Axis-VI'])
    # 画里程和载重之间的关系图
    sns.set(style="ticks")
    sns.pairplot(sheet[3], hue="veh")
    # 计算车货总重和平均运距之间的互相关信息MIC
    calMIC(sheet[3])
    # 客车相关性分析
    correlationanalysis(dealdata(sheet[1], ['date', 'veh'], ['date']))
    # 货车相关性分析
    correlationanalysis(dealdata(sheet[2], ['date', 'veh'], ['date']))

    plt.show()

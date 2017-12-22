# -*- coding: utf8 -*-

import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationBar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns


# import warnings
# warnings.filterwarnings("ignore")


# ----------------------------
# class definition

class SystemGain(object):
    pass


class SystemGainDocker:
    def __init__(self, accresponce, launch, maxacc, pedalmap, shiftmap):
        self.accresponce = accresponce
        self.launch = launch
        self.maxacc = maxacc
        self.pedalmap = pedalmap
        self.shiftmap = shiftmap


class MyFigureCanvas(FigureCanvas):

    def __init__(self, parent=None, width=10, height=10, dpi=100, plot_type='3d', **kwargs):
        fig = Figure(figsize=(width, height), dpi=100)
        super(MyFigureCanvas, self).__init__(fig)
        self.kwargs = kwargs
        # FigureCanvas.__init__(self, fig)  # 初始化父类   堆栈溢出问题！
        # self.setParent(parent)
        if plot_type == '2d':
            self.axes = fig.add_subplot(111)
        elif plot_type == '3d':
            self.axes = fig.add_subplot(111, projection='3d')
        elif plot_type == '2d-poly':
            self.axes = fig.add_subplot(111, polar=True)

    def plot_acc_response_(self):
        self.xdata = self.kwargs['data'][1]
        self.ydata = self.kwargs['data'][0]
        self.zdata = self.kwargs['data'][2]
        self.pedal_avg = self.kwargs['pedal_avg']
        for i in range(0, len(self.xdata)):
            self.axes.plot(self.xdata[i], self.ydata[i], self.zdata[i], label=int(round(self.pedal_avg[i] / 5) * 5))
            self.axes.legend(bbox_to_anchor=(1.02, 1), loc=1, borderaxespad=0)
        self.axes.set_xlabel('Vehicle Speed (km/h)', fontsize=12)
        self.axes.set_ylabel('Pedal(%)', fontsize=12)
        self.axes.set_zlabel('Acc (g)', fontsize=12)
        self.axes.set_title('Acc-3D Map', fontsize=12)

    def plot_pedal_map_(self):
        self.xdata = self.kwargs['data'][1]
        self.ydata = self.kwargs['data'][2]
        self.zdata = self.kwargs['data'][0]
        self.axes.scatter(self.xdata, self.ydata, c=self.zdata, marker='o', linewidths=0.1,
                          s=6, cmap=cm.get_cmap('RdYlBu_r'))
        self.axes.grid(True, linestyle="--", color="k", linewidth="0.4")
        self.axes.set_xlabel('Engine Speed (rpm)', fontsize=12)
        self.axes.set_ylabel('Torque (Nm)', fontsize=12)
        self.axes.set_title('PedalMap', fontsize=12)

    def plot_en_work_map_(self):
        # self.data = self.kwargs['En_work_point_heatmap_data']
        self.seg_size = self.kwargs['seg_size']
        self.xlim = self.kwargs['xlim']
        self.ylim = self.kwargs['ylim']
        # # self.csv = self.kwargs['BSFC_map']
        # col = self.data.columns
        # resultarray = np.zeros(self.seg_size)
        # x_seg_size = self.xlim / self.seg_size[0]
        # y_seg_size = self.ylim / self.seg_size[1]
        # self.data[col[0]] = self.data[col[0]] / x_seg_size
        # self.data[col[1]] = self.data[col[1]] / y_seg_size
        #
        # csv = pd.read_csv('N330_BSFC.csv', index_col=0)
        # x = np.array([int(i) for i in csv.columns.tolist()]) / x_seg_size
        # y = csv.index / y_seg_size
        # X, Y = np.meshgrid(x, y)
        # # plt.contourf(X, Y, csv, 18, alpha=.75, cmap=None)

        cs = self.axes.contour(self.kwargs['X'], self.kwargs['Y'], self.kwargs['csv'],
                               [240, 250, 260, 270, 280, 290, 300, 350, 400, 500, 700], colors='black',
                               linewidth=.1)
        self.axes.clabel(cs, inline=True, fontsize=10)

        # for i in range(self.seg_size[0]):
        #     for j in range(self.seg_size[1]):
        #         resultarray[i, j] = self.data[(self.data[col[0]] > i) & (self.data[col[0]] <= (i + 1)) &
        #                                       (self.data[col[1]] > j) & (self.data[col[1]] <= (j + 1))].shape[0]
        #
        # resultarray[7:9, :] = np.zeros([2, self.seg_size[1]])
        # resultarray = resultarray / resultarray.max() * 10
        # resultarray = (np.log10(resultarray + 1)).tolist()
        # resultarray[:] = zip(*resultarray)
        try:
            sns.heatmap(self.kwargs['resultarray'][::-1], cmap="YlGnBu", ax=self.axes)  # 逆时针旋转

            # plt.scatter(df_add[col[0]] / x_seg_size, df_add[col[1]] / y_seg_size, s=3, c='red')

            self.axes.set_xticks(range(0, self.seg_size[0], int(self.seg_size[0] / 10)))
            self.axes.set_xticklabels(range(0, self.xlim, int(self.xlim / 10)))
            self.axes.set_xlabel('Engine_Speed/rpm')
            self.axes.set_yticks(range(0, self.seg_size[1], int(self.seg_size[1] / 10)))
            self.axes.set_yticklabels(range(0, self.ylim, int(self.ylim / 10)))
            self.axes.set_ylabel('Engine_Torque/Nm')
            self.axes.set_title('Engine Operation Map')
        except:
            pass


class AccResponse(FigureCanvas):
    def __init__(self, matrix, para1, parent=None, width=10, height=10, dpi=100, plot_type='3d'):
        self.fig = Figure(figsize=(width, height), dpi=100)
        super(AccResponse, self).__init__(self.fig)
        self.xdata = matrix[1]
        self.ydata = matrix[0]
        self.zdata = matrix[2]
        self.data = matrix
        self.pedal_avg = para1
        self.plot_type = plot_type


class PedalMap(SystemGain):
    def __init__(self, matrix):
        self.xdata = matrix[1]
        self.ydata = matrix[2]
        self.zdata = matrix[0]
        self.data = matrix


class ShiftMap(SystemGain):
    def __init__(self, matrix):
        self.xdata = matrix[2]
        self.ydata = matrix[1]
        self.gear = matrix[0]


# ----------------------------
# end of class definition

# ----------------------------
# function definition


def acc_response(vehspd_data, acc_data, pedal_cut_index, pedal_avg):
    acc_ped_map = [[], [], []]
    for i in range(0, len(pedal_avg)):
        iVehSpd = vehspd_data[pedal_cut_index[0][i]:pedal_cut_index[1][i]]
        iPed = [pedal_avg[i] * ix / ix for ix in range(pedal_cut_index[0][i], pedal_cut_index[1][i])]
        iAcc = acc_data[pedal_cut_index[0][i]:pedal_cut_index[1][i]]
        acc_ped_map[0].append(iPed)
        acc_ped_map[1].append(iVehSpd)
        acc_ped_map[2].append(iAcc)
    obj = AccResponse(acc_ped_map, pedal_avg)
    return obj


def pedal_map(pedal_data, enSpd_data, torq_data, pedal_cut_index, pedal_avg, colour):
    pedal_map = [[], [], []]
    for i in range(0, len(pedal_avg)):
        iTorq = torq_data[pedal_cut_index[0][i]:pedal_cut_index[1][i]]
        iEnSpd = enSpd_data[pedal_cut_index[0][i]:pedal_cut_index[1][i]]
        pedal_map[0].extend(pedal_data[pedal_cut_index[0][i]:pedal_cut_index[1][i]])
        pedal_map[1].extend(iEnSpd)
        pedal_map[2].extend(iTorq)
    obj = PedalMap(pedal_map)
    return obj


def shift_map(pedal_data, gear_data, vehspd_data, pedal_cut_index, pedal_avg, colour):
    shiftMap = [[], [], []]
    for i in range(1, max(gear_data)):
        # Gear上升沿下降沿
        for j in range(1, len(gear_data) - 1):
            if gear_data[j - 1] == i and gear_data[j] == i + 1:
                for k in range(0, len(pedal_avg)):
                    if j > pedal_cut_index[0][k] and j < pedal_cut_index[1][k]:
                        shiftMap[0].append(gear_data[j - 1])
                        shiftMap[1].append(pedal_data[j - 1])
                        shiftMap[2].append(vehspd_data[j - 1])
    # 按档位油门车速排序
    shiftMap_Sort = sorted(np.transpose(shiftMap), key=lambda x: [x[0], x[1], x[2]])
    shiftMap_Data = np.transpose(shiftMap_Sort)
    obj = ShiftMap(shiftMap_Data)
    return obj


# *******3-MainCalculation*********

def plot_En_work_point_main(file_path, BSFC_filepath, xlim, ylim, xre=50, yre=50):
    '''
    Plot System Gain result figs
    :param file_path:
    :return:
    '''
    # *******1-GetSysGainData******
    # 获取数据，判断数据类型，不同读取，获取文件名信息，
    csv_Data_ful = pd.read_csv(file_path)
    # *******2-GetSGColumn*********
    # 获取列号，标准变量及面板输入，数据预处理
    csv_Data = csv_Data_ful.loc[:, ['Travel_ID', 'Time', 'Acc_Actu_Pos', 'VSE_Longt_Acc', 'Veh_Spd_NonDrvn',
                                    'TrEstdGear', 'En_Spd', 'En_Toq']]

    En_workdata = csv_Data[['En_Spd', 'En_Toq']]

    # colour_Bar = ['orange', 'lightgreen', 'c', 'royalblue', 'lightcoral', 'yellow', 'red', 'brown',
    #               'teal', 'blue', 'coral', 'gold', 'lime', 'olive']
    id = csv_Data['Travel_ID'].drop_duplicates()
    dict_return = {}
    for i in range(id.size):
        X, Y, csv, resultarray = En_work_point_cal(En_workdata[csv_Data['Travel_ID'] == id.iloc[i]],
                                                   BSFC_filepath, xlim, ylim, seg_size=[xre, yre])
        dict_return[i] = {'En_work_point_heatmap_data': En_workdata, 'X': X, 'Y': Y,
                          'csv': csv, 'resultarray': resultarray, 'xlim': xlim, 'ylim': ylim, 'seg_size': [xre, yre]}
    return dict_return


def En_work_point_cal(data, BSFC_filepath, xlim, ylim, seg_size):
    col = data.columns
    resultarray = np.zeros(seg_size)
    x_seg_size = xlim / seg_size[0]
    y_seg_size = ylim / seg_size[1]
    data[col[0]] = data[col[0]] / x_seg_size
    data[col[1]] = data[col[1]] / y_seg_size

    csv = pd.read_csv(BSFC_filepath, index_col=0)
    x = np.array([int(i) for i in csv.columns.tolist()]) / x_seg_size
    y = csv.index / y_seg_size
    X, Y = np.meshgrid(x, y)

    for i in range(seg_size[0]):
        for j in range(seg_size[1]):
            resultarray[i, j] = data[(data[col[0]] > i) & (data[col[0]] <= (i + 1)) &
                                     (data[col[1]] > j) & (data[col[1]] <= (j + 1))].shape[0]

    resultarray[7:9, :] = np.zeros([2, seg_size[1]])
    resultarray = resultarray / resultarray.max() * 10
    resultarray = (np.log10(resultarray + 1)).tolist()
    resultarray[:] = zip(*resultarray)
    return X, Y, csv, resultarray


if __name__ == '__main__':
    # *******1-GetSysGainData****** AS22_C16UVV016_SystemGain_20160925_D_M_SL, IP31_L16UOV055_10T_SystemGain_20160225
    plot_En_work_point_main('./AS24_predict_data.csv',BSFC_filepath='./N330_BSFC.csv',xlim=6000,ylim=250)
    plt.show()

    print('Finish!')

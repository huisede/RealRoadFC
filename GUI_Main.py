# coding= utf-8
"""
=====================================================================
Main UI for VI - Vehicle Performance Test&Validation
=====================================================================
Open Souce at https://github.com/huisedetest/VI_Project_Main
Author: SAIC VP Team
>
"""

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from test_ui import Ui_MainWindow  # 界面与逻辑分离
from Calculation_Functions import *  # 算法逻辑
from Generate_Figs import *
from En_working_plot_setting import Ui_En_workpoint_setting
from GUI_En_setting import EnWorkSetting

import sys
import warnings
import ctypes

try:
    temp1 = ctypes.windll.LoadLibrary('DLL\\Qt5Core.dll')
    temp2 = ctypes.windll.LoadLibrary('DLL\\Qt5Gui.dll')
    temp3 = ctypes.windll.LoadLibrary('DLL\\Qt5Widgets.dll')
    temp4 = ctypes.windll.LoadLibrary('DLL\\msvcp140.dll')
    temp5 = ctypes.windll.LoadLibrary('DLL\\Qt5PrintSupport.dll')
except:
    pass

warnings.filterwarnings("ignore")


class MainDlg(QMainWindow, Ui_MainWindow):
    """
    ==================
    Main UI Dialogue
    ==================
    __author__ = 'Lu chao'
    __revised__ = 20171012
    >
    """

    def __init__(self, parent=None):
        super(MainDlg, self).__init__(parent)
        self.setupUi(self)

        self.menu_InputData.triggered.connect(self.open_data)  # 继承图形界面的主菜单Menu_plot的QAction，绑定回调函数
        self.menu_CalData.triggered.connect(self.cal_data)
        self.menu_Engine_Working_Dist.triggered.connect(self.plot_engine_work_point_setting)
        self.menu_ContactUs.triggered.connect(self.connect_us)
        self.open_DBC.clicked.connect(self.push_DBC_Index_file)
        self.open_CAR.clicked.connect(self.push_CAR_Index_file)
        self.open_DRIVER.clicked.connect(self.push_Driver_Index_file)
        # self.DatatableView.setSelectionBehavior(QAbstractItemView.SelectRows)    # 报错  一次选一行功能
        self.DatatableView.clicked.connect(self.graphicview_show)
        # self.Input_SysGain_data.clicked.connect(lambda: self.combobox_index_refresh(['af41', '2fds']))

        self.radio_button_group=QtWidgets.QButtonGroup()
        self.radio_button_group.addButton(self.pt_traditional, id=1)
        self.radio_button_group.addButton(self.pt_hybrid, id=2)
        self.radio_button_group.addButton(self.pt_elec, id=3)

        self.filepath_fulldata = './ZS11_Standard_data.csv'
        self.filepath_DBC = './DBC_index.csv'  # 默认值
        self.filepath_Car = './Car_index.csv'
        self.filepath_Driver = './Driver_index.csv'
        self.filepath_SgResult = ''
        self.pt_type_dict = {1: 'traditional', 2: 'hybrid', 3: 'elec'}
        self.pt_type = self.pt_type_dict[self.radio_button_group.checkedId()]

        self.initial_setting()
        self.createContextMenu_DatatableView()

        # __________________________________多线程测试_________________________________________
        # aa = ViseProcess()
        # self.bb = ViseProcess2()
        # aa.viseprocess_signal.connect(self.thread_message)
        # aa.viseprocess_signal.connect(self.thread_message_2)
        # aa.viseprocess_signal.connect(self.bb.bb2)
        # aa.run()

        # -------------------------------- 回调函数------------------------------------------

    def initial_setting(self):
        self.plainTextEdit.setPlainText(self.filepath_DBC)
        self.plainTextEdit_2.setPlainText(self.filepath_Car)
        self.plainTextEdit_3.setPlainText(self.filepath_Driver)

    def open_data(self):
        """
        Callback function of menu 'InputData' clicked
        Transfer raw date to organized form, using Function 'MainProcess(Process_type=input_data)'

        :param : -
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        self.progressBar.setValue(0)
        self.statusbar.showMessage('测试数据导入中……')

        # filepath = QFileDialog.getOpenFileNames(self, filter='file(*.csv *.xls *.xlsx *txt)')
        filepath = QFileDialog.getOpenFileNames(self, filter='file(*.csv)')
        filepath_full = filepath[0]
        # filepath = QFileDialog.getExistingDirectory(self)
        # filepath_full = filepath + '/*.txt'
        self.MainProcess_thread = MainProcess(filepath_full, self.filepath_DBC, self.filepath_Car,
                                              self.filepath_Driver, Process_type='input_data')
        self.MainProcess_thread.Message_Signal.connect(self.thread_message)  # 传递参数不用写出来，对应好接口函数即可
        self.MainProcess_thread.Message_Finish.connect(self.thread_message)
        self.MainProcess_thread.Message_Process.connect(self.process_bar_show)
        self.MainProcess_thread.Message_Carname.connect(self.set_car_name)
        self.MainProcess_thread.start()

    def cal_data(self):
        """
        Callback function of menu 'CalData' clicked
        Calculate the organized data , using Function 'MainProcess(Process_type=cal_data)',
        and save the result to .csv data, also save the trajectory pictures in ./Image/

        :param : -
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        self.progressBar.setValue(0)
        self.statusbar.showMessage('计算中……')
        self.MainProcess_thread = MainProcess(self.filepath_fulldata, Save_name=self.plainTextEdit_4.toPlainText(),
                                              Process_type='cal_data', pt_type=self.pt_type)
        self.MainProcess_thread.Message_Signal.connect(self.thread_message)
        self.MainProcess_thread.Message_Data.connect(self.datatableview_show)
        self.MainProcess_thread.start()

    @QtCore.pyqtSlot(str)
    def set_car_name(self, carname):
        self.car_name = carname
        if self.car_name != self.filepath_fulldata[2:6:]:  # 后面要换正则匹配！车名不一定是4个字符的！！
            QtWidgets.QMessageBox.information(self, 'Warning', 'Car type from Save name and data is different!')

    @QtCore.pyqtSlot(str)
    def thread_message(self, mes_str):
        """
        Function of showing message on StatusBar

        :param : mes_str   message to show (str)
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        self.statusbar.showMessage(mes_str)
        self.filepath_fulldata = './' + mes_str[6::]  # 有风险，只有Message_Finish.emit("存储文件名:" + mes[2])才是正确的

    @QtCore.pyqtSlot(str)
    def thread_message_2(self, mes_str):
        """
        Function of showing message on StatusBar

        :param : mes_str   message to show (str)
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        print(mes_str)

    @QtCore.pyqtSlot(int)
    def process_bar_show(self, value):
        self.progressBar.setValue(value)

    def datatableview_show(self, data_list):
        """
        Function of showing calculation results in data_table

        :param : data_list   List of result data to show (list)
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        self.model = QtGui.QStandardItemModel(self.DatatableView)
        # self.model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('HH'))
        # self.model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("FF"))
        for i in range(data_list.__len__()):
            for j in range(data_list[0].__len__()):
                self.model.setItem(i, j, QtGui.QStandardItem(data_list[i][j]))

        self.DatatableView.setModel(self.model)
        self.DatatableView.resizeColumnsToContents()

    def plot_engine_work_point_setting(self):  # step 1
        self.En_setting = EnWorkSetting()
        self.En_setting.show()
        self.En_setting.message.connect(self.get_message_from_GUI_En_setting)

    @QtCore.pyqtSlot(dict)
    def get_message_from_GUI_En_setting(self, s):  # step 2
        print(s)
        self.MainProcess_thread = MainProcess(filepath=self.filepath_fulldata,
                                              Process_type='plot_en_work',
                                              BSFC_filepath=s['BSFC_filepath'],
                                              x_resolu=int(s['x_resolu']),
                                              y_resolu=int(s['y_resolu']),
                                              xlim=int(s['xlim']),
                                              ylim=int(s['ylim']),
                                              )
        self.MainProcess_thread.Message_Finish.connect(self.show_engine_work_fig)
        self.MainProcess_thread.start()

    @QtCore.pyqtSlot()
    def show_engine_work_fig(self):  # step 3
        for key, item in self.MainProcess_thread.ax_holder_EnWork.items():
            dr = MyFigureCanvas(width=8, height=5, plot_type='2d',
                                En_work_point_heatmap_data=item['En_work_point_heatmap_data'],
                                seg_size=item['seg_size'],
                                xlim=item['xlim'],
                                ylim=item['ylim'],
                                X=item['X'],
                                Y=item['Y'],
                                csv=item['csv'],
                                resultarray=item['resultarray'],)
            dr.plot_en_work_map_()
            exec('self.graphicsView_En_work_'+str(key)+' = QtWidgets.QGraphicsView()')
            eval('self.gridLayout_6.addWidget(self.graphicsView_En_work_'+str(key)+')')
            self.scene = QtWidgets.QGraphicsScene()
            self.scene.addWidget(dr)
            eval('self.graphicsView_En_work_'+str(key)+'.setScene(self.scene)')
            eval('self.graphicsView_En_work_'+str(key)+'.show()')

    def graphicview_show(self):
        """
        Function of showing the trajectory of the test data in graphic_view,
        we choose the test data which was clicked by user in data_table and find the real index of it,
        the routine pictures are stored in ./Image/, which have already been prepared using function
        'MainProcess(Process_type=cal_data)'

        :param : -
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        Current_index = self.DatatableView.currentIndex()
        Dri_ID = self.model.data(self.model.index(Current_index.row(), 0))
        Date = self.model.data(self.model.index(Current_index.row(), 1))
        Time = self.model.data(self.model.index(Current_index.row(), 2))
        self.scene = QtWidgets.QGraphicsScene()
        try:
            print('./RoutinePic/' + self.car_name + '_' + str(int(float(Dri_ID))) + '_' + str(int(float(Date))) +
                '_' + str(int(float(Time))) + '.png')
            self.routine_pic = QtGui.QPixmap(
                './RoutinePic/' + self.car_name + '_' + str(int(float(Dri_ID))) + '_' + str(int(float(Date))) +
                '_' + str(int(float(Time))) + '.png')  # 车型问题没定义好   待解决 2017/9/30
            self.scene.addPixmap(self.routine_pic)
            self.graphicsView.setScene(self.scene)
        except:
            pass

    def push_DBC_Index_file(self):
        """
        Callback function of Button 'file_path_DBC' clicked
        save the DBC file location you want to refer to

        :param : -
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        filepath = QFileDialog.getOpenFileName(self)
        self.plainTextEdit.setPlainText(filepath[0])
        self.filepath_DBC = filepath[0]

    def push_CAR_Index_file(self):
        """
        Callback function of Button 'file_path_Car' clicked
        save the Car data file location you want to refer to

        :param : -
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        filepath = QFileDialog.getOpenFileName(self)
        self.plainTextEdit_2.setPlainText(filepath[0])
        self.filepath_Car = filepath[0]

    def push_Driver_Index_file(self):
        """
        Callback function of Button 'file_path_Driver' clicked
        save the Driver data file location you want to refer to

        :param : -
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171012
        """
        filepath = QFileDialog.getOpenFileName(self)
        self.plainTextEdit_3.setPlainText(filepath[0])
        self.filepath_Driver = filepath[0]

    def connect_us(self):
        QtWidgets.QMessageBox.information(self, '联系方式', 'yytvo163@163.com')

    # ---------------------------- 右键菜单 -----------------------------------------

    def createContextMenu_DatatableView(self):
        '''

        :return:
        '''
        self.DatatableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.DatatableView.customContextMenuRequested.connect(self.showContextMenu)
        self.DatatableView.contextMenu = QtWidgets.QMenu(self)
        self.DatatableView.actionA = self.DatatableView.contextMenu.addAction(QtGui.QIcon("images/0.png"), u'|  动作A')

        # 添加二级菜单
        self.DatatableView.second = self.DatatableView.contextMenu.addMenu(QtGui.QIcon("images/0.png"), u"|  二级菜单")
        self.DatatableView.actionD = self.DatatableView.second.addAction(QtGui.QIcon("images/0.png"), u'|  动作A')
        self.DatatableView.actionE = self.DatatableView.second.addAction(QtGui.QIcon("images/0.png"), u'|  动作B')
        self.DatatableView.actionF = self.DatatableView.second.addAction(QtGui.QIcon("images/0.png"), u'|  动作C')
        # 将动作与处理函数相关联
        # 这里为了简单，将所有action与同一个处理函数相关联，
        # 当然也可以将他们分别与不同函数关联，实现不同的功能

        return

    def createContextMenu_QtGraphic(self):
        '''

        :return:
        '''
        self.graphicsView_5.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def showContextMenu(self, pos):
        '''''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        self.DatatableView.contextMenu.exec_(QtGui.QCursor.pos())  # 在鼠标位置显示
        # self.contextMenu.show()

    # ------------------------------------ EDQ ---------------------------------------------

    # ---------------------------- System Gain -----------------------------------------
    def load_sysgain_data(self):
        self.progressBar.setValue(0)
        self.statusbar.showMessage('SystemGain测试数据导入中……')
        filepath = QFileDialog.getOpenFileName(self, filter='*.csv')
        filepath_full = filepath[0]
        self.plainTextEdit_5.setPlainText(filepath_full)
        self.MainProcess_thread = MainProcess(filepath_full, Process_type='input_sysgain_data')
        self.MainProcess_thread.Message_Finish.connect(self.thread_message)
        self.MainProcess_thread.Message_Data.connect(self.combobox_index_refresh)
        self.MainProcess_thread.start()

    def combobox_index_refresh(self, itemlist):
        '''

        :param itemlist: headers for user to select
        :return:
        '''

        for i in range(1, 9, 1):  # 编号
            eval('self.comboBox_' + str(i) + '.clear()')  # 清空当前列表
            for j in itemlist:
                eval('self.comboBox_' + str(i) + ".addItem('" + j + "')")  # 写入列表

    def sysgain_cal(self):
        feature_index_array = []
        for i in range(1, 9, 1):  # 获取当前选取字段
            eval('feature_index_array.append(self.comboBox_' + str(i) + '.currentText())')

        self.progressBar.setValue(0)
        self.statusbar.showMessage('计算中……')
        self.MainProcess_thread = MainProcess(self.plainTextEdit_5.toPlainText(), Process_type='cal_SG_data',
                                              data_socket=feature_index_array)
        self.MainProcess_thread.Message_Finish.connect(self.thread_message)
        self.MainProcess_thread.Message_Finish.connect(self.show_ax_pictures)
        self.MainProcess_thread.start()

    def show_ax_pictures(self):

        dr = MyFigureCanvas(width=7, height=5, plot_type='3d',
                            data=self.MainProcess_thread.ax_holder_SG.accresponce.data,
                            para1=self.MainProcess_thread.ax_holder_SG.accresponce.pedal_avg)
        dr.plot_acc_response_()
        # dr = self.MainProcess_thread.ax_holder_SG.accresponce
        # dr.plot_acc_response()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addWidget(dr)
        self.PicToolBar = NavigationBar(dr, self)  # 初始化PicToolBar（本质为Wedgit），绑定到dr这个FigureCanvas上，然后将Toolbar绑到Layout上
        self.gridLayout_2.addWidget(self.PicToolBar)
        self.graphicsView_2.setScene(self.scene)
        self.graphicsView_2.show()

        dr2 = MyFigureCanvas(width=2, height=2, plot_type='2d', data=self.MainProcess_thread.ax_holder_SG.launch.data)
        dr2.plot_launch_()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addWidget(dr2)
        self.graphicsView_3.setScene(self.scene)
        self.graphicsView_3.show()

        dr3 = MyFigureCanvas(width=2, height=2, plot_type='2d', data=self.MainProcess_thread.ax_holder_SG.maxacc.xdata,
                             para1=self.MainProcess_thread.ax_holder_SG.maxacc.ydata)
        dr3.plot_max_acc_()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addWidget(dr3)
        self.graphicsView_4.setScene(self.scene)
        self.graphicsView_4.show()

        dr4 = MyFigureCanvas(width=2, height=2, plot_type='2d', data=self.MainProcess_thread.ax_holder_SG.pedalmap.data)
        dr4.plot_pedal_map_()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addWidget(dr4)
        self.graphicsView_7.setScene(self.scene)
        self.graphicsView_7.show()

        dr5 = MyFigureCanvas(width=7, height=3, plot_type='2d', data=self.MainProcess_thread.ax_holder_SG.launch.data)
        dr5.plot_launch_()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.addWidget(dr5)
        self.graphicsView_5.setScene(self.scene)
        self.graphicsView_5.show()
        self.PicToolBar = NavigationBar(dr5, self)
        self.gridLayout_3.addWidget(self.PicToolBar)
        self.get_mouse_loc = dr5.mpl_connect('button_press_event', self.get_mouse_xy_plot)

    def get_mouse_xy_plot(self, event):
        self.xyCoordinates = [event.xdata, event.ydata]  # 捕捉鼠标点击的坐标


class MainProcess(QtCore.QThread):  # 务必不要继承主窗口，并在线程里面更改主窗口的界面，会莫名其妙的出问题
    """
    =======================
    Main Processing Thread
    =======================
    __author__ = 'Lu chao'
    __revised__ = 20171012
    >
    """

    Message_Signal = QtCore.pyqtSignal(str)
    Message_Finish = QtCore.pyqtSignal(str)
    Message_Process = QtCore.pyqtSignal(int)
    Message_Data = QtCore.pyqtSignal(list)
    Message_Carname = QtCore.pyqtSignal(str)

    def __init__(self, filepath, DBC_path='', Car_path='', Driver_path='', Save_name='', data_socket=[],
                 Process_type='input_data', **kwargs):
        super(MainProcess, self).__init__()
        self.file_path = filepath
        self.DBC_path = DBC_path
        self.Car_path = Car_path
        self.Driver_path = Driver_path
        self.Save_name = Save_name
        self.Process_type = Process_type
        self.Data_Socket = data_socket
        self.output_data = []
        self.kwargs = kwargs

    def run(self):  # 重写进程函数
        """
        Main thread running function
        Cases: input_data
               cal_data
               .......

        :param : -
        :return: -
        __author__ = 'Lu chao'
        __revised__ = 20171111
        """
        if self.Process_type == 'input_data':
            message = read_file(self.file_path, self.DBC_path, self.Car_path, self.Driver_path)
            k = 1
            while k:
                try:
                    mes = message.__next__()  # generator [消息,总任务数]
                    self.Message_Signal.emit("测试数据 " + mes[0][0] + "导入中……")
                    self.Message_Process.emit(int(k / mes[1] * 100))
                    self.Message_Carname.emit(mes[3])  # Carname 用来返回回去查找路径图用
                    k = k + 1
                except:
                    self.Message_Signal.emit("导入完成……")
                    k = 0
            try:
                self.Message_Finish.emit("存储文件名:" + mes[2])
            except:
                self.Message_Finish.emit("导入失败")

        elif self.Process_type == 'cal_data':
            self.out_putdata = data_process(self.file_path, self.Save_name, self.kwargs['pt_type'])
            self.Message_Data.emit(self.out_putdata)
            self.Message_Finish.emit("计算完成！")

        elif self.Process_type == 'input_sysgain_data':
            self.out_putdata = readfile_new(self.file_path)
            self.Message_Data.emit(self.out_putdata)
            self.Message_Finish.emit("导入完成！")

        elif self.Process_type == 'plot_en_work':
            self.ax_holder_EnWork = plot_En_work_point_main(self.file_path, BSFC_filepath=self.kwargs['BSFC_filepath'],
                                                            xre=self.kwargs['x_resolu'], yre=self.kwargs['y_resolu'],
                                                            xlim=self.kwargs['xlim'], ylim=self.kwargs['ylim'])
            self.Message_Finish.emit("完成！")




#
# class ViseProcess(QtCore.QThread):
#     viseprocess_signal = QtCore.pyqtSignal(str)
#
#     def __init__(self, **kwargs):
#         super(ViseProcess, self).__init__()
#
#     def run(self):
#         print('From ViseThread')
#         self.viseprocess_signal.emit('from vise_thread_signal')
#
#
# class ViseProcess2(QtCore.QThread):
#
#     def __init__(self, **kwargs):
#         super(ViseProcess2, self).__init__()
#
#     def bb2(self):
#         print('bb2')
#
#     def run(self):
#         print('From ViseThread2')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = MainDlg()
    dlg.show()
    sys.exit(app.exec())

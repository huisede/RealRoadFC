#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#  @Time     : 2017/12/20 10:42
#  @Author  :  LuChao
#  @Site     : 
#  @File     : GUI_En_setting.py
#  @Software  : PyCharm

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from En_working_plot_setting import Ui_En_workpoint_setting


class EnWorkSetting(QtWidgets.QWidget, Ui_En_workpoint_setting):
    message = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super(EnWorkSetting, self).__init__(parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.ok_clicked_callback)
        self.buttonBox.rejected.connect(self.cancel_clicked_callback)
        self.radioButton.clicked.connect(self.add_filepath_input)
        self.horizontalSlider_1.valueChanged.connect(lambda: self.qsilder_value_change(1))
        self.horizontalSlider_2.valueChanged.connect(lambda: self.qsilder_value_change(2))
        self.initial()

    def initial(self):
        self.x_resolution = self.comboBox.currentText()
        self.y_resolution = self.comboBox_2.currentText()
        self.radio_button_group = QtWidgets.QButtonGroup()
        self.radio_button_group.addButton(self.radioButton, id=1)
        self.radio_button_group.addButton(self.radioButton_2, id=2)
        self.havent_add = True

    def add_filepath_input(self):
        if self.havent_add:
            self.plainTextEdit_2 = QtWidgets.QPlainTextEdit()
            self.plainTextEdit_2.setMaximumSize(QtCore.QSize(2000, 25))
            self.pushButton_2 = QtWidgets.QPushButton()
            self.pushButton_2.setMaximumSize(QtCore.QSize(40, 25))
            self.pushButton_2.setMinimumSize(QtCore.QSize(40, 25))
            self.pushButton_2.setStyleSheet("QPushButton{border-image: url(./Image/file.png);}")
            self.horizontalLayout_2.addWidget(self.plainTextEdit_2)
            self.horizontalLayout_2.addWidget(self.pushButton_2)
            self.pushButton_2.clicked.connect(self.open_BSFC_map)
        self.havent_add = False

    def open_BSFC_map(self):
        filepath = QFileDialog.getOpenFileName(self, filter='file(*.csv *.xls *.xlsx)')
        filepath_full = filepath[0]
        self.plainTextEdit_2.setPlainText(filepath_full)

    def ok_clicked_callback(self):
        self.buttonBox.Ok
        self.x_resolution = self.comboBox.currentText()
        self.y_resolution = self.comboBox_2.currentText()
        self.BSFC_need = self.radio_button_group.checkedId()
        if self.BSFC_need == 1:
            self.message.emit({'BSFC_filepath': self.plainTextEdit_2.toPlainText(),
                               'x_resolu': self.x_resolution,
                               'y_resolu': self.y_resolution,
                               'xlim': self.label_6.text(),
                               'ylim': self.label_7.text()})
        self.close()

    def cancel_clicked_callback(self):
        self.close()

    def qsilder_value_change(self, index):
        if index == 1:
            text_1 = 6000 + 40 * (self.horizontalSlider_1.value() - 50)
            self.label_6.setText(str(text_1))
        elif index == 2:
            text_2 = 250 + 3 * (self.horizontalSlider_2.value() - 50)
            self.label_7.setText(str(text_2))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = EnWorkSetting()
    dlg.show()
    sys.exit(app.exec())

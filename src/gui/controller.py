# -*- coding: utf-8 -*-
#-------------------------------------------------------------------
# controller.py
#-------------------------------------------------------------------
# Copyright (C) 2022-2023  sakura0711  <testuseroozx@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or 
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.




import os, sys
import subprocess


# PyQt5 引擎 ---------------------------------------
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from PyQt5.QtCore import *
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMessageBox, QFileDialog

# 用戶資料 -----------------------------------------
from data.UserData import *

# Socket 模塊-------------------------------------
from tcp.Client import *

# UI 介面 ----------------------------------------
from gui.LoginWindow import Ui_LoginWindow
from gui.MainWindow import Ui_MainWindow


client = Client()

GUI = 'GUI:'
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = '7000'
DEFAULT_SAVE_DIR = f'{os.path.expanduser("~/Downloads")}/save'.replace('\\','/') # .\foo\bar -> ./foo/bar




# LoginWindow 登入畫面
class LoginWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setup_control()

        # --- 窗體美化 ---#
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |  # 窗體置頂
            QtCore.Qt.FramelessWindowHint  # 窗體去邊框
        )
        self.setAttribute(
            QtCore.Qt.WA_TranslucentBackground  # 窗體去背景
        )
        # ---------------#

    # TODO (要互動的元件擺放位置)
    def setup_control(self):

        # self.ui.pushButton.clicked.connect(self.buttonClicked)

        # LoginClose 關閉視窗
        self.ui.label_LoginMin.mousePressEvent = self.LoginMinimized
        # LoginMin 縮小視窗
        self.ui.label_LoginClose.mousePressEvent = self.LoginClose

        # LoginMove 滑鼠移動事件 (拖動視窗實現) -----------------------
        self.ui.LoginMove.mousePressEvent = self.loginPressEvent
        self.ui.LoginMove.mouseMoveEvent = self.loginMoveEvent
        self.ui.LoginMove.mouseReleaseEvent = self.loginReleaseEvent

        # Login 按鈕，檢查帳號資訊-----------------------------------
        self.ui.button_LogicIn.clicked.connect(self.loginIn)

    def LoginClose(self, e:QMouseEvent):
        print(GUI, '關閉視窗!')
        self.close()

    def LoginMinimized(self, e:QMouseEvent):
        print(GUI, '縮小視窗!')
        self.showMinimized()

    ###---------- 滑鼠移動事件(拖動視窗實現) ----------###

    def loginPressEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._startPos = QPoint(e.x(), e.y())
            self._tracking = True

    def loginMoveEvent(self, e: QMouseEvent):
        if self._tracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def loginReleaseEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    ###----------------------------------------------###

    ###----------------- 登入檢查 -----------------###

    def loginIn(self):
        input_ID = self.ui.input_ID.text()
        input_PW = self.ui.input_PW.text()

        # print(GUI, input_ID, type(input_ID))
        # print(GUI, input_PW, type(input_PW))

        if userData.get(input_ID, 'fail') != 'fail':
            if userData[input_ID] == input_PW:
                # from main import MainWindow
                MainWindow = MainWindow_controller()
                MainWindow.show() # 開啟 MainWindow
                self.close() # 關閉 LoginWindow
            else:
                pwfailResult = QMessageBox.warning(self,
                                                   '提示訊息', '密碼錯誤',
                                                   QMessageBox.Ok)
                return
        else:
            allfailResult = QMessageBox.warning(self,
                                                '提示訊息', '找不到此帳號!',
                                                QMessageBox.Ok)
            return
        print(GUI, 'LoginIn clicked!')

    ###-------------------------------------------###


# MainWindow 主要畫面
class MainWindow_controller(QtWidgets.QWidget):

    DownloadProgressBarUpdate = pyqtSignal() # 初始化自訂義信號槽
    UploadProgressBarUpdate = pyqtSignal()

    recvKeyList = [] # 存放打包後產生的寄件碼
    downloadFileInfolist = [] # 存放下載的包裹資訊
    explorerPath = [] # 存放儲存路徑

    RecvCacheKey = '' # 暫存 boxKey 來判斷下載的目標是否相同


    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

        self.ui.stackedWidget.setCurrentIndex(0) # 登入成功後初始介面為 Recv package

        # ----------Setting 預設值-------------------------------------
        self.ui.input_clientIP.setText(DEFAULT_HOST)
        self.ui.input_clientPort.setText(DEFAULT_PORT)
        self.ui.input_ShowSavepath.setText(DEFAULT_SAVE_DIR) # 預設路徑

        ### 儲存設定 (不直接 call SettingSave() 因為會跳保存成功按鈕)
        input_clientIP = self.ui.input_clientIP.text()
        input_clientPort = int(self.ui.input_clientPort.text()) # Port 沒轉 int 會出問題
        client.setHost(input_clientIP, input_clientPort)
        client.setSaveFolder(DEFAULT_SAVE_DIR)
        # ------------------------------------------------------------

        self.ui.button_Client.setStyleSheet('background-color: rgb(255, 255, 255);'
                                             'border-radius: 10px;') # 更改顏色

        #self.ui.button_Client.setEnabled(False) # 未設定 IP 和 Port 時禁用
        #self.ui.button_Server.setEnabled(False) # 未設定 IP 和 Port 時禁用

        self.ui.button_Startlistening.setEnabled(False) # 開始聆聽 button 禁用 (沒有檔案)
        self.ui.label_button_SelectfFile.setEnabled(True)  # 選擇檔案啟用
        self.ui.label_button_SelectfFolder.setEnabled(True)# 選擇檔案啟用

        self.sFileLayoutVisible(False)
        self.ui.Layout_SelectFile.setAlignment(Qt.AlignTop) # 置上對齊
        self.ui.button_Startlistening.setEnabled(False)
        self.cFileLayoutVisible(False)
        self.cFileDownloadVisible(False)
        self.ui.Layout_cRequireFile.setAlignment(Qt.AlignTop) # 置上對齊
        self.ui.progressBar_RecevieFile.setValue(0) # 進度條 0 
        self.ui.progressBar_SendFile.setValue(0)
        
        # --------------標籤超連結----------------------------------------
        
        self.ui.label_logisticsStation.setText('    ‧ <a href="https://github.com/hmes98318/Logistics-Station">Logistics-Station</a>')
        self.ui.label_logisticsStation.setOpenExternalLinks(True)  # 使其成為超連結
        self.ui.label_logisticsStation.setTextInteractionFlags(Qt.TextBrowserInteraction)  # 雙擊可以選擇
        self.ui.label_hmes98318.setText('     ‧ <a href="https://github.com/hmes98318">hmes98318</a>')
        self.ui.label_hmes98318.setOpenExternalLinks(True)  # 使其成為超連結
        self.ui.label_hmes98318.setTextInteractionFlags(Qt.TextBrowserInteraction)  # 雙擊可以選擇
        self.ui.label_sakura0711.setText('     ‧ <a href="https://github.com/sakura0711">sakura0711</a>')
        self.ui.label_sakura0711.setOpenExternalLinks(True)  # 使其成為超連結
        self.ui.label_sakura0711.setTextInteractionFlags(Qt.TextBrowserInteraction)  # 雙擊可以選擇

        # ------------------------------------------------------------

        # ------------定義執行序------------
        self.thread_SendFile = QThread() # 發送包裹
        self.thread_ClientReceiveHeader = QThread() # 接收包裹 header
        self.thread_ClientReceiveFile = QThread() # 接收包裹 
        self.UploadProgressBarUpdate.connect(self.UpdataprogressBar_SendFile) # 連接自訂義信號槽函數
        self.DownloadProgressBarUpdate.connect(self.UpdataProgressBar_ReceiveFile)

        # --- 窗體美化 ---#
        self.setWindowFlags(
            QtCore.Qt.CustomizeWindowHint |  # 窗體置頂
            QtCore.Qt.FramelessWindowHint  # 窗體去邊框
        )
        self.setAttribute(
            QtCore.Qt.WA_TranslucentBackground  # 窗體去背景
        )
        # ---------------#

    # TODO (要互動的元件擺放位置)
    def setup_control(self):
        # self.ui.pushButton.clicked.connect(self.buttonClicked)

        # MainMin 縮小視窗
        self.ui.label_MainMin.mousePressEvent = self.MainMinimized
        # MainClose 關閉視窗
        self.ui.label_MainClose.mousePressEvent = self.MainClose

        # MainMove 滑鼠移動事件 (拖動視窗實現) -----------------------
        self.ui.MainMove.mousePressEvent = self.MainPressEvent
        self.ui.MainMove.mouseMoveEvent = self.MainMoveEvent
        self.ui.MainMove.mouseReleaseEvent = self.MainReleaseEvent

        # MainWindow 按鈕事件 (單窗口多視窗切換實現) ------------------------
        self.ui.button_Client.clicked.connect(self.SwitchToClientPage)
        self.ui.button_Server.clicked.connect(self.SwitchToServerPage)
        self.ui.button_Setting.clicked.connect(self.SwitchToSettingPage)
        self.ui.button_User.clicked.connect(self.SwitchToUserPage)

        # Client 頁面按鈕事件 -----------------------------------------
        self.ui.button_RequireFile.clicked.connect(self.ClientRequireFile)
        self.ui.button_DownloadFile.clicked.connect(self.DownloadFile)
        self.ui.listWidget_downloadInfo.clicked.connect(self.OpenExplorer)

        # Server 頁面按鈕事件 -----------------------------------------
        self.ui.button_Startlistening.clicked.connect(self.StartListening)
        # self.ui.button_SelectfFile.clicked.connect(self.SelectSendFile)
        # self.ui.button_SelectfFolder.clicked.connect(self.SelectSendFolder)
        self.ui.label_button_SelectfFile.mousePressEvent = self.SelectSendFile
        self.ui.label_button_SelectfFolder.mousePressEvent = self.SelectSendFolder
        
        # Setting 頁面按鈕事件 -----------------------------------------
        # self.ui.button_OpenSaveFolder.clicked.connect(self.OpenSaveFolder)
        self.ui.label_button_OpenSaveFolder.mousePressEvent = self.OpenSaveFolder
        self.ui.button_SettingSave.clicked.connect(self.SettingSave)

    ###--- 各事件對應函數 ---###

    def MainMinimized(self, e:QMouseEvent):
        print(GUI, '縮小視窗!')
        self.showMinimized()

        
    def MainClose(self, e:QMouseEvent):
        print(GUI, '關閉視窗!')
        self.close()

    ### Client -----------------------------------------------------------------------------------------------------------

    def SwitchToClientPage(self):
        self.ui.stackedWidget.setCurrentIndex(0) # 切換 Stack Widget 到 (索引值 0 / Client) 頁
        # self.ui.label_schedule.setText(str(0))

        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_Setting,
                                  self.ui.button_User)

    ### Client 取件碼要求 header --------------------------------
    def ClientRequireFile(self):
        self.ui.progressBar_RecevieFile.setMaximum(100) # 進度條最大值 100
        self.cFileLayoutVisible(False) # 清空 client layout 避免要重複下載 連接時還顯示著上一個 header
        self.cFileDownloadVisible(False)
        self.ui.button_RequireFile.setEnabled(False) # 查詢包裹 button 禁用

        self.thread_ClientReceiveHeader.run = self.QThread_ClientReqHeader
        self.thread_ClientReceiveHeader.start()

    def QThread_ClientReqHeader(self):
        boxKey = self.ui.input_PickupNumber.text()

        print('------------------')
        print('[Recv] checkConnection()')
        self.ui.button_RequireFile.setText('正在連接Server...')
        SUCCESS_START = checkConnection()
        if SUCCESS_START == False:
            print('[Recv] --Client connection fail.')
            self.ui.button_RequireFile.setText('連接失敗，重試')
            self.ui.button_RequireFile.setEnabled(True)
            self.thread_ClientReceiveHeader.quit() # 掛起線程
            return
        self.ui.button_RequireFile.setText('連接成功')

        try:
            print('[Recv] reqBoxHeader()')
            SUCCESS_FOUND_HEADER = client.reqBoxHeader(boxKey)
            if SUCCESS_FOUND_HEADER == False:
                self.ui.button_RequireFile.setText('查無包裹')
                client.stop()
                self.ui.button_RequireFile.setEnabled(True)
                self.thread_ClientReceiveHeader.quit() # 掛起線程
                return
        except Exception as error:
            # 瘋狂連續點擊查詢包裹按鈕才會造成接收錯誤
            # GUI 崩潰觸發條件 : 瘋狂連續點擊查詢包裹按鈕 (不影響正常運作)
            # GUI 崩潰只會發生在接收 header 後並且包裹存在並回傳成功, 在 layout 顯示檔名,大小時, 暫時無解
            print('[Recv] reqBoxHeader() json.loads() errors.')
            print(error)
            self.ui.button_RequireFile.setText('連接失敗，重試')
            client.stop()
            self.ui.button_RequireFile.setEnabled(True)
            self.thread_ClientReceiveHeader.quit() # 掛起線程
            return

        # client.stop() 
        self.RecvCacheKey = boxKey # 包裹存在 暫存 boxKey
        self.ui.button_RequireFile.setText('再次查詢')
        self.ui.button_DownloadFile.setText('Download')
        ### GUI 顯示 檔案資料 ----------------------------------
        file_name = str(client.box_name)
        file_type = str(client.box_type) if str(client.box_type) != '.dir' else '' # 是資料夾就清除附檔名
        file_size = str(sizeConverter(client.box_file_size / 1000))

        self.ui.label_cFilename.setText(file_name + file_type)
        self.ui.label_cFilesize.setText(file_size)
        self.cFileLayoutVisible(True)
        ### ---------------------------------------------------
        #time.sleep(1)
        self.ui.button_RequireFile.setEnabled(True)
        self.thread_ClientReceiveHeader.quit() # 掛起線程


    ### Client 取件碼下載檔案 --------------------------------
    def DownloadFile(self):
        self.cFileDownloadVisible(True) # 按下下載後顯示下載進度條
        self.ui.progressBar_RecevieFile.setValue(0) # 進度條歸0
        self.ui.progressBar_RecevieFile.setStyleSheet("#progressBar_RecevieFile{\n"
                                                    "border: 2px solid #000;\n"
                                                    "border-radius: 10px;\n"
                                                    "text-align:center;\n"
                                                    "}\n"
                                                    "#progressBar_RecevieFile::chunk { \n"
                                                    "background-color: rgb(170, 170, 255);\n"
                                                    "border-radius: 8px;\n"
                                                    "}")
        self.ui.button_RequireFile.setEnabled(False) # 查詢包裹 button 禁用
        self.ui.button_DownloadFile.setEnabled(False) # 開始下載 button 禁用

        self.thread_ClientReceiveFile.run = self.QThread_DownloadingFile
        self.thread_ClientReceiveFile.start()

    def QThread_DownloadingFile(self):
        boxKey = self.ui.input_PickupNumber.text()

        print('------------------')
        print('[Recv] checkConnection()')
        self.ui.button_DownloadFile.setText('下載中...')
        SUCCESS_START = checkConnection()
        if SUCCESS_START == False:
            print('[Recv] --Client connection fail.')
            self.ui.button_DownloadFile.setText('下載失敗，重試')
            self.cFileDownloadVisible(False)
            self.ui.button_RequireFile.setEnabled(True)
            self.ui.button_DownloadFile.setEnabled(True)
            self.thread_ClientReceiveFile.quit() # 掛起線程
            return

        QUERYED_KEY = True if boxKey == self.RecvCacheKey else False
        if QUERYED_KEY == False:
            print('[Recv] DownloadFile() not found header, trying reqBoxHeader()')
            SUCCESS_FOUND_HEADER = client.reqBoxHeader(boxKey)
            if SUCCESS_FOUND_HEADER == False:
                self.ui.button_DownloadFile.setText('下載失敗，重試')
                self.ui.button_RequireFile.setText('查無包裹')
                client.stop()
                self.cFileLayoutVisible(False)
                self.cFileDownloadVisible(False)
                self.ui.button_RequireFile.setEnabled(True)
                self.ui.button_DownloadFile.setEnabled(True)
                self.thread_ClientReceiveHeader.quit() # 掛起線程
                return

            self.RecvCacheKey = boxKey
            ### GUI 刷新 檔案資料 ----------------------------------
            file_name = str(client.box_name)
            file_type = str(client.box_type) if str(client.box_type) != '.dir' else '' # 是資料夾就清除附檔名
            file_size = str(sizeConverter(client.box_file_size / 1000))

            self.ui.label_cFilename.setText(file_name + file_type)
            self.ui.label_cFilesize.setText(file_size)
            ### ---------------------------------------------------

        print('[Recv] reqBoxRecv()')
        SUCCESS_RECV = client.reqBoxRecv(boxKey, self.DownloadProgressBarUpdate)
        if SUCCESS_RECV == False:
            print('[Recv] --reqBoxRecv() failed.')
            self.ui.button_DownloadFile.setText('下載失敗，重試')
            client.stop()
            self.cFileDownloadVisible(False)
            self.ui.button_RequireFile.setEnabled(True)
            self.ui.button_DownloadFile.setEnabled(True)
            self.thread_ClientReceiveFile.quit() # 掛起線程
            return

        client.stop()

        ### 下載成功，將文件資訊添加至listview裡面 ------------------------------
        file_name = str(client.box_name)
        file_type = str(client.box_type) if str(client.box_type) != '.dir' else '' # 是資料夾就清除附檔名
        file_size = str(sizeConverter(client.box_file_size / 1000))

        self.downloadFileInfolist.append(str('  取件碼 : ' + boxKey + '\t\t檔案名稱 : '+ file_name + file_type + '\t檔案大小 : ' + file_size))
        self.ui.listWidget_downloadInfo.clear()
        self.ui.listWidget_downloadInfo.addItems(self.downloadFileInfolist)
        ### -------------------------------------------------------------------

        self.ui.button_DownloadFile.setText('下載完成')
        self.ui.button_DownloadFile.setEnabled(True) # 下載結束 button 解鎖
        self.ui.button_RequireFile.setEnabled(True)
        self.thread_ClientReceiveFile.quit() # 掛起線程

    def UpdataProgressBar_ReceiveFile(self):
        progress = int(client.showDownloadProgress())
        #print('progress:',str(progress))

        if progress > 99:
            self.ui.progressBar_RecevieFile.setStyleSheet("#progressBar_RecevieFile{\n"
                                                        "border: 2px solid #000;\n"
                                                        "border-radius: 10px;\n"
                                                        "text-align:center;\n"
                                                        "}\n"
                                                        "#progressBar_RecevieFile::chunk { \n"
                                                        "background-color: rgb(0, 217, 0);\n"
                                                        "border-radius: 8px;\n"
                                                        "}")
        self.ui.progressBar_RecevieFile.setValue(progress) # 增加進度條

    ### Server -----------------------------------------------------------------------------------------------------------

    def SwitchToServerPage(self):
        self.ui.stackedWidget.setCurrentIndex(1) # 切換 Stack Widget 到 (索引值 1 / Server) 頁
        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Server,
                                  self.ui.button_Client,
                                  self.ui.button_Setting,
                                  self.ui.button_User)

        # print(GUI, server.host + ' ' + str(server.port))

    def SelectSendFile(self, e:QMouseEvent):
        try:
            # 開啟資料夾，回傳型態為 tuple
            folder_path = QFileDialog.getOpenFileName(self,
                                                      'Open file',
                                                      './') # start path
            file_name = os.path.basename(folder_path[0])
            file_size = os.path.getsize(folder_path[0]) / 1000  # 1000 byte = 1 kb

            print(GUI, 'folder_path: ', folder_path)
            print(GUI, 'file_name: ', file_name)
            print(GUI, 'file_size: ', file_size)
            client.setFile(folder_path[0])

            self.ui.label_Filename.setText(file_name)
            self.ui.progressBar_SendFile.setValue(0) #進度條歸0
            self.FileSizeConvert(file_size, self.ui.label_Filesize) # 文件大小轉換，印出

            self.ui.button_Startlistening.setText("發送包裹")
            self.ui.button_Startlistening.setEnabled(True)
            self.sFileLayoutVisible(True)
            return
        except:
            print(GUI, '沒有選檔案@w@, 或是檔案類型錯誤')

    def SelectSendFolder(self, e:QMouseEvent):
        try:
            # 開啟資料夾，回傳型態為 tuple
            folder_path = QFileDialog.getExistingDirectory(self,
                                                            'Open folder',
                                                            './') # start path

            if not os.path.isdir(str(folder_path)): # 沒選擇資料夾跳例外
                raise ValueError(GUI, '--folder_path is None.')

            print(str(folder_path))
            # file_name = os.path.basename(folder_path[0])
            # file_size = os.path.getsize(folder_path[0]) / 1000  # 1000 byte = 1 kb

            print(GUI, 'folder_path: ', folder_path)
            print(GUI, 'file_name: ', client.file_name)
            print(GUI, 'file_size: ', client.file_size)
            client.setFile(folder_path)

            self.ui.label_Filename.setText(client.file_name)
            self.ui.progressBar_SendFile.setValue(0) #進度條歸0
            self.FileSizeConvert(client.file_size / 1000, self.ui.label_Filesize) # 文件大小轉換，印出

            self.ui.button_Startlistening.setText("發送包裹")
            self.ui.button_Startlistening.setEnabled(True)
            self.sFileLayoutVisible(True)
            return
        except:
            print(GUI, '沒有選檔案@w@, 或是檔案類型錯誤')

    def FileSizeConvert(self, file_size, label: QtWidgets.QLabel):
        label.setText(sizeConverter(file_size))

    def StartListening(self):
        self.ui.progressBar_SendFile.setMaximum(100) # 進度條最大值 100
        self.ui.progressBar_SendFile.setStyleSheet("#progressBar_SendFile{\n"
                                                    "border: 2px solid #000;\n"
                                                    "border-radius: 10px;\n"
                                                    "text-align:center;\n"
                                                    "}\n"
                                                    "#progressBar_SendFile::chunk { \n"
                                                    "background-color: rgb(170, 170, 255);\n"
                                                    "border-radius: 8px;\n"
                                                    "}") # 進度條顏色
        self.ui.button_Startlistening.setEnabled(False) # 開始發送 button 禁用
        self.ui.label_button_SelectfFile.setEnabled(False) # 聆聽時選擇檔案 button 禁用
        self.ui.label_button_SelectfFolder.setEnabled(False) # 聆聽時選擇資料夾 button 禁用

        self.thread_SendFile.run = self.QThread_SendFile
        self.thread_SendFile.start()

    def QThread_SendFile(self):
        self.sFileLayoutVisible(True)
        self.ui.button_Startlistening.setEnabled(True)

        print('------------------')
        print('[Send] checkConnection()')
        self.ui.button_Startlistening.setText('連接Server...')
        SUCCESS_START = checkConnection()
        if SUCCESS_START == False:
            print(GUI, '--Client connection fail.')
            self.ui.button_Startlistening.setEnabled(True)
            self.ui.button_SelectfFile.setEnabled(True)
            self.ui.button_Startlistening.setText('連接失敗')
            self.thread_SendFile.quit() # 掛起線程
            return

        print('[Send] packingBox()')
        self.ui.button_Startlistening.setText('打包檔案中...')
        SUCCESS_PACKBOX = client.packingBox()
        if SUCCESS_PACKBOX == False:
            print(GUI, '--Client connection fail.')
            self.ui.button_Startlistening.setEnabled(True)
            self.ui.button_SelectfFile.setEnabled(True)
            self.ui.button_Startlistening.setText('打包失敗')
            self.thread_SendFile.quit() # 掛起線程
            return

        print('[Send] reqBoxSend()')
        self.ui.button_Startlistening.setText('發送包裹中...')
        recvKey = client.reqBoxSend(self.UploadProgressBarUpdate)
        print('reqBoxSend() -> recvKey :', recvKey)

        ### 取件碼顯示 -------------------------------------------
        if recvKey == False:
            self.recvKeyList.append('\t寄件失敗')
        else:
            # tar_size 算出來最小都 10KB 起跳 我也不知為啥 client.py 的寫法跟 self.SelectSendFile() 的一樣 說不定是打包成tar後的鍋 反正能動先不管了
            self.recvKeyList.append(str('  取件碼 : ' + recvKey + '\t\t檔案大小 : ' + sizeConverter(client.tar_size / 1000)))

        self.ui.listWidget_Sendpackage.clear()
        self.ui.listWidget_Sendpackage.addItems(self.recvKeyList)
        ### -----------------------------------------------------

        client.stop()

        self.ui.button_Startlistening.setText('發送包裹') # 傳送完成了按鈕重置
        self.ui.button_Startlistening.setEnabled(True) # 開始發送 button 啟用
        self.ui.label_button_SelectfFile.setEnabled(True) # 選擇檔案 button 啟用
        self.ui.label_button_SelectfFolder.setEnabled(True) # 選擇資料夾 button 啟用
        self.thread_SendFile.quit() # 掛起線程

    def UpdataprogressBar_SendFile(self):
        progress = int(client.showUploadProgress())
        #print('progress:',str(progress))

        if progress > 99:
            self.ui.button_Startlistening.setText('接收取件碼中...')
            self.ui.progressBar_SendFile.setStyleSheet("#progressBar_SendFile{\n"
                                                    "border: 2px solid #000;\n"
                                                    "border-radius: 10px;\n"
                                                    "text-align:center;\n"
                                                    "}\n"
                                                    "#progressBar_SendFile::chunk { \n"
                                                    "background-color: rgb(0, 217, 0);\n"
                                                    "border-radius: 8px;\n"
                                                    "}")
        self.ui.progressBar_SendFile.setValue(progress) # 增加進度條

    def OpenExplorer(self):
        self.explorerPath = ' \"' + str(self.ui.input_ShowSavepath.text()).replace('/','\\') + '\"' # 替換路徑 / -> \\
        # subprocess.Popen('explorer "C:\\Users\\MSI GP65\\Downloads"')  # 依照路徑開啟檔案管
        subprocess.Popen('explorer' + str(self.explorerPath) )  # 依照路徑開啟檔案管
        # subprocess.Popen('explorer' + str(self.explorerPath) )  # 依照路徑開啟檔案管
        # self.ui.listWidget_downloadInfo.currentitem()



    ### Setting -----------------------------------------------------------------------------------------------------------

    def SwitchToSettingPage(self):
        self.ui.stackedWidget.setCurrentIndex(2) # 切換 Stack Widget 到 (索引值 2 / Setting) 頁

        # 顏色轉換
        self.button_setStyleSheet(self.ui.button_Setting,
                                  self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_User)

    def SettingSave(self):
        while True:
            try:
                input_clientIP = self.ui.input_clientIP.text()
                input_clientPort = int(self.ui.input_clientPort.text())

                if input_clientPort > 65535 or input_clientPort < 1 :
                    raise ValueError(GUI, 'input_clientPort out of range.')

                client.setHost(input_clientIP, input_clientPort)
                QMessageBox.information(self,
                                        '提示訊息', '保存成功',
                                        QMessageBox.Ok)
                
                print(GUI, f'setHost({input_clientIP}, {input_clientPort})')
                self.ui.button_Client.setEnabled(True)
                self.ui.button_Server.setEnabled(True)
                return
            except socket.gaierror:
                result = QMessageBox.warning(self,
                                            '查無域名',
                                            '請檢察輸入的網址或IP是否正確!\n'+
                                            '網址範例 example.com\n'+
                                            'IPv4 範例 192.168.1.10',
                                            QMessageBox.Ok)
                if result == QMessageBox.Ok:
                    print(GUI, 'Domain not found or IP value error.')
                    return
            except TypeError and ValueError:
                result = QMessageBox.warning(self,
                                            '參數錯誤',
                                            '請確認輸入正確的數值!\n'+
                                            'Port 範例 7000',
                                            QMessageBox.Ok)
                if result == QMessageBox.Ok:
                    print(GUI, 'Setting input value error.')
                    return

    def OpenSaveFolder(self, e:QMouseEvent):
        folder_path = QFileDialog.getExistingDirectory(self,
                                                       'Open folder',
                                                       './') # start path

        if folder_path == '': # 沒選擇就跳回預設值
            folder_path = DEFAULT_SAVE_DIR

        client.setSaveFolder(folder_path) # 設置 client 儲存路徑
        print(GUI, 'setSaveFolder() =', folder_path)
        self.ui.input_ShowSavepath.setText(folder_path)

    ### User -----------------------------------------------------------------------------------------------------------

    def SwitchToUserPage(self):
        self.ui.stackedWidget.setCurrentIndex(3) # 切換 Stack Widget 到 (索引值 3 / User) 頁

        # 顏色轉換
        # button_union = [self.ui.button_User, self.ui.button_Client, self.ui.button_Server, self.ui.button_Setting]
        self.button_setStyleSheet(self.ui.button_User,
                                  self.ui.button_Client,
                                  self.ui.button_Server,
                                  self.ui.button_Setting)

    ### 滑鼠移動事件(拖動視窗實現) -----------------------------------------------------------------------------------------

    def MainPressEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._startPos = QPoint(e.x(), e.y())
            self._tracking = True

    def MainMoveEvent(self, e: QMouseEvent):
        if self._tracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def MainReleaseEvent(self, e: QMouseEvent):
        if e.button() == 1:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    ### 奇怪的東西 --------------------------------------------------------------------------------------------------------

    def sFileLayoutVisible(self, flag):
        self.ui.label_Filesize.setVisible(flag)
        self.ui.label_Filename.setVisible(flag)
        self.ui.hint_Filesize.setVisible(flag)
        self.ui.hint_Filename.setVisible(flag)
        self.ui.hint_Sendschedule.setVisible(flag)
        self.ui.progressBar_SendFile.setVisible(flag)

        self.ui.Layout_FileInfo.setEnabled(flag)
        # self.ui.Layout_Filesize.setEnabled(flag)
        # self.ui.Layout_Filename.setEnabled(flag)

    def cFileLayoutVisible(self, flag):
        self.ui.label_cFilename.setVisible(flag)
        self.ui.label_cFilesize.setVisible(flag)
        self.ui.hint_cFileize.setVisible(flag)
        self.ui.hint_cFilename.setVisible(flag)
        self.ui.button_DownloadFile.setVisible(flag)

        self.ui.Layout_cFileInfo.setEnabled(flag)
        self.ui.Layout_cFileInfo2.setEnabled(flag)
        self.ui.Layout_cFilename.setEnabled(flag)
        self.ui.Layout_cFilesize.setEnabled(flag)
        

    def cFileDownloadVisible(self, flag):
        self.ui.hint_schedule.setVisible(flag)
        self.ui.progressBar_RecevieFile.setVisible(flag)

    def button_setStyleSheet(self, NowFocus: QtWidgets.QPushButton,
                             Other1: QtWidgets.QPushButton,
                             Other2: QtWidgets.QPushButton,
                             Other3: QtWidgets.QPushButton):

        otherPage_StyleSheet = 'background-color: rgba(36, 67, 124, 50);' \
                                'border-radius: 10px;' \
                                'color: rgb(255, 255, 255);'
        nowPage_StyleSheet = 'background-color: rgba(255, 255, 255, 255);' \
                                'border-radius: 10px;'

        NowFocus.setStyleSheet(nowPage_StyleSheet)
        Other1.setStyleSheet(otherPage_StyleSheet)
        Other2.setStyleSheet(otherPage_StyleSheet)
        Other3.setStyleSheet(otherPage_StyleSheet)




# 檢查Server連接 沒連接就重連
def checkConnection():
    try:
        CONNECT = client.reqConnection()
        if CONNECT == False:
            try:
                print('[Check] Server not connected, try to reconnect.')
                SUCCESS_START = client.start()
                if SUCCESS_START == False:
                    print('[Check] Failed to connect to the server.')
                    return False
                print('[Check] Connected.')
                return True
            except:
                print('[Check] Failed to connect to the server.')
                return False
    except:
        try:
            print('[Check] Server not connected, try to reconnect.')
            SUCCESS_START = client.start()
            if SUCCESS_START == False:
                print('[Check] Failed to connect to the server.')
                return False
            print('[Check] Connected.')
            return True
        except:
            print('[Check] Failed to connect to the server.')
            return False
    print('[Check] Nothing to do.')
    return True


def sizeConverter(file_size):
    if file_size < 1000:
        return (str('%.2f' % file_size) + ' KB')
    elif file_size < 1000 * 1000:
        return (str('%.2f' % (file_size / 1000)) + ' MB')
    elif file_size < 1000 * 1000 * 1000:
        return (str('%.2f' % (file_size / 1000 / 1000)) + ' GB')
    else:
        return (str('%.2f' % (file_size / 1000 / 1000 / 1000)) + ' TB')
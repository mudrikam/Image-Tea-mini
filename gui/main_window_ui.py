# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionOpen_Image = QAction(MainWindow)
        self.actionOpen_Image.setObjectName(u"actionOpen_Image")
        icon = QIcon()
        iconThemeName = u"document-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionOpen_Image.setIcon(icon)
        self.actionOpen_Multiple_Images = QAction(MainWindow)
        self.actionOpen_Multiple_Images.setObjectName(u"actionOpen_Multiple_Images")
        self.actionOpen_Multiple_Images.setIcon(icon)
        self.actionOpen_Folder = QAction(MainWindow)
        self.actionOpen_Folder.setObjectName(u"actionOpen_Folder")
        icon1 = QIcon()
        iconThemeName = u"folder-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionOpen_Folder.setIcon(icon1)
        self.actionOpen_Multiple_Folders = QAction(MainWindow)
        self.actionOpen_Multiple_Folders.setObjectName(u"actionOpen_Multiple_Folders")
        self.actionOpen_Multiple_Folders.setIcon(icon1)
        self.actionOpen_Video = QAction(MainWindow)
        self.actionOpen_Video.setObjectName(u"actionOpen_Video")
        self.actionOpen_Video.setIcon(icon)
        self.actionOpen_Multiple_Videos = QAction(MainWindow)
        self.actionOpen_Multiple_Videos.setObjectName(u"actionOpen_Multiple_Videos")
        self.actionOpen_Multiple_Videos.setIcon(icon)
        self.actionCopy = QAction(MainWindow)
        self.actionCopy.setObjectName(u"actionCopy")
        icon2 = QIcon()
        iconThemeName = u"edit-copy"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionCopy.setIcon(icon2)
        self.actionPaste = QAction(MainWindow)
        self.actionPaste.setObjectName(u"actionPaste")
        icon3 = QIcon()
        iconThemeName = u"edit-paste"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionPaste.setIcon(icon3)
        self.actionCut = QAction(MainWindow)
        self.actionCut.setObjectName(u"actionCut")
        icon4 = QIcon()
        iconThemeName = u"edit-cut"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionCut.setIcon(icon4)
        self.actionDelete = QAction(MainWindow)
        self.actionDelete.setObjectName(u"actionDelete")
        icon5 = QIcon()
        iconThemeName = u"edit-delete"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionDelete.setIcon(icon5)
        self.actionSelect_All = QAction(MainWindow)
        self.actionSelect_All.setObjectName(u"actionSelect_All")
        icon6 = QIcon()
        iconThemeName = u"edit-select-all"
        if QIcon.hasThemeIcon(iconThemeName):
            icon6 = QIcon.fromTheme(iconThemeName)
        else:
            icon6.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionSelect_All.setIcon(icon6)
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName(u"actionNew")
        icon7 = QIcon()
        iconThemeName = u"document-new"
        if QIcon.hasThemeIcon(iconThemeName):
            icon7 = QIcon.fromTheme(iconThemeName)
        else:
            icon7.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionNew.setIcon(icon7)
        self.actionExport_CSV_Freepik = QAction(MainWindow)
        self.actionExport_CSV_Freepik.setObjectName(u"actionExport_CSV_Freepik")
        icon8 = QIcon()
        iconThemeName = u"document-export"
        if QIcon.hasThemeIcon(iconThemeName):
            icon8 = QIcon.fromTheme(iconThemeName)
        else:
            icon8.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionExport_CSV_Freepik.setIcon(icon8)
        self.actionExport_CSV_Shutterstock = QAction(MainWindow)
        self.actionExport_CSV_Shutterstock.setObjectName(u"actionExport_CSV_Shutterstock")
        self.actionExport_CSV_Shutterstock.setIcon(icon8)
        self.actionExport_CSV_Adobe_Stock = QAction(MainWindow)
        self.actionExport_CSV_Adobe_Stock.setObjectName(u"actionExport_CSV_Adobe_Stock")
        self.actionExport_CSV_Adobe_Stock.setIcon(icon8)
        self.actionExport_CSV_iStock = QAction(MainWindow)
        self.actionExport_CSV_iStock.setObjectName(u"actionExport_CSV_iStock")
        self.actionExport_CSV_iStock.setIcon(icon8)
        self.actionDeselect_All = QAction(MainWindow)
        self.actionDeselect_All.setObjectName(u"actionDeselect_All")
        icon9 = QIcon()
        iconThemeName = u"edit-select-none"
        if QIcon.hasThemeIcon(iconThemeName):
            icon9 = QIcon.fromTheme(iconThemeName)
        else:
            icon9.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionDeselect_All.setIcon(icon9)
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon10 = QIcon()
        iconThemeName = u"application-exit"
        if QIcon.hasThemeIcon(iconThemeName):
            icon10 = QIcon.fromTheme(iconThemeName)
        else:
            icon10.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionQuit.setIcon(icon10)
        self.actionRefresh = QAction(MainWindow)
        self.actionRefresh.setObjectName(u"actionRefresh")
        icon11 = QIcon()
        iconThemeName = u"view-refresh"
        if QIcon.hasThemeIcon(iconThemeName):
            icon11 = QIcon.fromTheme(iconThemeName)
        else:
            icon11.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionRefresh.setIcon(icon11)
        self.actionClear = QAction(MainWindow)
        self.actionClear.setObjectName(u"actionClear")
        icon12 = QIcon()
        iconThemeName = u"edit-clear"
        if QIcon.hasThemeIcon(iconThemeName):
            icon12 = QIcon.fromTheme(iconThemeName)
        else:
            icon12.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionClear.setIcon(icon12)
        self.actionRename = QAction(MainWindow)
        self.actionRename.setObjectName(u"actionRename")
        icon13 = QIcon()
        iconThemeName = u"edit-rename"
        if QIcon.hasThemeIcon(iconThemeName):
            icon13 = QIcon.fromTheme(iconThemeName)
        else:
            icon13.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionRename.setIcon(icon13)
        self.actionRename_All = QAction(MainWindow)
        self.actionRename_All.setObjectName(u"actionRename_All")
        self.actionRename_All.setIcon(icon13)
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        icon14 = QIcon()
        iconThemeName = u"preferences-system"
        if QIcon.hasThemeIcon(iconThemeName):
            icon14 = QIcon.fromTheme(iconThemeName)
        else:
            icon14.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionPreferences.setIcon(icon14)
        self.actionGoogle_Gemini = QAction(MainWindow)
        self.actionGoogle_Gemini.setObjectName(u"actionGoogle_Gemini")
        icon15 = QIcon()
        iconThemeName = u"system-run"
        if QIcon.hasThemeIcon(iconThemeName):
            icon15 = QIcon.fromTheme(iconThemeName)
        else:
            icon15.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionGoogle_Gemini.setIcon(icon15)
        self.actionOpen_AI = QAction(MainWindow)
        self.actionOpen_AI.setObjectName(u"actionOpen_AI")
        self.actionOpen_AI.setIcon(icon15)
        self.actionWhatsApp_Group = QAction(MainWindow)
        self.actionWhatsApp_Group.setObjectName(u"actionWhatsApp_Group")
        icon16 = QIcon()
        iconThemeName = u"user-group-properties"
        if QIcon.hasThemeIcon(iconThemeName):
            icon16 = QIcon.fromTheme(iconThemeName)
        else:
            icon16.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionWhatsApp_Group.setIcon(icon16)
        self.actionLicense = QAction(MainWindow)
        self.actionLicense.setObjectName(u"actionLicense")
        icon17 = QIcon()
        iconThemeName = u"text-x-generic"
        if QIcon.hasThemeIcon(iconThemeName):
            icon17 = QIcon.fromTheme(iconThemeName)
        else:
            icon17.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionLicense.setIcon(icon17)
        self.actionContributors = QAction(MainWindow)
        self.actionContributors.setObjectName(u"actionContributors")
        icon18 = QIcon()
        iconThemeName = u"system-users"
        if QIcon.hasThemeIcon(iconThemeName):
            icon18 = QIcon.fromTheme(iconThemeName)
        else:
            icon18.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionContributors.setIcon(icon18)
        self.actionReport_Issue = QAction(MainWindow)
        self.actionReport_Issue.setObjectName(u"actionReport_Issue")
        icon19 = QIcon()
        iconThemeName = u"dialog-warning"
        if QIcon.hasThemeIcon(iconThemeName):
            icon19 = QIcon.fromTheme(iconThemeName)
        else:
            icon19.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionReport_Issue.setIcon(icon19)
        self.actionGithub_Repository = QAction(MainWindow)
        self.actionGithub_Repository.setObjectName(u"actionGithub_Repository")
        icon20 = QIcon()
        iconThemeName = u"folder-remote"
        if QIcon.hasThemeIcon(iconThemeName):
            icon20 = QIcon.fromTheme(iconThemeName)
        else:
            icon20.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionGithub_Repository.setIcon(icon20)
        self.actionCheck_for_Updates = QAction(MainWindow)
        self.actionCheck_for_Updates.setObjectName(u"actionCheck_for_Updates")
        icon21 = QIcon()
        iconThemeName = u"software-update-available"
        if QIcon.hasThemeIcon(iconThemeName):
            icon21 = QIcon.fromTheme(iconThemeName)
        else:
            icon21.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionCheck_for_Updates.setIcon(icon21)
        self.actionAbout_2 = QAction(MainWindow)
        self.actionAbout_2.setObjectName(u"actionAbout_2")
        icon22 = QIcon()
        iconThemeName = u"help-about"
        if QIcon.hasThemeIcon(iconThemeName):
            icon22 = QIcon.fromTheme(iconThemeName)
        else:
            icon22.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionAbout_2.setIcon(icon22)
        self.actionDonate = QAction(MainWindow)
        self.actionDonate.setObjectName(u"actionDonate")
        icon23 = QIcon()
        iconThemeName = u"emblem-favorite"
        if QIcon.hasThemeIcon(iconThemeName):
            icon23 = QIcon.fromTheme(iconThemeName)
        else:
            icon23.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionDonate.setIcon(icon23)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuExport = QMenu(self.menuFile)
        self.menuExport.setObjectName(u"menuExport")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuAI = QMenu(self.menuSettings)
        self.menuAI.setObjectName(u"menuAI")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setStyleSheet(u"QStatusBar{\n"
"	border-top: 1px solid rgba(114, 114, 114, 0.2); \n"
"}")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen_Image)
        self.menuFile.addAction(self.actionOpen_Multiple_Images)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_Folder)
        self.menuFile.addAction(self.actionOpen_Multiple_Folders)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_Video)
        self.menuFile.addAction(self.actionOpen_Multiple_Videos)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.menuExport.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuFile.addSeparator()
        self.menuExport.addAction(self.actionExport_CSV_Freepik)
        self.menuExport.addAction(self.actionExport_CSV_Shutterstock)
        self.menuExport.addAction(self.actionExport_CSV_Adobe_Stock)
        self.menuExport.addAction(self.actionExport_CSV_iStock)
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addAction(self.actionDelete)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSelect_All)
        self.menuEdit.addAction(self.actionDeselect_All)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRefresh)
        self.menuEdit.addAction(self.actionClear)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRename)
        self.menuEdit.addAction(self.actionRename_All)
        self.menuSettings.addAction(self.actionPreferences)
        self.menuSettings.addAction(self.menuAI.menuAction())
        self.menuAI.addAction(self.actionGoogle_Gemini)
        self.menuAI.addAction(self.actionOpen_AI)
        self.menuHelp.addAction(self.actionWhatsApp_Group)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionLicense)
        self.menuHelp.addAction(self.actionContributors)
        self.menuHelp.addAction(self.actionReport_Issue)
        self.menuHelp.addAction(self.actionGithub_Repository)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionCheck_for_Updates)
        self.menuHelp.addAction(self.actionDonate)
        self.menuHelp.addAction(self.actionAbout_2)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen_Image.setText(QCoreApplication.translate("MainWindow", u"Open Image", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_Image.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_Multiple_Images.setText(QCoreApplication.translate("MainWindow", u"Open Multiple Images", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_Multiple_Images.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_Folder.setText(QCoreApplication.translate("MainWindow", u"Open Folder", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_Folder.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+F", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_Multiple_Folders.setText(QCoreApplication.translate("MainWindow", u"Open Multiple Folders", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_Multiple_Folders.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+F", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_Video.setText(QCoreApplication.translate("MainWindow", u"Open Video", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_Video.setShortcut(QCoreApplication.translate("MainWindow", u"Shift+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen_Multiple_Videos.setText(QCoreApplication.translate("MainWindow", u"Open Multiple Videos", None))
#if QT_CONFIG(shortcut)
        self.actionOpen_Multiple_Videos.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+Shift+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionCopy.setText(QCoreApplication.translate("MainWindow", u"Copy", None))
#if QT_CONFIG(shortcut)
        self.actionCopy.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.actionPaste.setText(QCoreApplication.translate("MainWindow", u"Paste", None))
#if QT_CONFIG(shortcut)
        self.actionPaste.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+V", None))
#endif // QT_CONFIG(shortcut)
        self.actionCut.setText(QCoreApplication.translate("MainWindow", u"Cut", None))
#if QT_CONFIG(shortcut)
        self.actionCut.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+X", None))
#endif // QT_CONFIG(shortcut)
        self.actionDelete.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
#if QT_CONFIG(shortcut)
        self.actionDelete.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.actionSelect_All.setText(QCoreApplication.translate("MainWindow", u"Select All", None))
#if QT_CONFIG(shortcut)
        self.actionSelect_All.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+A", None))
#endif // QT_CONFIG(shortcut)
        self.actionNew.setText(QCoreApplication.translate("MainWindow", u"New", None))
#if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionExport_CSV_Freepik.setText(QCoreApplication.translate("MainWindow", u"Export CSV Freepik", None))
        self.actionExport_CSV_Shutterstock.setText(QCoreApplication.translate("MainWindow", u"Export CSV Shutterstock", None))
        self.actionExport_CSV_Adobe_Stock.setText(QCoreApplication.translate("MainWindow", u"Export CSV Adobe Stock", None))
        self.actionExport_CSV_iStock.setText(QCoreApplication.translate("MainWindow", u"Export CSV iStock", None))
        self.actionDeselect_All.setText(QCoreApplication.translate("MainWindow", u"Deselect All", None))
#if QT_CONFIG(shortcut)
        self.actionDeselect_All.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+A", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionRefresh.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
#if QT_CONFIG(shortcut)
        self.actionRefresh.setShortcut(QCoreApplication.translate("MainWindow", u"F5", None))
#endif // QT_CONFIG(shortcut)
        self.actionClear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
#if QT_CONFIG(shortcut)
        self.actionClear.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+L", None))
#endif // QT_CONFIG(shortcut)
        self.actionRename.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
#if QT_CONFIG(shortcut)
        self.actionRename.setShortcut(QCoreApplication.translate("MainWindow", u"F2", None))
#endif // QT_CONFIG(shortcut)
        self.actionRename_All.setText(QCoreApplication.translate("MainWindow", u"Rename All", None))
#if QT_CONFIG(shortcut)
        self.actionRename_All.setShortcut(QCoreApplication.translate("MainWindow", u"Shift+F2", None))
#endif // QT_CONFIG(shortcut)
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
#if QT_CONFIG(shortcut)
        self.actionPreferences.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
        self.actionGoogle_Gemini.setText(QCoreApplication.translate("MainWindow", u"Google Gemini", None))
        self.actionOpen_AI.setText(QCoreApplication.translate("MainWindow", u"Open AI", None))
        self.actionWhatsApp_Group.setText(QCoreApplication.translate("MainWindow", u"WhatsApp Group", None))
        self.actionLicense.setText(QCoreApplication.translate("MainWindow", u"View License", None))
        self.actionContributors.setText(QCoreApplication.translate("MainWindow", u"Contributors", None))
        self.actionReport_Issue.setText(QCoreApplication.translate("MainWindow", u"Report Issue", None))
        self.actionGithub_Repository.setText(QCoreApplication.translate("MainWindow", u"Github Repository", None))
        self.actionCheck_for_Updates.setText(QCoreApplication.translate("MainWindow", u"Check for Updates", None))
        self.actionAbout_2.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionDonate.setText(QCoreApplication.translate("MainWindow", u"Donate", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuExport.setTitle(QCoreApplication.translate("MainWindow", u"Export", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuAI.setTitle(QCoreApplication.translate("MainWindow", u"AI", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi


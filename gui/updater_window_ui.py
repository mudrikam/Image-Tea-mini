# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'updater_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_UpdaterWindow(object):
    def setupUi(self, UpdaterWindow):
        if not UpdaterWindow.objectName():
            UpdaterWindow.setObjectName(u"UpdaterWindow")
        UpdaterWindow.resize(600, 300)
        self.verticalLayout_2 = QVBoxLayout(UpdaterWindow)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lblTitle = QLabel(UpdaterWindow)
        self.lblTitle.setObjectName(u"lblTitle")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.lblTitle.setFont(font)
        self.lblTitle.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lblTitle)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lblUpdateVersion = QLabel(UpdaterWindow)
        self.lblUpdateVersion.setObjectName(u"lblUpdateVersion")

        self.verticalLayout_3.addWidget(self.lblUpdateVersion)

        self.lblCurrentVersion = QLabel(UpdaterWindow)
        self.lblCurrentVersion.setObjectName(u"lblCurrentVersion")

        self.verticalLayout_3.addWidget(self.lblCurrentVersion)


        self.verticalLayout.addLayout(self.verticalLayout_3)

        self.lblUpdateMessage = QLabel(UpdaterWindow)
        self.lblUpdateMessage.setObjectName(u"lblUpdateMessage")
        self.lblUpdateMessage.setAlignment(Qt.AlignCenter)
        self.lblUpdateMessage.setWordWrap(True)

        self.verticalLayout.addWidget(self.lblUpdateMessage)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.progressUpdate = QProgressBar(UpdaterWindow)
        self.progressUpdate.setObjectName(u"progressUpdate")
        self.progressUpdate.setMinimumSize(QSize(0, 10))
        self.progressUpdate.setValue(0)
        self.progressUpdate.setTextVisible(False)

        self.verticalLayout_4.addWidget(self.progressUpdate)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.checkBox = QCheckBox(UpdaterWindow)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_3.addWidget(self.checkBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.btnCheck = QPushButton(UpdaterWindow)
        self.btnCheck.setObjectName(u"btnCheck")

        self.horizontalLayout_3.addWidget(self.btnCheck)

        self.btnUpdate = QPushButton(UpdaterWindow)
        self.btnUpdate.setObjectName(u"btnUpdate")
        self.btnUpdate.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.btnUpdate)

        self.pushButton = QPushButton(UpdaterWindow)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_3.addWidget(self.pushButton)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.verticalLayout_4)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(UpdaterWindow)

        QMetaObject.connectSlotsByName(UpdaterWindow)
    # setupUi

    def retranslateUi(self, UpdaterWindow):
        UpdaterWindow.setWindowTitle(QCoreApplication.translate("UpdaterWindow", u"Check for Updates", None))
        self.lblTitle.setText(QCoreApplication.translate("UpdaterWindow", u"Image Tea Mini Updater", None))
        self.lblUpdateVersion.setText(QCoreApplication.translate("UpdaterWindow", u"Latest Version: ", None))
        self.lblCurrentVersion.setText(QCoreApplication.translate("UpdaterWindow", u"Current Version: ", None))
        self.lblUpdateMessage.setText(QCoreApplication.translate("UpdaterWindow", u"Checking for updates...", None))
        self.progressUpdate.setFormat("")
        self.progressUpdate.setStyleSheet(QCoreApplication.translate("UpdaterWindow", u"QProgressBar {\n"
"    border: 1px solid gray;\n"
"    border-radius: 3px;\n"
"    background-color: #f0f0f0;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #4CAF50;\n"
"    width: 10px;\n"
"}\n"
"QProgressBar::chunk:disabled {\n"
"    background-color: #aaaaaa;\n"
"}", None))
        self.checkBox.setText(QCoreApplication.translate("UpdaterWindow", u"Automatic check for update", None))
        self.btnCheck.setText(QCoreApplication.translate("UpdaterWindow", u"Check", None))
        self.btnUpdate.setText(QCoreApplication.translate("UpdaterWindow", u"Update Now", None))
        self.pushButton.setText(QCoreApplication.translate("UpdaterWindow", u"Close", None))
    # retranslateUi


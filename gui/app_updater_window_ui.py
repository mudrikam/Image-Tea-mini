# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app_updater_window.ui'
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

class Ui_AppUpdater(object):
    def setupUi(self, AppUpdater):
        if not AppUpdater.objectName():
            AppUpdater.setObjectName(u"AppUpdater")
        AppUpdater.resize(600, 400)
        self.verticalLayout = QVBoxLayout(AppUpdater)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lblTitle = QLabel(AppUpdater)
        self.lblTitle.setObjectName(u"lblTitle")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.lblTitle.setFont(font)
        self.lblTitle.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lblTitle)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.label = QLabel(AppUpdater)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)
        self.label.setTextFormat(Qt.RichText)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.progressBar = QProgressBar(AppUpdater)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout.addWidget(self.progressBar)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox = QCheckBox(AppUpdater)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout.addWidget(self.checkBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btnCancel = QPushButton(AppUpdater)
        self.btnCancel.setObjectName(u"btnCancel")

        self.horizontalLayout.addWidget(self.btnCancel)

        self.pushButton = QPushButton(AppUpdater)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(AppUpdater)
        self.btnCancel.clicked.connect(AppUpdater.reject)

        QMetaObject.connectSlotsByName(AppUpdater)
    # setupUi

    def retranslateUi(self, AppUpdater):
        AppUpdater.setWindowTitle(QCoreApplication.translate("AppUpdater", u"Image Tea Mini Updater", None))
        self.lblTitle.setText(QCoreApplication.translate("AppUpdater", u"Image Tea Mini Updater", None))
        self.label.setText(QCoreApplication.translate("AppUpdater", u"<html><body>\n"
"<p align=\"center\"><b>Update Information</b></p>\n"
"<p align=\"center\">This update will download version <b>%version%</b> (<i>%hash%</i>) from the remote repository.</p>\n"
"<p>What will happen:</p>\n"
"<ul>\n"
"  <li>All core application files will be replaced with the latest version</li>\n"
"  <li>Custom files you've added to the application folder will <b>not</b> be affected</li>\n"
"  <li>Any modifications to core application files will be overwritten</li>\n"
"</ul>\n"
"<p style=\"color: #cc0000;\"><b>WARNING:</b></p>\n"
"<ul style=\"color: #cc0000;\">\n"
"  <li>By proceeding with this update, you acknowledge that you understand and accept all risks involved</li>\n"
"  <li>The developer is not responsible for any data loss, software malfunction, or other issues that may arise</li>\n"
"  <li>Please ensure you have backups of any customized files or configurations before proceeding</li>\n"
"  <li>Once updated, you cannot automatically revert to the previous version</li>\n"
"</ul>\n"
"<p><"
                        "b>IMPORTANT:</b> All consequences of updating the application are solely your responsibility as the user.</p>\n"
"</body></html>", None))
        self.checkBox.setText(QCoreApplication.translate("AppUpdater", u"I understand all risks and accept full responsibility for any consequences of this update.", None))
        self.btnCancel.setText(QCoreApplication.translate("AppUpdater", u"Cancel", None))
        self.pushButton.setText(QCoreApplication.translate("AppUpdater", u"Proceed", None))
    # retranslateUi


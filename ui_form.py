# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitled.ui'
##
## Created by: Qt User Interface Compiler version 6.4.1
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
from PySide6.QtWidgets import (QApplication, QComboBox, QPushButton, QSizePolicy,
    QTextEdit, QWidget, QLabel)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(874, 566)
        
        # 添加情感显示标签
        self.sentimentLabel = QLabel(Form)
        self.sentimentLabel.setObjectName(u"sentimentLabel")
        self.sentimentLabel.setGeometry(QRect(710, 50, 131, 31))
        font = QFont()
        font.setPointSize(10)
        self.sentimentLabel.setFont(font)
        self.sentimentLabel.setAlignment(Qt.AlignCenter)
        
        self.sendButton = QPushButton(Form)
        self.sendButton.setObjectName(u"sendButton")
        self.sendButton.setGeometry(QRect(710, 380, 131, 71))
        self.score = QComboBox(Form)
        self.score.addItem("")
        self.score.addItem("")
        self.score.addItem("")
        self.score.addItem("")
        self.score.addItem("")
        self.score.setObjectName(u"score")
        self.score.setGeometry(QRect(710, 130, 131, 61))
        self.receiveEdit = QTextEdit(Form)
        self.receiveEdit.setObjectName(u"receiveEdit")
        self.receiveEdit.setGeometry(QRect(10, 50, 651, 301))
        self.receiveEdit.setReadOnly(True)
        self.sendEdit = QTextEdit(Form)
        self.sendEdit.setObjectName(u"sendEdit")
        self.sendEdit.setGeometry(QRect(10, 380, 651, 111))
        self.markButton = QPushButton(Form)
        self.markButton.setObjectName(u"markButton")
        self.markButton.setGeometry(QRect(710, 200, 141, 71))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"医疗问答系统", None))
        self.sendButton.setText(QCoreApplication.translate("Form", u"提交", None))
        self.score.setItemText(0, QCoreApplication.translate("Form", u"1", None))
        self.score.setItemText(1, QCoreApplication.translate("Form", u"2", None))
        self.score.setItemText(2, QCoreApplication.translate("Form", u"3", None))
        self.score.setItemText(3, QCoreApplication.translate("Form", u"4", None))
        self.score.setItemText(4, QCoreApplication.translate("Form", u"5", None))
        self.markButton.setText(QCoreApplication.translate("Form", u"提交上次回答的评分", None))
        self.sentimentLabel.setText(QCoreApplication.translate("Form", u"情感：", None))
    # retranslateUi

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'snowquery.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QSplitter, QTextEdit, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

from AnimatedToggle import AnimatedToggle
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        icon = QIcon()
        icon.addFile(u":/icons/snowflake.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName(u"actionNew")
        icon1 = QIcon(QIcon.fromTheme(u"document-new"))
        self.actionNew.setIcon(icon1)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon2 = QIcon(QIcon.fromTheme(u"document-open"))
        self.actionOpen.setIcon(icon2)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon3 = QIcon(QIcon.fromTheme(u"document-save"))
        self.actionSave.setIcon(icon3)
        self.actionSave_As = QAction(MainWindow)
        self.actionSave_As.setObjectName(u"actionSave_As")
        icon4 = QIcon(QIcon.fromTheme(u"document-save-as"))
        self.actionSave_As.setIcon(icon4)
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon5 = QIcon(QIcon.fromTheme(u"window-close"))
        self.actionQuit.setIcon(icon5)
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        icon6 = QIcon(QIcon.fromTheme(u"help-contents"))
        self.actionHelp.setIcon(icon6)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon7 = QIcon(QIcon.fromTheme(u"help-about"))
        self.actionAbout.setIcon(icon7)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setObjectName(u"splitter_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy1)
        self.splitter_2.setFrameShape(QFrame.Shape.NoFrame)
        self.splitter_2.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter_2)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.refresh_button = QPushButton(self.layoutWidget)
        self.refresh_button.setObjectName(u"refresh_button")
        self.refresh_button.setMaximumSize(QSize(25, 16777215))
        icon8 = QIcon(QIcon.fromTheme(u"view-refresh"))
        self.refresh_button.setIcon(icon8)

        self.horizontalLayout_2.addWidget(self.refresh_button)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.tree = QTreeWidget(self.layoutWidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree.setHeaderItem(__qtreewidgetitem)
        self.tree.setObjectName(u"tree")
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tree.setUniformRowHeights(True)
        self.tree.setHeaderHidden(True)

        self.verticalLayout.addWidget(self.tree)

        self.splitter_2.addWidget(self.layoutWidget)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        sizePolicy1.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy1)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.query_label = QLabel(self.layoutWidget1)
        self.query_label.setObjectName(u"query_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.query_label.sizePolicy().hasHeightForWidth())
        self.query_label.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.query_label)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.theme_switch = AnimatedToggle(self.layoutWidget1)
        self.theme_switch.setObjectName(u"theme_switch")

        self.horizontalLayout_3.addWidget(self.theme_switch)

        self.run_button = QPushButton(self.layoutWidget1)
        self.run_button.setObjectName(u"run_button")
        self.run_button.setMaximumSize(QSize(25, 16777215))

        self.horizontalLayout_3.addWidget(self.run_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.query_box = QTextEdit(self.layoutWidget1)
        self.query_box.setObjectName(u"query_box")
        font = QFont()
        font.setFamilies([u"Liberation Mono"])
        self.query_box.setFont(font)

        self.verticalLayout_3.addWidget(self.query_box)

        self.splitter.addWidget(self.layoutWidget1)
        self.layoutWidget2 = QWidget(self.splitter)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.layoutWidget2)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_2.addWidget(self.label_3)

        self.output_box = QTextEdit(self.layoutWidget2)
        self.output_box.setObjectName(u"output_box")
        self.output_box.setFont(font)
        self.output_box.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.output_box)

        self.splitter.addWidget(self.layoutWidget2)
        self.splitter_2.addWidget(self.splitter)

        self.verticalLayout_4.addWidget(self.splitter_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.status = QLineEdit(self.centralwidget)
        self.status.setObjectName(u"status")
        self.status.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.status.setReadOnly(True)

        self.horizontalLayout.addWidget(self.status)

        self.query_id = QLineEdit(self.centralwidget)
        self.query_id.setObjectName(u"query_id")
        self.query_id.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.query_id.sizePolicy().hasHeightForWidth())
        self.query_id.setSizePolicy(sizePolicy3)
        self.query_id.setMinimumSize(QSize(255, 0))
        self.query_id.setMaximumSize(QSize(255, 16777215))
        self.query_id.setReadOnly(True)

        self.horizontalLayout.addWidget(self.query_id)

        self.query_duration = QLineEdit(self.centralwidget)
        self.query_duration.setObjectName(u"query_duration")
        sizePolicy3.setHeightForWidth(self.query_duration.sizePolicy().hasHeightForWidth())
        self.query_duration.setSizePolicy(sizePolicy3)
        self.query_duration.setMinimumSize(QSize(84, 0))
        self.query_duration.setMaximumSize(QSize(84, 16777215))
        self.query_duration.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.query_duration.setReadOnly(True)

        self.horizontalLayout.addWidget(self.query_duration)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 20))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Snow Query", None))
        self.actionNew.setText(QCoreApplication.translate("MainWindow", u"&New", None))
#if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"&Open", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"&Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_As.setText(QCoreApplication.translate("MainWindow", u"Save &As...", None))
#if QT_CONFIG(shortcut)
        self.actionSave_As.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"&Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"&Help", None))
#if QT_CONFIG(shortcut)
        self.actionHelp.setShortcut(QCoreApplication.translate("MainWindow", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"&About", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Databases", None))
#if QT_CONFIG(tooltip)
        self.refresh_button.setToolTip(QCoreApplication.translate("MainWindow", u"Refresh", None))
#endif // QT_CONFIG(tooltip)
        self.refresh_button.setText("")
        self.query_label.setText(QCoreApplication.translate("MainWindow", u"New Query", None))
#if QT_CONFIG(tooltip)
        self.theme_switch.setToolTip(QCoreApplication.translate("MainWindow", u"Toggle between light and dark themes", None))
#endif // QT_CONFIG(tooltip)
        self.theme_switch.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
#if QT_CONFIG(tooltip)
        self.run_button.setToolTip(QCoreApplication.translate("MainWindow", u"Run (F5)", None))
#endif // QT_CONFIG(tooltip)
        self.run_button.setText(QCoreApplication.translate("MainWindow", u"\u25b6", None))
#if QT_CONFIG(shortcut)
        self.run_button.setShortcut(QCoreApplication.translate("MainWindow", u"F5", None))
#endif // QT_CONFIG(shortcut)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Output", None))
#if QT_CONFIG(tooltip)
        self.query_id.setToolTip(QCoreApplication.translate("MainWindow", u"Query Id", None))
#endif // QT_CONFIG(tooltip)
        self.query_id.setText("")
#if QT_CONFIG(tooltip)
        self.query_duration.setToolTip(QCoreApplication.translate("MainWindow", u"Query duration", None))
#endif // QT_CONFIG(tooltip)
        self.query_duration.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi


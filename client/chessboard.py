#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QPalette, QPixmap, QBrush, QApplication, QMainWindow, QWidget

import sys


class ChessboardWidget(QWidget):
    def __init__(self):
        super(ChessboardWidget, self).__init__()
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(
            QPixmap("./images/chessboard.png")))
        window.setPalette(palette)
        window.setWindowTitle("QMainWindow Background Image")
        window.show()
        app.exec_()

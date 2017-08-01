import sip
sip.setapi('QString', 2)

import sys

from PyQt4 import QtCore, QtGui

class Gomoku(QtGui.QMainWindow):

	def __init__(self):
		pass



if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	
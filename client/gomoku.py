import sip
sip.setapi('QString', 2)

import sys

from PyQt4 import QtCore, QtGui

class Gomoku(QtGui.QMainWindow):

	def __init__(self):
		w = QtGui.QWidget()
   		b = QtGui.QLabel(w)
   		b.setText("Hello World!")
   		w.setGeometry(100,100,200,50)
   		b.move(50,20)
   		w.setWindowTitle(“PyQt”)
   		w.show()
   


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	sys.exit(app.exec_())


import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from view.gamelist_widget import GameListWidget
from controller.game_controller import GameController

game_controller = GameController()

app = QApplication(sys.argv)
widget = GameListWidget()
c = game_controller.get_client()
c.connect()
game_controller.add_polling_game_list_task()
game_controller.get_game_list()
widget.show()
sys.exit(app.exec_())


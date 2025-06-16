# Imports #
from Classes.Menu import MenuBase


class ConfigureScreen(MenuBase):
	def __init__(self,**kwargs):
		super(ConfigureScreen,self).__init__(**kwargs)

		self.protocol = '4-hPRL'

		# self.button_constructor(self.protocol)
		self.menu_back_start_screen(self.protocol)
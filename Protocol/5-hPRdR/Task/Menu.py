# Imports
from Classes.Menu import MenuBase

# TextInput(text="Test",id="Test1")


class ConfigureScreen(MenuBase):
	def __init__(self, **kwargs):
		super(ConfigureScreen, self).__init__(**kwargs)
		self.protocol = '5-hPRdR'
		
		# self.button_constructor(self.protocol)
		self.menu_back_start_screen(self.protocol)

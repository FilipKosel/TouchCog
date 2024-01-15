from Classes.Menu import MenuBase

class ConfigureScreen(MenuBase):
    def __init__(self, **kwargs):
        super(ConfigureScreen, self).__init__(**kwargs)

        self.protocol = 'iCPT2GStim1'

        self.menu_constructor(self.protocol)

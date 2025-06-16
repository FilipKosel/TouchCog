# Imports #
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton
from Classes.Menu import MenuBase


class ConfigureScreen(MenuBase):
	def __init__(self,**kwargs):
		super(ConfigureScreen,self).__init__(**kwargs)
		self.protocol = '2-TUNL'
		# self.correction_dropdown = DropDown()
		# self.correction_button = Button(text='Correction Trials Disabled')
		# self.correction_list = ['Correction Trials Enabled', 'Correction Trials Disabled']
		# for correction in self.correction_list:
		# 	corrections_opt = Button(text=correction, size_hint_y=None, height=100)
		# 	corrections_opt.bind(on_release=lambda corrections_opt: self.correction_dropdown.select(corrections_opt.text))
		# 	self.correction_dropdown.add_widget(corrections_opt)
		# self.correction_button.bind(on_release=self.correction_dropdown.open)
		# self.correction_dropdown.bind(on_select=lambda instance, x: setattr(self.correction_button, 'text', x))
		
		# self.correction_toggle_off = ToggleButton(text='Correction Trials Off'
		# 										 ,group='correction'
		# 										 ,state='down'
		# 										 )
		
		# self.correction_toggle_on = ToggleButton(text='Correction Trials On'
		# 										 ,group='correction'
		# 										 )
		
		# self.correction_toggle_off.bind(on_press=self.correction_off)
		# self.correction_toggle_on.bind(on_press=self.correction_on)
		
		# self.settings_widgets.append(Label(text='Correction Trials'))
		# self.settings_widgets.append(self.correction_button)
		
		# self.settings_widgets.append(self.correction_toggle_off)
		# self.settings_widgets.append(self.correction_toggle_on)
	
		# self.button_constructor(self.protocol)
		self.menu_back_start_screen(self.protocol)
		
	
	def correction_off(self, instance, **kwargs):
		
		if instance.state == 'down':
			setattr(self.correction_button, 'text', 'Correction Trials Disabled')
	
		
	def correction_on(self, instance, **kwargs):
		
		if instance.state == 'down':
			setattr(self.correction_button, 'text', 'Correction Trials Enabled')
			
		
		

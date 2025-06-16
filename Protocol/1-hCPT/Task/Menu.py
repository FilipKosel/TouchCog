from Classes.Menu import MenuBase
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton

class ConfigureScreen(MenuBase):
	def __init__(self, **kwargs):
		super(ConfigureScreen, self).__init__(**kwargs)

		self.protocol = '1-hCPT'


		# self.age_label = Label(text='Please select your age range', font_size='60sp')
		# # self.age_label.size_hint = (0.85, 0.05)
		# # self.age_label.pos_hint = {'center_x': 0.5, 'center_y': 0.925}

		# self.age_range = ''

		# self.start_button_present = False

		# self.button_24 = ToggleButton(text='24 and below', font_size='60sp')
		# self.button_25 = ToggleButton(text='25-34', font_size='60sp')
		# self.button_35 = ToggleButton(text='35-44', font_size='60sp')
		# self.button_45 = ToggleButton(text='45-54', font_size='60sp')
		# self.button_55 = ToggleButton(text='55-64', font_size='60sp')
		# self.button_65 = ToggleButton(text='65-74', font_size='60sp')
		# self.button_75 = ToggleButton(text='75 and above', font_size='60sp')
		# self.button_na = ToggleButton(text='Prefer not to answer', font_size='60sp')
		
		# self.button_24.bind(on_press=self.age_button_callback)
		# self.button_25.bind(on_press=self.age_button_callback)
		# self.button_35.bind(on_press=self.age_button_callback)
		# self.button_45.bind(on_press=self.age_button_callback)
		# self.button_55.bind(on_press=self.age_button_callback)
		# self.button_65.bind(on_press=self.age_button_callback)
		# self.button_75.bind(on_press=self.age_button_callback)
		# self.button_na.bind(on_press=self.age_button_callback)

		# self.button_24.group = 'Age'
		# self.button_25.group = 'Age'
		# self.button_35.group = 'Age'
		# self.button_45.group = 'Age'
		# self.button_55.group = 'Age'
		# self.button_65.group = 'Age'
		# self.button_75.group = 'Age'
		# self.button_na.group = 'Age'


		# self.button_list = [
		#	 self.age_label
		#	 , self.button_24
		#	 , self.button_25
		#	 , self.button_35
		#	 , self.button_45
		#	 , self.button_55
		#	 , self.button_65
		#	 , self.button_75
		#	 , self.button_na
		#	 ]
		

		# self.setting_gridlayout.rows = len(self.button_list)
		# self.setting_gridlayout.cols = 1
		# self.setting_scrollview.size_hint = (0.85, 0.8)
		# self.setting_scrollview.pos_hint = {"center_x": 0.5, "center_y": 0.575}


		# for button in self.button_list:
		#	 self.setting_gridlayout.add_widget(button)
		#	 # self.setting_gridlayout.add_widget(Label(text=self.parameters_demographics[iParam]))
		# # for wid in self.settings_widgets:
		# #	 self.setting_gridlayout.add_widget(wid)
		# self.setting_scrollview.add_widget(self.setting_gridlayout)
		# self.main_layout.add_widget(self.setting_scrollview)

#		 self.main_task_dropdown = DropDown()
#		 self.main_task_button = Button(text='Enabled')
#		 self.main_task_list = ['Enabled', 'Disabled']
#		 for option in self.main_task_list:
#			 main_task_opt = Button(text=option, size_hint_y=None, height=100)
#			 main_task_opt.bind(
#				 on_release=lambda main_task_opt: self.main_task_dropdown.select(stim_duration_opt.text))
#			 self.main_task_dropdown.add_widget(main_task_opt)
#		 self.main_task_button.bind(on_release=self.main_task_dropdown.open)
#		 self.main_task_dropdown.bind(
#			 on_select=lambda instance, x: setattr(self.main_task_button, 'text', x))
#		 self.settings_widgets.append(Label(text='Main Task'))
#		 self.settings_widgets.append(self.main_task_button)
#		 
#		 
#		 self.stim_duration_probe_dropdown = DropDown()
#		 self.stim_duration_probe_button = Button(text='Enabled')
#		 self.stim_duration_probe_list = ['Enabled','Disabled']
#		 for option in self.stim_duration_probe_list:
#			 stim_duration_opt = Button(text=option, size_hint_y=None,height=100)
#			 stim_duration_opt.bind(on_release=lambda stim_duration_opt: self.stim_duration_probe_dropdown.select(stim_duration_opt.text))
#			 self.stim_duration_probe_dropdown.add_widget(stim_duration_opt)
#		 self.stim_duration_probe_button.bind(on_release=self.stim_duration_probe_dropdown.open)
#		 self.stim_duration_probe_dropdown.bind(on_select=lambda instance, x: setattr(self.stim_duration_probe_button, 'text', x))
#		 self.settings_widgets.append(Label(text='Stimulus Duration Probe'))
#		 self.settings_widgets.append(self.stim_duration_probe_button)
#		 
#		 self.flanker_probe_dropdown = DropDown()
#		 self.flanker_probe_button = Button(text='Enabled')
#		 self.flanker_probe_list = ['Enabled','Disabled']
#		 for option in self.flanker_probe_list:
#			 flanker_opt = Button(text=option, size_hint_y=None,height=100)
#			 flanker_opt.bind(on_release=lambda flanker_opt: self.flanker_probe_dropdown.select(flanker_opt.text))
#			 self.flanker_probe_dropdown.add_widget(flanker_opt)
#		 self.flanker_probe_button.bind(on_release=self.flanker_probe_dropdown.open)
#		 self.flanker_probe_dropdown.bind(on_select=lambda instance, x: setattr(self.flanker_probe_button, 'text', x))
#		 self.settings_widgets.append(Label(text='Flanker Probe'))
#		 self.settings_widgets.append(self.flanker_probe_button)
# 
#		 self.probability_probe_dropdown = DropDown()
#		 self.probability_probe_button = Button(text='Enabled')
#		 self.probability_probe_list = ['Enabled', 'Disabled']
#		 for option in self.probability_probe_list:
#			 probability_opt = Button(text=option, size_hint_y=None, height=100)
#			 probability_opt.bind(on_release=lambda probability_opt: self.probability_probe_dropdown.select(probability_opt.text))
#			 self.probability_probe_dropdown.add_widget(probability_opt)
#		 self.probability_probe_button.bind(on_release=self.probability_probe_dropdown.open)
#		 self.probability_probe_dropdown.bind(on_select=lambda instance, x: setattr(self.probability_probe_button, 'text', x))
#		 self.settings_widgets.append(Label(text='Probability Probe'))
#		 self.settings_widgets.append(self.probability_probe_button)
# 
#		 self.SART_probe_dropdown = DropDown()
#		 self.SART_probe_button = Button(text='Enabled')
#		 self.SART_probe_list = ['Enabled', 'Disabled']
#		 for option in self.SART_probe_list:
#			 SART_opt = Button(text=option, size_hint_y=None, height=100)
#			 SART_opt.bind(on_release=lambda SART_opt: self.SART_probe_dropdown.select(SART_opt.text))
#			 self.SART_probe_dropdown.add_widget(SART_opt)
#		 self.SART_probe_button.bind(on_release=self.SART_probe_dropdown.open)
#		 self.SART_probe_dropdown.bind(on_select=lambda instance, x: setattr(self.SART_probe_button, 'text', x))
#		 self.settings_widgets.append(Label(text='SART Probe'))
#		 self.settings_widgets.append(self.SART_probe_button)

		# self.menu_constructor(self.protocol)
		# self.demographics_constructor(self.protocol)
		# self.button_constructor(self.protocol)
		self.menu_back_start_screen(self.protocol)

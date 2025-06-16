from kivy.uix.screenmanager import Screen, ScreenManagerException
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# from pathlib import Path
import pathlib

import sys
import os
import importlib
import importlib.util
import configparser

class MenuBase(Screen):
	def __init__(self, **kwargs):
		super(MenuBase, self).__init__(**kwargs)
		self.name = 'menuscreen'
		self.main_layout = FloatLayout()

		if sys.platform == 'linux' or sys.platform == 'darwin':
			self.folder_mod = '/'
		elif sys.platform == 'win32':
			self.folder_mod = '\\'

		self.protocol_name = ''
		self.protocol_path = ''
		self.parameters_config = dict()
		self.setting_scrollview = ScrollView()
		self.setting_gridlayout = GridLayout()

		self.language_dropdown = DropDown()
		self.dropdown_main = Button(text='Select Language')
		self.language_list = ['English', 'French']
		for language in self.language_list:
			lang_button = Button(text=language, size_hint_y=None, height=100)
			lang_button.bind(on_release=lambda lang_button: self.language_dropdown.select(lang_button.text))
			self.language_dropdown.add_widget(lang_button)
		self.dropdown_main.bind(on_release=self.language_dropdown.open)
		self.language_dropdown.bind(on_select=lambda instance, x: setattr(self.dropdown_main, 'text', x))

		self.id_grid = GridLayout(cols=2, rows=1)
		self.id_label = Label(text='Participant ID', font_size='24sp')
		self.id_entry = TextInput(text='Default', font_size='32sp')
		self.id_grid.add_widget(self.id_label)
		self.id_grid.add_widget(self.id_entry)
		self.id_grid.size_hint = (0.85, 0.03)
		self.id_grid.pos_hint = {'center_x': 0.5, 'center_y': 0.125}

		self.age_range = ''

		self.back_button = Button(text="Back", font_size='60sp')
		self.back_button.size_hint = (0.3,0.1)
		self.back_button.pos_hint = {"center_x": 0.25, "center_y": 0.08}
		self.back_button.bind(on_press=self.return_menu)

		self.start_button = Button(text="Start Task", font_size='60sp')
		self.start_button.size_hint = (0.3, 0.1)
		self.start_button.pos_hint = {"center_x": 0.75, "center_y": 0.08}
		self.start_button.bind(on_press=self.start_protocol)

		self.settings_widgets = [Label(text='Language'), self.dropdown_main]

	def start_protocol(self, *args):

		def lazy_import(protocol):
			
			mod_dir = str(pathlib.Path('Protocol', protocol, 'Task', 'Protocol.py'))

			# cwd = os.getcwd()
			# working = cwd + '\\Protocol\\' + protocol + '\\Task\\Protocol.py'
			mod_name = 'Protocol'
			mod_spec = importlib.util.spec_from_file_location(mod_name, mod_dir)
			mod_loader = importlib.util.LazyLoader(mod_spec.loader)
			mod_spec.loader = mod_loader
			module = importlib.util.module_from_spec(mod_spec)
			sys.modules[mod_name] = module
			mod_loader.exec_module(module)
			return module
		
		task_module = lazy_import(self.protocol)
		protocol_task_screen = task_module.ProtocolScreen(screen_resolution=self.size)
		

		try:
			self.manager.remove_widget(self.manager.get_screen('protocolscreen'))
			self.manager.add_widget(protocol_task_screen)
		except ScreenManagerException:
			self.manager.add_widget(protocol_task_screen)


		key = ''
		value = ''

		# parameter_dict = self.parameters_config

		parameter_dict = self.parameters_dict

		# config_file = str(pathlib.Path('Protocol', self.protocol, 'Configuration.ini'))



		# parameter_dict = {}
		# for widget in self.setting_gridlayout.walk():
		#	 if isinstance(widget, Label) and not isinstance(widget, Button):
		#		 key = widget.text
		#		 key = key.lower()
		#		 key = key.replace(' ','_')
		#	 elif isinstance(widget, TextInput):
		#		 value = widget.text
		#		 parameter_dict[key] = value
		#	 elif isinstance(widget, Button):
		#		 value = widget.text
		#		 parameter_dict[key] = value
		parameter_dict['participant_id'] = self.id_entry.text
		parameter_dict['age_range'] = self.age_range

		if self.dropdown_main.text == 'Select Language':
			parameter_dict['language'] = 'English'
		else:
			parameter_dict['language'] = self.dropdown_main.text

		protocol_task_screen.load_parameters(parameter_dict)

		self.manager.current = 'protocolscreen'

	def return_menu(self, *args):
		self.manager.current = 'protocolmenu'

	def menu_constructor(self, protocol_name):
		self.protocol_name = protocol_name
		self.protocol_path = os.getcwd() + self.folder_mod + 'Protocol' + self.folder_mod + self.protocol_name
		config_path = self.protocol_path + self.folder_mod + 'Configuration.ini'
		config_file = configparser.ConfigParser()
		config_file.read(config_path)

		if ('DebugParameters' in config_file) \
			and (int(config_file['DebugParameters']['debug_mode']) == 1):
			self.parameters_dict = config_file['DebugParameters']
		else:
			self.parameters_dict = config_file['TaskParameters']
			
		num_parameters = len(self.parameters_config)
		self.setting_gridlayout.rows = (num_parameters + int(len(self.settings_widgets) / 2))
		self.setting_gridlayout.cols = 2
		self.setting_scrollview.size_hint = (0.85, 0.8)
		self.setting_scrollview.pos_hint = {"center_x": 0.5, "center_y": 0.55}

		for parameter in self.parameters_config:
			self.setting_gridlayout.add_widget(Label(text=parameter))
			self.setting_gridlayout.add_widget(TextInput(text=self.parameters_config[parameter]))
		for wid in self.settings_widgets:
			self.setting_gridlayout.add_widget(wid)
		self.setting_scrollview.add_widget(self.setting_gridlayout)
		self.main_layout.add_widget(self.setting_scrollview)
		self.main_layout.add_widget(self.id_grid)
		self.main_layout.add_widget(self.back_button)
		self.main_layout.add_widget(self.start_button)
		self.add_widget(self.main_layout)



	def checkbox_constructor(self, protocol_name):
		self.protocol_name = protocol_name
		self.protocol_path = os.getcwd() + self.folder_mod + 'Protocol' + self.folder_mod + self.protocol_name
		# config_path = self.protocol_path + self.folder_mod + 'Demographics.ini'
		# config_file = configparser.ConfigParser()
		# config_file.read(config_path)
		# self.parameters_config = config_file['TaskParameters']
		self.parameters_demographics = ['24 or under', '25-34', '35-44', '45-54', '55-64', '65-75', '75 or over', 'Prefer not to answer']
		num_parameters = len(self.parameters_demographics)
		self.setting_gridlayout.rows = num_parameters
		self.setting_gridlayout.cols = 2
		self.setting_scrollview.size_hint = (0.85, 0.8)
		self.setting_scrollview.pos_hint = {"center_x": 0.5, "center_y": 0.55}

		self.checkbox_24 = CheckBox()
		self.checkbox_25 = CheckBox()
		self.checkbox_35 = CheckBox()
		self.checkbox_45 = CheckBox()
		self.checkbox_55 = CheckBox()
		self.checkbox_65 = CheckBox()
		self.checkbox_75 = CheckBox()
		self.checkbox_na = CheckBox()

		self.checkbox_24.group = 'Age'
		self.checkbox_25.group = 'Age'


		self.checkbox_list = [self.checkbox_24, self.checkbox_25, self.checkbox_35, self.checkbox_45, self.checkbox_55, self.checkbox_65, self.checkbox_75, self.checkbox_na]


		for iParam in range(len(self.parameters_demographics)):
			self.setting_gridlayout.add_widget(self.checkbox_list[iParam])
			self.setting_gridlayout.add_widget(Label(text=self.parameters_demographics[iParam]))
		# for wid in self.settings_widgets:
		#	 self.setting_gridlayout.add_widget(wid)
		self.setting_scrollview.add_widget(self.setting_gridlayout)
		self.main_layout.add_widget(self.setting_scrollview)
		self.main_layout.add_widget(self.id_grid)
		self.main_layout.add_widget(self.back_button)
		self.main_layout.add_widget(self.start_button)
		self.add_widget(self.main_layout)
	


	def age_button_callback(self, instance):

		self.age_range = instance.text
		# print('The button pressed is: <%s>' % instance)
		# print('The button text is: %s' % instance.text)
		# print('The value of self.age_range is: ', self.age_range)

		if not self.start_button_present:
			self.main_layout.add_widget(self.start_button)
			self.start_button_present = True




	def button_constructor(self, protocol_name):
		self.protocol_name = protocol_name
		self.protocol_path = os.getcwd() + self.folder_mod + 'Protocol' + self.folder_mod + self.protocol_name
		config_path = self.protocol_path + self.folder_mod + 'Configuration.ini'
		config_file = configparser.ConfigParser()
		config_file.read(config_path)

		if ('DebugParameters' in config_file) \
			and (int(config_file['DebugParameters']['debug_mode']) == 1):
			self.parameters_dict = config_file['DebugParameters']
		else:
			self.parameters_dict = config_file['TaskParameters']
		
		# self.parameters_demographics = ['24 or under', '25-34', '35-44', '45-54', '55-64', '65-75', '75 or over', 'Prefer not to answer']
		# num_parameters = len(self.parameters_demographics)

		self.age_label = Label(text='Please select your age range', font_size='60sp')
		# self.age_label.size_hint = (0.85, 0.05)
		# self.age_label.pos_hint = {'center_x': 0.5, 'center_y': 0.925}

		self.age_range = 'NA'
		self.start_button_present = True

		self.button_24 = ToggleButton(text='24 and below', font_size='60sp')
		self.button_25 = ToggleButton(text='25-34', font_size='60sp')
		self.button_35 = ToggleButton(text='35-44', font_size='60sp')
		self.button_45 = ToggleButton(text='45-54', font_size='60sp')
		self.button_55 = ToggleButton(text='55-64', font_size='60sp')
		self.button_65 = ToggleButton(text='65-74', font_size='60sp')
		self.button_75 = ToggleButton(text='75 and above', font_size='60sp')
		self.button_na = ToggleButton(text='Prefer not to answer', font_size='60sp')
		
		self.button_24.bind(on_press=self.age_button_callback)
		self.button_25.bind(on_press=self.age_button_callback)
		self.button_35.bind(on_press=self.age_button_callback)
		self.button_45.bind(on_press=self.age_button_callback)
		self.button_55.bind(on_press=self.age_button_callback)
		self.button_65.bind(on_press=self.age_button_callback)
		self.button_75.bind(on_press=self.age_button_callback)
		self.button_na.bind(on_press=self.age_button_callback)

		self.button_24.group = 'Age'
		self.button_25.group = 'Age'
		self.button_35.group = 'Age'
		self.button_45.group = 'Age'
		self.button_55.group = 'Age'
		self.button_65.group = 'Age'
		self.button_75.group = 'Age'
		self.button_na.group = 'Age'


		self.button_list = [
			self.age_label
			, self.button_24
			, self.button_25
			, self.button_35
			, self.button_45
			, self.button_55
			, self.button_65
			, self.button_75
			, self.button_na
			]
		

		self.setting_gridlayout.rows = len(self.button_list)
		self.setting_gridlayout.cols = 1
		self.setting_scrollview.size_hint = (0.85, 0.8)
		self.setting_scrollview.pos_hint = {"center_x": 0.5, "center_y": 0.5375}
		
		self.id_grid.size_hint = (0.85, 0.05)
		self.id_grid.pos_hint = {'center_x': 0.5, 'center_y': 0.9625}

		
		self.back_button.pos_hint = {"center_x": 0.25, "center_y": 0.0625}
		self.start_button.pos_hint = {"center_x": 0.75, "center_y": 0.0625}


		for button in self.button_list:
			self.setting_gridlayout.add_widget(button)
			# self.setting_gridlayout.add_widget(Label(text=self.parameters_demographics[iParam]))
		# for wid in self.settings_widgets:
		#	 self.setting_gridlayout.add_widget(wid)
		self.setting_scrollview.add_widget(self.setting_gridlayout)
		self.main_layout.add_widget(self.setting_scrollview)
		# self.main_layout.add_widget(self.id_grid)
		self.main_layout.add_widget(self.back_button)
		self.main_layout.add_widget(self.start_button)
		self.add_widget(self.main_layout)

		# self.start_protocol()






	def menu_back_start_screen(self, protocol_name):

		self.protocol_name = protocol_name
		self.protocol_path = os.getcwd() + self.folder_mod + 'Protocol' + self.folder_mod + self.protocol_name
		config_path = self.protocol_path + self.folder_mod + 'Configuration.ini'
		config_file = configparser.ConfigParser()
		config_file.read(config_path)

		if ('DebugParameters' in config_file) \
			and (int(config_file['DebugParameters']['debug_mode']) == 1):
			self.parameters_dict = config_file['DebugParameters']
		else:
			self.parameters_dict = config_file['TaskParameters']
		
		# self.parameters_demographics = ['24 or under', '25-34', '35-44', '45-54', '55-64', '65-75', '75 or over', 'Prefer not to answer']
		# num_parameters = len(self.parameters_demographics)

		# self.age_label = Label(text='Please select your age range', font_size='60sp')
		# self.age_label.size_hint = (0.85, 0.05)
		# self.age_label.pos_hint = {'center_x': 0.5, 'center_y': 0.925}

		self.age_range = 'NA'
		self.start_button_present = True

		# self.setting_gridlayout.rows = len(self.button_list)
		# self.setting_gridlayout.cols = 1
		# self.setting_scrollview.size_hint = (0.85, 0.8)
		# self.setting_scrollview.pos_hint = {"center_x": 0.5, "center_y": 0.7}
		
		self.id_grid.size_hint = (0.85, 0.1)
		self.id_grid.pos_hint = {'center_x': 0.5, 'center_y': 0.7}

		
		self.back_button.pos_hint = {"center_x": 0.25, "center_y": 0.3}
		self.start_button.pos_hint = {"center_x": 0.75, "center_y": 0.3}


		# for button in self.button_list:
		#	 self.setting_gridlayout.add_widget(button)
			# self.setting_gridlayout.add_widget(Label(text=self.parameters_demographics[iParam]))
		# for wid in self.settings_widgets:
		#	 self.setting_gridlayout.add_widget(wid)
		# self.setting_scrollview.add_widget(self.setting_gridlayout)
		# self.main_layout.add_widget(self.setting_scrollview)
		self.main_layout.add_widget(self.id_grid)
		self.main_layout.add_widget(self.back_button)
		self.main_layout.add_widget(self.start_button)
		self.add_widget(self.main_layout)

		# self.start_protocol()

# Import
import pandas as pd
import configparser
import datetime
import sys
import os
import time
import threading
import pathlib

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.video import Video as CoreVideo
from kivy.core.video import VideoBase
from kivy.core.window import Window
from kivy.loader import Loader
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.effectwidget import EffectWidget, EffectBase
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.video import Video

from pathlib import Path





class ImageButton(ButtonBehavior, Image):



	def __init__(self, **kwargs):
		super(ImageButton, self).__init__(**kwargs)
		self.coord = None
		self.fit_mode = 'fill'
		self.touch_pos = (0, 0)
		self.name = ''




class FloatLayoutLog(FloatLayout):



	def __init__(self, screen_resolution, **kwargs):
		super(FloatLayoutLog, self).__init__(**kwargs)
		self.app = App.get_running_app()
		self.touch_pos = [0, 0]
		self.last_recorded_pos = [0,0]
		self.width = screen_resolution[0]
		self.height = screen_resolution[1]
		self.width_min = self.width / 100
		self.height_min = self.height / 100
		self.held_name = ''
		self.event_columns = [ # Event types: State Change, Variable Change, Object Display, Object Remove
			'Time'
			, 'Event_Type'
			, 'Event_Name'
			, 'Arg1_Name'
			, 'Arg1_Value'
			, 'Arg2_Name'
			, 'Arg2_Value'
			, 'Arg3_Name'
			, 'Arg3_Value'
			]
		# self.event_dataframe = pd.DataFrame(columns=self.event_columns)
		# self.app.session_event_data = self.event_dataframe
		self.app.session_event_data = pd.DataFrame(columns=self.event_columns)
		self.event_index = 0
		self.save_path = ''
		self.elapsed_time = 0
		self.touch_time = 0
		self.start_time = 0
	

	
	def filter_children(self,string):
		return


	
	def on_touch_down(self, touch):
		self.touch_pos = touch.pos
		self.touch_time = time.time() - self.start_time
		if self.disabled and self.collide_point(*touch.pos):
			return True
		for child in self.children:
			if child.dispatch('on_touch_down', touch):
				if isinstance(child, ImageButton):
					self.held_name = child.name
				else:
					self.held_name = ''
				threading.Thread(target=self.add_event,args=([self.touch_time, 'Screen', 'Touch Press', 'X Position', self.touch_pos[0],
								'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name],), daemon=False).start()
				#self.add_event([self.touch_time, 'Screen', 'Touch Press', 'X Position', self.touch_pos[0],
								#'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name])
				return True
		self.held_name = ''
		threading.Thread(target=self.add_event,args=([self.touch_time, 'Screen', 'Touch Press', 'X Position',
						self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name],)).start()
		#add_thread.start()
		#self.add_event([self.touch_time, 'Screen', 'Touch Press', 'X Position',
						#self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name])
	
	
	
	def on_touch_move(self, touch):
		self.touch_pos = touch.pos
		self.touch_time = time.time() - self.start_time
		if self.disabled:
			return
		for child in self.children:
			if child.dispatch('on_touch_move', touch):
				if isinstance(child, ImageButton):
					self.held_name = child.name
				else:
					self.held_name = ''
				if (abs(self.touch_pos[0] - self.last_recorded_pos[0]) >= self.width_min) or (abs(self.touch_pos[1] - self.last_recorded_pos[1]) >= self.height_min):
					self.last_recorded_pos = self.touch_pos
					threading.Thread(target=self.add_event,args=([self.touch_time, 'Screen', 'Touch Move', 'X Position',
							self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name],)).start()
				#self.add_event([self.touch_time, 'Screen', 'Touch Move', 'X Position',
								#self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name])
				return True
		self.held_name = ''
		if (abs(self.touch_pos[0] - self.last_recorded_pos[0]) >= self.width_min) or (abs(self.touch_pos[1] - self.last_recorded_pos[1]) >= self.height_min):
			self.last_recorded_pos = self.touch_pos
			threading.Thread(target=self.add_event,args=([self.touch_time, 'Screen', 'Touch Move', 'X Position',
					self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name],)).start()
		#self.add_event([self.touch_time, 'Screen', 'Touch Press', 'X Position',
						#self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name])
	
	
	
	def on_touch_up(self, touch):
		self.touch_pos = touch.pos
		self.touch_time = time.time() - self.start_time
		if self.disabled:
			return
		for child in self.children:
			if child.dispatch('on_touch_up', touch):
				if isinstance(child, ImageButton):
					self.held_name = child.name
				else:
					self.held_name = ''
				threading.Thread(target=self.add_event,args=([self.touch_time, 'Screen', 'Touch Release', 'X Position',
								self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name],)).start()
				#self.add_event([self.touch_time, 'Screen', 'Touch Release', 'X Position',
								#self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name])
				return True
		self.held_name = ''
		threading.Thread(target=self.add_event,args=([self.touch_time, 'Screen', 'Touch Release', 'X Position',
						self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name],)).start()
		#self.add_event([self.touch_time, 'Screen', 'Touch Release', 'X Position',
						#self.touch_pos[0], 'Y Position', self.touch_pos[1], 'Stimulus Name', self.held_name])
		if self.held_name != '':
			self.held_name = ''
	
	
	
	# def add_event(self, row, *args):
		
	# 	while len(row) < len(self.event_columns):
			
	# 		row.append('')
		
	# 	row_df = pd.DataFrame(columns = self.event_columns)
	# 	row_df.loc[0] = row
		
	# 	self.app.session_event_data = pd.concat([self.app.session_event_data,row_df])
	
	
	
	def add_event(self, row, *args):

		row_df = pd.DataFrame(columns=self.event_columns)
		new_row = {}
		
		for iCol in range(len(self.event_columns)):

			if iCol >= len(row):

				new_row[self.event_columns[iCol]] = ''
			
			else:

				new_row[self.event_columns[iCol]] = str(row[iCol])
		

		row_df.loc[0] = new_row
		
		self.app.session_event_data = pd.concat([self.app.session_event_data,row_df])

		return
	
	# Add event - revised "standard" format for events
		
		# self.protocol_floatlayout.add_event([
		# 	(self.stimulus_start_time - self.start_time)
		# 	, 'State Change'		# Indicates change of program state (e.g., object display, object remove, block change)
		# 	, 'Object Display'		# Current labels: Object Display; Object Remove; Premature Response; Stimulus Response; Hold Remove; Section Start; Session End; Block End
		# 	])

		# self.protocol_floatlayout.add_event([
		# 	(self.response_time - self.start_time)
		# 	, 'State Change'
		# 	, 'Stimulus Response'
		# 	])

		# self.protocol_floatlayout.add_event([
		# 	(self.stimulus_press_time - self.start_time)
		# 	, 'State Change'
		# 	, 'No Stimulus Press'
		# 	])
		
		# self.protocol_floatlayout.add_event([
		# 	(self.stimulus_start_time - self.start_time)
		# 	, 'Object Display'		# Indicates object displayed on screen (e.g., image, button, text)
		# 	, 'Stimulus'			# Object type (Stimulus; Button; Text)
		# 	, 'Center'				# Object name (e.g., stimulus name, instructions, feedback)
		# 	, 'Center'				# Object position
		# 	, 'Image Name'			# Other object parameter labels
		# 	, self.center_image		# Other object parameter values
		# 	])
		
		# self.protocol_floatlayout.add_event([
		# 	(self.stimulus_press_time - self.start_time)
		# 	, 'Object Remove'		# Indicates object removed from screen (e.g., image, button, text)
		# 	, 'Stimulus'			# Object type (Stimulus; Button; Text)
		# 	, 'Center'				# Object name (e.g., stimulus name, instructions, feedback)
		# 	, 'Center'				# Object position
		# 	, 'Image Name'			# Other object parameter labels
		# 	, self.center_image		# Other object parameter values
		# 	])
		
		# self.protocol_floatlayout.add_event([
		# 	(time.time() - self.start_time)
		# 	, 'Variable Change'		# Change in variable
		# 	, 'Outcome'				# "Outcome" for output; "Parameter" for task parameter
		# 	, 'Trial Contingency'	# Variable label
		# 	, self.contingency		# Variable value
		# 	])

		# self.protocol_floatlayout.add_event([
		# 	(time.time() - self.start_time)
		# 	, 'Variable Change'
		# 	, 'Parameter'
		# 	, 'Staircasing'
		# 	, 'Increase'
		# 	])

		# self.protocol_floatlayout.add_event([
		# 	(time.time() - self.start_time)
		# 	, 'Variable Change'
		# 	, 'Outcome'
		# 	, 'Similarity'
		# 	, self.outcome_value
		# 	, 'Type'
		# 	, 'Mode'
		# 	])
	
	
	
	def write_data(self):
		self.app.session_event_data = self.app.session_event_data.sort_values(by=['Time'])
		self.app.session_event_data.to_csv(self.app.session_event_path, index=False)
	
	
	
	def update_path(self, path):
		self.save_path = path
		self.app.session_event_path = self.save_path
	



class ProtocolBase(Screen):



	def __init__(self, screen_resolution, **kwargs):
	
		super(ProtocolBase, self).__init__(**kwargs)
	
		self.name = 'protocolscreen'
	
		if sys.platform == 'linux' or sys.platform == 'darwin':
	
			self.folder_mod = '/'
	
		elif sys.platform == 'win32':
	
			self.folder_mod = '\\'
		
		config_path = pathlib.Path(os.getcwd(), 'Screen.ini')
		config_file = configparser.ConfigParser()
		config_file.read(config_path, encoding = 'utf-8')
		
		width = int(Config.get('graphics', 'width'))
		height = int(Config.get('graphics', 'height'))
		
		print(width)
		print(height)
		
		self.screen_resolution = (width, height)
		
		print(self.screen_resolution)
		
# 		self.screen_ratio = 1
		
		if width > height:
			
			self.width_adjust = height / width
			self.height_adjust = 1
		
		elif height < width:
			
			self.width_adjust = 1
			self.height_adjust = width / height
		
		else:
			
			self.width_adjust = 1
			self.height_adjust = 1
		
		# fullscreen = config_file['Screen']['fullscreen']
# 		print(fullscreen)
# 		
# 		x_dim = 0
# 		y_dim = 0
# 		
# 		if (fullscreen == 0) or not fullscreen:
# 	
# 			Window.size[0] = config_file['Screen']['x']
# 			Window.size[1] = config_file['Screen']['y']
# 			
# # 			print('Window size 0: ', Window.size[0])
# # 			print('Window size 1: ', Window.size[1])
# 		
# 		self.screen_resolution = Window.size
# 		
# 		print('Screen resolution: ', self.screen_resolution)
# 		print('Window size:', Window.size)
# 		print('Window system size:', Window.system_size)
# 		
# 		width = self.screen_resolution[0]
# 		height = self.screen_resolution[1]
# 		self.size = self.screen_resolution
# 		self.screen_ratio = 1
# 	
# 		if width > height:
# 			self.width_adjust = height / width
# 			self.height_adjust = 1
# 		elif height < width:
# 			self.width_adjust = 1
# 			self.height_adjust = width / height
# 		else:
# 			self.width_adjust = 1
# 			self.height_adjust = 1
		
		print('Width adjust: ', self.width_adjust)
		print('Height adjust: ', self.height_adjust)
	
		self.protocol_floatlayout = FloatLayoutLog(self.screen_resolution)
		self.protocol_floatlayout.size = self.screen_resolution
		self.add_widget(self.protocol_floatlayout)
		
		
		# Define App
		
		self.app = App.get_running_app()
		
		
		# Define Folders
		
		self.protocol_name = ''
		self.image_folder = pathlib.Path()
		
		# self.config_path = ''
		# self.file_path = ''
		
		
		# Define Datafile
		
		self.meta_data = pd.DataFrame()
		self.session_data = pd.DataFrame()
		self.data_cols = []
		self.metadata_cols = []
		
		
		# Define General Parameters
		
		self.participant_id = 'Default'
		self.block_max_length = 0
		self.block_max_count = 0
		self.block_min_rest_duration = 0.00
		self.session_length_max = 3600.00
		self.session_trial_max = 3600
		self.iti_length = 2.00
		self.feedback_length = 1.00
		self.hold_image = ''
		self.mask_image = ''
		self.image_dict = {}
		# self.age_range = ''
		
		
		# Define Language
		
		self.language = 'English'
		# self.start_label_str = ''
		# self.break_label_str = ''
		# self.end_label_str = ''
		# self.start_button_label_str = ''
		# self.continue_button_label_str = ''
		# self.return_button_label_str = ''
		# self.stim_feedback_correct_str = ''
		# self.stim_feedback_incorrect_str = ''
		# self.hold_feedback_wait_str = ''
		# self.hold_feedback_return_str = ''
		
		
		# Define Variables - Boolean
		
		self.stimulus_on_screen = False
		self.iti_active = False
		self.block_started = False
		self.feedback_on_screen = False
		self.hold_active = True
		self.instructions_on_screen = False
		
		
		# Define Variables - Counter
		
		self.current_block = 1
		self.current_trial = 1
		self.stage_index = 0
		
		
		# Define Variables - Time
		
		self.start_iti = 0.0
		self.start_time = 0.0
		self.block_start = 0.0
		self.block_start_time = 0.0
		self.elapsed_time = 0.0
		self.feedback_start_time = 0.0
		self.instruction_start_time = 0.0
		self.instruction_button_delay = 2.0
		
		
		# Define Class - Clock
		
		self.iti_clock = Clock
		self.iti_clock.interupt_next_only = False
		self.iti_event = self.iti_clock.create_trigger(self.iti, 0, interval=True)
		self.iti_event.cancel()
		
		self.session_clock = Clock
		self.session_clock.interupt_next_only = False
		self.session_event = self.session_clock.create_trigger(self.clock_monitor, self.session_length_max, interval=False)
		self.session_event.cancel()
		
		self.block_clock = Clock
		self.block_clock.interupt_next_only = False
		self.block_event = self.block_clock.create_trigger(self.block_screen, 0, interval=True)
		self.block_event.cancel()
		

		self.instruction_clock = Clock
		self.instruction_clock.interupt_next_only = True
		self.instruction_button_check_event = self.instruction_clock.create_trigger(self.present_instructions, 0, interval=True)
		self.instruction_button_check_event.cancel()
		
		
		# Define Dictionaries
		
		self.parameters_dict = {}
		self.feedback_dict = {}
		
		
		# Define Widgets - Images
		
		self.hold_button = ImageButton()
		self.hold_button.pos_hint = {"center_x": 0.5, "center_y": 0.1}
		self.hold_button.size_hint = (0.15 * self.width_adjust, 0.15 * self.height_adjust)
		self.hold_button.name = 'Hold Button'
		
		
		# Define Widgets - Text
		
		self.label_size = (0.90, 0.8)
		self.label_pos = {'center_x': 0.5, 'center_y': 0.6}
		self.label_font_size = '48sp'
		
		self.instruction_label = Label(font_size=self.label_font_size)
		self.instruction_label.size_hint = self.label_size
		self.instruction_label.pos_hint = self.label_pos
	
		self.block_label = Label(font_size=self.label_font_size)
		self.block_label.size_hint = self.label_size
		self.block_label.pos_hint = self.label_pos
	
		self.end_label = Label(font_size=self.label_font_size)
		self.end_label.size_hint = self.label_size
		self.end_label.pos_hint = self.label_pos
		
		
		# Define Widgets - Feedback
	
		self.feedback_string = ''
		self.feedback_label = Label(text=self.feedback_string, font_size='60sp', markup=True)
		self.feedback_label.size_hint = (0.7, 0.2)
		self.feedback_label.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
		
		
		# Define Widgets - Buttons
		
		self.button_size = (0.3, 0.15)
		self.button_pos = {'center_x': 0.5, 'center_y': 0.075}
		self.button_font_size = '60sp'
		
		self.start_button = Button(
			font_size = self.button_font_size
			, size_hint = self.button_size
			, pos_hint = self.button_pos
			, on_press = self.start_protocol
			)
		# self.start_button.size_hint = (0.3, 0.15)
		# self.start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.9}
		# self.start_button.bind(on_press=self.start_protocol)
		
		self.continue_button = Button(font_size='60sp')
		self.continue_button.size_hint = (0.3, 0.15)
		self.continue_button.pos_hint = {'center_x': 0.5, 'center_y': 0.1}
		self.continue_button.bind(on_press=self.block_end)
		
		self.return_button = Button(font_size='60sp')
		self.return_button.size_hint = (0.3, 0.15)
		self.return_button.pos_hint = {'center_x': 0.5, 'center_y': 0.1}
		self.return_button.bind(on_press=self.return_to_main)

		self.end_protocol_button = Button(font_size='60sp')
		self.end_protocol_button.size_hint = [0.4, 0.15]
		self.end_protocol_button.pos_hint =  {"center_x": 0.50, "center_y": 0.1}
		self.end_protocol_button.text = 'End Task'
		self.end_protocol_button.bind(on_press=self.protocol_end)
	
	
	
	def update_task(self):
	
		# self.image_folder = 'Protocol' + self.folder_mod + self.protocol_name + self.folder_mod + 'Image' + \
		# 					self.folder_mod

		self.image_folder = pathlib.Path('Protocol', self.protocol_name, 'Image')
	
	
	
	def load_images(self, image_list):
		# Load Images - Async
		
		self.image_dict = {}		
		
		for image_file in image_list:
			
			if Path(self.image_folder / image_file).exists():
				
				load_image = Loader.image(str(self.image_folder / image_file))
				image_name = str(image_file.stem)
			
			elif Path(self.image_folder, str(image_file) + '.png').exists():
				
				load_image = Loader.image((str(self.image_folder) + str(image_file) + '.png'))
				image_name = str(image_file)

			else: # Path(image_file).exists():
				
				image_file = Path(image_file)
				load_image = Loader.image(str(image_file))
				image_name = str(image_file.stem)


			self.image_dict[image_name] = load_image
	
	
	
	# def set_language(self, language):
	# 	self.language = language
	# 	lang_folder_path = 'Protocol' + self.folder_mod + self.protocol_name + self.folder_mod + 'Language' + \
	# 					   self.folder_mod + self.language + self.folder_mod
	# 	start_path = lang_folder_path + 'Start.txt'
	# 	start_open = open(start_path, 'r', encoding="utf-8")
	# 	start_label_str = start_open.read()
	# 	start_open.close()
	# 	self.instruction_label.text = start_label_str
	
	# 	break_path = lang_folder_path + 'Break.txt'
	# 	break_open = open(break_path, 'r', encoding="utf-8")
	# 	break_label_str = break_open.read()
	# 	break_open.close()
	# 	self.block_label.text = break_label_str
	
	# 	end_path = lang_folder_path + 'End.txt'
	# 	end_open = open(end_path, 'r', encoding="utf-8")
	# 	end_label_str = end_open.read()
	# 	end_open.close()
	# 	self.end_label.text = end_label_str
	
	# 	button_lang_path = lang_folder_path + 'Button.ini'
	# 	button_lang_config = configparser.ConfigParser()
	# 	button_lang_config.read(button_lang_path, encoding="utf-8")
	
	# 	start_button_label_str = button_lang_config['Button']['start']
	# 	self.start_button.text = start_button_label_str
	# 	continue_button_label_str = button_lang_config['Button']['continue']
	# 	self.continue_button.text = continue_button_label_str
	# 	return_button_label_str = button_lang_config['Button']['return']
	# 	self.return_button.text = return_button_label_str
	
	# 	feedback_lang_path = lang_folder_path + 'Feedback.ini'
	# 	feedback_lang_config = configparser.ConfigParser(allow_no_value=True)
	# 	feedback_lang_config.read(feedback_lang_path, encoding="utf-8")
	
	# 	self.feedback_dict = {}
	# 	stim_feedback_correct_str = feedback_lang_config['Stimulus']['correct']
	# 	stim_feedback_correct_color = feedback_lang_config['Stimulus']['correct_colour']
	# 	if stim_feedback_correct_color != '':
	# 		color_text = '[color=%s]' % stim_feedback_correct_color
	# 		stim_feedback_correct_str = color_text + stim_feedback_correct_str + '[/color]'
	# 	self.feedback_dict['correct'] = stim_feedback_correct_str
	
	# 	stim_feedback_incorrect_str = feedback_lang_config['Stimulus']['incorrect']
	# 	stim_feedback_incorrect_color = feedback_lang_config['Stimulus']['incorrect_colour']
	# 	if stim_feedback_incorrect_color != '':
	# 		color_text = '[color=%s]' % stim_feedback_incorrect_color
	# 		stim_feedback_incorrect_str = color_text + stim_feedback_incorrect_str + '[/color]'
	# 	self.feedback_dict['incorrect'] = stim_feedback_incorrect_str
	
	# 	hold_feedback_wait_str = feedback_lang_config['Hold']['wait']
	# 	hold_feedback_wait_color = feedback_lang_config['Hold']['wait_colour']
	# 	if hold_feedback_wait_color != '':
	# 		color_text = '[color=%s]' % hold_feedback_wait_color
	# 		hold_feedback_wait_str = color_text + hold_feedback_wait_str + '[/color]'
	# 	self.feedback_dict['wait'] = hold_feedback_wait_str
	
	# 	hold_feedback_return_str = feedback_lang_config['Hold']['return']
	# 	hold_feedback_return_color = feedback_lang_config['Hold']['return_colour']
	# 	if hold_feedback_return_color != '':
	# 		color_text = '[color=%s]' % hold_feedback_return_color
	# 		hold_feedback_return_str = color_text + hold_feedback_return_str + '[/color]'
	# 	self.feedback_dict['return'] = hold_feedback_return_str

	# 	stim_feedback_too_slow_str = feedback_lang_config['Stimulus']['too_slow']
	# 	stim_feedback_too_slow_color = feedback_lang_config['Stimulus']['too_slow_colour']
	# 	if stim_feedback_too_slow_color != '':
	# 		color_text = '[color=%s]' % stim_feedback_too_slow_color
	# 		stim_feedback_too_slow_str = color_text + stim_feedback_too_slow_str + '[/color]'
	# 	self.feedback_dict['too_slow'] = stim_feedback_too_slow_str

	# 	stim_feedback_miss_str = feedback_lang_config['Stimulus']['miss']
	# 	stim_feedback_miss_color = feedback_lang_config['Stimulus']['miss_colour']
	# 	if stim_feedback_miss_color != '':
	# 		color_text = '[color=%s]' % stim_feedback_miss_color
	# 		stim_feedback_miss_str = color_text + stim_feedback_miss_str + '[/color]'
	# 	self.feedback_dict['miss'] = stim_feedback_miss_str

	# 	stim_feedback_abort_str = feedback_lang_config['Stimulus']['abort']
	# 	stim_feedback_abort_color = feedback_lang_config['Stimulus']['abort_colour']
	# 	if stim_feedback_abort_color != '':
	# 		color_text = '[color=%s]' % stim_feedback_abort_color
	# 		stim_feedback_abort_str = color_text + stim_feedback_abort_str + '[/color]'
	# 	self.feedback_dict['abort'] = stim_feedback_abort_str
	
	
	
	def set_language(self, language):

		lang_folder_path = pathlib.Path('Protocol', self.protocol_name, 'Language', language)

		start_path = str(lang_folder_path / 'Start.txt')
		break_path = str(lang_folder_path / 'Break.txt')
		end_path = str(lang_folder_path / 'End.txt')
		button_lang_path = str(lang_folder_path / 'Button.ini')
		feedback_lang_path = str(lang_folder_path / 'Feedback.ini')

		with open(start_path, 'r', encoding="utf-8") as start_open:
			self.instruction_label.text = start_open.read()
	
		with open(break_path, 'r', encoding="utf-8") as break_open:
			self.block_label.text = break_open.read()
	
		with open(end_path, 'r', encoding="utf-8") as end_open:
			self.end_label.text = end_open.read()
	

		button_lang_config = configparser.ConfigParser()
		button_lang_config.read(button_lang_path, encoding="utf-8")
	
		self.start_button.text = button_lang_config['Button']['start']
		self.continue_button.text = button_lang_config['Button']['continue']
		self.return_button.text = button_lang_config['Button']['return']
	

		feedback_lang_config = configparser.ConfigParser(allow_no_value=True)
		feedback_lang_config.read(feedback_lang_path, encoding="utf-8")
	
		self.feedback_dict = {}

		stim_feedback_correct_str = feedback_lang_config['Stimulus']['correct']
		stim_feedback_correct_color = feedback_lang_config['Stimulus']['correct_colour']

		if stim_feedback_correct_color != '':
			color_text = '[color=%s]' % stim_feedback_correct_color
			stim_feedback_correct_str = color_text + stim_feedback_correct_str + '[/color]'

		self.feedback_dict['correct'] = stim_feedback_correct_str
	

		stim_feedback_incorrect_str = feedback_lang_config['Stimulus']['incorrect']
		stim_feedback_incorrect_color = feedback_lang_config['Stimulus']['incorrect_colour']

		if stim_feedback_incorrect_color != '':
			color_text = '[color=%s]' % stim_feedback_incorrect_color
			stim_feedback_incorrect_str = color_text + stim_feedback_incorrect_str + '[/color]'

		self.feedback_dict['incorrect'] = stim_feedback_incorrect_str
	

		hold_feedback_wait_str = feedback_lang_config['Hold']['wait']
		hold_feedback_wait_color = feedback_lang_config['Hold']['wait_colour']

		if hold_feedback_wait_color != '':
			color_text = '[color=%s]' % hold_feedback_wait_color
			hold_feedback_wait_str = color_text + hold_feedback_wait_str + '[/color]'

		self.feedback_dict['wait'] = hold_feedback_wait_str
	
		
		hold_feedback_return_str = feedback_lang_config['Hold']['return']
		hold_feedback_return_color = feedback_lang_config['Hold']['return_colour']
		
		if hold_feedback_return_color != '':
			color_text = '[color=%s]' % hold_feedback_return_color
			hold_feedback_return_str = color_text + hold_feedback_return_str + '[/color]'
		
		self.feedback_dict['return'] = hold_feedback_return_str


		stim_feedback_too_slow_str = feedback_lang_config['Stimulus']['too_slow']
		stim_feedback_too_slow_color = feedback_lang_config['Stimulus']['too_slow_colour']
		
		if stim_feedback_too_slow_color != '':
			color_text = '[color=%s]' % stim_feedback_too_slow_color
			stim_feedback_too_slow_str = color_text + stim_feedback_too_slow_str + '[/color]'
		
		self.feedback_dict['too_slow'] = stim_feedback_too_slow_str

		
		stim_feedback_miss_str = feedback_lang_config['Stimulus']['miss']
		stim_feedback_miss_color = feedback_lang_config['Stimulus']['miss_colour']
		
		if stim_feedback_miss_color != '':
			color_text = '[color=%s]' % stim_feedback_miss_color
			stim_feedback_miss_str = color_text + stim_feedback_miss_str + '[/color]'
		
		self.feedback_dict['miss'] = stim_feedback_miss_str

		
		stim_feedback_abort_str = feedback_lang_config['Stimulus']['abort']
		stim_feedback_abort_color = feedback_lang_config['Stimulus']['abort_colour']
		
		if stim_feedback_abort_color != '':
			color_text = '[color=%s]' % stim_feedback_abort_color
			stim_feedback_abort_str = color_text + stim_feedback_abort_str + '[/color]'
		
		self.feedback_dict['abort'] = stim_feedback_abort_str
	
	
	
	def generate_output_files(self):

		if (self.participant_id == 'Default') \
			or (self.participant_id == ''):

			self.participant_id = 'Default'
		
		
		folder_path = 'Data' + self.folder_mod + self.participant_id
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)

			
		self.file_index = 1
		
		temp_filename = self.participant_id + '_' + self.protocol_name + '_' + str(datetime.date.today()) + '_' + str(self.file_index) + '_Summary_Data.csv'
		self.summary_path = folder_path + self.folder_mod + temp_filename
		
		while os.path.isfile(self.summary_path):
			self.file_index += 1
			temp_filename = self.participant_id + '_' + self.protocol_name + '_' + str(datetime.date.today()) + '_' + str(self.file_index) + '_Summary_Data.csv'
			self.summary_path = folder_path + self.folder_mod + temp_filename
		

		self.session_data = pd.DataFrame(columns=self.data_cols)
		self.session_data.to_csv(path_or_buf=self.summary_path, sep=',', index=False)

		self.app.summary_event_path = self.summary_path
		self.app.summary_event_data = self.session_data


		self.event_path = folder_path + self.folder_mod + self.participant_id + '_' + self.protocol_name + '_' + str(datetime.date.today()) + '_' + str(self.file_index) + '_Event_Data.csv'
		
		self.protocol_floatlayout.update_path(self.event_path)
		
		self.event_data = pd.DataFrame(columns=[ # Event types: State Change, Variable Change, Object Display, Object Remove
			'Time'
			, 'Event_Type'
			, 'Event_Name'
			, 'Arg1_Name'
			, 'Arg1_Value'
			, 'Arg2_Name'
			, 'Arg2_Value'
			, 'Arg3_Name'
			, 'Arg3_Value'
			])
		self.event_data.to_csv(path_or_buf=self.event_path, sep=',', index=False)
		

		self.log_file_path = folder_path + self.folder_mod + self.participant_id + '_' + self.protocol_name + '_' + str(datetime.date.today()) + '_' + str(self.file_index) + '_Log.txt'
		
		with open(self.log_file_path, 'w') as log_file:
			log_file.write('Log file start...\n\n')
			log_file.write('Participant ID: ' + str(self.participant_id) + '\n')

			if self.parameters_dict['age_range'] != '':
				log_file.write('Age range: ' + str(self.parameters_dict['age_range']) + '\n')

			log_file.write('Task: ' + str(self.protocol_name) + '\n')
			log_file.write('Current date: ' + str(datetime.date.today()) + '\n')
			log_file.write('File index: ' + str(self.file_index) + '\n\n')
		
# 		self.log_path = folder_path + self.folder_mod + self.participant_id + '_' + self.protocol_name + str(datetime.date.today()) + '_' + str(file_index) + '_Output_Log.csv'
	
	
	
	def metadata_output_generation(self):
		folder_path = 'Data' + self.folder_mod + self.participant_id
	
		meta_list = list()

		# if self.age_range != '':			
		# 	row_list = list('age_range', self.age_range)
		# 	meta_list.append(row_list)

		for meta_row in self.metadata_cols:
			row_list = list()
			row_list.append(meta_row)
			row_list.append(str(self.parameters_dict[meta_row]))
			meta_list.append(row_list)
	
		alt_index = 1
		meta_output_filename = self.participant_id + '_' + self.protocol_name + '_' + str(datetime.date.today()) + '_' + str(self.file_index) + '_Metadata.csv'
		meta_output_path = folder_path + self.folder_mod + meta_output_filename
		while os.path.isfile(meta_output_path):
# 			self.file_index += 1
			meta_output_filename = self.participant_id + '_' + self.protocol_name + '_' + str(datetime.date.today()) + '_' + str(self.file_index) + '_Metadata' + str(alt_index) + '.csv'
			meta_output_path = folder_path + self.folder_mod + meta_output_filename
			alt_index += 1
	
		self.meta_data = pd.DataFrame(meta_list, columns=['Parameter', 'Value'])
		self.meta_data.to_csv(path_or_buf=meta_output_path, sep=',', index=False)
	
	
	
	def printlog(self, *args):
		
		with open(self.log_file_path, 'a') as log_file:
			output = ''.join([str(arg) for arg in args])
			print(output)
			log_file.write(output)
			log_file.write('\n')
	
	
	
	# def present_instructions(self, instruction_label='', start_button='', *kwargs):
	def present_instructions(self, *kwargs):

		if self.instructions_on_screen == False:

			self.protocol_floatlayout.clear_widgets()
			
			# if instruction_label == '':
			# 	instruction_label = self.instruction_label
			
			# if start_button == '':
			# 	start_button = self.start_button
	
			self.generate_output_files()
			self.metadata_output_generation()
		
			self.protocol_floatlayout.add_widget(self.instruction_label)

			self.instructions_on_screen = True
			self.instruction_start_time = time.time()

			self.protocol_floatlayout.add_event([
				0
				, 'Stage Change'
				, 'Instruction Presentation'
				])
			
			self.protocol_floatlayout.add_event([
				0
				, 'Text Displayed'
				, 'Task Instruction'
				])
		

		if (time.time() - self.instruction_start_time) > self.instruction_button_delay:

			self.instruction_button_check_event.cancel()

			self.protocol_floatlayout.add_widget(self.start_button)

			self.instructions_on_screen = False
			
			self.protocol_floatlayout.add_event([
				0
				, 'Button Displayed'
				, 'Task Start Button'
				])
		
		else:

			self.instruction_button_check_event()
	
	
	
	# Block Staging #
	
	def block_screen(self, *args):
		
# 		self.protocol_floatlayout.clear_widgets()
		
		if not self.block_started:
			
			self.protocol_floatlayout.add_widget(self.block_label)
			self.protocol_floatlayout.add_event(
				[(time.time() - self.start_time), 'Text Displayed', 'Block Instruction', '', '',
				 '', '', '', ''])
			self.block_start = time.time()
			self.block_start_time = time.time()
			self.block_started = True
			self.block_event()
		
		if (time.time() - self.block_start) > self.block_min_rest_duration:
			
			self.block_event.cancel()
			self.protocol_floatlayout.add_widget(self.continue_button)
			# self.protocol_floatlayout.add_event(
			# 	[(time.time() - self.start_time), 'Button Displayed', 'Continue Button', '', '',
			# 	 '', '', '', ''])
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Display'
				, 'Button'
				, 'Block'
				, 'Continue'
				])
	
	
	
	def block_end(self, *args):
		
		self.block_started = False
		self.protocol_floatlayout.clear_widgets()
		self.protocol_floatlayout.add_event(
			[(time.time() - self.start_time), 'Text Removed', 'Block Instruction', '', '',
			 '', '', '', ''])
		self.protocol_floatlayout.add_event(
			[(time.time() - self.start_time), 'Button Removed', 'Continue Button', '', '',
			 '', '', '', ''])
		self.block_start = time.time()
		self.block_start_time = time.time()
		self.hold_button.bind(on_press=self.iti)
		# self.hold_button.bind(on_release=self.premature_response)
		self.protocol_floatlayout.add_widget(self.hold_button)
		self.protocol_floatlayout.add_event(
			[(time.time() - self.start_time), 'Button Displayed', 'Hold Button', '', '',
			 '', '', '', ''])
	
	
	
	# End Staging #
	
	def protocol_end(self, *args):
		
		# self.protocol_floatlayout.clear_widgets()
		# self.protocol_floatlayout.add_widget(self.end_label)
		# self.protocol_floatlayout.add_event(
		# 	[(time.time() - self.start_time), 'Text Displayed', 'End Instruction', '', '',
		# 	 '', '', '', ''])
		# self.protocol_floatlayout.add_widget(self.return_button)
		# self.protocol_floatlayout.add_event(
		# 	[(time.time() - self.start_time), 'Button Displayed', 'Return Button', '', '',
		# 	 '', '', '', ''])
		self.app.summary_event_data.to_csv(self.app.summary_event_path, index=False)
		self.protocol_floatlayout.write_data()

		self.return_to_main()
	
	
	
	def return_to_main(self, *args):
		
		self.manager.current = 'mainmenu'
	
	
	
	def start_protocol(self, *args):
		
		self.protocol_floatlayout.add_event(
			[0, 'Stage Change', 'Instruction Presentation', '', '',
			 '', '', '', ''])
		self.protocol_floatlayout.remove_widget(self.instruction_label)
		self.protocol_floatlayout.add_event(
			[0, 'Text Removed', 'Task Instruction', '', '',
			 '', '', '', ''])
		self.protocol_floatlayout.remove_widget(self.start_button)
		self.protocol_floatlayout.add_event(
			[0, 'Button Removed', 'Task Start Button', '', '',
			 '', '', '', ''])
		self.start_clock()
	
		self.protocol_floatlayout.add_widget(self.hold_button)
		self.protocol_floatlayout.add_event(
			[(time.time() - self.start_time), 'Button Displayed', 'Hold Button', '', '',
			 '', '', '', ''])
		self.hold_button.size_hint = ((0.15 * self.width_adjust), (0.15 * self.height_adjust))
		self.hold_button.bind(on_press=self.iti)
	
	
	
	def iti(self, *args):
		
		if not self.iti_active:
			
			self.hold_button.unbind(on_press=self.iti)
			self.hold_button.bind(on_release=self.premature_response)
			self.start_iti = time.time()
			self.iti_active = True
			self.protocol_floatlayout.add_event(
				[(time.time() - self.start_time), 'Stage Change', 'ITI Start', '', '',
				 '', '', '', ''])
	
			if (self.feedback_string == self.feedback_dict['wait']) \
				or (self.feedback_string == self.feedback_dict['abort']):
				
				self.protocol_floatlayout.remove_widget(self.feedback_label)
				self.protocol_floatlayout.add_event(
					[(time.time() - self.start_time), 'Text Removed', 'Feedback', '', '',
					 '', '', '', ''])
				self.feedback_string = ''
			
			
			if not self.feedback_on_screen:
				
				self.feedback_label.text = self.feedback_string
				self.protocol_floatlayout.add_widget(self.feedback_label)
				self.protocol_floatlayout.add_event(
					[(time.time() - self.start_time), 'Text Displayed', 'Feedback', '', '',
					 '', '', '', ''])
				self.feedback_start_time = time.time()
				self.feedback_on_screen = True
			
			
			if ((time.time() - self.feedback_start_time) > self.feedback_length) and self.feedback_on_screen and \
					self.feedback_length > 0:
				
				self.protocol_floatlayout.remove_widget(self.feedback_label)
				self.protocol_floatlayout.add_event(
					[(time.time() - self.start_time), 'Text Removed', 'Feedback', '', '',
					 '', '', '', ''])
				self.feedback_on_screen = False
			
			self.iti_event()
			
			return
		
		
		if self.iti_active:
			
			if (((time.time() - self.start_iti) > self.feedback_length) or ((time.time() - self.feedback_start_time) > self.feedback_length)) \
				and self.feedback_on_screen:
				
				self.protocol_floatlayout.remove_widget(self.feedback_label)
				self.protocol_floatlayout.add_event(
					[(time.time() - self.start_time), 'Text Removed', 'Feedback', '', '',
					 '', '', '', ''])
				self.feedback_on_screen = False  
				
				return
			
			elif (time.time() - self.start_iti) > self.iti_length:
				
				self.iti_event.cancel()
				self.iti_active = False
				self.protocol_floatlayout.add_event(
					[(time.time() - self.start_time), 'Stage Change', 'ITI End', '', '',
					 '', '', '', ''])
				self.hold_button.unbind(on_release=self.premature_response)
				self.hold_active = True
				self.stimulus_presentation()
				
				return
	
	
	
	def write_summary_file(self, data_row):
		
		data_row = pd.Series(data_row, index=self.data_cols)
		self.app.summary_event_data = pd.concat([self.app.summary_event_data, data_row.to_frame().T], axis=0, ignore_index=True)
		self.app.summary_event_data
		
		return
	
	
	
	def start_clock(self, *args):
		
		self.start_time = time.time()
		self.session_event()
		self.protocol_floatlayout.start_time = self.start_time
		
		return
	
	
	
	def clock_monitor(self, *args):
		
		self.session_event.cancel()
		self.protocol_end()
		
		return
# Imports #

import configparser
import csv
import kivy
import os
import pathlib
import random
import sys
import time
import datetime
import ffpyplayer


# print(kivy.kivy_options['VIDEO'])

# print(os.environ)

# print(kivy.kivy_options['video'])

# os.environ['KIVY_VIDEO'] = 'ffpyplayer'
# os.environ['KIVY_VIDEO'] = 'gstplayer'

# print(os.environ)




# import kivy.core.video

import numpy as np
import pandas as pd

from Classes.Protocol import ImageButton, ProtocolBase

from kivy.clock import Clock
from kivy.config import Config
from kivy.core.video import Video as CoreVideo
from kivy.core.video import VideoBase
from kivy.graphics import context_instructions
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.video import Video
# from kivy.uix.videoplayer import VideoPlayer
# os.environ['KIVY_VIDEO'] = 'gstplayer'





environ_vars = dict(os.environ)

# for iVar in environ_vars:
# 	print(environ_vars[1, :])
# 	print('\n')

# with open('OS_environ.csv', 'w') as newfile:
# 	for key, value in environ_vars:
# 		newfile.write([key, value])
# 		newfile.write('\n')




class ProtocolScreen(ProtocolBase):
	
	
	
	def __init__(self, **kwargs):
		
		
		super(ProtocolScreen, self).__init__(**kwargs)
		
		
		self.protocol_name = '2-TUNL'
		self.update_task()
		
		
# 		temp_log_path = self.participant_id + '_' + self.protocol_name + '_' + str(datetime.date.today()) + '.txt'
		
# 		with open(temp_log_path, 'w') as self.temp_logfile:
# 			self.printlog('New temp log file.')
# 			self.printlog('Participant: ', self.participant_id)
# 			self.printlog('Task: ', self.protocol_name)
# 			self.printlog('Date: ', str(datetime.date.today()))
		
		
# 		self.temp_logfile = open(temp_log_path, 'a')
		
		
		width = int(Config.get('graphics', 'width'))
		height = int(Config.get('graphics', 'height'))
		self.maxfps = 120 # int(Config.get('graphics', 'maxfps'))
		
		print(width)
		print(height)
		
		self.screen_resolution = (width, height)
		
		print(self.screen_resolution)
		
		self.protocol_floatlayout.size = self.screen_resolution
# 		self.screen_ratio = 1
		
		if width > height:
			
			self.width_adjust = height / width
			self.height_adjust = 1
			
			print('Width > Height')
		
		
		elif width < height:
			
			
			self.width_adjust = 1
			self.height_adjust = width / height
			
			print('Width < Height')
		
		
		elif width == height:
			
			
			self.width_adjust = 1
			self.height_adjust = 1
			
			print('Width = Height')
		
		
		else:
			
			
			print('Screen resolution issue')
			
			self.width_adjust = 1
			self.height_adjust = 1
			
		print('Width adjust: ', self.width_adjust)
		print('height adjust: ', self.height_adjust)
			
			
# 		self.width_adjust = 0.66
# 		self.height_adjust = 1
		
# 		if sys.platform == 'linux' or sys.platform == 'darwin':
# 			self.folder_mod = '/'
# 		elif sys.platform == 'win32':
# 			self.folder_mod = '\\'
		
		
		# Define Variables - Folder Path
		
# 		self.image_folder = 'Protocol' + self.folder_mod + 'TUNLProbe' + self.folder_mod + 'Image' + self.folder_mod
		
		print('Initializing task...')
		
		self.image_folder = pathlib.Path('Protocol', self.protocol_name, 'Image')
		
		self.data_output_path = None
		
		self.data_cols = [
			'TrialNo'
			, 'Current Block'
			, 'Probe Type'
			, 'Separation'
			, 'Delay'
			, 'Video Time'
			, 'Cue_X'
			, 'Cue_Y'
			, 'Target_X'
			, 'Target_Y'
			, 'Correct'
			, 'Target Latency'
			]
		
		self.metadata_cols = [
			'participant_id'
			# , 'stage_list'
			, 'skip_tutorial_video'
			, 'block_change_on_duration_only'
			, 'iti_length'
			, 'iti_fixed_or_range'
			, 'feedback_length'
			, 'block_duration'
			, 'block_multiplier'
			, 'session_length_max'
			, 'screen_x_padding'
			, 'screen_y_padding_top'
			, 'screen_y_padding_bottom'
			, 'stimulus_gap'
			, 'x_boundaries'
			, 'y_boundaries'
			, 'stimulus_image'
			, 'distractor_video'
			, 'staircase_sep_initial'
			, 'staircase_delay_initial'
			, 'minimum_sep'
			, 'minimum_delay'
			, 'space_probe_sep_list'
			, 'delay_probe_delay_list'
			]
		
		
		# Define Variables - Config
		
		print('Reading configuration data...')
		
		config_path = pathlib.Path('Protocol', self.protocol_name, 'Configuration.ini')
		config_file = configparser.ConfigParser()
		config_file.read(config_path)

		if ('DebugParameters' in config_file) \
			and (int(config_file['DebugParameters']['debug_mode']) == 1):
			self.parameters_dict = config_file['DebugParameters']
		else:
			self.parameters_dict = config_file['TaskParameters']

		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_import = self.parameters_dict['iti_length']
		iti_import = iti_import.split(',')
		
		stimdur_import = self.parameters_dict['stimulus_duration']
		stimdur_import = stimdur_import.split(',')
		
		limhold_import = self.parameters_dict['limited_hold']
		limhold_import = limhold_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration = float(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_length_max'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])

		self.stimulus_scale = float(self.parameters_dict['stimulus_scale'])
		
		self.screen_x_padding = int(self.parameters_dict['screen_x_padding'])
		self.screen_y_padding_t = int(self.parameters_dict['screen_y_padding_top'])
		self.screen_y_padding_b = int(self.parameters_dict['screen_y_padding_bottom'])

		self.stimulus_gap = float(self.parameters_dict['stimulus_gap'])
		
		self.x_boundaries = self.parameters_dict['x_boundaries']
		self.x_boundaries = self.x_boundaries.split(',')

		self.y_boundaries = self.parameters_dict['y_boundaries']
		self.y_boundaries = self.y_boundaries.split(',')

		self.stimulus_image = self.parameters_dict['stimulus_image']
		self.stimulus_button_image = self.parameters_dict['stimulus_button_image']
		self.distractor_video = self.parameters_dict['distractor_video']

		self.staircase_sep_initial = int(self.parameters_dict['staircase_sep_initial'])
		self.staircase_delay_initial = float(self.parameters_dict['staircase_delay_initial'])
		
		self.min_sep = int(self.parameters_dict['minimum_sep'])
		self.max_sep = int(self.parameters_dict['maximum_sep'])
		self.min_delay = float(self.parameters_dict['minimum_delay'])
		self.max_delay = float(self.parameters_dict['maximum_delay'])
		
		self.space_probe_sep_list = self.parameters_dict['space_probe_sep_list']
		self.space_probe_sep_list = self.space_probe_sep_list.split(',')

		self.delay_probe_delay_list = self.parameters_dict['delay_probe_delay_list']
		self.delay_probe_delay_list = self.delay_probe_delay_list.split(',')

		self.hold_image = config_file['Hold']['hold_image']
		
		
		# Create stage list
		
		self.stage_list = list()

		
		# Define Language
		
		self.language = 'English'
		self.set_language(self.language)
		self.stage_instructions = ''
		

		# Define Clock
		
		self.block_check_clock = Clock
		self.block_check_clock.interupt_next_only = False
		self.block_check_event = self.block_check_clock.create_trigger(self.block_contingency, 0, interval=True)

		self.block_check_event.cancel()

		
		self.presentation_clock = Clock
		self.presentation_clock.interupt_next_only = True

		self.tutorial_video_end_event = self.presentation_clock.schedule_once(self.present_tutorial_video_start_button, 1)

		self.stimulus_event = self.presentation_clock.create_trigger(self.stimulus_presentation, 0, interval=True)
		self.cue_present_event = self.presentation_clock.create_trigger(self.cue_present, 0)
		self.delay_present_event = self.presentation_clock.create_trigger(self.delay_present, 0)
		self.delay_end_event = self.presentation_clock.create_trigger(self.delay_end, 0)
		self.target_present_event = self.presentation_clock.create_trigger(self.target_present, 0)

		self.tutorial_video_end_event.cancel()

		self.stimulus_event.cancel()
		self.cue_present_event.cancel()
		self.delay_present_event.cancel()
		self.delay_end_event.cancel()
		self.target_present_event.cancel()


		# Define Variables - Time

		self.frame_duration = 0 #float(1/30)

		self.cue_start_time = 0.0
		self.target_start_time = 0.0
		self.target_lat = 0.0
		self.current_delay = 0.0
		self.video_start_time = 0.0
		self.video_end_time = 0.0
		self.video_position = 0.0

		self.last_staircase_time_increase = self.staircase_delay_initial

		
		self.iti_range = [float(iNum) for iNum in iti_import]
		self.iti_length = self.iti_range[0]
		
		self.stimdur_list = [float(iNum) for iNum in stimdur_import]
		self.limhold_list = [float(iNum) for iNum in limhold_import]

		self.stimdur = self.stimdur_list[0]
		self.limhold = self.limhold_list[0]
		
		
		# Define Variables - Numeric

		self.x_boundaries = [float(iNum) for iNum in self.x_boundaries]
		self.y_boundaries = [float(iNum) for iNum in self.y_boundaries]

		self.current_sep = 0
				
		self.current_block = 1
		self.current_block_trial = 0
		
		self.last_response = 0
		
		self.hold_button_x_pos = 0.5
		self.hold_button_y_pos = 0.05
		
		self.hold_button_x_size = 0.1
		self.hold_button_y_size = 0.1

		self.response_tracking = list()
		self.accuracy_tracking = list()
		
		
		# Define Boolean
		
		self.hold_active = False
		self.cue_completed = False
		self.cue_on_screen = False
		self.target_on_screen = False
		self.video_on_screen = False
		self.limhold_started = False
		self.delay_ended = False


		# Define String

		self.staircase_change = 'non'
		
		
# 		# Define Widgets - Background Grid
		
		hold_button_top_loc = self.hold_button_y_pos + (self.hold_button_y_size/2)

		if self.y_boundaries[0] < hold_button_top_loc:
			self.y_boundaries[0] = hold_button_top_loc
		
		elif self.y_boundaries[1] < hold_button_top_loc:
			self.y_boundaries[1] = hold_button_top_loc
		
		self.stimulus_image_path = str(pathlib.Path(self.image_folder, self.stimulus_image + '.png'))
		self.stimulus_button_image_path = str(pathlib.Path(self.image_folder, self.stimulus_button_image + '.png'))
		
		
		# Define Widgets - Buttons
		
		self.hold_button_image_path = str(pathlib.Path(self.image_folder, self.hold_image + '.png'))
		self.hold_button.source = self.hold_button_image_path
		
		self.cue_image = ImageButton(source=self.stimulus_image_path)
		self.target_image = ImageButton(source=self.stimulus_image_path)

		self.cue_image_button = ImageButton(source=self.stimulus_button_image_path)
		self.cue_image_button.bind(on_press=self.cue_pressed)
		
		self.target_image_button = ImageButton(source=self.stimulus_button_image_path)
		self.target_image_button.bind(on_press=self.target_pressed)


		self.load_images(['white', 'circle', 'circlesquare','bluesquare'])


		self.test_image = Image(source=str(self.image_folder / 'circlesquare.png'))
		self.test_image.size_hint = [1,1]
		# self.test_image.size_hint = [None, None] #[self.width_adjust,self.height_adjust]
		# self.test_image.size = self.test_image.texture_size

		# self.test_image.texture = self.image_dict['circlesquare']

		self.protocol_floatlayout.add_widget(self.test_image)

		print('Texture size: ', self.test_image.texture_size)
		print('Norm image size: ', self.test_image.norm_image_size)

		# self.test_image.size = [228, 228]
		
		
		# Define Widgets - Labels
		
		self.feedback_label.size_hint = (0.7, 0.3)
		self.feedback_label.pos_hint = {'center_x': 0.5, 'center_y': 0.55}


		# Instruction - Dictionary
		
		self.instruction_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'Instructions.ini'))
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Training'] = {}
		self.instruction_dict['Space'] = {}
		self.instruction_dict['Delay'] = {}
		self.instruction_dict['Combo'] = {}
		
		
		instruction_temp_train_str = self.instruction_config['Training']['train']
		instruction_temp_probe_str = self.instruction_config['Training']['task']
		
		self.instruction_dict['Training']['train'] = instruction_temp_train_str
		self.instruction_dict['Training']['task'] = instruction_temp_train_str
		
		
		instruction_temp_train_str = self.instruction_config['Space']['train']
		instruction_temp_probe_str = self.instruction_config['Space']['task']
		
		self.instruction_dict['Space']['train'] = instruction_temp_train_str
		self.instruction_dict['Space']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Delay']['train']
		instruction_temp_probe_str = self.instruction_config['Delay']['task']
		
		self.instruction_dict['Delay']['train'] = instruction_temp_train_str
		self.instruction_dict['Delay']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Combo']['train']
		instruction_temp_probe_str = self.instruction_config['Combo']['task']
		
		self.instruction_dict['Combo']['train'] = instruction_temp_train_str
		self.instruction_dict['Combo']['task'] = instruction_temp_probe_str
		
		
		# Instruction - Text Widget
		
		self.section_instr_string = ''
		
		
		# Instruction - Button Widget
		
		self.instruction_button = Button()
		self.instruction_button.bind(on_press=self.section_start)
		self.instruction_button_str = ''
	
	
	
	# Initialization Functions
	
	def load_parameters(self, parameter_dict):
		
		
		print('Load parameters...')
		
		self.parameters_dict = parameter_dict
		
		config_path = pathlib.Path('Protocol', self.protocol_name, 'Configuration.ini')
		config_file = configparser.ConfigParser()
		config_file.read(config_path)
	
		self.participant_id = self.parameters_dict['participant_id']
		self.language = self.parameters_dict['language']

		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_import = self.parameters_dict['iti_length']
		iti_import = iti_import.split(',')
		
		stimdur_import = self.parameters_dict['stimulus_duration']
		stimdur_import = stimdur_import.split(',')
		
		limhold_import = self.parameters_dict['limited_hold']
		limhold_import = limhold_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration = float(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_length_max'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])

		self.stimulus_scale = float(self.parameters_dict['stimulus_scale'])
		
		self.screen_x_padding = int(self.parameters_dict['screen_x_padding'])
		self.screen_y_padding_t = int(self.parameters_dict['screen_y_padding_top'])
		self.screen_y_padding_b = int(self.parameters_dict['screen_y_padding_bottom'])

		self.stimulus_gap = float(self.parameters_dict['stimulus_gap'])
		
		self.x_boundaries = self.parameters_dict['x_boundaries']
		self.x_boundaries = self.x_boundaries.split(',')

		self.y_boundaries = self.parameters_dict['y_boundaries']
		self.y_boundaries = self.y_boundaries.split(',')

		self.stimulus_image = self.parameters_dict['stimulus_image']
		self.stimulus_button_image = self.parameters_dict['stimulus_button_image']
		self.distractor_video = self.parameters_dict['distractor_video']

		self.staircase_sep_initial = int(self.parameters_dict['staircase_sep_initial'])
		self.staircase_delay_initial = float(self.parameters_dict['staircase_delay_initial'])
		
		self.min_sep = int(self.parameters_dict['minimum_sep'])
		self.max_sep = int(self.parameters_dict['maximum_sep'])
		self.min_delay = float(self.parameters_dict['minimum_delay'])
		self.max_delay = float(self.parameters_dict['maximum_delay'])
		
		self.space_probe_sep_list = self.parameters_dict['space_probe_sep_list']
		self.space_probe_sep_list = self.space_probe_sep_list.split(',')

		self.delay_probe_delay_list = self.parameters_dict['delay_probe_delay_list']
		self.delay_probe_delay_list = self.delay_probe_delay_list.split(',')
		
		
		# Create stage list
		
		self.stage_list = list()
		
		if int(self.parameters_dict['space_probe']) == 1:
			
			self.stage_list.append('Space')
		

		if int(self.parameters_dict['delay_probe']) == 1:
			
			self.stage_list.append('Delay')
		
		if len(self.stage_list) > 1:
			
			random.shuffle(self.stage_list)
		
		
		if int(self.parameters_dict['combined_probe']) == 1:
			
			self.stage_list.append('Combo')


		# Define Variables - Time

		self.cue_start_time = 0.0
		self.target_start_time = 0.0
		self.target_lat = 0.0
		self.current_delay = 0.0
		self.video_start_time = 0.0
		self.video_end_time = 0.0
		self.video_position = 0.0

		self.last_staircase_time_increase = self.staircase_delay_initial

		self.combo_probe_max_section_dur = self.block_duration // 3

		
		self.iti_range = [float(iNum) for iNum in iti_import]
		self.iti_length = self.iti_range[0]
		
		self.stimdur_list = [float(iNum) for iNum in stimdur_import]
		self.limhold_list = [float(iNum) for iNum in limhold_import]

		self.stimdur = self.stimdur_list[0]
		self.limhold = self.limhold_list[0]


		# Define Variables - Trial Lists
		
		self.space_probe_sep_list = [int(iNum) for iNum in self.space_probe_sep_list]
		self.delay_probe_delay_list = [float(iNum) for iNum in self.delay_probe_delay_list]
		self.combo_probe_sep_list = [int(iNum) for iNum in self.space_probe_sep_list]
		self.combo_probe_sep_list.sort(reverse=True)

		self.space_probe_delay_list = [self.staircase_delay_initial for iElem in self.space_probe_sep_list]
		self.space_probe_staircase_list = [self.staircase_delay_initial for iElem in self.space_probe_sep_list]
		self.delay_probe_sep_list = [self.staircase_sep_initial for iElem in self.delay_probe_delay_list]
		self.combo_probe_delay_list = [self.staircase_delay_initial for iElem in self.space_probe_sep_list]
		self.combo_probe_staircase_list = [self.staircase_delay_initial for iElem in self.space_probe_sep_list]

		self.space_probe_response_list = [0 for iElem in self.space_probe_sep_list]
		self.delay_probe_response_list = [0 for iElem in self.delay_probe_delay_list]
		self.combo_probe_response_list = [0 for iElem in self.combo_probe_sep_list]

		self.combo_probe_delay_tracking_dict = {}
		
		for iSep in self.combo_probe_sep_list:

			self.combo_probe_delay_tracking_dict[iSep] = [0,0]


		self.space_trial_index_list = list(range(0, len(self.space_probe_sep_list)))
		self.delay_trial_index_list = list(range(0, len(self.delay_probe_delay_list)))

		random.shuffle(self.space_trial_index_list)
		random.shuffle(self.delay_trial_index_list)

		print(self.space_probe_sep_list)
		print(self.delay_probe_delay_list)
		print(self.combo_probe_sep_list)
		
		print(self.space_trial_index_list)
		print(self.delay_trial_index_list)
		

		# Define Variables - Numeric

		self.x_boundaries = [float(iNum) for iNum in self.x_boundaries]
		self.y_boundaries = [float(iNum) for iNum in self.y_boundaries]

		self.stage_index = 0

		self.trial_index = 0
		self.space_trial_index = self.space_trial_index_list[0]
		self.delay_trial_index = self.delay_trial_index_list[0]
		self.combo_trial_index = 0

		self.current_sep = 0
				
		self.current_block = 1
		self.current_block_trial = 0

		self.max_blocks = len(self.stage_list) * self.block_multiplier
		
		self.last_response = 0
		

		self.hold_button_x_pos = 0.5
		self.hold_button_y_pos = 0.05
		
		self.hold_button_x_size = 0.1
		self.hold_button_y_size = 0.1

		self.current_correction = 0

		self.response_tracking = list()
		self.accuracy_tracking = list()
		
		
		# Define Boolean
		
		self.hold_active = False
		self.cue_completed = False
		self.cue_on_screen = False
		self.target_on_screen = False
		self.video_on_screen = False
		self.limhold_started = False
		self.delay_active = False
		self.delay_ended = False


		# Define String

		self.staircase_change = 'non'
		
		
		# Define Language
		
		self.set_language(self.language)
		
		
		# Define Widgets - Screen Boundaries
		
		hold_button_top_loc = self.hold_button_y_pos + (self.hold_button_y_size/2)

		if self.y_boundaries[0] < hold_button_top_loc:
			self.y_boundaries[0] = hold_button_top_loc
		
		elif self.y_boundaries[1] < hold_button_top_loc:
			self.y_boundaries[1] = hold_button_top_loc
		

		# Define Variables - Coordinates
		
		self.current_stage = self.stage_list[self.stage_index]
		
		if self.current_stage == 'Space':
			
			self.current_sep = self.space_probe_sep_list[self.space_trial_index]
			self.current_delay = self.space_probe_delay_list[self.space_trial_index]
		
		elif self.current_stage == 'Delay':
			
			self.current_sep = self.delay_probe_sep_list[self.delay_trial_index]
			self.current_delay = self.delay_probe_delay_list[self.delay_trial_index]
		
		elif self.current_stage == 'Combo':
			
			self.current_sep = self.combo_probe_sep_list[self.combo_trial_index]
			self.current_delay = self.combo_probe_delay_list[self.combo_trial_index]


		self.stimulus_image_path = str(pathlib.Path(self.image_folder, self.stimulus_image + '.png'))


		# Define GUI Sizes and Pos

		self.hold_button_size = ((self.hold_button_x_size * self.width_adjust), (self.hold_button_y_size * self.height_adjust))

		self.video_size = (1, 1)

		self.text_button_size = [0.4, 0.15]

		self.stimulus_image_spacing = [
			((self.cue_image.texture_size[0]/self.screen_resolution[0]) * self.stimulus_scale)
			, ((self.cue_image.texture_size[1]/self.screen_resolution[1]) * self.stimulus_scale)
			]
		
		self.stimulus_image_size = (np.array(self.stimulus_image_spacing) * (1 - self.stimulus_gap)).tolist()

		self.stimulus_button_size = (np.array(self.stimulus_image_size) * 0.77).tolist()
		

		self.hold_button_pos = {"center_x": self.hold_button_x_pos, "center_y": self.hold_button_y_pos}
		
		self.video_pos = {"center_x": 0.5, "center_y": 0.55}

		self.text_button_pos_UL = {"center_x": 0.25, "center_y": 0.92}
		self.text_button_pos_UC = {"center_x": 0.50, "center_y": 0.92}
		self.text_button_pos_UR = {"center_x": 0.75, "center_y": 0.92}

		self.text_button_pos_LL = {"center_x": 0.25, "center_y": 0.08}
		self.text_button_pos_LC = {"center_x": 0.50, "center_y": 0.08}
		self.text_button_pos_LR = {"center_x": 0.75, "center_y": 0.08}


		# Instruction - Dictionary
		
		self.instruction_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'Instructions.ini'))
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Training'] = {}
		self.instruction_dict['Space'] = {}
		self.instruction_dict['Delay'] = {}
		self.instruction_dict['Combo'] = {}
		
		for stage in self.stage_list:
			
			self.instruction_dict[stage]['train'] = self.instruction_config[stage]['train']
			self.instruction_dict[stage]['task'] = self.instruction_config[stage]['task']
		
		
		# Instruction - Text Widget
		
		self.section_instr_string = self.instruction_label.text
		self.section_instr_label = Label(text=self.section_instr_string, font_size='44sp', markup=True)
		self.section_instr_label.size_hint = {0.58, 0.4}
		self.section_instr_label.pos_hint = {'center_x': 0.5, 'center_y': 0.35}
		
		# Instruction - Button Widget
		
		self.instruction_button = Button(font_size='60sp')
		self.instruction_button.size_hint = [0.4, 0.15]
		self.instruction_button.pos_hint =  {"center_x": 0.50, "center_y": 0.92}
		self.instruction_button.text = ''
		self.instruction_button.bind(on_press=self.section_start)
		self.instruction_button_str = ''
		
		
		# Define Widgets - Buttons
		
		self.hold_button_image_path = str(pathlib.Path(self.image_folder, self.hold_image + '.png'))
		
		self.hold_button.source = self.hold_button_image_path
		self.hold_button.size_hint = self.hold_button_size
		self.hold_button.pos_hint = self.hold_button_pos
		self.hold_button.bind(on_press=self.iti)
				
		self.cue_image = ImageButton(source=self.stimulus_image_path)
		self.target_image = ImageButton(source=self.stimulus_image_path)

		self.cue_image_button = ImageButton(source=self.stimulus_button_image_path)
		self.target_image_button = ImageButton(source=self.stimulus_button_image_path)

		print('Cue image texture size:', self.cue_image.texture_size)
		print('Cue button texture size:', self.cue_image_button.texture_size)

		# self.stimulus_image_spacing = [
		# 	((self.cue_image.texture_size[0]/self.screen_resolution[0]) * self.stimulus_scale)
		# 	, ((self.cue_image.texture_size[1]/self.screen_resolution[1]) * self.stimulus_scale)
		# 	]
		
		# self.stimulus_image_size = (np.array(self.stimulus_image_spacing) * (1 - self.stimulus_gap)).tolist()

		# self.stimulus_button_size = (np.array(self.stimulus_image_size) * 0.77).tolist()

		print('self.stimulus_image_spacing: ', self.stimulus_image_spacing)
		print('self.stimulus_image_size: ', self.stimulus_image_size)
		print('self.stimulus_button_size: ', self.stimulus_button_size)

		self.cue_image.size_hint = self.stimulus_image_size
		self.target_image.size_hint = self.stimulus_image_size

		self.cue_image_button.size_hint = self.stimulus_button_size
		self.cue_image_button.bind(on_press=self.cue_pressed)
		self.cue_image_button.name = 'Cue Image'

		self.target_image_button.size_hint = self.stimulus_button_size
		self.target_image_button.bind(on_press=self.target_pressed)
		self.target_image_button.name = 'Target Image'

		self.trial_coord = self.generate_trial_pos_sep(
			self.x_boundaries
			, self.y_boundaries
			, self.current_sep
			, self.stimulus_image_spacing
			, self.screen_x_padding
			, self.screen_y_padding_t
			, self.screen_y_padding_b
			)
		
		self.cue_image.pos_hint = {
			"center_x": self.trial_coord['Cue']['x'], 
			"center_y": self.trial_coord['Cue']['y']
			}
		self.target_image.pos_hint = {
			"center_x": self.trial_coord['Target']['x'], 
			"center_y": self.trial_coord['Target']['y']
			}
		
		self.cue_image_button.pos_hint = {
			"center_x": self.trial_coord['Cue']['x'], 
			"center_y": self.trial_coord['Cue']['y']
			}
		self.target_image_button.pos_hint = {
			"center_x": self.trial_coord['Target']['x'], 
			"center_y": self.trial_coord['Target']['y']
			}


		self.delay_video_folder = pathlib.Path('Delay_Videos')

		self.delay_video_path_list = list(pathlib.Path(self.image_folder).glob(str(self.delay_video_folder / '*.mp4')))

		if len(self.delay_video_path_list) > 1:

			self.delay_video_path = random.choice(self.delay_video_path_list)
			self.delay_video_path_list.remove(self.delay_video_path)
		
		else:

			self.delay_video_path = self.delay_video_path_list[0]

		
		self.delay_video = Video(
			source = str(self.delay_video_path)
			, allow_stretch = True
			, options = {'eos': 'loop'}
			, state = 'stop'
			)

		self.delay_video.pos_hint = self.video_pos

		# self.delay_video.allow_stretch = True
		self.delay_video.size_hint = self.video_size

		self.protocol_floatlayout.add_widget(self.delay_video)
		self.delay_video.state = 'pause'
		self.protocol_floatlayout.remove_widget(self.delay_video)




		self.tutorial_video_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'TUNL_Tutorial_Video.mp4'))
		# self.delay_video_path = str(pathlib.Path.home() / 'Touchcog' / 'Videos' / self.distractor_video)

		self.tutorial_video = Video(
			source = self.tutorial_video_path
			, allow_stretch = True
			# , options = {'eos': 'loop'}
			, state = 'stop'
			)

		self.tutorial_video.pos_hint = self.video_pos

		self.tutorial_video.size_hint = self.video_size




		
		
		# self.present_tutorial_video()
		# self.present_instructions()
		self.present_tutorial()










	





	def generate_trial_pos_sep(
		self
		, x_boundaries = [0, 1]
		, y_boundaries = [0.1, 1]
		, sep_level = 0
		, stimulus_size = [0.066, 0.1]
		, x_padding = 0
		, y_padding_t = 0
		, y_padding_b = 0
		):

		x_lim = [
			min(x_boundaries) + stimulus_size[0]*(x_padding + 0.5)
			, max(x_boundaries) - stimulus_size[0]*(x_padding + 0.5)
			]
		
		y_lim = [
			min(y_boundaries) + stimulus_size[1]*(y_padding_b + 0.5)
			, max(y_boundaries) - stimulus_size[1]*(y_padding_t + 0.5)
			]
		
		print('X lim:', x_lim)
		print('Y lim:', y_lim)

		main_move = float(sep_level) + 1
		
		cue_xpos = random.uniform(min(x_lim), max(x_lim))
		cue_ypos = random.uniform(min(y_lim), max(y_lim))

		print('Cue xpos:', cue_xpos)
		print('Cue ypos:', cue_ypos)
		
		horz_dist = random.uniform(-main_move, main_move)

		horz_move = horz_dist * stimulus_size[0]

		print('Main move:', main_move)
		print('Horz move:', horz_move)
		
		target_xpos = cue_xpos + horz_move

		vert_dist = float(np.sqrt(main_move**2 - horz_dist**2))

		print('Vert dist:', vert_dist)
		
		vert_move = (random.choice([-vert_dist, vert_dist])) * stimulus_size[1]

		print('Vert move:', vert_move)
		
		target_ypos = cue_ypos + vert_move

		print('Target xpos:', target_xpos)
		print('Target ypos:', target_ypos)
		
		while (target_xpos < min(x_lim)) \
			or (target_xpos > max(x_lim)) \
			or (target_ypos < min(y_lim)) \
			or (target_ypos > max(y_lim)):

			if (target_xpos < min(x_lim)) \
				or (target_xpos > max(x_lim)):

				horz_move *= -1
			

			if (target_ypos < min(y_lim)) \
				or (target_ypos > max(y_lim)):

				vert_move *= -1
			

			target_xpos = cue_xpos + horz_move
			target_ypos = cue_ypos + vert_move

			if (target_xpos < min(x_lim)) \
				or (target_xpos > max(x_lim)) \
				or (target_ypos < min(y_lim)) \
				or (target_ypos > max(y_lim)):

				horz_dist = random.uniform(-main_move, main_move)

				horz_move = horz_dist * stimulus_size[0]

				target_xpos = cue_xpos + horz_move

				vert_dist = float(np.sqrt(main_move**2 - horz_dist**2))
		
				vert_move = (random.choice([-vert_dist, vert_dist])) * stimulus_size[1]
		
				target_ypos = cue_ypos + vert_move
		

		print('Cue xpos: ', cue_xpos)
		print('Cue ypos: ', cue_ypos)

		print('Horz move: ', horz_move)
		print('Vert move: ', vert_move)
		
		print('Target xpos: ', target_xpos)
		print('Target ypos: ', target_ypos)

		print('Stimulus size: ', stimulus_size)

		print('Current sep: ', self.current_sep)
		print('Sep level: ', sep_level)

		print('Main move: ', main_move)

		cue_coord = {'x': round(cue_xpos, 4), 'y': round(cue_ypos, 4)}
		target_coord = {'x': round(target_xpos, 4), 'y': round(target_ypos, 4)}

		trial_coord = {'Cue': cue_coord, 'Target': target_coord}
		
		return trial_coord
	



		
		
		
	# Remove Block Screen and Resume Task
	
	# def block_end(self, *args):
		
	# 	print('Block end')
		
	# 	self.block_started = False
	# 	self.protocol_floatlayout.clear_widgets()
		
	# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
	# 										, 'Text Removed'
	# 										, 'Block Instruction'
	# 										])
		
	# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
	# 										, 'Button Removed'
	# 										, 'Continue Button'
	# 										])
		
	# 	self.block_start_time = time.time()
	# 	self.trial_contingency()
		
	# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
	# 										, 'Image Displayed'
	# 										, 'Grid Array'
	# 										])
		
	# 	self.protocol_floatlayout.add_widget(self.hold_button)
		
	# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
	# 										, 'Button Displayed'
	# 										, 'Hold Button'
	# 										])
		
		
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	# Protocol Staging
	
	def present_tutorial(self, *args):

		self.protocol_floatlayout.clear_widgets()
		
		self.tutorial_hold = ImageButton(source=self.hold_button_image_path)
		self.tutorial_hold.size_hint = ((self.hold_button_x_size * self.width_adjust), (self.hold_button_y_size * self.height_adjust))
		self.tutorial_hold.pos_hint = {"center_x": self.hold_button_x_pos, "center_y": self.hold_button_y_pos}
		self.tutorial_hold.bind(on_press=self.tutorial_cue_screen)
		
		self.tutorial_continue = Button(text='CONTINUE TUTORIAL', font_size='48sp')
		self.tutorial_continue.size_hint = (0.4, 0.1)
		self.tutorial_continue.pos_hint = {"center_x": 0.5, "center_y": 0.95}
		self.tutorial_continue.bind(on_press=self.tutorial_delay_screen)
		
		self.tutorial_cue = ImageButton(source=self.stimulus_image_path)
		self.tutorial_cue.size_hint = self.stimulus_image_size
		self.tutorial_cue.pos_hint = {"center_x": 0.4, "center_y": 0.25}
		
		self.tutorial_delay_image = ImageButton(source=str(pathlib.Path(self.image_folder, 'delay_video_image.png')))
		self.tutorial_delay_image.size_hint = (1, 1)
		self.tutorial_delay_image.pos_hint = {"center_x": 0.5, "center_y": 0.55}
		
		self.tutorial_target = ImageButton(source=self.stimulus_image_path)
		self.tutorial_target.size_hint = self.stimulus_image_size
		self.tutorial_target.pos_hint = {"center_x": 0.6, "center_y": 0.25}
		self.tutorial_target.bind(on_press=self.tutorial_correct_screen)
		
		self.tutorial_start_button = Button(text='START', font_size='48sp')
		self.tutorial_start_button.size_hint = (0.4, 0.1)
		self.tutorial_start_button.pos_hint = {"center_x": 0.25, "center_y": 0.95}
		self.tutorial_start_button.bind(on_press=self.start_protocol_from_tutorial)
		
		self.tutorial_restart_button = Button(text='RESTART TUTORIAL', font_size='48sp')
		self.tutorial_restart_button.size_hint = (0.4, 0.1)
		self.tutorial_restart_button.pos_hint = {"center_x": 0.75, "center_y": 0.95}
		self.tutorial_restart_button.bind(on_press=self.present_tutorial)
		
		self.tutorial_label = Label(font_size='35sp')
		self.tutorial_label.size_hint = (0.6, 0.4)
		self.tutorial_label.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
		self.tutorial_label.text = 'The following screens will teach you how to perform this task.\n\nBefore each trial, you will see a white square at the bottom of the screen.\n\nYou will need to hold this square as long as it remains on the screen,\notherwise the trial will be cancelled.\n\nPress and hold the white square below to start the trial.'
		# self.tutorial_label.text = 'PRESS BELOW TO START TASK'
		
		self.protocol_floatlayout.add_widget(self.tutorial_label)
		self.protocol_floatlayout.add_widget(self.tutorial_hold)

		# self.delay_video

		# with self.protocol_floatlayout.canvas.before:
		# 	# context_instructions.PushMatrix()
		# 	# context_instructions.Translate(0,0)
		# 	context_instructions.PushMatrix()
		# 	context_instructions.Rotate(angle=-45)
		# 	self.protocol_floatlayout.add_widget(self.delay_video)

		# # self.protocol_floatlayout.add_widget(self.delay_video)

		# self.protocol_floatlayout.canvas.after

		# self.delay_video.state = 'play'

		# with self.protocol_floatlayout.canvas.before:
		# 	# context_instructions.PushMatrix()
		# 	# context_instructions.Translate(0,0)
		# 	context_instructions.PushMatrix()
		# 	context_instructions.Rotate(angle=45)
		# 	self.protocol_floatlayout.add_widget(self.tutorial_start_button)
		
		# with self.protocol_floatlayout.canvas.before:
		# 	context_instructions.PopMatrix()
		

		# self.protocol_floatlayout.add_widget(self.tutorial_start_button)

		# self.protocol_floatlayout.canvas.after


		# self.trial_coord = self.generate_trial_pos_sep(
		# 	self.x_boundaries
		# 	, self.y_boundaries
		# 	, self.current_sep
		# 	, self.stimulus_image_spacing
		# 	)

		# self.cue_image.pos_hint = {
		# 	'center_x': self.trial_coord['Cue']['x']
		# 	, 'center_y': self.trial_coord['Cue']['y']
		# 	}

		# self.cue_image_button.pos_hint = {
		# 	'center_x': self.trial_coord['Cue']['x']
		# 	, 'center_y': self.trial_coord['Cue']['y']
		# 	}
		
		# print('Cue x:', self.trial_coord['Cue']['x'])
		# print('Cue y:', self.trial_coord['Cue']['y'])

		# self.target_image.pos_hint = {
		# 	'center_x': self.trial_coord['Target']['x']
		# 	, 'center_y': self.trial_coord['Target']['y']
		# 	}
		
		# self.target_image_button.pos_hint = {
		# 	'center_x': self.trial_coord['Target']['x']
		# 	, 'center_y': self.trial_coord['Target']['y']
		# 	}
		
		# print('Target x:', self.trial_coord['Target']['x'])
		# print('Target y:', self.trial_coord['Target']['y'])
		
		# self.protocol_floatlayout.add_widget(self.cue_image)
		# self.protocol_floatlayout.add_widget(self.cue_image_button)

		# self.protocol_floatlayout.add_widget(self.target_image)
		# self.protocol_floatlayout.add_widget(self.target_image_button)

		# print(self.test_image.texture_size)
		# print(self.test_image.norm_image_size)
	
	
	
	def tutorial_cue_screen(self, *args):
		
		time.sleep(1)

		self.protocol_floatlayout.clear_widgets()
		
		self.tutorial_label.text = 'At the start of the trial, you will be presented with a small white circle on the screen.\nThis square is the cue.\n\nDuring this test, you will have ' + str(self.stimdur) + ' seconds to memorize the location of the cue.\n\nDuring the cue presentation, you will need to continue holding the white square at the\nbottom of the screen.\n\nFor this tutorial, press "CONTINUE TUTORIAL" above to continue.'
		
		self.tutorial_hold.unbind(on_press=self.tutorial_cue_screen)

		self.protocol_floatlayout.add_widget(self.tutorial_label)
		self.protocol_floatlayout.add_widget(self.tutorial_hold)
		self.protocol_floatlayout.add_widget(self.tutorial_cue)
		self.protocol_floatlayout.add_widget(self.tutorial_continue)
	
	
	
	def tutorial_delay_screen(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		self.tutorial_label.text = 'Next, there will be a short delay period.\nDuring this delay, you will be shown a video clip.\n\nDuring the video, you will need to continue holding the white square \n at the bottom of the screen.\n\nFor this tutorial, press "CONTINUE TUTORIAL" above to continue.'
		# self.tutorial_label.text = 'Next, there will be a short delay period.\nDuring this delay, you will be shown a portion of a video.\n\nDuring the video, you will need to continue holding the white square at\nthe bottom of the screen.\n\nFor this tutorial, press "CONTINUE TUTORIAL" above to start the video.'
		
		self.tutorial_continue.unbind(on_press=self.tutorial_delay_screen)
		self.tutorial_continue.bind(on_press=self.tutorial_target_screen)
		
		self.protocol_floatlayout.add_widget(self.delay_video)
		self.delay_video.state = 'pause'
		
		self.protocol_floatlayout.add_widget(self.tutorial_delay_image)
		self.protocol_floatlayout.add_widget(self.tutorial_label)
		self.protocol_floatlayout.add_widget(self.tutorial_hold)
		self.protocol_floatlayout.add_widget(self.tutorial_continue)
	


	def tutorial_delay_screen_video(self, *args):
		
		self.protocol_floatlayout.clear_widgets()

		self.tutorial_continue.bind(on_press=self.tutorial_target_screen)
	
		self.protocol_floatlayout.add_widget(self.tutorial_delay_image)
		self.protocol_floatlayout.add_widget(self.tutorial_continue)
	
	
	
	def tutorial_target_screen(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		self.tutorial_label.text = 'Finally, you will see two white circles.\nOne of these (on the left) is the cue you saw previously.\nThe other (on the right) is new.\n\nYour goal is to correctly identify the new circle (the target).\n\nTo respond, lift your finger from the white square and tap the \ncircle in the new location.\n\nDuring this test, you will have ' + str(self.limhold) + ' seconds to select the target.\n\nTap the target to continue.'

		self.tutorial_cue.bind(on_press=self.tutorial_incorrect_screen)
		
		self.protocol_floatlayout.add_widget(self.tutorial_label)
		self.protocol_floatlayout.add_widget(self.tutorial_cue)
		self.protocol_floatlayout.add_widget(self.tutorial_target)
	
	
	
	def tutorial_incorrect_screen(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		self.tutorial_label.text = 'Good try, but you have selected the original cue.\n\nYour aim is to select the new circle (the target).\n\nPlease tap the target (on the right) to continue.'

		self.tutorial_cue.unbind(on_press=self.tutorial_incorrect_screen)
		
		self.protocol_floatlayout.add_widget(self.tutorial_label)
		self.protocol_floatlayout.add_widget(self.tutorial_cue)
		self.protocol_floatlayout.add_widget(self.tutorial_target)
	
	
	
	def tutorial_correct_screen(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		self.tutorial_label.text = 'Great, you have selected the target!\n\nThe rest of this task will be like this tutorial, although \nthe duration of the video clip and circle locations will change.\n\nPress the "START" button above to start the task,\nor press "RESTART TUTORIAL" to do the tutorial again.'
		
		self.protocol_floatlayout.add_widget(self.tutorial_label)
		self.protocol_floatlayout.add_widget(self.tutorial_start_button)
		self.protocol_floatlayout.add_widget(self.tutorial_restart_button)
	
	
	


	# Protocol Staging

		
	def present_tutorial_video(self, *args):
		
		# self.tutorial_continue = Button(text='CONTINUE', font_size='48sp')
		# self.tutorial_continue.size_hint = self.text_button_size
		# self.tutorial_continue.pos_hint = self.text_button_pos_LC
		# self.tutorial_continue.bind(on_press=self.tutorial_target_present_screen)
		
		self.tutorial_start_button = Button(text='START', font_size='48sp')
		self.tutorial_start_button.size_hint = self.text_button_size
		self.tutorial_start_button.pos_hint = self.text_button_pos_LC #{'center_x': 0.5, 'center_y': 0.2} 
		self.tutorial_start_button.bind(on_press=self.start_protocol_from_tutorial)

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_widget(self.tutorial_video)
		self.tutorial_video.state = 'play'

		if self.skip_tutorial_video == 1:
			
			self.tutorial_video_end_event = self.presentation_clock.schedule_once(self.present_tutorial_video_start_button, 0)
		
		else:

			self.tutorial_video_end_event = self.presentation_clock.schedule_once(self.present_tutorial_video_start_button, 73)
	


	def present_tutorial_video_start_button(self, *args):

		self.tutorial_video_end_event.cancel()

		self.tutorial_video.state = 'pause'

		self.protocol_floatlayout.add_widget(self.tutorial_start_button)
	


	# def tutorial_target_present_screen(self, *args):

	# 	self.tutorial_video_end_event.cancel()

	# 	self.tutorial_video.state = 'stop'

	# 	self.protocol_floatlayout.remove_widget(self.tutorial_video)
	# 	self.protocol_floatlayout.remove_widget(self.tutorial_continue)

	# 	self.protocol_floatlayout.add_widget(self.tutorial_start_button)
	
	
	
	def start_protocol_from_tutorial(self, *args):
		
		self.generate_output_files()
		self.metadata_output_generation()
		self.start_protocol()
	
	
	
	
	
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
	
	
	
	def start_protocol(self, *args):
		
		print('Start protocol')
		
		self.protocol_floatlayout.clear_widgets()
	
		self.protocol_floatlayout.add_widget(self.hold_button)
		
		self.protocol_floatlayout.add_event([0
											, 'Button Removed'
											, 'Task Start Button'
											])
		
		self.protocol_floatlayout.add_event([0
											, 'Text Removed'
											, 'Task Instruction'
											])
		
		self.protocol_floatlayout.add_event([0
											, 'Button Displayed'
											, 'Hold Button'
											])
		
		self.protocol_floatlayout.add_event([0
											, 'Stage Change'
											, 'Current Probe'
											, self.current_stage
											])
		
		self.protocol_floatlayout.add_event([0
											, 'Stage Change'
											, 'Instruction Presentation'
											])
		
		self.printlog('Screen resolution: ', self.screen_resolution)
		
		self.printlog('Width adjust: ', self.width_adjust)
		self.printlog('height adjust: ', self.height_adjust)
		
		self.start_clock()
		
		self.block_start_time = time.time()
		
		self.feedback_label.text = ''
		
		
	




	

		
		
		
	
	
	
	
	
	
	
	
	
	def cue_present(self, *args): # Present cue
		
		self.printlog('Cue presentation')
		
		self.hold_button.unbind(on_press=self.iti)
		self.hold_button.unbind(on_release=self.premature_response)
		
		self.hold_button.bind(on_press=self.hold_returned)
		self.hold_button.bind(on_release=self.hold_released)
		
		self.cue_image_button.unbind(on_press=self.cue_pressed)
		
		self.protocol_floatlayout.add_widget(self.cue_image)
		self.protocol_floatlayout.add_widget(self.cue_image_button)
		
		self.stimulus_on_screen = True
		self.cue_completed = True
		self.delay_active = False
		self.delay_ended = False
		self.limhold_started = False
		
		self.cue_start_time = time.time()
		
		self.protocol_floatlayout.add_event([self.cue_start_time - self.start_time
											, 'Stage Change'
											, 'Display Cue'
											])
		
		self.protocol_floatlayout.add_event([self.cue_start_time - self.start_time
											, 'Image Displayed'
											, 'Cue Image'
											, 'X Position'
											, self.trial_coord['Cue']['x']
											, 'Y Position'
											, self.trial_coord['Cue']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		self.printlog('Cue start time: ', (self.cue_start_time - self.start_time))
		self.printlog('Cue x coord: ', self.trial_coord['Cue']['x'])
		self.printlog('Cue y coord: ', self.trial_coord['Cue']['y'])
		
		self.stimulus_event()
	


	# Display Distractor During Delay
	
	def delay_present(self, *args):

		self.cue_present_event.cancel()
		self.stimulus_event.cancel()

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_widget(self.hold_button)
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'Delay Start'
											])
		
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Removed'
											, 'Cue Image'
											, 'X Position'
											, self.trial_coord['Cue']['x']
											, 'Y Position'
											, self.trial_coord['Cue']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		# self.current_delay = 4
		
		self.delay_end_event = self.presentation_clock.schedule_once(self.delay_end, self.current_delay)

		self.protocol_floatlayout.add_widget(self.delay_video)
		self.delay_video.state = 'play'

		self.video_start_time = time.time()

		self.delay_active = True

		self.protocol_floatlayout.add_event([self.video_start_time - self.start_time
											, 'Video Displayed'
											, self.distractor_video
											, 'Video Position'
											, self.video_position
											])
	


	# Display Distractor During Delay
	
	def delay_end(self, *args):

		self.delay_present_event.cancel()

		self.delay_video.state = 'pause'
		# self.protocol_floatlayout.remove_widget(self.delay_video)

		self.protocol_floatlayout.clear_widgets()

		self.video_end_time = time.time()

		self.video_time = self.video_end_time - self.video_start_time

		self.video_position += self.video_time

		self.delay_ended = True
		self.delay_active = False
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'Delay End'
											])
		

		self.protocol_floatlayout.add_event([self.video_end_time - self.start_time
											, 'Video Removed'
											, self.distractor_video
											, 'Video Duration'
											, self.video_time
											, 'Video Position'
											, self.video_position
											])
		

		self.target_present_event()
	
	
	
	def target_present(self, *args): # Present stimulus

		self.delay_end_event.cancel()
		
		self.printlog('Target presentation')
		
		self.hold_button.unbind(on_press=self.hold_returned)
		self.hold_button.unbind(on_release=self.hold_released)

		self.cue_image_button.bind(on_press=self.cue_pressed)
		
		self.protocol_floatlayout.add_widget(self.cue_image)
		self.protocol_floatlayout.add_widget(self.target_image)

		self.protocol_floatlayout.add_widget(self.cue_image_button)
		self.protocol_floatlayout.add_widget(self.target_image_button)
		
		self.target_start_time = time.time()
		
		self.stimulus_on_screen = True
		self.limhold_started = True
		self.cue_completed = False
		
		self.feedback_string = ''
		self.feedback_label.text = self.feedback_string
			
		self.printlog('Start target time: ', (self.target_start_time - self.start_time))
		self.printlog('Delay length: ', self.current_delay)
		self.printlog('Target x coord: ', self.trial_coord['Target']['x'])
		self.printlog('Target y coord: ', self.trial_coord['Target']['y'])
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'Display Cue'
											])
		
		self.protocol_floatlayout.add_event([self.target_start_time - self.start_time
											, 'Stage Change'
											, 'Display Target'
											])
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Displayed'
											, 'Cue Image'
											, 'X Position'
											, self.trial_coord['Cue']['x']
											, 'Y Position'
											, self.trial_coord['Cue']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		self.protocol_floatlayout.add_event([self.target_start_time - self.start_time
											, 'Image Displayed'
											, 'Target Image'
											, 'X Position'
											, self.trial_coord['Target']['x']
											, 'Y Position'
											, self.trial_coord['Target']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		# self.hold_button.unbind(on_press=self.hold_returned)
		# self.hold_button.unbind(on_release=self.hold_released)
		
		# self.hold_button.bind(on_press=self.iti)
		# self.hold_button.bind(on_release=self.premature_response)
			
		self.stimulus_event()
	
	
	
	def stimulus_presentation(self, *args): # Stimulus presentation
		
		if not self.stimulus_on_screen \
			and not self.cue_completed \
			and not self.delay_active \
			and not self.limhold_started:

			self.cue_present_event() 
		
		
		elif self.stimulus_on_screen \
			and not self.limhold_started \
			and (time.time() - self.cue_start_time) < self.stimdur \
			and self.hold_active:
			
			self.stimulus_event()
		

		elif self.stimulus_on_screen \
			and not self.limhold_started \
			and (time.time() - self.cue_start_time) >= self.stimdur \
			and self.hold_active:

			self.stimulus_event.cancel()
			self.delay_present_event()
		
		
		elif self.stimulus_on_screen \
			and self.limhold_started \
			and (time.time() - self.target_start_time) < self.limhold:
			
			self.stimulus_event()
		

		else:

			self.stimulus_event.cancel()
			self.target_present_event.cancel()
			self.no_response()


	
	
	
	
	
	
	
	
	
	
	
	
	
	

	
	
	

	
	
	
	
	
	
	
	def hold_returned(self, *args):
		
		self.hold_active = True

		return
	


	def hold_released(self, *args):
		
		self.protocol_floatlayout.clear_widgets()

		self.hold_button.unbind(on_press=self.hold_returned)
		self.hold_button.unbind(on_release=self.hold_released)

		self.hold_active = False

		if self.stimulus_on_screen \
			and not self.cue_completed:

			return

		self.printlog('Hold released; trial aborted.')
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'State Change'
			, 'Hold Released'
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'State Change'
			, 'Trial Aborted'
			])

		self.stimulus_event.cancel()

		self.cue_present_event.cancel()
		self.target_present_event.cancel()
		self.delay_present_event.cancel()
		self.delay_end_event.cancel()
		
		if self.stimulus_on_screen \
			and self.cue_completed:

			self.printlog('Trial aborted during cue presentation.')

			self.protocol_floatlayout.add_event([time.time() - self.start_time
				, 'Image Removed'
				, 'Cue Image'
				, 'X Position'
				, self.trial_coord['Cue']['x']
				, 'Y Position'
				, self.trial_coord['Cue']['y']
				, 'Image Name'
				, self.stimulus_image
				])

		elif self.delay_active:

			self.printlog('Trial aborted during delay presentation.')

			self.delay_video.state = 'pause'

			self.video_end_time = time.time()

			self.video_time = self.video_end_time - self.video_start_time

			self.video_position += self.video_time

			self.protocol_floatlayout.add_event([self.video_end_time - self.start_time
				, 'Video Removed'
				, self.distractor_video
				, 'Video Duration'
				, self.video_time
				, 'Video Position'
				, self.video_position
				])
		
		self.feedback_string = self.feedback_dict['abort']
		self.feedback_label.text = self.feedback_string

		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		self.protocol_floatlayout.add_widget(self.hold_button)

		self.protocol_floatlayout.add_widget(self.feedback_label)

		self.feedback_start = time.time()
		
		self.protocol_floatlayout.add_event([self.feedback_start - self.start_time
			, 'Text Displayed'
			, 'Feedback'
			])
		
		self.stimulus_on_screen = False
		self.cue_completed = False
		self.delay_active = False
		self.delay_ended = False
		self.limhold_started = False
		self.feedback_on_screen = True
		
		self.last_response = 0
		
		self.write_trial()
		
		self.trial_contingency()
		
		return
	





	
	
	
	# Hold released too early
	
	def premature_response(self, *args):
		
		
		self.printlog('Premature response')
		
		if self.stimulus_on_screen is True:
			
			return

	
		self.hold_active = False
		
		Clock.unschedule(self.iti)
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'Premature Response'
											])
		

		self.feedback_string = self.feedback_dict['abort']
		self.response_lat = 0
		self.iti_active = False
		self.feedback_label.text = self.feedback_string
		
		if self.feedback_on_screen is False:
			
			self.protocol_floatlayout.add_widget(self.feedback_label)
		
			self.feedback_start = time.time()
			
			self.protocol_floatlayout.add_event([self.feedback_start - self.start_time
												, 'Text Displayed'
												, 'Feedback'
												])
		
		
		self.hold_button.unbind(on_release=self.premature_response)
		self.hold_button.bind(on_press=self.iti)
	
	
	
	# Cue Stimuli Pressed during Target
	
	def cue_pressed(self, *args):
		
		self.printlog('Cue pressed')

		self.stimulus_event.cancel()
		
		self.last_response = -1
		
		self.accuracy_tracking.append(0)

		self.target_touch_time = time.time()
		self.target_lat = self.target_touch_time - self.target_start_time
		
		self.protocol_floatlayout.remove_widget(self.cue_image)
		self.protocol_floatlayout.remove_widget(self.target_image)

		self.protocol_floatlayout.remove_widget(self.cue_image_button)
		self.protocol_floatlayout.remove_widget(self.target_image_button)
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Removed'
											, 'Cue Image'
											, 'X Position'
											, self.trial_coord['Cue']['x']
											, 'Y Position'
											, self.trial_coord['Cue']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Removed'
											, 'Target Image'
											, 'X Position'
											, self.trial_coord['Target']['x']
											, 'Y Position'
											, self.trial_coord['Target']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'Incorrect Response'])
		

		self.feedback_string = self.feedback_dict['incorrect']
		self.feedback_label.text = self.feedback_string

		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		self.protocol_floatlayout.add_widget(self.hold_button)
		self.protocol_floatlayout.add_widget(self.feedback_label)
		
		self.feedback_start = time.time()
		
		self.protocol_floatlayout.add_event(
			[self.feedback_start - self.start_time
			, 'Text Displayed'
			, 'Feedback'
			])
		
		
		self.hold_active = False
		self.stimulus_on_screen = False
		self.cue_completed = False
		self.delay_active = False
		self.delay_ended = False
		self.limhold_started = False
		self.feedback_on_screen = True
		
		self.write_trial()
		
		self.trial_contingency()
		
		return
	
	
	
	# Target Stimuli Pressed during Target
	
	def target_pressed(self, *args):
		
		self.printlog('Target pressed')

		self.stimulus_event.cancel()
		
		self.last_response = 1
		
		self.accuracy_tracking.append(1)

		self.target_touch_time = time.time()
		self.target_lat = self.target_touch_time - self.target_start_time
		
		self.protocol_floatlayout.remove_widget(self.cue_image)
		self.protocol_floatlayout.remove_widget(self.target_image)
		
		self.protocol_floatlayout.remove_widget(self.cue_image_button)
		self.protocol_floatlayout.remove_widget(self.target_image_button)
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Removed'
											, 'Cue Image'
											, 'X Position'
											, self.trial_coord['Cue']['x']
											, 'Y Position'
											, self.trial_coord['Cue']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Removed'
											, 'Target Image'
											, 'X Position'
											, self.trial_coord['Target']['x']
											, 'Y Position'
											, self.trial_coord['Target']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		

		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'Correct Response'
											])

		self.feedback_string = self.feedback_dict['correct']
		self.feedback_label.text = self.feedback_string

		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		self.protocol_floatlayout.add_widget(self.hold_button)
		self.protocol_floatlayout.add_widget(self.feedback_label)
		
		self.feedback_start = time.time()
		
		self.protocol_floatlayout.add_event([self.feedback_start - self.start_time
											, 'Text Displayed'
											, 'Feedback'
											])
		
		
		self.hold_active = False
		self.stimulus_on_screen = False
		self.cue_completed = False
		self.delay_active = False
		self.delay_ended = False
		self.limhold_started = False
		self.feedback_on_screen = True
		
		self.write_trial()
		
		self.trial_contingency()
		
		return
	
	
	
	# No response during test phase limited hold
	
	def no_response(self, *args):
		
		self.printlog('No response; limhold ended')

		self.stimulus_event.cancel()
		
		self.last_response = 0

		self.target_touch_time = time.time()
		self.target_lat = self.target_touch_time - self.target_start_time
		
		self.protocol_floatlayout.remove_widget(self.cue_image)
		self.protocol_floatlayout.remove_widget(self.target_image)
		
		self.protocol_floatlayout.remove_widget(self.cue_image_button)
		self.protocol_floatlayout.remove_widget(self.target_image_button)
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Removed'
											, 'Cue Image'
											, 'X Position'
											, self.trial_coord['Cue']['x']
											, 'Y Position'
											, self.trial_coord['Cue']['y']
											, 'Image Name'
											, self.stimulus_image
											])
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Image Removed'
											, 'Target Image'
											, 'X Position'
											, self.trial_coord['Target']['x']
											, 'Y Position'
											, self.trial_coord['Target']['y']
											, 'Image Name'
											, self.stimulus_image
											])

		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'No Response'
											])
		
		# self.feedback_string = self.feedback_dict['miss']
		# self.feedback_label.text = self.feedback_string

		self.feedback_label.text = ''

		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		self.protocol_floatlayout.add_widget(self.hold_button)
		# self.protocol_floatlayout.add_widget(self.feedback_label)

		# self.feedback_start = time.time()
		
		# self.protocol_floatlayout.add_event([self.feedback_start - self.start_time
		# 									, 'Text Displayed'
		# 									, 'Feedback'
		# 									])
		
		self.stimulus_on_screen = False
		self.cue_completed = False
		self.delay_active = False
		self.delay_ended = False
		self.limhold_started = False
		# self.feedback_on_screen = True
		
		self.write_trial()
		
		self.trial_contingency()
		
		if self.hold_active == True:

			self.hold_active = False

			self.iti()
		

		return
	
	
	
	# # Hold removed during cue or delay
	
	# def trial_abort(self, *args):
		
	# 	self.printlog('Hold released; trial aborted.')

	# 	self.abort_event.cancel()
		
	# 	self.last_response = 0
		
	# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
	# 										, 'Stage Change'
	# 										, 'Trial Aborted'
	# 										])
		
	# 	# self.target_touch_time = time.time()
	# 	self.target_lat = 0.0 #self.target_touch_time - self.target_start_time

	# 	self.protocol_floatlayout.clear_widgets()

	# 	# self.protocol_floatlayout.remove_widget(self.cue_image_button)
		
	# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
	# 										, 'Image Removed'
	# 										, 'Cue Image'
	# 										, 'X Position'
	# 										, self.trial_coord['Cue']['x']
	# 										, 'Y Position'
	# 										, self.trial_coord['Cue']['y']
	# 										, 'Image Name'
	# 										, self.stimulus_image
	# 										])
		
	# 	# self.protocol_floatlayout.remove_widget(self.target_image_button)
		
	# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
	# 										, 'Image Removed'
	# 										, 'Target Image'
	# 										, 'X Position'
	# 										, self.trial_coord['Target']['x']
	# 										, 'Y Position'
	# 										, self.trial_coord['Target']['y']
	# 										, 'Image Name'
	# 										, self.stimulus_image
	# 										])
		
	# 	self.feedback_string = self.feedback_dict['abort']
	# 	self.feedback_label.text = self.feedback_string

	# 	self.protocol_floatlayout.add_widget(self.feedback_label)

	# 	self.feedback_start = time.time()
		
	# 	self.protocol_floatlayout.add_event([self.feedback_start - self.start_time
	# 										, 'Text Displayed'
	# 										, 'Feedback'
	# 										])
		
		
		
	# 	self.stimulus_on_screen = False
	# 	self.cue_completed = False
	# 	self.delay_active = False
	# 	self.delay_ended = False
	# 	self.limhold_started = False
	# 	self.feedback_on_screen = True

	# 	self.hold_button.unbind(on_press=self.hold_returned)
	# 	self.hold_button.unbind(on_release=self.hold_released)

	# 	self.hold_button.bind(on_press=self.iti)
	# 	self.hold_button.bind(on_release=self.premature_response)
		
	# 	self.write_trial()
		
	# 	self.trial_contingency()
		
	# 	self.protocol_floatlayout.add_widget(self.hold_button)
		
	# 	return
	
	
	
	# Data Saving Function
	
	def write_trial(self):
		
		
		self.printlog('Write trial')
		
		cue_x = self.trial_coord['Cue']['x']
		cue_y = self.trial_coord['Cue']['y']
		target_x = self.trial_coord['Target']['x']
		target_y = self.trial_coord['Target']['y']
		
		trial_data = [
						self.current_trial
						, self.current_block
						, self.current_stage
						, self.current_sep
						, self.current_delay
						, self.video_position
						, (cue_x + 1)
						, (cue_y + 1)
						, (target_x + 1)
						, (target_y + 1)
						# , num_distractors
						, self.last_response
						, self.target_lat
						]
		
		self.write_summary_file(trial_data)
		
		return
	
	
	
	# Trial Contingency Functions
	
	def trial_contingency(self):
		
		
		try:
			
			if self.hold_active:

				self.hold_active = False


			if self.current_block_trial != 0:
				
				self.printlog('\n\n\n')
				self.printlog('Trial contingency start')
				self.printlog('')
				self.printlog('Current stage: ', self.current_stage)
				self.printlog('Current block: ', self.current_block)
				self.printlog('Current trial: ', self.current_trial)
				self.printlog('Current task time: ', (time.time() - self.start_time))
				self.printlog('Current block time: ', (time.time() - self.block_start_time))
				self.printlog('')
				self.printlog('ITI: ', self.iti_length)
				self.printlog('Separation: ', self.current_sep)
				self.printlog('Delay: ', self.current_delay)
				self.printlog('Video position: ', self.video_position)
				
				self.printlog('')
				self.printlog('Last response: ', self.last_response)
				self.printlog('Target latency: ', self.target_lat)
				# self.printlog('Cue to target time: ', self.cue_press_to_target)
				self.printlog('')
				

				if self.last_response != 0:
					self.response_tracking.append(self.last_response)
				

				if self.current_delay >= self.max_delay \
					and len(self.response_tracking) > 3:

					del self.response_tracking[1]


				if (len(self.response_tracking) >= 2) \
					and (sum(self.response_tracking) < 0):

					self.staircase_change = 'dec'
					self.response_tracking = list()

				elif (len(self.response_tracking) >= 2) \
					and (sum(self.response_tracking) > 0):

					self.staircase_change = 'inc'
					self.response_tracking = list()
				
				else:

					self.staircase_change = 'non'

				# Adjust staircasing
				
				# if self.last_response == 1:
				if self.staircase_change == 'inc':
					
					self.printlog('Performance over chance.')
				
					if self.current_stage == 'Space':

						self.space_probe_delay_list[self.space_trial_index] += self.space_probe_staircase_list[self.space_trial_index]
						self.space_probe_response_list[self.space_trial_index] = self.last_response


					elif self.current_stage == 'Delay':

						self.delay_probe_sep_list[self.delay_trial_index] -= 1
						self.delay_probe_response_list[self.delay_trial_index] = self.last_response

						if self.delay_probe_sep_list[self.delay_trial_index] < self.min_sep:

							self.delay_probe_sep_list[self.delay_trial_index] = self.min_sep


					elif self.current_stage == 'Combo':

						self.combo_probe_delay_tracking_dict[self.current_sep].append(self.current_delay)

						# # if (len(self.combo_probe_delay_tracking_dict[self.current_sep]) > 10) \
						# # 	and (max(self.combo_probe_delay_tracking_dict[self.current_sep][-5:]) - min(self.combo_probe_delay_tracking_dict[self.current_sep][-5:]) <= 3):
						# if (time.time() - self.block_start_time) >= (self.combo_probe_max_section_dur * (self.combo_trial_index + 1)):

						# 	self.combo_trial_index += 1

						# 	if self.combo_trial_index < len(self.combo_probe_sep_list):

						# 		self.current_sep = self.combo_probe_sep_list[self.combo_trial_index]
						# 		self.current_delay = self.combo_probe_delay_list[self.combo_trial_index]						

						# 	else:

						# 		self.block_check_event()


						self.combo_probe_delay_list[self.combo_trial_index] += self.combo_probe_staircase_list[self.combo_trial_index]

						self.last_staircase_time_increase = self.combo_probe_staircase_list[self.combo_trial_index]

						if self.combo_probe_delay_list[self.combo_trial_index] > self.max_delay:

							self.combo_probe_delay_list[self.combo_trial_index] = self.max_delay
						
						self.current_delay = self.combo_probe_delay_list[self.combo_trial_index]
						
						self.combo_probe_response_list[self.combo_trial_index] = self.last_response
						
						
				# elif self.last_response == -1:
				if self.staircase_change == 'dec':
					
					self.printlog('Performance under chance.')
				
					if self.current_stage == 'Space':

						if self.space_probe_response_list[self.space_trial_index] == 1:

							self.space_probe_staircase_list[self.space_trial_index] /= 2

						self.space_probe_delay_list[self.space_trial_index] -= self.space_probe_staircase_list[self.space_trial_index]
						self.space_probe_response_list[self.space_trial_index] = self.last_response

						if self.space_probe_delay_list[self.space_trial_index] < self.min_delay:

							self.space_probe_delay_list[self.space_trial_index] = self.min_delay
					

					elif self.current_stage == 'Delay':

						self.delay_probe_sep_list[self.delay_trial_index] += 1
						self.delay_probe_response_list[self.delay_trial_index] = self.last_response

						if self.delay_probe_sep_list[self.delay_trial_index] > self.max_sep:

							self.delay_probe_sep_list[self.delay_trial_index] = self.max_sep
					

					elif self.current_stage == 'Combo':

						# if self.combo_probe_response_list[self.combo_trial_index] == 1:
						if self.combo_probe_staircase_list[self.combo_trial_index] == self.last_staircase_time_increase:

							self.combo_probe_staircase_list[self.combo_trial_index] /= 2

						self.combo_probe_delay_list[self.combo_trial_index] -= self.combo_probe_staircase_list[self.combo_trial_index]

						if self.combo_probe_delay_list[self.combo_trial_index] < self.min_delay:

							self.combo_probe_delay_list[self.combo_trial_index] = self.min_delay
						

						self.current_delay = self.combo_probe_delay_list[self.combo_trial_index]

						self.combo_probe_response_list[self.combo_trial_index] = self.last_response
				

				if self.current_stage == 'Combo' \
					and ((time.time() - self.block_start_time) >= (self.combo_probe_max_section_dur * (self.combo_trial_index + 1))):

					# if (len(self.combo_probe_delay_tracking_dict[self.current_sep]) > 10) \
					# 	and (max(self.combo_probe_delay_tracking_dict[self.current_sep][-5:]) - min(self.combo_probe_delay_tracking_dict[self.current_sep][-5:]) <= 3):
					# if (time.time() - self.block_start_time) >= (self.combo_probe_max_section_dur * (self.combo_trial_index + 1)):

					self.combo_trial_index += 1

					if self.combo_trial_index < len(self.combo_probe_sep_list):

						self.current_sep = self.combo_probe_sep_list[self.combo_trial_index]
						self.combo_probe_delay_list[self.combo_trial_index] = self.current_delay

					else:

						self.block_check_event()


				if (time.time() - self.block_start_time >= self.block_duration):
					# or (self.current_trial >= self.block_length):

					self.current_block += 1
				
					self.protocol_floatlayout.add_event([time.time() - self.start_time
														, 'Block Change'
														, 'Current Probe'
														, 'Value'
														, str(self.current_stage)
														])
					
					self.block_check_event()
			



			
			# Set next trial parameters

			# Trial number and trial index

			self.current_trial += 1
			self.current_block_trial += 1
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Variable Change'
				, 'Parameter'
				, 'Current Trial'
				, str(self.current_trial)
				])
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Variable Change'
				, 'Parameter'
				, 'Current Block Trial'
				, str(self.current_block_trial)
				])
			
			
			# Set ITI

			if len(self.iti_range) > 1:
				
				if self.iti_fixed_or_range == 'fixed':
					
					self.iti_length = random.choice(self.iti_range)
				
				
				else:
					
					self.iti_length = round(random.uniform(min(self.iti_range), max(self.iti_range)), 2)
				
				
				self.protocol_floatlayout.add_event([
					time.time() - self.start_time
					, 'Variable Change'
					, 'Current ITI'
					, 'Value'
					, str(self.iti_length)
					])
			


			
			
			if self.current_stage == 'Space':
				
				if self.trial_index >= len(self.space_trial_index_list):
					
					self.trial_index = 0
					random.shuffle(self.space_trial_index_list)
				
				self.space_trial_index = self.space_trial_index_list[self.trial_index]
				
				self.current_sep = self.space_probe_sep_list[self.space_trial_index]
				self.current_delay = self.space_probe_delay_list[self.space_trial_index]
			
			
			elif self.current_stage == 'Delay':
				
				if self.trial_index >= len(self.delay_trial_index_list):
					
					self.trial_index = 0
					random.shuffle(self.delay_trial_index_list)
				
				
				self.delay_trial_index = self.delay_trial_index_list[self.trial_index]
				
				self.current_sep = self.delay_probe_sep_list[self.delay_trial_index]
				self.current_delay = self.delay_probe_delay_list[self.delay_trial_index]
			
			
			# Set cue and target coordinates
			
			self.trial_coord = self.generate_trial_pos_sep(
				self.x_boundaries
				, self.y_boundaries
				, self.current_sep
				, self.stimulus_image_spacing
				, self.screen_x_padding
				, self.screen_y_padding_t
				, self.screen_y_padding_b
				)
			
			
			# Set cue and target locations
			
			self.cue_image.pos_hint = {
				"center_x": self.trial_coord['Cue']['x'], 
				"center_y": self.trial_coord['Cue']['y']
				}
			self.target_image.pos_hint = {
				"center_x": self.trial_coord['Target']['x'], 
				"center_y": self.trial_coord['Target']['y']
				}
			
			self.cue_image_button.pos_hint = {
				"center_x": self.trial_coord['Cue']['x'], 
				"center_y": self.trial_coord['Cue']['y']
				}
			self.target_image_button.pos_hint = {
				"center_x": self.trial_coord['Target']['x'], 
				"center_y": self.trial_coord['Target']['y']
				}
			

			
			self.protocol_floatlayout.add_event([time.time() - self.start_time
												, 'Variable Change'
												, 'Current Delay'
												, 'Value'
												, str(self.current_delay)
												])
			
			self.protocol_floatlayout.add_event([time.time() - self.start_time
												, 'Variable Change'
												, 'Current Separation'
												, 'Value'
												, str(self.current_sep)
												])
			
			self.protocol_floatlayout.add_event([time.time() - self.start_time
												, 'Variable Change'
												, 'Cue Position'
												, 'X Position'
												, str(self.trial_coord['Cue']['x'])
												, 'Y Position'
												, str(self.trial_coord['Cue']['y'])
												])
			
			self.protocol_floatlayout.add_event([time.time() - self.start_time
												, 'Variable Change'
												, 'Target Position'
												, 'X Position'
												, str(self.trial_coord['Target']['x'])
												, 'Y Position'
												, str(self.trial_coord['Target']['y'])
												])
			




			
			# if (time.time() - self.block_start_time >= self.block_duration) \
			# 	and self.current_block_trial > 1:
			# 	# or (self.current_trial >= self.block_length):

			# 	self.current_block += 1
			
			# 	self.protocol_floatlayout.add_event([time.time() - self.start_time
			# 										, 'Block Change'
			# 										, 'Current Probe'
			# 										, 'Value'
			# 										, str(self.current_stage)
			# 										])
				
			# 	self.block_check_event()
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()
	
	
	
	def section_start(self, *args):

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'State Change'
			, 'Section Start'
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Object Remove'
			, 'Text'
			, 'Type'
			, 'Instructions'
			, 'Value'
			, 'Section'
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Object Remove'
			, 'Button'
			, 'Type'
			, 'Continue'
			, 'Value'
			, 'Section'
			])
		
		self.block_end()
	




	



	def results_screen(
			self
			, *args
			):
		
		self.protocol_floatlayout.clear_widgets()
		self.feedback_on_screen = False

		self.hit_accuracy = sum(self.accuracy_tracking) / len(self.accuracy_tracking)

		self.outcome_string = 'Great job!\n\nYour overall accuracy was ' + str(round(self.hit_accuracy, 2) * 100) + '%!\n\nPlease inform the researcher that you have finished this task.'


		
		self.instruction_button.unbind(on_press=self.section_start)
		self.instruction_button.bind(on_press=self.protocol_end)
		self.instruction_button.text = 'End Task'

		self.section_instr_label.text = self.outcome_string

		self.protocol_floatlayout.add_widget(self.section_instr_label)
		self.protocol_floatlayout.add_widget(self.instruction_button)
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Object Display'
			, 'Text'
			, 'Stage'
			, 'Results'
			])


	
	
	
	# Block Contingency Function
	
	def block_contingency(self, *args):
		
		
		try:

			if self.feedback_on_screen:
				# self.printlog('Feedback on screen')
				
				if (time.time() - self.feedback_start_time) >= self.feedback_length:
					self.printlog('Feedback over')
					self.block_check_event.cancel()
					self.protocol_floatlayout.remove_widget(self.feedback_label)
					self.feedback_string = ''
					self.feedback_label.text = self.feedback_string
					self.feedback_on_screen = False
				else:
					# self.printlog('Wait for feedback delay')
					return
			else:
				self.printlog('Block check event cancel')
				self.block_check_event.cancel()
			
			
			self.printlog('\n\n\n\nBlock contingency\n\n')

			self.protocol_floatlayout.clear_widgets()

			self.printlog('Clear widgets')

			# self.trial_index = 0


			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'State Change'
				, 'Block Change'
				, 'Current Block'
				, self.current_block
				])
			
			self.printlog('Current block: ', self.current_block)
			self.printlog('Current task time: ', (time.time() - self.start_time))
			# self.printlog('Block duration: ', self.block_duration)

			
			if (self.current_block > self.block_multiplier) or (self.current_block == -1):

				self.stage_index += 1
				self.current_block = 1
				# self.response_tracking = [-2,-2]
				
				self.printlog('Stage index: ', self.stage_index)
			
	
			if self.stage_index >= len(self.stage_list): # Check if all stages complete

				self.printlog('All stages complete')
				self.session_event.cancel()
				# self.protocol_end()
				self.results_screen()

				return
			
			
			else:

				self.current_stage = self.stage_list[self.stage_index]
				self.printlog('Current stage: ', self.current_stage)

		
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'State Change'
					, 'Stage Change'
					, 'Current Stage'
					, self.current_stage
					])
			
			
			if self.current_stage == 'Space':
				
				random.shuffle(self.space_trial_index_list)
			
				# self.space_trial_index = self.space_trial_index_list[self.trial_index]
				
				# self.current_sep = self.space_probe_sep_list[self.space_trial_index]
				# self.current_delay = self.space_probe_delay_list[self.space_trial_index]
			
			
			elif self.current_stage == 'Delay':

				random.shuffle(self.delay_trial_index_list)
				
				# self.delay_trial_index = self.delay_trial_index_list[self.trial_index]
				
				# self.current_sep = self.delay_probe_sep_list[self.delay_trial_index]
				# self.current_delay = self.delay_probe_delay_list[self.delay_trial_index]
			
			
			elif self.current_stage == 'Combo':
				
				self.combo_trial_index = 0
				
				self.current_sep = self.combo_probe_sep_list[self.combo_trial_index]
				self.current_delay = self.combo_probe_delay_list[self.combo_trial_index]
			






			if (self.current_block == 1) and (self.stage_index == 0): #and self.display_instructions:
				
				self.printlog('Section Task Instructions')
				self.section_instr_label.text = self.instruction_dict[str(self.current_stage)]['task']
				
# 				self.block_max_length = 360
				
				# if self.current_stage == 'Training':
				# 	self.block_max_length = self.training_block_max_correct
				

				self.instruction_button.text = 'Begin Section'

				
				self.protocol_floatlayout.add_widget(self.section_instr_label)
				self.protocol_floatlayout.add_widget(self.instruction_button)
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Object Display'
					, 'Text'
					, 'Block'
					, 'Instructions'
					, 'Type'
					, 'Task'
					])
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Object Display'
					, 'Button'
					, 'Block'
					, 'Instructions'
					, 'Type'
					, 'Continue'
					])
			
			else:
				
				self.printlog('Else: Block Screen')
				self.block_event()
			



			self.response_tracking = list()
			self.last_response = 0
			self.contingency = 0
			self.trial_outcome = 0
			self.current_block_trial = 0
			self.trial_index = 0
				
			
			#self.present_instructions(self.stage_instructions)
			
	# 		self.current_block += 1
			
			self.printlog('Block contingency end')
			
			self.trial_contingency()
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()
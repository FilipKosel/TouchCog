# Imports #
import sys
import os
import configparser
import time
import numpy as np
import pandas as pd
import pathlib
import csv
import threading
import random
import statistics

from kivy.config import Config
from kivy.loader import Loader
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from Classes.Protocol import ImageButton, ProtocolBase

# from pathlib import Path





class ProtocolScreen(ProtocolBase):



	def __init__(self,**kwargs):

		super(ProtocolScreen,self).__init__(**kwargs)
		self.protocol_name = '3-hPAL'
		self.update_task()
		
		
		# Set screen size
		
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
			print('Width adjust: ', self.width_adjust)
			print('height adjust: ', self.height_adjust)
		
		
		elif width < height:
			
			
			self.width_adjust = 1
			self.height_adjust = width / height
			
			print('Width < Height')
			print('Width adjust: ', self.width_adjust)
			print('height adjust: ', self.height_adjust)
		
		
		elif width == height:
			
			
			self.width_adjust = 1
			self.height_adjust = 1
			
			print('Width = Height')
			print('Width adjust: ', self.width_adjust)
			print('height adjust: ', self.height_adjust)
		
		
		else:
			
			
			print('Screen resolution issue')
			
			self.width_adjust = 1
			self.height_adjust = 1
			
			print('Width adjust: ', self.width_adjust)
			print('height adjust: ', self.height_adjust)

		# Define Variables - Folder Path
		# self.image_folder = 'Protocol' + self.folder_mod + 'PAL' + self.folder_mod + 'Image' + self.folder_mod
		# self.data_output_path = None

		# Define Data Columns

		self.data_cols = [
			'TrialNo'
			, 'CurrentStage'
			, 'CurrentBlock'
			, 'BlockTrial'
			, 'TargetImage'
			, 'TargetLoc'
			, 'NontargetImage'
			, 'NontargetLoc'
			, 'Correct'
			, 'ResponseLat'
			]
		

		self.metadata_cols = [
			'participant_id'
			, 'skip_tutorial_video'
			, 'block_change_on_duration_only'
			, 'training_task'
			, 'dpal_probe'
			, 'spal_probe'
			, 'recall_probe'
			, 'iti_fixed_or_range'
			, 'iti_length'
			, 'feedback_length'
			, 'block_duration'
			, 'block_min_rest_duration'
			, 'session_duration'
			, 'block_multiplier'
			, 'dpal_trial_max'
			, 'spal_trial_max'
			, 'recall_trial_max'
			, 'training_block_max_correct'
			, 'num_stimuli_pal'
			, 'num_stimuli_pa'
			, 'num_rows'
			, 'training_image'
			]


		# Define Variables - Config

		self.protocol_path = pathlib.Path('Protocol', self.protocol_name)

		config_path = str(self.protocol_path / 'Configuration.ini')
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
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration = int(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])

		self.dpal_trial_max = int(self.parameters_dict['dpal_trial_max'])
		self.spal_trial_max = int(self.parameters_dict['spal_trial_max'])
		self.recall_trial_max = int(self.parameters_dict['recall_trial_max'])

		self.training_block_max_correct = int(self.parameters_dict['training_block_max_correct'])

		self.recall_target_present_duration = float(self.parameters_dict['recall_target_present_duration'])
		
		self.num_stimuli_pal = int(self.parameters_dict['num_stimuli_pal'])
		self.num_stimuli_pa = int(self.parameters_dict['num_stimuli_pa'])
		self.num_rows = int(self.parameters_dict['num_rows'])

		self.training_image = self.parameters_dict['training_image']

		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']
		
		self.correction_trials_enabled = False


		# Create stage list

		self.stage_list = list()



		# Define Language

		self.language = 'English'
		self.set_language(self.language)


		# Define Variables - Clock

		self.block_break_clock = Clock
		self.block_break_clock.interupt_next_only = False
		self.block_break_event = self.block_break_clock.create_trigger(self.block_break_screen, 0, interval=True)

		self.block_break_event.cancel()
		

		self.block_check_clock = Clock
		self.block_check_clock.interupt_next_only = False
		self.block_check_event = self.block_check_clock.create_trigger(self.block_contingency, 0, interval=True)

		self.block_check_event.cancel()
		

		self.task_clock = Clock
		self.task_clock.interupt_next_only = True
		
		self.recall_instruction_target_present_event = self.task_clock.create_trigger(self.recall_target_screen, 0, interval=True)
		self.recall_instruction_target_present_event.cancel()

		self.start_protocol_event = self.task_clock.schedule_once(self.start_protocol_from_tutorial, 0.5)
		self.start_protocol_event.cancel()


		# Define Variables - Time

		self.stimulus_start_time = 0.0
		self.stimulus_press_time = 0.0
		self.response_latency = 0.0
		
		self.iti_range = list()
		self.iti_length = 0.0

		self.recall_target_screen_start_time = 0.0


		# Define Variables - Numeric
		
		self.current_block = 0
		self.current_block_trial = 0
		# self.current_hits = 0
		
		self.stage_index = 0
		# self.trial_index = 0
		
		self.block_max_count = self.block_multiplier
		self.block_trial_max = 120

		self.last_response = 0

		self.response_tracking = [0,0]

		self.target_loc = 0
		self.nontarget_loc = 1
		self.nontarget_image_loc = 2
		self.last_target_loc = -1
		self.last_nontarget_loc = -1

		self.recall_target_display_pos = 0


		# Define Variables - String

		self.current_stage = ''

		self.target_image = ''
		self.nontarget_image = ''
		self.blank_image = ''
		self.recall_image = ''

		self.feedback_string = ''


		# Define Widgets - Image Paths

		self.image_folder = self.protocol_path / 'Image'

		self.target_folder = str(self.image_folder / 'Targets')

		self.outline_image = 'whitesquare'

		self.hold_image_path = str(self.image_folder / str(self.hold_image + '.png'))
		self.mask_image_path = str(self.image_folder / str(self.mask_image + '.png'))
		self.outline_image_path = str(self.image_folder / str(self.outline_image + '.png'))


		# Define Widgets - Images

		self.stimulus_grid_list = list()
		self.recall_stimulus = ImageButton()


		# Define Widgets - Instructions
		
		self.instruction_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'Instructions.ini'))
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Training'] = {}
		self.instruction_dict['dPAL'] = {}
		self.instruction_dict['sPAL'] = {}
		self.instruction_dict['Recall'] = {}
		
		
		instruction_temp_train_str = self.instruction_config['Training']['train']
		instruction_temp_probe_str = self.instruction_config['Training']['task']
		
		self.instruction_dict['Training']['train'] = instruction_temp_train_str
		self.instruction_dict['Training']['task'] = instruction_temp_train_str
		
		
		instruction_temp_train_str = self.instruction_config['dPAL']['train']
		instruction_temp_probe_str = self.instruction_config['dPAL']['task']
		
		self.instruction_dict['dPAL']['train'] = instruction_temp_train_str
		self.instruction_dict['dPAL']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['sPAL']['train']
		instruction_temp_probe_str = self.instruction_config['sPAL']['task']
		
		self.instruction_dict['sPAL']['train'] = instruction_temp_train_str
		self.instruction_dict['sPAL']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Recall']['train']
		instruction_temp_probe_str = self.instruction_config['Recall']['task']
		
		self.instruction_dict['Recall']['train'] = instruction_temp_train_str
		self.instruction_dict['Recall']['task'] = instruction_temp_probe_str




	# Initialization Functions #
		
	def load_parameters(self,parameter_dict):

		self.parameters_dict = parameter_dict

		config_path = str(self.protocol_path / 'Configuration.ini')
		config_file = configparser.ConfigParser()
		config_file.read(config_path)
		
		
		self.participant_id = self.parameters_dict['participant_id']
		self.age_range = self.parameters_dict['age_range']
		
		self.language = self.parameters_dict['language']

		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_import = self.parameters_dict['iti_length']
		iti_import = iti_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration = int(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])

		self.dpal_trial_max = int(self.parameters_dict['dpal_trial_max'])
		self.spal_trial_max = int(self.parameters_dict['spal_trial_max'])
		self.recall_trial_max = int(self.parameters_dict['recall_trial_max'])
		
		self.training_block_max_correct = int(self.parameters_dict['training_block_max_correct'])

		self.recall_target_present_duration = float(self.parameters_dict['recall_target_present_duration'])
		
		self.num_stimuli_pal = int(self.parameters_dict['num_stimuli_pal'])
		self.num_stimuli_pa = int(self.parameters_dict['num_stimuli_pa'])
		self.num_rows = int(self.parameters_dict['num_rows'])

		self.training_image = self.parameters_dict['training_image']

		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']
		
		self.correction_trials_enabled = False


		# Create stage list

		
		
		self.stage_list = list()
		
		if int(self.parameters_dict['training_task']) == 1:
			
			self.stage_list.append('Training')
		

		if int(self.parameters_dict['dpal_probe']) == 1:
			
			self.stage_list.append('dPAL')
		
		
		if int(self.parameters_dict['spal_probe']) == 1:
			
			self.stage_list.append('sPAL')
		
		
		if int(self.parameters_dict['recall_probe']) == 1:
			
			self.stage_list.append('Recall')


		# Define Language

		self.language = 'English'
		self.set_language(self.language)


		# Define Variables - Numeric
		
		self.current_block = 0
		self.current_block_trial = 0
		# self.current_hits = 0
		
		self.stage_index = 0
		# self.trial_index = 0
		
		self.block_max_count = self.block_multiplier
		self.block_trial_max = 120

		self.last_response = 0

		self.response_tracking = [0,0]

		self.target_loc = 0
		self.nontarget_loc = 1
		self.nontarget_image_loc = 2

		self.recall_target_display_pos = 0


		# Define Variables - String

		self.current_stage = ''
		self.feedback_string = ''
		
		self.target_image = self.mask_image
		self.nontarget_image = self.mask_image
		self.blank_image = self.mask_image
		self.recall_image = self.mask_image


		# Define Variables - Boolean

		self.images_loaded = False
		self.recall_instruction_target_display_started = False


		# Define Variables - Time

		self.stimulus_start_time = 0.0
		self.stimulus_press_time = 0.0
		self.response_latency = 0.0

		self.recall_target_screen_start_time = 0.0
		
		self.iti_range = [float(iNum) for iNum in iti_import]
		self.iti_length = self.iti_range[0]


		# Define Widgets - Images

		self.image_folder = self.protocol_path / 'Image'
		
		self.outline_image = 'whitecircle'

		self.hold_image_path = str(self.image_folder / str(self.hold_image + '.png'))
		self.mask_image_path = str(self.image_folder / str(self.mask_image + '.png'))
		self.outline_image_path = str(self.image_folder / str(self.outline_image + '.png'))
		self.training_image_path = str(self.image_folder / str(self.training_image + '.png'))

		self.stimulus_image_path_list = list()


		# if ('dPAL' or 'sPAL' or 'Training') in self.stage_list:
		if any(True for stage in ['dPAL', 'sPAL', 'Training'] if stage in self.stage_list):

			stimulus_path_list = list(pathlib.Path(self.image_folder).glob(str(pathlib.Path('PAL-Targets', '*.png'))))
			stimulus_image_list = list()

			for filename in stimulus_path_list:
				self.stimulus_image_path_list.append(filename)
				stimulus_image_list.append(filename.stem)
			
			if self.num_stimuli_pal > len(stimulus_image_list):
				self.num_stimuli_pal = len(stimulus_image_list)
			
			self.target_image_list_pal = list()

			while len(self.target_image_list_pal) < self.num_stimuli_pal:
				new_target = random.choice(stimulus_image_list)
				self.target_image_list_pal.append(new_target)
				stimulus_image_list.remove(new_target)


		if 'Recall' in self.stage_list:

			stimulus_path_list = list(pathlib.Path(self.image_folder).glob(str(pathlib.Path('PA-Targets', '*.png'))))
			stimulus_image_list = list()

			for filename in stimulus_path_list:
				self.stimulus_image_path_list.append(filename)
				stimulus_image_list.append(filename.stem)
			
			if self.num_stimuli_pa > len(stimulus_image_list):
				self.num_stimuli_pa = len(stimulus_image_list)
			
			self.target_image_list_pa = list()

			while len(self.target_image_list_pa) < self.num_stimuli_pa:
				new_target = random.choice(stimulus_image_list)
				self.target_image_list_pa.append(new_target)
				stimulus_image_list.remove(new_target)
		

		self.total_image_list = self.stimulus_image_path_list

		self.total_image_list += [self.hold_image_path, self.mask_image_path, self.outline_image_path, self.training_image_path]
		print('\n\nTotal image list: ', self.total_image_list, '\n\n')

		self.load_images(self.total_image_list)

		self.recall_stimulus = ImageButton(
			source = self.mask_image_path
			, size_hint = [0.3 * self.width_adjust, 0.3 * self.height_adjust]
			, pos_hint = {"center_x": 0.5, "center_y": 0.85}
			# , name = 'Recall Image'
			)
		
		self.hold_button.source = self.hold_image_path
		# self.hold_button.texture = self.image_dict[self.hold_image].image.texture
		self.hold_button.bind(on_press=self.iti)


		# Define trial lists

		self.trial_list = list()
		self.trial_list_pal = list()
		self.trial_list_pa = list()
		self.trial_list_index = 0

		for iNum in range(15):

			self.trial_list_pal.append(iNum % self.num_stimuli_pal)
			self.trial_list_pa.append(iNum % self.num_stimuli_pa)




		# # Define Widgets - Instructions
		
		# self.instruction_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'Instructions.ini'))
		
		# self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		# self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		# self.instruction_dict = {}
		# self.instruction_dict['Training'] = {}
		# self.instruction_dict['dPAL'] = {}
		# self.instruction_dict['sPAL'] = {}
		# self.instruction_dict['Recall'] = {}
		
		
		# instruction_temp_train_str = self.instruction_config['Training']['train']
		# instruction_temp_probe_str = self.instruction_config['Training']['task']
		
		# self.instruction_dict['Training']['train'] = instruction_temp_train_str
		# self.instruction_dict['Training']['task'] = instruction_temp_train_str
		
		
		# instruction_temp_train_str = self.instruction_config['dPAL']['train']
		# instruction_temp_probe_str = self.instruction_config['dPAL']['task']
		
		# self.instruction_dict['dPAL']['train'] = instruction_temp_train_str
		# self.instruction_dict['dPAL']['task'] = instruction_temp_probe_str
		
		
		# instruction_temp_train_str = self.instruction_config['sPAL']['train']
		# instruction_temp_probe_str = self.instruction_config['sPAL']['task']
		
		# self.instruction_dict['sPAL']['train'] = instruction_temp_train_str
		# self.instruction_dict['sPAL']['task'] = instruction_temp_probe_str
		
		
		# instruction_temp_train_str = self.instruction_config['Recall']['train']
		# instruction_temp_probe_str = self.instruction_config['Recall']['task']
		
		# self.instruction_dict['Recall']['train'] = instruction_temp_train_str
		# self.instruction_dict['Recall']['task'] = instruction_temp_probe_str
		
		
		# Instruction - Text Widget
		
		self.section_instr_string = self.instruction_label.text
		self.section_instr_label = Label(text=self.section_instr_string, font_size='44sp', markup=True)
		self.section_instr_label.size_hint = {0.9, 0.8}
		self.section_instr_label.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
		
		# Instruction - Button Widget
		
		self.instruction_button = Button(font_size='60sp')
		self.instruction_button.size_hint = [0.4, 0.15]
		self.instruction_button.pos_hint =  {"center_x": 0.50, "center_y": 0.1}
		self.instruction_button.text = ''
		self.instruction_button.bind(on_press=self.section_start)
		self.instruction_button_str = ''
		
		self.recall_instruction_button = Button(font_size='60sp')
		self.recall_instruction_button.size_hint = [0.4, 0.15]
		self.recall_instruction_button.pos_hint =  {"center_x": 0.50, "center_y": 0.1}
		self.recall_instruction_button.text = 'Display Targets'
		self.recall_instruction_button.bind(on_press=self.recall_instruction_target_present_event)
		self.recall_instruction_button = ''




		# self.protocol_floatlayout.add_widget(self.recall_stimulus)
		# self.protocol_floatlayout.remove_widget(self.recall_stimulus)
		
		# self.recall_stimulus.texture = self.image_dict[self.mask_image].image.texture

		# self.protocol_floatlayout.add_widget(self.recall_stimulus)
		

		# Define Widgets - Stimulus Layout

		self.x_boundaries = [0.1, 0.9]
		self.y_boundaries = [0.1, 1]

		self.stimulus_image_x_size = (max(self.x_boundaries) - min(self.x_boundaries))/np.ceil(max(self.num_stimuli_pal, self.num_stimuli_pa)/self.num_rows)

		self.stimulus_x_boundaries = [
			(min(self.x_boundaries) + (self.stimulus_image_x_size/2))
			, (max(self.x_boundaries) - (self.stimulus_image_x_size/2))
			]


		if any(True for stage in ['dPAL', 'sPAL', 'Training'] if stage in self.stage_list):

			self.num_stimuli = self.num_stimuli_pal
		
		else:

			self.num_stimuli = self.num_stimuli_pa
		
		
		self.stimulus_x_loc = np.linspace(min(self.stimulus_x_boundaries), max(self.stimulus_x_boundaries), int(self.num_stimuli)).tolist()


		self.stimulus_grid_list = self.generate_stimulus_grid(
			self.stimulus_x_loc
			, self.num_rows
			, grid_gap = 0.1
			)


		# for stimulus in self.stimulus_grid_list:
			
		# # 	stimulus.texture = self.image_dict[self.mask_image].image.texture
		# 	self.protocol_floatlayout.add_widget(stimulus)
		
		# self.protocol_floatlayout.add_widget(self.recall_stimulus)

		# for iStim in range(len(self.stimulus_grid_list)):

		# 	self.stimulus_grid_list[iStim].texture = self.image_dict[self.target_image_list[iStim]].image.texture
		# 	self.protocol_floatlayout.add_widget(self.stimulus_grid_list[iStim])
		# 	self.protocol_floatlayout.remove_widget(self.stimulus_grid_list[iStim])
		# 	self.stimulus_grid_list[iStim].texture = self.image_dict[self.mask_image].image.texture

		
		# self.recall_stimulus.texture = self.image_dict[self.mask_image].image.texture
		# self.protocol_floatlayout.add_widget(self.recall_stimulus)
		# self.protocol_floatlayout.remove_widget(self.recall_stimulus)

		# for iImage in self.image_dict:

		# 	print(str(self.image_dict[iImage]))
		


		# Instruction - Dictionary
		
		self.instruction_path = str(self.protocol_path / 'Language' / self.language / 'Instructions.ini')
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Training'] = {}
		self.instruction_dict['dPAL'] = {}
		self.instruction_dict['sPAL'] = {}
		self.instruction_dict['Recall'] = {}
		
		for stage in self.stage_list:
			
			self.instruction_dict[stage]['train'] = self.instruction_config[stage]['train']
			self.instruction_dict[stage]['task'] = self.instruction_config[stage]['task']
		


		for stimulus in self.stimulus_grid_list:

			self.protocol_floatlayout.add_widget(stimulus)
		
		self.protocol_floatlayout.add_widget(self.recall_stimulus)



		self.start_protocol_event()
	


	
	
	def start_protocol_from_tutorial(self, *args):
		
		self.generate_output_files()
		self.metadata_output_generation()
		self.start_protocol()






	
	
	
	def protocol_load_images(self, image_list, *args):
		# Load Images - Async
		
		self.image_dict = {}
		
		for image_file in image_list:
			
			if pathlib.Path(self.image_folder / image_file).exists():
				
				load_image = Loader.image(str(self.image_folder / image_file))
				image_name = str(image_file.stem)
			
			elif pathlib.Path(self.image_folder, str(image_file) + '.png').exists():
				
				load_image = Loader.image((str(self.image_folder) + str(image_file) + '.png'))
				image_name = str(image_file)

			else: # Path(image_file).exists():
				
				image_file = pathlib.Path(image_file)
				load_image = Loader.image(str(image_file))
				image_name = str(image_file.stem)


			self.image_dict[image_name] = load_image
		
		self.images_loaded = True






	def generate_stimulus_grid(
			self
			, grid_x_pos_list
			, num_rows = 1
			, grid_gap = 0.1
			):
		
		grid_square_dim = (max(grid_x_pos_list) - min(grid_x_pos_list)) / (len(grid_x_pos_list) - 1)

		grid_square_fill = [(grid_square_dim * self.width_adjust) * (1 - grid_gap), (grid_square_dim * self.height_adjust) * (1 - grid_gap)]
		
		grid_x_squares = len(grid_x_pos_list)
		
		stimulus_grid_loc = [ImageButton() for position in range(int(grid_x_squares * num_rows))]
		
		x_pos = 0
		y_pos = 0
		initial_target = random.choice(list(range(0,len(stimulus_grid_loc))))
		
		for cell in stimulus_grid_loc:
			
			if x_pos >= grid_x_squares:
				
				x_pos = 0
				y_pos += 1
				
			grid_square_x_pos = grid_x_pos_list[x_pos]
			grid_square_y_pos = 0.3 + ((y_pos + 0.5) * (grid_square_dim * self.height_adjust))

			# if (x_pos == initial_target) \
			# 	and (y_pos == 0):

			# 	cell.source = self.training_image_path
			# 	cell.bind(on_press=self.target_pressed)
			

			# else:

			cell.source = self.mask_image_path
			cell.bind(on_press=self.nontarget_pressed)
			

			# cell.texture = self.image_dict[self.mask_image].image.texture
			cell.size_hint = grid_square_fill
			cell.pos_hint = {"center_x": grid_square_x_pos, "center_y": grid_square_y_pos}
			# cell.name = 'Stimulus Image ' + str(cell)
			
			x_pos += 1
		
		
		return stimulus_grid_loc



	def start_protocol(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		print('Stage list: ', self.stage_list)

		# self.protocol_load_images(self.total_image_list)
		
		self.start_clock()
		
		# self.block_contingency()
		# self.trial_contingency()
		self.block_check_event()
	
	
	
	def stimulus_presentation(self, *args): # Stimulus presentation
		
		self.printlog('Stimulus presentation')
		
		# self.hold_button.unbind(on_press=self.iti)
		self.iti_event.cancel()

		self.hold_button.unbind(on_release=self.premature_response)
		
		# self.protocol_floatlayout.remove_widget(self.hold_button)

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_widget(self.recall_stimulus)
					
		for stimulus in self.stimulus_grid_list:

			self.protocol_floatlayout.add_widget(stimulus)

		
		self.stimulus_start_time = time.time()
		
		self.feedback_string = ''
		self.feedback_label.text = self.feedback_string
			
		# self.printlog('Start target time: ', (self.stimulus_start_time - self.start_time))
		# self.printlog('Target loc: ', self.target_loc)
		# self.printlog('Target image: ', self.target_image)
		
		self.protocol_floatlayout.add_event([
			self.stimulus_start_time - self.start_time
			, 'Stage Change'
			, 'Display Target'
			])


		if self.current_stage in ['dPAL', 'sPAL']:

			# self.printlog('Nontarget loc: ', self.nontarget_loc)
			# self.printlog('Nontarget image loc: ', self.nontarget_image_loc)
			# self.printlog('Nontarget image: ', self.nontarget_image)

			self.protocol_floatlayout.add_event([
				self.stimulus_start_time - self.start_time
				, 'Stage Change'
				, 'Display Nontarget'
				])


		elif self.current_stage == 'Recall':

			# self.printlog('Recall prompt: ', self.target_image_list[self.target_loc])

			self.protocol_floatlayout.add_event([
				self.stimulus_start_time - self.start_time
				, 'Stage Change'
				, 'Display Recall Prompt'
				])
		
		# return

	





	
	
	
	# Hold released too early
	
	def premature_response(self, *args):
		
		self.printlog('Premature response')
		
		if self.stimulus_on_screen is True:
			
			return

		
		Clock.unschedule(self.iti)
		
		self.protocol_floatlayout.add_event([time.time() - self.start_time
											, 'Stage Change'
											, 'Premature Response'
											])
		

		self.feedback_string = self.feedback_dict['wait']
		self.response_lat = 0
		self.iti_active = False
		self.feedback_label.text = self.feedback_string
		
		if self.feedback_on_screen is False:
			
			self.protocol_floatlayout.add_widget(self.feedback_label)

			self.feedback_on_screen = True
		
			self.feedback_start_time = time.time()
			
			self.protocol_floatlayout.add_event([self.feedback_start_time - self.start_time
												, 'Text Displayed'
												, 'Feedback'
												])
		
		
		self.hold_button.unbind(on_release=self.premature_response)
		self.hold_button.bind(on_press=self.iti)
	
	
	
	# Target Pressed
	
	def target_pressed(self, *args):
		
		self.printlog('Target pressed')

		self.protocol_floatlayout.add_event([
			time.time() - self.start_time
			, 'Stage Change'
			, 'Correct Response'
			])
		
		self.last_response = 1

		self.stimulus_press_time = time.time()
		self.response_latency = self.stimulus_press_time - self.stimulus_start_time

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Image Removed'
			, 'Target'
			, 'Image'
			, self.target_image
			, 'Location'
			, self.target_loc
			])


		if self.current_stage in ['dPAL', 'sPAL']:
		
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Image Removed'
				, 'Nontarget'
				, 'Image'
				, self.nontarget_image
				, 'Location'
				, self.nontarget_loc
			])


		elif self.current_stage == 'Recall':
		
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Image Removed'
				, 'Recall Prompt'
				, 'Image'
				, self.target_image_list[self.target_loc]
			])
		

		self.feedback_string = self.feedback_dict['correct']
		self.feedback_label.text = self.feedback_string

		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		# self.protocol_floatlayout.add_widget(self.hold_button)
		self.protocol_floatlayout.add_widget(self.feedback_label)

		self.feedback_on_screen = True
		
		self.feedback_start_time = time.time()
		
		self.protocol_floatlayout.add_event(
			[self.feedback_start_time - self.start_time
			, 'Text Displayed'
			, 'Feedback'
			, 'Text'
			, self.feedback_string
			])
		
		self.write_trial()
		
		self.trial_contingency()

		return
	
	
	
	# Nontarget Pressed
	
	def nontarget_pressed(self, *args):
		
		self.printlog('Nontarget pressed')

		self.protocol_floatlayout.add_event([
			time.time() - self.start_time
			, 'Stage Change'
			, 'Incorrect Response'
			])
		
		self.last_response = -1

		self.stimulus_press_time = time.time()
		self.response_latency = self.stimulus_press_time - self.stimulus_start_time

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Image Removed'
			, 'Target'
			, 'Image'
			, self.target_image
			, 'Location'
			, self.target_loc
			])


		if self.current_stage in ['dPAL', 'sPAL']:
		
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Image Removed'
				, 'Nontarget'
				, 'Image'
				, self.nontarget_image
				, 'Location'
				, self.nontarget_loc
			])


		elif self.current_stage == 'Recall':
		
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Image Removed'
				, 'Recall Prompt'
				, 'Image'
				, self.target_image_list[self.target_loc]
			])
		

		self.feedback_string = self.feedback_dict['incorrect']
		self.feedback_label.text = self.feedback_string

		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		# self.protocol_floatlayout.add_widget(self.hold_button)
		self.protocol_floatlayout.add_widget(self.feedback_label)

		self.feedback_on_screen = True
		
		self.feedback_start_time = time.time()
		
		self.protocol_floatlayout.add_event(
			[self.feedback_start_time - self.start_time
			, 'Text Displayed'
			, 'Feedback'
			, 'Text'
			, self.feedback_string
			])
		
		self.write_trial()
		
		self.trial_contingency()

		return
	
	
	
	# Data Saving Function
	
	def write_trial(self, *args):
		
		self.printlog('Write trial')

		if self.current_stage in ['dPAL', 'sPAL']:

			self.nontarget_image_string = self.nontarget_image
			self.nontarget_loc_string = self.nontarget_loc
		

		else:

			self.nontarget_image_string = 'Mask'
			self.nontarget_loc_string = '-1'
		

		trial_data = [
			self.current_trial
			, self.current_stage
			, self.current_block
			, self.current_block_trial
			, self.target_image
			, self.target_loc
			, self.nontarget_image_string
			, self.nontarget_loc_string
			, self.last_response
			, self.response_latency
			]
		
		self.write_summary_file(trial_data)
	
	
	
	# Trial Contingency Functions
	
	def trial_contingency(self, *args):
		
		try:

			# self.iti_event.cancel()

			# self.protocol_floatlayout.remove_widget(self.hold_button)

			# 	stimulus.texture = self.image_dict[self.blank_image].image.texture
				
			# 	if self.current_stage == 'Recall':
					
			# 		stimulus.bind(on_press=self.nontarget_pressed)

				# else:
				# 	stimulus.texture = self.image_dict[self.mask_image].image.texture
			

			if self.current_block_trial != 0:
				
				self.printlog('\n\n\n')
				self.printlog('Trial contingency start')
				self.printlog('')
				self.printlog('Current trial: ', self.current_trial)
				self.printlog('Current stage: ', self.current_stage)
				self.printlog('Current block: ', self.current_block)
				self.printlog('Current block trial: ', self.current_block_trial)
				self.printlog('Current task time: ', (time.time() - self.start_time))
				self.printlog('Current block time: ', (time.time() - self.block_start_time))
				self.printlog('')
				self.printlog('ITI: ', self.iti_length)
				self.printlog('Start target time: ', (self.stimulus_start_time - self.start_time))
				self.printlog('Response latency: ', self.response_latency)
				self.printlog('')
				self.printlog('Last response: ', self.last_response)
				self.printlog('')
				self.printlog('Target loc: ', self.target_loc)
				self.printlog('Target image: ', self.target_image)
				self.printlog('')


				if self.current_stage in ['dPAL', 'sPAL']:

					self.printlog('Nontarget loc: ', self.nontarget_loc)
					self.printlog('Nontarget image loc: ', self.nontarget_image_loc)
					self.printlog('Nontarget image: ', self.nontarget_image)
					self.printlog('')


				elif self.current_stage == 'Recall':

					self.printlog('Recall prompt: ', self.target_image_list[self.target_loc])
					self.printlog('')
				
				
				self.printlog('')


			
				self.protocol_floatlayout.add_event([
					time.time() - self.start_time
					, 'Variable Change'
					, 'Current Trial'
					, 'Value'
					, str(self.current_trial)
					])
				

			# if self.current_block_trial > 1: # Check for block end if not first trial of block

				# self.stimulus_grid_list[self.target_loc].unbind(on_press=self.target_pressed)

				# if self.nontarget_loc != -1:

				# 	self.stimulus_grid_list[self.nontarget_loc].unbind(on_press=self.nontarget_pressed)




				self.response_tracking.append(self.last_response)

				if self.current_stage == 'Training' \
					and self.last_response == -1:

					self.response_tracking.pop()

					# if sum(self.response_tracking) >= self.training_block_max_correct:

					# 	self.printlog('Training max correct reached')

					# 	self.iti_event.cancel()
					
					# 	self.protocol_floatlayout.add_event([
					# 		time.time() - self.start_time
					# 		, 'Block Change'
					# 		, 'Current Probe'
					# 		, 'Value'
					# 		, str(self.current_stage)
					# 		])
						
					# 	self.block_check_event()




			# Check if block ended

			# if self.current_block_trial != 0:

				if (time.time() - self.block_start_time >= self.block_duration):

					self.printlog('Block max duration reached')

					self.iti_event.cancel()

					self.protocol_floatlayout.add_event([
						time.time() - self.start_time
						, 'Block Change'
						, 'Current Probe'
						, 'Value'
						, str(self.current_stage)
						])
					
					# self.block_contingency()
					self.block_check_event()

				elif (self.current_block_trial >= self.block_trial_max):

					self.printlog('Block max trials reached')

					self.iti_event.cancel()

					self.protocol_floatlayout.add_event([
						time.time() - self.start_time
						, 'Block Change'
						, 'Current Probe'
						, 'Value'
						, str(self.current_stage)
						])
					
					# self.block_contingency()
					self.block_check_event()
				

				elif (self.current_stage == 'Training') \
					and (sum(self.response_tracking) >= self.training_block_max_correct):

					self.printlog('Training block max correct reached')

					self.iti_event.cancel()
					self.hold_button.unbind(on_release=self.premature_response)

					self.protocol_floatlayout.add_event([
						time.time() - self.start_time
						, 'Block Change'
						, 'Current Probe'
						, 'Value'
						, str(self.current_stage)
						])
					
					
					self.hold_button.bind(on_release=self.premature_response)
					
					# self.block_contingency()
					self.block_check_event()
				

				elif (len(self.response_tracking) > 10) \
					and (sum(self.response_tracking[-10:]) >= 6) \
					and not self.block_change_on_duration:

					self.printlog('Criterion accuracy (0.8 or better) reached')
					
					self.iti_event.cancel()

					self.protocol_floatlayout.add_event([
						time.time() - self.start_time
						, 'Block Change'
						, 'Block End'
						, 'Value'
						, str(self.current_block)
						])
					
					# self.block_contingency()
					self.block_check_event()
			

				else:

					self.protocol_floatlayout.add_widget(self.hold_button)
			



			# Set next trial parameters
			
			
			for stimulus in self.stimulus_grid_list:

				stimulus.bind(on_press=self.target_pressed)
				stimulus.unbind(on_press=self.target_pressed)

				stimulus.bind(on_press=self.nontarget_pressed)
				stimulus.unbind(on_press=self.nontarget_pressed)


			# self.last_target_loc = self.target_loc
			# self.last_nontarget_loc = self.nontarget_loc


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

			







			# Set target/nontarget stimuli

			if self.current_stage == 'Training':

				self.target_loc = random.choice(list(range(self.num_stimuli)))

				self.nontarget_loc = -1
				self.nontarget_image_loc = -1
				
				self.target_image = self.training_image
				self.nontarget_image = self.mask_image
				self.blank_image = self.mask_image
				self.recall_image = self.mask_image
			

			else:

				if self.trial_list_index >= len(self.trial_list):
					
					random.shuffle(self.trial_list)
					self.trial_list_index = 0
				
				new_target_loc = self.trial_list[self.trial_list_index]
				self.trial_list_index += 1
				
				if self.current_stage in ['dPAL', 'sPAL']:

					pos_list = list(range(self.num_stimuli))

					pos_list.remove(new_target_loc)

					random.shuffle(pos_list)

					new_nontarget_loc = pos_list[0]
					new_nontarget_image_loc = pos_list[1]

					if (new_target_loc == self.target_loc) \
						and (new_nontarget_loc == self.nontarget_loc):

						new_nontarget_loc = pos_list[1]
						new_nontarget_image_loc = pos_list[0]
					
					if self.current_stage == 'sPAL':
						new_nontarget_image_loc = new_target_loc
				
					self.target_loc = new_target_loc
					self.nontarget_loc = new_nontarget_loc
					self.nontarget_image_loc = new_nontarget_image_loc

					self.target_image = self.target_image_list[self.target_loc]
					self.nontarget_image = self.target_image_list[self.nontarget_image_loc]
					self.blank_image = self.mask_image
					self.recall_image = self.mask_image


				elif self.current_stage == 'Recall':

					self.target_loc = new_target_loc
					self.nontarget_loc = -1
					self.nontarget_image_loc = -1

					self.target_image = self.outline_image
					self.nontarget_image = self.outline_image
					self.blank_image = self.outline_image
					self.recall_image = self.target_image_list[self.target_loc]

					self.protocol_floatlayout.add_event([
							time.time() - self.start_time
							, 'Variable Change'
							, 'Recall Prompt'
							, 'Image'
							, self.recall_image
							])
			

			# elif self.current_block == -1:

			# 	self.target_loc = random.randint(0, (self.num_stimuli - 1))

			# 	self.nontarget_loc = -1
			# 	self.nontarget_image_loc = -1
				
			# 	self.target_image = self.training_image
			# 	self.nontarget_image = self.mask_image
			# 	self.recall_image = self.mask_image
			

			# self.stimulus_grid_list[self.target_loc].texture = self.image_dict[self.target_image].image.texture
			# self.stimulus_grid_list[self.target_loc].bind(on_press=self.target_pressed)

			# self.recall_stimulus.texture = self.image_dict[self.recall_image].image.texture

			# if (self.nontarget_loc or self.nontarget_image_loc) != -1:

			# 	self.stimulus_grid_list[self.nontarget_loc].texture = self.image_dict[self.nontarget_image].image.texture
			# 	self.stimulus_grid_list[self.nontarget_loc].bind(on_press=self.nontarget_pressed)


			for iLoc in list(range(0, self.num_stimuli)):

				# if iLoc == last_target_loc:

				# 	self.stimulus_grid_list[iLoc].unbind(on_press=self.target_pressed)
				
				# elif iLoc == last_nontarget_loc:

				# 	self.stimulus_grid_list[iLoc].unbind(on_press=self.nontarget_pressed)


				if iLoc == self.target_loc:

					self.stimulus_grid_list[iLoc].texture = self.image_dict[self.target_image].image.texture
					self.stimulus_grid_list[iLoc].bind(on_press=self.target_pressed)
				
				elif iLoc == self.nontarget_loc:

					self.stimulus_grid_list[iLoc].texture = self.image_dict[self.nontarget_image].image.texture
					self.stimulus_grid_list[iLoc].bind(on_press=self.nontarget_pressed)
				
				else:
					
					self.stimulus_grid_list[iLoc].texture = self.image_dict[self.blank_image].image.texture

					if self.current_stage == 'Recall':

						self.stimulus_grid_list[iLoc].bind(on_press=self.nontarget_pressed)
			

			self.recall_stimulus.texture = self.image_dict[self.recall_image].image.texture
			

			self.protocol_floatlayout.add_event([
				time.time() - self.start_time
				, 'Variable Change'
				, 'Target'
				, 'Location'
				, str(self.target_loc)
				, 'Image'
				, self.target_image
				])
			
			self.protocol_floatlayout.add_event([
				time.time() - self.start_time
				, 'Variable Change'
				, 'Nontarget'
				, 'Location'
				, str(self.nontarget_loc)
				, 'Image'
				, self.nontarget_image
				])
			

			if self.current_stage == 'Recall':

				self.protocol_floatlayout.add_event([
					time.time() - self.start_time
					, 'Variable Change'
					, 'Recall'
					, 'Location'
					, 'Recall Stimulus'
					, 'Image'
					, self.recall_image
					])
			


			# self.hold_button.bind(on_press=self.iti)
			# self.hold_button.bind(on_press=self.iti)

			self.last_response = 0
			self.trial_outcome = 0


			# Check if block ended

			# if self.current_block_trial > 1:

			# 	if (time.time() - self.block_start_time >= self.block_duration):

			# 		self.printlog('Block max duration reached')

			# 		self.iti_event.cancel()

			# 		self.protocol_floatlayout.add_event([
			# 			time.time() - self.start_time
			# 			, 'Block Change'
			# 			, 'Current Probe'
			# 			, 'Value'
			# 			, str(self.current_stage)
			# 			])
					
			# 		# self.block_contingency()
			# 		self.block_check_event()
				

			# 	elif (self.current_stage == 'Training') \
			# 		and (sum(self.response_tracking) >= self.training_block_max_correct):

			# 		self.printlog('Training block max correct reached')

			# 		self.iti_event.cancel()
			# 		self.hold_button.unbind(on_release=self.premature_response)

			# 		self.protocol_floatlayout.add_event([
			# 			time.time() - self.start_time
			# 			, 'Block Change'
			# 			, 'Current Probe'
			# 			, 'Value'
			# 			, str(self.current_stage)
			# 			])
					
					
			# 		self.hold_button.bind(on_release=self.premature_response)
					
			# 		# self.block_contingency()
			# 		self.block_check_event()
				

			# 	elif (len(self.response_tracking) > 10) \
			# 		and (sum(self.response_tracking[-10:]) >= 6) \
			# 		and not self.block_change_on_duration:

			# 		self.printlog('Criterion accuracy (0.8 or better) reached')
					
			# 		self.iti_event.cancel()

			# 		self.protocol_floatlayout.add_event([
			# 			time.time() - self.start_time
			# 			, 'Block Change'
			# 			, 'Block End'
			# 			, 'Value'
			# 			, str(self.current_block)
			# 			])
					
			# 		# self.block_contingency()
			# 		self.block_check_event()
			

			# if self.current_block == -1:
			# 	self.block_contingency()
			# 	return


			# return


			# self.protocol_floatlayout.add_widget(self.hold_button)
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()
	



	def block_break_screen(self, *args):
		
# 		self.protocol_floatlayout.clear_widgets()
		
		if not self.block_started:
			
			self.protocol_floatlayout.add_widget(self.block_label)

			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Display'
				, 'Text'
				, 'Block'
				, 'Instruction'
				])
			
			self.block_start = time.time()
			self.block_start_time = time.time()
			self.block_started = True

			self.block_break_event()
		
		if (time.time() - self.block_start) > self.block_min_rest_duration:
			
			self.block_break_event.cancel()

			self.protocol_floatlayout.add_widget(self.continue_button)

			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Display'
				, 'Button'
				, 'Block'
				, 'Continue'
				])
	
	
	
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
	


	def recall_target_screen(self, *args):

		if not self.recall_instruction_target_display_started:

			for stimulus in self.stimulus_grid_list:

				# print('Checking stimulus: ', str(stimulus))

				stimulus.bind(on_press=self.target_pressed)
				stimulus.unbind(on_press=self.target_pressed)

				stimulus.bind(on_press=self.nontarget_pressed)
				stimulus.unbind(on_press=self.nontarget_pressed)
			
			# self.recall_stage_start_label = Label(text='Press "Start Section" below to begin the next block.', font_size='44sp', markup=True)
			# self.recall_stage_start_label.size_hint = {0.9, 0.8}
			# self.recall_stage_start_label.pos_hint = {'center_x': 0.5, 'center_y': 0.7}

			# self.recall_stage_start_button = Button(text='Start Section', font_size='48sp')
			# self.recall_stage_start_button.size_hint = {0.4, 0.15}
			# self.recall_stage_start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.1}
			# self.recall_stage_start_button.bind(on_press=self.section_start)

			self.protocol_floatlayout.clear_widgets()

			self.stimulus_grid_list[0].texture = self.image_dict[self.target_image_list[0]].image.texture

			for stimulus in self.stimulus_grid_list:

				self.protocol_floatlayout.add_widget(stimulus)
			
			self.recall_target_screen_start_time = time.time()

			self.recall_instruction_target_display_started = True


		if (time.time() - self.recall_target_screen_start_time) >= self.recall_target_present_duration:

			self.recall_instruction_target_present_event.cancel()

			if self.recall_target_display_pos < self.num_stimuli:

				self.protocol_floatlayout.remove_widget(self.stimulus_grid_list[self.recall_target_display_pos])

				self.stimulus_grid_list[self.recall_target_display_pos].texture = self.image_dict[self.outline_image].image.texture

				self.protocol_floatlayout.add_widget(self.stimulus_grid_list[self.recall_target_display_pos])

				self.recall_target_display_pos += 1

			if self.recall_target_display_pos == self.num_stimuli:

				for iLoc in list(range(0, self.num_stimuli)):

					self.protocol_floatlayout.remove_widget(self.stimulus_grid_list[iLoc])

					self.stimulus_grid_list[iLoc].texture = self.image_dict[self.target_image_list[iLoc]].image.texture

					self.protocol_floatlayout.add_widget(self.stimulus_grid_list[iLoc])
				
				
				self.recall_target_display_pos += 1

				self.recall_target_screen_start_time = time.time()

				self.recall_instruction_target_present_event()


			elif self.recall_target_display_pos > self.num_stimuli:

				for iLoc in list(range(0, self.num_stimuli)):

					self.protocol_floatlayout.remove_widget(self.stimulus_grid_list[iLoc])

					self.stimulus_grid_list[iLoc].texture = self.image_dict[self.outline_image].image.texture

					if iLoc == self.target_loc:

						self.stimulus_grid_list[iLoc].bind(on_press=self.target_pressed)
					
					else:

						self.stimulus_grid_list[iLoc].bind(on_press=self.nontarget_pressed)

					self.protocol_floatlayout.add_widget(self.stimulus_grid_list[iLoc])

				# self.protocol_floatlayout.add_widget(self.recall_stage_start_button)

				self.hold_button.bind(on_press=self.iti)
				self.section_start()
				# self.protocol_floatlayout.add_widget(self.hold_button)
			

			else:
				
				self.protocol_floatlayout.remove_widget(self.stimulus_grid_list[self.recall_target_display_pos])

				self.stimulus_grid_list[self.recall_target_display_pos].texture = self.image_dict[self.target_image_list[self.recall_target_display_pos]].image.texture

				self.protocol_floatlayout.add_widget(self.stimulus_grid_list[self.recall_target_display_pos])

				self.recall_target_screen_start_time = time.time()

				self.recall_instruction_target_present_event()
		

		else:

			self.recall_instruction_target_present_event()
	


	def start_recall_block(self, *args):

		self.hold_button.unbind(on_press=self.start_recall_block)

		self.hold_button.bind(on_press=self.iti)

		self.protocol_floatlayout.remove_widget(self.hold_button)

		self.trial_contingency()
		
		self.iti()


		
		# self.recall_stage_start_button = Button(text='Start Section', font_size='48sp')
		# self.recall_stage_start_button.size_hint = {0.4, 0.15}
		# self.recall_stage_start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}

		# for stimulus in self.stimulus_grid_list:

		# 	self.protocol_floatlayout.add_widget(stimulus)


		# for iLoc in list(range(0, self.num_stimuli)):

		# 	self.recall_target_display(iLoc)

		# 	time.sleep(2)

		# 	self.recall_target_remove(iLoc)

		
		# self.protocol_floatlayout.add_widget(self.recall_stage_start_button)


	
	# def recall_target_display(self, iLoc = 0, *args):
		
	# 	iLoc = int(iLoc)

	# 	self.protocol_floatlayout.remove_widget(self.stimulus_grid_list[iLoc])

	# 	self.stimulus_grid_list[iLoc].texture = self.image_dict[self.target_image_list[iLoc]].image.texture

	# 	self.protocol_floatlayout.add_widget(self.stimulus_grid_list[iLoc])

	# 	return


	
	# def recall_target_remove(self, iLoc, *args):

	# 	self.protocol_floatlayout.remove_widget(self.stimulus_grid_list[iLoc])

	# 	self.stimulus_grid_list[iLoc].texture = self.image_dict[self.blank_image].image.texture

	# 	self.protocol_floatlayout.add_widget(self.stimulus_grid_list[iLoc])

	# 	return


	
	# Block Contingency Function
	
	def block_contingency(self, *args):
		
		
		try:

			# if not self.images_loaded:
			# 	self.protocol_load_images(self.total_image_list)
			
			self.hold_button.unbind(on_press=self.iti)
			self.hold_button.unbind(on_release=self.premature_response)

			self.iti_event.cancel()
			
			Clock.unschedule(self.iti)

			if self.feedback_on_screen:
				# self.printlog('Feedback on screen')
				
				if (time.time() - self.feedback_start_time) >= self.feedback_length:
					self.printlog('Feedback over')
					self.block_check_event.cancel()
					# self.protocol_floatlayout.remove_widget(self.feedback_label)
					self.protocol_floatlayout.clear_widgets()
					self.feedback_string = ''
					self.feedback_label.text = self.feedback_string
					self.feedback_on_screen = False
				else:
					# self.printlog('Wait for feedback delay')
					return
			else:
				self.printlog('Block check event cancel')
				self.block_check_event.cancel()
			
			
			self.printlog('Block contingency')

			self.protocol_floatlayout.clear_widgets()

			self.printlog('Clear widgets')

			self.current_block += 1


			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'State Change'
				, 'Block Change'
				, 'Current Block'
				, self.current_block
				])
			
			self.printlog('Current block: ', self.current_block)

			
			if (self.current_block > self.block_multiplier) or (self.current_block == -1):

				self.stage_index += 1
				self.current_block = 1
				# self.response_tracking = [-2,-2]
				
				self.printlog('Stage index: ', self.stage_index)
			
	
			if self.stage_index >= len(self.stage_list): # Check if all stages complete

				self.printlog('All stages complete')
				self.session_event.cancel()
				self.protocol_end()

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
			





			# # Set generic block parameters

			# self.target_image = self.mask_image
			# self.nontarget_image = self.mask_image
			# self.recall_image = self.mask_image

			# if self.current_stage == 'Recall':

			# 	self.blank_image = self.outline_image
			
			# else:

			# 	self.blank_image = self.mask_image






			if self.current_stage in ['Training', 'dPAL', 'sPAL']:

				self.num_stimuli = self.num_stimuli_pal
				self.target_image_list = self.target_image_list_pal

				self.trial_list = self.trial_list_pal

				if self.current_stage == 'dPAL':

					self.block_trial_max = self.dpal_trial_max

				elif self.current_stage == 'sPAL':

					self.block_trial_max = self.spal_trial_max

			elif self.current_stage == 'Recall':

				self.num_stimuli = self.num_stimuli_pa
				self.target_image_list = self.target_image_list_pa

				self.trial_list = self.trial_list_pa

				self.block_trial_max = self.recall_trial_max

			
			self.stimulus_x_loc = np.linspace(min(self.stimulus_x_boundaries), max(self.stimulus_x_boundaries), int(self.num_stimuli)).tolist()

			self.stimulus_grid_list = self.generate_stimulus_grid(
				self.stimulus_x_loc
				, self.num_rows
				, grid_gap = 0.1
				)
			

			




			
			
			for stimulus in self.stimulus_grid_list:

				# print('Checking stimulus: ', str(stimulus))

				stimulus.bind(on_press=self.target_pressed)
				stimulus.unbind(on_press=self.target_pressed)

				stimulus.bind(on_press=self.nontarget_pressed)
				stimulus.unbind(on_press=self.nontarget_pressed)
			

			random.shuffle(self.trial_list)

			self.target_loc = self.trial_list[0]
			
			pos_list = list(range(self.num_stimuli))

			pos_list.remove(self.target_loc)

			random.shuffle(pos_list)

			# self.target_loc = pos_list[0]
			self.nontarget_loc = pos_list[0]
			self.nontarget_image_loc = pos_list[1]

			# if self.num_stimuli == 3:

			# 	pos_list = list(range(0, 3))

			# 	pos_list.remove(self.target_loc)

			# 	random.shuffle(pos_list)

			# 	# self.target_loc = pos_list[0]
			# 	self.nontarget_loc = pos_list[0]
			# 	self.nontarget_image_loc = pos_list[1]
			
			# else:
				
			# 	# self.target_loc = random.randint(0, (self.num_stimuli - 1))
			# 	self.nontarget_loc = random.randint(0, (self.num_stimuli - 1))
			# 	self.nontarget_image_loc = random.randint(0, (self.num_stimuli - 1))

			# 	while self.nontarget_loc == self.target_loc:

			# 		self.nontarget_loc = random.randint(0, (self.num_stimuli - 1))


			# 	while self.nontarget_image_loc in [self.target_loc, self.nontarget_loc]:

			# 		self.nontarget_image_loc = random.randint(0, (self.num_stimuli - 1))
			






			if self.current_block == 1: #and self.display_instructions:
				
				self.printlog('Section Task Instructions')
				self.section_instr_label.text = self.instruction_dict[str(self.current_stage)]['task']
				
				self.block_max_length = 360
				
				if self.current_stage == 'Training':
					self.block_max_length = self.training_block_max_correct
				

				self.instruction_button.text = 'Start Section'


				# for stimulus in self.stimulus_grid_list:
				# 	self.protocol_floatlayout.add_widget(stimulus)

				# self.protocol_floatlayout.add_widget(self.recall_stimulus)
				

				if self.current_stage == 'Recall':

					self.instruction_button.unbind(on_press=self.section_start)
					self.instruction_button.bind(on_press=self.recall_instruction_target_present_event)
					self.instruction_button.text = 'See Image Locations'

				
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
				self.block_screen()





			# 	# stimulus.source = self.mask_image_path
				
			# 	if self.current_stage == 'Recall':
			# 		# stimulus.texture = self.image_dict[self.outline_image].image.texture
			# 		stimulus.source = self.outline_image_path
			# 		stimulus.bind(on_press=self.nontarget_pressed)

			# 	else:
			# 		# stimulus.texture = self.image_dict[self.mask_image].image.texture
			# 		stimulus.source = self.mask_image_path
			

			# self.recall_stimulus.source = self.mask_image_path
			# # self.recall_stimulus.texture = self.image_dict[self.mask_image].image.texture


			# # self.current_stage = self.stage_list[self.stage_index]
			
			# self.protocol_floatlayout.add_event([
			# 	time.time() - self.start_time
			# 	, 'Stage Change'
			# 	, self.current_stage
			# 	])
			
			
			# self.feedback_string = ''
			# self.feedback_label.text = self.feedback_string
			
			# self.trial_index = 0
			# self.last_response = 2 # Set to 2 to indicate block change for staircasing

			# self.printlog('Current task time: ', (time.time() - self.start_time))
			# self.printlog('Block duration: ', self.block_duration)
			
			
			# # Set target/nontarget stimuli

			# if self.current_stage in ['Training', 'Recall']:

			# 	self.target_loc = random.randint(0, (self.num_stimuli - 1))

			# 	if self.current_stage == 'Training':

			# 		self.nontarget_loc = -1
			# 		self.nontarget_image_loc = -1
					
			# 		self.target_image = self.training_image
			# 		self.nontarget_image = self.mask_image
			# 		self.recall_image = self.mask_image

			# 	elif self.current_stage == 'Recall':

			# 		self.nontarget_loc = -1
			# 		self.nontarget_image_loc = -1

			# 		self.target_image = self.mask_image
			# 		self.nontarget_image = self.mask_image
			# 		self.recall_image = self.target_image_list[self.target_loc]

			# 		self.protocol_floatlayout.add_event([
			# 			time.time() - self.start_time
			# 			, 'Variable Change'
			# 			, 'Recall Prompt'
			# 			, 'Image'
			# 			, self.recall_image
			# 			])
			
			
			# elif self.current_stage in ['dPAL', 'sPAL']:

			# 	image_locations = list(range(0, self.num_stimuli))
			# 	random.shuffle(image_locations)
				
			# 	self.target_loc = image_locations[0]
			# 	self.nontarget_loc = image_locations[1]
			# 	self.nontarget_image_loc = image_locations[2]

			# 	if self.current_stage == 'sPAL':
					
			# 		self.nontarget_image_loc = self.target_loc


			# 	self.target_image = self.target_image_list[self.target_loc]
			# 	self.nontarget_image = self.target_image_list[self.nontarget_image_loc]
			# 	self.recall_image = self.mask_image

			# 	self.stimulus_grid_list[self.nontarget_loc].texture = self.image_dict[self.nontarget_image].image.texture
			# 	self.stimulus_grid_list[self.nontarget_loc].bind(on_press=self.nontarget_pressed)
			

			# self.stimulus_grid_list[self.target_loc].texture = self.image_dict[self.target_image].image.texture
			# self.stimulus_grid_list[self.target_loc].bind(on_press=self.target_pressed)

			# self.recall_stimulus.texture = self.image_dict[self.recall_image].image.texture
			

			# self.protocol_floatlayout.add_event([
			# 	time.time() - self.start_time
			# 	, 'Variable Change'
			# 	, 'Target'
			# 	, 'Location'
			# 	, str(self.target_loc)
			# 	, 'Image'
			# 	, self.target_image
			# 	])
			
			# self.protocol_floatlayout.add_event([
			# 	time.time() - self.start_time
			# 	, 'Variable Change'
			# 	, 'Nontarget'
			# 	, 'Location'
			# 	, str(self.nontarget_loc)
			# 	, 'Image'
			# 	, self.nontarget_image
			# 	])
			

			# # Set ITI

			# if len(self.iti_range) > 1:
				
			# 	if self.iti_fixed_or_range == 'fixed':
					
			# 		self.iti_length = random.choice(self.iti_range)
				
				
			# 	else:
					
			# 		self.iti_length = round(random.uniform(min(self.iti_range), max(self.iti_range)), 2)
				
				
			# 	self.protocol_floatlayout.add_event([
			# 		time.time() - self.start_time
			# 		, 'Variable Change'
			# 		, 'Current ITI'
			# 		, 'Value'
			# 		, str(self.iti_length)
			# 		])


			# self.hold_button.bind(on_press=self.iti)

			# self.protocol_floatlayout.clear_widgets()
			
			# self.block_break_event()

			# self.block_screen()
			

			self.response_tracking = [0,0]
			self.last_response = 0
			self.contingency = 0
			self.trial_outcome = 0
			self.current_block_trial = 0
			# self.trial_index = -1
			
			
			# self.block_start_time = time.time()
			
			# self.protocol_floatlayout.add_event([
			# 	(self.block_start_time - self.start_time)
			# 	, 'Variable Change'
			# 	, 'Parameter'
			# 	, 'Block Start Time'
			# 	, str(self.block_start_time)
			# 	])
			

			self.printlog('Block contingency end')

			self.trial_contingency()

			# self.block_screen()
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()
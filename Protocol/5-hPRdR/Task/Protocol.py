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
import ffpyplayer

import kivy.graphics
# import kivy.uix.effectwidget

from Classes.Protocol import ImageButton, ProtocolBase

from kivy.clock import Clock
from kivy.config import Config
from kivy.core.video import Video as CoreVideo
from kivy.core.video import VideoBase
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect, PixelateEffect
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.video import Video

# from pathlib import Path





class ProtocolScreen(ProtocolBase):



	def __init__(self, **kwargs):
		super(ProtocolScreen, self).__init__(**kwargs)
		self.protocol_name = '5-hPRdR'
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
		




		self.data_cols = [
			'TrialNo'
			, 'CurrentBlock'
			, 'BlockTrial'
			, 'TotalHitCount'
			, 'ResponseLevel'
			, 'TargetXPos'
			, 'TargetYPos'
			, 'Latency'
			]

		self.metadata_cols = [
			'participant_id'
			, 'skip_tutorial_video'
			, 'block_change_on_duration_only'
			, 'iti_fixed_or_range'
			, 'iti_length'
			, 'feedback_length'
			, 'block_duration'
			, 'block_min_rest_duration'
			, 'session_duration'
			, 'stimulus_image'
			, 'response_level_start'
			, 'response_level_end'
			, 'grid_squares_x'
			, 'grid_squares_y'
			, 'min_separation'
			, 'pr_ratio_multiplier'
			, 'baseline_pr'
			, 'pr_step_max'
			, 'block_count'
			, 'reward_type'
			]
		
		
		# Define Variables - Config Import
		
		config_path = str(pathlib.Path('Protocol', self.protocol_name, 'Configuration.ini'))
		config_file = configparser.ConfigParser()
		config_file.read(config_path)

		if ('DebugParameters' in config_file) \
			and (int(config_file['DebugParameters']['debug_mode']) == 1):
			self.parameters_dict = config_file['DebugParameters']
		else:
			self.parameters_dict = config_file['TaskParameters']
			
		self.participant_id = 'Default'

		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_import = self.parameters_dict['iti_length']
		iti_import = iti_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.timeout_duration = int(self.parameters_dict['timeout_duration'])
		self.hold_button_delay = float(self.parameters_dict['hold_button_delay'])
		self.block_duration = int(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])

		self.background_grid_image = self.parameters_dict['background_grid_image']
		self.stimulus_image = self.parameters_dict['stimulus_image']
		self.stimulus_pressed_image = self.parameters_dict['stimulus_pressed_image']
		
		self.response_level = int(self.parameters_dict['response_level_start'])
		self.response_level_end = int(self.parameters_dict['response_level_end'])

		self.grid_squares_x = int(self.parameters_dict['grid_squares_x'])
		self.grid_squares_y = int(self.parameters_dict['grid_squares_y'])
		
		self.min_separation = int(self.parameters_dict['min_separation'])
		
		self.use_confirmation = int(self.parameters_dict['use_confirmation'])

		self.current_pr_multiplier = int(self.parameters_dict['pr_ratio_multiplier'])
		self.baseline_pr_threshold = int(self.parameters_dict['baseline_pr'])
		self.current_pr_threshold_step_max = int(self.parameters_dict['pr_step_max'])

		self.reward_type = str(self.parameters_dict['reward_type'])

		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']
		

		# Define Clock
		
		self.session_event = self.session_clock.create_trigger(self.clock_monitor, self.session_length_max, interval=False)
		self.session_event.cancel()
		
		self.task_clock = Clock
		self.task_clock.interupt_next_only = False

		self.stimulus_present_event = self.task_clock.schedule_once(self.stimulus_presentation, 0.4)
		self.stimulus_present_event.cancel()

		self.display_hold_button_event = self.task_clock.schedule_once(self.display_hold_button, self.hold_button_delay)
		self.display_hold_button_event.cancel()

		self.no_response_event = self.task_clock.schedule_once(self.protocol_end, self.timeout_duration)
		self.no_response_event.cancel()

		self.tutorial_end_event = self.task_clock.schedule_once(self.present_tutorial_video_start_button, 0)
		self.tutorial_end_event.cancel()


		# Define Widgets - Buttons

		self.quit_button = Button()


		# Define Language

		self.language = 'English'
		self.feedback_dict = {}
		self.set_language(self.language)


		# Define Variables - List
		# self.stage_list = ['Reward x20', 'Reward x10', 'Reward x5', 'Reward x2', 'Reward x1']
		# self.reward_value_score = [200, 100, 50, 20, 10]
		# self.reward_value_curr = [2.00, 1.00, 0.50, 0.25, 0.10]

		# Define Variables - Boolean
		# self.correction_trial = True

		# Define Variables - Count
		self.current_pr_threshold = self.baseline_pr_threshold
		self.current_pr_step = 0
		self.current_response_count = 0

		self.hit_target = 2 ** self.response_level

		self.high_score = 0.0

		self.loc_num = 0
		self.loc_hits = 0

		self.response_count_list = list()

		# self.block_threshold = 10 + self.block_length

		# Define Variables - String
		# self.current_stage = self.stage_list[self.stage_index]

		# Define Variables - Time
		
		self.iti_range = list()
		self.iti_length = 0

		self.block_start_time = 0.0
		self.block_end_time = 0.0
		self.stimulus_start_time = 0.0
		self.response_lat = 0.0

		# Define Variables - Trial Configuration
		self.trial_configuration = 0
		if self.reward_type == 'point':
			# self.reward_list = self.reward_value_score
			self.current_reward_value = 0
			# self.feedback_string = 'Reward:\n %d Points' % self.current_reward_value
		elif self.reward_type == 'currency':
			# self.reward_list = self.reward_value_curr
			self.current_reward_value = 0.00
			# self.feedback_string = 'Reward:\n $%.2f' % self.current_reward_value

		# self.current_reward = self.reward_list[self.stage_index]
		self.target_x_pos = random.randint(0, self.grid_squares_x - 1)
		self.target_y_pos = random.randint(1, self.grid_squares_y - 1)
		
		
		# Define Widgets - Images

		self.image_folder = pathlib.Path('Protocol', self.protocol_name, 'Image')

		self.background_grid_image_path = str(self.image_folder / str(self.background_grid_image + '.png'))
		self.stimulus_image_path = str(self.image_folder / str(self.stimulus_image + '.png'))
		self.stimulus_pressed_image_path = str(self.image_folder / str(self.stimulus_pressed_image + '.png'))
		self.hold_image_path = str(self.image_folder / str(self.hold_image + '.png'))
		self.mask_image_path = str(self.image_folder / str(self.mask_image + '.png'))
		self.checkmark_image_path = str(self.image_folder / 'checkmark.png')

		self.stimulus_button = ImageButton()

		self.target_x_pos = 0
		self.target_y_pos = 1
		

		# Define Widgets - Images
		# self.hold_button_image_path = self.image_folder + self.hold_image + '.png'
		# self.hold_button.source = self.hold_button_image_path

		self.x_boundaries = [0.04, 0.96]
		self.y_boundaries = [0.18, 0.95]

		self.x_dim_hint = np.linspace(self.x_boundaries[0], self.x_boundaries[1], self.grid_squares_x).tolist()
		self.y_dim_hint = np.linspace(self.y_boundaries[0], self.y_boundaries[1], self.grid_squares_y).tolist()

		# self.stimulus_image_path = self.image_folder + self.stimulus_image + '.png'
		# self.mask_image_path = self.image_folder + self.mask_image + '.png'
		self.background_grid_list = [ImageButton() for _ in range((self.grid_squares_x * self.grid_squares_y))]

		x_pos = 0
		y_pos = 0

		for cell in self.background_grid_list:
			cell.fit_mode = 'fill'
			cell.size_hint = ((.08 * self.width_adjust), (.08 * self.height_adjust))

			if x_pos >= self.grid_squares_x:
				x_pos = 0
				y_pos = y_pos + 1

			cell.pos_hint = {"center_x": self.x_dim_hint[x_pos], "center_y": self.y_dim_hint[y_pos]}
			cell.source = self.background_grid_image_path
			x_pos = x_pos + 1

		# self.stimulus_button = ImageButton(source=self.stimulus_image_path)
		# self.stimulus_button.bind(on_press=self.stimulus_pressed)


	# Initialization Functions #
		
	def load_parameters(self,parameter_dict):
		
		# Import parameters from config file
		
		self.parameters_dict = parameter_dict
		
		config_path = str(pathlib.Path('Protocol', self.protocol_name, 'Configuration.ini'))
		config_file = configparser.ConfigParser()
		config_file.read(config_path)
		
		
		self.participant_id = self.parameters_dict['participant_id']

		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_import = self.parameters_dict['iti_length']
		iti_import = iti_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.timeout_duration = int(self.parameters_dict['timeout_duration'])
		self.hold_button_delay = float(self.parameters_dict['hold_button_delay'])
		self.block_duration = int(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])

		self.background_grid_image = self.parameters_dict['background_grid_image']
		self.stimulus_image = self.parameters_dict['stimulus_image']
		self.stimulus_pressed_image = self.parameters_dict['stimulus_pressed_image']
		
		self.response_level = int(self.parameters_dict['response_level_start'])
		self.response_level_end = int(self.parameters_dict['response_level_end'])

		self.grid_squares_x = int(self.parameters_dict['grid_squares_x'])
		self.grid_squares_y = int(self.parameters_dict['grid_squares_y'])
		
		self.min_separation = int(self.parameters_dict['min_separation'])
		
		self.use_confirmation = int(self.parameters_dict['use_confirmation'])

		self.current_pr_multiplier = int(self.parameters_dict['pr_ratio_multiplier'])
		self.baseline_pr_threshold = int(self.parameters_dict['baseline_pr'])
		self.current_pr_threshold_step_max = int(self.parameters_dict['pr_step_max'])

		self.reward_type = str(self.parameters_dict['reward_type'])

		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']


		# Define Language

		self.language = self.parameters_dict['language']
		self.set_language(self.language)

		# self.feedback_label.size_hint = (0.7, 0.4)
		# self.feedback_label.pos_hint = {'center_x': 0.5, 'center_y': 0.7}


		# Define Variables - Clock

		self.no_response_event = self.task_clock.schedule_once(self.protocol_end, self.timeout_duration)
		self.no_response_event.cancel()


		# Define Variables - Boolean

		self.feedback_on_screen = False
		self.stimulus_on_screen = False


		# Define Variables - Time
		
		self.iti_range = [float(iNum) for iNum in iti_import]
		self.iti_length = self.iti_range[0]

		self.block_start_time = 0.0
		self.block_end_time = 0.0
		self.stimulus_start_time = 0.0
		self.response_lat = 0.0
		self.stimulus_max_delay = 0.2

		self.high_score = 0.0


		# Define Variables - List
		# self.stage_list = ['Reward x20', 'Reward x10', 'Reward x5', 'Reward x2', 'Reward x1']
		# self.reward_value_score = [200, 100, 50, 20, 10]
		# self.reward_value_curr = [2.00, 1.00, 0.50, 0.25, 0.10]


		# Define Variables - Count

		self.total_hit_count = 0

		self.hit_target = 2 ** self.response_level
		
		self.loc_num = 0
		self.loc_hits = 0

		self.response_count_list = list()

		# self.current_pr_threshold = self.baseline_pr_threshold
		# self.block_threshold = 10 + self.block_length


		# Define Variables - Trial Configuration

		if self.reward_type == 'point':
			# self.reward_list = self.reward_value_score
			self.current_reward_value = 0
			# self.feedback_string = 'Reward:\n %d Points' % self.current_reward_value
		elif self.reward_type == 'currency':
			# self.reward_list = self.reward_value_curr
			self.current_reward_value = 0.00
			# self.feedback_string = 'Reward:\n $%.2f' % self.current_reward_value


		# self.current_reward = self.reward_list[self.stage_index]
		# self.protocol_floatlayout.add_event(
		# 	[0, 'Variable Change', 'Current Reward', 'Value', str(self.current_reward_value),
		# 	 '', '', '', ''])

		self.target_x_pos = random.randint(0, self.grid_squares_x - 1)
		self.target_y_pos = random.randint(1, self.grid_squares_y - 1)

		# Define Widgets - Images
		# self.hold_button_image_path = self.image_folder + self.hold_image + '.png'
		# self.hold_button.source = self.hold_button_image_path
		# self.hold_button.pos_hint = {"center_x": 0.5, "center_y": 0.001}


		# Define Widgets - Results Label

		self.results_label = Label(font_size='32sp')
		self.results_label.size_hint = (0.8, 0.4)
		self.results_label.pos_hint = {'center_x': 0.5, 'center_y': 0.55}
		self.results_label.text = ''
		


		# Define Widgets - Buttons

		self.quit_button = Button(text='End Task', font_size='24sp')
		self.quit_button.size_hint = (0.2, 0.1)
		self.quit_button.pos_hint = {'center_x': 0.3, 'center_y': 0.07}
		self.quit_button.bind(on_press=self.protocol_end)

		self.confirm_button = Button(text='Confirm', font_size='24sp')
		# self.confirm_button = ImageButton(source=)
		self.confirm_button.size_hint = (0.2, 0.1)
		self.confirm_button.pos_hint = {'center_x': 0.75, 'center_y': 0.07}
		self.confirm_button.color = 'grey'

		self.block_start_button = Button(text='Start Task', font_size='24sp')
		self.block_start_button.size_hint = (0.4, 0.1)
		self.block_start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.1}
		self.block_start_button.bind(on_press=self.start_block)

		self.hold_button.size_hint = (0.1 * self.width_adjust, 0.1 * self.height_adjust)
		self.hold_button.pos_hint = {'center_x': 0.5, 'center_y': 0.07}
		self.hold_button.bind(on_press=self.iti)

		self.x_dim_hint = np.linspace(self.x_boundaries[0], self.x_boundaries[1], self.grid_squares_x).tolist()
		self.y_dim_hint = np.linspace(self.y_boundaries[0], self.y_boundaries[1], self.grid_squares_y).tolist()
			

		
		# Load images

		self.background_grid_image_path = str(self.image_folder / str(self.background_grid_image + '.png'))
		self.stimulus_image_path = str(self.image_folder / str(self.stimulus_image + '.png'))
		self.stimulus_pressed_image_path = str(self.image_folder / str(self.stimulus_pressed_image + '.png'))
		self.hold_image_path = str(pathlib.Path(self.image_folder, self.hold_image + '.png'))
		self.mask_image_path = str(pathlib.Path(self.image_folder, self.mask_image + '.png'))
		self.checkmark_image_path = str(self.image_folder / 'checkmark.png')
		# self.outline_mask_path = str(self.image_folder / 'whitecircle.png')

		total_image_list = [
			self.stimulus_image_path
			, self.stimulus_pressed_image_path
			, self.background_grid_image_path
			, self.hold_image_path
			, self.mask_image_path
			, self.checkmark_image_path
			]
		
		print('\n\nTotal image list: ', total_image_list, '\n\n')

		# self.stimulus_image_path = self.image_folder + self.stimulus_image + '.png'
		# self.mask_image_path = self.image_folder + self.mask_image + '.png'

		self.background_grid_list = [ImageButton() for _ in range((self.grid_squares_x * self.grid_squares_y))]
		
		x_pos = 0
		y_pos = 0

		for cell in self.background_grid_list:
			cell.fit_mode = 'fill'
			cell.size_hint = ((.08 * self.width_adjust), (.08 * self.height_adjust))

			if x_pos >= self.grid_squares_x:
				x_pos = 0
				y_pos = y_pos + 1
			
			cell.pos_hint = {"center_x": self.x_dim_hint[x_pos], "center_y": self.y_dim_hint[y_pos]}
			cell.source = self.background_grid_image_path
			x_pos = x_pos + 1

		self.stimulus_button = ImageButton(source=self.stimulus_image_path) #, allow_stretch=True)
		self.stimulus_button.pos_hint = {
			"center_x": self.x_dim_hint[self.target_x_pos]
			, "center_y": self.y_dim_hint[self.target_y_pos]
			}
		self.stimulus_button.size_hint = (0.08 * self.width_adjust, 0.08 * self.height_adjust)
		self.stimulus_button.bind(on_press=self.target_pressed)

		self.stimulus_pressed_button = ImageButton(source=self.stimulus_pressed_image_path) #, allow_stretch=True)
		self.stimulus_pressed_button.pos_hint = {
			"center_x": self.x_dim_hint[self.target_x_pos]
			, "center_y": self.y_dim_hint[self.target_y_pos]
			}
		self.stimulus_pressed_button.size_hint = (0.08 * self.width_adjust, 0.08 * self.height_adjust)
		# self.stimulus_button.bind(on_press=self.target_pressed)

		self.reward_image = Image(source=self.checkmark_image_path) #, allow_stretch=True)
		self.reward_image.pos_hint = {"center_x": 0.5, "center_y": 0.8}
		self.reward_image.size_hint = (1 * self.width_adjust, 1 * self.height_adjust)


		self.instruction_label.pos_hint = {'center_x': 0.5, 'center_y': 0.55}

		self.present_instructions()
		# self.present_tutorial()





		
	def present_tutorial(self, *args):
		
		self.tutorial_hold = ImageButton(source=self.hold_image_path)
		self.tutorial_hold.size_hint = (0.1 * self.width_adjust, 0.1 * self.height_adjust)
		self.tutorial_hold.pos_hint = {'center_x': 0.5, 'center_y': 0.1}
		self.tutorial_hold.bind(on_press=self.start_protocol_from_tutorial)
		
		self.tutorial_label_top = Label(font_size='35sp')
		self.tutorial_label_top.size_hint = (0.6, 0.8)
		self.tutorial_label_top.pos_hint = {'center_x': 0.5, 'center_y': 0.58}
		
		self.tutorial_label_bottom = Label(font_size='35sp')
		self.tutorial_label_bottom.size_hint = (0.6, 0.3)
		self.tutorial_label_bottom.pos_hint = {'center_x': 0.5, 'center_y': 0.4}

		lang_folder_path = pathlib.Path('Protocol', self.protocol_name, 'Language', self.language)
		start_path = str(lang_folder_path / 'Start.txt')

		with open(start_path, 'r', encoding="utf-8") as start_open:
			self.tutorial_label_top.text = start_open.read()
		
		# self.tutorial_label_top.text = 'This is a test of attention.\n\nDuring the test, you will see a series of images.\nYour task is to respond to target images, like the one below.\n\n\n\n\n\n\n\n\n\nThe following screens will teach you how to perform this task.\n\nPress the "CONTINUE TUTORIAL" button below to continue.'
		# self.tutorial_label_bottom.text = 'Your task is to respond as quickly as possible whenever a target\nimage appears, and withhold response to all other images.\n\nThe following screens will teach you how to perform this task.\n\nPress the "CONTINUE TUTORIAL" button below to continue.'
		# self.tutorial_label.text = 'PRESS BELOW TO START TASK'

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_widget(self.tutorial_hold)


		
	def present_tutorial_video(self, *args):
		
		self.tutorial_start_button = Button(text='START', font_size='48sp')
		self.tutorial_start_button.size_hint = (0.4, 0.15)
		self.tutorial_start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.2} #self.text_button_pos_LC
		self.tutorial_start_button.bind(on_press=self.start_protocol_from_tutorial)

		self.protocol_floatlayout.clear_widgets()

		# self.protocol_floatlayout.add_widget(self.tutorial_video)
		# self.tutorial_video.state = 'play'

		if self.skip_tutorial_video == 1:
			
			self.tutorial_video_end_event = self.stimdur_clock.schedule_once(self.present_tutorial_video_start_button, 0)
		
		else:

			self.tutorial_video_end_event = self.stimdur_clock.schedule_once(self.present_tutorial_video_start_button, 74)
	


	def present_tutorial_video_start_button(self, *args):

		self.tutorial_video_end_event.cancel()

		self.tutorial_video.state = 'pause'

		self.protcol_floatlayout.add_widget(self.tutorial_start_button)
	
	
	
	def start_protocol_from_tutorial(self, *args):
		
		# self.protocol_floatlayout.remove_widget(self.tutorial_stimulus_image)
		# self.blur_effect_widget.remove_widget(self.tutorial_stimulus_image)
		self.generate_output_files()
		self.metadata_output_generation()
		self.start_protocol()


	
	def start_protocol(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		self.start_clock()
		
		self.block_contingency()













	def stimulus_presentation(self, *args): # Stimulus presentation
		
		self.printlog('Stimulus presentation')

		self.iti_event.cancel()
		# self.stimulus_present_event.cancel()

		self.hold_button.unbind(on_press=self.iti)
		self.hold_button.unbind(on_release=self.premature_response)

		self.protocol_floatlayout.remove_widget(self.hold_button)
		
		# for grid_image in self.background_grid_list:

		# 	self.protocol_floatlayout.add_widget(grid_image)

		if (self.current_block_trial % 2) != 1 \
			and self.use_confirmation == 1:

			self.hold_button.bind(on_press=self.target_pressed)
			self.protocol_floatlayout.add_widget(self.hold_button)
			# self.protocol_floatlayout.add_widget(self.stimulus_pressed_button)
			# self.protocol_floatlayout.add_widget(self.confirm_button)
			# self.confirm_button.color = 'white'
			# self.confirm_button.bind(on_press=self.target_pressed)

		else:

			self.protocol_floatlayout.add_widget(self.stimulus_button)
			# self.protocol_floatlayout.remove_widget(self.hold_button)
		

		self.stimulus_start_time = time.time()

		self.stimulus_on_screen = True
		
		self.protocol_floatlayout.add_event([
			self.stimulus_start_time - self.start_time
			, 'Stage Change'
			, 'Display Target'
			])

		self.no_response_event()
		
		# return
	
				
	
	def premature_response(self, *args): # Trial Outcomes: 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Hit, no center touch,6-False Alarm, no center touch
		if self.stimulus_on_screen:
			return None
		
		if self.iti_active:
			self.iti_event.cancel()
		
		self.protocol_floatlayout.clear_widgets()

		self.contingency = 3
		self.response = 1
		self.trial_outcome = 0
		self.response_latency = -1.0
		self.stimulus_press_latency = -1.0
		self.movement_latency = -1.0

		self.feedback_label.text = ''
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'State Change'
			, 'Premature Response'
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Contingency'
			, str(self.contingency)
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Response'
			, str(self.response)
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Outcome'
			, str(self.trial_outcome)
			])
		

		self.write_trial()

		self.iti_active = False

		self.feedback_string = self.feedback_dict['wait']
		# self.feedback_label.text = self.feedback_string
		
		# if not self.feedback_on_screen:

		# 	self.protocol_floatlayout.add_widget(self.feedback_label)

		# 	self.feedback_start_time = time.time()
		# 	self.feedback_on_screen = True

		# 	self.protocol_floatlayout.add_event([
		# 		(self.feedback_start_time - self.start_time)
		# 		, 'Object Display'
		# 		, 'Text'
		# 		, 'Feedback'
		# 		, self.feedback_string
		# 		])


		self.results_label.text = self.feedback_string
		
		self.hold_button.unbind(on_release=self.premature_response)
		self.hold_button.bind(on_press=self.start_block)

		self.protocol_floatlayout.add_widget(self.results_label)
		self.protocol_floatlayout.add_widget(self.hold_button)
		self.protocol_floatlayout.add_widget(self.quit_button)
	
	
	
	# Target Pressed
	
	def target_pressed(self, *args):
		
		self.printlog('Target pressed')

		self.no_response_event.cancel()

		self.stimulus_press_time = time.time()
		self.response_latency = self.stimulus_press_time - self.stimulus_start_time

		self.protocol_floatlayout.add_event([
			time.time() - self.start_time
			, 'Stage Change'
			, 'Target Pressed'
			])


		if (self.current_block_trial % 2) != 1 \
			and self.use_confirmation == 1:

			# self.protocol_floatlayout.remove_widget(self.confirm_button)
			# self.confirm_button.color = 'grey'
			self.hold_button.unbind(on_press=self.target_pressed)
			self.protocol_floatlayout.remove_widget(self.hold_button)
			self.protocol_floatlayout.remove_widget(self.stimulus_pressed_button)

		else:

			self.protocol_floatlayout.remove_widget(self.stimulus_button)
			self.protocol_floatlayout.add_widget(self.stimulus_pressed_button)
		
		# self.current_block_trial += 1
		self.total_hit_count += 1
		self.loc_hits += 1
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Block Hit Count'
			, str(self.current_block_trial)
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Total Hit Count'
			, str(self.total_hit_count)
			])

		self.stimulus_on_screen = False

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Image Removed'
			, 'Target'
			, 'X_Pos'
			, self.target_x_pos
			, 'Y_Pos'
			, self.target_y_pos
			])

		
		self.write_trial()
		
		self.trial_contingency()

		return
	
	
	
	# Data Saving Function
	
	def write_trial(self):
		
		self.printlog('Write trial')
		

		trial_data = [
			self.current_trial
			, self.current_block
			, self.current_block_trial
			, self.total_hit_count
			, self.response_level
			, self.target_x_pos
			, self.target_y_pos
			, self.response_latency
			]
		
		self.write_summary_file(trial_data)
	
	
	
	# Trial Contingency Functions
	
	def trial_contingency(self):
		
		try:

			if self.current_block_trial != 1:
				
				self.printlog('\n\n\n')
				self.printlog('Trial contingency start')
				self.printlog('')
				self.printlog('Current trial: ', self.current_trial)
				self.printlog('Current block trial: ', self.current_block_trial)
				self.printlog('Current task time: ', (time.time() - self.start_time))
				self.printlog('')
				self.printlog('Stimulus presentation time: ', (self.stimulus_start_time - self.start_time))
				self.printlog('Response latency: ', self.response_latency)
				self.printlog('')
				self.printlog('Target x pos: ', self.target_x_pos)
				self.printlog('Target y pos: ', self.target_y_pos)
				self.printlog('\n\n')


			if self.current_block_trial >= self.hit_target:

				self.printlog('Block hits completed')

				self.iti_event.cancel()

				self.current_block += 1
				self.response_level += 1

				self.hit_target = 2 ** self.response_level

				self.stimulus_max_delay = self.response_level/10
				
				self.block_end_time = time.time()
		
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'State Change'
					, 'Block Change'
					, 'Current Block'
					, self.current_block
					])
		
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Response Level'
					, self.response_level
					])
				
				self.block_contingency()
			

			else:

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
					
				
				# Set next trial parameters

				if (self.current_block_trial % 2) != 1 \
					and self.use_confirmation == 1:

					# Confirmation button trial

					pass


				else:

					new_x_pos = random.randint(0, self.grid_squares_x - 1)
					new_y_pos = random.randint(1, self.grid_squares_y - 1)

					while (
						abs(new_x_pos - self.target_x_pos) \
						+ abs(new_y_pos - self.target_y_pos)
						) <= self.min_separation:

						new_x_pos = random.randint(0, self.grid_squares_x - 1)
						new_y_pos = random.randint(1, self.grid_squares_y - 1)


					self.target_x_pos = new_x_pos
					self.target_y_pos = new_y_pos
					
					self.stimulus_button.pos_hint = {
						'center_x': self.x_dim_hint[self.target_x_pos]
						, 'center_y': self.y_dim_hint[self.target_y_pos]
						}
					
					self.stimulus_pressed_button.pos_hint = {
						'center_x': self.x_dim_hint[self.target_x_pos]
						, 'center_y': self.y_dim_hint[self.target_y_pos]
						}
					

					self.protocol_floatlayout.add_event([
						time.time() - self.start_time
						, 'Variable Change'
						, 'Target'
						, 'X_Pos'
						, self.target_x_pos
						, 'Y_Pos'
						, self.target_y_pos
						])
				

				self.stimulus_presentation()
				# self.stimulus_present_event()
				# self.stimulus_present_event = self.task_clock.schedule_once(self.stimulus_presentation, random.uniform(0.1, self.stimulus_max_delay))
				


				# self.hold_button.bind(on_press=self.iti)
				# self.hold_button.bind(on_press=self.iti)
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()
	


	# Block start function (add widgets and set block start time)

	def start_block(self, *args):

		# self.protocol_floatlayout.clear_widgets()
		
		# if self.feedback_on_screen:

		# 	self.protocol_floatlayout.remove_widget(self.feedback_label)

		# 	self.feedback_on_screen = False

		if self.current_block != 1:
			self.protocol_floatlayout.remove_widget(self.reward_image)

		self.protocol_floatlayout.remove_widget(self.results_label)

		self.block_start_time = time.time()

		self.hold_button.unbind(on_press=self.start_block)
		self.hold_button.bind(on_press=self.iti)

		self.hold_button.bind(on_release=self.premature_response)

		# self.protocol_floatlayout.add_widget(self.hold_button)
		# self.protocol_floatlayout.add_widget(self.quit_button)

		for grid_square in self.background_grid_list:
			self.protocol_floatlayout.add_widget(grid_square)
		
		self.iti()



	# Block start function (add widgets and set block start time)

	def display_hold_button(self, *args):

		self.display_hold_button_event.cancel()
		self.protocol_floatlayout.add_widget(self.hold_button)


	
	
	
	# Block Contingency Function
	
	def block_contingency(self, *args):
		
		
		try:

			self.iti_event.cancel()
			
			Clock.unschedule(self.iti)
			
			self.hold_button.unbind(on_press=self.iti)
			self.hold_button.unbind(on_release=self.premature_response)
			
			
			self.printlog('Block contingency')

			self.protocol_floatlayout.clear_widgets()

			self.printlog('Clear widgets')

			
			if self.response_level > self.response_level_end:
			
				self.printlog('All stages complete')
				self.session_event.cancel()
				self.protocol_end()

				return
			
			
			else:

				if self.current_block == 1: #and self.display_instructions:
					
					# self.results_label.text = '\n\nPress and hold the white button\nto start the first trial.'
					self.results_label.text = 'Press and hold the white button to start the first \ntrial, or press "End Task" to end the task.'

					self.hold_button.bind(on_press=self.start_block)
					# self.protocol_floatlayout.add_widget(self.hold_button)
					self.protocol_floatlayout.add_widget(self.quit_button)
					# self.protocol_floatlayout.add_widget(self.confirm_button)
					self.protocol_floatlayout.add_widget(self.results_label)

					# self.display_hold_button_event()
					self.display_hold_button_event = self.task_clock.schedule_once(self.display_hold_button, self.hold_button_delay)
				
				else:
					
					self.printlog('Results Screen')
					
					# self.results_label.text = 'Trial complete.\n\nPress "End Task" to end the task, or press and \nhold the white button to start the next trial.'
					self.results_label.text = 'Block complete!\n\nPress and hold the white button to start the next \ntrial, or press "End Task" to end the task.'

					self.hold_button.bind(on_press=self.start_block)
					# self.protocol_floatlayout.add_widget(self.hold_button)
					self.protocol_floatlayout.add_widget(self.reward_image)
					self.protocol_floatlayout.add_widget(self.results_label)
					self.protocol_floatlayout.add_widget(self.quit_button)
					# self.protocol_floatlayout.add_widget(self.confirm_button)
					
					# self.display_hold_button_event()
					self.display_hold_button_event = self.task_clock.schedule_once(self.display_hold_button, self.hold_button_delay)
			


			
			
			
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
			


			self.target_x_pos = random.randint(0, self.grid_squares_x - 1)
			self.target_y_pos = random.randint(1, self.grid_squares_y - 1)

			self.stimulus_button.pos_hint = {
				'center_x': self.x_dim_hint[self.target_x_pos]
				, 'center_y': self.y_dim_hint[self.target_y_pos]
				}
					
			self.stimulus_pressed_button.pos_hint = {
				'center_x': self.x_dim_hint[self.target_x_pos]
				, 'center_y': self.y_dim_hint[self.target_y_pos]
				}
			

			self.current_block_trial = 1
			

			self.printlog('Block contingency end')

			self.printlog('\n\n\n')
			self.printlog('*************')
			self.printlog('Block start')
			self.printlog('')
			self.printlog('ITI: ', self.iti_length)
			self.printlog('Response level: ', self.response_level)
			self.printlog('Required responses: ', self.hit_target)
			self.printlog('*************')
			self.printlog('\n\n')

			# self.trial_contingency()

			# self.block_screen()
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()














		
	# # Block Staging
			
	# def block_end(self, *args):
	# 	self.block_started = False
	# 	self.protocol_floatlayout.clear_widgets()
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Text Removed', 'Block Instruction', '', '',
	# 		 '', '', '', ''])
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Button Removed', 'Continue Button', '', '',
	# 		 '', '', '', ''])
	# 	self.trial_contingency()
	# 	self.protocol_floatlayout.add_widget(self.hold_button)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Button Displayed', 'Hold Button', '', '',
	# 		 '', '', '', ''])
	# 	self.score_label.text = 'Your Points:\n%s' % (self.current_score)
	# 	self.protocol_floatlayout.add_widget(self.score_label)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Text Displayed', 'Score', '', '',
	# 		 '', '', '', ''])
	
	# # End Staging #
		
	# def return_to_main(self, *args):
	# 	self.manager.current = 'mainmenu'
	
	# # Protocol Staging #
	
	# def start_protocol(self,*args):
	# 	self.protocol_floatlayout.add_event(
	# 		[0, 'Stage Change', 'Instruction Presentation', '', '',
	# 		 '', '', '', ''])
	# 	self.protocol_floatlayout.remove_widget(self.instruction_label)
	# 	self.protocol_floatlayout.add_event(
	# 		[0, 'Text Removed', 'Task Instruction', '', '',
	# 		 '', '', '', ''])
	# 	self.protocol_floatlayout.remove_widget(self.start_button)
	# 	self.protocol_floatlayout.add_event(
	# 		[0, 'Button Removed', 'Task Start Button', '', '',
	# 		 '', '', '', ''])
	# 	self.start_clock()
		
	# 	self.protocol_floatlayout.add_widget(self.hold_button)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Button Displayed', 'Hold Button', '', '',
	# 		 '', '', '', ''])
	# 	self.hold_button.size_hint = ((0.1 * self.width_adjust), (0.1 * self.height_adjust))
	# 	for image_wid in self.background_grid_list:
	# 		self.protocol_floatlayout.add_widget(image_wid)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Displayed', 'Grid Array', '', '',
	# 		 '', '', '', ''])
	# 	self.protocol_floatlayout.add_widget(self.quit_button)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Button Displayed', 'Quit Button', '', '',
	# 		 '', '', '', ''])
	# 	self.feedback_label.text = self.feedback_string
	# 	self.protocol_floatlayout.add_widget(self.feedback_label)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Text Displayed', 'Score', '', '',
	# 		 '', '', '', ''])
	# 	self.feedback_on_screen = True
	# 	self.hold_button.pos_hint = {"center_x":0.5,"center_y":0.1}
	# 	self.hold_button.bind(on_press=self.iti)
				
	# def stimulus_presentation(self,*args):
	# 	self.protocol_floatlayout.add_widget(self.stimulus_button)
	# 	self.stimulus_button.size_hint = ((0.08 * self.width_adjust), (0.08 * self.height_adjust))
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Displayed', 'Sample Image', 'X Position', self.x_dim_hint[self.target_x_pos],
	# 		 'Y Position', self.y_dim_hint[self.target_y_pos], 'Image Name', self.stimulus_image])
	# 	self.stimulus_start_time = time.time()
	# 	self.stimulus_on_screen = True
				
	# def premature_response(self,*args):
	# 	if self.stimulus_on_screen:
	# 		return None
	# 	self.iti_event.cancel()
	# 	self.response_lat = 0
	# 	self.iti_active = False
	# 	self.hold_button.unbind(on_release=self.premature_response)
	# 	self.hold_button.bind(on_press=self.iti)

	# def iti(self, *args):
	# 	if not self.iti_active:
	# 		self.hold_button.unbind(on_press=self.iti)
	# 		self.start_iti = time.time()
	# 		self.iti_active = True
	# 		self.protocol_floatlayout.add_event(
	# 			[time.time() - self.start_time, 'Stage Change', 'ITI Start', '', '',
	# 			'', '', '', ''])

	# 		if self.feedback_string == self.hold_feedback_wait_str:
	# 			self.protocol_floatlayout.remove_widget(self.feedback_label)
	# 			self.protocol_floatlayout.add_event(
	# 				[time.time() - self.start_time, 'Text Removed', 'Feedback', '', '',
	# 				 '', '', '', ''])
	# 		self.iti_event()
	# 	if self.iti_active:
	# 		if (time.time() - self.start_iti) > self.iti_length:
	# 			self.iti_event.cancel()
	# 			self.iti_active = False
	# 			self.stimulus_presentation()

	# # Contingency Stages
	# def stimulus_pressed(self, *args):
	# 	self.stimulus_on_screen = False
	# 	self.protocol_floatlayout.remove_widget(self.stimulus_button)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Removed', 'Sample Image', 'X Position', self.x_dim_hint[self.target_x_pos],
	# 		 'Y Position', self.y_dim_hint[self.target_y_pos], 'Image Name', self.stimulus_image])
		
	# 	self.current_response_count += 1
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Variable Change', 'Current Responses', 'Value', str(self.current_response_count),
	# 		 '', '', '', ''])

	# 	self.response_lat = time.time() - self.stimulus_start_time
	# 	self.response_time = time.time() - self.start_time
	# 	self.write_trial()
	# 	self.trial_contingency()
	# 	self.hold_button.bind(on_press=self.iti)
		
	# # Data Saving Functions #

	# def write_trial(self):
	# 	trial_data = [self.current_trial, self.current_stage, self.current_pr_threshold, str(self.target_x_pos + 1),
	# 				  str(self.target_y_pos + 1), self.response_lat, self.response_time]
	# 	self.write_summary_file(trial_data)
	# 	return
	
	# # Trial Contingency Functions #
	
	# def trial_contingency(self):
	# 	self.current_trial += 1
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Variable Change', 'Current Trial', 'Value', str(self.current_trial),
	# 		 '', '', '', ''])
		
	# 	self.target_x_pos = random.randint(0,7)
	# 	self.target_y_pos = random.randint(0,7)
	# 	self.stimulus_button.pos_hint = {"center_x":self.x_dim_hint[self.target_x_pos],"center_y":self.y_dim_hint[self.target_y_pos]}

	# 	if self.current_response_count >= self.current_pr_threshold:
	# 		self.current_pr_threshold *= self.current_pr_multiplier
	# 		self.protocol_floatlayout.add_event(
	# 			[0, 'Variable Change', 'Current Threshold', 'Value', str(self.current_pr_threshold),
	# 			 '', '', '', ''])
	# 		self.current_pr_step += 1
	# 		self.current_reward_value += self.current_reward
	# 		self.protocol_floatlayout.add_event(
	# 			[0, 'Variable Change', 'Current Reward', 'Value', str(self.current_reward_value),
	# 			 '', '', '', ''])
	# 		self.current_response_count = 0
	# 		if self.reward_type == 'point':
	# 			self.feedback_string = 'Reward: \n %d Points' % self.current_reward_value
	# 		elif self.reward_type == 'currency':
	# 			self.current_reward_value = 0.00
	# 			self.feedback_string = 'Reward: \n $%.2f' % self.current_reward_value
	# 		self.feedback_label.text = self.feedback_string
			
	# 	if self.current_pr_step > self.current_pr_threshold_step_max:
	# 		self.stage_index += 1
	# 		self.current_stage = self.stage_list[self.stage_index]
	# 		self.protocol_floatlayout.add_event(
	# 			[0, 'Variable Change', 'Current Stage', 'Value', str(self.current_stage),
	# 			 '', '', '', ''])
	# 		self.current_pr_step = 0
	# 		self.current_reward = self.reward_list[self.stage_index]
	# 		self.current_pr_threshold = self.baseline_pr_threshold

	# 	if self.current_trial > self.session_trial_max:
	# 		self.protocol_end()
	# 		return
		
	# 	if self.stage_index > len(self.stage_list):
	# 		self.protocol_end()
	# 		return

	# def block_contingency(self):
	# 	self.protocol_floatlayout.clear_widgets()
		
	# 	if self.stage_index == 0:
	# 		self.stage_index = 1
	# 		self.current_block = 1
	# 		self.trial_configuration = random.randint(1,6)
	# 		self.generate_trial_contingency()
	# 		self.current_stage = self.stage_list[self.stage_index]
	# 	elif self.stage_index == 1:
	# 		self.current_block += 1
	# 		if self.current_block > self.block_count:
	# 			self.protocol_end()
	# 			return
			
	# 		self.trial_configuration = random.randint(1,6)
	# 		self.generate_trial_contingency()

	# 	self.block_screen()

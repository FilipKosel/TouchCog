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
		self.protocol_name = '4-hPRL'
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
		

		# Define Data Columns
		
		self.data_cols = [
			'TrialNo'
			, 'Stage'
			, 'ReversalNo'
			, 'TargetImage'
			, 'TargetLoc'
			, 'NontargetImage'
			, 'NontargetLoc'
			, 'TargetReward'
			, 'NontargetReward'
			# , 'ImageChosen'
			, 'SideChosen'
			, 'Correct'
			, 'Rewarded'
			, 'ResponseLat'
			]

		self.metadata_cols = [
			'participant_id'
			, 'age_range'
			, 'skip_tutorial_video'
			, 'block_change_on_duration_only'
			, 'training_task'
			, 'iti_fixed_or_range'
			, 'iti_length'
			, 'feedback_length'
			, 'block_duration'
			, 'block_min_rest_duration'
			, 'session_duration'
			, 'block_multiplier'
			, 'block_trial_max'
			, 'target_reward_probability'
			, 'reversal_threshold'
			, 'max_reversals'
			, 'image_set'
			, 'training_target_image'
			, 'training_nontarget_image'
			, 'training_block_max_correct'
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

		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])
		self.tutorial_video_length = int(self.parameters_dict['tutorial_video_length'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_import = self.parameters_dict['iti_length']
		iti_import = iti_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration = int(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])
		self.block_trial_max = int(self.parameters_dict['block_trial_max'])
		
		self.target_reward_probability = float(self.parameters_dict['target_reward_probability'])
		self.reversal_threshold = int(self.parameters_dict['reversal_threshold'])
		self.max_reversals = int(self.parameters_dict['max_reversals'])

		self.image_set = self.parameters_dict['image_set']

		self.training_target_image = self.parameters_dict['training_target_image']
		self.training_nontarget_image = self.parameters_dict['training_nontarget_image']
		
		self.training_block_max_correct = int(self.parameters_dict['training_block_max_correct'])

		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']


		# Define Variables - List

		self.stage_list = list()

		if self.parameters_dict['training_task'] == 1:

			self.stage_list.append('Training')
		

		self.stage_list.append('Test')


		# Define Language

		self.language = 'English'
		self.set_language(self.language)


		# Define Paths

		self.language_dir_path = pathlib.Path('Protocol', self.protocol_name, 'Language', self.language)

		self.image_dir_path = pathlib.Path('Protocol', self.protocol_name, 'Image')


		# Define Clock
		
		self.block_check_clock = Clock
		self.block_check_clock.interupt_next_only = False

		self.block_check_event = self.block_check_clock.create_trigger(self.block_contingency, 0, interval=True)

		self.block_check_event.cancel()


		self.task_clock = Clock
		self.task_clock.interupt_next_only = False

		self.trial_contingency_event = self.task_clock.create_trigger(self.trial_contingency, 0, interval=True)
		self.trial_contingency_event.cancel()


		# Define Variables - Time

		self.start_stimulus = 0.0
		self.response_lat = 0.0


		# Define Variables - Count

		self.current_hits = 0
		self.current_reversal = 0

		self.stage_index = 0

		self.target_image_index = 0
		self.nontarget_image_index = 1

		self.point_counter = 0


		# Define Boolean

		self.target_rewarded = True
		self.nontarget_rewarded = False

		self.choice_rewarded = True


		# Define Variables - String

		self.target_image = self.training_target_image
		self.nontarget_image = self.training_nontarget_image
		self.current_stage = self.stage_list[self.stage_index]
		self.feedback_string = ''
		self.side_chosen = ''


		# Define Widgets - Images

		self.stimulus_path_list = list(self.image_dir_path.glob(str(pathlib.Path('Targets', self.image_set, '*.png'))))
		stimulus_image_list = list()

		for filename in self.stimulus_path_list:
			stimulus_image_list.append(filename.stem)
		
		self.total_image_list = self.stimulus_path_list


		self.hold_image_path = str(self.image_dir_path / (self.hold_image + '.png'))
		self.mask_image_path = str(self.image_dir_path / (self.mask_image + '.png'))
		

		self.stimulus_size = (0.4 * self.width_adjust, 0.4 * self.height_adjust)
		self.stimulus_pos_l = {'center_x': 0.25, 'center_y': 0.55}
		self.stimulus_pos_r = {'center_x': 0.75, 'center_y': 0.55}

		self.left_stimulus = ImageButton(source=self.mask_image_path)
		self.left_stimulus.size_hint = self.stimulus_size
		self.left_stimulus.pos_hint = self.stimulus_pos_l

		self.right_stimulus = ImageButton(source=self.mask_image_path)
		self.right_stimulus.size_hint = self.stimulus_size
		self.right_stimulus.pos_hint = self.stimulus_pos_r


		# Define Widgets - Text

		self.score_string = 'Your Points:\n%s' % (0)
		self.score_label = Label(text=self.score_string, font_size='50sp', markup=True, halign='center')
		self.score_label.size_hint = (0.8, 0.2)
		self.score_label.pos_hint = {'center_x': 0.5, 'center_y': 0.9}


		# Define Widgets - Instructions
		
		self.instruction_path = str(self.language_dir_path / 'Instructions.ini')
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Main'] = {}
		
		
		instruction_temp_train_str = self.instruction_config['Main']['train']
		instruction_temp_probe_str = self.instruction_config['Main']['task']
		
		self.instruction_dict['Main']['train'] = instruction_temp_train_str
		self.instruction_dict['Main']['task'] = instruction_temp_probe_str




	# Initialization Functions #
		
	def load_parameters(self,parameter_dict):

		self.parameters_dict = parameter_dict
		
		config_path = str(pathlib.Path('Protocol', self.protocol_name, 'Configuration.ini'))
		config_file = configparser.ConfigParser()
		config_file.read(config_path)
		
		
		self.participant_id = self.parameters_dict['participant_id']
		self.age_range = self.parameters_dict['age_range']
		
		self.language = self.parameters_dict['language']


		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])
		self.tutorial_video_length = int(self.parameters_dict['tutorial_video_length'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_import = self.parameters_dict['iti_length']
		iti_import = iti_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration = int(self.parameters_dict['block_duration'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])
		self.block_trial_max = int(self.parameters_dict['block_trial_max'])
		
		self.target_reward_probability = float(self.parameters_dict['target_reward_probability'])
		self.reversal_threshold = int(self.parameters_dict['reversal_threshold'])
		self.max_reversals = int(self.parameters_dict['max_reversals'])

		self.image_set = self.parameters_dict['image_set']

		self.training_target_image = self.parameters_dict['training_target_image']
		self.training_nontarget_image = self.parameters_dict['training_nontarget_image']
		
		self.training_block_max_correct = int(self.parameters_dict['training_block_max_correct'])

		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']


		# Define Variables - List

		self.stage_list = list()

		if self.parameters_dict['training_task'] == 1:

			self.stage_list.append('Training')
		

		self.stage_list.append('Test')


		# Define Language

		self.language = 'English'
		self.set_language(self.language)


		# Define Paths

		self.language_dir_path = pathlib.Path('Protocol', self.protocol_name, 'Language', self.language)

		self.image_dir_path = pathlib.Path('Protocol', self.protocol_name, 'Image')


		# Define Variables - Time

		self.start_stimulus = 0.0
		self.response_lat = 0.0
		
		self.iti_range = [float(iNum) for iNum in iti_import]
		self.iti_length = self.iti_range[0]


		# Define Variables - Count

		self.current_hits = 0
		self.current_reversal = 0

		self.current_block = 0
		self.current_block_trial = 0

		self.stage_index = 0

		self.point_counter = 0


		image_index_choice = [0, 1]
		random.shuffle(image_index_choice)

		self.target_image_index = image_index_choice[0]
		self.nontarget_image_index = image_index_choice[1]


		# Define Boolean

		self.target_rewarded = True
		self.nontarget_rewarded = False

		self.choice_rewarded = True


		# Nontarget Prob

		self.nontarget_reward_probability = round(1 - self.target_reward_probability, 2)

		self.trial_reward_list = list()
		self.trial_reward_list_index = -1

		for iTrial in range(int(self.target_reward_probability * 20)):
			self.trial_reward_list.append('Target')
		

		for iTrial in range(int(self.nontarget_reward_probability * 20)):
			self.trial_reward_list.append('Nonarget')
		
		random.shuffle(self.trial_reward_list)


		# Define Variables - String

		self.target_image = self.training_target_image
		self.nontarget_image = self.training_nontarget_image

		self.current_stage = self.stage_list[self.stage_index]
		self.feedback_string = ''
		self.side_chosen = ''

		self.target_loc_list = ['Left', 'Right']
		random.shuffle(self.target_loc_list)

		self.target_loc_index = 0
		self.nontarget_loc_index = 1

		self.target_loc = self.target_loc_list[self.target_loc_index]
		self.nontarget_loc = self.target_loc_list[self.nontarget_loc_index]


		# Define Widgets - Images

		self.stimulus_path_list = list(self.image_dir_path.glob(str(pathlib.Path('Targets', self.image_set, '*.png'))))
		self.target_image_list = list()

		for filename in self.stimulus_path_list:
			self.target_image_list.append(filename.stem)
		
		self.total_image_list = self.stimulus_path_list


		self.hold_image_path = str(self.image_dir_path / (self.hold_image + '.png'))
		self.mask_image_path = str(self.image_dir_path / (self.mask_image + '.png'))


		self.training_target_image_path = str(self.image_dir_path / (self.training_target_image + '.png'))
		self.training_nontarget_image_path = str(self.image_dir_path / (self.training_nontarget_image + '.png'))


		self.total_image_list += [self.hold_image_path, self.mask_image_path, self.training_target_image_path, self.training_nontarget_image_path]

		print('\n\nTotal image list: ', self.total_image_list, '\n\n')

		self.load_images(self.total_image_list)


		if len(self.target_image_list) == 1:

			self.stimulus_image_source = str(self.stimulus_path_list[0])
		
		else:

			self.stimulus_image_source = self.mask_image_path
		

		self.stimulus_size = (0.4 * self.width_adjust, 0.4 * self.height_adjust)
		self.stimulus_pos_l = {'center_x': 0.25, 'center_y': 0.55}
		self.stimulus_pos_r = {'center_x': 0.75, 'center_y': 0.55}

		self.left_stimulus = ImageButton(source=self.stimulus_image_source)
		self.left_stimulus.size_hint = self.stimulus_size
		self.left_stimulus.pos_hint = self.stimulus_pos_l
		self.left_stimulus.bind(on_press=self.left_pressed)

		self.right_stimulus = ImageButton(source=self.stimulus_image_source)
		self.right_stimulus.size_hint = self.stimulus_size
		self.right_stimulus.pos_hint = self.stimulus_pos_r
		self.right_stimulus.bind(on_press=self.right_pressed)
		

		self.instruction_button = Button(font_size='60sp')
		self.instruction_button.size_hint = [0.4, 0.15]
		self.instruction_button.pos_hint =  {"center_x": 0.5, "center_y": 0.1}
		# self.instruction_button.text = ''
		self.instruction_button.bind(on_press=self.section_start)
		# self.instruction_button_str = ''



		
		
		# self.present_tutorial()
		self.start_protocol_from_tutorial()











		
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

			self.tutorial_video_end_event = self.stimdur_clock.schedule_once(self.present_tutorial_video_start_button, self.tutorial_video_length + 1)
	


	def present_tutorial_video_start_button(self, *args):

		self.tutorial_video_end_event.cancel()

		self.tutorial_video.state = 'pause'

		self.protcol_floatlayout.add_widget(self.tutorial_start_button)
	
	
	
	def start_protocol_from_tutorial(self, *args):
		self.generate_output_files()
		self.metadata_output_generation()
		self.start_protocol()


	
	def start_protocol(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		self.start_clock()
		
		self.block_contingency()

























	def start_protocol(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		print('Stage list: ', self.stage_list)
		
		self.start_clock()

		self.block_check_event()
	
	
	
	def stimulus_presentation(self, *args): # Stimulus presentation
		
		self.printlog('Stimulus presentation')

		self.iti_event.cancel()

		self.hold_button.unbind(on_release=self.premature_response)

		self.protocol_floatlayout.remove_widget(self.hold_button)

		# self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_widget(self.left_stimulus)
		self.protocol_floatlayout.add_widget(self.right_stimulus)
		
		self.stimulus_start_time = time.time()
		
		# self.feedback_string = ''
		# self.feedback_label.text = ''
		
		self.protocol_floatlayout.add_event([
			self.stimulus_start_time - self.start_time
			, 'Stage Change'
			, 'Display Target'
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
		

		# self.feedback_string = self.feedback_dict['wait']
		self.response_lat = 0
		self.iti_active = False
		self.feedback_label.text = self.feedback_dict['wait']
		
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
	
	
	
	# Left Stimulus Pressed
	
	def left_pressed(self, *args):

		self.stimulus_press_time = time.time()
		
		self.printlog('Left pressed')

		self.protocol_floatlayout.add_event([
			time.time() - self.start_time
			, 'Stage Change'
			, 'Left Stimulus Pressed'
			])
		

		if self.target_loc == 'Left':
		
			self.last_response = 1
			self.current_hits += 1

			if self.current_stage == 'Training':

				self.feedback_label.text = '[color=00C000]CORRECT[/color]'
				self.choice_rewarded = True

			elif self.target_rewarded:
				
				self.feedback_label.text = self.feedback_dict['correct']
				self.choice_rewarded = True

				self.point_counter += 10

			else:
				
				self.feedback_label.text = ''
				self.choice_rewarded = False

		else:
		
			self.last_response = 0
			self.current_hits = 0

			if self.target_rewarded:
				
				self.feedback_label.text = ''
				self.choice_rewarded = False

			else:
				
				self.feedback_label.text = self.feedback_dict['correct']
				self.choice_rewarded = True

				self.point_counter += 10
	

		self.side_chosen = 'Left'

		self.response_latency = self.stimulus_press_time - self.stimulus_start_time

		# self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.remove_widget(self.left_stimulus)
		self.protocol_floatlayout.remove_widget(self.right_stimulus)

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Image Removed'
			, 'Target'
			, 'Location'
			, self.target_loc
			])

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Image Removed'
			, 'Nontarget'
			, 'Location'
			, self.nontarget_loc
			])


		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		if self.feedback_label.text != '' \
			and not self.feedback_on_screen:
			
			self.protocol_floatlayout.add_widget(self.feedback_label)

			self.feedback_start_time = time.time()
			self.feedback_on_screen = True

			self.protocol_floatlayout.add_event([
				(self.feedback_start_time - self.start_time)
				, 'Object Display'
				, 'Text'
				, 'Feedback'
				, self.feedback_label.text
				])
		
		
		self.protocol_floatlayout.add_widget(self.hold_button)
		
		self.write_trial()
		
		self.trial_contingency_event()

		return
	
	
	
	# Right Stimulus Pressed
	
	def right_pressed(self, *args):

		self.stimulus_press_time = time.time()
		
		self.printlog('Right pressed')

		self.protocol_floatlayout.add_event([
			time.time() - self.start_time
			, 'Stage Change'
			, 'Right Stimulus Pressed'
			])
		

		if self.target_loc == 'Right':
		
			self.last_response = 1
			self.current_hits += 1

			if self.current_stage == 'Training':

				self.feedback_label.text = '[color=00C000]CORRECT[/color]'
				self.choice_rewarded = True

			elif self.target_rewarded:
				
				self.feedback_label.text = self.feedback_dict['correct']
				self.choice_rewarded = True

				self.point_counter += 10

			else:
				
				self.feedback_label.text = ''
				self.choice_rewarded = False

		else:
		
			self.last_response = 0
			self.current_hits = 0

			if self.target_rewarded:
				
				self.feedback_label.text = ''
				self.choice_rewarded = False

			else:
				
				self.feedback_label.text = self.feedback_dict['correct']
				self.choice_rewarded = True

				self.point_counter += 10
	

		self.side_chosen = 'Right'

		self.response_latency = self.stimulus_press_time - self.stimulus_start_time

		# self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.remove_widget(self.left_stimulus)
		self.protocol_floatlayout.remove_widget(self.right_stimulus)

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Image Removed'
			, 'Target'
			, 'Location'
			, self.target_loc
			])

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Image Removed'
			, 'Nontarget'
			, 'Location'
			, self.nontarget_loc
			])


		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)

		if self.feedback_label.text != '' \
			and not self.feedback_on_screen:
			
			self.protocol_floatlayout.add_widget(self.feedback_label)

			self.feedback_start_time = time.time()
			self.feedback_on_screen = True

			self.protocol_floatlayout.add_event([
				(self.feedback_start_time - self.start_time)
				, 'Object Display'
				, 'Text'
				, 'Feedback'
				, self.feedback_label.text
				])
		
		
		self.protocol_floatlayout.add_widget(self.hold_button)
		
		self.write_trial()
		
		self.trial_contingency_event()

		return
	
	
	
	# # Nontarget Pressed
	
	# def nontarget_pressed(self, *args):
		
	# 	self.printlog('Nontarget pressed')

	# 	self.protocol_floatlayout.add_event([
	# 		time.time() - self.start_time
	# 		, 'Stage Change'
	# 		, 'Incorrect Response'
	# 		])
		
	# 	self.last_response = 0

	# 	self.stimulus_press_time = time.time()
	# 	self.response_latency = self.stimulus_press_time - self.stimulus_start_time

	# 	# self.protocol_floatlayout.clear_widgets()

	# 	self.protocol_floatlayout.remove_widget(self.left_stimulus)
	# 	self.protocol_floatlayout.remove_widget(self.right_stimulus)

	# 	self.protocol_floatlayout.add_event([
	# 		(self.stimulus_press_time - self.start_time)
	# 		, 'Image Removed'
	# 		, 'Target'
	# 		, 'Image'
	# 		, self.target_image
	# 		, 'Location'
	# 		, self.target_loc
	# 		])
		

	# 	if self.target_rewarded:
			
	# 		# self.feedback_string = ''
	# 		self.feedback_label.text = ''

	# 		self.choice_rewarded = False

	# 	else:
			
	# 		# self.feedback_string = self.feedback_dict['correct']
	# 		self.feedback_label.text = self.feedback_dict['correct']

	# 		self.choice_rewarded = True


	# 	if self.nontarget_loc == 'Left':

	# 		self.side_chosen = 'Left'
		
	# 	else:

	# 		self.side_chosen = 'Right'
		

	# 	self.image_chosen = self.nontarget_image


	# 	self.hold_button.bind(on_press=self.iti)
	# 	self.hold_button.bind(on_release=self.premature_response)

	# 	if self.feedback_label.text != '' \
	# 		and not self.feedback_on_screen:
			
	# 		self.protocol_floatlayout.add_widget(self.feedback_label)

	# 		self.feedback_start_time = time.time()
	# 		self.feedback_on_screen = True

	# 		self.protocol_floatlayout.add_event([
	# 			(self.feedback_start_time - self.start_time)
	# 			, 'Object Display'
	# 			, 'Text'
	# 			, 'Feedback'
	# 			, self.feedback_label.text
	# 			])
		
	# 	self.write_trial()
		
	# 	self.trial_contingency_event()

	# 	return
	
	
	
	# Data Saving Function
	
	def write_trial(self):
		

		
		# self.data_cols = [
		# 	'TrialNo'
		# 	, 'Stage'
		# 	, 'ReversalNo'
		# 	, 'TargetImage'
		# 	, 'TargetLoc'
		# 	, 'NontargetImage'
		# 	, 'NontargetLoc'
		# 	, 'TargetReward'
		# 	, 'NontargetReward'
		# 	, 'ImageChosen'
		# 	, 'SideChosen'
		# 	, 'Correct'
		# 	, 'Rewarded'
		# 	, 'ResponseLat'
		# 	]
		

		trial_data = [
			self.current_trial
			, self.current_stage
			, self.current_reversal
			, self.target_image
			, self.target_loc
			, self.nontarget_image
			, self.nontarget_loc
			, self.target_rewarded
			, self.nontarget_rewarded
			# , self.image_chosen
			, self.side_chosen
			, self.last_response
			, self.choice_rewarded
			, self.response_latency
			]
		
		self.write_summary_file(trial_data)
	
	
	
	# Trial Contingency Functions
	
	def trial_contingency(self, *args):
		
		try:

			if self.feedback_on_screen:
				# self.printlog('Feedback on screen')
				
				if (time.time() - self.feedback_start_time) >= self.feedback_length:
					# self.printlog('Feedback over')
					self.trial_contingency_event.cancel()
					self.protocol_floatlayout.remove_widget(self.feedback_label)
					# self.protocol_floatlayout.clear_widgets()
					# self.feedback_string = ''
					self.feedback_label.text = ''
					self.feedback_on_screen = False
				else:
					# self.printlog('Wait for feedback delay')
					return
				
			else:
				# self.printlog('Block check event cancel')
				self.trial_contingency_event.cancel()

			if self.current_block_trial != 0:
				
				self.printlog('\n\n\n')
				self.printlog('Trial contingency start')
				self.printlog('')
				self.printlog('Current trial: ', self.current_trial)
				self.printlog('Current stage: ', self.current_stage)
				self.printlog('Current task time: ', (time.time() - self.start_time))
				self.printlog('Current block time: ', (time.time() - self.block_start_time))
				self.printlog('')
				self.printlog('ITI: ', self.iti_length)
				self.printlog('Start target time: ', (self.stimulus_start_time - self.start_time))
				self.printlog('Response latency: ', self.response_latency)
				self.printlog('')
				self.printlog('Last response: ', self.last_response)
				self.printlog('')
				self.printlog('Target image: ', self.target_image)
				self.printlog('Target loc: ', self.target_loc)
				self.printlog('')
				self.printlog('Nontarget image: ', self.nontarget_image)
				self.printlog('Nontarget loc: ', self.nontarget_loc)
				self.printlog('')
				self.printlog('Target rewarded: ', str(self.target_rewarded))
				self.printlog('Nontarget rewarded: ', str(self.nontarget_rewarded))
				self.printlog('')
				
				
				self.printlog('')


			
				self.protocol_floatlayout.add_event([
					time.time() - self.start_time
					, 'Variable Change'
					, 'Current Trial'
					, 'Value'
					, str(self.current_trial)
					])
				

				self.response_tracking.append(self.last_response)

				if self.current_stage == 'Training' \
					and self.last_response == -1:

					self.response_tracking.pop()




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
			



			# Set next trial parameters
			
			self.feedback_label.text = ''

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

			


			if self.current_hits >= self.reversal_threshold:

				self.current_hits = 0
				self.current_reversal += 1

				if self.current_reversal > self.max_reversals:

					self.block_check_event()
				
				else:

					self.target_loc_index += 1
					self.nontarget_loc_index += 1

					if self.target_loc_index >= len(self.target_loc_list):

						self.target_loc_index = 0

					elif self.nontarget_loc_index >= len(self.target_loc_list):
						
						self.nontarget_loc_index = 0
					

					self.target_loc = self.target_loc_list[self.target_loc_index]
					self.nontarget_loc = self.target_loc_list[self.nontarget_loc_index]



			

			# self.target_loc = random.choice(['Left', 'Right'])

			# if self.target_loc == 'Left':

			# 	self.left_stimulus.texture = self.image_dict[self.target_image].image.texture

			# 	self.right_stimulus.texture = self.image_dict[self.nontarget_image].image.texture

			# 	self.nontarget_loc = 'Right'
			
			# else:

			# 	self.left_stimulus.texture = self.image_dict[self.nontarget_image].image.texture

			# 	self.right_stimulus.texture = self.image_dict[self.target_image].image.texture

			# 	self.nontarget_loc = 'Left'


			if self.current_stage == 'Training':

				self.target_rewarded = True
				self.nontarget_rewarded = False
			
			else:

				self.trial_reward_list_index += 1

				if (self.trial_reward_list_index >= len(self.trial_reward_list)):

					random.shuffle(self.trial_reward_list)
					self.trial_reward_list_index = 0
				
				if self.trial_reward_list[self.trial_reward_list_index] == 'Target':

					self.target_rewarded = True
					self.nontarget_rewarded = False
				
				else:

					self.target_rewarded = False
					self.nontarget_rewarded = True
			

			# self.target_rewarded = np.random.choice([True, False], p = [self.target_reward_probability, self.nontarget_reward_probability])

			# if self.target_rewarded:

			# 	self.nontarget_rewarded = False
			
			# else:

			# 	self.nontarget_rewarded = True
			

			# if self.current_stage == 'Training':

			# 	if self.target_loc == 'Left':

			# 		self.left_stimulus.bind(on_press=self.target_pressed)
				
			# 	else:

			# 		self.right_stimulus.bind(on_press=self.target_pressed)
			
			# else:
			
				# self.target_rewarded = np.random.choice([True, False], p = [self.target_reward_probability, self.nontarget_reward_probability])

			# 	if ((self.target_loc == 'Left') and self.target_rewarded) \
			# 		or ((self.target_loc == 'Right') and not self.target_rewarded):

			# 			self.left_stimulus.bind(on_press=self.target_pressed)
			# 			self.right_stimulus.bind(on_press=self.nontarget_pressed)

			# 	else:

			# 			self.left_stimulus.bind(on_press=self.nontarget_pressed)
			# 			self.right_stimulus.bind(on_press=self.target_pressed)
			

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
			

			self.last_response = 0
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()
	



# 	def block_break_screen(self, *args):
		
# # 		self.protocol_floatlayout.clear_widgets()
		
# 		if not self.block_started:
			
# 			self.protocol_floatlayout.add_widget(self.block_label)

# 			self.protocol_floatlayout.add_event([
# 				(time.time() - self.start_time)
# 				, 'Object Display'
# 				, 'Text'
# 				, 'Block'
# 				, 'Instruction'
# 				])
			
# 			self.block_start = time.time()
# 			self.block_start_time = time.time()
# 			self.block_started = True

# 			self.block_break_event()
		
# 		if (time.time() - self.block_start) > self.block_min_rest_duration:
			
# 			self.block_break_event.cancel()

# 			self.protocol_floatlayout.add_widget(self.continue_button)

# 			self.protocol_floatlayout.add_event([
# 				(time.time() - self.start_time)
# 				, 'Object Display'
# 				, 'Button'
# 				, 'Block'
# 				, 'Continue'
# 				])
	
	
	
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
	


	def final_results_screen(self, *args):

		self.end_protocol_button = Button(font_size='60sp')
		self.end_protocol_button.size_hint = [0.4, 0.15]
		self.end_protocol_button.pos_hint =  {"center_x": 0.50, "center_y": 0.1}
		self.end_protocol_button.text = 'End Task'
		self.end_protocol_button.bind(on_press=self.protocol_end)

		self.result_label_str = 'Great job! You have earned ' + str(self.point_counter) + ' points!'
		self.result_label = Label(text=self.result_label_str, font_size='50sp', markup=True, halign='center')
		self.result_label.size_hint = (0.8, 0.3)
		self.result_label.pos_hint = {'center_x': 0.5, 'center_y': 0.6}

		self.protocol_floatlayout.add_widget(self.result_label)
		self.protocol_floatlayout.add_widget(self.end_protocol_button)


	
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
					# self.feedback_string = ''
					self.feedback_label.text = ''
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
				# self.protocol_end()
				self.final_results_screen()

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



			

			
			# Set next block parameters

			if self.current_stage == 'Training':

				self.target_image = self.training_target_image
				self.nontarget_image = self.training_nontarget_image
			
			
			elif len(self.target_image_list) == 1:

				self.target_image = self.target_image_list[0]
				self.nontarget_image = self.target_image

				self.target_loc_index += 1
				self.nontarget_loc_index += 1

				if self.target_loc_index >= len(self.target_loc_list):

					self.target_loc_index = 0

				elif self.nontarget_loc_index >= len(self.target_loc_list):
					
					self.nontarget_loc_index = 0
				

				self.target_loc = self.target_loc_list[self.target_loc_index]
				self.nontarget_loc = self.target_loc_list[self.nontarget_loc_index]
			

			else:

				self.target_image_index += 1
				self.nontarget_image_index += 1

				if self.target_image_index >= len(self.target_image_list):

					self.target_image_index = 0

				elif self.nontarget_image_index >= len(self.target_image_list):

					self.nontarget_image_index = 0
				

				self.target_image = self.target_image_list[self.target_image_index]
				self.nontarget_image = self.target_image_list[self.nontarget_image_index]



				random.shuffle(self.trial_reward_list)
				self.trial_reward_list_index = 0
				
				if self.trial_reward_list[self.trial_reward_list_index] == 'Target':

					self.target_rewarded = True
					self.nontarget_rewarded = False
				
				else:

					self.target_rewarded = False
					self.nontarget_rewarded = True



			if self.current_block == 1: #and self.display_instructions:
				
				self.printlog('Section Task Instructions')
				# self.instruction_label.text = #self.instruction_dict[str(self.current_stage)]['task']
				
				self.block_max_length = 360
				
				if self.current_stage == 'Training':
					self.block_max_length = self.training_block_max_correct
					self.instruction_label.text = self.instruction_dict['Main']['train']
				

				else:

					self.instruction_label.text = self.instruction_dict['Main']['task']

				self.instruction_button.text = 'Begin Section'

				
				self.protocol_floatlayout.add_widget(self.instruction_label)
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
			

			self.response_tracking = [0,0,0,0,0]
			self.last_response = 0
			self.contingency = 0
			self.trial_outcome = 0
			self.current_block_trial = 0
			

			self.printlog('Block contingency end')

			self.trial_contingency_event()
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
		# except:
			
		# 	self.printlog('Error; program terminated.')
			
		# 	self.protocol_end()
























		

	# def start_protocol(self,*args):
	# 	self.protocol_floatlayout.add_event(
	# 		[0, 'Stage Change', 'Instruction Presentation', '', '',
	# 			'', '', '', ''])
	# 	self.protocol_floatlayout.remove_widget(self.instruction_label)
	# 	self.protocol_floatlayout.add_event(
	# 		[0, 'Text Removed', 'Task Instruction', '', '',
	# 			'', '', '', ''])
	# 	self.protocol_floatlayout.remove_widget(self.start_button)
	# 	self.protocol_floatlayout.add_event(
	# 		[0, 'Button Removed', 'Task Start Button', '', '',
	# 			'', '', '', ''])
	# 	self.start_clock()
		
	# 	self.protocol_floatlayout.add_widget(self.hold_button)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Button Displayed', 'Hold Button', '', '',
	# 			'', '', '', ''])
	# 	self.hold_button.size_hint = ((0.2 * self.width_adjust), (0.2 * self.height_adjust))
	# 	self.hold_button.size_hint_y = 0.2
	# 	self.hold_button.width = self.hold_button.height
	# 	self.hold_button.pos_hint = {"center_x":0.5,"center_y":0.1}
	# 	self.hold_button.bind(on_press=self.iti)
	# 	self.protocol_floatlayout.add_widget(self.score_label)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Text Displayed', 'Score', '', '',
	# 			'', '', '', ''])
				
	# def stimulus_presentation(self,*args):
	# 	self.protocol_floatlayout.add_widget(self.left_stimulus)
	# 	self.left_stimulus.size_hint = ((0.4 * self.width_adjust), (0.4 * self.height_adjust))
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Displayed', 'Left Stimulus', 'X Position', '1',
	# 			'Y Position', '1', 'Image Name', self.left_stimulus_image])
	# 	self.protocol_floatlayout.add_widget(self.right_stimulus)
	# 	self.right_stimulus.size_hint = ((0.4 * self.width_adjust), (0.4 * self.height_adjust))
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Displayed', 'Right Stimulus', 'X Position', '2',
	# 			'Y Position', '1', 'Image Name', self.right_stimulus_image])
			
	# 	self.start_stimulus = time.time()
		
	# 	self.stimulus_on_screen = True
			
				
	# def premature_response(self,*args):
	# 	if self.stimulus_on_screen == True:
	# 		return None
		
	# 	self.iti_event.cancel()
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Stage Change', 'Premature Response', '', '',
	# 			'', '', '', ''])
	# 	self.feedback_string = self.feedback_dict['wait']
	# 	contingency = '2'
	# 	response = '1'
	# 	self.response_lat = 0
	# 	self.iti_active = False
	# 	self.feedback_label.text = self.feedback_string
	# 	if self.feedback_on_screen == False:
	# 		self.protocol_floatlayout.add_widget(self.feedback_label)
	# 		self.protocol_floatlayout.add_event(
	# 			[time.time() - self.start_time, 'Text Displayed', 'Feedback', '', '',
	# 				'', '', '', ''])
	# 	self.hold_button.unbind(on_release=self.premature_response)
	# 	self.hold_button.bind(on_press=self.iti)
		
		
			
		
	# # Contingency Stages #
	# def left_stimulus_pressed(self,*args):
	# 	self.stimulus_on_screen = False
	# 	self.protocol_floatlayout.remove_widget(self.left_stimulus)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Removed', 'Left Stimulus', 'X Position', '1',
	# 			'Y Position', '1', 'Image Name', self.left_stimulus_image])
	# 	self.protocol_floatlayout.remove_widget(self.right_stimulus)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Removed', 'Right Stimulus', 'X Position', '2',
	# 			'Y Position', '1', 'Image Name', self.right_stimulus_image])
		
	# 	self.left_chosen = 1
	# 	self.right_chosen = 0
		
	# 	if self.left_stimulus_image == self.correct_image:
	# 		response = '1'
	# 		self.current_correct += 1
	# 		if self.reward_contingency == 1:
	# 			self.feedback_string = self.feedback_dict['correct']
	# 			self.current_score += 50
	# 			contingency = '1'
	# 		else:
	# 			self.feedback_string = self.feedback_dict['incorrect']
	# 			contingency = '0'
	# 	else:
	# 		response = '0'
	# 		self.current_correct = 0
	# 		if self.reward_contingency == 1:
	# 			self.feedback_string = self.feedback_dict['incorrect']
	# 			contingency = '0'
	# 		else:
	# 			self.feedback_string = self.feedback_dict['correct']
	# 			self.current_score += 50
	# 			contingency = '1'
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Variable Change', 'Trial Correct', 'Value', str(response),
	# 			'', '', '', ''])
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Variable Change', 'Total Correct', 'Value', str(self.current_correct),
	# 			'', '', '', ''])

	# 	self.response_lat = time.time() - self.start_stimulus

	# 	self.feedback_label.text = self.feedback_string
	# 	self.score_label.text = 'Your Points:\n%s' % (self.current_score)
	# 	self.protocol_floatlayout.add_widget(self.feedback_label)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Text Displayed', 'Feedback', '', '',
	# 			'', '', '', ''])
	# 	self.feedback_on_screen = True
	# 	self.write_trial(response, contingency)
	# 	self.trial_contingency()
		
	# 	self.hold_button.bind(on_press=self.iti)

	# def right_stimulus_pressed(self,*args):
	# 	self.stimulus_on_screen = False
	# 	self.protocol_floatlayout.remove_widget(self.left_stimulus)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Removed', 'Left Stimulus', 'X Position', '1',
	# 			'Y Position', '1', 'Image Name', self.left_stimulus_image])
	# 	self.protocol_floatlayout.remove_widget(self.right_stimulus)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Image Removed', 'Right Stimulus', 'X Position', '2',
	# 			'Y Position', '1', 'Image Name', self.right_stimulus_image])
		
	# 	self.left_chosen = 0
	# 	self.right_chosen = 1
		
	# 	if self.right_stimulus_image == self.correct_image:
	# 		response = '1'
	# 		self.current_correct += 1
	# 		if self.reward_contingency == 1:
	# 			self.feedback_string = self.feedback_dict['correct']
	# 			self.current_score += 50
	# 			contingency = '1'
	# 		else:
	# 			self.feedback_string = self.feedback_dict['incorrect']
	# 			contingency = '0'
	# 	else:
	# 		response = '0'
	# 		self.current_correct = 0
	# 		if self.reward_contingency == 1:
	# 			self.feedback_string = self.feedback_dict['incorrect']
	# 			contingency = '0'
	# 		else:
	# 			self.feedback_string = self.feedback_dict['correct']
	# 			self.current_score += 50
	# 			contingency = '1'
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Variable Change', 'Trial Correct', 'Value', str(response),
	# 			'', '', '', ''])
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Variable Change', 'Total Correct', 'Value', str(self.current_correct),
	# 			'', '', '', ''])
				

	# 	self.response_lat = time.time() - self.start_stimulus

	# 	self.feedback_label.text = self.feedback_string
	# 	self.score_label.text = 'Your Points:\n%s' % (self.current_score)
	# 	self.protocol_floatlayout.add_widget(self.feedback_label)
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Text Displayed', 'Feedback', '', '',
	# 			'', '', '', ''])
	# 	self.feedback_on_screen = True
	# 	self.write_trial(response, contingency)
	# 	self.trial_contingency()
		
	# 	self.hold_button.bind(on_press=self.iti)

	# # Data Saving Functions #
	# def write_trial(self, response, contingency):
	# 	if self.reward_contingency == 1:
	# 		s_min_cont = '0'
	# 	else:
	# 		s_min_cont = '1'
	# 	trial_data = [self.current_trial, self.current_stage, self.current_reversal, self.correct_image,
	# 					self.incorrect_image, self.left_stimulus_image, self.right_stimulus_image,
	# 					self.reward_contingency, s_min_cont, self.left_chosen, self.right_chosen, response, contingency,
	# 					self.response_lat]
	# 	self.write_summary_file(trial_data)
	# 	return

	# # Trial Contingency Functions #

	# def trial_contingency(self):
	# 	self.current_trial += 1
	# 	self.protocol_floatlayout.add_event(
	# 		[time.time() - self.start_time, 'Variable Change', 'Current Trial', 'Value', str(self.current_trial),
	# 			'', '', '', ''])
		
	# 	if self.current_trial > self.session_trial_max:
	# 		self.session_event.cancel()
	# 		self.protocol_end()
	# 		return
	# 	if self.stage_index == 0:
	# 		if self.current_correct >= 10:
	# 			self.block_contingency()
	# 			return
	# 		self.left_stimulus_index = random.randint(0,1)
	# 		if self.left_stimulus_index == 0:
	# 			self.right_stimulus_index = 1
	# 		else:
	# 			self.right_stimulus_index = 0
	# 		self.left_stimulus_image = self.training_images[self.left_stimulus_index]
	# 		self.right_stimulus_image = self.training_images[self.right_stimulus_index]
	# 		self.left_stimulus.texture = self.image_dict[self.left_stimulus_image].image.texture
	# 		self.right_stimulus.texture = self.image_dict[self.right_stimulus_image].image.texture
	# 		self.reward_contingency = 1

	# 	if self.stage_index == 1:
	# 		self.left_stimulus_index = random.randint(0,1)
	# 		if self.left_stimulus_index == 0:
	# 			self.right_stimulus_index = 1
	# 		else:
	# 			self.right_stimulus_index = 0
	# 		self.left_stimulus_image = self.test_images[self.left_stimulus_index]
	# 		self.right_stimulus_image = self.test_images[self.right_stimulus_index]
	# 		self.left_stimulus.texture = self.image_dict[self.left_stimulus_image].image.texture
	# 		self.right_stimulus.texture = self.image_dict[self.right_stimulus_image].image.texture
			
	# 		if self.current_correct >= self.reversal_threshold:
	# 			if self.correct_image == self.test_images[0]:
	# 				self.correct_image = self.test_images[1]
	# 				self.incorrect_image = self.test_images[0]
	# 			else:
	# 				self.correct_image = self.test_images[0]
	# 				self.incorrect_image = self.test_images[1]
	# 			self.current_correct = 0
	# 			self.current_reversal += 1
	# 			self.protocol_floatlayout.add_event(
	# 				[time.time() - self.start_time, 'Variable Change', 'Current Reversal', 'Value', str(self.current_reversal),
	# 					'', '', '', ''])
				
	# 		if self.reward_index >= len(self.reward_distribution):
	# 			self.reward_index = 0
	# 			random.shuffle(self.reward_distribution)
	# 		self.reward_contingency = self.reward_distribution[self.reward_index]
	# 		self.protocol_floatlayout.add_event(
	# 			[time.time() - self.start_time, 'Variable Change', 'Current Reward Contingency', 'Value',
	# 				str(self.reward_contingency), '', '', '', ''])
	# 		self.reward_index += 1
	# 		if self.current_reversal >= self.max_reversals:
	# 			self.protocol_end()
	# 			return
		
	# def block_contingency(self):
	# 	self.protocol_floatlayout.clear_widgets()
		
	# 	self.stage_index += 1
	# 	self.current_stage = self.stage_list[self.stage_index]
		
	# 	randindex = random.randint(0,1)
		
	# 	self.correct_image = self.test_images[randindex]
	# 	if randindex == 0:
	# 		self.incorrect_image = self.test_images[1]
	# 	else:
	# 		self.incorrect_image = self.test_images[0]
	# 	self.current_correct = 0
	# 	self.current_score = 0
	# 	self.trial_contingency()
	# 	self.block_screen()

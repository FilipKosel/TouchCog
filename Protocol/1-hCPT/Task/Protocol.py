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
		self.protocol_name = '1-hCPT'
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
			, 'Substage'
			, 'TarProb'
			, 'Block'
			, 'CurrentBlockTrial'
			#, 'Trial Type'
			, 'Stimulus'
			, 'Correction'
			, 'StimFrames'
			, 'StimDur'
			, 'LimHold'
			, 'Similarity'
			, 'BlurLevel'
			, 'NoiseMaskValue'
			, 'Response'
			, 'Contingency'
			, 'Outcome'
			, 'ResponseLatency'
			, 'StimulusPressLatency'
			, 'MovementLatency'
			]
		
		
		self.metadata_cols = [
			'participant_id'
			, 'age_range'
			, 'skip_tutorial_video'
			, 'block_change_on_duration_only'
			, 'training_task'
			, 'similarity_scaling'
			, 'noise_scaling'
			, 'blur_scaling'
			, 'speed_scaling'
			, 'noise_probe'
			, 'blur_probe'
			, 'speed_probe'
			, 'midprob_probe'
			, 'lowprob_probe'
			, 'highprob_probe'
			, 'flanker_probe'
			, 'sart_probe'
			, 'iti_fixed_or_range'
			, 'iti_length'
			, 'stimulus_duration'
			, 'limited_hold'
			, 'feedback_length'
			, 'block_duration-staircase'
			, 'block_duration-probe'
			, 'block_min_rest_duration'
			, 'session_duration'
			, 'block_multiplier'
			, 'block_trial_max'
			, 'training_block_max_correct'
			, 'target_prob_over_num_trials'
			, 'target_prob_low'
			, 'target_prob_mid'
			, 'target_prob_high'
			, 'target_prob_similarity'
			, 'target_prob_flanker'
			, 'stimulus_family'
			, 'display_stimulus_outline'
			, 'similarity_percentile_initial'
			, 'similarity_percentile_range'
			, 'staircase_stimdur_min_frames'
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

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		iti_temp = self.parameters_dict['iti_length']
		iti_temp = iti_temp.split(',')
		
		self.stimdur_import = self.parameters_dict['stimulus_duration']
		self.stimdur_import = self.stimdur_import.split(',')
		
		self.limhold_import = self.parameters_dict['limited_hold']
		self.limhold_import = self.limhold_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration_staircase = int(self.parameters_dict['block_duration-staircase'])
		self.block_duration_probe = int(self.parameters_dict['block_duration-probe'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])
		self.block_trial_max = int(self.parameters_dict['block_trial_max'])
		self.training_block_max_correct = int(self.parameters_dict['training_block_max_correct'])
		self.correction_trials_active = int(self.parameters_dict['correction_trials_active'])
		
# 		self.target_prob_low = round(20 * float(self.parameters_dict['target_probability']))

		self.target_prob_trial_num = int(self.parameters_dict['target_prob_over_num_trials'])
		
		target_prob_import = self.parameters_dict['target_prob_list']
		target_prob_import = target_prob_import.split(',')

		self.target_prob_low = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_low']))
		self.target_prob_mid = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_mid']))
		self.target_prob_high = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_high']))
		self.target_prob_sim = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_similarity']))
		self.target_prob_flanker = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_flanker']))
		
		# self.stimulus_family = self.parameters_dict['stimulus_family']

		self.display_stimulus_outline = int(self.parameters_dict['display_stimulus_outline'])
		self.mask_during_limhold = int(self.parameters_dict['mask_during_limhold'])
		self.limhold_mask_type = self.parameters_dict['limhold_mask_type']
		
		self.similarity_percentile_initial = float(self.parameters_dict['similarity_percentile_initial'])
		self.similarity_percentile_range = float(self.parameters_dict['similarity_percentile_range'])
		self.staircase_stimdur_frame_min = float(self.parameters_dict['staircase_stimdur_min_frames'])
		staircase_stimdur_seconds_max = float(self.parameters_dict['staircase_stimdur_max_seconds'])

		# self.staircase_limhold_change = float(self.parameters_dict['staircase_limhold_change'])
		# self.staircase_limhold_min = float(self.parameters_dict['staircase_limhold_min'])
		
		# self.target_image = str(self.parameters_dict['alternate_target_image_list'])
		# self.nontarget_images = str(self.parameters_dict['alternate_nontarget_images_list'])
		
		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']
		
		
		# Create stage list
		
		self.stage_list = list()
		
		if int(self.parameters_dict['training_task']) == 1:
			
			self.stage_list.append('Training')
		
		
		if int(self.parameters_dict['speed_scaling']) == 1:
			
			self.stage_list.append('Speed_Scaling')
			
		
		if int(self.parameters_dict['similarity_scaling']) == 1:
			
			self.stage_list.append('Similarity')
			self.stimulus_family = 'Fb'
		
		else:
			
			self.stimulus_family = self.parameters_dict['stimulus_family']
		

		if int(self.parameters_dict['noise_scaling']) == 1 \
			and 'Similarity' not in self.stage_list:
			
			self.stage_list.append('Noise_Scaling')
		

		if int(self.parameters_dict['blur_scaling']) == 1 \
			and 'Similarity' not in self.stage_list:
			
			self.stage_list.append('Blur_Scaling')
		
		
		if int(self.parameters_dict['noise_probe']) == 1:
			
			self.stage_list.append('Noise')
		
		
		if int(self.parameters_dict['blur_probe']) == 1:
			
			self.stage_list.append('Blur')
		
		
		if int(self.parameters_dict['speed_probe']) == 1:
			
			self.stage_list.append('Speed')
		
		
		if int(self.parameters_dict['flanker_probe']) == 1:
			
			self.stage_list.append('Flanker')
		
		
		if int(self.parameters_dict['tarprob_probe']) == 1:
			
			self.stage_list.append('TarProb')
		
		
		if int(self.parameters_dict['midprob_probe']) == 1:
			
			self.stage_list.append('MidProb')
		
		
		if int(self.parameters_dict['lowprob_probe']) == 1:
			
			self.stage_list.append('LowProb')
		
		
		if int(self.parameters_dict['highprob_probe']) == 1:
			
			self.stage_list.append('HighProb')
		
		
		if int(self.parameters_dict['sart_probe']) == 1:
			
			self.stage_list.append('SART')
		
		
		# Set images

		self.similarity_data = pd.DataFrame({})

		self.target_image = ''
		self.target_image_path = ''

		self.similarity_index = 0
		
		
		# Define Language
		
		self.language = 'English'
		self.set_language(self.language)
		self.stage_instructions = ''
		
		
		# Define Variables - Boolean
		
		self.current_correction = False
		self.stimulus_on_screen = False
		self.limhold_started = False
		self.response_made = False
		self.hold_active = False
		self.stimulus_mask_on_screen = True
		
		# Define Variables - Count
		
		self.current_block = -1
		self.current_block_trial = 0

		self.current_hits = 0
		
		self.stage_index = -1
		self.trial_index = 0
		
		self.block_max_count = self.block_multiplier

		self.trial_outcome = 0  # 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Correct, no center tap,6-Incorrect, no center tap
		self.contingency = 0
		self.response = 0

		self.target_probability = 1.0

		self.block_target_total = 1
		self.block_nontarget_total = 1
		self.block_false_alarms = 0
		self.block_hits = 0
		
		
		# Define Variables - Staircasing
		
		self.last_response = 0
		
		self.response_tracking = [-2,-2]
		self.blur_tracking = list()
		self.noise_tracking = list()
		self.stimdur_frame_tracking = list()

		self.similarity_tracking = list()

		self.current_similarity = 0.0
		
		self.outcome_value = 0.0

		self.noise_mask_index_change = 2

		self.blur_level = 0
		self.blur_base = 0
		self.blur_change = 30
		
		
		# Define Variables - String
		
		self.center_image = self.mask_image
		self.left_image = self.mask_image
		self.right_image = self.mask_image

		self.current_substage = ''
		self.outcome_string = ''
		self.stage_string = ''
		
		
		# Define Variables - Time
		
		self.stimulus_start_time = 0.0
		self.response_latency = 0.0
		self.stimulus_press_latency = 0.0
		self.movement_latency = 0.0
		self.frame_duration = 1/self.maxfps
		self.stimdur_actual = 0.0

		self.staircase_stimdur_frame_max = staircase_stimdur_seconds_max/self.frame_duration
		
		iti_temp = [float(iNum) for iNum in iti_temp]
		self.iti_frame_range = (np.array(iti_temp) // self.frame_duration).tolist()
		self.iti_frame_range = [int(iNum) for iNum in self.iti_frame_range]
		self.iti_length = self.iti_frame_range[0] * self.frame_duration
		
		self.stimdur_import = [float(iNum) for iNum in self.stimdur_import]
		self.limhold_durations = [float(iNum) for iNum in self.limhold_import]

		stimdur_frame_steps = np.round(np.array(self.stimdur_import) / self.frame_duration, decimals=0)
		# limhold_frame_steps = np.round(np.array(self.limhold_import) / self.frame_duration)
		
		if 0 in stimdur_frame_steps:

			stimdur_frame_steps += 1
		

		if self.limhold_durations == 0:

			pass


		elif min(self.limhold_durations) < (max(stimdur_frame_steps) * self.frame_duration):

			sd_lh_diff = (max(stimdur_frame_steps) * self.frame_duration) - min(self.limhold_durations)
			self.limhold_durations = (np.array(self.limhold_durations) + sd_lh_diff).tolist()
		

		self.stimdur_frames = stimdur_frame_steps.tolist()
		# self.limhold_durations = limhold_frame_steps.tolist()

		self.stimdur_index = 0
		self.limhold_index = 0

		self.stimdur_current_frames = self.stimdur_frames[self.stimdur_index]
		# self.limhold_current_frames = self.limhold_frames[self.limhold_index]

		self.stimdur = self.stimdur_current_frames * self.frame_duration
		# self.limhold = self.limhold_durations[self.limhold_index]

		if self.staircase_stimdur_frame_min < 1:
			
			self.staircase_stimdur_frame_min = 1
		

		self.stimdur_base = self.stimdur_current_frames
		self.stimdur_change = self.stimdur_current_frames
		
		self.stimdur_use_steps = True
		

		# Define Clock
		
		self.task_clock = Clock
		self.task_clock.interupt_next_only = True

		self.tutorial_video_end_event = self.task_clock.create_trigger(self.present_tutorial_video_start_button, 0)
		self.tutorial_video_end_event.cancel()

		self.stimdur_event = self.task_clock.create_trigger(self.stimulus_presentation, 0, interval=True)
		self.stimdur_event.cancel()

		self.trial_contingency_event = self.task_clock.schedule_once(self.trial_contingency, 0)
		self.trial_contingency_event.cancel()

		self.stimulus_present_event = self.task_clock.schedule_once(self.stimulus_present, -1)
		self.stimulus_present_event.cancel()

		self.stimulus_end_event = self.task_clock.schedule_once(self.stimulus_end, 0)
		self.stimulus_end_event.cancel()

		self.blur_preload_start_event = self.task_clock.schedule_once(self.blur_preload_start, 0)
		self.blur_preload_start_event.cancel()

		self.blur_preload_end_event = self.task_clock.schedule_once(self.blur_preload_end, 0)
		self.blur_preload_end_event.cancel()


		self.block_check_clock = Clock
		self.block_check_clock.interupt_next_only = False

		self.block_check_event = self.block_check_clock.create_trigger(self.block_contingency, 0, interval=True)
		self.block_check_event.cancel()
		
		self.stage_screen_event = self.block_check_clock.create_trigger(self.stage_screen, 0, interval=True)
		self.stage_screen_event.cancel()
		
		
		# Define Variables

		self.target_prob_list = [int(float(iProb) * self.target_prob_trial_num) for iProb in target_prob_import]
		
		self.nontarget_prob_low = self.target_prob_trial_num - self.target_prob_low
		self.nontarget_prob_mid = self.target_prob_trial_num - self.target_prob_mid
		self.nontarget_prob_high = self.target_prob_trial_num - self.target_prob_high
		
		
		if 'Similarity' in self.stage_list:

			self.nontarget_prob_sim = self.target_prob_trial_num - self.target_prob_sim
		
		
		if 'Flanker' in self.stage_list:
			
			self.flanker_stage_list = ['none', 'same', 'diff', 'none', 'same', 'diff']
			random.shuffle(self.flanker_stage_list)
			
			self.flanker_stage_index = 0
			
			self.current_substage = ''
			self.flanker_image = ''
		
		
		if 'SART' in self.stage_list:
			
			self.target_prob_SART = self.nontarget_prob_high
			self.nontarget_prob_SART = self.target_prob_high
		
		
		# Define Widgets - Images

		self.image_folder = pathlib.Path('Protocol', self.protocol_name, 'Image')

		self.hold_image_path = str(self.image_folder / str(self.hold_image + '.png'))
		self.mask_image_path = str(self.image_folder / str(self.mask_image + '.png'))
		
# 		self.img_stimulus_C_image_path = self.image_folder + self.training_image_center + '.png'
		self.img_stimulus_C = ImageButton()
		# self.img_stimulus_C.bind(on_press=self.center_pressed)
		
		# self.img_stimulus_L_image_path = self.image_folder + 'black.png'
		self.img_stimulus_L = ImageButton(source=self.mask_image_path)
		
		# self.img_stimulus_R_image_path = self.image_folder + 'black.png'
		self.img_stimulus_R = ImageButton(source=self.mask_image_path)

		# self.center_instr_image_path = self.image_folder + 'black.png'
		self.center_instr_image = ImageButton(source=self.mask_image_path)
		
		# self.left_instr_image_path = self.image_folder + 'black.png'
		self.left_instr_image = ImageButton(source=self.mask_image_path)
		
		# self.right_instr_image_path = self.image_folder + 'black.png'
		self.right_instr_image = ImageButton(source=self.mask_image_path)

		self.img_noise_C = ImageButton()

		self.img_outline_C = ImageButton()
		
		
		# Define Instruction Components


		# Instruction - Dictionary
		
		self.instruction_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'Instructions.ini'))
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Training'] = {}
		self.instruction_dict['Similarity'] = {}
		self.instruction_dict['Noise_Scaling'] = {}
		self.instruction_dict['Blur_Scaling'] = {}
		self.instruction_dict['Speed_Scaling'] = {}
		self.instruction_dict['Noise'] = {}
		self.instruction_dict['Blur'] = {}
		self.instruction_dict['Speed'] = {}
		self.instruction_dict['LowProb'] = {}
		self.instruction_dict['MidProb'] = {}
		self.instruction_dict['HighProb'] = {}
		self.instruction_dict['TarProb'] = {}
		self.instruction_dict['Flanker'] = {}
		self.instruction_dict['SART'] = {}
		
		
		instruction_temp_train_str = self.instruction_config['Training']['train']
		instruction_temp_probe_str = self.instruction_config['Training']['task']
		
		self.instruction_dict['Training']['train'] = instruction_temp_train_str
		self.instruction_dict['Training']['task'] = instruction_temp_train_str
		
		
		instruction_temp_train_str = self.instruction_config['Similarity']['train']
		instruction_temp_probe_str = self.instruction_config['Similarity']['task']
		
		self.instruction_dict['Similarity']['train'] = instruction_temp_train_str
		self.instruction_dict['Similarity']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Noise_Scaling']['train']
		instruction_temp_probe_str = self.instruction_config['Noise_Scaling']['task']
		
		self.instruction_dict['Noise_Scaling']['train'] = instruction_temp_train_str
		self.instruction_dict['Noise_Scaling']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Blur_Scaling']['train']
		instruction_temp_probe_str = self.instruction_config['Blur_Scaling']['task']
		
		self.instruction_dict['Blur_Scaling']['train'] = instruction_temp_train_str
		self.instruction_dict['Blur_Scaling']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Speed_Scaling']['train']
		instruction_temp_probe_str = self.instruction_config['Speed_Scaling']['task']
		
		self.instruction_dict['Speed_Scaling']['train'] = instruction_temp_train_str
		self.instruction_dict['Speed_Scaling']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Noise']['train']
		instruction_temp_probe_str = self.instruction_config['Noise']['task']
		
		self.instruction_dict['Noise']['train'] = instruction_temp_train_str
		self.instruction_dict['Noise']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Blur']['train']
		instruction_temp_probe_str = self.instruction_config['Blur']['task']
		
		self.instruction_dict['Blur']['train'] = instruction_temp_train_str
		self.instruction_dict['Blur']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Speed']['train']
		instruction_temp_probe_str = self.instruction_config['Speed']['task']
		
		self.instruction_dict['Speed']['train'] = instruction_temp_train_str
		self.instruction_dict['Speed']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Main']['train']
		instruction_temp_probe_str = self.instruction_config['Main']['task']
		
		self.instruction_dict['LowProb']['train'] = instruction_temp_train_str
		self.instruction_dict['LowProb']['task'] = instruction_temp_probe_str
		
		self.instruction_dict['MidProb']['train'] = instruction_temp_train_str
		self.instruction_dict['MidProb']['task'] = instruction_temp_probe_str
		
		self.instruction_dict['HighProb']['train'] = instruction_temp_train_str
		self.instruction_dict['HighProb']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['TarProb']['train']
		instruction_temp_probe_str = self.instruction_config['TarProb']['task']
		
		self.instruction_dict['TarProb']['train'] = instruction_temp_train_str
		self.instruction_dict['TarProb']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Flanker']['train']
		instruction_temp_probe_str = self.instruction_config['Flanker']['task']
		
		self.instruction_dict['Flanker']['train'] = instruction_temp_train_str
		self.instruction_dict['Flanker']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['SART']['train']
		instruction_temp_probe_str = self.instruction_config['SART']['task']
		
		self.instruction_dict['SART']['train'] = instruction_temp_train_str
		self.instruction_dict['SART']['task'] = instruction_temp_probe_str
	
		
		lang_folder_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language))
		feedback_lang_path = str(pathlib.Path(lang_folder_path, 'Feedback.ini'))
		feedback_lang_config = configparser.ConfigParser(allow_no_value=True)
		feedback_lang_config.read(feedback_lang_path, encoding="utf-8")

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
		
		
		# Instruction - Text Widget
		
		self.section_instr_string = ''
		
		
		# Instruction - Button Widget
		
		self.instruction_button = Button()
		self.instruction_button.bind(on_press=self.section_start)
		self.instruction_button_str = ''
		
		
		# Stage Results - Button Widget
		
		self.stage_continue_button = Button()
		self.stage_continue_button.bind(on_press=self.block_contingency)
		
		self.session_end_button = Button()
		self.session_end_button.bind(on_press=self.protocol_end)
	
	
	
	def load_parameters(self, parameter_dict):
		
		# Import parameters from config file
		
		self.parameters_dict = parameter_dict
		
		config_path = str(pathlib.Path('Protocol', self.protocol_name, 'Configuration.ini'))
		config_file = configparser.ConfigParser()
		config_file.read(config_path)
		
		
		self.participant_id = self.parameters_dict['participant_id']
		self.age_range = self.parameters_dict['age_range']
		
		self.language = self.parameters_dict['language']

		self.skip_tutorial_video = int(self.parameters_dict['skip_tutorial_video'])

		self.block_change_on_duration = int(self.parameters_dict['block_change_on_duration_only'])
		
		self.iti_fixed_or_range = self.parameters_dict['iti_fixed_or_range']
		
		
		iti_temp = self.parameters_dict['iti_length']
		iti_temp = iti_temp.split(',')
		
		self.stimdur_import = self.parameters_dict['stimulus_duration']
		self.stimdur_import = self.stimdur_import.split(',')
		
		self.limhold_import = self.parameters_dict['limited_hold']
		self.limhold_import = self.limhold_import.split(',')
		
		self.feedback_length = float(self.parameters_dict['feedback_length'])
		self.block_duration_staircase = int(self.parameters_dict['block_duration-staircase'])
		self.block_duration_probe = int(self.parameters_dict['block_duration-probe'])
		self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
		self.session_duration = float(self.parameters_dict['session_duration'])
		
		self.block_multiplier = int(self.parameters_dict['block_multiplier'])
		self.block_trial_max = int(self.parameters_dict['block_trial_max'])
		self.training_block_max_correct = int(self.parameters_dict['training_block_max_correct'])
		self.correction_trials_active = int(self.parameters_dict['correction_trials_active'])

		self.target_prob_trial_num = int(self.parameters_dict['target_prob_over_num_trials'])
		
		target_prob_import = self.parameters_dict['target_prob_list']
		target_prob_import = target_prob_import.split(',')
			
		self.target_prob_low = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_low']))
		self.target_prob_mid = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_mid']))
		self.target_prob_high = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_high']))
		self.target_prob_sim = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_similarity']))
		self.target_prob_flanker = round(self.target_prob_trial_num * float(self.parameters_dict['target_prob_flanker']))
		
		# self.stimulus_family = self.parameters_dict['stimulus_family']

		self.display_stimulus_outline = int(self.parameters_dict['display_stimulus_outline'])
		self.mask_during_limhold = int(self.parameters_dict['mask_during_limhold'])
		self.limhold_mask_type = self.parameters_dict['limhold_mask_type']

		self.similarity_percentile_initial = float(self.parameters_dict['similarity_percentile_initial'])
		self.similarity_percentile_range = float(self.parameters_dict['similarity_percentile_range'])

		self.staircase_stimdur_frame_min = float(self.parameters_dict['staircase_stimdur_min_frames'])
		staircase_stimdur_seconds_max = float(self.parameters_dict['staircase_stimdur_max_seconds'])

		# self.staircase_limhold_change = float(self.parameters_dict['staircase_limhold_change'])
		# self.staircase_limhold_min = float(self.parameters_dict['staircase_limhold_min'])
		
		# self.target_image = str(self.parameters_dict['alternate_target_images_list'])
		# self.nontarget_images = str(self.parameters_dict['alternate_nontarget_images_list'])
		
		self.hold_image = config_file['Hold']['hold_image']
		self.mask_image = config_file['Mask']['mask_image']
		
		
		# Create stage list and import stage parameters
		
		self.stage_list = list()
		
		if int(self.parameters_dict['training_task']) == 1:
			
			self.stage_list.append('Training')
		
		
		if int(self.parameters_dict['speed_scaling']) == 1:
			
			self.stage_list.append('Speed_Scaling')
		

		if int(self.parameters_dict['similarity_scaling']) == 1:
			
			self.stage_list.append('Similarity')
			self.stimulus_family = 'Fb'
		
		else:
			
			self.stimulus_family = self.parameters_dict['stimulus_family']
		

		if int(self.parameters_dict['noise_scaling']) == 1 \
			and 'Similarity' not in self.stage_list:
			
			self.stage_list.append('Noise_Scaling')
		

		if int(self.parameters_dict['blur_scaling']) == 1 \
			and 'Similarity' not in self.stage_list:
			
			self.stage_list.append('Blur_Scaling')
		
		
		if int(self.parameters_dict['noise_probe']) == 1:
			
			self.stage_list.append('Noise')
		
		
		if int(self.parameters_dict['blur_probe']) == 1:
			
			self.stage_list.append('Blur')
		
		
		if int(self.parameters_dict['speed_probe']) == 1:
			
			self.stage_list.append('Speed')
		
		
		if int(self.parameters_dict['flanker_probe']) == 1:
			
			self.stage_list.append('Flanker')
		
		
		if int(self.parameters_dict['tarprob_probe']) == 1:
			
			self.stage_list.append('TarProb')
		
		
		if int(self.parameters_dict['midprob_probe']) == 1:
			
			self.stage_list.append('MidProb')
		
		
		if int(self.parameters_dict['lowprob_probe']) == 1:
			
			self.stage_list.append('LowProb')
		
		
		if int(self.parameters_dict['highprob_probe']) == 1:
			
			self.stage_list.append('HighProb')
		
		
		if int(self.parameters_dict['sart_probe']) == 1:
			
			self.stage_list.append('SART')

		
		# Convert parameters to useable types
		
		
		# General properties		
		
		self.trial_list = list()
		self.trial_list_low = list()
		self.trial_list_mid = list()
		self.trial_list_high = list()


		self.target_prob_list = [int(float(iProb) * self.target_prob_trial_num) for iProb in target_prob_import]
		random.shuffle(self.target_prob_list)
		
		
		self.nontarget_prob_low = self.target_prob_trial_num - self.target_prob_low
		self.nontarget_prob_mid = self.target_prob_trial_num - self.target_prob_mid
		self.nontarget_prob_high = self.target_prob_trial_num - self.target_prob_high
		
		
		for iTrial in range(self.target_prob_low):
			self.trial_list_low.append('Target')
		
		for iTrial in range(self.nontarget_prob_low):
			self.trial_list_low.append('Nontarget')
		
		
		for iTrial in range(self.target_prob_mid):
			self.trial_list_mid.append('Target')
		
		for iTrial in range(self.nontarget_prob_mid):
			self.trial_list_mid.append('Nontarget')
		
		
		for iTrial in range(self.target_prob_high):
			self.trial_list_high.append('Target')
		
		for iTrial in range(self.nontarget_prob_high):
			self.trial_list_high.append('Nontarget')
		
		
		random.shuffle(self.trial_list_low)
		random.shuffle(self.trial_list_mid)
		random.shuffle(self.trial_list_high)
		
		
		self.trial_list = self.trial_list_mid
		print('Trial list mid prob: ', self.trial_list)
		
		
		if 'Similarity' in self.stage_list:

			self.trial_list_sim = list()

			self.nontarget_prob_sim = self.target_prob_trial_num - self.target_prob_sim
		
			for iTrial in range(self.target_prob_sim):
				self.trial_list_sim.append('Target')
			
			for iTrial in range(self.nontarget_prob_sim):
				self.trial_list_sim.append('Nontarget')
			
			random.shuffle(self.trial_list_sim)
		
		
		if 'SART' in self.stage_list:
			
			self.trial_list_SART = list()
			
			self.nontarget_prob_SART = self.target_prob_high
			self.target_prob_SART = self.nontarget_prob_high
		
			for iTrial in range(self.target_prob_SART):
				self.trial_list_SART.append('Target')
			
			for iTrial in range(self.nontarget_prob_SART):
				self.trial_list_SART.append('Nontarget')
			
			random.shuffle(self.trial_list_SART)
		
		
		if 'Flanker' in self.stage_list:

			self.trial_list_flanker = list()

			self.nontarget_prob_flanker = self.target_prob_trial_num - self.target_prob_flanker
		
			for iTrial in range(self.target_prob_flanker):
				self.trial_list_flanker.append('Target')
			
			for iTrial in range(self.nontarget_prob_flanker):
				self.trial_list_flanker.append('Nontarget')
			
			random.shuffle(self.trial_list_flanker)
			
			self.flanker_stage_list = ['none', 'same', 'diff', 'none', 'same', 'diff']
			random.shuffle(self.flanker_stage_list)
			
			self.flanker_stage_index = 0
			
			self.current_substage = ''
			self.flanker_image = ''
		
		
		# Set images

		self.fribble_folder = pathlib.Path('Fribbles', self.stimulus_family)

		self.stimulus_image_path_list = list(pathlib.Path(self.image_folder).glob(str(self.fribble_folder / '*.png')))


		if 'Similarity' in self.stage_list:

			self.similarity_data = pd.read_csv(str(self.image_folder / self.fribble_folder / str(self.stimulus_family + '-SSIM_Data.csv')))
			# self.similarity_data.rename(columns={'NA': 'Nontarget'}, inplace=True)

			stimulus_list = list(self.similarity_data.columns)
			stimulus_list.remove('Nontarget')
			print('\n\nStimulus list: ', stimulus_list, '\n\n')

			self.target_image = random.choice(stimulus_list)
			
			print('Target image: ', self.target_image)

			self.similarity_data = self.similarity_data.loc[:, ['Nontarget', self.target_image]]

			self.similarity_data = self.similarity_data.drop(
				self.similarity_data[
					self.similarity_data['Nontarget'] == self.target_image
					].index
				)
			

			self.similarity_data = self.similarity_data.sort_values(by=self.target_image, ascending=True)

			self.nontarget_images = self.similarity_data['Nontarget'].tolist()

			# print(self.similarity_data)

			self.similarity_index_range = int(len(self.nontarget_images) * (self.similarity_percentile_range/100))

			# self.similarity_index_change = self.similarity_index_range

			if (self.similarity_percentile_initial - self.similarity_percentile_range/2) < 0:

				self.similarity_index_min = 0
				self.similarity_index_max = self.similarity_index_range


			elif (self.similarity_percentile_initial + self.similarity_percentile_range/2) > 100:

				self.similarity_index_max = len(self.nontarget_images) - 1
				self.similarity_index_min = self.similarity_index_max - self.similarity_index_range
			
			else:

				self.similarity_index_min = (int(len(self.nontarget_images) * (self.similarity_percentile_initial/100))) \
					- (self.similarity_index_range//2)
				
				self.similarity_index_max = (int(len(self.nontarget_images) * (self.similarity_percentile_initial/100))) \
					+ (self.similarity_index_range//2)
			
			
			self.current_nontarget_image_list = self.nontarget_images[self.similarity_index_min:self.similarity_index_max]

			print(self.current_nontarget_image_list)

			# self.current_nontarget_image_list = self.similarity_data.loc[
			# 	self.similarity_index_min:self.similarity_index_max
			# 	, 'Nontarget'
			# 	].tolist()

			# while len(self.current_nontarget_image_list) == 0:

			# 	self.similarity_limit += self.similarity_change

			# 	self.current_nontarget_image_list = self.similarity_data.loc[
			# 		(self.similarity_data[self.target_image] >= self.similarity_min) \
			# 		& (self.similarity_data[self.target_image] <= self.similarity_limit)
			# 		, 'Nontarget'
			# 		].tolist()
			

			# self.current_nontarget = random.choice(self.current_nontarget_image_list)
			# self.current_similarity = float(self.similarity_data.loc[
			# 		self.similarity_data['Nontarget'] == self.current_nontarget
			# 		, self.target_image
			# 		].to_numpy())

			self.current_similarity = 1.00


		else:
			
			stimulus_image_list = list()

			for filename in self.stimulus_image_path_list:
				stimulus_image_list.append(filename.stem)


			print('\n\nStimulus image list: ', stimulus_image_list, '\n\n')
			

			self.target_image = random.choice(stimulus_image_list)
			self.nontarget_images = list()

			stimulus_image_list.remove(self.target_image)

			subfamily_string = self.target_image[:3]

			while len(stimulus_image_list) > 0:

				iElem = 0

				while iElem < len(stimulus_image_list):

					if stimulus_image_list[iElem].startswith(subfamily_string):
						
						stimulus_image_list.pop(iElem)
					

					else:

						iElem += 1


				if len(stimulus_image_list) > 0:

					nontarget_image = random.choice(stimulus_image_list)

					self.nontarget_images.append(nontarget_image)

					subfamily_string = nontarget_image[:3]

				# [stimulus_image_list.remove(iStim) for iStim in stimulus_image_list if iStim.startswith(subfamily_string)]

				# stimulus_image_list.pop(stimulus_image_list[startswith(subfamily_string)])
			

			self.nontarget_images.sort()

			self.current_nontarget_image_list = self.nontarget_images
		
		print('Target image: ', self.target_image)
		print('Nontarget image list: ', self.nontarget_images)
		print('Current nontarget image list: ', self.current_nontarget_image_list)


		total_image_list = self.stimulus_image_path_list


		








		# Staircasing - Noise Masks

		# self.noise_mask_paths = pathlib.Path('Protocol', self.protocol_name, 'Image', 'Noise_Masks-Circle')
		self.noise_mask_value = '0'

		self.noise_mask_index = 0

		self.noise_mask_paths = list(pathlib.Path(self.image_folder).glob('Noise_Masks-Circle/*.png'))
		self.noise_mask_list = list()

		for filename in self.noise_mask_paths:
			self.noise_mask_list.append(filename.stem)

		self.noise_mask_value = self.noise_mask_list[self.noise_mask_index]

		print(self.noise_mask_paths)
		print(self.noise_mask_list)

		total_image_list += self.noise_mask_paths
			

		
		# Load images

		self.hold_image_path = str(pathlib.Path(self.image_folder, self.hold_image + '.png'))
		self.mask_image_path = str(pathlib.Path(self.image_folder, self.mask_image + '.png'))
		self.outline_mask_path = str(self.image_folder / 'whitecircle.png')

		total_image_list += [self.hold_image_path, self.mask_image_path]
		print('\n\nTotal image list: ', total_image_list, '\n\n')
		
		# loader_images = total_image_list
		# print(loader_images)
		#threading.Thread(target=self.load_images, args=(loader_images,)).start()
		self.load_images(total_image_list)
		
		
		# Define Language
		
		self.set_language(self.language)
		self.stage_instructions = ''
		
		
		# Define Variables - Boolean
		
		self.current_correction = False
		self.stage_screen_started = False
		self.limhold_started = False
		self.response_made = False
		self.hold_active = False
		self.stimulus_mask_on_screen = False
		
		
		# Define Variables - Count
		
		self.current_block = -1
		self.current_block_trial = 0
# 		self.current_trial = 0
		self.current_hits = 0
		# self.block_trial_max = 1
		self.block_max_count = self.block_multiplier
		self.trial_outcome = 0  # 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Correct, no center touch,6-Incorrect, no center touch
		self.contingency = 0
		self.response = 0
		self.stage_index = -1
		self.trial_index = 0

		self.target_probability = 1.0

		self.block_target_total = 1
		self.block_nontarget_total = 1
		self.block_false_alarms = 0
		self.block_hits = 0
		
		
		# Define Variables - Staircasing
		
		self.last_response = 0
		
		self.response_tracking = [-2,-2]
		self.blur_tracking = list()
		self.noise_tracking = list()
		self.stimdur_frame_tracking = list()

		self.similarity_tracking = list()

		self.current_similarity = 0.0
		
		self.outcome_value = 0.0

		self.noise_mask_index_change = 2

		image_texture_for_size = Image(source=str(self.stimulus_image_path_list[0]))
		self.image_texture_size = image_texture_for_size.texture_size

		print(self.image_texture_size)

		self.blur_level = 0
		self.blur_base = 0
		self.blur_change = 30
		
		# self.blur_horz = int(self.blur_level * self.image_texture_size[0])
		# self.blur_vert = int(self.blur_level * self.image_texture_size[1])

		# print(self.blur_horz)
		# print(self.blur_vert)
		
		
		# Define Variables - String
		
		self.center_image = self.mask_image
		self.left_image = self.mask_image
		self.right_image = self.mask_image
		
		self.current_stage = ''
		self.current_substage = ''
		self.outcome_string = ''
		self.stage_string = ''
		
		
		# Define Variables - Time
		
		self.stimulus_start_time = 0.0
		self.response_latency = 0.0
		self.stimulus_press_latency = 0.0
		self.movement_latency = 0.0
		self.frame_duration = 1/self.maxfps
		self.stimdur_actual = 0.0

		self.staircase_stimdur_frame_max = staircase_stimdur_seconds_max/self.frame_duration
		
		iti_temp = [float(iNum) for iNum in iti_temp]
		self.iti_frame_range = (np.array(iti_temp) // self.frame_duration).tolist()
		self.iti_frame_range = [int(iNum) for iNum in self.iti_frame_range]
		self.iti_length = self.iti_frame_range[0] * self.frame_duration
		
		self.stimdur_import = [float(iNum) for iNum in self.stimdur_import]
		self.limhold_durations = [float(iNum) for iNum in self.limhold_import]

		stimdur_frame_steps = np.round(np.array(self.stimdur_import) / self.frame_duration)
		# limhold_frame_steps = np.round(np.array(self.limhold_import) / self.frame_duration)
		
		if 0 in stimdur_frame_steps:

			stimdur_frame_steps += 1


		if self.limhold_durations == 0:

			pass
		

		elif min(self.limhold_durations) < (max(stimdur_frame_steps) * self.frame_duration):

			sd_lh_diff = (max(stimdur_frame_steps) * self.frame_duration) - min(self.limhold_durations)
			self.limhold_durations = (np.array(self.limhold_durations) + sd_lh_diff).tolist()
		

		self.stimdur_frames = stimdur_frame_steps.tolist()
		# self.limhold_durations = limhold_frame_steps.tolist()

		self.stimdur_index = 0
		self.limhold_index = 0

		self.stimdur_current_frames = self.stimdur_frames[self.stimdur_index]
		# self.limhold_current_frames = self.limhold_frames[self.limhold_index]

		self.stimdur = self.stimdur_current_frames * self.frame_duration
		# self.limhold = self.limhold_durations[self.limhold_index]

		if self.staircase_stimdur_frame_min < 1:
			
			self.staircase_stimdur_frame_min = 1
		

		self.stimdur_base = self.stimdur_current_frames
		self.stimdur_change = self.stimdur_current_frames//2
		
		self.stimdur_use_steps = True

		self.limhold = self.stimdur
		self.limhold_base = self.limhold
		
		
		# Define Session Event
		
		self.session_event = self.session_clock.create_trigger(self.clock_monitor, self.session_duration, interval=False)


		# Define GUI Sizes and Pos

		self.hold_button_proportion = 0.2
		self.stimulus_image_proportion = 0.35
		self.instruction_image_proportion = 0.25

		self.hold_button_size = ((self.hold_button_proportion * self.width_adjust), (self.hold_button_proportion * self.height_adjust))

		self.stimulus_image_size = ((self.stimulus_image_proportion * self.width_adjust), (self.stimulus_image_proportion * self.height_adjust))
		self.instruction_image_size = ((self.instruction_image_proportion * self.width_adjust), (self.instruction_image_proportion * self.height_adjust))

		self.stimulus_mask_size = (self.stimulus_image_size[0] * 1.2, self.stimulus_image_size[1] * 1.2)

		self.text_button_size = [0.4, 0.15]
		

		self.hold_button_pos = {"center_x": 0.5, "center_y": 0.1}

		self.stimulus_pos_C = {"center_x": 0.50, "center_y": 0.6}
		self.stimulus_pos_L = {"center_x": 0.20, "center_y": 0.6}
		self.stimulus_pos_R = {"center_x": 0.80, "center_y": 0.6}

		self.instruction_image_pos_C = {"center_x": 0.50, "center_y": 0.9}
		self.instruction_image_pos_L = {"center_x": 0.25, "center_y": 0.9}
		self.instruction_image_pos_R = {"center_x": 0.75, "center_y": 0.9}

		self.text_button_pos_UL = {"center_x": 0.25, "center_y": 0.92}
		self.text_button_pos_UC = {"center_x": 0.50, "center_y": 0.92}
		self.text_button_pos_UR = {"center_x": 0.75, "center_y": 0.92}

		self.text_button_pos_LL = {"center_x": 0.25, "center_y": 0.08}
		self.text_button_pos_LC = {"center_x": 0.50, "center_y": 0.08}
		self.text_button_pos_LR = {"center_x": 0.75, "center_y": 0.08}
		
		
		# Define Widgets - Images
		
		# self.hold_button_image_path = str(self.image_folder / self.hold_image) + '.png'
		self.hold_button.source = self.hold_image_path
		self.hold_button.size_hint = self.hold_button_size
		self.hold_button.bind(on_press=self.iti)
		self.hold_button.bind(on_release=self.premature_response)
		
		# self.img_stimulus_C_image_path = str(self.image_folder / self.fribble_folder/ self.target_image) + '.png'
		self.img_stimulus_C = ImageButton()
		self.img_stimulus_C.size_hint = self.stimulus_image_size
		self.img_stimulus_C.pos_hint = self.stimulus_pos_C
		self.img_stimulus_C.bind(on_press=self.center_pressed)
		self.img_stimulus_C.name = 'Center Stimulus'

		# self.mask_image_path = str(self.image_folder / 'black.png')
		
		# self.img_stimulus_L_image_path = self.image_folder + 'black.png'
		self.img_stimulus_L = ImageButton(source=self.mask_image_path)
		self.img_stimulus_L.size_hint = self.stimulus_image_size
		self.img_stimulus_L.pos_hint = self.stimulus_pos_L
		
		# self.img_stimulus_R_image_path = self.image_folder + 'black.png'
		self.img_stimulus_R = ImageButton(source=self.mask_image_path)
		self.img_stimulus_R.size_hint = self.stimulus_image_size
		self.img_stimulus_R.pos_hint = self.stimulus_pos_R

		# self.center_instr_image_path = self.image_folder + 'black.png'
		self.center_instr_image = ImageButton(source=self.mask_image_path)
		self.center_instr_image.size_hint = self.instruction_image_size
		self.center_instr_image.pos_hint = self.instruction_image_pos_C
		
		# self.left_instr_image_path = self.image_folder + 'black.png'
		self.left_instr_image = ImageButton(source=self.mask_image_path)
		self.left_instr_image.size_hint = self.instruction_image_size
		self.left_instr_image.pos_hint = self.instruction_image_pos_L
		
		# self.right_instr_image_path = self.image_folder + 'black.png'
		self.right_instr_image = ImageButton(source=self.mask_image_path)
		self.right_instr_image.size_hint = self.instruction_image_size
		self.right_instr_image.pos_hint = self.instruction_image_pos_R


		# self.img_noise_C_path = str(self.noise_mask_paths[0])
		self.img_noise_C = ImageButton(source=str(self.noise_mask_paths[0]))
		self.img_noise_C.size_hint = self.stimulus_mask_size
		self.img_noise_C.pos_hint = self.stimulus_pos_C
		self.img_noise_C.bind(on_press=self.center_pressed)
		self.img_noise_C.name = 'Center Noise Mask'

		self.img_noise_L = ImageButton(source=str(self.noise_mask_paths[0]))
		self.img_noise_L.size_hint = self.stimulus_mask_size
		self.img_noise_L.pos_hint = self.stimulus_pos_L
		self.img_noise_L.name = 'Left Noise Mask'

		self.img_noise_R = ImageButton(source=str(self.noise_mask_paths[0]))
		self.img_noise_R.size_hint = self.stimulus_mask_size
		self.img_noise_R.pos_hint = self.stimulus_pos_R
		self.img_noise_R.name = 'Right Noise Mask'


		# self.img_outline_C_path = str(self.image_folder / 'whitecircle.png')
		self.img_outline_C = ImageButton(source=self.outline_mask_path)
		self.img_outline_C.size_hint = self.stimulus_mask_size
		self.img_outline_C.pos_hint = self.stimulus_pos_C
		self.img_outline_C.bind(on_press=self.center_pressed)
		self.img_outline_C.name = 'Center Outline Mask'

		self.img_outline_L = ImageButton(source=self.outline_mask_path)
		self.img_outline_L.size_hint = self.stimulus_mask_size
		self.img_outline_L.pos_hint = self.stimulus_pos_L
		self.img_outline_L.name = 'Left Outline Mask'

		self.img_outline_R = ImageButton(source=self.outline_mask_path)
		self.img_outline_R.size_hint = self.stimulus_mask_size
		self.img_outline_R.pos_hint = self.stimulus_pos_R
		self.img_outline_R.name = 'Right Outline Mask'


		if self.mask_during_limhold == 1:

			if self.limhold_mask_type == 'noise':

				self.stimulus_mask_path = str(self.noise_mask_paths[-1])

			self.img_stimulus_C_mask = ImageButton(source=self.stimulus_mask_path)
			self.img_stimulus_C_mask.size_hint = self.stimulus_mask_size
			self.img_stimulus_C_mask.pos_hint = self.stimulus_pos_C
			self.img_stimulus_C_mask.bind(on_press=self.center_pressed)
			self.img_stimulus_C_mask.name = 'Center Stimulus Mask'


		# Tutorial Video Import

		self.tutorial_video_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'CPT_Tutorial_Video.mp4'))
		# self.tutorial_video_path = str(pathlib.Path.home() / 'Touchcog' / 'Videos' / self.distractor_video)

		self.tutorial_video = Video(
			source = self.tutorial_video_path
			# , allow_stretch = True
			# , options = {'eos': 'stop'}
			, state = 'stop'
			)

		self.tutorial_video.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

		# self.tutorial_video.allow_stretch = True
		self.tutorial_video.size_hint = (1, 1)

		# self.protocol_floatlayout.add_widget(self.tutorial_video)
		# self.tutorial_video.state = 'pause'
		# self.protocol_floatlayout.remove_widget(self.tutorial_video)


		if any(True for stage in ['Blur_Scaling', 'Blur'] if stage in self.stage_list):

			self.blur_widget = EffectWidget()
			self.blur_widget.effects = [HorizontalBlurEffect(size=self.blur_level), VerticalBlurEffect(size=self.blur_level)]
			# self.blur_widget.add_widget(self.img_stimulus_C)
		 


		
		
		# Define Instruction Components
		
# 		self.display_instructions = True
		
		# Instruction - Dictionary
		
		self.instruction_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language, 'Instructions.ini'))
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Training'] = {}
		self.instruction_dict['Noise_Scaling'] = {}
		self.instruction_dict['Blur_Scaling'] = {}
		self.instruction_dict['Speed_Scaling'] = {}
		self.instruction_dict['Noise'] = {}
		self.instruction_dict['Blur'] = {}
		self.instruction_dict['Speed'] = {}
		self.instruction_dict['Similarity'] = {}
		self.instruction_dict['LowProb'] = {}
		self.instruction_dict['MidProb'] = {}
		self.instruction_dict['HighProb'] = {}
		self.instruction_dict['TarProb'] = {}
		self.instruction_dict['Flanker'] = {}
		self.instruction_dict['SART'] = {}
		
		
		instruction_temp_train_str = self.instruction_config['Training']['train']
		instruction_temp_probe_str = self.instruction_config['Training']['task']
		
		self.instruction_dict['Training']['train'] = instruction_temp_train_str
		self.instruction_dict['Training']['task'] = instruction_temp_train_str
		
		
		instruction_temp_train_str = self.instruction_config['Main']['train']
		instruction_temp_probe_str = self.instruction_config['Main']['task']
		
		self.instruction_dict['LowProb']['train'] = instruction_temp_train_str
		self.instruction_dict['LowProb']['task'] = instruction_temp_probe_str
		
		self.instruction_dict['MidProb']['train'] = instruction_temp_train_str
		self.instruction_dict['MidProb']['task'] = instruction_temp_probe_str
		
		self.instruction_dict['HighProb']['train'] = instruction_temp_train_str
		self.instruction_dict['HighProb']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['TarProb']['train']
		instruction_temp_probe_str = self.instruction_config['TarProb']['task']
		
		self.instruction_dict['TarProb']['train'] = instruction_temp_train_str
		self.instruction_dict['TarProb']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Noise_Scaling']['train']
		instruction_temp_probe_str = self.instruction_config['Noise_Scaling']['task']
		
		self.instruction_dict['Noise_Scaling']['train'] = instruction_temp_train_str
		self.instruction_dict['Noise_Scaling']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Blur_Scaling']['train']
		instruction_temp_probe_str = self.instruction_config['Blur_Scaling']['task']
		
		self.instruction_dict['Blur_Scaling']['train'] = instruction_temp_train_str
		self.instruction_dict['Blur_Scaling']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Speed_Scaling']['train']
		instruction_temp_probe_str = self.instruction_config['Speed_Scaling']['task']
		
		self.instruction_dict['Speed_Scaling']['train'] = instruction_temp_train_str
		self.instruction_dict['Speed_Scaling']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Noise']['train']
		instruction_temp_probe_str = self.instruction_config['Noise']['task']
		
		self.instruction_dict['Noise']['train'] = instruction_temp_train_str
		self.instruction_dict['Noise']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Blur']['train']
		instruction_temp_probe_str = self.instruction_config['Blur']['task']
		
		self.instruction_dict['Blur']['train'] = instruction_temp_train_str
		self.instruction_dict['Blur']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Speed']['train']
		instruction_temp_probe_str = self.instruction_config['Speed']['task']
		
		self.instruction_dict['Speed']['train'] = instruction_temp_train_str
		self.instruction_dict['Speed']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['Similarity']['train']
		instruction_temp_probe_str = self.instruction_config['Similarity']['task']
		
		self.instruction_dict['Similarity']['train'] = instruction_temp_train_str
		self.instruction_dict['Similarity']['task'] = instruction_temp_probe_str
				
		
		instruction_temp_train_str = self.instruction_config['Flanker']['train']
		instruction_temp_probe_str = self.instruction_config['Flanker']['task']
		
		self.instruction_dict['Flanker']['train'] = instruction_temp_train_str
		self.instruction_dict['Flanker']['task'] = instruction_temp_probe_str
		
		
		instruction_temp_train_str = self.instruction_config['SART']['train']
		instruction_temp_probe_str = self.instruction_config['SART']['task']
		
		self.instruction_dict['SART']['train'] = instruction_temp_train_str
		self.instruction_dict['SART']['task'] = instruction_temp_probe_str
	
		
		lang_folder_path = str(pathlib.Path('Protocol', self.protocol_name, 'Language', self.language))
		feedback_lang_path = str(pathlib.Path(lang_folder_path, 'Feedback.ini'))
		feedback_lang_config = configparser.ConfigParser(allow_no_value=True)
		feedback_lang_config.read(feedback_lang_path, encoding="utf-8")

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
		
		
		# Instruction - Text Widget
		
		self.section_instr_string = self.instruction_label.text
		self.section_instr_label = Label(text=self.section_instr_string, font_size='44sp', markup=True)
		self.section_instr_label.size_hint = {0.58, 0.7}
		self.section_instr_label.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
		
		# Instruction - Button Widget
		
		self.instruction_button = Button(font_size='60sp')
		self.instruction_button.size_hint = self.text_button_size
		self.instruction_button.pos_hint = self.text_button_pos_LC
		self.instruction_button.text = ''
		self.instruction_button.bind(on_press=self.section_start)
		self.instruction_button_str = ''
		
		
		# Stage Results - Text Widget
		
		self.stage_results_label = Label(text='', font_size='48sp', markup=True)
		self.stage_results_label.size_hint = (0.85, 0.8)
		self.stage_results_label.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
		
		
		# Stage Results - Button Widget
		
		self.stage_continue_button = Button(font_size='60sp')
		self.stage_continue_button.size_hint = self.text_button_size
		self.stage_continue_button.pos_hint = self.text_button_pos_LC
		self.stage_continue_button.text = 'CONTINUE'
		self.stage_continue_button.bind(on_press=self.block_check_event)
		
		self.session_end_button = Button(font_size='60sp')
		self.session_end_button.size_hint = self.text_button_size
		self.session_end_button.pos_hint = self.text_button_pos_LL
		self.session_end_button.text = 'END SESSION'
		self.session_end_button.bind(on_press=self.protocol_end)
		
		
		self.protocol_floatlayout.clear_widgets()
		
		
		# Begin Task
		
# 		self.start_protocol()
# 		self.present_instructions(self.section_instr_label, self.start_button)
		self.present_instructions()
		# self.present_tutorial_video()
		# self.start_protocol_direct()
	
	
	





















	# Protocol Staging
		
	def present_tutorial(self, *args):
		
		self.tutorial_hold = ImageButton(source=self.hold_image_path)
		self.tutorial_hold.size_hint = self.hold_button_size
		self.tutorial_hold.pos_hint = self.hold_button_pos
		
		self.tutorial_continue = Button(text='CONTINUE TUTORIAL', font_size='48sp')
		self.tutorial_continue.size_hint = self.text_button_size
		self.tutorial_continue.pos_hint = self.text_button_pos_LC
		self.tutorial_continue.bind(on_press=self.tutorial_intro_screen)

		self.is_target = True

		self.tutorial_stimulus_texture = self.target_image
		self.tutorial_stimulus = ImageButton(source=str(self.image_folder / self.fribble_folder / self.target_image) + '.png')
		# self.tutorial_stimulus.texture = self.image_dict[self.target_image].image.texture
		self.tutorial_stimulus.size_hint = self.stimulus_image_size
		self.tutorial_stimulus.pos_hint = self.stimulus_pos_C
		self.tutorial_stimulus.bind(on_press=self.tutorial_limhold_screen)
		
		self.tutorial_restart_button = Button(text='RESTART TUTORIAL', font_size='48sp')
		self.tutorial_restart_button.size_hint = self.text_button_size
		self.tutorial_restart_button.pos_hint = self.text_button_pos_UR
		self.tutorial_restart_button.bind(on_press=self.present_tutorial)
		
		
		self.tutorial_label_top = Label(font_size='35sp')
		self.tutorial_label_top.size_hint = (0.6, 0.8)
		self.tutorial_label_top.pos_hint = {'center_x': 0.5, 'center_y': 0.58}
		
		self.tutorial_label_bottom = Label(font_size='35sp')
		self.tutorial_label_bottom.size_hint = (0.6, 0.3)
		self.tutorial_label_bottom.pos_hint = {'center_x': 0.5, 'center_y': 0.4}
		
		self.tutorial_label_top.text = 'This is a test of attention.\n\nDuring the test, you will see a series of images.\nYour task is to respond to target images, like the one below.\n\n\n\n\n\n\n\n\n\nThe following screens will teach you how to perform this task.\n\nPress the "CONTINUE TUTORIAL" button below to continue.'
		# self.tutorial_label_bottom.text = 'Your task is to respond as quickly as possible whenever a target\nimage appears, and withhold response to all other images.\n\nThe following screens will teach you how to perform this task.\n\nPress the "CONTINUE TUTORIAL" button below to continue.'
		# self.tutorial_label.text = 'PRESS BELOW TO START TASK'

		self.protocol_floatlayout.clear_widgets()
		
		# self.protocol_floatlayout.add_widget(self.tutorial_label_top)
		# self.protocol_floatlayout.add_widget(self.tutorial_label_bottom)
		# self.protocol_floatlayout.add_widget(self.tutorial_stimulus)
		# self.protocol_floatlayout.add_widget(self.tutorial_continue)

		self.protocol_floatlayout.add_widget(self.tutorial_start_button)


		
	def present_tutorial_video(self, *args):

		self.tutorial_stimulus_image = ImageButton(source=str(self.image_folder / self.fribble_folder/ self.target_image) + '.png')
		self.tutorial_stimulus_image.size_hint = (0.6 * self.width_adjust, 0.6 * self.height_adjust)
		self.tutorial_stimulus_image.pos_hint = self.stimulus_pos_C
		
		self.tutorial_continue = Button(text='CONTINUE', font_size='48sp')
		self.tutorial_continue.size_hint = self.text_button_size
		self.tutorial_continue.pos_hint = self.text_button_pos_LC
		self.tutorial_continue.bind(on_press=self.tutorial_target_present_screen)
		
		self.tutorial_start_button = Button(text='START', font_size='48sp')
		self.tutorial_start_button.size_hint = self.text_button_size
		self.tutorial_start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.2} #self.text_button_pos_LC
		self.tutorial_start_button.bind(on_press=self.start_protocol_from_tutorial)

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_widget(self.tutorial_video)
		self.tutorial_video.state = 'play'

		if self.skip_tutorial_video == 1:
			
			self.tutorial_video_end_event = self.task_clock.schedule_once(self.tutorial_target_present_screen, 0)
		
		else:

			self.tutorial_video_end_event = self.task_clock.schedule_once(self.tutorial_target_present_screen, 74)
	


	def present_tutorial_video_start_button(self, *args):

		self.tutorial_video_end_event.cancel()

		self.tutorial_video.state = 'pause'

		self.protcol_floatlayout.add_widget(self.tutorial_continue)
	


	def tutorial_target_present_screen(self, *args):

		self.tutorial_video_end_event.cancel()

		self.tutorial_video.state = 'stop'

		self.protocol_floatlayout.remove_widget(self.tutorial_video)
		self.protocol_floatlayout.remove_widget(self.tutorial_continue)

		self.protocol_floatlayout.add_widget(self.tutorial_stimulus_image)
		self.protocol_floatlayout.add_widget(self.tutorial_start_button)


		# self.blur_widget.add_widget(self.tutorial_stimulus_image)
		# self.blur_widget.effects = [HorizontalBlurEffect(size=20), VerticalBlurEffect(size=20)]
		# self.protocol_floatlayout.add_widget(self.blur_widget)
	
	
	
	def start_protocol_from_tutorial(self, *args):
		
		self.protocol_floatlayout.remove_widget(self.tutorial_stimulus_image)
		# self.blur_widget.remove_widget(self.tutorial_stimulus_image)
		self.generate_output_files()
		self.metadata_output_generation()
		self.start_protocol()
	
	
	
	def start_protocol_direct(self, *args):

		self.generate_output_files()
		self.metadata_output_generation()
		self.start_protocol()























	
	def start_protocol(self, *args):
		
		self.protocol_floatlayout.clear_widgets()
		
		print('Stage list: ', self.stage_list)
		
		self.start_clock()
		
		self.block_contingency()
	


	def blur_preload_start(self, *args):

		self.blur_preload_start_event.cancel()

		self.img_stimulus_C.texture = self.image_dict[self.mask_image].image.texture

		self.protocol_floatlayout.add_widget(self.blur_widget)
		self.blur_widget.add_widget(self.img_stimulus_C)

		self.blur_preload_end_event()
	


	def blur_preload_end(self, *args):

		self.blur_preload_end_event.cancel()

		self.protocol_floatlayout.remove_widget(self.blur_widget)
		self.blur_widget.remove_widget(self.img_stimulus_C)

		self.trial_contingency_event()

		# return
	
	
	
	def stimulus_present(self, *args): # Present stimulus

		print('Present stimulus')

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur':

			self.blur_widget.add_widget(self.img_stimulus_C)
			self.protocol_floatlayout.add_widget(self.blur_widget)
		
		else:
			
			self.protocol_floatlayout.add_widget(self.img_stimulus_C)
		

		self.stimulus_start_time = time.time()
		
		self.stimulus_on_screen = True
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_start_time - self.start_time)
			, 'State Change'
			, 'Object Display'
			])
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_start_time - self.start_time)
			, 'Object Display'
			, 'Stimulus'
			, 'Center'
			, 'Center'
			, 'Image Name'
			, self.center_image
			])
		

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise':
			
			self.protocol_floatlayout.add_widget(self.img_noise_C)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Display'
				, 'Mask'
				, 'Noise'
				, 'Center'
				, 'Image Name'
				, self.noise_mask_value
				])
		

		if self.display_stimulus_outline == 1:
			
			self.protocol_floatlayout.add_widget(self.img_outline_C)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Mask'
				, 'Outline'
				, 'Center'
				, 'Image Name'
				, self.display_stimulus_outline
				])
		

		if self.current_stage == 'Flanker':
			
			self.protocol_floatlayout.add_widget(self.img_stimulus_L)
			self.protocol_floatlayout.add_widget(self.img_stimulus_R)

			# if self.display_stimulus_outline == 1:
				
			# 	self.protocol_floatlayout.add_widget(self.img_outline_L)
			# 	self.protocol_floatlayout.add_widget(self.img_outline_R)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Display'
				, 'Stimulus'
				, 'Flanker'
				, 'Left'
				, 'Image Name'
				, self.img_stimulus_L
				])
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Display'
				, 'Stimulus'
				, 'Flanker'
				, 'Right'
				, 'Image Name'
				, self.img_stimulus_R
				])
		

		self.stimdur_event()
	
	
	
	def stimulus_end(self, *args): # Present stimulus
		
		self.stimulus_present_event.cancel()

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur':

			self.protocol_floatlayout.remove_widget(self.blur_widget)
			self.blur_widget.remove_widget(self.img_stimulus_C)
		
		else:
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C)
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'State Change'
			, 'Object Remove'
			])

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise':

			self.protocol_floatlayout.remove_widget(self.img_noise_C)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Mask'
				, 'Noise'
				, 'Center'
				, 'Image Name'
				, self.noise_mask_value
				])
		

		if (self.mask_during_limhold == 1) \
			and (self.current_stage == 'Speed'):
			
			self.protocol_floatlayout.remove_widget(self.img_outline_C)

			self.protocol_floatlayout.add_widget(self.img_stimulus_C_mask)
			
			self.protocol_floatlayout.add_widget(self.img_outline_C)

			self.stimulus_mask_on_screen = True


		self.stimdur_actual = time.time() - self.stimulus_start_time
		
		self.stimulus_on_screen = False
		self.limhold_started = True

		if self.current_stage == 'Flanker':
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_L)
			self.protocol_floatlayout.remove_widget(self.img_stimulus_R)

			# if self.display_stimulus_outline == 1:
				
			# 	self.protocol_floatlayout.remove_widget(self.img_outline_L)
			# 	self.protocol_floatlayout.remove_widget(self.img_outline_R)
			
			# self.img_stimulus_L_image_path = str(self.image_folder / self.mask_image) + '.png'
			# self.img_stimulus_R_image_path = str(self.image_folder / self.mask_image) + '.png'
			# self.img_stimulus_L.texture = self.image_dict[self.mask_image].image.texture
			# self.img_stimulus_R.texture = self.image_dict[self.mask_image].image.texture
			
			# self.protocol_floatlayout.add_widget(self.img_stimulus_L)
			# self.protocol_floatlayout.add_widget(self.img_stimulus_R)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Stimulus'
				, 'Flanker'
				, 'Left'
				, 'Image Name'
				, self.img_stimulus_L
				])
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Stimulus'
				, 'Flanker'
				, 'Right'
				, 'Image Name'
				, self.img_stimulus_R
				])
		

		self.stimdur_event()
	
	
	
	def stimulus_presentation(self, *args): # Stimulus presentation by frame
		
		if not self.stimulus_on_screen \
			and not self.limhold_started:

			print('Stimulus not on screen')

			self.hold_active = True
		
			self.hold_button.unbind(on_press=self.iti)
			self.hold_button.unbind(on_release=self.premature_response)
			
			# self.hold_button.bind(on_press=self.hold_returned_stim)
			self.hold_button.bind(on_release=self.stimulus_response)
			
			self.stimulus_present_event() # = self.task_clock.schedule_once(self.stimulus_present, 0)
			# self.task_clock.create_trigger(self.stimulus_present)
			
#			self.stimdur_present_event()
			
			# return
		
		
		elif (time.time() - self.stimulus_start_time < self.stimdur):
			# and self.stimulus_on_screen:
			# and self.hold_active:

#			print('Stimdur event active')
			
			self.stimdur_event()
			
#			return
		
		
		elif ((time.time() - self.stimulus_start_time) < self.limhold) \
			and self.limhold_started:

			self.stimdur_event()
		
		
		elif ((time.time() - self.stimulus_start_time) >= self.stimdur) \
			and not self.limhold_started:
			
			# self.img_stimulus_C.texture = self.image_dict[self.mask_image].image.texture
			self.stimulus_end_event()
			# self.task_clock.schedule_once(self.stimulus_end, -1)
			# self.task_clock.create_trigger(self.stimulus_end)
#				self.stimdur_end_event()

			# if self.limhold <= self.stimdur:

			# 	self.center_notpressed()
		

		else:

			self.center_notpressed()
			
			
			# if (time.time() - self.stimulus_start_time) > self.limhold:

			# 	print('Stimulus end cancel and return')
				
			# 	self.center_notpressed()
	
				
	
	def premature_response(self, *args): # Trial Outcomes: 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Hit, no center touch,6-False Alarm, no center touch
		if self.stimulus_on_screen:
			return None
		
		if self.iti_active:
			self.iti_event.cancel()
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
			, self.contingency
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Response'
			, self.response
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Outcome'
			, self.trial_outcome
			])
		

		self.write_trial()

		self.iti_active = False
		
		if (self.current_block == 0) \
			or (self.current_stage == 'Training'):

			# self.feedback_string = self.feedback_dict['wait']
			self.feedback_label.text = self.feedback_dict['wait']
			
			if not self.feedback_on_screen:

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
				
		
		self.hold_button.unbind(on_release=self.premature_response)
		self.hold_button.bind(on_press=self.iti)
	
	
	
	# Contingency Stages #
	
	def stimulus_response(self, *args): # Trial Outcomes: 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Hit, no center press,6-False Alarm, no center press
										# Contingencies: 0: Incorrect; 1: Correct; 2: Response, no center touch; 3: Premature response
		
		self.response_time = time.time()
		self.response_latency = self.response_time - self.stimulus_start_time
		
		self.response_made = True
		self.hold_active = False

		self.protocol_floatlayout.add_event([
			(self.response_time - self.start_time)
			, 'State Change'
			, 'Stimulus Response'
			])
		
		self.response = 1

		self.feedback_label.text = ''
		
		if (self.current_stage == 'SART'):
			if (self.center_image in self.current_nontarget_image_list):
				self.contingency = 2
				self.trial_outcome = 5
				
				# if self.current_block == 0:
				# 	self.feedback_label.text = self.feedback_dict['correct']
					
			else:
				self.contingency = 2
				self.trial_outcome = 6
				
				# if self.current_block == 0:
				# 	self.feedback_label.text = self.feedback_dict['incorrect']
		
		else:
			if (self.center_image == self.target_image):
				#self.feedback_string = self.feedback_dict['correct']
				self.contingency = 2
				self.trial_outcome = 5
				# self.current_hits += 1

				if self.current_stage == 'Speed_Scaling':
					self.feedback_label.text = self.feedback_dict['too_slow']
				
				# self.feedback_label.text = self.feedback_dict['correct']
				
			else:
				self.contingency = 2
				self.trial_outcome = 6
				
				# self.feedback_label.text = self.feedback_dict['incorrect']
		
		self.protocol_floatlayout.add_event([
			(self.response_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Response'
			, str(self.response)
			])
				
		self.protocol_floatlayout.add_event([
			(self.response_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Contingency'
			, str(self.contingency)
			])
		
		self.protocol_floatlayout.add_event([
			(self.response_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Outcome'
			, str(self.trial_outcome)
			])
		
		self.protocol_floatlayout.add_event([
			(self.response_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Response Latency'
			, str(self.response_latency)
			])
		
		# self.write_trial()
		
		self.hold_button.bind(on_press=self.response_cancelled)
		self.hold_button.unbind(on_release=self.stimulus_response)
	
	
	
	def center_pressed(self, *args): # Trial Outcomes: 1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Premature,6-Dual Image, wrong side
		
		self.stimulus_present_event.cancel()
		self.stimulus_end_event.cancel()
		self.stimdur_event.cancel()
		self.iti_event.cancel()

		self.hold_button.unbind(on_press=self.response_cancelled)
		
		self.stimulus_press_time = time.time()
		self.stimulus_press_latency = self.stimulus_press_time - self.stimulus_start_time
		self.movement_latency = self.stimulus_press_latency - self.response_latency

		self.feedback_label.text = ''

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur':

			self.protocol_floatlayout.remove_widget(self.blur_widget)
			self.blur_widget.remove_widget(self.img_stimulus_C)
		
		else:
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C)
		

		if self.stimulus_mask_on_screen:
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C_mask)
			self.stimulus_mask_on_screen = False
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'State Change'
			, 'Stimulus Press'
			])
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Object Remove'
			, 'Stimulus'
			, 'Center'
			, 'Center'
			, 'Image Name'
			, self.center_image
			])
		

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise':
			
			self.protocol_floatlayout.remove_widget(self.img_noise_C)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Mask'
				, 'Noise'
				, 'Center'
				, 'Image Name'
				, self.noise_mask_value
				])
		

		if self.display_stimulus_outline == 1:
			
			self.protocol_floatlayout.remove_widget(self.img_outline_C)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Mask'
				, 'Outline'
				, 'Center'
				, 'Image Name'
				, self.display_stimulus_outline
				])
		
		
		if self.current_stage == 'Flanker':
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_L)
			self.protocol_floatlayout.remove_widget(self.img_stimulus_R)

			# if self.display_stimulus_outline == 1:
				
			# 	self.protocol_floatlayout.remove_widget(self.img_outline_L)
			# 	self.protocol_floatlayout.remove_widget(self.img_outline_R)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Stimulus'
				, 'Flanker'
				, 'Left'
				, 'Image Name'
				, self.img_stimulus_L
				])
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Stimulus'
				, 'Flanker'
				, 'Right'
				, 'Image Name'
				, self.img_stimulus_R
				])
		
		self.stimulus_on_screen = False
		self.limhold_started = False
		self.response_made = False

		self.feedback_label.text = ''
		
		if (self.current_stage == 'SART'):
			if (self.center_image in self.current_nontarget_image_list):
				self.contingency = 1
				self.trial_outcome = 1
				
				if self.current_block == 0:
					self.feedback_label.text = self.feedback_dict['correct']
					
			else:
				self.contingency = 0
				self.trial_outcome = 3
				
				if self.current_block == 0:
					self.feedback_label.text = self.feedback_dict['incorrect']
		
		else:
			if (self.center_image == self.target_image):
				#self.feedback_string = self.feedback_dict['correct']
				self.contingency = 1
				self.trial_outcome = 1
				self.current_hits += 1

				self.block_hits += 1
				
				self.feedback_label.text = self.feedback_dict['correct']
				
			else:
				self.contingency = 0
				self.trial_outcome = 3

				self.block_false_alarms += 1
				
				self.feedback_label.text = self.feedback_dict['incorrect']
		

		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Response'
			, str(self.response)
			])
				
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Contingency'
			, str(self.contingency)
			])
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Trial Outcome'
			, str(self.trial_outcome)
			])
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Stimulus Press Latency'
			, str(self.stimulus_press_latency)
			])
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Variable Change'
			, 'Outcome'
			, 'Movement Latency'
			, str(self.movement_latency)
			])
		
		
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
			

		self.write_trial()

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur':

			self.blur_preload_start_event()
		
		else:
			
			self.trial_contingency_event()


		# self.hold_button.bind(on_press=self.iti)
	
	
	
	def center_notpressed(self, *args):
		
		self.stimulus_present_event.cancel()
		self.stimulus_end_event.cancel()
		self.stimdur_event.cancel()
		self.iti_event.cancel()

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur':

			self.protocol_floatlayout.remove_widget(self.blur_widget)
			self.blur_widget.remove_widget(self.img_stimulus_C)
		
		else:
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C)
		

		if self.stimulus_mask_on_screen:
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C_mask)
			self.stimulus_mask_on_screen = False
		

		self.stimulus_press_time = time.time()
		self.stimulus_press_latency = 0.0
		self.movement_latency = 0.0
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'State Change'
			, 'No Stimulus Press'
			])
		
		self.protocol_floatlayout.add_event([
			(self.stimulus_press_time - self.start_time)
			, 'Object Remove'
			, 'Stimulus'
			, 'Center'
			, 'Center'
			, 'Image Name'
			, self.center_image
			])
		

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise':
			
			self.protocol_floatlayout.remove_widget(self.img_noise_C)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Mask'
				, 'Noise'
				, 'Center'
				, 'Image Name'
				, self.noise_mask_value
				])
		

		if self.display_stimulus_outline == 1:
			
			self.protocol_floatlayout.remove_widget(self.img_outline_C)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Mask'
				, 'Outline'
				, 'Center'
				, 'Image Name'
				, self.display_stimulus_outline
				])
		
		
		if self.current_stage == 'Flanker':
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_L)
			self.protocol_floatlayout.remove_widget(self.img_stimulus_R)

			# if self.display_stimulus_outline == 1:
				
			# 	self.protocol_floatlayout.remove_widget(self.img_outline_L)
			# 	self.protocol_floatlayout.remove_widget(self.img_outline_R)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Stimulus'
				, 'Flanker'
				, 'Left'
				, 'Image Name'
				, self.img_stimulus_L
				])
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Remove'
				, 'Stimulus'
				, 'Flanker'
				, 'Right'
				, 'Image Name'
				, self.img_stimulus_R
				])
		
		
		self.stimulus_on_screen = False
		self.limhold_started = False

		if not self.response_made:

			self.response = 0
			self.response_latency = 0.0

			self.feedback_label.text = ''
			
			if (self.current_stage == 'SART'):
				if (self.center_image == self.target_image):
					self.contingency = 1
					self.trial_outcome = 4
					
					self.current_hits += 1
					self.feedback_label.text = self.feedback_dict['correct']
					
				
				else:
					self.contingency = 0
					self.trial_outcome = 2
			
			else:
				if (self.center_image == self.target_image):
					self.contingency = 0  #######
					self.trial_outcome = 2  #####

					if self.current_stage in ['Training', 'Speed_Scaling', 'Blur_Scaling', 'Noise_Scaling', 'Speed', 'Blur', 'Noise']:
						self.feedback_label.text = self.feedback_dict['miss']

					# elif self.current_stage == 'Speed_Scaling':
					# 	self.feedback_label.text = self.feedback_dict['too_slow']
				
				else:
					#self.feedback_string = ''
					self.contingency = 1  #####
					self.trial_outcome = 4  ######
		

			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Variable Change'
				, 'Outcome'
				, 'Trial Response'
				, str(self.response)
				])
					
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Variable Change'
				, 'Outcome'
				, 'Trial Contingency'
				, str(self.contingency)
				])
			
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Variable Change'
				, 'Outcome'
				, 'Trial Outcome'
				, str(self.trial_outcome)
				])
			
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Variable Change'
				, 'Outcome'
				, 'Stimulus Press Latency'
				, str(self.stimulus_press_latency)
				])
			
			self.protocol_floatlayout.add_event([
				(self.stimulus_press_time - self.start_time)
				, 'Variable Change'
				, 'Outcome'
				, 'Movement Latency'
				, str(self.movement_latency)
				])
			

			# if self.feedback_label.text != '' \
			# 	and not self.feedback_on_screen:
				
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
			
			# self.hold_button.unbind(on_press=self.hold_returned_stim)
			# self.hold_button.unbind(on_release=self.hold_removed_stim)
			self.hold_button.unbind(on_release=self.stimulus_response)
		

		else:

			# self.response_made = False
			# self.hold_active = True

			self.hold_button.unbind(on_press=self.response_cancelled)
			

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


		self.response_made = False

		self.write_trial()

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur':

			self.blur_preload_start_event()
		
		else:
			
			self.trial_contingency_event()


		# self.hold_button.bind(on_press=self.iti)
		
		# if self.hold_active == True:
		# 	self.iti()
		# else:
		# 	self.return_hold()
	
	
	
	def response_cancelled(self, *args):
		
		if self.trial_outcome == 5:
			self.feedback_label.text = self.feedback_dict['miss']
		else:
			self.feedback_label.text = self.feedback_dict['abort']

		self.trial_outcome = 7

		self.hold_active = True
		
		self.center_notpressed()
	
	
	
	def hold_removed_stim(self, *args):
		
#		self.hold_button.unbind(on_press=self.hold_returned_stim)
#		self.hold_button.unbind(on_release=self.hold_removed_stim)
		
		self.hold_active = False

#		self.hold_returned = False
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'State Change'
			, 'Hold Removed'
			])
		
#		self.hold_button.bind(on_press=self.center_pressed)
		
		# return
	
	
	
# 	def hold_returned_stim(self, *args):
	
# 		self.hold_active = True
		
# # 		self.protocol_floatlayout.add_event([
# # 			(time.time() - self.start_time)
# # 			, 'State Change'
# # 			, 'Hold Returned'
# # 			])
	
# 		return
	
	
	
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
			, 'Instructions'
			, 'Section'
			])
		
		self.protocol_floatlayout.add_event([
			(time.time() - self.start_time)
			, 'Object Remove'
			, 'Button'
			, 'Continue'
			, 'Section'
			])
		
		self.block_end()
		
	
	# Data Saving Functions # ************ NEEDS TO BE EDITED TO SAVE ALL IMAGES
	def write_trial(self, *args):

		# self.data_cols = [
		# 	'TrialNo'
		# 	, 'Stage'
		# 	, 'Substage'
		# 	, 'Block'
		# 	, 'CurrentBlockTrial'
		# 	#, 'Trial Type'
		# 	, 'Stimulus'
		# 	, 'Correction'
		# 	, 'StimFrames'
		# 	, 'StimDur'
		# 	, 'LimHold'
		# 	, 'Similarity'
		# 	, 'BlurLevel'
		# 	, 'NoiseMaskValue'
		# 	, 'Response'
		# 	, 'Contingency'
		# 	, 'Outcome'
		# 	, 'ResponseLatency'
		# 	, 'StimulusPressLatency'
		# 	, 'MovementLatency'
		# 	]
		
		trial_data = [
			self.current_trial
			, self.current_stage
			, self.current_substage
			, self.target_probability
			, self.current_block
			, self.current_block_trial
			, self.center_image
			, self.current_correction
			, self.stimdur_current_frames
			, self.stimdur
			, self.limhold
			, self.current_similarity
			, self.blur_level
			, self.noise_mask_value
			, self.response
			, self.contingency
			, self.trial_outcome
			, self.response_latency
			, self.stimulus_press_latency
			, self.movement_latency
			]

		self.write_summary_file(trial_data)

		return
	
	
	# Trial Contingency Functions #
	
	def trial_contingency(self, *args):
		# Trial Contingencies: 0-Incorrect; 1-Correct; 2-Response, no center touch; 3-Premature
		# Trial Outcomes: 0-Premature; 1-Hit; 2-Miss; 3-False Alarm; 4-Correct Rejection; 5-Hit, no center touch; 6-False Alarm, no center touch
		
		try:

			self.trial_contingency_event.cancel()

			if self.current_block_trial != 0:
				
				self.printlog('\n\n\n')
				self.printlog('Trial contingency start')
				self.printlog('')
				self.printlog('Current stage: ', self.current_stage)
				self.printlog('Current block: ', self.current_block)
				
				if self.current_substage != '':
					self.printlog('Current substage: ', self.current_substage)
				
				
				self.printlog('Current trial: ', self.current_trial)
				self.printlog('')
				self.printlog('Trial type: ', self.trial_list[self.trial_index])
				self.printlog('ITI: ', self.iti_length)
				self.printlog('Stimulus duration expected frames: ', self.stimdur_current_frames)
				self.printlog('Stimulus duration expected time: ', self.stimdur)
				self.printlog('Stimulus duration actual time: ', self.stimdur_actual)
				self.printlog('Limited hold: ', self.limhold)

				if 'Similarity' in self.stage_list:
					self.printlog('Similarity value: ', self.current_similarity)

				if self.current_stage == 'Similarity':
					self.printlog('Current similarity min: ', self.similarity_index_min)
					self.printlog('Current similarity max: ', self.similarity_index_max)
					self.printlog('Current similarity range: ', self.similarity_index_range)

					# if self.current_similarity < 1.0:
					
					# 	self.similarity_tracking.append(self.current_similarity)

				
				if 'Blur_Scaling' in self.stage_list \
					or self.current_stage == 'Blur':

					self.printlog('Blur level (percent): ', self.blur_level)
					
					# self.blur_widget.remove_widget(self.img_stimulus_C)

					# self.blur_preload_start_event()

				
				if 'Noise_Scaling' in self.stage_list \
					or self.current_stage == 'Noise':

					self.printlog('Noise level: ', self.noise_mask_value)
				
				self.printlog('')
				self.printlog('Trial outcome: ', self.trial_outcome)
				self.printlog('Response latency: ', self.stimulus_press_latency)
				self.printlog('Center image is: ', self.center_image)
				
				




				# Trial Outcomes: 0-Premature; 1-Hit; 2-Miss; 3-False Alarm; 4-Correct Rejection; 5-Premature; 6-Dual Image, wrong side
				
				print('Trial outcome: ', self.trial_outcome)
				
				if (self.current_stage == 'Training') \
					or (self.current_block == 0):
					
					if self.trial_outcome == 1:
						self.last_response = 1
					
					else:
						self.last_response = 0
				
				
				elif self.current_stage == 'Similarity':
					
					if self.trial_outcome == 4:
						self.last_response = 1
					
					elif self.trial_outcome in [2, 3]:
						self.last_response = -1
					
					else:
						self.last_response = 0
				
				
				elif self.current_stage in ['Blur_Scaling', 'Noise_Scaling', 'Blur', 'Noise']:
					
					if self.trial_outcome == 1:
						self.last_response = 1
					
					elif self.trial_outcome in [2, 3]:
						self.last_response = -1
					
					else:
						self.last_response = 0
				
				
				elif self.current_stage == 'Speed_Scaling':
					
					if self.trial_outcome == 1:
						self.last_response = 1
					
					elif self.trial_outcome in [2, 3, 5, 6]:
						self.last_response = -1
					
					else:
						self.last_response = 0
				
				
				elif self.current_stage == 'Speed':
					
					if self.trial_outcome in [1, 5]:
						self.last_response = 1
					
					elif self.trial_outcome in [2, 3, 6]:
						self.last_response = -1
					
					else:
						self.last_response = 0
				
				
				elif self.current_stage in ['SART', 'HighProb']:
					
					if self.trial_outcome == 4:
						self.last_response = 1
					
					elif self.trial_outcome in [3, 6]:
						self.last_response = -1
					
					else:
						self.last_response = 0
				

				else:

					if self.trial_outcome == 1:
						self.last_response = 1
					
					elif self.trial_outcome in [3, 6]:
						self.last_response = -1
					
					else:
						self.last_response = 0
				
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Outcome'
					, 'Last Response'
					, self.last_response
					])
				

				if self.last_response != 0:
					self.response_tracking.append(self.last_response)
				
				
				print('Last response: ', self.last_response)
				print('Response tracking: ', self.response_tracking)

				# if self.current_stage == 'Similarity':

				# 	print('Similarity tracking: ', self.similarity_tracking)
				

				# if 'Blur_Scaling' in self.stage_list \
				# 	or self.current_stage == 'Blur':

				# 	self.blur_preload_start_event()

	
				# FOR STAIRCASING, TRACK STAIRCASE ON MIDDLE PROBABILITY AND USE
					# THAT AS BASELINE FOR HIGH/LOW PROBABILITY; KEEP HIGH AND LOW
					# PROBABILITY STAIRCASES SEPARATE
				
				if self.last_response == 1:
					
					print('Last response correct.')

					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Staircasing'
						, 'Increase'
						])

					if self.current_stage == 'Similarity':

						self.similarity_tracking.append(self.current_similarity)

						print('Similarity tracking: ', self.similarity_tracking)

						if len(self.similarity_tracking) > 20 \
							and self.block_change_on_duration != 1:

							# block_outcome = statistics.multimode(self.similarity_tracking)

							if len(self.similarity_tracking) == 0:
								self.outcome_value = float(
									self.similarity_data.loc[
										self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1]
										, self.target_image
										].to_numpy()
									)
								
							else:
								self.outcome_value = max(self.similarity_tracking)

							# if len(block_outcome) != 1:

							# 	self.outcome_value = max(block_outcome)
							
							# else:

							# 	self.outcome_value = float(block_outcome[0])


							# if self.outcome_value == 0:
							# 	self.outcome_value = statistics.mean(self.similarity_tracking)
				
							if (sum(self.response_tracking[-10:]) <= 4) \
								or ((sum(self.response_tracking[-10:] >= 6)) and (statistics.mean(self.similarity_tracking[-10:]) > 0.90)):
						
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Outcome'
									, 'Similarity'
									, self.outcome_value
									, 'Type'
									, 'Mode'
									])
								

								self.printlog('Similarity Outcome Value: ', self.outcome_value)

								
								baseline_nontarget_image_list = self.similarity_data.loc[
									(self.similarity_data[self.target_image] <= self.outcome_value)
									, 'Nontarget'
									].tolist()
								
								if len(baseline_nontarget_image_list) < (self.similarity_index_range * 2):

									self.current_nontarget_image_list = self.similarity_data.loc[0:(self.similarity_index_range * 2), 'Nontarget']

								else:
									
									self.current_nontarget_image_list = baseline_nontarget_image_list[-(self.similarity_index_range * 2):]
								

								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Parameter'
									, 'Similarity'
									, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])])
									, 'Type'
									, 'Baseline'
									, 'Units'
									, 'Min'
									])
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Parameter'
									, 'Similarity'
									, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])])
									, 'Type'
									, 'Baseline'
									, 'Units'
									, 'Max'
									])


								self.printlog('Baseline nontarget image list: ', self.current_nontarget_image_list)


								# self.similarity_index_max -= self.similarity_index_range
								# self.similarity_index_min -= self.similarity_index_range

								# self.printlog('Final similarity index min: ', self.similarity_index_min)
								# self.printlog('Final similarity index max: ', self.similarity_index_max)

								self.current_block += 1
								# self.feedback_start = time.time()
								self.protocol_floatlayout.remove_widget(self.hold_button)
								# self.block_check_event()
								self.stage_screen_event()


						# if self.trial_index > 1 \
						# 	and self.trial_list[self.trial_index - 2] != 'Target':

						self.similarity_index_min = int(self.nontarget_images.index(self.center_image))

						# self.similarity_index_min += self.similarity_index_change
						self.similarity_index_max = self.similarity_index_min + self.similarity_index_range

						if self.similarity_index_max >= len(self.nontarget_images):

							self.similarity_index_max = len(self.nontarget_images) - 1
							self.similarity_index_min = self.similarity_index_max - self.similarity_index_range
			
			
						self.current_nontarget_image_list = self.nontarget_images[self.similarity_index_min:self.similarity_index_max]
							
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Similarity'
							, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])])
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Min'
							])
						
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Similarity'
							, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])])
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Max'
							])


					elif self.current_stage in ['Blur_Scaling', 'Blur']:

						self.blur_tracking.append(self.blur_level)

						if (len(self.blur_tracking) >= 20) \
							and ((max(self.blur_tracking[-6:]) - min(self.blur_tracking[-6:])) <= 2) \
							and (self.block_change_on_duration != 1):

							block_outcome = statistics.multimode(self.blur_tracking)

							if len(block_outcome) != 1:

								self.outcome_value = max(block_outcome)

							else:

								self.outcome_value = int(block_outcome[0])


							self.protocol_floatlayout.add_event([
								(time.time() - self.start_time)
								, 'Variable Change'
								, 'Outcome'
								, 'Blur'
								, self.outcome_value
								, 'Type'
								, 'Mode'
								])

							self.printlog('Blur Outcome Value: ', self.outcome_value)

							if self.current_stage == 'Blur_Scaling':

								self.blur_base = int(self.outcome_value * 0.9)

								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Parameter'
									, 'Blur'
									, self.blur_base
									, 'Type'
									, 'Baseline'
									])


							self.blur_tracking = list()
							self.last_response = 0
							self.current_block += 1
							# self.feedback_start = time.time()
							self.protocol_floatlayout.remove_widget(self.hold_button)
							# self.block_check_event()
							self.stage_screen_event()

						self.blur_level += self.blur_change


						# self.blur_horz = int(self.blur_level * self.image_texture_size[0])
						# self.blur_vert = int(self.blur_level * self.image_texture_size[1])

						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Blur'
							, self.blur_level
							, 'Type'
							, 'Staircasing'
							])


						self.blur_widget.effects = [HorizontalBlurEffect(size=self.blur_level), VerticalBlurEffect(size=self.blur_level)]


					elif self.current_stage in ['Noise_Scaling', 'Noise']:

						self.noise_tracking.append(int(self.noise_mask_value))

						if len(self.noise_tracking) >= 20 \
							and ((max(self.noise_tracking[-6:]) - min(self.noise_tracking[-6:])) <= 15) \
							and self.block_change_on_duration != 1:

							block_outcome = statistics.multimode(self.noise_tracking)

							if len(block_outcome) != 1:

								self.outcome_value = max(block_outcome)
							
							else:

								self.outcome_value = float(block_outcome[0])


							self.protocol_floatlayout.add_event([
								(time.time() - self.start_time)
								, 'Variable Change'
								, 'Outcome'
								, 'Noise'
								, self.outcome_value
								, 'Type'
								, 'Mode'
								])

							
							self.printlog('Noise Outcome Value: ', self.outcome_value)
							
							if self.current_stage == 'Noise_Scaling':
								
								self.noise_base = int(self.outcome_value) - 10

								if self.noise_base < 0:

									self.noise_base = 0
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Parameter'
									, 'Noise'
									, self.noise_base
									, 'Type'
									, 'Baseline'
									])


							self.noise_mask_index = round(self.noise_base/5) - 1

							if self.noise_mask_index < 0:

								self.noise_mask_index = 0
							

							self.noise_tracking = list()
							
							self.last_response = 0
							self.current_block += 1
							# self.feedback_start = time.time()
							self.protocol_floatlayout.remove_widget(self.hold_button)
							# self.block_check_event()
							self.stage_screen_event()

						
						if self.noise_mask_index < len(self.noise_mask_list) - 1:
							
							self.noise_mask_index += self.noise_mask_index_change

							if self.noise_mask_index >= len(self.noise_mask_list):

								self.noise_mask_index = len(self.noise_mask_list) - 1


							self.img_noise_C_path = str(self.noise_mask_paths[self.noise_mask_index])
							self.noise_mask_value = self.noise_mask_list[self.noise_mask_index]
						

						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Noise'
							, self.noise_mask_value
							, 'Type'
							, 'Staircasing'
							])

						self.img_noise_C.texture = self.image_dict[self.noise_mask_value].image.texture
					

					elif self.current_stage in ['Speed_Scaling', 'Speed']:

						self.stimdur_frame_tracking.append(self.stimdur_current_frames)

						if (len(self.stimdur_frame_tracking) > 20) \
							and ((max(self.stimdur_frame_tracking[-10:]) - min(self.stimdur_frame_tracking[-10:])) <= 12) \
							and self.block_change_on_duration != 1:

							block_outcome = statistics.multimode(self.stimdur_frame_tracking)

							if len(block_outcome) != 1:

								self.outcome_value = min(block_outcome)
							
							else:

								self.outcome_value = float(block_outcome[0])
							

							self.printlog('StimDur Outcome Value: ', self.outcome_value)

							if self.current_stage == 'Speed_Scaling':

								self.stimdur_base = self.outcome_value + round(0.100/self.frame_duration)

								if self.stimdur_base > self.staircase_stimdur_frame_max:
									
									self.stimdur_base = self.staircase_stimdur_frame_max


								self.limhold_base = self.stimdur_base * self.frame_duration

								self.limhold = self.limhold_base
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Outcome'
									, 'Stimulus Duration'
									, self.outcome_value
									, 'Type'
									, 'Mode'
									, 'Units'
									, 'Frames'
									])
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Outcome'
									, 'Stimulus Duration'
									, str(self.outcome_value * self.frame_duration)
									, 'Type'
									, 'Mode'
									, 'Units'
									, 'Seconds'
									])
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Outcome'
									, 'Limited Hold'
									, str(self.outcome_value * self.frame_duration)
									, 'Type'
									, 'Mode'
									, 'Units'
									, 'Seconds'
									])
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Parameter'
									, 'Stimulus Duration'
									, self.stimdur_base
									, 'Type'
									, 'Baseline'
									, 'Units'
									, 'Frames'
									])
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Parameter'
									, 'Stimulus Duration'
									, str(self.stimdur_base * self.frame_duration)
									, 'Type'
									, 'Baseline'
									, 'Units'
									, 'Seconds'
									])
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Parameter'
									, 'Limited Hold'
									, self.limhold
									, 'Type'
									, 'Baseline'
									, 'Units'
									, 'Seconds'
									])
							

							else:
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Outcome'
									, 'Stimulus Duration'
									, self.outcome_value
									, 'Type'
									, 'Mode'
									, 'Units'
									, 'Frames'
									])
								
								self.protocol_floatlayout.add_event([
									(time.time() - self.start_time)
									, 'Variable Change'
									, 'Outcome'
									, 'Stimulus Duration'
									, str(self.outcome_value * self.frame_duration)
									, 'Type'
									, 'Mode'
									, 'Units'
									, 'Seconds'
									])
						
								# self.stimdur_frames = [int(frames) for frames in self.stimdur_frames if frames <= self.stimdur_base]
						
							self.stimdur_frame_tracking = list()
							
							self.last_response = 0
							self.current_block += 1
							# self.feedback_start = time.time()
							self.protocol_floatlayout.remove_widget(self.hold_button)
							# self.block_check_event()
							self.stage_screen_event()
						

						elif (self.stimdur_use_steps) \
							and (self.stimdur_index < len(self.stimdur_frames) - 1):
							
							self.stimdur_index += 1
							self.stimdur_current_frames = self.stimdur_frames[self.stimdur_index]
							self.stimdur_change = self.stimdur_frames[self.stimdur_index - 1] - self.stimdur_frames[self.stimdur_index]
						
						
						else:
							
							if sum(self.response_tracking[-3:]) == 3 \
								and self.stimdur_current_frames > min(self.stimdur_frames):
								
								self.printlog('Last 3 responses correct; increase stimdur frame change.')

								self.stimdur_index = 0

								while self.stimdur_current_frames < self.stimdur_frames[self.stimdur_index] \
									and self.stimdur_index < len(self.stimdur_frames) - 1:

									self.stimdur_index += 1
								
								self.stimdur_current_frames = self.stimdur_frames[self.stimdur_index]
								self.stimdur_change = self.stimdur_frames[self.stimdur_index - 1] - self.stimdur_frames[self.stimdur_index]
								self.stimdur_use_steps = True
								
								self.response_tracking.append(0)
								self.response_tracking.append(0)
							

							else:

								if self.stimdur_current_frames < min(self.stimdur_frames) \
									and self.stimdur_change not in [1, 2]:

									self.stimdur_change = 2
								

								self.stimdur_current_frames -= self.stimdur_change
						
						
						if self.stimdur_current_frames < self.staircase_stimdur_frame_min:
							
							self.stimdur_current_frames = self.staircase_stimdur_frame_min
						
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Outcome'
							, 'Stimulus Duration'
							, self.outcome_value
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Frames'
							])
						
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Outcome'
							, 'Stimulus Duration'
							, str(self.outcome_value * self.frame_duration)
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Seconds'
							])
						

						if self.current_stage == 'Speed_Scaling':

							self.limhold = self.stimdur_current_frames * self.frame_duration
							
							self.protocol_floatlayout.add_event([
								(time.time() - self.start_time)
								, 'Variable Change'
								, 'Outcome'
								, 'Limited Hold'
								, self.limhold
								, 'Type'
								, 'Staircasing'
								, 'Units'
								, 'Seconds'
								])
				
				
				elif self.last_response == -1:
					
					print('Last response incorrect.')

					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Staircasing'
						, 'Decrease'
						])

					if self.current_stage == 'Similarity':

						if self.center_image != self.target_image:
						
							self.similarity_index_max = int(self.nontarget_images.index(self.center_image))
							self.similarity_index_min = self.similarity_index_max - self.similarity_index_range
						
						else:

							self.similarity_index_max -= int(self.similarity_index_range//2)
							self.similarity_index_min = self.similarity_index_max - self.similarity_index_range
						

						if self.similarity_index_min < 0:

							self.similarity_index_min = 0
							self.similarity_index_max = self.similarity_index_range
			
			
						self.current_nontarget_image_list = self.nontarget_images[self.similarity_index_min:self.similarity_index_max]
							
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Similarity'
							, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])])
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Min'
							])

						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Similarity'
							, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])])
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Max'
							])


					elif self.current_stage in ['Blur_Scaling', 'Blur']:

						if self.response_tracking[-2] in [0, 1]:

							if self.blur_change > 1:

								self.blur_change //= 2

								if self.blur_change < 1:

									self.blur_change = 1


						self.blur_level -= self.blur_change

						if self.blur_level < 0:
							self.blur_level = 0


						# self.blur_horz = int(self.blur_level * self.image_texture_size[0])
						# self.blur_vert = int(self.blur_level * self.image_texture_size[1])


						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Blur'
							, self.blur_level
							, 'Type'
							, 'Staircasing'
							])


						self.blur_widget.effects = [HorizontalBlurEffect(size=self.blur_level), VerticalBlurEffect(size=self.blur_level)]


					if self.current_stage in ['Noise_Scaling', 'Noise']:

						if self.response_tracking[-2] in [0, 1]:

							if self.noise_mask_index_change > 1:

								self.noise_mask_index_change //= 2

								if self.noise_mask_index_change < 1:

									self.noise_mask_index_change = 1


						self.noise_mask_index -= self.noise_mask_index_change
						
						if self.noise_mask_index < 0:
							self.noise_mask_index = 0

						self.img_noise_C_path = str(self.noise_mask_paths[self.noise_mask_index])
						self.noise_mask_value = self.noise_mask_list[self.noise_mask_index]

						self.img_noise_C.texture = self.image_dict[self.noise_mask_value].image.texture
						
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Parameter'
							, 'Noise'
							, self.noise_mask_value
							, 'Type'
							, 'Staircasing'
							])

					
					elif self.current_stage in ['Speed_Scaling', 'Speed']:
						
						self.stimdur_use_steps = False
						
						if self.response_tracking[-2] in [0, 1]:
							
							self.stimdur_change //= 2
							
							if self.stimdur_change < 1: # self.staircase_stimdur_frame_min:
								
								self.stimdur_change = 1 # self.staircase_stimdur_frame_min
						
						
						self.stimdur_current_frames += self.stimdur_change

						if (self.stimdur_current_frames > self.stimdur_base) \
							or (self.stimdur_current_frames > (self.limhold_base/self.frame_duration)):

							if self.stimdur_base > (self.limhold_base/self.frame_duration):

								self.stimdur_current_frames = (self.limhold_base/self.frame_duration)
							
							else:

								self.stimdur_current_frames = self.stimdur_base
						
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Outcome'
							, 'Stimulus Duration'
							, self.outcome_value
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Frames'
							])
						
						self.protocol_floatlayout.add_event([
							(time.time() - self.start_time)
							, 'Variable Change'
							, 'Outcome'
							, 'Stimulus Duration'
							, str(self.outcome_value * self.frame_duration)
							, 'Type'
							, 'Staircasing'
							, 'Units'
							, 'Seconds'
							])
						

						if self.current_stage == 'Speed_Scaling':

							self.limhold = self.stimdur_current_frames * self.frame_duration
							
							self.protocol_floatlayout.add_event([
								(time.time() - self.start_time)
								, 'Variable Change'
								, 'Outcome'
								, 'Limited Hold'
								, self.limhold
								, 'Type'
								, 'Staircasing'
								, 'Units'
								, 'Seconds'
								])





			# Set next trial parameters

			# Trial number and trial index

			self.current_trial += 1
			self.current_block_trial += 1
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Variable Change'
				, 'Parameter'
				, 'Current Trial'
				, self.current_trial
				])
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Variable Change'
				, 'Parameter'
				, 'Current Block Trial'
				, self.current_block_trial
				])


			# ITI
			
			if len(self.iti_frame_range) > 1:
				
				if self.iti_fixed_or_range == 'fixed':
					
					self.iti_length = random.choice(self.iti_frame_range) * self.frame_duration
				
				
				else:
					
					self.iti_length = random.randint(min(self.iti_frame_range), max(self.iti_frame_range)) * self.frame_duration
				

				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Current ITI'
					, self.iti_length
					])


			# Stimulus duration/limited hold frames

			if self.current_block == 0:
				
				self.stimdur_current_frames = self.stimdur_base
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Outcome'
					, 'Stimulus Duration'
					, self.outcome_value
					, 'Type'
					, 'Training'
					, 'Units'
					, 'Frames'
					])
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Outcome'
					, 'Stimulus Duration'
					, str(self.outcome_value * self.frame_duration)
					, 'Type'
					, 'Training'
					, 'Units'
					, 'Seconds'
					])
				

			if self.current_stage == 'Speed_Scaling':

				self.limhold = self.stimdur_current_frames * self.frame_duration
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Outcome'
					, 'Limited Hold'
					, self.limhold
					, 'Type'
					, 'Training'
					, 'Units'
					, 'Seconds'
					])
			

			self.stimdur = self.stimdur_current_frames * self.frame_duration

			if self.stimdur > self.limhold:

				self.limhold = self.stimdur
			




			# Set next trial type and stimulus
			
			# False alarm (mistake + response)
			if (self.correction_trials_active == 1) \
				and (self.contingency == 0) \
				and (self.response == 1) \
				and (self.current_stage != 'HighProb'):
				
				self.printlog('False alarm')
				self.printlog('Correction trial initiated...')
				self.current_correction = True
				# self.img_stimulus_C_image_path = str(self.image_folder / self.center_image) + '.png'
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Stimulus'
					, self.center_image
					, 'Type'
					, 'Correction'
					])
				
				# self.img_stimulus_C.texture = self.image_dict[self.center_image].image.texture
				# self.blur_widget.add_widget(self.img_stimulus_C)

				# return
			
			# SART miss (nontarget + no response)
			elif (self.contingency == 0) \
				and (self.response == 0) \
				and (self.current_stage == 'SART'):
				
				self.printlog('Miss (SART)')
				self.printlog('Correction trial initiated...')
				self.current_correction = True
				# self.img_stimulus_C_image_path = str(self.image_folder / self.center_image) + '.png'
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Stimulus'
					, self.center_image
					, 'Type'
					, 'Correction'
					])
				
				# self.img_stimulus_C.texture = self.image_dict[self.center_image].image.texture
				# self.blur_widget.add_widget(self.img_stimulus_C)
				# return
			
			# Premature response
			elif self.contingency == 3:
				
				self.printlog('Premature response')
				# self.img_stimulus_C_image_path = str(self.image_folder / self.center_image) + '.png'
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Stimulus'
					, self.center_image
					, 'Type'
					, 'Premature'
					])
				
				# self.img_stimulus_C.texture = self.image_dict[self.center_image].image.texture
				# self.blur_widget.add_widget(self.img_stimulus_C)
				# return
			
			# Hit or miss
			else: # Set next stimulus image
				
				self.printlog('Next trial (hit or miss)')
				self.printlog('Set next stimulus image')
				self.current_correction = False

				# if 'Blur_Scaling' in self.stage_list:

				# 	self.blur_widget.remove_widget(self.img_stimulus_C)


				self.trial_index += 1
				
				if self.trial_index >= len(self.trial_list):
					random.shuffle(self.trial_list)
					self.trial_index = 0
				
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Trial Index'
					, self.trial_index
					])
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Trial Type'
					, self.trial_list[self.trial_index]
					])
				
				if self.trial_list[self.trial_index] == 'Target':
					
					self.center_image = self.target_image
					self.current_similarity = 1.00
				
				else:

					self.center_image = random.choice(self.current_nontarget_image_list)
				
					if self.current_stage == 'Similarity':

						# self.current_nontarget = random.choice(self.current_nontarget_image_list)
						self.current_similarity = float(self.similarity_data.loc[
								self.similarity_data['Nontarget'] == self.center_image
								, self.target_image
								].to_numpy())
					
					# else:
					
					# 	self.current_nontarget = random.choice(self.nontarget_images)
					
					# self.center_image = self.current_nontarget
				
				self.img_stimulus_C_image_path = str(self.image_folder / self.center_image) + '.png'
				self.img_stimulus_C.texture = self.image_dict[self.center_image].image.texture
				
				# if 'Blur_Scaling' in self.stage_list \
				# 	or self.current_stage == 'Blur':

				# 	self.blur_widget.add_widget(self.img_stimulus_C)
				
				# self.trial_index += 1
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Stimulus'
					, self.center_image
					, 'Type'
					, 'Novel'
					])
			
			# Flanker probe - set flankers
			if self.current_stage == 'Flanker':

				self.printlog('Set flankers...')
				
				if self.flanker_stage_index >= len(self.flanker_stage_list):
					random.shuffle(self.flanker_stage_list)
					self.flanker_stage_index = 0
								
				self.current_substage = self.flanker_stage_list[self.flanker_stage_index]

				self.printlog('Current flanker substage: ', self.current_substage)

				self.flanker_stage_index += 1
				
				if self.current_substage == 'none':
					# self.img_stimulus_L_image_path = str(self.image_folder) + 'black.png'
					# self.img_stimulus_R_image_path = str(self.image_folder) + 'black.png'
					# self.left_image = 'black'
					# self.right_image = 'black'
					self.flanker_image = 'black'
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Flanker'
						, self.left_image
						, 'Type'
						, 'Blank'
					])

				elif self.current_substage == 'same':
					# self.img_stimulus_L_image_path = self.img_stimulus_C_image_path
					# self.img_stimulus_R_image_path = self.img_stimulus_C_image_path
					# self.left_image = self.center_image
					# self.right_image = self.center_image
					self.flanker_image = self.center_image
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Flanker'
						, self.left_image
						, 'Type'
						, 'Congruent'
					])
				
				elif self.current_substage == 'diff':
					
					if self.trial_list[self.trial_index] == 'Target':
						self.flanker_image = random.choice(self.current_nontarget_image_list)
					
					else:
						self.flanker_image = self.target_image
					
					# self.img_stimulus_L_image_path = str(self.image_folder / self.flanker_image) + '.png'
					# self.img_stimulus_R_image_path = str(self.image_folder / self.flanker_image) + '.png'
					# self.left_image = self.flanker_image
					# self.right_image = self.flanker_image
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Flanker'
						, self.flanker_image
						, 'Type'
						, 'Incongruent'
					])
				
				self.img_stimulus_L.texture = self.image_dict[self.flanker_image].image.texture
				self.img_stimulus_R.texture = self.image_dict[self.flanker_image].image.texture
			
			
			self.last_response = 0
			self.trial_outcome = 0
			
			
			# Over session length/duration?
			if (self.current_trial > self.session_trial_max) \
				or ((time.time() - self.start_time) >= self.session_length_max):

				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'State Change'
					, 'Session End'
					])

				self.printlog('Trial/time over session max; end session.')
				self.hold_button.unbind(on_release=self.stimulus_response)
				self.session_event.cancel()
				self.protocol_end()
				
				# return
			
			# Over block length/duration?
			if (self.current_block_trial > self.block_trial_max) \
				or ((time.time() - self.block_start_time) >= self.block_duration):

				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'State Change'
					, 'Block End'
					])
				
				self.hold_button.unbind(on_release=self.stimulus_response)
				self.contingency = 0
				self.trial_outcome = 0
				self.last_response = 0

				self.printlog('Max trials/duration reached for block')
				
				if self.current_stage == 'Similarity':
					
					# block_outcome = statistics.multimode(self.similarity_tracking)

					if len(self.similarity_tracking) == 0:
						self.outcome_value = float(
							self.similarity_data.loc[
								self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1]
								, self.target_image
								].to_numpy()
							)
						
					else:
						self.outcome_value = max(self.similarity_tracking)

					# if len(block_outcome) != 1:

					# 	self.outcome_value = max(block_outcome)
					
					# else:

					# 	self.outcome_value = float(block_outcome[0])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Similarity'
						, self.outcome_value
						, 'Type'
						, 'Mode'
						])
					

					baseline_nontarget_image_list = self.similarity_data.loc[
						(self.similarity_data[self.target_image] <= self.outcome_value)
						, 'Nontarget'
						].tolist()
					
					self.current_nontarget_image_list = baseline_nontarget_image_list[-self.similarity_index_range:]
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Similarity'
						, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])])
						, 'Type'
						, 'Baseline'
						, 'Units'
						, 'Min'
						])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Similarity'
						, str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])])
						, 'Type'
						, 'Baseline'
						, 'Units'
						, 'Max'
						])


					# self.similarity_index_max -= self.similarity_index_range
					# self.similarity_index_min -= self.similarity_index_range

					
					self.similarity_tracking = list()
				

				elif self.current_stage in ['Blur_Scaling', 'Blur']:

					block_outcome = statistics.multimode(self.blur_tracking)

					if len(block_outcome) == 0:

						self.outcome_value = 0

					elif len(block_outcome) != 1:

						self.outcome_value = max(block_outcome)
					

					else:

						self.outcome_value = float(block_outcome[0])
					

					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, self.outcome_value
						, 'Type'
						, 'Mode'
						])

					self.blur_base = int(self.outcome_value * 0.9)
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, self.blur_base
						, 'Type'
						, 'Baseline'
						])

					self.blur_tracking = list()
				

				elif self.current_stage == 'Noise_Scaling':
					
					block_outcome = statistics.multimode(self.noise_tracking)

					if len(block_outcome) == 0:

						self.outcome_value = 0

					elif len(block_outcome) != 1:

						self.outcome_value = max(block_outcome)
					
					else:

						self.outcome_value = float(block_outcome[0])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Noise'
						, self.outcome_value
						, 'Type'
						, 'Mode'
						])

					self.noise_base = int(self.outcome_value - 10)

					if self.noise_base < 0:

						self.noise_base = 0

					self.noise_mask_index = round(self.noise_base//5) - 1

					if self.noise_mask_index < 0:

						self.noise_mask_index = 0
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Noise'
						, str(self.noise_base)
						, 'Type'
						, 'Baseline'
						])

					
					self.noise_tracking = list()
				

				elif self.current_stage == 'Speed_Scaling':
					
					block_outcome = statistics.multimode(self.stimdur_frame_tracking)

					if len(block_outcome) == 0:

						self.outcome_value = min(self.stimdur_frame_tracking) #240

					elif len(block_outcome) != 1:

						self.outcome_value = min(block_outcome)
					
					else:

						self.outcome_value = int(block_outcome[0])

					
					self.stimdur_base = self.outcome_value + int(0.100/self.frame_duration)

					self.limhold_base = self.stimdur_base * self.frame_duration
					self.limhold = self.limhold_base
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Stimulus Duration'
						, self.outcome_value
						, 'Type'
						, 'Mode'
						, 'Units'
						, 'Frames'
						])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Stimulus Duration'
						, str(self.outcome_value * self.frame_duration)
						, 'Type'
						, 'Mode'
						, 'Units'
						, 'Seconds'
						])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Limited Hold'
						, str(self.outcome_value * self.frame_duration)
						, 'Type'
						, 'Mode'
						, 'Units'
						, 'Seconds'
						])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Stimulus Duration'
						, self.stimdur_base
						, 'Type'
						, 'Baseline'
						, 'Units'
						, 'Frames'
						])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Stimulus Duration'
						, str(self.stimdur_base * self.frame_duration)
						, 'Type'
						, 'Baseline'
						, 'Units'
						, 'Seconds'
						])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Limited Hold'
						, self.limhold
						, 'Type'
						, 'Baseline'
						, 'Units'
						, 'Seconds'
						])
					
					# self.stimdur_frames = [int(frames) for frames in self.stimdur_frames if frames <= self.stimdur_base]
					
					self.stimdur_frame_tracking = list()
				

				elif self.current_stage == 'Noise':
					
					block_outcome = statistics.multimode(self.noise_tracking)

					if len(block_outcome) == 0:

						self.outcome_value = 0

					elif len(block_outcome) != 1:

						self.outcome_value = max(block_outcome)
					
					else:

						self.outcome_value = float(block_outcome[0])

					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Noise'
						, self.outcome_value
						, 'Type'
						, 'Mode'
						])
					
					
					self.noise_tracking = list()
				

				elif self.current_stage == 'Speed':
					
					block_outcome = statistics.multimode(self.stimdur_frame_tracking)

					if len(block_outcome) == 0:

						self.outcome_value = min(self.stimdur_frame_tracking) #240

					elif len(block_outcome) != 1:

						self.outcome_value = min(block_outcome)
					
					else:

						self.outcome_value = int(block_outcome[0])
					

					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Stimulus Duration'
						, self.outcome_value
						, 'Type'
						, 'Mode'
						, 'Units'
						, 'Frames'
						])
					
					self.protocol_floatlayout.add_event([
						(time.time() - self.start_time)
						, 'Variable Change'
						, 'Outcome'
						, 'Stimulus Duration'
						, str(self.outcome_value * self.frame_duration)
						, 'Type'
						, 'Mode'
						, 'Units'
						, 'Seconds'
						])
					
					
					self.stimdur_frame_tracking = list()
				

				# elif self.current_stage == 'MidProb':
					
				# 	block_outcome = statistics.multimode(self.stimdur_frame_tracking)

				# 	if len(block_outcome) != 1:

				# 		self.outcome_value = min(block_outcome)
					
				# 	else:

				# 		self.outcome_value = float(block_outcome[0])

					
				# 	self.stimdur_mid = self.outcome_value + int(0.100/self.frame_duration)

				# 	self.stimdur_frame_tracking = list()
				
				
				# elif self.current_stage in ['HighProb', 'SART']:
					
				# 	block_outcome = statistics.multimode(self.stimdur_frame_tracking)

				# 	if len(block_outcome) != 1:

				# 		self.outcome_value = min(block_outcome)
					
				# 	else:

				# 		self.outcome_value = float(block_outcome[0])

					
				# 	self.stimdur_high = self.outcome_value + int(0.100/self.frame_duration)
					
				# 	self.stimdur_frame_tracking = list()
				
				
				# elif self.current_stage in ['LowProb', 'Flanker']:
					
				# 	block_outcome = statistics.multimode(self.stimdur_frame_tracking)

				# 	if len(block_outcome) != 1:

				# 		self.outcome_value = min(block_outcome)
					
				# 	else:

				# 		self.outcome_value = float(block_outcome[0])

					
				# 	self.stimdur_low = self.outcome_value + int(0.100/self.frame_duration)
					
				# 	self.stimdur_frame_tracking = list()
				
				
				self.current_block += 1

				self.protocol_floatlayout.remove_widget(self.hold_button)
				
				if self.current_stage == 'Training':
					self.block_check_event()
				
				# elif (self.current_stage == 'TarProb') \
				# 	and (self.current_block <= len(self.target_prob_list)):
				# 	self.block_check_event()

				else:
					
					self.stage_screen_event()
			

			elif (self.current_stage == 'Training') \
				and (sum(self.response_tracking) >= self.training_block_max_correct):

				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'State Change'
					, 'Block End'
					])
				
				self.hold_button.unbind(on_release=self.stimulus_response)
				self.contingency = 0
				self.trial_outcome = 0
				self.last_response = 0
				
				self.current_block += 1

				self.protocol_floatlayout.remove_widget(self.hold_button)
				
				self.block_check_event()

				# return

			self.printlog('Trial contingency end')


			self.hold_button.bind(on_press=self.iti)
			
			if self.hold_active == True:
				self.iti()
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
# 		except:
# 			
# 			self.printlog('Error; program terminated.')
# 			
# 			self.protocol_end()



	def stage_screen(
			self
			, *args
			):
		

		if not self.stage_screen_started:
		
			self.protocol_floatlayout.add_event([
				(self.stimulus_start_time - self.start_time)
				, 'State Change'
				, 'Stage End'
				])

			self.iti_event.cancel()
			self.stimdur_event.cancel()
			self.stimulus_present_event.cancel()
			self.stimulus_end_event.cancel()

			self.protocol_floatlayout.clear_widgets()
			self.feedback_on_screen = False
			
			
			if self.current_stage == 'Similarity':

				self.outcome_string = 'Great job!\n\nYou were able to correctly discriminate between stimuli\nwith ' + str(int(self.outcome_value*100)) + '%' + ' similarity.'
			
			elif self.current_stage in ['Blur_Scaling', 'Blur']:

				self.outcome_string = 'Great job!\n\nYou were able to correctly discriminate between stimuli\nwith ' + str(int(self.outcome_value)) + ' pixels of blur.'
			
			elif self.current_stage in ['Noise_Scaling', 'Noise']:

				self.outcome_string = 'Great job!\n\nYou were able to correctly identify stimuli with \n' + str(100 - self.outcome_value) + '%' + ' of the image visible.'

			elif self.current_stage == 'Speed_Scaling':

				self.outcome_string = 'Great job!\n\nYou were able to correctly respond to stimuli\nwithin ' + str(round((self.outcome_value * self.frame_duration), 3)) + ' seconds.'
			
			elif self.current_stage == 'Speed':

				self.outcome_string = 'Great job!\n\nYou were able to correctly identify stimuli presented\nfor ' + str(int(self.outcome_value)) + ' frames (' + str(round((self.outcome_value * self.frame_duration), 3)) + ' seconds).'

			elif self.current_stage in ['TarProb', 'Flanker']:

				self.hit_accuracy = (self.block_hits / self.block_target_total)

				self.outcome_string = 'Great job!\n\nYour accuracy on that block was ' + str(round(self.hit_accuracy, 2) * 100) + '%!\n\nYou made ' + str(self.block_false_alarms) + ' false alarms (responses to nontarget images).'
			
			else:

				self.outcome_string = "Great job!\n\nYou've completed all of the trials in this block."
			

			if self.stage_index < len(self.stage_list):

				self.stage_string = 'Please press "CONTINUE" to start the next block.'

			else:
				
				self.stage_string = 'You have completed this task.\n\nPlease inform your researcher.' # 'Please press "END SESSION" to end the session.'

				self.session_end_button.pos_hint = {"center_x": 0.5, "center_y": 0.15}

				self.protocol_floatlayout.add_widget(self.session_end_button)

			
			stage_text = self.outcome_string + '\n\n' + self.stage_string

			self.stage_results_label.text = stage_text

			self.protocol_floatlayout.add_widget(self.stage_results_label)
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Object Display'
				, 'Text'
				, 'Stage'
				, 'Results'
				])

			self.stage_screen_time = time.time()
			self.stage_screen_started = True

			self.stage_screen_event()


		if (time.time() - self.stage_screen_time) >= 1.0:

			self.stage_screen_event.cancel()
			self.stage_screen_started = False

			if self.stage_index < (len(self.stage_list)):
				self.protocol_floatlayout.add_widget(self.stage_continue_button)
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Object Display'
					, 'Button'
					, 'Stage'
					, 'Continue'
					])
			
			# else:
			# 	self.session_end_button.pos_hint = {"center_x": 0.5, "center_y": 0.15}

			# self.protocol_floatlayout.add_widget(self.session_end_button)
			
			# self.protocol_floatlayout.add_event([
			# 	(time.time() - self.start_time)
			# 	, 'Object Display'
			# 	, 'Button'
			# 	, 'Session'
			# 	, 'End'
			# 	])
	
	
	
	def block_contingency(self, *args):
		
		try:
			
			self.stimulus_present_event.cancel()
			self.stimulus_end_event.cancel()
			self.stimdur_event.cancel()
			self.iti_event.cancel()
			
			if self.feedback_on_screen:
				# self.printlog('Feedback on screen')
				
				if (time.time() - self.feedback_start_time) >= self.feedback_length:
					self.printlog('Feedback over')
					self.block_check_event.cancel()
					self.protocol_floatlayout.remove_widget(self.feedback_label)
					# self.feedback_string = ''
					self.feedback_label.text = ''
					self.feedback_on_screen = False
				else:
					# self.printlog('Wait for feedback delay')
					return
			else:
				self.printlog('Block check event cancel')
				self.block_check_event.cancel()
			
			self.printlog('\n\n\n')
			self.printlog('Block contingency start')
			self.printlog('Current block: ', self.current_block)
			self.printlog('Current trial: ', self.current_trial)
		
			self.protocol_floatlayout.add_event([
				(self.stimulus_start_time - self.start_time)
				, 'State Change'
				, 'Block Contingency'
				])


			self.protocol_floatlayout.clear_widgets()
		
			self.protocol_floatlayout.add_event([
				(self.stimulus_start_time - self.start_time)
				, 'State Change'
				, 'Screen Cleared'
				])

			self.previous_stage = self.current_stage

			self.hold_active = False
			
			# self.current_hits = 0
			
			# self.block_start_time = time.time()
			
			# self.protocol_floatlayout.add_event([
			# 	(self.block_start_time - self.start_time)
			# 	, 'Variable Change'
			# 	, 'Parameter'
			# 	, 'Block Start Time'
			# 	, str(self.block_start_time)
			# 	])
			
			
			if (self.current_block > self.block_max_count) or (self.current_block == -1):

				self.stage_index += 1
				self.current_block = 1
				# self.response_tracking = [0,0]
				
				self.printlog('Stage index: ', self.stage_index)
	
				if self.stage_index >= len(self.stage_list): # Check if all stages complete
					self.printlog('All stages complete')
					self.session_event.cancel()
					self.protocol_end()
					# return
				else:
					self.current_stage = self.stage_list[self.stage_index]
					self.current_substage = ''
					self.printlog('Current stage: ', self.current_stage)
			
				self.protocol_floatlayout.add_event([
					(self.stimulus_start_time - self.start_time)
					, 'State Change'
					, 'Stage Change'
					, 'Current Stage'
					, self.current_stage
					])
			
				self.protocol_floatlayout.add_event([
					(self.stimulus_start_time - self.start_time)
					, 'State Change'
					, 'Training Block'
					, 'Current Stage'
					, self.current_stage
					])
				
				self.trial_list = ['Target']
			
				self.protocol_floatlayout.add_event([
					(self.stimulus_start_time - self.start_time)
					, 'Variable Change'
					, 'Parameter'
					, 'Trial List'
					, 'Target'
					])

				self.stimdur_current_frames = self.stimdur_base

				if 'Blur_Scaling' in self.stage_list \
					or self.current_stage == 'Blur':

					self.blur_level = self.blur_base

				# self.limhold = self.stimdur_base * self.frame_duration #self.limhold_base
				
				
				if self.current_stage == 'Noise': # Set high prob task params
					# self.stimdur_current_frames = self.stimdur_base
					# self.limhold = self.stimdur_base * self.frame_duration #self.limhold_base
					# self.staircase_stimdur = 0
					# self.noise_mask_index = 0 #int(len(self.noise_mask_list)//2)
					self.printlog('Noise task initialized')
				
				
				elif self.current_stage == 'SART': # Set SART probe params
					self.current_block = 0
					# self.stimdur_current_frames = self.stimdur_base
					# self.limhold = self.stimdur_base * self.frame_duration #self.limhold_base
					# self.staircase_stimdur = int(self.parameters_dict['staircase_stimdur'])
					self.printlog('SART task initialized')
				
				# elif self.current_block == 'TarProb':
				# 	self.block_max_count = len(self.target_prob_list)
				# 	self.printlog('TarProb task initialized')
			
			
			if self.stage_index >= len(self.stage_list): # Check if all stages complete again
			
				self.protocol_floatlayout.add_event([
					(self.stimulus_start_time - self.start_time)
					, 'State Change'
					, 'Protocol End'
					])
				
				self.printlog('All stages complete')
				self.session_event.cancel()
				self.protocol_end()
				# return

			
			if self.current_block == 0: #and self.display_instructions:
					
				self.printlog('Section Training Instructions')
				self.block_trial_max = self.training_block_max_correct
				self.block_duration = 60
				self.printlog(self.trial_list)
				self.section_instr_label.text = self.instruction_dict[str(self.current_stage)]['train']
	# 			self.section_instr_label.text = self.section_instr_string
				self.instruction_button.text = 'Begin Training Block'
				
	# 			self.protocol_floatlayout.add_widget(self.instruction_image_left)
	# 			self.protocol_floatlayout.add_widget(self.instruction_image_right)
				
				
				# self.center_instr_image_path = str(self.image_folder / self.fribble_folder / self.target_image) + '.png'
				# self.center_instr_image = ImageButton(source=self.center_instr_image_path)
				self.center_instr_image.texture = self.image_dict[self.target_image].image.texture
					
				self.protocol_floatlayout.add_widget(self.center_instr_image)
				
				self.protocol_floatlayout.add_widget(self.section_instr_label)
				self.protocol_floatlayout.add_widget(self.instruction_button)
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Object Display'
					, 'Image'
					, 'Block'
					, 'Instructions'
					, 'Type'
					, 'Target'
					])
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Object Display'
					, 'Text'
					, 'Block'
					, 'Instructions'
					, 'Type'
					, 'Training'
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
			
			
			elif self.current_block == 1: #and self.display_instructions:
				
				self.printlog('Section Task Instructions')
				self.section_instr_label.text = self.instruction_dict[str(self.current_stage)]['task']
				
				self.block_trial_max = int(self.parameters_dict['block_trial_max'])

				self.block_duration = self.block_duration_staircase
				
				self.stimdur_current_frames = self.stimdur_base
				
				if self.current_stage == 'Training':
					self.trial_list = ['Target']
					self.block_trial_max = self.training_block_max_correct
					self.block_duration = 60
					self.target_probability = 1.0

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, 'Training'
						])
				
				elif self.current_stage == 'Similarity':
					self.trial_list = self.trial_list_sim
					self.target_probability = self.target_prob_sim / self.target_prob_trial_num

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, 'Similarity'
						])
				
				elif self.current_stage in ['Blur_Scaling', 'Noise_Scaling', 'Speed_Scaling', 'Noise', 'Blur', 'Speed', 'MidProb']:
					self.trial_list = self.trial_list_mid
					self.target_probability = self.target_prob_mid / self.target_prob_trial_num

					if self.current_stage == 'MidProb':

						self.block_duration = self.block_duration_probe


					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, 'Mid'
						])
				
				
				elif self.current_stage == 'Flanker':

					self.block_target_total = 1
					self.block_nontarget_total = 1
					self.block_false_alarms = 0
					self.block_hits = 0

					self.trial_list = self.trial_list_flanker
					self.target_probability = self.target_prob_sim / self.target_prob_trial_num

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, self.target_probability
						])
				
				
				elif self.current_stage == 'TarProb':
						
					self.block_max_count = len(self.target_prob_list)

					self.block_duration = self.block_duration_probe

					self.block_target_total = 1
					self.block_nontarget_total = 1
					self.block_false_alarms = 0
					self.block_hits = 0

					trial_multiplier = self.block_trial_max / self.target_prob_trial_num

					# if self.current_block == 0:

					# 	self.trial_list = ['Target']
					
					# else:

					self.target_prob_list_index = self.current_block - 1

					self.trial_list = list()
					self.target_probability = self.target_prob_list[self.target_prob_list_index] / self.target_prob_trial_num

					self.block_target_total = trial_multiplier * self.target_prob_list[self.target_prob_list_index]
					self.block_nontarget_total = self.block_trial_max - self.block_target_total

					for iTrial in range(self.target_prob_list[self.target_prob_list_index]):
						self.trial_list.append('Target')

					for iTrial in range((self.target_prob_trial_num - self.target_prob_list[self.target_prob_list_index])):
						self.trial_list.append('Nontarget')


					random.shuffle(self.trial_list)

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, self.target_prob_list[self.target_prob_list_index]
						])
				
				
				elif self.current_stage == 'LowProb':
					self.trial_list = self.trial_list_low
					self.target_probability = self.target_prob_low / self.target_prob_trial_num

					self.block_duration = self.block_duration_probe

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, 'Low'
						])
				
				
				elif self.current_stage == 'HighProb':
					self.trial_list = self.trial_list_high
					self.target_probability = self.target_prob_high / self.target_prob_trial_num

					self.block_duration = self.block_duration_probe

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, 'High'
						])
				
				
				elif self.current_stage == 'SART':
					self.trial_list = self.trial_list_SART
					self.target_probability = self.target_prob_low / self.target_prob_trial_num

					self.block_duration = self.block_duration_probe

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, 'SART'
						])
				
				
				else:
					self.printlog('Unknown stage!')
					self.trial_list = self.trial_list_mid
					self.target_probability = self.target_prob_mid / self.target_prob_trial_num

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, 'Mid'
						])

				
				
				self.instruction_button.text = 'Press Here to Start'			
				
				# self.center_instr_image_path = str(self.image_folder / self.fribble_folder / self.target_image) + '.png'
				# self.center_instr_image = ImageButton(source=self.center_instr_image_path)
				self.center_instr_image.texture = self.image_dict[self.target_image].image.texture

				
				self.protocol_floatlayout.add_widget(self.center_instr_image)
				self.protocol_floatlayout.add_widget(self.section_instr_label)
				self.protocol_floatlayout.add_widget(self.instruction_button)
				
				self.protocol_floatlayout.add_event([
					(time.time() - self.start_time)
					, 'Object Display'
					, 'Image'
					, 'Block'
					, 'Instructions'
					, 'Type'
					, 'Target'
					])
				
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

				if self.current_stage == 'TarProb':
						
					self.block_max_count = len(self.target_prob_list)
					self.block_duration = self.block_duration_probe

					self.block_target_total = 1
					self.block_nontarget_total = 1
					self.block_false_alarms = 0
					self.block_hits = 0

					trial_multiplier = self.block_trial_max / self.target_prob_trial_num

					# if self.current_block == 0:

					# 	self.trial_list = ['Target']
					
					# else:

					self.target_prob_list_index = self.current_block - 1

					self.trial_list = list()
					self.target_probability = self.target_prob_list[self.target_prob_list_index] / self.target_prob_trial_num

					self.block_target_total = trial_multiplier * self.target_prob_list[self.target_prob_list_index]
					self.block_nontarget_total = self.block_trial_max - self.block_target_total

					for iTrial in range(self.target_prob_list[self.target_prob_list_index]):
						self.trial_list.append('Target')

					for iTrial in range((self.target_prob_trial_num - self.target_prob_list[self.target_prob_list_index])):
						self.trial_list.append('Nontarget')


					random.shuffle(self.trial_list)

					self.protocol_floatlayout.add_event([
						(self.stimulus_start_time - self.start_time)
						, 'Variable Change'
						, 'Parameter'
						, 'Trial List'
						, self.current_stage
						, 'Probability'
						, self.target_prob_list[self.target_prob_list_index]
						])
				
				self.printlog('Else: Block Screen')
				self.block_screen()
			

			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Variable Change'
				, 'Parameter'
				, 'Stimulus Duration'
				, str(self.stimdur_current_frames)
				, 'Type'
				, 'Staircasing'
				, 'Units'
				, 'Frames'
				])

			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Variable Change'
				, 'Parameter'
				, 'Stimulus Duration'
				, str(self.stimdur_current_frames * self.frame_duration)
				, 'Type'
				, 'Staircasing'
				, 'Units'
				, 'Frames'
				])
			
			self.protocol_floatlayout.add_event([
				(time.time() - self.start_time)
				, 'Variable Change'
				, 'Outcome'
				, 'Limited Hold'
				, str(self.limhold)
				, 'Type'
				, 'Staircasing'
				, 'Units'
				, 'Seconds'
				])
			

			self.current_hits = 0
			self.last_response = 0
			self.contingency = 0
			self.trial_outcome = 0
			self.current_block_trial = 0
			self.trial_index = -1

			if self.current_stage == 'Training':
				
				self.response_tracking = [0, 0]
			
			else:
				
				self.response_tracking = [-2,-2]
			
			random.shuffle(self.trial_list)
			self.printlog('Trial list: ', self.trial_list)
			
			
			self.block_start_time = time.time()
			
			self.protocol_floatlayout.add_event([
				(self.block_start_time - self.start_time)
				, 'Variable Change'
				, 'Parameter'
				, 'Block Start Time'
				, str(self.block_start_time)
				])
			
			
			self.printlog('Block contingency end')

			if 'Blur_Scaling' in self.stage_list \
				or self.current_stage == 'Blur':

				self.blur_preload_start_event()
			
			else:
				
				self.trial_contingency_event()
				
			
			#self.present_instructions(self.stage_instructions)
			
	# 		self.current_block += 1
		
		
		except KeyboardInterrupt:
			
			self.printlog('Program terminated by user.')
			
			self.protocol_end()
		
# 		except:
# 			
# 			self.printlog('Error; program terminated.')
# 			
# 			self.protocol_end()
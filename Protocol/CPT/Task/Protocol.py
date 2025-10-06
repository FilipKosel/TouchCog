# Imports #

import configparser
import numpy as np
import pandas as pd
import pathlib
import random
import statistics
import time
from collections import Counter

from Classes.Protocol import ImageButton, ProtocolBase

from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.button import Button
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.video import Video




class ProtocolScreen(ProtocolBase):

	def __init__(self, **kwargs):

		super(ProtocolScreen, self).__init__(**kwargs)
		self.protocol_name = 'CPT'
		self.name = self.protocol_name + '_protocolscreen'
		self.update_task()
		
		# Define Data Columns

		self.data_cols = [
			'TrialNo'
			, 'Stage'
			, 'Substage'
			, 'TarProb_Probe'
			, 'Block'
			, 'CurrentBlockTrial'
			, 'Stimulus'
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
			, 'skip_tutorial_video'
			, 'tutorial_video_duration'
			, 'block_change_on_duration_only'
			, 'training_task'
			, 'similarity_scaling'
			, 'limdur_scaling'
			, 'noise_scaling'
			, 'blur_scaling'
			, 'noise_probe'
			, 'blur_probe'
			, 'stimdur_probe'
			, 'flanker_probe'
			, 'tarprob_probe'
			, 'sart_probe'
			, 'iti_fixed_or_range'
			, 'iti_length'
			, 'stimulus_duration'
			, 'feedback_length'
			, 'block_duration-staircase'
			, 'block_duration-probe'
			, 'block_min_rest_duration'
			, 'session_duration'
			, 'block_multiplier'
			, 'block_trial_max'
			, 'training_block_max_correct'
			, 'target_prob_over_num_trials'
			, 'target_prob_list'
			, 'target_prob_similarity'
			, 'target_prob_flanker'
			, 'stimulus_family'
			, 'display_stimulus_outline'
			, 'mask_during_limhold'
			, 'limhold_mask_type'
			, 'similarity_percentile_initial'
			, 'similarity_percentile_range'
			, 'staircase_stimdur_min_frames'
			]
		
		# Define Variables - Config Import
		
		self.config_path = str(pathlib.Path('Protocol', self.protocol_name, 'Configuration.ini'))
		self.config_file = configparser.ConfigParser()
		self.config_file.read(self.config_path)

		self.debug_mode = False

		if ('DebugParameters' in self.config_file) \
			and self.config_file.getboolean('DebugParameters', 'debug_mode'):

			self.parameters_dict = self.config_file['DebugParameters']
			self.debug_mode = True
		
		else:
			self.parameters_dict = self.config_file['TaskParameters']
			self.debug_mode = False
	
	def _load_config_parameters(self, parameters_dict):
		
		self.participant_id = parameters_dict['participant_id']
		
		self.language = parameters_dict['language']

		self.skip_tutorial_video = parameters_dict['skip_tutorial_video']
		self.tutorial_video_duration = float(parameters_dict['tutorial_video_duration'])

		self.block_change_on_duration = parameters_dict['block_change_on_duration_only']
		
		self.iti_fixed_or_range = parameters_dict['iti_fixed_or_range']
		
		
		self.iti_temp = parameters_dict['iti_length']
		self.iti_temp = self.iti_temp.split(',')
		
		self.stimdur_import = parameters_dict['stimulus_duration']
		self.stimdur_import = self.stimdur_import.split(',')
		
		self.feedback_length = float(parameters_dict['feedback_length'])
		self.block_duration_staircase = int(parameters_dict['block_duration-staircase'])
		self.block_duration_probe = int(parameters_dict['block_duration-probe'])
		self.block_min_rest_duration = float(parameters_dict['block_min_rest_duration'])
		self.session_duration = float(parameters_dict['session_duration'])
		
		self.block_multiplier = int(parameters_dict['block_multiplier'])
		self.block_trial_max = int(parameters_dict['block_trial_max'])
		self.training_block_max_correct = int(parameters_dict['training_block_max_correct'])

		self.target_prob_trial_num = int(parameters_dict['target_prob_over_num_trials'])
		
		self.target_prob_import = parameters_dict['target_prob_list']
		self.target_prob_import = self.target_prob_import.split(',')
		
		self.target_prob_base = round(self.target_prob_trial_num * float(parameters_dict['target_prob_base']))
		self.target_prob_sim = round(self.target_prob_trial_num * float(parameters_dict['target_prob_similarity']))
		self.target_prob_flanker = round(self.target_prob_trial_num * float(parameters_dict['target_prob_flanker']))
		
		self.stimulus_family = parameters_dict['stimulus_family']

		self.display_stimulus_outline = int(parameters_dict['display_stimulus_outline'])
		self.mask_during_limhold = int(parameters_dict['mask_during_limhold'])
		self.limhold_mask_type = parameters_dict['limhold_mask_type']

		self.similarity_percentile_initial = float(parameters_dict['similarity_percentile_initial'])
		self.similarity_percentile_range = float(parameters_dict['similarity_percentile_range'])

		self.staircase_stimdur_frame_min = float(parameters_dict['staircase_stimdur_min_frames'])
		self.staircase_stimdur_seconds_max = float(parameters_dict['staircase_stimdur_max_seconds'])
		
		self.hold_image = self.config_file['Hold']['hold_image']
		self.mask_image = self.config_file['Mask']['mask_image']
		
		
		# Create stage list and import stage parameters
		
		self.stage_list = list()
		
		if parameters_dict['training_task']:
			self.stage_list.append('Training')

		if parameters_dict['limdur_scaling']:
			self.stage_list.append('LimDur_Scaling')

		if parameters_dict['similarity_scaling']:
			self.stage_list.append('Similarity_Scaling')
			self.stimulus_family = 'Fb'
		
		else:
			self.stimulus_family = parameters_dict['stimulus_family']

		if parameters_dict['noise_scaling'] \
			and 'Similarity_Scaling' not in self.stage_list:
			self.stage_list.append('Noise_Scaling')

		if parameters_dict['blur_scaling'] \
			and 'Similarity_Scaling' not in self.stage_list:
			self.stage_list.append('Blur_Scaling')

		if parameters_dict['noise_probe']:
			self.stage_list.append('Noise_Probe')

		if parameters_dict['blur_probe']:
			self.stage_list.append('Blur_Probe')

		if parameters_dict['stimdur_probe']:
			self.stage_list.append('StimDur_Probe')

		if parameters_dict['flanker_probe']:
			self.stage_list.append('Flanker_Probe')

		if parameters_dict['tarprob_probe']:
			self.stage_list.append('TarProb_Probe')

		if parameters_dict['sart_probe']:
			self.stage_list.append('SART_Probe')
	
	def _load_task_variables(self):
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
		
		self.stimulus_on_screen = False
		self.limhold_started = False
		self.response_made = False
		self.hold_active = False
		self.stimulus_mask_on_screen = True
		self.training_complete = False
		
		# Define Variables - Count
		
		self.current_block = -1
		self.current_block_trial = 0

		self.current_hits = 0
		
		self.stage_index = -1
		self.trial_index = 0
		
		self.block_max_count = self.block_multiplier

		self.trial_outcome = 0 # 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Correct, no center tap,6-Incorrect, no center tap
		self.contingency = 0
		self.response = 0

		self.target_probability = 1.0

		self.block_target_total = 0
		self.block_false_alarms = 0
		self.block_hits = 0
		
		
		# Define Variables - Staircasing
		
		self.last_response = 0
		
		self.response_tracking = list()
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
		self.current_stage = ''
		
		
		# Define Variables - Time
		
		self.stimulus_start_time = 0.0
		self.response_latency = 0.0
		self.stimulus_press_latency = 0.0
		self.movement_latency = 0.0
		self.frame_duration = 1/self.maxfps
		self.stimdur_actual = 0.0
		self.trial_end_time = 0.0

		self.stimulus_image_proportion = 0.35
		self.instruction_image_proportion = 0.25

	def _load_staircase_variables(self):
		self.staircase_stimdur_frame_max = self.staircase_stimdur_seconds_max/self.frame_duration

		self.iti_temp = [float(iNum) for iNum in self.iti_temp]
		self.iti_frame_range = sorted((np.array(self.iti_temp) // self.frame_duration).tolist(), reverse=True)
		self.iti_frame_range = [int(iNum) for iNum in self.iti_frame_range]
		self.iti_length = self.iti_frame_range[0] * self.frame_duration
		
		self.stimdur_import = [float(iNum) for iNum in self.stimdur_import]

		stimdur_frame_steps = np.round(np.array(self.stimdur_import) / self.frame_duration, decimals=0)
		
		if 0 in stimdur_frame_steps:
			stimdur_frame_steps += 1

		self.stimdur_frames = sorted(stimdur_frame_steps.tolist(), reverse=True)
		self.stimdur_index = 0

		self.stimdur_current_frames = self.stimdur_frames[self.stimdur_index]
		self.stimdur = self.stimdur_current_frames * self.frame_duration

		if self.staircase_stimdur_frame_min < 1:
			self.staircase_stimdur_frame_min = 1

		self.stimdur_base = self.stimdur_current_frames
		self.stimdur_change = self.stimdur_current_frames

		self.limhold = self.stimdur
		self.limhold_base = self.limhold
		
		self.stimdur_use_steps = True

		
	def _setup_session_stages(self):
		# General properties
		self.trial_list = list()
		self.trial_list_base = list()

		self.target_prob_list = [int(float(iProb) * self.target_prob_trial_num) for iProb in self.target_prob_import]
		self.target_prob_list = self.constrained_shuffle(self.target_prob_list, max_run=3)

		self.nontarget_prob_base = self.target_prob_trial_num - self.target_prob_base
		
		for iTrial in range(self.target_prob_base):
			self.trial_list_base.append('Target')
		
		for iTrial in range(self.nontarget_prob_base):
			self.trial_list_base.append('Nontarget')
		
		self.trial_list_base = self.constrained_shuffle(self.trial_list_base, max_run=3)
		
		self.trial_list = self.trial_list_base
		# print('Trial list mid prob: ', self.trial_list)
		
		if 'Similarity_Scaling' in self.stage_list:
			self.trial_list_sim = list()
			self.nontarget_prob_sim = self.target_prob_trial_num - self.target_prob_sim
		
			for iTrial in range(self.target_prob_sim):
				self.trial_list_sim.append('Target')
				
			for iTrial in range(self.nontarget_prob_sim):
				self.trial_list_sim.append('Nontarget')
			
			self.trial_list_sim = self.constrained_shuffle(self.trial_list_sim, max_run=3)
		
		if 'SART_Probe' in self.stage_list:
			self.trial_list_SART = list()
			self.nontarget_prob_SART = max(self.target_prob_list)
			self.target_prob_SART = self.target_prob_trial_num - self.nontarget_prob_SART
		
			for iTrial in range(self.target_prob_SART):
				self.trial_list_SART.append('Target')
				
			for iTrial in range(self.nontarget_prob_SART):
				self.trial_list_SART.append('Nontarget')
			
			self.trial_list_SART = self.constrained_shuffle(self.trial_list_SART, max_run=3)
		
		if 'Flanker_Probe' in self.stage_list:
			self.trial_list_flanker = list()
			self.nontarget_prob_flanker = self.target_prob_trial_num - self.target_prob_flanker
		
			for iTrial in range(self.target_prob_flanker):
				self.trial_list_flanker.append('Target')
				
			for iTrial in range(self.nontarget_prob_flanker):
				self.trial_list_flanker.append('Nontarget')
			
			self.trial_list_flanker = self.constrained_shuffle(self.trial_list_flanker, max_run=3)
			
			self.flanker_stage_index = 0
			self.flanker_stage_list = ['none', 'same', 'diff', 'none', 'same', 'diff']
			self.flanker_stage_list = self.constrained_shuffle(self.flanker_stage_list, max_run=3)
			self.current_substage = ''
			self.flanker_image = ''
	
	def _setup_image_widgets(self):
		# Set images
		self.image_folder = pathlib.Path('Protocol', self.protocol_name, 'Image')

		self.mask_image_path = str(self.image_folder / str(self.mask_image + '.png'))

		self.fribble_folder = pathlib.Path('Fribbles', self.stimulus_family)

		self.stimulus_image_path_list = sorted(list(self.image_folder.glob(str(self.fribble_folder / '*.png'))))

		if 'Similarity_Scaling' in self.stage_list:
			self.similarity_data = pd.read_csv(str(self.image_folder / self.fribble_folder / str(self.stimulus_family + '-SSIM_Data.csv')))

			stimulus_list = list(self.similarity_data.columns)
			stimulus_list.remove('Nontarget')
			# print('\n\nStimulus list: ', stimulus_list, '\n\n')
			self.target_image = random.choice(stimulus_list)
			# print('Target image: ', self.target_image)

			self.similarity_data = self.similarity_data.loc[:, ['Nontarget', self.target_image]]

			self.similarity_data = self.similarity_data.drop(
				self.similarity_data[
					self.similarity_data['Nontarget'] == self.target_image
					].index
				)

			self.similarity_data = self.similarity_data.sort_values(by=self.target_image, ascending=True)

			self.nontarget_images = self.similarity_data['Nontarget'].tolist()

			self.similarity_index_range = int(len(self.nontarget_images) * (self.similarity_percentile_range/100))

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
			# print(self.current_nontarget_image_list)

			self.current_similarity = 1.00

		else:
			stimulus_image_list = list()

			for filename in self.stimulus_image_path_list:
				stimulus_image_list.append(filename.stem)

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

			self.nontarget_images.sort()
			self.current_nontarget_image_list = self.nontarget_images

		total_image_list = self.stimulus_image_path_list

		# Staircasing - Noise Masks

		self.noise_mask_index = 0

		self.noise_mask_paths = sorted(list(self.image_folder.glob('Noise_Masks-Circle/*.png')))
		self.noise_mask_list = list()

		for filename in self.noise_mask_paths:
			self.noise_mask_list.append(filename.stem)

		self.noise_mask_value = self.noise_mask_list[self.noise_mask_index]

		total_image_list += self.noise_mask_paths

		# GUI Parameters
		self.stimulus_image_size = ((self.stimulus_image_proportion * self.width_adjust), (self.stimulus_image_proportion * self.height_adjust))
		self.instruction_image_size = ((self.instruction_image_proportion * self.width_adjust), (self.instruction_image_proportion * self.height_adjust))
		self.stimulus_mask_size = (self.stimulus_image_size[0] * 1.2, self.stimulus_image_size[1] * 1.2)
		self.text_button_size = [0.4, 0.15]

		self.stimulus_pos_C = {"center_x": 0.50, "center_y": 0.5}
		self.stimulus_pos_L = {"center_x": 0.20, "center_y": 0.5}
		self.stimulus_pos_R = {"center_x": 0.80, "center_y": 0.5}

		self.instruction_image_pos_C = {"center_x": 0.50, "center_y": 0.75}

		self.text_button_pos_UC = {"center_x": 0.50, "center_y": 0.92}
		self.text_button_pos_LL = {"center_x": 0.25, "center_y": 0.08}
		self.text_button_pos_LR = {"center_x": 0.75, "center_y": 0.08}

		# Load images

		self.hold_image_path = str(self.image_folder / (self.hold_image + '.png'))
		self.mask_image_path = str(self.image_folder / (self.mask_image + '.png'))
		self.outline_mask_path = str(self.image_folder / 'whitecircle.png')

		total_image_list += [self.hold_image_path, self.mask_image_path]
		self.load_images(total_image_list)

		# Create ImageButton Widgets
		# Define Widgets - Images

		self.tutorial_stimulus_image = ImageButton(source=str(self.image_folder / self.fribble_folder / (self.target_image + '.png')))
		
		self.hold_button.source = self.hold_image_path
		self.hold_button.bind(on_press=self.iti_start)
		self.hold_button.unbind(on_release=self.hold_remind)
		self.hold_button.bind(on_release=self.premature_response)
		
		self.img_stimulus_C = ImageButton()
		self.img_stimulus_C.size_hint = self.stimulus_image_size
		self.img_stimulus_C.pos_hint = self.stimulus_pos_C
		self.img_stimulus_C.bind(on_press=self.center_pressed)
		self.img_stimulus_C.name = 'Center Stimulus'

		self.img_stimulus_L = ImageButton(source=self.mask_image_path)
		self.img_stimulus_L.size_hint = self.stimulus_image_size
		self.img_stimulus_L.pos_hint = self.stimulus_pos_L
		
		self.img_stimulus_R = ImageButton(source=self.mask_image_path)
		self.img_stimulus_R.size_hint = self.stimulus_image_size
		self.img_stimulus_R.pos_hint = self.stimulus_pos_R

		self.center_instr_image = ImageButton(source=self.mask_image_path)
		self.center_instr_image.size_hint = self.instruction_image_size
		self.center_instr_image.pos_hint = self.instruction_image_pos_C

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


		if any(True for stage in ['Blur_Scaling', 'Blur_Probe'] if stage in self.stage_list):
			self.blur_widget = EffectWidget()
			self.blur_widget.effects = [HorizontalBlurEffect(size=self.blur_level), VerticalBlurEffect(size=self.blur_level)]
	

	def _setup_language_localization(self):		
		self.set_language(self.language)
		self.stage_instructions = ''

	def _load_video_and_instruction_components(self):

		# Instruction Import

		self.lang_folder_path = pathlib.Path('Protocol', self.protocol_name, 'Language', self.language)


		if (self.lang_folder_path / 'Tutorial_Video').is_dir():
			self.tutorial_video_path = str(list((self.lang_folder_path / 'Tutorial_Video').glob('*.mp4'))[0])

			self.tutorial_video = Video(
				source = self.tutorial_video_path
				)

			self.tutorial_video.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
			self.tutorial_video.size_hint = (1, 1)

		# Define Instruction Components
		
		# Instruction - Dictionary
		
		self.instruction_path = str(self.lang_folder_path / 'Instructions.ini')
		
		self.instruction_config = configparser.ConfigParser(allow_no_value = True)
		self.instruction_config.read(self.instruction_path, encoding = 'utf-8')
		
		self.instruction_dict = {}
		self.instruction_dict['Training'] = {}
		self.instruction_dict['LimDur_Scaling'] = {}
		self.instruction_dict['Similarity_Scaling'] = {}
		self.instruction_dict['Noise_Scaling'] = {}
		self.instruction_dict['Blur_Scaling'] = {}
		self.instruction_dict['Noise_Probe'] = {}
		self.instruction_dict['Blur_Probe'] = {}
		self.instruction_dict['StimDur_Probe'] = {}
		self.instruction_dict['TarProb_Probe'] = {}
		self.instruction_dict['Flanker_Probe'] = {}
		self.instruction_dict['SART_Probe'] = {}
		
		for stage in self.stage_list:
			
			self.instruction_dict[stage]['train'] = self.instruction_config[stage]['train']
			self.instruction_dict[stage]['task'] = self.instruction_config[stage]['task']


		feedback_lang_path = str(self.lang_folder_path / 'Feedback.ini')
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

		# Instruction - ImageButton
		self.tutorial_stimulus_image = ImageButton(source=str(self.image_folder / self.fribble_folder / (self.target_image + '.png')))
		self.tutorial_outline = ImageButton(source=self.outline_mask_path)
		self.tutorial_checkmark = ImageButton(source=str(self.image_folder / 'checkmark.png'))
		self.tutorial_continue = Button(text='CONTINUE', font_size='48sp')
		self.tutorial_continue.bind(on_press=self.tutorial_target_present_screen)
		self.tutorial_restart = Button(text='RESTART VIDEO', font_size='48sp')
		self.tutorial_restart.bind(on_press=self.start_tutorial_video)
		self.tutorial_start_button = Button(text='START TASK', font_size='48sp')
		self.tutorial_start_button.bind(on_press=self.start_protocol_from_tutorial)
		self.tutorial_video_button = Button(text='TAP THE SCREEN\nTO START VIDEO', font_size='48sp', halign='center', valign='center')
		self.tutorial_video_button.background_color = 'black'
		self.tutorial_video_button.bind(on_press=self.start_tutorial_video)
		
		
		# Instruction - Text Widget
		self.section_instr_string = ''
		self.section_instr_label = Label(text=self.section_instr_string, font_size='44sp', markup=True)
		self.section_instr_label.size_hint = {0.58, 0.7}
		self.section_instr_label.pos_hint = {'center_x': 0.5, 'center_y': 0.35}
		
		# Instruction - Button Widget
		
		self.instruction_button = Button(font_size='60sp')
		self.instruction_button.size_hint = self.text_button_size
		self.instruction_button.pos_hint = self.text_button_pos_UC
		self.instruction_button.text = ''
		self.instruction_button.bind(on_press=self.section_start)
		self.instruction_button_str = ''
		
		
		# Stage Results - Text Widget
		
		self.stage_results_label = Label(text='', font_size='48sp', markup=True)
		self.stage_results_label.size_hint = (0.85, 0.8)
		self.stage_results_label.pos_hint = {'center_x': 0.5, 'center_y': 0.35}
		
		
		# Stage Results - Button Widget
		
		self.continue_button.font_size = '60sp'
		self.continue_button.size_hint = self.text_button_size
		self.continue_button.pos_hint = self.text_button_pos_UC
		
		self.stage_continue_button = Button(font_size='60sp')
		self.stage_continue_button.size_hint = self.text_button_size
		self.stage_continue_button.pos_hint = self.text_button_pos_UC
		self.stage_continue_button.text = 'CONTINUE'
		self.stage_continue_button.bind(on_press=self.block_contingency)
		
		self.session_end_button = Button(font_size='60sp')
		self.session_end_button.size_hint = self.text_button_size
		self.session_end_button.pos_hint = self.text_button_pos_LL
		self.session_end_button.text = 'END SESSION'
		self.session_end_button.bind(on_press=self.protocol_end)
		
		
		self.protocol_floatlayout.clear_widgets()
		
		
	def load_parameters(self, parameters_dict):
		self.parameters_dict = parameters_dict
		self._load_config_parameters(self.parameters_dict)
		self._load_task_variables()
		self._load_staircase_variables()
		self._setup_session_stages()
		self._setup_image_widgets()
		self._setup_language_localization()
		self._load_video_and_instruction_components()

		self.start_clock()
		if (self.lang_folder_path / 'Tutorial_Video').is_dir() \
			and not self.skip_tutorial_video:

			self.protocol_floatlayout.clear_widgets()
			self.present_tutorial_video()
		
		else:
			self.present_instructions()


	# Protocol Staging

	def present_tutorial_video(self, *args):

		self.protocol_floatlayout.clear_widgets()

		self.tutorial_stimulus_image.size_hint = self.stimulus_image_size
		self.tutorial_stimulus_image.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
		self.tutorial_outline.size_hint = self.stimulus_mask_size
		self.tutorial_outline.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
		self.tutorial_checkmark.size_hint = ((0.2 * self.width_adjust), (0.2 * self.height_adjust))
		self.tutorial_checkmark.pos_hint = {'center_x': 0.52, 'center_y': 0.9}
		self.tutorial_continue.size_hint = self.text_button_size
		self.tutorial_continue.pos_hint = self.text_button_pos_LR
		self.tutorial_restart.size_hint = self.text_button_size
		self.tutorial_restart.pos_hint = self.text_button_pos_LL
		self.tutorial_start_button.size_hint = self.text_button_size
		self.tutorial_start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.3}
		self.tutorial_video_button.size_hint = (1, 1)
		self.tutorial_video_button.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
			
		self.protocol_floatlayout.add_stage_event('Object Display')

		self.protocol_floatlayout.add_widget(self.tutorial_video)
		self.protocol_floatlayout.add_widget(self.tutorial_video_button)

		self.tutorial_video.state = 'stop'
		return
	

	def start_tutorial_video(self, *args):

		self.tutorial_video.state = 'play'
		self.protocol_floatlayout.remove_widget(self.tutorial_video_button)

		self.tutorial_video_end_event = Clock.schedule_once(self.present_tutorial_video_start_button, self.tutorial_video_duration)
		self.protocol_floatlayout.add_object_event('Display', 'Video', 'Section', 'Instructions')
		return


	def present_tutorial_video_start_button(self, *args):

		self.protocol_floatlayout.add_widget(self.tutorial_continue)
		self.protocol_floatlayout.add_widget(self.tutorial_restart)
		return


	def tutorial_target_present_screen(self, *args):

		self.tutorial_video.state = 'stop'

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_widget(self.tutorial_checkmark)
		self.protocol_floatlayout.add_widget(self.tutorial_stimulus_image)
		self.protocol_floatlayout.add_widget(self.tutorial_outline)
		self.protocol_floatlayout.add_widget(self.tutorial_start_button)
		return



	def start_protocol_from_tutorial(self, *args):

		self.protocol_floatlayout.clear_widgets()

		self.generate_output_files()
		self.metadata_output_generation()

		self.block_contingency()
		return



	def blur_preload_start(self, *args):

		self.img_stimulus_C.texture = self.image_dict[self.mask_image].image.texture

		self.protocol_floatlayout.add_widget(self.blur_widget)
		self.blur_widget.add_widget(self.img_stimulus_C)

		self.blur_preload_end()



	def blur_preload_end(self, *args):
		self.protocol_floatlayout.remove_widget(self.blur_widget)
		self.blur_widget.remove_widget(self.img_stimulus_C)

		self.trial_contingency()



	def stimulus_present(self, *args): # Present stimulus
		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur_Probe':

			self.blur_widget.add_widget(self.img_stimulus_C)
			self.protocol_floatlayout.add_widget(self.img_noise_C)
			
			self.protocol_floatlayout.add_object_event('Display', 'Mask', 'Noise', 'Center', self.noise_mask_value)
		else:
			
			self.protocol_floatlayout.add_widget(self.img_stimulus_C)

		self.stimulus_start_time = time.perf_counter()
		
		self.stimulus_on_screen = True

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise_Probe':

			self.protocol_floatlayout.add_widget(self.img_noise_C)

			self.protocol_floatlayout.add_object_event('Display', 'Mask', 'Noise', 'Center', self.noise_mask_value)
		

		if self.display_stimulus_outline == 1:
			
			self.protocol_floatlayout.add_widget(self.img_outline_C)
			
			self.protocol_floatlayout.add_object_event('Display', 'Mask', 'Outline', 'Center', self.display_stimulus_outline)
		

		if self.current_stage == 'Flanker_Probe':
			
			self.protocol_floatlayout.add_widget(self.img_stimulus_L)
			self.protocol_floatlayout.add_widget(self.img_stimulus_R)
            
			self.protocol_floatlayout.add_object_event('Display', 'Stimulus', 'Flanker', 'Left', self.img_stimulus_L)
			self.protocol_floatlayout.add_object_event('Display', 'Stimulus', 'Flanker', 'Right', self.img_stimulus_R)


		Clock.schedule_once(self.stimulus_end, self.stimdur)

		Clock.schedule_once(self.center_notpressed, self.limhold)



	def stimulus_end(self, *args): # Remove stimulus

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur_Probe':

			self.protocol_floatlayout.remove_widget(self.blur_widget)
			self.blur_widget.remove_widget(self.img_stimulus_C)
		
		else:
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C)

		self.protocol_floatlayout.add_stage_event('Object Remove')

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise_Probe':

			self.protocol_floatlayout.remove_widget(self.img_noise_C)
			self.protocol_floatlayout.add_object_event('Remove', 'Mask', 'Noise', 'Center', self.noise_mask_value)


		if (self.mask_during_limhold == 1) \
			and (self.current_stage == 'StimDur_Probe'):
			
			self.protocol_floatlayout.remove_widget(self.img_outline_C)

			self.protocol_floatlayout.add_widget(self.img_stimulus_C_mask)
			self.protocol_floatlayout.add_widget(self.img_outline_C)

			self.stimulus_mask_on_screen = True

		self.stimdur_actual = time.perf_counter() - self.stimulus_start_time
		
		self.stimulus_on_screen = False
		self.limhold_started = True

		if self.current_stage == 'Flanker_Probe':
			
			self.protocol_floatlayout.remove_widget(self.img_stimulus_L)
			self.protocol_floatlayout.remove_widget(self.img_stimulus_R)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Flanker', 'Left', self.img_stimulus_L)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Flanker', 'Right', self.img_stimulus_R)



	def stimulus_presentation(self, *args): # Stimulus presentation by frame
		
		if not self.stimulus_on_screen \
			and not self.limhold_started:

			self.hold_active = True
		
			self.hold_button.unbind(on_press=self.iti_start)
			self.hold_button.unbind(on_release=self.premature_response)
			self.hold_button.bind(on_release=self.stimulus_response)
			
			self.stimulus_present()



	def premature_response(self, *args): # Trial Outcomes: 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Hit, no center touch,6-False Alarm, no center touch

		self.hold_button_pressed = False
		if self.stimulus_on_screen:
			return None
		
		self.contingency = 3
		self.response = 1
		self.trial_outcome = 0
		self.response_latency = np.nan
		self.stimulus_press_latency = np.nan
		self.movement_latency = np.nan

		self.feedback_label.text = ''
		
		self.protocol_floatlayout.add_stage_event('Premature Response')
		
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Contingency', self.contingency)
		
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Response', self.response)
		
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Outcome', self.trial_outcome)

		self.write_trial()

		self.iti_active = False

		self.feedback_label.text = self.feedback_dict['wait']
			
		if not self.feedback_on_screen:
			self.protocol_floatlayout.add_widget(self.feedback_label)

			self.feedback_start_time = time.perf_counter()
			self.feedback_on_screen = True

			self.protocol_floatlayout.add_object_event('Display', 'Text', 'Feedback', self.feedback_label.text)
		else:
			Clock.unschedule(self.remove_feedback)
		
		self.hold_button.unbind(on_release=self.premature_response)
		self.hold_button.bind(on_press=self.premature_resolved)

	def premature_resolved(self, *args):
		Clock.unschedule(self.remove_feedback)
		self.remove_feedback()
		self.hold_button_pressed = True
		self.hold_button.bind(on_release=self.premature_response)
		self.iti_start()
		return
	
	
	
	# Contingency Stages #
	# Tracks contingencies and outcomes based on removal of hold from hold_button
	def stimulus_response(self, *args): # Trial Outcomes: 0-Premature,1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Hit, no center press,6-False Alarm, no center press
										# Contingencies: 0: Incorrect; 1: Correct; 2: Response, no center touch; 3: Premature response

		self.response_time = time.perf_counter()
		self.response_latency = self.response_time - self.stimulus_start_time
		
		self.response_made = True
		self.hold_active = False

		self.protocol_floatlayout.add_stage_event('Stimulus Response')
		
		self.response = 1

		self.feedback_label.text = ''
		
		if (self.current_stage == 'SART_Probe'):

			if (self.center_image in self.current_nontarget_image_list):
				self.contingency = 2
				self.trial_outcome = 5
				
			else:
				self.contingency = 2
				self.trial_outcome = 6

		else:

			if (self.center_image == self.target_image):
				self.contingency = 2
				self.trial_outcome = 5
				
				if self.current_stage == 'LimDur_Scaling':
					self.feedback_label.text = self.feedback_dict['too_slow']
				
			else:
				self.contingency = 2
				self.trial_outcome = 6
		
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Response', str(self.response))
			
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Contingency', str(self.contingency))
		
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Outcome', str(self.trial_outcome))
		
		self.protocol_floatlayout.add_variable_event('Outcome','Response Latency', str(self.response_latency))
		
		self.hold_button.bind(on_press=self.response_cancelled)
		self.hold_button.unbind(on_release=self.stimulus_response)
	
	
	# Tracks contingencies based on responses direectly to the stimulus image
	def center_pressed(self, *args): # Trial Outcomes: 1-Hit,2-Miss,3-False Alarm,4-Correct Rejection,5-Premature,6-Dual Image, wrong side
		
		Clock.unschedule(self.stimulus_end)
		Clock.unschedule(self.center_notpressed)

		self.hold_active = False

		self.hold_button.unbind(on_press=self.response_cancelled)
		
		self.stimulus_press_time = time.perf_counter()
		self.stimulus_press_latency = self.stimulus_press_time - self.stimulus_start_time
		self.movement_latency = self.stimulus_press_latency - self.response_latency

		self.feedback_label.text = ''

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur_Probe':

			self.protocol_floatlayout.remove_widget(self.blur_widget)
			self.blur_widget.remove_widget(self.img_stimulus_C)
		
		else:
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C)


		if self.stimulus_mask_on_screen:
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C_mask)
			self.stimulus_mask_on_screen = False
		
		self.protocol_floatlayout.add_stage_event('Stimulus Press')
		
		self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Center', 'Center', self.center_image)

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise_Probe':
			
			self.protocol_floatlayout.remove_widget(self.img_noise_C)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Mask', 'Noise', 'Center', self.noise_mask_value)
		

		if self.display_stimulus_outline == 1:
			self.protocol_floatlayout.remove_widget(self.img_outline_C)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Mask', 'Outline', 'Center', self.display_stimulus_outline)
		
		
		if self.current_stage == 'Flanker_Probe':
			self.protocol_floatlayout.remove_widget(self.img_stimulus_L)
			self.protocol_floatlayout.remove_widget(self.img_stimulus_R)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Flanker', 'Left', self.img_stimulus_L)
			self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Flanker', 'Right', self.img_stimulus_R)
		
		self.stimulus_on_screen = False
		self.limhold_started = False
		self.response_made = False

		self.feedback_label.text = ''
		
		if (self.current_stage == 'SART_Probe'):

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

		self.protocol_floatlayout.add_variable_event('Outcome','Trial Response', str(self.response))
		
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Contingency', str(self.contingency))
		
		self.protocol_floatlayout.add_variable_event('Outcome','Trial Outcome', str(self.trial_outcome))
		
		self.protocol_floatlayout.add_variable_event('Outcome','Stimulus Press Latency', str(self.stimulus_press_latency))
		
		self.protocol_floatlayout.add_variable_event('Outcome','Movement Latency', str(self.movement_latency))
		
		if self.feedback_label.text != '' \
			and not self.feedback_on_screen:
			
			self.protocol_floatlayout.add_widget(self.feedback_label)

			self.feedback_start_time = time.perf_counter()
			self.feedback_on_screen = True

			self.protocol_floatlayout.add_object_event('Display', 'Text', 'Feedback', self.feedback_label.text)

		self.write_trial()

		self.hold_button.bind(on_press=self.iti_start)
		self.hold_button.bind(on_release=self.premature_response)

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur_Probe':

			self.blur_preload_start()
		
		else:
			self.trial_contingency()



	def center_notpressed(self, *args):

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur_Probe':

			self.protocol_floatlayout.remove_widget(self.blur_widget)
			self.blur_widget.remove_widget(self.img_stimulus_C)
		
		else:
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C)
		

		if self.stimulus_mask_on_screen:
			self.protocol_floatlayout.remove_widget(self.img_stimulus_C_mask)
			self.stimulus_mask_on_screen = False

		self.stimulus_press_time = np.nan
		self.stimulus_press_latency = np.nan
		self.movement_latency = np.nan
		
		self.protocol_floatlayout.add_stage_event('No Stimulus Press')
		
		self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Center', 'Center', self.center_image)

		if 'Noise_Scaling' in self.stage_list \
			or self.current_stage == 'Noise_Probe':
			
			self.protocol_floatlayout.remove_widget(self.img_noise_C)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Mask', 'Noise', 'Center', self.noise_mask_value)


		if self.display_stimulus_outline == 1:
			self.protocol_floatlayout.remove_widget(self.img_outline_C)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Mask', 'Outline', 'Center', self.display_stimulus_outline)
		
		
		if self.current_stage == 'Flanker_Probe':
			self.protocol_floatlayout.remove_widget(self.img_stimulus_L)
			self.protocol_floatlayout.remove_widget(self.img_stimulus_R)
			
			self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Flanker', 'Left', self.img_stimulus_L)
			self.protocol_floatlayout.add_object_event('Remove', 'Stimulus', 'Flanker', 'Right', self.img_stimulus_R)
		
		self.stimulus_on_screen = False
		self.limhold_started = False

		if not self.response_made:
			self.response = 0
			self.response_latency = np.nan

			self.feedback_label.text = ''
			
			if (self.current_stage == 'SART_Probe'):

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
					self.contingency = 0
					self.trial_outcome = 2

					if self.current_stage in ['Training', 'LimDur_Scaling', 'Similarity_Scaling', 'Blur_Scaling', 'Noise_Scaling', 'StimDur_Probe', 'Blur_Probe', 'Noise_Probe']:
						self.feedback_label.text = self.feedback_dict['miss']
				
				else:
					self.contingency = 1
					self.trial_outcome = 4

			self.protocol_floatlayout.add_variable_event('Outcome','Trial Response', str(self.response))
			
			self.protocol_floatlayout.add_variable_event('Outcome','Trial Contingency', str(self.contingency))
			
			self.protocol_floatlayout.add_variable_event('Outcome','Trial Outcome', str(self.trial_outcome))
			
			self.protocol_floatlayout.add_variable_event('Outcome','Stimulus Press Latency', str(self.stimulus_press_latency))
			
			self.protocol_floatlayout.add_variable_event('Outcome','Movement Latency', str(self.movement_latency))

			self.hold_button.unbind(on_release=self.stimulus_response)

		else:
			self.hold_button.unbind(on_press=self.response_cancelled)
			

		if self.feedback_label.text != '' \
			and not self.feedback_on_screen:
			
			self.protocol_floatlayout.add_widget(self.feedback_label)

			self.feedback_start_time = time.perf_counter()
			self.feedback_on_screen = True

			self.protocol_floatlayout.add_object_event('Display', 'Text', 'Feedback', self.feedback_label.text)

		self.response_made = False

		self.write_trial()

		self.hold_button.bind(on_press=self.iti_start)
		self.hold_button.bind(on_release=self.premature_response)

		if 'Blur_Scaling' in self.stage_list \
			or self.current_stage == 'Blur_Probe':

			self.blur_preload_start()
		
		else:
			self.trial_contingency()
	
	
	
	def response_cancelled(self, *args):
		
		if self.trial_outcome == 5:
			self.feedback_label.text = self.feedback_dict['miss']

		else:
			self.feedback_label.text = self.feedback_dict['abort']

		self.trial_outcome = 7

		self.hold_active = True
		
		self.center_notpressed()



	def hold_removed_stim(self, *args):
		
		self.hold_active = False
		
		self.protocol_floatlayout.add_stage_event('Hold Removed')



	def section_start(self, *args):

		self.protocol_floatlayout.clear_widgets()

		self.protocol_floatlayout.add_stage_event('Section Start')
		
		self.protocol_floatlayout.add_object_event('Remove', 'Text', 'Instructions', 'Section')
		
		self.protocol_floatlayout.add_object_event('Remove', 'Button', 'Continue', 'Section')
		
		self.trial_end_time = time.perf_counter()
		self.block_end()



	# Data Saving Functions #

	def write_trial(self, *args):		
		trial_data = [
			self.current_trial
			, self.current_stage
			, self.current_substage
			, self.target_probability
			, self.current_block
			, self.current_block_trial
			, self.center_image
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
			## ENCODE TRIAL OUTCOME AS last_response FOR EACH CONTINGENCY ##
			# Check that current block trial is not the first trial of the block
			if self.current_block_trial != 0:
				# Determine if the stage is Training or the first block index			
				if (self.current_stage == 'Training') \
					or (self.current_block == 0):
					#Encode previous trial as current hit=hit
					if self.trial_outcome == 1:
						self.last_response = 1
					
					else:
						self.last_response = 0
				
				# Check if stage is Similarity Scaling Task - Only CR gets a positive outcome. Miss FAR get negative. Everything else neutral
				elif self.current_stage == 'Similarity_Scaling':
					#Encode previous trial as current
					if self.trial_outcome == 4:
						self.last_response = 1
					# Encode last_response as -1 if trial outcome is a miss or false alarm
					elif self.trial_outcome in [2, 3]:
						self.last_response = -1
					# If not miss, false alarm, or correct rejection, encoded as 0
					else:
						self.last_response = 0
				
				# Check if stage is blur scaling, noise scaling, blur probe, or noise probe
				elif self.current_stage in ['Blur_Scaling', 'Noise_Scaling', 'Blur_Probe', 'Noise_Probe']:
					# Encode last_response as 1 if trial outcome is a hit
					if self.trial_outcome == 1:
						self.last_response = 1
					# Encode last_response as -1 if trial outcome is a miss or false alarm
					elif self.trial_outcome in [2, 3]:
						self.last_response = -1
					# If not miss, false alarm, or hit, encoded as 0
					else:
						self.last_response = 0
				
				# Check if stage is limited duration scaling
				elif self.current_stage == 'LimDur_Scaling':
					# Encode last_response as 1 if trial outcome is a hit
					if self.trial_outcome == 1:
						self.last_response = 1
					# Encode last_response as -1 if trial outcome is a miss, false alarm, hit no center, false alarm no center
					elif self.trial_outcome in [2, 3, 5, 6]:
						self.last_response = -1
					# Encode correct rejection as 0
					else:
						self.last_response = 0
				
				# Check if stage is stimulus duration probe
				elif self.current_stage == 'StimDur_Probe': # Counts if hit or lift for a hit. Negative if miss or FA with or without press.
					# Encode last_response as 1 if trial outcome is a hit or hit no center
					if self.trial_outcome in [1, 5]:
						self.last_response = 1
					# Encode last_response as -1 if trial outcome is a miss, false alarm, or false alarm no center
					elif self.trial_outcome in [2, 3, 6]:
						self.last_response = -1
					# Encode correct rejection as 0
					else:
						self.last_response = 0
				
				# Check if stage is target probability probe with target probability >= 75% or sustained attention to response task
				elif (self.current_stage == 'SART_Probe') \
					or ((self.current_stage == 'TarProb_Probe') and (self.target_probability >= 0.75)):
					# Encode last_response as 1 if trial outcome is a correct rejection
					if self.trial_outcome == 4:
						self.last_response = 1
					# Encode last_response as -1 if trial outcome is a false alarm or false alarm no center
					elif self.trial_outcome in [3, 6]:
						self.last_response = -1
					# If not false alarm or correct rejection, encoded as 0
					else:
						self.last_response = 0
				# Check for any other stage non-specific
				else:
					# Encode last_response as 1 if trial outcome is a hit
					if self.trial_outcome == 1:
						self.last_response = 1
					# Encode last_response as -1 if trial outcome is a false alarm or false alarm no center
					elif self.trial_outcome in [3, 6]:
						self.last_response = -1
					# If not false alarm or hit, encoded as 0
					else:
						self.last_response = 0
				
				self.protocol_floatlayout.add_variable_event('Outcome', 'Last Response', self.last_response)

				self.response_tracking.append(self.last_response)		
				# If current/last_response was equal to 1
				## CONDUCT STAIRCASE ADJUSTMENTS FOR POSITIVE OUTCOME ##
				if self.last_response == 1:

					self.protocol_floatlayout.add_variable_event('Parameter', 'Staircasing', 'Increase')
					# If the current stage is a similarity scaling probe
					if self.current_stage == 'Similarity_Scaling':
						# add current similarity to list of similarity tracking
						self.similarity_tracking.append(self.current_similarity)
						# If tracking list is greater than or equal to 20 trials and block change on duration is not equal to 1
						if len(self.similarity_tracking) >= 20 \
							and not self.block_change_on_duration:
							# If the length of similarity_tracking is equal to 0
							if len(self.similarity_tracking) == 0:
								# Take a float value of the similarity of the last nontarget image in the current nontarget image list
								self.outcome_value = float(
									self.similarity_data.loc[
										self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1]
										, self.target_image
										].to_numpy()
									)
								
							else:
								# Take the maximum value of the similarity tracking list
								self.outcome_value = max(self.similarity_tracking)
							# If the sum of the last 10 responses is less than or equal to 4 or the sum of the last 10 responses is greater than or equal to 6 and the mean of the last 10 similarity tracking values is greater than 0.90
							if (sum(self.response_tracking[-10:]) <= 4) \
								or ((sum(self.response_tracking[-10:] >= 6)) and (statistics.mean(self.similarity_tracking[-10:]) > 0.90)):
						
								self.protocol_floatlayout.add_variable_event('Outcome', 'Similarity', self.outcome_value, 'Mode')	
								baseline_nontarget_image_list = self.similarity_data.loc[
									(self.similarity_data[self.target_image] <= self.outcome_value)
									, 'Nontarget'
									].tolist()
								
								# If the length of the baseline nontarget image list is less than two times the similarity index range
								if len(baseline_nontarget_image_list) < (self.similarity_index_range * 2):
									self.current_nontarget_image_list = self.similarity_data.loc[0:(self.similarity_index_range * 2), 'Nontarget']

								else:
									self.current_nontarget_image_list = baseline_nontarget_image_list[-(self.similarity_index_range * 2):]
								
								self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])]),'Baseline', 'Min')

								self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])]), 'Baseline', 'Max')
								self.current_block += 1
								self.protocol_floatlayout.remove_widget(self.hold_button)
								self.stage_screen_start()

						self.similarity_index_min = int(self.nontarget_images.index(self.center_image))
						self.similarity_index_max = self.similarity_index_min + self.similarity_index_range

						if self.similarity_index_max >= len(self.nontarget_images):
							self.similarity_index_max = len(self.nontarget_images) - 1
							self.similarity_index_min = self.similarity_index_max - self.similarity_index_range

						self.current_nontarget_image_list = self.nontarget_images[self.similarity_index_min:self.similarity_index_max]
							
						self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])]),'Staircasing','Min')
						
						self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])]), 'Staircasing', 'Max')

					# Adjust Staircasing for Blur Scaling or Blur Probe
					elif self.current_stage in ['Blur_Scaling', 'Blur_Probe']:
						self.blur_tracking.append(self.blur_level)

						# If the length of the blur tracking list is greater than or equal to 20 and the difference between the maximum and minimum of the last 6 values in the blur tracking list is less than or equal to 2 and block change on duration is not equal to 1
						if (len(self.blur_tracking) >= 20) \
							and ((max(self.blur_tracking[-6:]) - min(self.blur_tracking[-6:])) <= 2) \
							and not self.block_change_on_duration:

							block_outcome = statistics.multimode(self.blur_tracking)

							# If the length of the block outcome is not equal to 1
							if len(block_outcome) != 1:
								self.outcome_value = max(block_outcome)

							else:
								self.outcome_value = int(block_outcome[0])

							self.protocol_floatlayout.add_variable_event('Outcome', 'Blur', self.outcome_value, 'Mode')

							# If the current stage is Blur Scaling
							if self.current_stage == 'Blur_Scaling':
								self.blur_base = int(self.outcome_value * 0.9)

								self.protocol_floatlayout.add_variable_event('Parameter', 'Blur', self.blur_base, 'Baseline')

							self.blur_tracking = list()
							self.last_response = 0
							self.current_block += 1
							self.protocol_floatlayout.remove_widget(self.hold_button)
							self.stage_screen_start()

						self.blur_level += self.blur_change

						self.protocol_floatlayout.add_variable_event('Parameter', 'Blur', self.blur_level, 'Staircasing')

						self.blur_widget.effects = [HorizontalBlurEffect(size=self.blur_level), VerticalBlurEffect(size=self.blur_level)]

					# Adjust Staircasing for Noise Scaling or Noise Probe
					elif self.current_stage in ['Noise_Scaling', 'Noise_Probe']:
						self.noise_tracking.append(int(self.noise_mask_value))

						# If the length of noise_tracking is greater than 20 and the difference between the maximum and minimum of the last 6 values in the noise tracking list is less than or equal to 15 and block change on duration is not equal to 1
						if len(self.noise_tracking) >= 20 \
							and ((max(self.noise_tracking[-6:]) - min(self.noise_tracking[-6:])) <= 15) \
							and not self.block_change_on_duration:

							block_outcome = statistics.multimode(self.noise_tracking) # Gets a vector of the most common values

							# If block_outcome has multiple mode values, take the maximum
							if len(block_outcome) != 1:
								self.outcome_value = max(block_outcome)
							
							else:
								self.outcome_value = float(block_outcome[0])

							self.protocol_floatlayout.add_variable_event('Outcome', 'Noise', self.outcome_value, 'Mode')
							
							# If the current stage is Noise Scaling
							if self.current_stage == 'Noise_Scaling':
								self.noise_base = int(self.outcome_value) - 10

								# Ensure noise base is not less than 0
								if self.noise_base < 0:
									self.noise_base = 0
								
								self.protocol_floatlayout.add_variable_event('Parameter', 'Noise', self.noise_base,'Baseline')

							self.noise_mask_index = round(self.noise_base/5) - 1

							# Ensure noise mask index is within bounds of noise mask list
							if self.noise_mask_index < 0:
								self.noise_mask_index = 0

							self.noise_tracking = list()
							
							self.last_response = 0
							self.current_block += 1
							self.protocol_floatlayout.remove_widget(self.hold_button)
							self.stage_screen_start()
						
						# If the noise mask index is less than the maximum index of the noise mask list
						if self.noise_mask_index < len(self.noise_mask_list) - 1:
							self.noise_mask_index += self.noise_mask_index_change

							# If the noise mask index is greater than the maximum index of the noise mask list
							if self.noise_mask_index >= len(self.noise_mask_list):
								self.noise_mask_index = len(self.noise_mask_list) - 1

							self.img_noise_C_path = str(self.noise_mask_paths[self.noise_mask_index])
							self.noise_mask_value = self.noise_mask_list[self.noise_mask_index]

						self.protocol_floatlayout.add_variable_event('Parameter', 'Noise', self.noise_mask_value, 'Staircasing')

						self.img_noise_C.texture = self.image_dict[self.noise_mask_value].image.texture

					# Adjust Staircasing for Limited Duration Scaling or Stimulus Duration Probe
					elif self.current_stage in ['LimDur_Scaling', 'StimDur_Probe']:
						self.stimdur_frame_tracking.append(self.stimdur_current_frames)

						# If the length of stimdur_frame_tracking is greater than 20 and the difference between the maximum and minimum of the last 10 values in the stimdur_frame_tracking list is less than or equal to 12 and block change on duration is not equal to 1
						if (len(self.stimdur_frame_tracking) > 20) \
							and ((max(self.stimdur_frame_tracking[-10:]) - min(self.stimdur_frame_tracking[-10:])) <= 12) \
							and not self.block_change_on_duration:

							block_outcome = statistics.multimode(self.stimdur_frame_tracking)

							# If the length of stimdur_frame_tracking is equal to 0
							if len(self.stimdur_frame_tracking) == 0:
								self.outcome_value = 240

							# If the length of block_outcome is equal to 0
							elif len(block_outcome) == 0:
								self.outcome_value = min(self.stimdur_frame_tracking)

							# If block_outcome has multiple mode values, take the minimum. Outcome value mapped twice if == 0
							elif len(block_outcome) != 1:
								self.outcome_value = min(block_outcome)
							
							else:
								self.outcome_value = float(block_outcome[0])

							# If current stage is Limited Duration Scaling
							if self.current_stage == 'LimDur_Scaling':
								self.stimdur_base = self.outcome_value + round(0.100/self.frame_duration)

								# Ensure stimdur_base is not greater than the maximum stimdur frame value
								if self.stimdur_base > self.staircase_stimdur_frame_max:
									self.stimdur_base = self.staircase_stimdur_frame_max

								self.limhold_base = self.stimdur_base * self.frame_duration

								self.limhold = self.limhold_base
								
								self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', self.outcome_value, 'Mode', 'Frames')

								self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', str(self.outcome_value * self.frame_duration), 'Mode', 'Seconds')

								self.protocol_floatlayout.add_variable_event('Outcome', 'Limited Hold', str(self.outcome_value * self.frame_duration), 'Mode', 'Seconds')

								self.protocol_floatlayout.add_variable_event('Parameter', 'Stimulus Duration', self.stimdur_base, 'Baseline', 'Frames')

								self.protocol_floatlayout.add_variable_event('Parameter', 'Stimulus Duration', str(self.stimdur_base * self.frame_duration), 'Baseline', 'Seconds')

								self.protocol_floatlayout.add_variable_event('Parameter', 'Limited Hold', self.limhold, 'Baseline', 'Seconds')

							else:
								self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', self.outcome_value, 'Mode', 'Frames')
								self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', str(self.outcome_value * self.frame_duration), 'Mode', 'Seconds')

							self.stimdur_frame_tracking = list()
							
							self.last_response = 0
							self.current_block += 1
							self.protocol_floatlayout.remove_widget(self.hold_button)
							self.stage_screen_start() ##

						# If using steps and the stimdur index is less than the maximum index of the stimdur frames list
						elif (self.stimdur_use_steps) \
							and (self.stimdur_index < len(self.stimdur_frames) - 1):
							
							self.stimdur_index += 1
							self.stimdur_current_frames = self.stimdur_frames[self.stimdur_index]
							self.stimdur_change = self.stimdur_frames[self.stimdur_index - 1] - self.stimdur_frames[self.stimdur_index]
						
						# If not using steps
						else:
							
							if (len(self.response_tracking) >= 3) \
								and (sum(self.response_tracking[-3:]) == 3) \
								and (self.stimdur_current_frames > min(self.stimdur_frames)):

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
						
						self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', self.outcome_value, 'Staircasing', 'Frames')
						self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', str(self.outcome_value * self.frame_duration), 'Staircasing', 'Seconds')

						if self.current_stage == 'LimDur_Scaling':
							self.limhold = self.stimdur_current_frames * self.frame_duration

							self.protocol_floatlayout.add_variable_event('Outcome', 'Limited Hold', self.limhold, 'Staircasing', 'Seconds')
				
				# If current/last_response was equal to -1
				## CONDUCT STAIRCASE ADJUSTMENTS FOR NEGATIVE OUTCOME ##
				elif self.last_response == -1:
					self.protocol_floatlayout.add_variable_event('Parameter', 'Staircasing', 'Decrease')

					# If the current stage is a similarity scaling probe
					if self.current_stage == 'Similarity_Scaling':
						# if center image is not equal to target image
						if self.center_image != self.target_image:
							self.similarity_index_max = int(self.nontarget_images.index(self.center_image))
							self.similarity_index_min = self.similarity_index_max - self.similarity_index_range
						
						else:
							self.similarity_index_max -= int(self.similarity_index_range//2)
							self.similarity_index_min = self.similarity_index_max - self.similarity_index_range
						
						# Ensure similarity index min and max are within bounds of nontarget images list
						if self.similarity_index_min < 0:
							self.similarity_index_min = 0
							self.similarity_index_max = self.similarity_index_range

						self.current_nontarget_image_list = self.nontarget_images[self.similarity_index_min:self.similarity_index_max]
							
						self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])]),'Staircasing','Min')

						self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])]),'Staircasing', 'Max')

					# Adjust Staircasing for Blur Scaling or Blur Probe
					elif self.current_stage in ['Blur_Scaling', 'Blur_Probe']:

						# If the length of the response tracking list is greater than or equal to 2 and the second to last response was a correct response
						if (len(self.response_tracking) >= 2) \
							and (self.response_tracking[-2] in [0, 1]):

							# If the blur change is greater than 1
							if self.blur_change > 1:
								self.blur_change //= 2 # Integer division to ensure blur change is an integer
								# Ensure blur change is not less than 1
								if self.blur_change < 1:
									self.blur_change = 1

						self.blur_level -= self.blur_change

						# Ensure blur level is not less than 0
						if self.blur_level < 0:
							self.blur_level = 0

						self.protocol_floatlayout.add_variable_event('Parameter', 'Blur', self.blur_level, 'Staircasing')

						self.blur_widget.effects = [HorizontalBlurEffect(size=self.blur_level), VerticalBlurEffect(size=self.blur_level)]

					# Adjust Staircasing for Noise Scaling or Noise Probe
					if self.current_stage in ['Noise_Scaling', 'Noise_Probe']:

						# If the length of the response tracking list is greater than or equal to 2 and the second to last response was a correct response
						if (len(self.response_tracking) >= 2) \
							and (self.response_tracking[-2] in [0, 1]):

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
						
						self.protocol_floatlayout.add_variable_event('Parameter', 'Noise', self.noise_mask_value, 'Staircasing')
					
					# Adjust Staircasing for Limited Duration Scaling or Stimulus Duration Probe
					elif self.current_stage in ['LimDur_Scaling', 'StimDur_Probe']:
						self.stimdur_use_steps = False
						
						# If the length of the response tracking list is greater than or equal to 2 and the second to last response was a correct response
						if (len(self.response_tracking) >= 2) \
							and (self.response_tracking[-2] in [0, 1]):
							
							self.stimdur_change //= 2
							
							if self.stimdur_change < 1:
								self.stimdur_change = 1
						
						self.stimdur_current_frames += self.stimdur_change

						# Ensure stimdur current frames is not greater than the base stimdur or the limited hold duration
						if (self.stimdur_current_frames > self.stimdur_base) \
							or (self.stimdur_current_frames > (self.limhold_base/self.frame_duration)):

							# If the base stimdur is greater than the limited hold duration divided by the frame duration
							if self.stimdur_base > (self.limhold_base/self.frame_duration):
								self.stimdur_current_frames = (self.limhold_base/self.frame_duration)
							
							else:
								self.stimdur_current_frames = self.stimdur_base
						
						self.protocol_floatlayout.add_variable_event('Outcome','Stimulus Duration', self.outcome_value,
												   'Staircasing','Frames')
						self.protocol_floatlayout.add_variable_event('Outcome','Stimulus Duration',str(self.outcome_value * self.frame_duration),
												   'Staircasing','Seconds')

						if self.current_stage == 'LimDur_Scaling':
							self.limhold = self.stimdur_current_frames * self.frame_duration
							
							self.protocol_floatlayout.add_variable_event('Outcome','Limited Hold', self.limhold,
													   'Staircasing','Seconds')

			## SET NEXT TRIAL PARAMETERS ##

			# Trial number and trial index

			self.current_trial += 1
			self.current_block_trial += 1
		
			self.protocol_floatlayout.add_variable_event('Parameter','Current Trial', self.current_trial)
			self.protocol_floatlayout.add_variable_event('Parameter','Current Block Trial', self.current_block_trial)

			# ITI - SET VALUE
			
			if len(self.iti_frame_range) > 1:
				# Randomly select ITI length from range of frames
				if self.iti_fixed_or_range == 'fixed':
					self.iti_length = random.choice(self.iti_frame_range) * self.frame_duration
				# Randomly select ITI length from range of frames
				else:
					self.iti_length = random.randint(min(self.iti_frame_range), max(self.iti_frame_range)) * self.frame_duration
				
				self.protocol_floatlayout.add_variable_event('Parameter', 'Current ITI', self.iti_length, 'Seconds')

			# Stimulus duration/limited hold frames
			# If first block of training, set stimdur to base value
			if self.current_block == 0:				
				self.stimdur_current_frames = self.stimdur_base
			
				self.protocol_floatlayout.add_variable_event('Outcome','Stimulus Duration', self.outcome_value,'Training','Frames')
				self.protocol_floatlayout.add_variable_event('Outcome','Stimulus Duration',str(self.outcome_value * self.frame_duration),'Training','Seconds')
			# If Limited Duration Scaling stage, set limhold to stimdur
			if self.current_stage == 'LimDur_Scaling':
				self.limhold = self.stimdur_current_frames * self.frame_duration
				self.protocol_floatlayout.add_variable_event('Outcome','Limited Hold', self.limhold,'Training','Seconds')

			self.stimdur = self.stimdur_current_frames * self.frame_duration

			# Ensure limhold is not less than stimdur
			if self.stimdur > self.limhold:
				self.limhold = self.stimdur

			# Set next trial type and stimulus
			
			# SART miss (nontarget + no response)
			if (self.contingency == 0) \
				and (self.response == 0) \
				and (self.current_stage == 'SART_Probe'):
				self.protocol_floatlayout.add_variable_event('Parameter','Stimulus', self.center_image,'SART Correction')
			
			# Premature response
			elif self.contingency == 3:
				self.protocol_floatlayout.add_variable_event('Parameter','Stimulus', self.center_image,'Premature')

			# Hit or miss
			else: # Set next stimulus image
				self.trial_index += 1
				
				# If trial index is greater than or equal to the length of the trial list, reshuffle and reset index
				if self.trial_index >= len(self.trial_list):
					self.trial_list = self.constrained_shuffle(self.trial_list, max_run=3)
					self.trial_index = 0
				
				self.protocol_floatlayout.add_variable_event('Parameter','Trial Index', self.trial_index)

				self.protocol_floatlayout.add_variable_event('Parameter','Trial Type', self.trial_list[self.trial_index])
				
				# Set center stimulus image and similarity value
				if self.trial_list[self.trial_index] == 'Target':
					self.center_image = self.target_image
					self.current_similarity = 1.00
				
				else:
					self.center_image = random.choice(self.current_nontarget_image_list)

					if self.current_stage == 'Similarity_Scaling':

						self.current_similarity = float(self.similarity_data.loc[
								self.similarity_data['Nontarget'] == self.center_image
								, self.target_image
								].to_numpy())
				
				self.img_stimulus_C_image_path = str(self.image_folder / self.center_image) + '.png'
				self.img_stimulus_C.texture = self.image_dict[self.center_image].image.texture

				self.protocol_floatlayout.add_variable_event('Parameter','Stimulus', self.center_image,'Novel')

			# Flanker probe - set flankers

			if self.current_stage == 'Flanker_Probe':
				
				if self.flanker_stage_index >= len(self.flanker_stage_list):
					self.flanker_stage_list = self.constrained_shuffle(self.flanker_stage_list, max_run=3)
					self.flanker_stage_index = 0
				
				self.current_substage = self.flanker_stage_list[self.flanker_stage_index]

				self.flanker_stage_index += 1
				
				if self.current_substage == 'none':
					self.flanker_image = 'black'
					
					self.protocol_floatlayout.add_variable_event('Parameter', 'Flanker', self.flanker_image, 'Blank')

				elif self.current_substage == 'same':
					self.flanker_image = self.center_image
					
					self.protocol_floatlayout.add_variable_event('Parameter', 'Flanker', self.flanker_image, 'Congruent')
				
				elif self.current_substage == 'diff':
					
					if self.trial_list[self.trial_index] == 'Target':
						self.flanker_image = random.choice(self.current_nontarget_image_list)
					
					else:
						self.flanker_image = self.target_image

					self.protocol_floatlayout.add_variable_event('Parameter', 'Flanker', self.flanker_image, 'Incongruent')

				self.img_stimulus_L.texture = self.image_dict[self.flanker_image].image.texture
				self.img_stimulus_R.texture = self.image_dict[self.flanker_image].image.texture			
			
			self.last_response = 0
			self.trial_outcome = 0

			if self.trial_list[self.trial_index] == 'Target':
				self.block_target_total += 1
			
			# Over session length/duration?
			
			if (self.current_stage == 'Training') \
				and (sum(self.response_tracking) >= self.training_block_max_correct):

				self.protocol_floatlayout.add_stage_event('Block End')
				
				self.hold_button.unbind(on_release=self.stimulus_response)
				self.contingency = 0
				self.trial_outcome = 0
				self.last_response = 0
				self.current_block += 1

				self.protocol_floatlayout.remove_widget(self.hold_button)
				
				self.block_contingency()
			
			elif (self.current_trial > self.session_trial_max) \
				or ((time.perf_counter() - self.start_time) >= self.session_length_max):

				self.protocol_floatlayout.add_stage_event('Session End')

				self.hold_button.unbind(on_release=self.stimulus_response)
				self.session_event.cancel()
				self.protocol_end()
			
			# Over block length/duration?
			
			elif (self.current_block_trial > self.block_trial_max) \
				or ((time.perf_counter() - self.block_start) >= self.block_duration):

				self.protocol_floatlayout.add_stage_event('Block End')
				
				self.hold_button.unbind(on_release=self.stimulus_response)
				self.contingency = 0
				self.trial_outcome = 0
				self.last_response = 0
				
				if self.current_stage == 'Similarity_Scaling':

					if len(self.similarity_tracking) == 0:
						self.outcome_value = float(
							self.similarity_data.loc[
								self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1]
								, self.target_image
								].to_numpy()
							)
					
					else:
						self.outcome_value = max(self.similarity_tracking)

					self.protocol_floatlayout.add_variable_event('Outcome', 'Similarity', self.outcome_value, 'Mode')

					baseline_nontarget_image_list = self.similarity_data.loc[
						(self.similarity_data[self.target_image] <= self.outcome_value)
						, 'Nontarget'
						].tolist()
					
					self.current_nontarget_image_list = baseline_nontarget_image_list[-self.similarity_index_range:]
					
					self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[0])]), 'Baseline', 'Min')
					
					self.protocol_floatlayout.add_variable_event('Parameter', 'Similarity', str(self.similarity_data.loc[(self.similarity_data['Nontarget'] == self.current_nontarget_image_list[-1])]), 'Baseline', 'Max')

					self.similarity_tracking = list()

				elif self.current_stage in ['Blur_Scaling', 'Blur_Probe']:
					block_outcome = statistics.multimode(self.blur_tracking)

					if len(block_outcome) == 0:
						self.outcome_value = 0

					elif len(block_outcome) != 1:
						self.outcome_value = max(block_outcome)

					else:
						self.outcome_value = float(block_outcome[0])

					self.protocol_floatlayout.add_variable_event('Outcome', 'Blur', self.outcome_value, 'Mode')

					self.blur_base = int(self.outcome_value * 0.9)

					self.protocol_floatlayout.add_variable_event('Parameter', 'Blur', self.blur_base, 'Baseline')

					self.blur_tracking = list()

				elif self.current_stage == 'Noise_Scaling':
					block_outcome = statistics.multimode(self.noise_tracking)

					if len(block_outcome) == 0:
						self.outcome_value = 0

					elif len(block_outcome) != 1:
						self.outcome_value = max(block_outcome)
					
					else:
						self.outcome_value = float(block_outcome[0])
					
					self.protocol_floatlayout.add_variable_event('Outcome', 'Noise', self.outcome_value, 'Mode')

					self.noise_base = int(self.outcome_value - 10)

					if self.noise_base < 0:
						self.noise_base = 0

					self.noise_mask_index = round(self.noise_base//5) - 1

					if self.noise_mask_index < 0:
						self.noise_mask_index = 0
					
					self.protocol_floatlayout.add_variable_event('Parameter', 'Noise', str(self.noise_base), 'Baseline')

					self.noise_tracking = list()

				elif self.current_stage == 'LimDur_Scaling':
					block_outcome = statistics.multimode(self.stimdur_frame_tracking)

					if len(self.stimdur_frame_tracking) == 0:
						self.outcome_value = 240

					elif len(block_outcome) == 0:
						self.outcome_value = min(self.stimdur_frame_tracking)

					elif len(block_outcome) != 1:
						self.outcome_value = min(block_outcome)
					
					else:
						self.outcome_value = int(block_outcome[0])
					
					self.stimdur_base = self.outcome_value + int(0.100/self.frame_duration)

					self.limhold_base = self.stimdur_base * self.frame_duration
					self.limhold = self.limhold_base
					
					self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', self.outcome_value,'Mode', 'Frames')
					
					self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', str(self.outcome_value * self.frame_duration), 'Mode', 'Seconds')
					
					self.protocol_floatlayout.add_variable_event('Outcome', 'Limited Hold', str(self.outcome_value * self.frame_duration),'Mode', 'Seconds')

					self.protocol_floatlayout.add_variable_event('Parameter', 'Stimulus Duration', self.stimdur_base, 'Baseline', 'Frames')

					self.protocol_floatlayout.add_variable_event('Parameter', 'Stimulus Duration', str(self.stimdur_base * self.frame_duration), 'Baseline', 'Seconds')

					self.protocol_floatlayout.add_variable_event('Parameter', 'Limited Hold', self.limhold, 'Baseline', 'Seconds')

					self.stimdur_frame_tracking = list()

				elif self.current_stage == 'Noise_Probe':
					block_outcome = statistics.multimode(self.noise_tracking)

					if len(block_outcome) == 0:
						self.outcome_value = 0

					elif len(block_outcome) != 1:
						self.outcome_value = max(block_outcome)
					
					else:
						self.outcome_value = float(block_outcome[0])
					
					self.protocol_floatlayout.add_variable_event('Outcome', 'Noise', self.outcome_value, 'Mode')
					
					self.noise_tracking = list()

				elif self.current_stage == 'StimDur_Probe':
					block_outcome = statistics.multimode(self.stimdur_frame_tracking)

					if len(self.stimdur_frame_tracking) == 0:
						self.outcome_value = self.stimdur_base

					elif len(block_outcome) == 0:
						self.outcome_value = min(self.stimdur_frame_tracking)

					elif len(block_outcome) != 1:
						self.outcome_value = min(block_outcome)
					
					else:
						self.outcome_value = int(block_outcome[0])

					self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', self.outcome_value, 'Mode', 'Frames')

					self.protocol_floatlayout.add_variable_event('Outcome', 'Stimulus Duration', str(self.outcome_value * self.frame_duration), 'Mode', 'Seconds')

					self.stimdur_frame_tracking = list()
				
				self.protocol_floatlayout.remove_widget(self.hold_button)
				
				if self.current_stage == 'Training':
					self.block_contingency()
					return

				else:
					self.current_block += 1
					self.start_stage_screen()
					return

			# print('Trial contingency end')

			self.trial_end_time = time.perf_counter()
			
			if self.hold_button_pressed == True:
				self.iti_start()
		
		
		except KeyboardInterrupt:
			
			print('Program terminated by user.')
			self.protocol_end()
		
		except:

			print('Error; program terminated by Trial Contingency.')
			self.protocol_end()

	def start_stage_screen(self, *args):
		self.protocol_floatlayout.add_stage_event('Stage End')

		Clock.unschedule(self.stimulus_end)
		Clock.unschedule(self.center_notpressed)
		Clock.unschedule(self.iti_end)

		self.protocol_floatlayout.clear_widgets()
		self.feedback_on_screen = False
			
		if self.current_stage == 'Similarity_Scaling':
			self.outcome_string = 'Great job!\n\nYou were able to correctly discriminate between stimuli\nwith ' + str(int(self.outcome_value*100)) + '%' + ' similarity.'
			
		elif self.current_stage in ['Blur_Scaling', 'Blur_Probe']:
			self.outcome_string = 'Great job!\n\nYou were able to correctly discriminate between stimuli\nwith ' + str(int(self.outcome_value)) + ' pixels of blur.'
			
		elif self.current_stage in ['Noise_Scaling', 'Noise_Probe']:
			self.outcome_string = 'Great job!\n\nYou were able to correctly identify stimuli with \n' + str(100 - self.outcome_value) + '%' + ' of the image visible.'

		elif self.current_stage == 'LimDur_Scaling':
			self.outcome_string = 'Great job!\n\nYou were able to correctly respond to stimuli\nwithin ' + str(round((self.outcome_value * self.frame_duration), 3)) + ' seconds.'
			
		elif self.current_stage == 'StimDur_Probe':
			self.outcome_string = 'Great job!\n\nYou were able to correctly identify stimuli presented\nfor ' + str(int(self.outcome_value)) + ' frames (' + str(round((self.outcome_value * self.frame_duration), 3)) + ' seconds).'

		elif self.current_stage in ['TarProb_Probe', 'Flanker_Probe']:

			if self.block_target_total == 0:
				self.outcome_string = 'Great job!\n\n'
				
			else:
				self.hit_accuracy = (self.block_hits / self.block_target_total)
				self.outcome_string = 'Great job!\n\nYour accuracy on that block was ' + str(round(self.hit_accuracy, 2) * 100) + '%!\n\nYou made ' + str(self.block_false_alarms) + ' false alarms (responses to nontarget images).'
			
		else:
			self.outcome_string = "Great job!\n\n"


		if self.stage_index < len(self.stage_list):
			self.stage_string = 'Please press "CONTINUE" to start the next block.'

		else:
			self.stage_string = 'You have completed this task.\n\nPlease inform your researcher.' # 'Please press "END SESSION" to end the session.'
			self.session_end_button.pos_hint = self.text_button_pos_UC
			self.protocol_floatlayout.add_widget(self.session_end_button)
			
		self.stage_results_label.text = self.outcome_string + '\n\n' + self.stage_string
		self.protocol_floatlayout.add_widget(self.stage_results_label)
			
		self.protocol_floatlayout.add_object_event('Display', 'Text', 'Stage', 'Results')

		self.stage_screen_time = time.perf_counter()
		self.stage_screen_started = True
		self.block_started = True

		Clock.schedule_once(self.stage_screen_end, 1.0)

	def stage_screen_end(self, *args):
		self.stage_screen_started = False

		if self.stage_index < (len(self.stage_list)):
			self.protocol_floatlayout.add_widget(self.stage_continue_button)
				
			self.protocol_floatlayout.add_object_event('Display', 'Button', 'Stage', 'Continue')
	
	
	
	def block_contingency(self, *args):
		
		try:
			Clock.unschedule(self.stimulus_end)
			Clock.unschedule(self.center_notpressed)
			Clock.unschedule(self.iti_end)
		
			self.protocol_floatlayout.add_stage_event('Block Contingency')

			self.protocol_floatlayout.clear_widgets()
		
			self.protocol_floatlayout.add_stage_event('Screen Cleared')

			self.previous_stage = self.current_stage

			self.feedback_label.text = ''

			self.hold_active = False
			self.block_started = True
			
			# Advance to next stage if current block exceeds max blocks or is -1 (initial value)
			if (self.current_block > self.block_max_count) or (self.current_block == -1):
				self.stage_index += 1
				self.current_block = 1
	
				if self.stage_index >= len(self.stage_list): # Check if all stages complete
					self.protocol_end()

				else:
					self.current_stage = self.stage_list[self.stage_index]
					self.current_substage = ''
			
				self.protocol_floatlayout.add_stage_event(self.current_stage)
				
				self.trial_list = ['Target']

				self.stimdur_current_frames = self.stimdur_base

				# If blur scaling active, reset blur level to base
				if 'Blur_Scaling' in self.stage_list \
					or self.current_stage == 'Blur_Probe':

					self.blur_level = self.blur_base
				
				if self.current_stage == 'SART_Probe': # Set SART probe params
					self.current_block = 0
			
			
			if self.stage_index >= len(self.stage_list): # Check if all stages complete again
			
				self.protocol_floatlayout.add_stage_event('Protocol End')
				self.protocol_end()
			

			# If current stage is training and tutorial video has not been skipped and training not yet complete
			if (self.current_stage == 'Training') \
				and not self.skip_tutorial_video \
				and not self.training_complete:

				self.trial_list = ['Target']
				self.block_trial_max = 2*(self.training_block_max_correct)
				self.block_duration = 3*(self.block_trial_max)
				self.target_probability = 1.0

				self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				self.block_start = time.perf_counter()
				self.block_started = False
				self.training_complete = True

				self.hold_button.bind(on_press=self.iti_start)
				
				self.protocol_floatlayout.add_widget(self.hold_button)
				
				self.protocol_floatlayout.add_button_event('Displayed', 'Hold Button')

			# If current block is 0 (instructions for block 1)
			elif self.current_block == 0:
				self.block_trial_max = 2*(self.training_block_max_correct)
				self.block_duration = 3*(self.block_trial_max)
				self.section_instr_label.text = self.instruction_dict[str(self.current_stage)]['train']
				self.instruction_button.text = 'Begin Training Block'
				self.center_instr_image.texture = self.image_dict[self.target_image].image.texture
				
				self.protocol_floatlayout.add_widget(self.center_instr_image)
				self.protocol_floatlayout.add_widget(self.section_instr_label)
				self.protocol_floatlayout.add_widget(self.instruction_button)
				
				self.protocol_floatlayout.add_object_event('Display', 'Image', 'Block', 'Instructions', self.target_image)
				
				self.protocol_floatlayout.add_object_event('Display', 'Text', 'Block', 'Instructions')
				self.protocol_floatlayout.add_event([
					(time.perf_counter() - self.start_time),
					'Object Attribute',
					'Text',
					'Block',
					'Instructions',
					'Type',
					'Training'
				])
				
				self.protocol_floatlayout.add_object_event('Display', 'Button', 'Block', 'Instructions')
				self.protocol_floatlayout.add_event([
					(time.perf_counter() - self.start_time),
					'Object Attribute',
					'Button',
					'Block',
					'Instructions',
					'Type',
					'Continue'
				])
			
			# If current block is 1 (instructions for block 2+)
			elif self.current_block == 1:
				self.section_instr_label.text = self.instruction_dict[str(self.current_stage)]['task']
				
				self.block_trial_max = int(self.parameters_dict['block_trial_max'])
				self.block_duration = self.block_duration_staircase
				self.stimdur_current_frames = self.stimdur_base
				
				if self.current_stage == 'Training':
					self.trial_list = ['Target']
					self.block_trial_max = 2*(self.training_block_max_correct)
					self.block_duration = 3*(self.block_trial_max)
					self.target_probability = 1.0

					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				elif self.current_stage == 'Similarity_Scaling':
					self.trial_list = self.trial_list_sim
					self.target_probability = self.target_prob_sim / self.target_prob_trial_num

					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				elif self.current_stage in ['Blur_Scaling', 'Noise_Scaling', 'LimDur_Scaling', 'Noise_Probe', 'Blur_Probe', 'StimDur_Probe', 'MidProb']:
					self.trial_list = self.trial_list_base
					self.target_probability = self.target_prob_base / self.target_prob_trial_num

					if self.current_stage == 'MidProb':
						self.block_duration = self.block_duration_probe

					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				elif self.current_stage == 'Flanker_Probe':
					self.trial_list = self.trial_list_flanker
					self.target_probability = self.target_prob_sim / self.target_prob_trial_num

					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				elif self.current_stage == 'TarProb_Probe':
					self.block_max_count = len(self.target_prob_list)
					self.block_duration = self.block_duration_probe
					trial_multiplier = self.block_trial_max / self.target_prob_trial_num

					self.target_prob_list_index = self.current_block - 1
					self.trial_list = list()
					self.target_probability = self.target_prob_list[self.target_prob_list_index] / self.target_prob_trial_num

					self.block_target_total = trial_multiplier * self.target_prob_list[self.target_prob_list_index]

					for iTrial in range(self.target_prob_list[self.target_prob_list_index]):
						self.trial_list.append('Target')

					for iTrial in range((self.target_prob_trial_num - self.target_prob_list[self.target_prob_list_index])):
						self.trial_list.append('Nontarget')

					self.constrained_shuffle(self.trial_list)
					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				elif self.current_stage == 'SART_Probe':
					self.trial_list = self.trial_list_SART
					self.target_probability = self.target_prob_SART / self.target_prob_trial_num
					self.block_duration = self.block_duration_probe

					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				else:
					self.trial_list = self.trial_list_base
					self.target_probability = self.target_prob_base / self.target_prob_trial_num

					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)


				self.instruction_button.text = 'Press Here to Start'
				self.center_instr_image.texture = self.image_dict[self.target_image].image.texture
				
				self.protocol_floatlayout.add_widget(self.center_instr_image)
				self.protocol_floatlayout.add_widget(self.section_instr_label)
				self.protocol_floatlayout.add_widget(self.instruction_button)
				
				self.protocol_floatlayout.add_object_event('Display', 'Image', 'Block', 'Instructions', self.target_image)
				
				self.protocol_floatlayout.add_object_event('Display', 'Text', 'Block', 'Instructions')
				self.protocol_floatlayout.add_event([
					(time.perf_counter() - self.start_time),
					'Object Attribute',
					'Text',
					'Block',
					'Instructions',
					'Type',
					'Task'
				])
				
				self.protocol_floatlayout.add_object_event('Display', 'Button', 'Block', 'Instructions')
				self.protocol_floatlayout.add_event([
					(time.perf_counter() - self.start_time),
					'Object Attribute',
					'Button',
					'Block',
					'Instructions',
					'Type',
					'Continue'
				])
			# If current block is greater than 1 (normal task block)
			else:

				if self.current_stage == 'TarProb_Probe':
					self.block_max_count = len(self.target_prob_list)
					self.block_duration = self.block_duration_probe
					trial_multiplier = self.block_trial_max / self.target_prob_trial_num

					self.target_prob_list_index = self.current_block - 1
					self.trial_list = list()
					self.target_probability = self.target_prob_list[self.target_prob_list_index] / self.target_prob_trial_num

					self.block_target_total = trial_multiplier * self.target_prob_list[self.target_prob_list_index]

					for iTrial in range(self.target_prob_list[self.target_prob_list_index]):
						self.trial_list.append('Target')

					for iTrial in range((self.target_prob_trial_num - self.target_prob_list[self.target_prob_list_index])):
						self.trial_list.append('Nontarget')

					self.constrained_shuffle(self.trial_list)

					self.protocol_floatlayout.add_variable_event('Parameter', 'Trial List', self.current_stage, 'Probability', self.target_probability)
				
				self.block_started = False

			self.protocol_floatlayout.add_variable_event('Parameter', 'Stimulus Duration', str(self.stimdur_current_frames),'Staircasing', 'Frames')

			self.protocol_floatlayout.add_variable_event('Parameter', 'Stimulus Duration', str(self.stimdur_current_frames * self.frame_duration), 'Staircasing', 'Seconds')

			self.protocol_floatlayout.add_variable_event('Outcome', 'Limited Hold', str(self.limhold), 'Staircasing', 'Seconds')

			self.current_hits = 0
			self.last_response = 0
			self.contingency = 0
			self.trial_outcome = 0
			self.current_block_trial = 0
			self.trial_index = -1
			self.block_target_total = 0
			self.block_false_alarms = 0
			self.block_hits = 0

			self.response_tracking = list()
			
			self.constrained_shuffle(self.trial_list)

			self.block_start = time.perf_counter()
			
			self.protocol_floatlayout.add_variable_event('Parameter', 'Block Start Time', str(self.block_start))

			if 'Blur_Scaling' in self.stage_list \
				or self.current_stage == 'Blur_Probe':

				self.blur_preload_start()
			
			else:
				self.trial_contingency()
		

		except KeyboardInterrupt:
			
			print('Program terminated by user.')
			self.protocol_end()
		
		except:
			
			print('Error; program terminated from Block Contingency.')
			self.protocol_end()
# Imports #
import kivy
import zipimport
import sys
import os
import configparser
import time
import numpy as np
import random
import csv
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
#from win32api import GetSystemMetrics
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.screenmanager import ScreenManager, Screen
from functools import partial

class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.coord = None
        self.fit_mode = 'fill'
        self.press_x = 0
        self.press_y = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.press_x = touch.pos[0]
            self.press_y = touch.pos[1]
            return super(ImageButton, self).on_touch_down(touch)
        else:
            return False


class Protocol_Screen(Screen):
    def __init__(self,screen_resolution,**kwargs):
        super(Protocol_Screen,self).__init__(**kwargs)
        self.protocol_floatlayout = FloatLayout()
        self.add_widget(self.protocol_floatlayout)
        width  = screen_resolution[0]
        height = screen_resolution[1]
        self.size = screen_resolution
        self.protocol_floatlayout.size = screen_resolution

        if width > height:
            self.width_adjust = height / width
            self.height_adjust = 1
        elif height < width:
            self.width_adjust = 1
            self.height_adjust = width / height
        else:
            self.width_adjust = 1
            self.height_adjust = 1
        
        if sys.platform == 'linux' or sys.platform == 'darwin':
            self.folder_mod = '/'
        elif sys.platform == 'win32':
            self.folder_mod = '\\'

        # Define Variables - Folder Path
        self.image_folder = 'Protocol' + self.folder_mod + 'PAL' + self.folder_mod + 'Image' + self.folder_mod
        self.data_output_path = None

        # Define Variables - Config
        config_path = 'Protocol' + self.folder_mod + 'PAL' + self.folder_mod + 'Configuration.ini'
        config_file = configparser.ConfigParser()
        config_file.read(config_path)
        self.parameters_dict = config_file['TaskParameters']
        self.participant_id = 'Default'
        self.session_max_length = float(self.parameters_dict['session_length_max'])
        self.session_trial_max = int(self.parameters_dict['session_trial_max'])
        self.iti_length = float(self.parameters_dict['iti_length'])
        self.feedback_length = float(self.parameters_dict['feedback_length'])
        self.training_image = self.parameters_dict['training_image']
        self.training_image_incorrect = 'Grey'
        self.test_images = self.parameters_dict['test_images']
        self.test_images = self.test_images.split(',')
        self.l1_correct = self.parameters_dict['location_1_correct']
        self.l2_correct = self.parameters_dict['location_2_correct']
        self.l3_correct = self.parameters_dict['location_3_correct']
        self.block_length = int(self.parameters_dict['block_length'])
        self.block_count = int(self.parameters_dict['block_count'])
        self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
        self.hold_image = config_file['Hold']['hold_image']
        self.mask_image = config_file['Mask']['mask_image']
        self.paltype = 'dPAL'

        # Define Language
        self.language = 'English'
        lang_folder_path = 'Protocol' + self.folder_mod + 'PAL' + self.folder_mod + 'Language' + \
                           self.folder_mod + self.language + self.folder_mod
        start_path = lang_folder_path + 'Start.txt'
        start_open = open(start_path, 'r', encoding="utf-8")
        self.start_label_str = start_open.read()
        start_open.close()

        break_path = lang_folder_path + 'Break.txt'
        break_open = open(break_path, 'r', encoding="utf-8")
        self.break_label_str = break_open.read()
        break_open.close()

        end_path = lang_folder_path + 'End.txt'
        end_open = open(end_path, 'r', encoding="utf-8")
        self.end_label_str = end_open.read()
        end_open.close()

        button_lang_path = lang_folder_path + 'Button.ini'
        button_lang_config = configparser.ConfigParser()
        button_lang_config.read(button_lang_path, encoding="utf-8")

        self.start_button_label_str = button_lang_config['Button']['start']
        self.continue_button_label_str = button_lang_config['Button']['continue']
        self.return_button_label_str = button_lang_config['Button']['return']

        feedback_lang_path = lang_folder_path + 'Feedback.ini'
        feedback_lang_config = configparser.ConfigParser(allow_no_value=True)
        feedback_lang_config.read(feedback_lang_path, encoding="utf-8")

        self.stim_feedback_correct_str = feedback_lang_config['Stimulus']['correct']
        stim_feedback_correct_color = feedback_lang_config['Stimulus']['correct_colour']
        if stim_feedback_correct_color != '':
            color_text = '[color=%s]' % stim_feedback_correct_color
            self.stim_feedback_correct_str = color_text + self.stim_feedback_correct_str + '[/color]'

        self.stim_feedback_incorrect_str = feedback_lang_config['Stimulus']['incorrect']
        stim_feedback_incorrect_color = feedback_lang_config['Stimulus']['incorrect_colour']
        if stim_feedback_incorrect_color != '':
            color_text = '[color=%s]' % stim_feedback_incorrect_color
            self.stim_feedback_incorrect_str = color_text + self.stim_feedback_incorrect_str + '[/color]'

        self.hold_feedback_wait_str = feedback_lang_config['Hold']['wait']
        hold_feedback_wait_color = feedback_lang_config['Hold']['wait_colour']
        if hold_feedback_wait_color != '':
            color_text = '[color=%s]' % hold_feedback_wait_color
            self.hold_feedback_wait_str = color_text + self.hold_feedback_wait_str + '[/color]'

        self.hold_feedback_return_str = feedback_lang_config['Hold']['return']
        hold_feedback_return_color = feedback_lang_config['Hold']['return_colour']
        if hold_feedback_return_color != '':
            color_text = '[color=%s]' % hold_feedback_return_color
            self.hold_feedback_return_str = color_text + self.hold_feedback_return_str + '[/color]'
        # Define Variables - List
        self.stage_list = ['Training', 'Test']

        # Define Variables - Boolean
        self.stimulus_on_screen = False
        self.iti_active = False
        self.feedback_on_screen = False
        self.hold_active = True
        self.block_started = False
        self.correction_trial = True

        # Define Variables - Counter
        self.current_trial = 1
        self.current_correct = 0
        self.stage_index = 0
        self.current_block = 0

        # Define Variables - String
        self.correct_image = self.training_image
        self.incorrect_image = self.training_image_incorrect
        self.current_stage = self.stage_list[self.stage_index]
        self.feedback_string = ''

        # Define Variables - Time
        self.start_iti = 0
        self.start_time = 0
        self.current_time = 0
        self.start_stimulus = 0
        self.response_lat = 0

        # Define Variables - Trial Configuration
        self.trial_configuration = random.randint(1, 6)
        self.generate_trial_contingency(training=True)

        self.block_threshold = 10 + self.block_length

        # Define Widgets - Images
        self.hold_button_image_path = self.image_folder + self.hold_image + '.png'
        self.hold_button = ImageButton(source=self.hold_button_image_path)

        self.left_stimulus_image_path = self.image_folder + self.l1_image + '.png'
        self.left_stimulus = ImageButton(source=self.left_stimulus_image_path)

        self.center_stimulus_image_path = self.image_folder + self.l2_image + '.png'
        self.center_stimulus = ImageButton(source=self.left_stimulus_image_path)

        self.right_stimulus_image_path = self.image_folder + self.l3_image + '.png'
        self.right_stimulus = ImageButton(source=self.right_stimulus_image_path)

        # Define Widgets - Text
        self.instruction_label = Label(text=self.start_label_str
                                       , font_size='35sp')
        self.instruction_label.size_hint = (0.6, 0.4)
        self.instruction_label.pos_hint = {'center_x': 0.5, 'center_y': 0.3}

        self.block_label = Label(text=self.break_label_str, font_size='50sp')
        self.block_label.size_hint = (0.5, 0.3)
        self.block_label.pos_hint = {'center_x': 0.5, 'center_y': 0.3}

        self.end_label = Label(text=self.end_label_str)
        self.end_label.size_hint = (0.6, 0.4)
        self.end_label.pos_hint = {'center_x': 0.5, 'center_y': 0.3}

        self.feedback_string = ''
        self.feedback_label = Label(text=self.feedback_string, font_size='50sp', markup=True)
        self.feedback_label.size_hint = (0.7, 0.4)
        self.feedback_label.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Define Widgets - Buttons
        self.start_button = Button(text=self.start_button_label_str)
        self.start_button.size_hint = (0.1, 0.1)
        self.start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        self.start_button.bind(on_press=self.start_protocol)

        self.continue_button = Button(text=self.continue_button_label_str)
        self.continue_button.size_hint = (0.1, 0.1)
        self.continue_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        self.continue_button.bind(on_press=self.block_end)

        self.return_button = Button(text=self.return_button_label_str)
        self.return_button.size_hint = (0.1, 0.1)
        self.return_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        self.return_button.bind(on_press=self.return_to_main)

    # Initialization Functions #
        
    def load_parameters(self,parameter_dict):
        self.parameters_dict = parameter_dict
        config_path = 'Protocol' + self.folder_mod + 'PAL' + self.folder_mod + 'Configuration.ini'
        config_file = configparser.ConfigParser()
        config_file.read(config_path)

        if len(self.parameters_dict) == 0:
            self.parameters_dict = config_file['TaskParameters']
        else:
            self.participant_id = self.parameters_dict['participant_id']

            # Define Variables - Config
            self.session_max_length = float(self.parameters_dict['session_length_max'])
            self.session_trial_max = int(self.parameters_dict['session_trial_max'])
            self.iti_length = float(self.parameters_dict['iti_length'])
            self.feedback_length = float(self.parameters_dict['feedback_length'])
            self.training_image = self.parameters_dict['training_image']
            self.training_image_incorrect = 'Grey'
            self.test_images = self.parameters_dict['test_images']
            self.test_images = self.test_images.split(',')
            self.l1_correct = self.parameters_dict['location_1_correct']
            self.l2_correct = self.parameters_dict['location_2_correct']
            self.l3_correct = self.parameters_dict['location_3_correct']
            self.block_length = int(self.parameters_dict['block_length'])
            self.block_count = int(self.parameters_dict['block_count'])
            self.block_min_rest_duration = float(self.parameters_dict['block_min_rest_duration'])
            self.hold_image = config_file['Hold']['hold_image']
            self.mask_image = config_file['Mask']['mask_image']
            self.paltype = 'dPAL'


            # Define Language
            self.language = 'English'
            lang_folder_path = 'Protocol' + self.folder_mod + 'PAL' + self.folder_mod + 'Language' + \
                               self.folder_mod + self.language + self.folder_mod
            start_path = lang_folder_path + 'Start.txt'
            start_open = open(start_path, 'r', encoding="utf-8")
            self.start_label_str = start_open.read()
            start_open.close()

            break_path = lang_folder_path + 'Break.txt'
            break_open = open(break_path, 'r', encoding="utf-8")
            self.break_label_str = break_open.read()
            break_open.close()

            end_path = lang_folder_path + 'End.txt'
            end_open = open(end_path, 'r', encoding="utf-8")
            self.end_label_str = end_open.read()
            end_open.close()

            button_lang_path = lang_folder_path + 'Button.ini'
            button_lang_config = configparser.ConfigParser()
            button_lang_config.read(button_lang_path, encoding="utf-8")

            self.start_button_label_str = button_lang_config['Button']['start']
            self.continue_button_label_str = button_lang_config['Button']['continue']
            self.return_button_label_str = button_lang_config['Button']['return']

            feedback_lang_path = lang_folder_path + 'Feedback.ini'
            feedback_lang_config = configparser.ConfigParser(allow_no_value=True)
            feedback_lang_config.read(feedback_lang_path, encoding="utf-8")

            self.stim_feedback_correct_str = feedback_lang_config['Stimulus']['correct']
            stim_feedback_correct_color = feedback_lang_config['Stimulus']['correct_colour']
            if stim_feedback_correct_color != '':
                color_text = '[color=%s]' % stim_feedback_correct_color
                self.stim_feedback_correct_str = color_text + self.stim_feedback_correct_str + '[/color]'

            self.stim_feedback_incorrect_str = feedback_lang_config['Stimulus']['incorrect']
            stim_feedback_incorrect_color = feedback_lang_config['Stimulus']['incorrect_colour']
            if stim_feedback_incorrect_color != '':
                color_text = '[color=%s]' % stim_feedback_incorrect_color
                self.stim_feedback_incorrect_str = color_text + self.stim_feedback_incorrect_str + '[/color]'

            self.hold_feedback_wait_str = feedback_lang_config['Hold']['wait']
            hold_feedback_wait_color = feedback_lang_config['Hold']['wait_colour']
            if hold_feedback_wait_color != '':
                color_text = '[color=%s]' % hold_feedback_wait_color
                self.hold_feedback_wait_str = color_text + self.hold_feedback_wait_str + '[/color]'

            self.hold_feedback_return_str = feedback_lang_config['Hold']['return']
            hold_feedback_return_color = feedback_lang_config['Hold']['return_colour']
            if hold_feedback_return_color != '':
                color_text = '[color=%s]' % hold_feedback_return_color
                self.hold_feedback_return_str = color_text + self.hold_feedback_return_str + '[/color]'

            # Define Variables - List
            self.stage_list = ['Training', 'Test']

            # Define Variables - Boolean
            self.stimulus_on_screen = False
            self.iti_active = False
            self.feedback_on_screen = False
            self.hold_active = True
            self.block_started = False
            self.correction_trial = True

            # Define Variables - Counter
            self.current_trial = 1
            self.current_correct = 0
            self.stage_index = 0
            self.current_block = 0

            # Define Variables - String
            self.correct_image = self.training_image
            self.incorrect_image = self.training_image_incorrect
            self.current_stage = self.stage_list[self.stage_index]
            self.feedback_string = ''

            # Define Variables - Time
            self.start_iti = 0
            self.start_time = 0
            self.current_time = 0
            self.start_stimulus = 0
            self.response_lat = 0

            # Define Variables - Trial Configuration
            self.trial_configuration = random.randint(1, 6)
            self.generate_trial_contingency(training=True)

            self.block_threshold = 10 + self.block_length

            # Define Widgets - Images
            self.hold_button_image_path = self.image_folder + self.hold_image + '.png'
            self.hold_button = ImageButton(source=self.hold_button_image_path)
            self.hold_button.pos_hint = {"center_x": 0.5, "center_y": 0.1}

            self.left_stimulus_image_path = self.image_folder + self.l1_image + '.png'
            self.left_stimulus = ImageButton(source=self.left_stimulus_image_path)
            self.left_stimulus.pos_hint = {"center_x": 0.2, "center_y": 0.6}
            self.left_stimulus.bind(on_press=self.left_stimulus_pressed)

            self.center_stimulus_image_path = self.image_folder + self.l2_image + '.png'
            self.center_stimulus = ImageButton(source=self.left_stimulus_image_path)
            self.center_stimulus.pos_hint = {"center_x": 0.5, "center_y": 0.6}
            self.center_stimulus.bind(on_press=self.center_stimulus_pressed)

            self.right_stimulus_image_path = self.image_folder + self.l3_image + '.png'
            self.right_stimulus = ImageButton(source=self.right_stimulus_image_path)
            self.right_stimulus.width = self.right_stimulus.height
            self.right_stimulus.pos_hint = {"center_x": 0.8, "center_y": 0.6}
            self.right_stimulus.bind(on_press=self.right_stimulus_pressed)

            # Define Widgets - Text
            self.instruction_label = Label(text=self.start_label_str
                                           , font_size='35sp')
            self.instruction_label.size_hint = (0.6, 0.4)
            self.instruction_label.pos_hint = {'center_x': 0.5, 'center_y': 0.3}

            self.block_label = Label(text=self.break_label_str, font_size='50sp')
            self.block_label.size_hint = (0.5, 0.3)
            self.block_label.pos_hint = {'center_x': 0.5, 'center_y': 0.3}

            self.end_label = Label(text=self.end_label_str)
            self.end_label.size_hint = (0.6, 0.4)
            self.end_label.pos_hint = {'center_x': 0.5, 'center_y': 0.3}

            self.feedback_string = ''
            self.feedback_label = Label(text=self.feedback_string, font_size='50sp', markup=True)
            self.feedback_label.size_hint = (0.7, 0.4)
            self.feedback_label.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

            # Define Widgets - Buttons
            self.start_button = Button(text=self.start_button_label_str)
            self.start_button.size_hint = (0.1, 0.1)
            self.start_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
            self.start_button.bind(on_press=self.start_protocol)

            self.continue_button = Button(text=self.continue_button_label_str)
            self.continue_button.size_hint = (0.1, 0.1)
            self.continue_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
            self.continue_button.bind(on_press=self.block_end)

            self.return_button = Button(text=self.return_button_label_str)
            self.return_button.size_hint = (0.1, 0.1)
            self.return_button.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
            self.return_button.bind(on_press=self.return_to_main)

            self.present_instructions()
        
        
    def generate_trial_contingency(self,training=False):
        if not training and self.paltype == 'dPAL':
            if self.trial_configuration == 1:
                self.correct_location = 0
                self.incorrect_location = 1
                self.correct_image = self.l1_correct
                self.incorrect_image = self.l3_correct
                self.l1_image = self.correct_image
                self.l2_image = self.incorrect_image
                self.l3_image = self.mask_image
            elif self.trial_configuration == 2:
                self.correct_location = 0
                self.incorrect_location = 2
                self.correct_image = self.l1_correct
                self.incorrect_image = self.l2_correct
                self.l1_image = self.correct_image
                self.l3_image = self.incorrect_image
                self.l2_image = self.mask_image
            elif self.trial_configuration == 3:
                self.correct_location = 1
                self.incorrect_location = 0
                self.correct_image = self.l2_correct
                self.incorrect_image = self.l3_correct
                self.l2_image = self.correct_image
                self.l1_image = self.incorrect_image
                self.l3_image = self.mask_image
            elif self.trial_configuration == 4:
                self.correct_location = 1
                self.incorrect_location = 2
                self.correct_image = self.l2_correct
                self.incorrect_image = self.l1_correct
                self.l2_image = self.correct_image
                self.l3_image = self.incorrect_image
                self.l1_image = self.mask_image
            elif self.trial_configuration == 5:
                self.correct_location = 2
                self.incorrect_location = 0
                self.correct_image = self.l3_correct
                self.incorrect_image = self.l2_correct
                self.l3_image = self.correct_image
                self.l1_image = self.incorrect_image
                self.l2_image = self.mask_image
            elif self.trial_configuration == 6:
                self.correct_location = 2
                self.incorrect_location = 1
                self.correct_image = self.l3_correct
                self.incorrect_image = self.l1_correct
                self.l3_image = self.correct_image
                self.l2_image = self.incorrect_image
                self.l1_image = self.mask_image
        if not training and self.paltype == 'sPAL':
            if self.trial_configuration == 1:
                self.correct_location = 0
                self.incorrect_location = 1
                self.correct_image = self.l1_correct
                self.incorrect_image = self.l1_correct
                self.l1_image = self.correct_image
                self.l2_image = self.incorrect_image
                self.l3_image = self.mask_image
            elif self.trial_configuration == 2:
                self.correct_location = 0
                self.incorrect_location = 2
                self.correct_image = self.l1_correct
                self.incorrect_image = self.l1_correct
                self.l1_image = self.correct_image
                self.l3_image = self.incorrect_image
                self.l2_image = self.mask_image
            elif self.trial_configuration == 3:
                self.correct_location = 1
                self.incorrect_location = 0
                self.correct_image = self.l2_correct
                self.incorrect_image = self.l2_correct
                self.l2_image = self.correct_image
                self.l1_image = self.incorrect_image
                self.l3_image = self.mask_image
            elif self.trial_configuration == 4:
                self.correct_location = 1
                self.incorrect_location = 2
                self.correct_image = self.l2_correct
                self.incorrect_image = self.l2_correct
                self.l2_image = self.correct_image
                self.l3_image = self.incorrect_image
                self.l1_image = self.mask_image
            elif self.trial_configuration == 5:
                self.correct_location = 2
                self.incorrect_location = 0
                self.correct_image = self.l3_correct
                self.incorrect_image = self.l3_correct
                self.l3_image = self.correct_image
                self.l1_image = self.incorrect_image
                self.l2_image = self.mask_image
            elif self.trial_configuration == 6:
                self.correct_location = 2
                self.incorrect_location = 1
                self.correct_image = self.l3_correct
                self.incorrect_image = self.l3_correct
                self.l3_image = self.correct_image
                self.l2_image = self.incorrect_image
                self.l1_image = self.mask_image
        elif training == True:
            if self.trial_configuration == 1:
                self.correct_location = 0
                self.incorrect_location = 1
                self.correct_image = self.training_image
                self.incorrect_image = self.training_image_incorrect
                self.l1_image = self.correct_image
                self.l2_image = self.incorrect_image
                self.l3_image = self.mask_image
            elif self.trial_configuration == 2:
                self.correct_location = 0
                self.incorrect_location = 2
                self.correct_image = self.training_image
                self.incorrect_image = self.training_image_incorrect
                self.l1_image = self.correct_image
                self.l3_image = self.incorrect_image
                self.l2_image = self.mask_image
            elif self.trial_configuration == 3:
                self.correct_location = 1
                self.incorrect_location = 0
                self.correct_image = self.training_image
                self.incorrect_image = self.training_image_incorrect
                self.l2_image = self.correct_image
                self.l1_image = self.incorrect_image
                self.l3_image = self.mask_image
            elif self.trial_configuration == 4:
                self.correct_location = 1
                self.incorrect_location = 2
                self.correct_image = self.training_image
                self.incorrect_image = self.training_image_incorrect
                self.l2_image = self.correct_image
                self.l3_image = self.incorrect_image
                self.l1_image = self.mask_image
            elif self.trial_configuration == 5:
                self.correct_location = 2
                self.incorrect_location = 0
                self.correct_image = self.training_image
                self.incorrect_image = self.training_image_incorrect
                self.l3_image = self.correct_image
                self.l1_image = self.incorrect_image
                self.l2_image = self.mask_image
            elif self.trial_configuration == 6:
                self.correct_location = 2
                self.incorrect_location = 1
                self.correct_image = self.training_image
                self.incorrect_image = self.training_image_incorrect
                self.l3_image = self.correct_image
                self.l2_image = self.incorrect_image
                self.l1_image = self.mask_image
                
        self.left_stimulus_image_path = self.image_folder + self.l1_image + '.png'
        self.center_stimulus_image_path = self.image_folder + self.l2_image + '.png'
        self.right_stimulus_image_path = self.image_folder + self.l3_image + '.png'
    def generate_output_files(self):
        folder_path = 'Data' + self.folder_mod + self.participant_id
        if os.path.exists(folder_path) == False:
            os.makedirs(folder_path)
        folder_list = os.listdir(folder_path)
        file_index = 1
        temp_filename = self.participant_id + '_PAL_' + str(file_index) + '.csv'
        self.file_path = folder_path + self.folder_mod + temp_filename
        while os.path.isfile(self.file_path):
            file_index += 1
            temp_filename = self.participant_id + '_PAL_' + str(file_index) + '.csv'
            self.file_path = folder_path + self.folder_mod + temp_filename
        data_cols = 'TrialNo,Current Stage,Correct Image,Incorrect Image,Correct Location,Incorrect Location,Correction Trial,Location Chosen,Correct,Response Latency'
        self.data_file = open(self.file_path, "w+")
        self.data_file.write(data_cols)
        self.data_file.close()
        
    def metadata_output_generation(self):
        folder_path = 'Data' + self.folder_mod + self.participant_id
        metadata_rows = ['participant_id','training_image','test_images',
                         'iti_length', 'block_length','block_count',
                         'location_1_correct','location_2_correct','location_3_correct',
                         'session_length_max','session_trial_max','paltype']
    
        
        meta_list = list()
        for meta_row in metadata_rows:
            row_list = list()
            row_list.append(meta_row)
            row_list.append(str(self.parameters_dict[meta_row]))
            meta_list.append(row_list)
        
        file_index = 1
        meta_output_filename = self.participant_id + '_PAL_Metadata_' + str(file_index) + '.csv'
        meta_output_path = folder_path + self.folder_mod + meta_output_filename
        while os.path.isfile(meta_output_path):
            file_index += 1
            meta_output_filename = self.participant_id + '_PAL_Metadata_' + str(file_index) + '.csv'
            meta_output_path = folder_path + self.folder_mod + meta_output_filename
        
        meta_colnames = ['Parameter','Value']
        
        with open(meta_output_path,'w') as meta_output_file:
            csv_writer = csv.writer(meta_output_file,delimiter=',')
            csv_writer.writerow(meta_colnames)
            for meta_param in meta_list:
                csv_writer.writerow(meta_param)
                

    
    # Instructions Staging #
    def present_instructions(self):
        self.generate_output_files()
        self.metadata_output_generation()
        self.protocol_floatlayout.add_widget(self.instruction_label)
        self.protocol_floatlayout.add_widget(self.start_button)
        
    # Block Staging #
    def block_screen(self,*args):
        if self.block_started == False:
            self.protocol_floatlayout.add_widget(self.block_label)
            self.block_start = time.time()
            self.block_started = True
            Clock.schedule_interval(self.block_screen,0.1)
        if (time.time() - self.block_start) > self.block_min_rest_duration:
            Clock.unschedule(self.block_screen)
            self.protocol_floatlayout.add_widget(self.continue_button)
            
    def block_end(self,*args):
        self.block_started = False
        self.protocol_floatlayout.clear_widgets()
        self.trial_contingency()
        self.protocol_floatlayout.add_widget(self.hold_button)
    
    # End Staging #
    def protocol_end(self):
        self.protocol_floatlayout.clear_widgets()
        self.protocol_floatlayout.add_widget(self.end_label)
        self.protocol_floatlayout.add_widget(self.return_button)
        
    def return_to_main(self,*args):
        self.manager.current='mainmenu'
    
    # Protocol Staging #
    
    def start_protocol(self,*args):
        self.protocol_floatlayout.remove_widget(self.instruction_label)
        self.protocol_floatlayout.remove_widget(self.start_button)
        self.start_clock()
        
        self.protocol_floatlayout.add_widget(self.hold_button)
        self.hold_button.size_hint = ((0.2 * self.width_adjust), (0.2 * self.height_adjust))
        self.hold_button.width = self.hold_button.height
        self.hold_button.pos_hint = {"center_x":0.5,"center_y":0.1}
        self.hold_button.bind(on_press=self.iti)
    
        
    def iti(self,*args):
        if self.iti_active == False:
            self.hold_button.unbind(on_press=self.iti)
            self.hold_button.bind(on_release=self.premature_response)
            self.start_iti = time.time()
            self.iti_active = True
            
            if self.feedback_string == 'WAIT FOR IMAGE - PLEASE TRY AGAIN':
                self.protocol_floatlayout.remove_widget(self.feedback_label)
                self.feedback_string = ''
            
            if self.feedback_on_screen == False:
                self.feedback_label.text = self.feedback_string
                self.protocol_floatlayout.add_widget(self.feedback_label)
                self.feedback_on_screen = True
            Clock.schedule_interval(self.iti,0.1)
        if self.iti_active == True:
            if (time.time() - self.start_iti) > self.feedback_length:
                self.protocol_floatlayout.remove_widget(self.feedback_label)
                self.feedback_on_screen = False
            if (time.time() - self.start_iti) > self.iti_length:
                Clock.unschedule(self.iti)
                self.iti_active = False
                self.hold_button.unbind(on_release=self.premature_response)
                self.stimulus_presentation()
                
    def stimulus_presentation(self,*args):
        self.left_stimulus.source = self.left_stimulus_image_path
        self.center_stimulus.source = self.center_stimulus_image_path
        self.right_stimulus.source = self.right_stimulus_image_path
        self.protocol_floatlayout.add_widget(self.left_stimulus)
        self.protocol_floatlayout.add_widget(self.center_stimulus)
        self.protocol_floatlayout.add_widget(self.right_stimulus)
        self.left_stimulus.size_hint = ((0.4 * self.width_adjust), (0.4 * self.height_adjust))
        self.right_stimulus.size_hint = ((0.4 * self.width_adjust), (0.4 * self.height_adjust))
        self.center_stimulus.size_hint = ((0.4 * self.width_adjust), (0.4 * self.height_adjust))


            
        self.start_stimulus = time.time()
        
        self.stimulus_on_screen = True
            
                
    def premature_response(self,*args):
        if self.stimulus_on_screen == True:
            return None
        
        Clock.unschedule(self.iti)
        self.feedback_string = 'WAIT FOR IMAGE - PLEASE TRY AGAIN'
        self.response_lat = 0
        self.iti_active = False
        self.feedback_label.text = self.feedback_string
        if self.feedback_on_screen == False:
            self.protocol_floatlayout.add_widget(self.feedback_label)
        self.hold_button.unbind(on_release=self.premature_response)
        self.hold_button.bind(on_press=self.iti)
        
        
            
        
    # Contingency Stages #
    def left_stimulus_pressed(self,*args):
        if self.l1_image == self.mask_image:
            return
        self.stimulus_on_screen = False
        self.protocol_floatlayout.remove_widget(self.left_stimulus)
        self.protocol_floatlayout.remove_widget(self.center_stimulus)
        self.protocol_floatlayout.remove_widget(self.right_stimulus)
        
        self.left_chosen = 1
        self.center_chosen = 0
        self.right_chosen = 0
        self.location_chosen = 1
        
        if self.l1_image == self.correct_image and self.correct_location == 0:
            correct = '1'
            self.current_correct += 1
            self.feedback_string = '[color=008000]CORRECT[/color]'
        elif self.l1_image == self.incorrect_image:
            correct = '0'
            self.feedback_string = '[color=FF0000]INCORRECT[/color]'
            
        self.response_lat = time.time() - self.start_stimulus
        
        self.feedback_label.text = self.feedback_string
        self.protocol_floatlayout.add_widget(self.feedback_label)
        self.feedback_on_screen = True
        self.write_summary_file(correct)
        
        if correct == '0':
            self.correction_trial = True
        else:
            self.correction_trial = False
            self.trial_contingency()
            
        
        self.hold_button.bind(on_press=self.iti)
        
    def center_stimulus_pressed(self,*args):
        if self.l2_image == self.mask_image:
            return
        self.stimulus_on_screen = False
        self.protocol_floatlayout.remove_widget(self.left_stimulus)
        self.protocol_floatlayout.remove_widget(self.center_stimulus)
        self.protocol_floatlayout.remove_widget(self.right_stimulus)
        
        self.left_chosen = 0
        self.center_chosen = 1
        self.right_chosen = 0
        self.location_chosen = 2
        
        if self.l2_image == self.correct_image and self.correct_location == 1:
            correct = '1'
            self.current_correct += 1
            self.feedback_string = '[color=008000]CORRECT[/color]'
        elif self.l2_image == self.incorrect_image:
            correct = '0'
            self.feedback_string = '[color=FF0000]INCORRECT[/color]'
            
        self.response_lat = time.time() - self.start_stimulus
        
        self.feedback_label.text = self.feedback_string
        self.protocol_floatlayout.add_widget(self.feedback_label)
        self.feedback_on_screen = True
        self.write_summary_file(correct)
        
        if correct == '0':
            self.correction_trial = True
        else:
            self.correction_trial = False
            self.trial_contingency()
            
        
        self.hold_button.bind(on_press=self.iti)
    
    def right_stimulus_pressed(self,*args):
        if self.l3_image == self.mask_image:
            return
        self.stimulus_on_screen = False
        self.protocol_floatlayout.remove_widget(self.left_stimulus)
        self.protocol_floatlayout.remove_widget(self.center_stimulus)
        self.protocol_floatlayout.remove_widget(self.right_stimulus)
        
        self.left_chosen = 0
        self.center_chosen = 0
        self.right_chosen = 1
        self.location_chosen = 3
        
        if self.l3_image == self.correct_image and self.correct_location == 2:
            correct = '1'
            self.current_correct += 1
            self.feedback_string = '[color=008000]CORRECT[/color]'
        elif self.l3_image == self.incorrect_image:
            correct = '0'
            self.feedback_string = '[color=FF0000]INCORRECT[/color]'
            
        self.response_lat = time.time() - self.start_stimulus
        
        self.feedback_label.text = self.feedback_string
        self.protocol_floatlayout.add_widget(self.feedback_label)
        self.feedback_on_screen = True
        self.write_summary_file(correct)
        
        if correct == '0':
            self.correction_trial = True
        else:
            self.correction_trial = False
            self.trial_contingency()
            
        
        self.hold_button.bind(on_press=self.iti)
        
        
    # Data Saving Functions #
    def write_summary_file(self,correct):
        if self.correction_trial == True:
            correction = 1
        else:
            correction = 0
        data_file = open(self.file_path, "a")
        data_file.write("\n")
        data_file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (self.current_trial,self.current_stage,self.correct_image,self.incorrect_image,self.correct_location,self.incorrect_location,correction,self.location_chosen,correct,self.response_lat))
        data_file.close()
        return
    
    # Trial Contingency Functions #
    
    def trial_contingency(self):
        self.current_trial += 1
        
        if self.current_trial > self.session_trial_max:
            Clock.unschedule(self.clock_monitor)
            self.protocol_end()
            return
        if self.stage_index == 0:
            if self.current_correct >= 10:
                self.block_contingency()
                return
            self.trial_configuration = random.randint(1,6)
            self.generate_trial_contingency(training=True)
        
            
        
        if self.stage_index == 1:
            if self.current_trial > self.block_threshold:
                self.block_contingency()
                self.block_threshold += self.block_length
                return
            self.trial_configuration = random.randint(1,6)
            self.generate_trial_contingency()
        
    def block_contingency(self):
        self.protocol_floatlayout.clear_widgets()
        
        if self.stage_index == 0:
            self.stage_index = 1
            self.current_block = 1
            self.trial_configuration = random.randint(1,6)
            self.generate_trial_contingency()
            self.current_stage = self.stage_list[self.stage_index]
        elif self.stage_index == 1:
            self.current_block += 1
            if self.current_block > self.block_count:
                self.protocol_end()
                return
            
            self.trial_configuration = random.randint(1,6)
            self.generate_trial_contingency()

        
        self.block_screen()
            
    
    # Time Monitor Functions #
    def start_clock(self,*args):
        self.start_time = time.time()
        Clock.schedule_interval(self.clock_monitor,0.1)
        Clock.schedule_interval(self.display_monitor,0.1)
    
    def clock_monitor(self,*args):
        self.current_time = time.time()
        self.elapsed_time = self.current_time - self.start_time
        
        if self.elapsed_time > self.session_max_length:
            Clock.unschedule(self.clock_monitor)
            self.protocol_end()
            
    def display_monitor(self,*args):
       width  = self.protocol_floatlayout.width
       height = self.protocol_floatlayout.height
       
       self.screen_ratio = width/height
            
        
        
        
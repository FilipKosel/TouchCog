##############################################################################
#                      Kivy Launcher Interface                               #
#                      by: Daniel Palmer PhD                                 #
#                      Version: 2.0                                          #
##############################################################################




# Imports #

# import os
# import importlib.util
# import importlib
# import cProfile
# import configparser
# import pathlib
# import kivy
# import zipimport
# import sys
# import configparser
# import pandas as pd
# 
# from Classes.Menu import MenuBase
# 
# from functools import partial
# 
# from kivy.app import App
# from kivy.clock import Clock
# from kivy.config import Config
# from kivy.core.window import Window
# from kivy.uix.behaviors import ButtonBehavior
# from kivy.uix.button import Button
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.image import Image
# from kivy.uix.label import Label
# from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.uix.textinput import TextInput
# from kivy.uix.vkeyboard import VKeyboard
# from kivy.uix.widget import Widget


# from win32api import GetSystemMetrics
# from Protocol_Configure import Protocol_Select




# Setup #




import tkinter
import sys
import os
import ffpyplayer

os.environ['KIVY_VIDEO'] = 'ffpyplayer'
os.environ['KIVY_IMAGE'] = 'sdl2'

from kivy.config import Config




if sys.platform == 'win32':
	
	import ctypes
	ctypes.windll.shcore.SetProcessDpiAwareness(2)
	scale_factor = (ctypes.windll.shcore.GetScaleFactorForDevice(0))/100
	screensize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

	print(screensize)

else:
	
	scale_factor = 1.0
	

print(scale_factor)


root = tkinter.Tk()
screen_resolution = (int((root.winfo_screenwidth())/scale_factor), int((root.winfo_screenheight())/scale_factor))
# screen_resolution = (root.winfo_screenwidth(), root.winfo_screenheight())
current_dpi = root.winfo_fpixels('1i')
root.quit()

print('Current DPI: ', current_dpi)


def get_screen_resolution(self, **kwargs):
	# self.screen_resolution = screen_resolution
	
	print('Unadjusted screen resolution: ', screen_resolution)

	self.screen_resolution = [screen_resolution[0] * scale_factor, screen_resolution[1] * scale_factor]
	
	print('Adjusted screen resolution: ', self.screen_resolution)

	return self.screen_resolution


# print('Unadjusted screen resolution: ', screen_resolution)

# sr_adjusted = [screen_resolution[0] * scale_factor, screen_resolution[1] * scale_factor]


if screen_resolution[0] < screen_resolution[1]:
	
	x_scaling = 1
	y_scaling = screen_resolution[0]/screen_resolution[1]
	
elif screen_resolution[0] > screen_resolution[1]:
	
	x_scaling = screen_resolution[1]/screen_resolution[0]
	y_scaling = 1
	
else:
	
	x_scaling = 1
	y_scaling = 1


if (Config.get('graphics', 'width') != str(round(screen_resolution[0]))) or \
   (Config.get('graphics', 'height') != str(round(screen_resolution[1]))):
	
	Config.set('graphics', 'width', round(screen_resolution[0]))
	Config.set('graphics', 'height', round(screen_resolution[1]))
	Config.write()


print('Screen resolution: ', screen_resolution)
print('X scaling: ', x_scaling)
print('Y scaling: ', y_scaling)
# print(current_dpi)




import cProfile
import configparser
import importlib
import importlib.util
# import os
import pathlib


# from kivy.config import Config
from kivy.base import EventLoop




EventLoop.ensure_window()
print('Event loop dpi: ', EventLoop.window.dpi)
print('Event loop size: ', EventLoop.window.size)

# self.screen_dim = EventLoop.window.size


# main_path = os.getcwd()
# config_path = main_path + '/Screen.ini'

# ctypes.windll.shcore.SetProcessDpiAwareness(2)
# # user32 = ctypes.windll.user32
# screensize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
# 
# print(screensize)


os.chdir(pathlib.Path(__file__).parent.resolve())

config_path_screen = pathlib.Path(os.getcwd(), 'Screen.ini')
config_file_screen = configparser.ConfigParser()
config_file_screen.read(config_path_screen, encoding = 'utf-8')

print(str(config_path_screen))

fullscreen = str(config_file_screen['Screen']['fullscreen'])
virtual_keyboard = str(config_file_screen['keyboard']['virtual_keyboard'])
cursor_visible = str(config_file_screen['mouse']['cursor_visible'])
# use_mouse = config_file_screen['mouse']['use_mouse']


# Config.set('graphics', 'allow_screensaver', 0)
# Config.set('kivy', 'kivy_clock', 'interrupt')
# Config.set('graphics', 'maxfps', 0)


write_config = False


if Config.get('graphics', 'allow_screensaver') != str(0):
	
	Config.set('graphics', 'allow_screensaver', 0)
	
	write_config = True
	print('allow_screensaver set.')
	

if Config.get('graphics', 'always_on_top') != str(0):
	
	Config.set('graphics', 'always_on_top', 0)
	
	write_config = True
	print('always_on_top set.')
	

if Config.get('graphics', 'borderless') != str(1):
	
	Config.set('graphics', 'borderless', 1)
	
	write_config = True
	print('borderless set.')


if Config.get('graphics', 'maxfps') != str(0):
	
	Config.set('graphics', 'maxfps', 0)
	
	write_config = True
	print('maxfps set.')
	

if str(Config.get('graphics', 'fullscreen')) != fullscreen:
	
	Config.set('graphics', 'fullscreen', fullscreen)
	
	write_config = True
	print('fullscreen set.')


if (Config.get('graphics', 'width') != str(round(screen_resolution[0]))) or \
   (Config.get('graphics', 'height') != str(round(screen_resolution[1]))):
	
	Config.set('graphics', 'width', round(screen_resolution[0]))
	Config.set('graphics', 'height', round(screen_resolution[1]))
	
# 	Window.size = (int(screen_resolution[0]), int(screen_resolution[1]))
	
	write_config = True
	print('width or height set.')
	

if Config.get('graphics', 'show_cursor') != cursor_visible:

	Config.set('graphics','show_cursor', cursor_visible)
	
	write_config = True
	print('show_cursor set.')
		
	
if Config.get('kivy', 'kivy_clock') != 'interrupt':
	
	Config.set('kivy', 'kivy_clock', 'interrupt')
	
	write_config = True
	print('kivy_clock interrupt set.')
	

if virtual_keyboard == 1:
	
	if Config.get('kivy', 'keyboard_mode') != 'systemanddock':
		
		Config.set('kivy', 'keyboard_mode', 'systemanddock')
		
		write_config = True
		print('keyboard_mode systemanddock set.')
		
elif virtual_keyboard == 0:
	
	if Config.get('kivy', 'keyboard_mode') != 'system':
		
		Config.set('kivy', 'keyboard_mode', 'system')
		
		write_config = True
		print('keyboard_mode system set.')
		

if write_config:
	
	Config.write()
	print('Config written.')




from kivy.core.window import Window




# print('screensaver')
# print(Window.allow_screensaver)
# print(bool(int(Config.get('graphics', 'allow_screensaver'))))
if Window.allow_screensaver != bool(int(Config.get('graphics', 'allow_screensaver'))):
	Window.allow_screensaver = bool(int(Config.get('graphics', 'allow_screensaver')))
	print('Window screensaver set')

# print('always on top')
# print(Window.always_on_top)
# print(bool(int(Config.get('graphics', 'always_on_top'))))
if Window.always_on_top != bool(int(Config.get('graphics', 'always_on_top'))):
	Window.always_on_top = bool(int(Config.get('graphics', 'always_on_top')))
	print('Window always on top set')

# print('borderless')
# print(Window.borderless)
# print(bool(int(Config.get('graphics', 'borderless'))))
if Window.borderless != bool(int(Config.get('graphics', 'borderless'))):
	Window.borderless = bool(int(Config.get('graphics', 'borderless')))
	print('Window borderless set')

# print('fullscreen')
# print(Window.fullscreen)
# print(bool(int(Config.get('graphics', 'fullscreen'))))
if Window.fullscreen != bool(int(Config.get('graphics', 'fullscreen'))):
	Window.fullscreen = bool(int(Config.get('graphics', 'fullscreen')))
	print('Window fullscreen set')



# print('Window size: ', Window.size)


# # Window.fullscreen = int(config_file['Screen']['fullscreen'])
# Window.fullscreen = 1

# print(Window.fullscreen)

# print(int(config_file['Screen']['x']), int(config_file['Screen']['y']))

# if not Window.fullscreen:
# 	
# 	print('Not fullscreen')

# Window.size = (int(screen_resolution[0]), int(screen_resolution[1])) #int(config_file['Screen']['x']), int(config_file['Screen']['y'])


# x_dim = Window.size[0]
# y_dim = Window.size[1]

# print('Screen size: ', Window.size)


# if bool(config_file['keyboard']['virtual_keyboard']):
# 	
# 	print('Virtual keyboard')
# 	
# # 	Config.set('kivy', 'keyboard_mode', 'systemanddock')
# 	
# else:
# 	
# 	print('No virtual keyboard')
# 	
# # 	Config.set('kivy', 'keyboard_mode', 'system')
# 
# 
# if not bool(config_file['mouse']['use_mouse']):
# 	
# 	print('No mouse')
	
# 	Config.set('graphics','show_cursor', 0)




# Protocol Start




# Import #




# import os
# import importlib.util
# import importlib
# import cProfile
# import configparser
# import pathlib
import kivy
import zipimport
# import sys
# import configparser
import pandas as pd

from Classes.Menu import MenuBase

from functools import partial

from kivy.app import App
from kivy.clock import Clock
# from kivy.config import Config
# from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.widget import Widget

from kivy.uix.video import Video
from kivy.core.video import Video as CoreVideo
from kivy.core.video import VideoBase




# General Functions #

def os_folder_modifier():
	os_platform = sys.platform
	if os_platform == "linux":
		mod = "/"
	elif os_platform == "darwin":
		mod = "/"
	elif os_platform == "win32":
		mod = "\\"
	else:
		mod = "/"
	return mod




# Class Objects #
class ImageButton(ButtonBehavior, Image):



	def __init__(self, **kwargs):
		super(ImageButton, self).__init__(**kwargs)




# Class Screen Manager #

class ScreenManager(ScreenManager):



	def __init__(self, **kwargs):
		super(ScreenManager, self).__init__(**kwargs)




# Class Task Selection #

class MainMenu(Screen):



	def __init__(self, **kwargs):
		super(MainMenu, self).__init__(**kwargs)
		self.name = 'mainmenu'
		self.Menu_Layout = FloatLayout()
		self.protocol_window = ''
		self.add_widget(self.Menu_Layout)
		launch_button = Button(text="Start Session")
		launch_button.size_hint = (0.3, 0.2)
		launch_button.pos_hint = {"x": 0.35, "y": 0.6}
		launch_button.bind(on_press=self.load_protocol_menu)
		self.Menu_Layout.add_widget(launch_button)
		
		exit_button = Button(text="Close Program")
		exit_button.size_hint = (0.3, 0.2)
		exit_button.pos_hint = {"x": 0.35, "y": 0.2}
		exit_button.bind(on_press=self.exit_program)
		self.Menu_Layout.add_widget(exit_button)
		


	def load_protocol_menu(self, *args):
		if isinstance(self.protocol_window, ProtocolMenu):
			self.manager.current = "protocolmenu"

		else:
			self.protocol_window = ProtocolMenu()
			self.manager.add_widget(self.protocol_window)
			self.manager.current = "protocolmenu"
	


	def exit_program(self, *args):
		App.get_running_app().stop()
		Window.close()




# Class Protocol Selection #

class ProtocolMenu(Screen):



	def __init__(self, **kwargs):
		super(ProtocolMenu, self).__init__(**kwargs)
		self.Protocol_Layout = FloatLayout()
		self.Protocol_Configure_Screen = ''
		self.name = 'protocolmenu'
		
		self.Protocol_Configure_Screen = MenuBase()
		
		protocol_list = self.search_protocols()
		self.Protocol_List = GridLayout(rows=len(protocol_list), cols=1)
		protocol_index = 0

		for protocol in protocol_list:
			button_func = partial(self.set_protocol, protocol)
			self.Protocol_List.add_widget(Button(text=protocol, on_press=button_func))
			protocol_index += 1
		
		self.Protocol_List.size_hint = (0.8, 0.7)
		self.Protocol_List.pos_hint = {"x": 0.1, "y": 0.3}
		self.Protocol_Layout.add_widget(self.Protocol_List)
		
		cancel_button = Button(text="Cancel")
		cancel_button.size_hint = (0.2, 0.1)
		cancel_button.pos_hint = {"x": 0.4, "y": 0.1}
		cancel_button.bind(on_press=self.cancel_protocol)
		self.Protocol_Layout.add_widget(cancel_button)
		
		self.add_widget(self.Protocol_Layout)
	


	def set_protocol(self, label, *args):
		if isinstance(self.Protocol_Configure_Screen,MenuBase):
			self.manager.remove_widget(self.Protocol_Configure_Screen)

		self.protocol_constructor(label)
		self.Protocol_Configure_Screen.size = Window.size
		self.manager.add_widget(self.Protocol_Configure_Screen)
		self.manager.current = 'menuscreen'
	


	def cancel_protocol(self, *args):
		self.manager.current = "mainmenu"
	


	def search_protocols(self):
		cwd = os.getcwd()
		mod = os_folder_modifier()
		folder = cwd + mod + "Protocol"
		task_list = os.listdir(folder)
		for task in task_list:
			if '.py' in task:
				task_list.remove(task)
		return task_list
	


	def protocol_constructor(self, protocol):
		#cwd = os.getcwd()
		#mod = os_folder_modifier()
		#prot_path = cwd + mod + 'Protocol' + mod + protocol
		#sys.path.append(prot_path)
		#from Task.Menu import ConfigureScreen
		#self.Protocol_Configure_Screen = ConfigureScreen()
		#sys.path.remove(prot_path)


		def lazy_import(protocol):
			cwd = os.getcwd()
			working = cwd + '\\Protocol\\' + protocol + '\\Task\\Menu.py'
			mod_name = 'Menu'
			mod_spec = importlib.util.spec_from_file_location(mod_name, working)
			mod_loader = importlib.util.LazyLoader(mod_spec.loader)
			mod_spec.loader = mod_loader
			module = importlib.util.module_from_spec(mod_spec)
			sys.modules[mod_name] = module
			mod_loader.exec_module(module)
			return module


		task_module = lazy_import(protocol)
		self.Protocol_Configure_Screen = task_module.ConfigureScreen()




# Class App Builder #

class MenuApp(App):



	def build(self):
		self.session_event_data = pd.DataFrame()
		self.session_event_path = ''
		self.summary_event_data = pd.DataFrame()
		self.summary_event_path = ''
		self.s_manager = ScreenManager()
		self.main_menu = MainMenu()
		self.s_manager.add_widget(self.main_menu)
	
		return self.s_manager
	


	def add_screen(self, screen):
		self.s_manager.add_widget(screen)
	


	def on_stop(self):
		if len(self.session_event_data.index > 1):
			# self.session_event_data = self.session_event_data.sort_values(by=['Time'])
			self.session_event_data.to_csv(self.session_event_path, index=False)
			self.summary_event_data.to_csv(self.summary_event_path, index=False)
		else:
			print('No data to save.')




if __name__ == '__main__':
	MenuApp().run()
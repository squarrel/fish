__version__ = '0.1'

from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 600)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import cymunk
from random import randint
from math import radians#, atan2, degrees
import kivent_core
import kivent_cymunk
from kivent_core.gamesystems import GameSystem
from kivent_core.renderers import texture_manager
#from cymunk import PivotJoint, GearJoint, Body
from kivy.properties import NumericProperty#, ListProperty

texture_manager.load_atlas('assets/background_objects.atlas')
texture_manager.load_atlas('assets/foreground_objects.atlas')


class MainGame(Widget):
	current_entity = NumericProperty(None)
	x_1 = NumericProperty(0)
	y_1 = NumericProperty(0)
	count = 0

	def __init__(self, **kwargs):
		super(MainGame, self).__init__(**kwargs)
		Clock.schedule_once(self.init_game)

	def ensure_startup(self):
		systems_to_check = ['map', 'physics', 'renderer', 'rotate', 'position']
		systems = self.gameworld.systems
		for each in systems_to_check:
			if each not in systems:
				return False
		return True

	def init_game(self, dt):
		if self.ensure_startup():
			self.setup_map()
			self.setup_states()
			self.set_state()
			self.setup_collision_callbacks()
			self.draw_some_stuff()
			Clock.schedule_interval(self.update, 0)
		else:
			Clock.schedule_once(self.init_game)

	def btn_press(self):
		print('Hey, ya pressed me!')

	def movement(self):
		self.x_1 += 1
		self.y_1 += 1

	def move_it(self):
		gameworld = self.gameworld
		entities = gameworld.entities
		entity_1 = entities[self.current_entity]
		steering_1 = entity_1.steering
		steering_1.target = (self.x_1, self.y_1)

	def on_touch_down(self, touch):
		
		gameworld = self.gameworld
		entities = gameworld.entities
		entity_2 = entities[1]
		steering_2 = entity_2.steering
		steering_2.target = (touch.x+200, touch.y)
		entity_3 = entities[2]
		steering_3 = entity_3.steering
		steering_3.target = (touch.x+200, touch.y+200)
		if touch.x < 100 and touch.y < 100:
			if self.gameworld.state == 'main':
				self.set_pause()
			else:
				self.set_state()

	def draw_some_stuff(self):
		size = Window.size
		pos_1 = (250, 150)
		ship_1 = self.create_ship(pos_1)
		self.current_entity = ship_1
		pos_2 = (250, 100)
		ship_2 = self.create_ship(pos_2)
		self.current_entity = ship_2
		pos_3 = (250, 300)
		ship_3 = self.create_ship(pos_3)
		self.current_entity = ship_3
		
		self.draw_goal((200, 100), (140, 100))
		self.draw_goal((200, 400), (140, 100))
		
		self.create_asteroid((250, 550))

	def no_collide(self, space, arbiter):
		return False

	def setup_collision_callbacks(self):
		systems = self.gameworld.systems
		physics_system = systems['physics']
		physics_system.add_collision_handler(
			1, 2, 
			begin_func=self.no_collide)

	def create_ship(self, pos):
		x_vel = 0
		y_vel = 0
		angle = 0
		angular_velocity = 0
		shape_dict = {'inner_radius': 0, 'outer_radius': 45, 
			'mass': 10, 'offset': (0, 0)}
		col_shape = {'shape_type': 'circle', 'elasticity': .0, 
			'collision_type': 1, 'shape_info': shape_dict, 'friction': .7}
		col_shapes = [col_shape]
		physics_component = {'main_shape': 'circle', 
			'velocity': (x_vel, y_vel), 
			'position': pos, 'angle': angle, 
			'angular_velocity': angular_velocity, 
			'vel_limit': 750, 
			'ang_vel_limit': radians(900), 
			'mass': 50, 'col_shapes': col_shapes}
		steering_component = {
			'turn_speed': 10.0,
			'stability': 900000.0,
			'max_force': 200000.0,
			'speed': 350,
			}
		create_component_dict = {'physics': physics_component, 
			'physics_renderer': {'texture': 'ship7', 'size': (96 , 88)}, 
			'position': pos, 'rotate': 0, 'steering': steering_component}
		component_order = ['position', 'rotate', 
			'physics', 'physics_renderer', 'steering']
		return self.gameworld.init_entity(create_component_dict, component_order)

	def draw_goal(self, pos, size, collision_type=4):
		x_vel = 0
		y_vel = 0
		angle = 0
		angular_velocity = 0
		width, height = size
		shape_dict = {'width': width, 'height': height,
			'mass': 0, 'offset': (0, 0)}
		col_shape = {'shape_type': 'box', 'elasticity': .5,
		'collision_type': collision_type, 'shape_info': shape_dict,
			'friction': 1.0}
		col_shapes = [col_shape]
		physics_component = {'main_shape': 'box',
			'velocity': (x_vel, y_vel),
			'position': pos, 'angle': angle,
			'angular_velocity': angular_velocity,
			'vel_limit': 0.,
			'ang_vel_limit': radians(0.),
			'mass': 0, 'col_shapes': col_shapes}
		create_component_dict = {'physics': physics_component,
			'renderer': {'size': (width, height), 'renderer': True},
			'position': pos, 'rotate': 0}
		component_order = ['position', 'rotate',
			'physics', 'renderer']
		
		return self.gameworld.init_entity(create_component_dict,
			component_order)
			
	def create_asteroid(self, pos):
		x_vel = randint(-100, 100)
		y_vel = randint(-100, 100)
		angle = radians(randint(-360, 360))
		angular_velocity = radians(randint(-150, -150))
		shape_dict = {'inner_radius': 0, 'outer_radius': 32,
			'mass': 50, 'offset': (0, 0)}
		col_shape = {'shape_type': 'circle', 'elasticity': .5,
			'collision_type': 1, 'shape_info': shape_dict, 'friction': 1.0}
		col_shapes = [col_shape]
		physics_component = {'main_shape': 'circle',
			'velocity': (x_vel, y_vel),
			'position': pos, 'angle': angle,
			'angular_velocity': angular_velocity,
			'vel_limit': 250,
			'ang_vel_limit': radians(200),
			'mass': 50, 'col_shapes': col_shapes}
		create_component_dict = {'physics': physics_component,
			'renderer': {'texture': 'asteroid1',
			'size': (64, 64),
			'render': True},
			'position': pos, 'rotate': 0,
			}
		component_order = ['position', 'rotate', 'physics', 'renderer']
		
		return self.gameworld.init_entity(create_component_dict, component_order)

	def setup_map(self):
		gameworld = self.gameworld
		gameworld.currentmap = gameworld.systems['map']

	def update(self, dt):
		self.gameworld.update(dt)
		self.movement()
		self.move_it()
		self.count += 1

	def setup_states(self):
		self.gameworld.add_state(state_name='menu',
			systems_added=['renderer', 'physics_renderer'],
			systems_removed=[], 
			systems_paused=['steering'],
			systems_unpaused=['renderer', 'physics_renderer'],
			screenmanager_screen='menu')
		
		self.gameworld.add_state(state_name='main', 
			systems_added=['renderer', 'physics_renderer'],
			systems_removed=[], systems_paused=[],
			systems_unpaused=['renderer', 'physics_renderer',
				'steering'],
			screenmanager_screen='main')
			
		self.gameworld.add_state(state_name='pause',
			systems_added=['renderer', 'physics_renderer'],
			systems_removed=[],
			systems_paused=['steering'],
			systems_unpaused=['renderer', 'physics_renderer'],
			screenmanager_screen='pause')

	def set_menu(self):
		self.gameworld.state = 'menu'
		print(self.gameworld.state)

	def set_state(self):
		self.gameworld.state = 'main'
		print(self.gameworld.state)
		
	def set_pause(self):
		self.gameworld.state = 'pause'
		print(self.gameworld.state)
		

class YourAppNameApp(App):
	def build(self):
		Window.clearcolor = (0.1, 0.1, 0.1, 1.)


if __name__ == '__main__':
	YourAppNameApp().run()

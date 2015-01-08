__version__ = '0.1'

'''from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 600)'''

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
import cymunk
from random import randint
from math import radians
import kivent_core
import kivent_cymunk
from kivent_core.gamesystems import GameSystem
from kivent_core.renderers import texture_manager
from kivy.properties import NumericProperty, StringProperty
import random
from functools import partial

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

	# Start up
	def ensure_startup(self):
		systems_to_check = ['map', 'physics', 'renderer', 'rotate', 'position']
		systems = self.gameworld.systems
		for each in systems_to_check:
			if each not in systems:
				return False
		return True

	# Initialize game
	def init_game(self, dt):
		if self.ensure_startup():
			self.setup_map()
			self.setup_states()
			self.set_state()
			self.draw_some_stuff()
			self.setup_collision_callbacks()
			Clock.schedule_interval(self.update, 0)
		else:
			Clock.schedule_once(self.init_game)

	def movement(self):
		self.x_1 += 1
		self.y_1 += 1

	def move_it(self):
		gameworld = self.gameworld
		entities = gameworld.entities
		entity_1 = entities[self.current_entity]
		steering_1 = entity_1.steering
		steering_1.target = (self.x_1, self.y_1)

	# On touch down
	def on_touch_down(self, touch):
		gameworld = self.gameworld
		entities = gameworld.entities
		win_x = Window.size[0]
		win_y = Window.size[1]
		
		if self.gameworld.state == 'main' and App.get_running_app().level == 1:
			entity_1 = entities[1]
			steering_1 = entity_1.steering
			steering_1.target = (touch.x+100, touch.y)
			entity_2 = entities[2]
			steering_2 = entity_2.steering
			steering_2.target = (touch.x+100, touch.y+100)
			entity_3 = entities[3]
			steering_3 = entity_3.steering
			steering_3.target = (touch.x, touch.y+100)
			entity_4 = entities[4]
			steering_4 = entity_4.steering
			steering_4.target = (touch.x, touch.y+100)
			entity_5 = entities[5]
			steering_5 = entity_5.steering
			steering_5.target = (touch.x, touch.y+100)
			entity_6 = entities[6]
			steering_6 = entity_6.steering
			steering_6.target = (touch.x, touch.y+100)
			entity_7 = entities[7]
			steering_7 = entity_7.steering
			steering_7.target = (touch.x, touch.y+100)
			
		if self.gameworld.state == 'message':
			if touch.x > win_x * 0.4 and touch.x < win_x * 0.6 and touch.x > win_y * 0.4 and touch.y < win_y * 0.6:
				self.set_state()
		
		if touch.x < Window.size[0] * 0.1 and touch.y > Window.size[1] * 0.95:
			if self.gameworld.state == 'main':
				self.set_pause()
			elif gameworld.state == 'pause':
				self.set_state()
		if touch.x > Window.size[0] * 0.9 and touch.y > Window.size[1] * 0.95:
			if self.gameworld.state == 'main':
				self.set_menu()
			elif gameworld.state == 'menu':
				self.set_state()

	# Draw
	def draw_some_stuff(self):
		size_x = Window.size[0]
		size_y = Window.size[1]
		
		for j in range(7):
			self.create_fish((100+j*40, 100+j*40))
			if j == 0:
				self.current_entity = j
		
		self.draw_wall((size_x*0.01, size_y*0.5), (size_x*0.02, size_y)) #left wall. the position starts at the center of the object, not at the bottom or top, not sure
		self.draw_wall((size_x*0.99, size_y*0.5), (size_x*0.02, size_y)) #right wall
		self.draw_wall((size_x*0.5, size_y*0.01), (size_x, size_y*0.03)) #bottom wall
		self.draw_wall((size_x*0.5, size_y*0.97), (size_x, size_y*0.06)) #top wall
		
	# Breadcrumbs enter
	def enter_breadcrumbs(self):
		r = random.uniform(Window.size[0]*0.1, Window.size[0]*0.9)
		self.create_breadcrumb((r, Window.size[1]*0.9))

	# Remove entities
	def remove_entities(self, entity_id):
		Clock.schedule_once(partial(
			self.gameworld.timed_remove_entity, entity_id))
		App.get_running_app().score += 1
		
	# Clear level
	def clear_level(self):
		self.gameworld.clear_entities()
		
	# Jump to level
	def jump_to_level(self, dt):
		self.clear_level()
		self.set_message()
		
	# Collision start
	def begin_collide(self, space, arbiter):
		ent1_id = arbiter.shapes[0].body.data
		ent2_id = arbiter.shapes[1].body.data
		
		self.remove_entities(ent2_id)
		
	# Collision end
	'''def finish_collide(self, space, arbiter):
		print('finish collide')'''

	# Collisions
	def setup_collision_callbacks(self):
		systems = self.gameworld.systems
		physics_system = systems['physics']
		
		physics_system.gravity = (0, -100)
		
		physics_system.add_collision_handler(
			1, 2, 
			begin_func=self.begin_collide
			)
			
	# Fish
	def create_fish(self, pos):
		x_vel = 10
		y_vel = 0
		angle = 0
		angular_velocity = 0
		shape_dict = {'inner_radius': 0, 'outer_radius': 45, 
			'mass': 10, 'offset': (0, 0)}
		col_shape = {'shape_type': 'circle', 'elasticity': .0, 
			'collision_type': 1, 'shape_info': shape_dict, 'friction': 0.0}
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

	# Walls
	def draw_wall(self, pos, size, collision_type=3):
		x_vel = 0
		y_vel = 0
		angle = 0
		angular_velocity = 0
		width, height = size
		shape_dict = {'width': width, 'height': height,
			'mass': 0, 'offset': (0, 0)}
		col_shape = {'shape_type': 'box', 'elasticity': .5,
		'collision_type': collision_type, 'shape_info': shape_dict,
			'friction': 0.5}
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
	
	# Breadcrumbs
	def create_breadcrumb(self, pos):
		x_vel = 0
		y_vel = -5
		angle = radians(randint(-360, 360))
		angular_velocity = radians(randint(-150, -150))
		shape_dict = {'inner_radius': 0, 'outer_radius': 16,
			'mass': 50, 'offset': (0, 0)}
		col_shape = {'shape_type': 'circle', 'elasticity': .5,
			'collision_type': 2, 'shape_info': shape_dict, 'friction': 0.5}
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
			'size': (32, 32),
			'render': True},
			'position': pos, 'rotate': 0,
			}
		component_order = ['position', 'rotate', 'physics', 'renderer']
		
		return self.gameworld.init_entity(create_component_dict, component_order)
	
	# Map
	def setup_map(self):
		gameworld = self.gameworld
		gameworld.currentmap = gameworld.systems['map']

	# Update -------------------
	def update(self, dt):
		self.gameworld.update(dt)
		#self.movement()
		#self.move_it()
		self.count += 0.25
		#print(self.count)
		if self.count % 17 == 0.0:
			self.enter_breadcrumbs()
		if App.get_running_app().level == 1 and App.get_running_app().score == 10:
			App.get_running_app().score += 1
			App.get_running_app().level += 1
			Clock.schedule_once(self.jump_to_level)
			
	# States
	def setup_states(self):
		self.gameworld.add_state(state_name='menu',
			systems_added=['renderer', 'physics_renderer', 'steering'],
			systems_removed=[], 
			systems_paused=['steering'],
			systems_unpaused=['renderer', 'physics_renderer'],
			screenmanager_screen='menu')
		
		self.gameworld.add_state(state_name='main', 
			systems_added=['renderer', 'physics_renderer', 'steering'],
			systems_removed=[], systems_paused=[],
			systems_unpaused=['renderer', 'physics_renderer',
				'steering'],
			screenmanager_screen='main')
			
		self.gameworld.add_state(state_name='pause',
			systems_added=['renderer', 'physics_renderer', 'steering'],
			systems_removed=[],
			systems_paused=['steering'],
			systems_unpaused=['renderer', 'physics_renderer'],
			screenmanager_screen='pause')
			
		self.gameworld.add_state(state_name='message',
			systems_added=['renderer', 'physics_renderer', 'steering'],
			systems_removed=[],
			systems_paused=['steering'],
			systems_unpaused=['renderer', 'physics_renderer'],
			screenmanager_screen='message')
	
	# Menu
	def set_menu(self):
		self.gameworld.state = 'menu'
		print(self.gameworld.state)

	# Main
	def set_state(self):
		self.gameworld.state = 'main'
		print(self.gameworld.state)
	
	# Pause
	def set_pause(self):
		self.gameworld.state = 'pause'
		print(self.gameworld.state)
	
	# Message
	def set_message(self):
		self.gameworld.state = 'message'
		print(self.gameworld.state)

class YourAppNameApp(App):
	score = NumericProperty(0)
	level = 1
	
	def build(self):
		Window.clearcolor = (0.1, 0.1, 0.1, 1.)


if __name__ == '__main__':
	YourAppNameApp().run()

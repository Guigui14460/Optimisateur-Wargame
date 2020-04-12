import os
import pickle
import pygame, pygame.gfxdraw
import random
import time

##### LES SOURCES : https://pythonprogramming.net/ #####

# IMPORT PYTHON FILES OF YOUR GAME

from army import Army
from ga_wargame import genetic_algorithm_best_army
from mapping import Map
from simulator import left_army_attack
from sound import GameVictorySound
import units
from utils import unit_cost

# MAIN INFORMATIONS

WIDTH = 1024
HEIGHT = 768
FPS = 60

run = True
pause = False
music_paused = False
music_muted = False
effect_played = False
victory_music_played = False
sounds_volume = 1


# INITIALIZATION OF PYGAME AND CREATION OF THE WINDOW // SETTING FOR THE WINDOW

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('WarGame')
clock = pygame.time.Clock()

# COLORS // FONTS

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

RED_TRANSPARENT = (100, 0, 0, 127)
BLACK_TRANSPARENT = (0, 0, 0, 127)

SMALL_FONT = pygame.font.Font("diablo_l.ttf", 20)
MEDIUM_FONT = pygame.font.Font("diablo_l.ttf", 30)
LARGE_FONT = pygame.font.Font("diablo_l.ttf", 50)

# PATH FOR IMAGES /// LOADING IMAGES

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")

background_menu = pygame.image.load(os.path.join(IMG_DIR, "menu.png")).convert()
background_menu_rect = background_menu.get_rect()

background_about = pygame.image.load(os.path.join(IMG_DIR, "about.png")).convert()
background_about_rect = background_about.get_rect()

background_play_select = pygame.image.load(os.path.join(IMG_DIR, "play_select.png")).convert()
background_play_select_rect = background_play_select.get_rect()

background_play_opti = pygame.image.load(os.path.join(IMG_DIR, "play_opti.png")).convert()
background_play_opti_rect = background_play_opti.get_rect()

background_play_create = pygame.image.load(os.path.join(IMG_DIR, "play_create.png")).convert()
background_play_create_rect = background_play_select.get_rect()

sound_speaking = pygame.image.load(os.path.join(IMG_DIR, "on.png")).convert_alpha()
sound_speaking_rect = sound_speaking.get_rect()
sound_mute = pygame.image.load(os.path.join(IMG_DIR, "off.png")).convert_alpha()
sound_mute_rect = sound_mute.get_rect()


# INITIALIZATION SOUNDS
channel_0_for_background_sound = pygame.mixer.Channel(0)
channel_1_for_fight_effect_sound = pygame.mixer.Channel(1)

background_sound = pygame.mixer.Sound("got.wav")
fight_effect_sound = pygame.mixer.Sound("Effect.wav")

channel_0_for_background_sound.play(background_sound, loops=-1)
channel_0_for_background_sound.set_volume(sounds_volume)

channel_1_for_fight_effect_sound.play(fight_effect_sound, loops=-1)
channel_1_for_fight_effect_sound.set_volume(2 * sounds_volume)
channel_1_for_fight_effect_sound.pause()


dico_unit = {'King': 1, 'Horseman': 0, 'Knight': 0, 'Bowman': 0, 'Warrior': 0}

# FUNCTIONS

def message_screen(message, display_x=0, display_y=0, size="small", color=GOLD, background_color=None):
	screen_text, box_text = text_objects(message, size, color)
	box_text.center = ((WIDTH/2) + display_x, (HEIGHT/2) + display_y)
	if background_color:
		pygame.gfxdraw.box(screen, pygame.Rect(box_text.topleft[0] - 10, box_text.topleft[1] - 10, screen_text.get_width() + 20, screen_text.get_height() + 20), background_color)
	screen.blit(screen_text, box_text)
	return box_text


def text_objects(text, size, color=GOLD):
	if size == "small":
		textSurface = SMALL_FONT.render(text, True, color)
	elif size == "medium":
		textSurface = MEDIUM_FONT.render(text, True, color)
	elif size == "large":
		textSurface = LARGE_FONT.render(text, True, color)
	return textSurface, textSurface.get_rect()


def button(message, x, y, width, height, color, form, action=None, action_argument={}):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()

	if form == "box":
		if x + width > mouse[0] > x and y + height > mouse[1] > y:
			pygame.gfxdraw.box(screen, pygame.Rect(x, y, width, height), color)
			if click[0] and action is not None:
				action(**action_argument)

	elif form == "circle":
		if x + width > mouse[0] > x and y + height > mouse[1] > y:
			pygame.gfxdraw.filled_circle(screen, x + int(width/2), y + int(height/2), int(width/2), color)
			if click[0] and action is not None:
				action(**action_argument)

	screen_text, box_text = text_objects(message, "medium", color=WHITE)
	box_text.center = (x + (width/2), y + (height/2))
	screen.blit(screen_text, box_text)

def button_hover_message(message, message2, x, x_message, y, y_message, width, height, color, form):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()

	if form == "box":
		if x + width > mouse[0] > x and y + height > mouse[1] > y:
			pygame.gfxdraw.box(screen, pygame.Rect(x, y, width, height), color)
			message_screen(message2, x_message, y_message, 'small', color=WHITE, background_color=BLACK)

	elif form == "circle":
		if x + width > mouse[0] > x and y + height > mouse[1] > y:
			pygame.gfxdraw.filled_circle(screen, x + int(width/2), y + int(height/2), int(width/2), color)
			message_screen(message2, x_message, y_message, 'small', color=WHITE, background_color=BLACK)

	screen_text, box_text = text_objects(message, "medium", color=WHITE)
	box_text.center = (x + (width/2), y + (height/2))
	screen.blit(screen_text, box_text)


def mute_music():
	global music_muted
	
	channel_0_for_background_sound.set_volume(0)
	channel_1_for_fight_effect_sound.set_volume(0)
	music_muted = True


def unmute_music():
	global music_muted

	channel_0_for_background_sound.set_volume(sounds_volume)
	channel_1_for_fight_effect_sound.set_volume(2 * sounds_volume)
	music_muted = False


def display_army(army, display_x, display_y):
	if army.right_side_army:
		message_screen("Allied army :", display_x=display_x, display_y=display_y, size="medium")
	else:
		message_screen("Enemy army :", display_x=display_x, display_y=display_y, size="medium")

	y = display_y + 70
	for key, val in army.units_type_number().items():
		message_screen(f"{key} : {val}", display_x=display_x, display_y=y, size="small")
		y += 50


def draw_units(unit, color, circle_radius=5, possible_movement=None):
	if possible_movement is None:
		if unit.type == 'Bowman':
			pygame.gfxdraw.filled_trigon(screen,
										 unit.box.box_position[0] + 2,
										 unit.box.center_box[1] - 1,
										 unit.box.box_position[0] + unit.box.box_size - 2,
										 unit.box.box_position[1] + 2,
										 unit.box.box_position[0] + unit.box.box_size - 2,
										 unit.box.box_position[1] + unit.box.box_size - 2,
										 color)
		elif unit.type == 'Knight':
			pygame.gfxdraw.filled_polygon(screen,
										  [
										  	(unit.box.box_position[0] + 2, unit.box.center_box[1] - 1),
										  	(unit.box.center_box[0] - 1, unit.box.box_position[1] + 2),
										  	(unit.box.box_position[0] + unit.box.box_size - 2, unit.box.center_box[1] - 1),
										  	(unit.box.center_box[0] - 1, unit.box.box_position[1] + unit.box.box_size - 2)
										  ],
										  color)
		elif unit.type == 'King':
			pygame.gfxdraw.filled_polygon(screen,
										  [
										  	(unit.box.box_position[0] + 1, unit.box.center_box[1] - 6),
										  	(unit.box.box_position[0] + 3, unit.box.center_box[1] - 6),
										  	(unit.box.box_position[0] + 3, unit.box.center_box[1] - 1),
										  	(unit.box.center_box[0] - 3, unit.box.center_box[1], - 1),
										  	(unit.box.center_box[0] - 3, unit.box.center_box[1] - 7),
										  	(unit.box.center_box[0], unit.box.center_box[1] - 7),
										  	(unit.box.center_box[0], unit.box.center_box[1] - 1),
										  	(unit.box.box_position[0] + 14, unit.box.center_box[1] - 1),
										  	(unit.box.box_position[0] + 14, unit.box.center_box[1] - 6),
										  	(unit.box.box_position[0] + 16, unit.box.center_box[1] - 6),
										  	(unit.box.box_position[0] + 16, unit.box.center_box[1] + 3),
										  	(unit.box.box_position[0] + 1, unit.box.center_box[1] + 3)
										  ],
										  color)
		elif unit.type == 'Horseman':
			pygame.gfxdraw.filled_polygon(screen,
										  [
										  	(unit.box.box_position[0] + 3, unit.box.box_position[1] + 1),
										  	(unit.box.box_position[0] + 18, unit.box.box_position[1] + 16),
										  	(unit.box.box_position[0] + 16, unit.box.box_position[1] + 17),
										  	(unit.box.box_position[0] + 1, unit.box.box_position[1] + 3)
										  ],
										  color)
		else:
			pygame.gfxdraw.filled_circle(screen, unit.box.center_box[0] - 1, unit.box.center_box[1] - 1, circle_radius, color)
	else:
		if unit.type == 'Bowman':
			pygame.gfxdraw.filled_trigon(screen,
										 possible_movement.box_position[0] + 2,
										 possible_movement.center_box[1] - 1,
										 possible_movement.box_position[0] + possible_movement.box_size - 2,
										 possible_movement.box_position[1] + 2,
										 possible_movement.box_position[0] + possible_movement.box_size - 2,
										 possible_movement.box_position[1] + possible_movement.box_size - 2,
										 color)
		elif unit.type == 'Knight':
			pygame.gfxdraw.filled_polygon(screen,
										  [
										  	(possible_movement.box_position[0] + 2, possible_movement.center_box[1] - 1),
										  	(possible_movement.center_box[0] - 1, possible_movement.box_position[1] + 2),
										  	(possible_movement.box_position[0] + possible_movement.box_size - 2, possible_movement.center_box[1] - 1),
										  	(possible_movement.center_box[0] - 1, possible_movement.box_position[1] + possible_movement.box_size - 2)
										  ],
										  color)
		elif unit.type == 'King':
			pygame.gfxdraw.filled_polygon(screen,
										  [
										  	(possible_movement.box_position[0] + 1, possible_movement.center_box[1] - 6),
										  	(possible_movement.box_position[0] + 3, possible_movement.center_box[1] - 6),
										  	(possible_movement.box_position[0] + 3, possible_movement.center_box[1] - 1),
										  	(possible_movement.center_box[0] - 3, possible_movement.center_box[1], - 1),
										  	(possible_movement.center_box[0] - 3, possible_movement.center_box[1] - 7),
										  	(possible_movement.center_box[0], possible_movement.center_box[1] - 7),
										  	(possible_movement.center_box[0], possible_movement.center_box[1] - 1),
										  	(possible_movement.box_position[0] + 14, possible_movement.center_box[1] - 1),
										  	(possible_movement.box_position[0] + 14, possible_movement.center_box[1] - 6),
										  	(possible_movement.box_position[0] + 16, possible_movement.center_box[1] - 6),
										  	(possible_movement.box_position[0] + 16, possible_movement.center_box[1] + 3),
										  	(possible_movement.box_position[0] + 1, possible_movement.center_box[1] + 3)
										  ],
										  color)
		elif unit.type == 'Horseman':
			pygame.gfxdraw.filled_polygon(screen,
										  [
										  	(possible_movement.box_position[0] + 3, possible_movement.box_position[1] + 1),
										  	(possible_movement.box_position[0] + 18, possible_movement.box_position[1] + 16),
										  	(possible_movement.box_position[0] + 16, possible_movement.box_position[1] + 17),
										  	(possible_movement.box_position[0] + 1, possible_movement.box_position[1] + 3)
										  ],
										  color)
		else:
			pygame.gfxdraw.filled_circle(screen, possible_movement.center_box[0] - 1, possible_movement.center_box[1] - 1, circle_radius, color)


def main_events(event):
	global music_paused, sounds_volume

	if event.type == pygame.QUIT:
		quitgame()
	elif event.type == pygame.KEYDOWN:
		if event.key == pygame.K_p:
			if not victory_music_played:
				if music_paused:
					channel_0_for_background_sound.unpause()
					if effect_played:
						channel_1_for_fight_effect_sound.unpause()
					music_paused = False
				else:
					channel_0_for_background_sound.pause()
					if effect_played:
						channel_1_for_fight_effect_sound.pause()
					music_paused = True
		elif event.key == pygame.K_u:
			if not victory_music_played:
				if music_muted:
					unmute_music()
				else:
					mute_music()
		elif pygame.key.get_mods() & pygame.KMOD_CTRL and event.key == pygame.K_LEFT:
			if sounds_volume > 0:
				sounds_volume -= 0.1
			else:
				sounds_volume = 0
			if not music_muted:
				channel_0_for_background_sound.set_volume(sounds_volume)
				channel_1_for_fight_effect_sound.set_volume(2 * sounds_volume)
		elif pygame.key.get_mods() & pygame.KMOD_CTRL and event.key == pygame.K_RIGHT:
			if sounds_volume < 1:
				sounds_volume += 0.1
			else:
				sounds_volume = 1
			if not music_muted:
				channel_0_for_background_sound.set_volume(sounds_volume)
				channel_1_for_fight_effect_sound.set_volume(2 * sounds_volume)


def paused(left_army, right_army, other_map, points, map_test, player_turn, object_to_move):
	global pause

	while pause:
		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)

		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		message_screen("PAUSE", display_x=0, display_y=-100, size="large")

		button("CONTINUE", 378, 350, 267, 81, RED_TRANSPARENT, "box", Continue)
		button("SAVE", 378, 479, 267, 81, RED_TRANSPARENT, "box", save_game, action_argument={
			'left_army': left_army,
			'right_army': right_army,
			'other_map': other_map,
			'map_test': map_test,
			'points': points,
			'player_turn': player_turn,
			'object_to_move': object_to_move
			})
		button("QUIT", 378, 601, 267, 81, RED_TRANSPARENT, "box", quitgame)

		pygame.display.update()
		clock.tick(FPS)


def Continue():
	global pause

	pause = False


def save_game(left_army, right_army, other_map, points, map_test, player_turn, object_to_move):
	pickle_file = open("./wargame_last_saving.p", "wb")
	pickle.dump({'left_army': left_army, 'right_army': right_army, 'other_map': other_map, 'map_test': map_test, 'points': points, 'player_turn': player_turn, 'object_to_move': object_to_move}, pickle_file)
	pickle_file.close()

	screen.fill(BLACK)
	message_screen("Your game has been saved !", display_x=0, display_y=0, size="large")
	pygame.display.update()

	pygame.time.wait(2000)


# MENU AND BUTTONS ACTIONS
def play_or_old_saving():
	pickle_file = open("./wargame_last_saving.p", "rb")
	content = pickle.load(pickle_file)
	pickle_file.close()

	pickle_file = open("./wargame_last_saving.p", "wb")
	pickle.dump("", pickle_file)
	pickle_file.close()

	while run:
		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)
		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		message_screen("A part has been saved !", display_x=0, display_y=-100, size="large")
		message_screen("What do you want to do ?", display_x=0, display_y=-50, size="medium")

		button("CONTINUE", 378, 350, 267, 81, RED_TRANSPARENT, "box", play, action_argument={
			'points': content['points'],
			'other_map': content['other_map'],
			'left_army_army_base': content['left_army'].army_base,
			'right_army_army_base': content['right_army'].army_base,
			'left_army': content['left_army'],
			'right_army': content['right_army'],
			'map_test': content['map_test'],
			'player_turn': content['player_turn'],
			'object_to_move': content['object_to_move']
			})
		button("OVERWRITE", 378, 479, 267, 81, RED_TRANSPARENT, "box", play_select)
		button("QUIT", 378, 601, 267, 81, RED_TRANSPARENT, "box", quitgame)

		pygame.display.update()
		clock.tick(FPS)


def play_select():
	if channel_0_for_background_sound.get_volume() == 0 and sounds_volume != 0 and not music_muted:
		channel_0_for_background_sound.set_volume(sounds_volume)

	map_test = Map(box_size=20, nb_river=19, nb_mountain=35, nb_forest=61, nb_desert=35)
	points = random.randint(200, 500)
	left_army = Army(map_test, False, points, in_simulation=True)

	while run:
		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)
		screen.blit(background_play_select, background_play_select_rect)
		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		display_army(left_army, 290, -140)

		button("", 482, 654, 55, 55, BLACK_TRANSPARENT, "circle", menu)
		button("OPTIMIZE", 87, 225, 281, 78, RED_TRANSPARENT, "box", play_opti, action_argument={'map_test': map_test, 'left_army': left_army, 'points': points})
		button("CREATE", 87, 438, 281, 78, RED_TRANSPARENT, "box", play_create, action_argument={'map_test': map_test, 'left_army': left_army, 'points': points})

		pygame.display.update()
		clock.tick(FPS)


def play_opti(map_test, left_army, points):
	population = 10
	generations = 25
	in_simulation = True

	screen.fill(BLACK)
	message_screen("Creation of", display_x=0, display_y=-50, size="large")
	message_screen("your army ...", display_x=0, display_y=0, size="large")
	message_screen("(Approximate duration : 15-20 seconds)", display_x=0, display_y=50, size="small")
	pygame.display.update()
	debut_best_army_ga = time.time()
	right_army = genetic_algorithm_best_army(population, generations, in_simulation, map_test.for_other_map(), points, left_army)
	print(time.time() - debut_best_army_ga)

	while run:
		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)
		screen.blit(background_play_opti, background_play_opti_rect)
		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		display_army(left_army, 320, -140)
		display_army(right_army, -325, -140)

		button("", 480, 650, 57, 57, BLACK_TRANSPARENT, "circle", play_select)
		button("VALIDATE", 371, 391, 281, 77, RED_TRANSPARENT, "box", play, action_argument={'points': points, 'other_map': map_test.for_other_map(), 'left_army_army_base': left_army.army_base, 'right_army_army_base': right_army.army_base})

		pygame.display.update()
		clock.tick(FPS)


def play_create(map_test, left_army, points):
	global dico_unit

	dico_unit_cost = {'King': 70, 'Horseman': 40, 'Knight': 30, 'Bowman': 20, 'Warrior':10}

	actual_unit = 1

	while run:
		points_select = points

		for event in pygame.event.get():
			main_events(event)
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					unit_select('-', list(dico_unit.keys())[actual_unit])
				elif event.key == pygame.K_RIGHT:
					unit_select('+', list(dico_unit.keys())[actual_unit])
				elif event.key == pygame.K_UP:
					if actual_unit == 1:
						actual_unit = 1
					else:
						actual_unit -= 1
				elif event.key == pygame.K_DOWN:
					if actual_unit == len(dico_unit) - 1:
						actual_unit = len(dico_unit) - 1
					else:
						actual_unit += 1

		for key, val in dico_unit_cost.items():
			for key2, val2 in dico_unit.items():
				if key == key2:
					points_select -= val * val2

		screen.fill(BLACK)
		screen.blit(background_play_create, background_play_create_rect)
		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		button("", 480, 650, 57, 57, BLACK_TRANSPARENT, "circle", play_select)

		if points_select >= 0:
			button("VALIDATE", 429, 387, 225, 66, RED_TRANSPARENT, "box", army_creation, action_argument={'points': points, 'map_test': map_test, 'left_army_army_base': left_army.army_base, 'dico_unit': dico_unit})

		display_army(left_army, 325, -130)

		message_screen("PTS",display_x=-430,display_y=-210,size="medium")
		message_screen("NAME",display_x=-300,display_y=-210,size="medium")
		message_screen("NB",display_x=-175,display_y=-210,size="medium")

		y = -80
		for key, val in dico_unit_cost.items():
			message_screen(f"{key}", display_x=-300, display_y=y, size="small")
			message_screen(f"{val}", display_x=-430, display_y=y, size="small")
			button_hover_message("-", 'Click in LEFT ARROW', 300, 25, 375 + y, 0, 20, 20, RED_TRANSPARENT, "box")
			message_screen(f"{dico_unit[key]}", display_x=-170, display_y=y, size="small")
			button_hover_message("+", "Click in RIGHT ARROW", 364, 25, 375 + y, 0, 20, 20, RED_TRANSPARENT, "box")
			y += 50

		message_screen(f"Maximal cost : {points}", display_x=-300, display_y=185, size="small")
		message_screen(f"Army's  cost : {points_select}", display_x=-300, display_y=215, size="small")

		pygame.display.update()
		clock.tick(FPS)


def unit_select(signe, unit_type):
	global dico_unit

	if signe == '+':
		dico_unit[unit_type] += 1
	else:
		if dico_unit[unit_type] > 0:
			dico_unit[unit_type] -= 1


def army_creation(dico_unit, map_test, left_army_army_base, points):
	map_test.create_box_from_base()
	right_army_army_base = []
	dico_unit_base = {key: val for key, val in dico_unit.items()}
	actual_selected_unit = None

	while run:
		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()

		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)

		x, y = -300, -100
		for key, val in dico_unit.items():
			if val > 0:
				box = message_screen(f"{key} : {val}", display_x=x, display_y=y, size="medium")
				y += 30
				if box.left <= mouse[0] < box.right and box.top <= mouse[1] < box.bottom:
					if click[0]:
						actual_selected_unit = key

		for box in map_test.right_side_position():
			pygame.gfxdraw.box(screen, [box.box_position[0], box.box_position[1], box.box_size, box.box_size], box.background_color)
			if box.box_position[0] <= mouse[0] < box.box_position[0] + box.box_size + 2 and box.box_position[1] <= mouse[1] < box.box_position[1] + box.box_size + 2 and box.object == None:
				pygame.gfxdraw.box(screen, [box.box_position[0], box.box_position[1], box.box_size, box.box_size], box.background_color_hover)
				if click[0] and actual_selected_unit != None:
					if actual_selected_unit == 'King':
						right_army_army_base = [(actual_selected_unit, box.center_box, unit_cost(actual_selected_unit, map_test, box))] + right_army_army_base
					else:
						right_army_army_base.append((actual_selected_unit, box.center_box, unit_cost(actual_selected_unit, map_test, box)))
					dico_unit[actual_selected_unit] -= 1
					box.object = actual_selected_unit
					actual_selected_unit = None
		
		for unit in right_army_army_base:
			if unit[0] == 'King':
				draw_units(units.King(True, map_test.research_one_box(unit[1]), map_test, create_army_with_points=True), WHITE)
			if unit[0] == 'Knight':
				draw_units(units.Knight(True, map_test.research_one_box(unit[1]), map_test, create_army_with_points=True), WHITE)
			if unit[0] == 'Horseman':
				draw_units(units.Horseman(True, map_test.research_one_box(unit[1]), map_test, create_army_with_points=True), WHITE)
			if unit[0] == 'Bowman':
				draw_units(units.Bowman(True, map_test.research_one_box(unit[1]), map_test, create_army_with_points=True), WHITE)
			else:
				draw_units(units.Warrior(True, map_test.research_one_box(unit[1]), map_test, create_army_with_points=True), WHITE)

		if dico_unit == {'King': 0, 'Horseman': 0, 'Knight': 0, 'Bowman': 0, 'Warrior': 0}:
			button("CANCEL", 87, 225, 281, 78, RED_TRANSPARENT, "box", army_creation, action_argument={'points': points, 'map_test': map_test, 'left_army_army_base': left_army_army_base, 'dico_unit': dico_unit_base})
			button("VALIDATE", 87, 438, 281, 78, RED_TRANSPARENT, "box", play, action_argument={'points': points, 'other_map': map_test.for_other_map(), 'left_army_army_base': left_army_army_base, 'right_army_army_base': right_army_army_base})
		
		pygame.display.update()
		clock.tick(FPS)


def play(other_map, points, left_army_army_base, right_army_army_base, left_army=None, right_army=None, map_test=None, player_turn=None, object_to_move=[]):
	global effect_played, sounds_volume, pause

	channel_1_for_fight_effect_sound.unpause()
	effect_played = True
	sounds_volume = 0.4
	channel_0_for_background_sound.set_volume(sounds_volume)
	channel_1_for_fight_effect_sound.set_volume(2 * sounds_volume)

	if music_paused:
		channel_1_for_fight_effect_sound.pause()

	if music_muted:
		mute_music()

	if map_test is None:
		map_test = Map(other_map=other_map)
	if left_army is None:
		left_army = Army(map_test, False, points, army_base=left_army_army_base)
	if right_army is None:
		right_army = Army(map_test, True, points, army_base=right_army_army_base)

	if player_turn is None:
		player_turn = False
	selected_unit = None
	selected_unit_boxes_movement = None
	selected_unit_boxes_attack = None
	unit_in_boxes_attack = None

	i = 0
	while run:
		mouse = pygame.mouse.get_pos()
		click = pygame.mouse.get_pressed()

		for event in pygame.event.get():
			main_events(event)
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					if pause:
						Continue()
					else:
						pause = True
						paused(left_army, right_army, other_map, points, map_test, player_turn, object_to_move)

		if player_turn:
			if object_to_move == []:
				object_to_move = [unit for unit in right_army.full_army]
		else:
			in_progress = left_army_attack(i, left_army, right_army, True)
			i += 1
			if i == len(left_army.full_army):
				i = 0
				player_turn = True
			pygame.time.wait(int(random.uniform(100, 250)))

		screen.fill(BLACK)

		if selected_unit_boxes_movement is None and selected_unit is not None:
			selected_unit_boxes_movement = selected_unit.movement_boxes_valid()
		if selected_unit_boxes_attack is None and selected_unit is not None:
			unit_in_boxes_attack, selected_unit_boxes_attack = selected_unit.attack_boxes_valid()

		for box in map_test.boxes:
			if selected_unit is not None and selected_unit_boxes_attack is not None:
				if box in unit_in_boxes_attack:
					pygame.gfxdraw.box(screen, [box.box_position[0], box.box_position[1], box.box_size, box.box_size],  RED)
				elif box in selected_unit_boxes_attack:
					pygame.gfxdraw.box(screen, [box.box_position[0], box.box_position[1], box.box_size, box.box_size],  box.background_color_attack)
				else:
					pygame.gfxdraw.box(screen, [box.box_position[0], box.box_position[1], box.box_size, box.box_size], box.background_color)
			else:
				pygame.gfxdraw.box(screen, [box.box_position[0], box.box_position[1], box.box_size, box.box_size], box.background_color)
			if box.box_position[0] <= mouse[0] < box.box_position[0] + box.box_size + 2 and box.box_position[1] <= mouse[1] < box.box_position[1] + box.box_size + 2:
				pygame.gfxdraw.box(screen, [box.box_position[0], box.box_position[1], box.box_size, box.box_size], box.background_color_hover)
				if click[0]:
					if box.object is not None and selected_unit is None and box.object in object_to_move:
						selected_unit = box.object
					if selected_unit is not None and selected_unit_boxes_movement is not None and box in selected_unit_boxes_movement:
						selected_unit.out_box()
						selected_unit.x, selected_unit.y = box.center_box
						selected_unit.enter_in_box(box)
						object_to_move.remove(selected_unit)
						selected_unit_boxes_movement = None
						selected_unit_boxes_attack = None
						unit_in_boxes_attack = None
						selected_unit = None
						if object_to_move == []:
							player_turn = False
							pygame.time.wait(100)
					if selected_unit is not None and unit_in_boxes_attack is not None and box in unit_in_boxes_attack:
						enemy_index = left_army.full_army.index(box.object)
						selected_unit.attack(left_army.full_army[enemy_index])
						if left_army.full_army[enemy_index].die():
							left_army.full_army.remove(left_army.full_army[enemy_index])
							box.object = None
						object_to_move.remove(selected_unit)
						selected_unit_boxes_movement = None
						selected_unit_boxes_attack = None
						unit_in_boxes_attack = None
						selected_unit = None
						if object_to_move == []:
							player_turn = False
							pygame.time.wait(100)
				if click[2]:
					if selected_unit == box.object:
						selected_unit = None
						selected_unit_boxes_movement = None
						selected_unit_boxes_attack = None
						unit_in_boxes_attack = None

		for unit in left_army.full_army:
			draw_units(unit, BLACK, circle_radius=5)
		for unit in right_army.full_army:
			if selected_unit is None:
				draw_units(unit, WHITE)
			else:
				if unit == selected_unit and selected_unit_boxes_movement is not None:
					for box in selected_unit_boxes_movement:
						draw_units(unit, WHITE, possible_movement=box)
					draw_units(unit, (0, 102, 102))
				else:
					draw_units(unit, (0, 102, 102))

		if left_army.full_army == [] or right_army.full_army == []:
			effect_played = False
			channel_0_for_background_sound.set_volume(0)
			channel_1_for_fight_effect_sound.pause()
			game_over(left_army, right_army)

		pygame.display.update()
		clock.tick(FPS)


def about():
	while run:
		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)
		screen.blit(background_about, background_about_rect)
		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		message_screen("PyGame version : " + pygame.version.ver, display_x=270, display_y=-180, size="small")
		message_screen("Authors :", display_x=270, display_y=-110, size="small")
		message_screen("KABORI Hamza", display_x=270, display_y=-80, size="small")
		message_screen("LETELLIER Guillaume", display_x=270, display_y=-50, size="small")
		message_screen("LUCCHINI Melvin", display_x=270, display_y=-20, size="small")
		message_screen("MOK William", display_x=270, display_y=10, size="small")
		message_screen("PAIS OLIVEIRA Lorenzo", display_x=270, display_y=40, size="small")
		message_screen("This game was made", display_x=270, display_y=110, size="small")
		message_screen("as part of a software", display_x=270, display_y=140, size="small")
		message_screen("design project at the", display_x=270, display_y=170, size="small")
		message_screen("University of Caen", display_x=270, display_y=200, size="small")

		button("", 533, 597, 47, 47, BLACK_TRANSPARENT, "circle", menu)

		pygame.display.update()
		clock.tick(FPS)


def quitgame():
	global run

	run = False
	pygame.quit()
	quit()


def game_over(left_army, right_army):
	sound_game_over = GameVictorySound()

	i = 0
	while run:
		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)

		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		if left_army.full_army == []:
			if i == 0:
				sound_game_over.play_victory(sound_volume=sounds_volume)
				i += 1
			elif i == 1 and not pygame.mixer.music.get_busy():
				sound_game_over.play_clap(sound_volume=sounds_volume)
				i += 1
			elif i == 2 and not pygame.mixer.music.get_busy():
				i += 4
				channel_0_for_background_sound.set_volume(sounds_volume)
			message_screen("VICTORY", display_x=0, display_y=-100, size="large")
		else:
			message_screen("DEFEAT", display_x=0, display_y=-100, size="large")

		button("PLAY AGAIN", 378, 350, 267, 81, RED_TRANSPARENT, "box", play_select)
		button("QUIT", 378, 550, 267, 81, RED_TRANSPARENT, "box", quitgame)

		pygame.display.update()
		clock.tick(FPS)


def menu():
	while run:
		for event in pygame.event.get():
			main_events(event)

		screen.fill(BLACK)
		screen.blit(background_menu, background_menu_rect)
		if music_muted:
			screen.blit(sound_mute, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", unmute_music)
		else:
			screen.blit(sound_speaking, (0, 0), (-940, -40, 1024, 768))
			button("", 929, 37, 57, 57, BLACK_TRANSPARENT, "circle", mute_music)

		# INTERACTIVE BUTTONS
		try:
			pickle_file = open("./wargame_last_saving.p", "rb")
			content = pickle.load(pickle_file)
			pickle_file.close()
		except FileNotFoundError:
			content = ''

		if content == '':
			button("PLAY", 684, 350, 267, 83, RED_TRANSPARENT, "box", play_select)
		else:
			button("PLAY", 684, 350, 267, 83, RED_TRANSPARENT, "box", play_or_old_saving)
		button("ABOUT", 684, 479, 267, 83, RED_TRANSPARENT, "box", about)
		button("QUIT", 684, 601, 267, 83, RED_TRANSPARENT, "box", quitgame)

		# DRAWINGS /// RETURN

		pygame.display.update()
		clock.tick(FPS)


if __name__ == '__main__':
	menu()
	quitgame()

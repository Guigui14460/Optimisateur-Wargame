from random import choice, randint


# CONSTANTE LIÉES A LA TAILLE DE LA FENÊTRE PYGAME
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768


class Box:
	"""
	Cette classe définit et créer une case.

	Paramètres :
		box_position : tuple (x, y) représentant la position du coin haut gauche de la case (pour PyGame notamment)
		box_size : entier correspondant à la taille de la case en pixels

		Optionnels :
			background_color : tuple (r, g, b) représentant une couleur associée à la case voulant être crée (pour PyGame notamment)
				Défaut : (0, 0, 0) (noir)
	"""

	def __init__(self, box_position, box_size, background_color=(0, 0, 0)):
		self.type = 'Box'
		self.box_position = (box_position[0], box_position[1])
		self.box_size = box_size - 2  # -2 : fait des bordures aux cases
		self.center_box = (int(box_position[0] + box_size / 2), int(box_position[1] + box_size / 2))  # Position du centre de la case
		self.object = None
		self.background_color = background_color
		self.background_color_hover = None
		self.background_color_attack = None
		self.right_side = None

	def __repr__(self):
		"""
		Permet de représenter l'objet Box.

		Paramètres :
			-----

		Return :
			chaîne de caractères représentant l'instance de l'objet Box
		"""
		return f"< {self.type} : {self.center_box}, object : {self.object} >"

	def malus_bonus_entry_box(self):
		"""
		Applique les malus/bonus lorsque l'unité associée à la case entre dans celle-ci.

		Paramètres :
			-----

		Return :
			None
		"""
		if self.object is not None:
			if self.type == 'Forest':
				self.object.attack_range -= 2
			elif self.type == 'Mountain':
				self.object.damage -= 7
				self.object.attack_range += 1
			elif self.type == 'Desert':
				self.object.hp -= 30
			elif self.type == 'Town':
				if self.object.right_side is self.right_side:
					self.object.damage += 10
					self.object.attack_range += 1
				else:
					self.object.damage -= 10
					self.object.attack_range -= 1

	def malus_bonus_output_box(self):
		"""
		Applique les malus/bonus lorsque l'unité associée à la case sort de celle-ci.

		Paramètres :
			-----

		Return :
			None
		"""
		if self.object is not None:
			if self.type == 'Forest':
				self.object.attack_range += 2
			elif self.type == 'Mountain':
				self.object.damage += 7
				self.object.attack_range -= 1
			elif self.type == 'Town':
				if self.object.right_side is self.right_side:
					self.object.damage -= 10
					self.object.attack_range -= 1
				else:
					self.object.damage += 10
					self.object.attack_range += 1


class Desert(Box):
	"""
	Cette classe définit et créer une case représentant un désert.

	Paramètres :
		box_position : tuple (x, y) représentant la position du coin haut gauche de la case
		box_size : entier correspondant à la taille de la case en pixels
	"""

	def __init__(self, box_position, box_size):
		Box.__init__(self, box_position, box_size, (255, 204, 0))
		self.type = 'Desert'
		self.background_color_hover = (153, 122, 0)
		self.background_color_attack = (255, 224, 102)


class Forest(Box):
	"""
	Cette classe définit et créer une case représentant une forêt.

	Paramètres :
		box_position : tuple (x, y) représentant la position du coin haut gauche de la case
		box_size : entier correspondant à la taille de la case en pixels
	"""

	def __init__(self, box_position, box_size):
		Box.__init__(self, box_position, box_size, (0, 128, 64))
		self.type = 'Forest'
		self.background_color_hover = (0, 77, 38)
		self.background_color_attack = (26, 255, 140)


class Mountain(Box):
	"""
	Cette classe définit et créer une case représentant une montagne.

	Paramètres :
		box_position : tuple (x, y) représentant la position du coin haut gauche de la case
		box_size : entier correspondant à la taille de la case en pixels
	"""

	def __init__(self, box_position, box_size):
		Box.__init__(self, box_position, box_size, (140, 140, 140))
		self.type = 'Mountain'
		self.background_color_hover = (64, 64, 64)
		self.background_color_attack = (191, 191, 191)


class Plain(Box):
	"""
	Cette classe définit et créer une case représentant une plaine.

	Paramètres :
		box_position : tuple (x, y) représentant la position du coin haut gauche de la case
		box_size : entier correspondant à la taille de la case en pixels
	"""

	def __init__(self, box_position, box_size):
		Box.__init__(self, box_position, box_size, (102, 255, 102))
		self.type = 'Plain'
		self.background_color_hover = (0, 179, 0)
		self.background_color_attack = (153, 255, 153)


class Town(Box):
	"""
	Cette classe définit et créer une case représentant une ville.

	Paramètres :
		box_position : tuple (x, y) représentant la position du coin haut gauche de la case
		box_size : entier correspondant à la taille de la case en pixels
		side : chaîne de caractère représentant le côté de la ville (pour les malus/bonus)
			Options : 'left', 'right'
	"""

	def __init__(self, box_position, box_size, side):
		if side == 'right':
			Box.__init__(self, box_position, box_size, (0, 191, 255))
			self.right_side = True
			self.background_color_hover = (0, 96, 128)
			self.background_color_attack = (102, 217, 255)
		else:
			Box.__init__(self, box_position, box_size, (255, 26, 26))
			self.right_side = False
			self.background_color_hover = (179, 0, 0)
			self.background_color_attack = (255, 102, 102)
		self.type = 'Town'


class River(Box):
	"""
	Cette classe définit et créer une case représentant une rivière.

	Paramètres :
		box_position : tuple (x, y) représentant la position du coin haut gauche de la case
		box_size : entier correspondant à la taille de la case en pixels
	"""

	def __init__(self, box_position, box_size):
		Box.__init__(self, box_position, box_size, (26, 83, 255))
		self.type = 'River'
		self.background_color_hover = (0, 38, 153)
		self.background_color_attack = (102, 140, 255)


class Map:
	"""
	Cette classe définit et créer une carte de jeu pour le combat entre 2 armées.

	Paramètres :
		Optionnels :
			map_position : tuple (x, y) correspondant à la position du point haut gauche de la carte dans la fenêtre (pour placer la carte sur une surface pour PyGame)
				Défaut : (0, 0)
			map_size : tuple (x, y) correspondant en x, à la largeur de la carte en pixels et en y, la hauteur de la carte en pixels
				Défaut : None (calculé par la suite)
			box_size : entier correspondant à la taille des cases en pixels
				Défaut : 20 pixels
			nb_river : entier correspondant au nombre de cases de type 'River' à placer sur la carte (nombre de rivières)
				Défaut : 27
			nb_mountain : entier correspondant au nombre de cases de type 'Mountain' à placer sur la carte (nombre de montagnes)
				Défaut : 49
			nb_forest : entier correspondant au nombre de cases de type 'Forest' à placer sur la carte (nombre de forêts)
				Défaut : 87
			nb_desert : entier correspondant au nombre de cases de type 'Desert' à placer sur la carte (nombre de déserts)
				Défaut : 63
			town_size : entier correspondant à la taille en nombre de case pour chaque ville (gauche ou droite)
				Défaut : 7
			other_map : dictionnaire conportant tous les paramètres cités au-dessus afin de recréer la même carte de jeu (utilisé pour l'algorithme génétique)
	"""

	def __init__(self, map_position=(0, 0), map_size=None, box_size=20, nb_river=27, nb_mountain=49, nb_forest=87, nb_desert=63, town_size=7, other_map=None):
		if other_map is None:  # Si on veut créer une nouvelle carte
			self.map_position = map_position
			if map_size is None:
				self.map_size = (WINDOW_WIDTH - self.map_position[0], WINDOW_HEIGHT - self.map_position[1])
			else:
				self.map_size = map_size
			self.box_size = box_size
			self.nb_types = {'river': randint(nb_river - 2, nb_river + 2), 'town': town_size, 'mountain': randint(nb_mountain - 2, nb_mountain + 2), 'forest': randint(nb_forest - 2, nb_forest + 2), 'desert': randint(nb_desert - 2, nb_desert + 2)}
			self.boxes_base = self.create_box_from_scratch()
		else:  # Si l'on veut recréer une carte
			self.map_position = other_map['map_position']
			if 'map_size' not in other_map:
				self.map_size = (WINDOW_WIDTH - self.map_position[0], WINDOW_HEIGHT - self.map_position[1])
			else:
				self.map_size = other_map['map_size']
			self.box_size = other_map['box_size']
			self.nb_types = other_map['types']
			self.boxes_base = other_map['boxes_base']
		self.boxes = self.create_box_from_base()

	def __repr__(self):
		"""
		Permet de représenter l'objet Map.

		Paramètres :
			-----

		Return :
			chaîne de caractères représentant l'instance de l'objet Map
		"""
		return f"< Map : Position={self.map_position}, Size={self.map_size}, BoxSize={self.box_size} >"

	def for_other_map(self):
		"""
		Permet de renvoyer les paramètres pour créer la même map mais pour un autre objet (utilisé par l'algorithme génétique).

		Paramètres :
			-----

		Return :
			dictionnaire conportant les paramètres pour une autre même map
		"""
		return {'map_position': self.map_position,
				'map_size': self.map_size,
				'box_size': self.box_size,
				'boxes_base': self.boxes_base,
				'types': self.nb_types}

	def create_box_from_scratch(self):
		"""
		Permet de créer toutes les cases qui seront sur la map.
		Création de chaque type : 1 - Ville à gauche
								  2 - Ville à droite
								  3 - Rivières
								  4 - Montagnes
								  5 - Forêts
								  6 - Déserts
								  7 - Plaines

		Return :
			liste contenant toutes les cases de la map (sous forme d'objet)
		"""
		all_box = []
		nb_box_in_width, nb_box_in_height = int(self.map_size[0] / self.box_size), int(self.map_size[1] / self.box_size)

		# Ville à gauche
		for i in range(self.nb_types['town']):
			for j in range(nb_box_in_height):
				all_box.append(('lefttown', (i*self.box_size + self.map_position[0], j*self.box_size + self.map_position[1])))
		
		# Ville à droite
		for i in range(nb_box_in_width - self.nb_types['town'], nb_box_in_width):
			for j in range(nb_box_in_height):
				all_box.append(('righttown', (i*self.box_size + self.map_position[0], j*self.box_size + self.map_position[1])))
		
		# Cases encore possibles
		possible_boxes = []
		for i in range(self.nb_types['town'], nb_box_in_width - self.nb_types['town']):
			for j in range(nb_box_in_height):
				possible_boxes.append((i*self.box_size + self.map_position[0], j*self.box_size + self.map_position[1]))
		
		# Rivières
		for nb in range(self.nb_types['river']):
			position_choice = choice(possible_boxes)
			possible_boxes.remove(position_choice)
			all_box.append(('river', position_choice))
		
		# Montagnes
		for nb in range(self.nb_types['mountain']):
			position_choice = choice(possible_boxes)
			possible_boxes.remove(position_choice)
			all_box.append(('mountain', position_choice))
		
		# Forêts
		for nb in range(self.nb_types['forest']):
			position_choice = choice(possible_boxes)
			possible_boxes.remove(position_choice)
			all_box.append(('forest', position_choice))
		
		# Déserts
		for nb in range(self.nb_types['desert']):
			position_choice = choice(possible_boxes)
			possible_boxes.remove(position_choice)
			all_box.append(('desert', position_choice))
		
		# Plaines
		for position in possible_boxes:
			all_box.append(('plain', position))
		return all_box

	def create_box_from_base(self):
		"""
		Permet de créer toutes les cases qui seront sur la map.
		Création de chaque type : 1 - Ville à gauche
								  2 - Ville à droite
								  3 - Rivières
								  4 - Montagnes
								  5 - Forêts
								  6 - Déserts
								  7 - Plaines

		Paramètres :
			-----

		Return :
			liste contenant toutes les cases de la map (sous forme d'objet Box)
		"""
		all_box = []
		for box in self.boxes_base:
			if box[0] == 'lefttown':
				all_box.append(Town(box[1], self.box_size, 'left'))
			elif box[0] == 'righttown':
				all_box.append(Town(box[1], self.box_size, 'right'))
			elif box[0] == 'river':
				all_box.append(River(box[1], self.box_size))
			elif box[0] == 'mountain':
				all_box.append(Mountain(box[1], self.box_size))
			elif box[0] == 'forest':
				all_box.append(Forest(box[1], self.box_size))
			elif box[0] == 'desert':
				all_box.append(Desert(box[1], self.box_size))
			else:
				all_box.append(Plain(box[1], self.box_size))
		return all_box

	def research_valid_position(self):
		"""
		Recherche toutes les cases valides (où l'on peut se déplacer dessus).

		Paramètres :
			-----

		Return :
			liste d'objets Box si les cases sont disponibles et valides (pas d'objet sur la case et pas une rivière)
		"""
		return [box for box in self.boxes if box.type != 'River' and box.object is None]

	def research_one_box(self, position):
		"""
		Permet de choisir une case qui correspond à une position choisie (ne compare que le centre de la case).

		Paramètres :
			position : tuple (x, y) correspondant à la position à trouver

		Return :
			- box : objet Box trouvé
			- None : si la position recherchée est inconnue
		"""
		for box in self.boxes:
			if box.center_box == position:
				return box
		return None

	def research_one_valid_box(self, position):
		"""
		Recherche une case valide associée à la position choisie (où l'on peut se déplacer dessus).

		Paramètres :
			position : tuple (x, y) représentant la position où l'on souhaite déplacer l'unité

		Return :
			- box : objet Box si elle est disponible et valide
			- None : si la position n'est pas disponible
		"""
		for box in self.boxes:
			if box.center_box == position and box.type != 'River':
				if box.object is None:
					return box
				else:
					break  # Utilisation du break pour aller plus vite car la position n'est associée qu'à une seule case
		return None

	def right_side_position(self):
		"""
		Récupère les cases du côté droit.

		Paramètres :
			-----

		Return :
			liste contenant toutes les cases du côté droit (hors rivières)
		"""
		positions = [box for box in self.boxes if (self.map_size[0] / 2 + self.map_position[0], self.map_size[1] / 2 + self.map_position[1]) < box.center_box]
		return [box for box in positions if box.type != 'River']

	def left_side_position(self):
		"""
		Récupère les cases du côté gauche.

		Paramètres :
			-----

		Return :
			liste contenant toutes les cases du côté gauche (hors rivières)
		"""
		positions = [box for box in self.boxes if (self.map_size[0] / 2 + self.map_position[0], self.map_size[1] / 2 + self.map_position[1]) > box.center_box]
		return [box for box in positions if box.type != 'River']

	def number_of_each_type(self):
		"""
		Récupère le nombre de case pour chaque type de case (permet de vérifier lors du TEST #1).

		Paramètres :
			-----

		Return :
			dict1 : dictionnaire représentant le type d'une case et la valeur, un entier le nombre de case de ce type dans la map
		"""
		dict1 = {'plain': 0, 'river': 0, 'mountain': 0, 'town': 0, 'forest': 0, 'desert': 0}
		for box in self.boxes:
			if box.type == 'Plain':
				dict1['plain'] += 1
			elif box.type == 'River':
				dict1['river'] += 1
			elif box.type == 'Mountain':
				dict1['mountain'] += 1
			elif box.type == 'Town':
				dict1['town'] += 1
			elif box.type == 'Forest':
				dict1['forest'] += 1
			else:
				dict1['desert'] += 1
		return dict1


if __name__ == '__main__':
	from units import Horseman, King


	message = """0 - Test des cases (avec unités, malus/bonus)
1 - Test de la carte (vérification des cases crées, disponibles)"""
	print(message)
	choix = int(input('Quel test voulez-vous réaliser ? '))

	##### TEST SUR LES CASES #####
	if choix == 0:
		plain1 = Plain((500,500), 20)
		desert1 = Desert((500,500), 20)
		right_town = Town((500,500), 20, 'right')

		unit1 = Horseman(True, plain1, None)
		unit2 = Horseman(True, desert1, None)
		unit3 = Horseman(False, right_town, None)

		plain1.object = unit1
		desert1.object = unit2
		right_town.object = unit3
		print('Centre de l\'objet plain1 :', plain1.center_box)

		print('---------------------------------------------------------------------------------------------')
		print('Les unités rentrent dans leur case ...')
		print((unit1.attack_range, unit1.hp, unit1.damage), (unit2.attack_range, unit2.hp, unit2.damage), (unit3.attack_range, unit3.hp, unit3.damage))
		plain1.malus_bonus_entry_box()
		desert1.malus_bonus_entry_box()
		right_town.malus_bonus_entry_box()

		print('---------------------------------------------------------------------------------------------')
		print('Changements des valeurs ...')
		print((unit1.attack_range, unit1.hp, unit1.damage), (unit2.attack_range, unit2.hp, unit2.damage), (unit3.attack_range, unit3.hp, unit3.damage))
		plain1.malus_bonus_output_box()
		desert1.malus_bonus_output_box()
		right_town.malus_bonus_output_box()

		print('---------------------------------------------------------------------------------------------')
		print('Les unités sortent de leur case ...')
		print((unit1.attack_range, unit1.hp, unit1.damage), (unit2.attack_range, unit2.hp, unit2.damage), (unit3.attack_range, unit3.hp, unit3.damage))
		print('---------------------------------------------------------------------------------------------')

		river1 = River((400, 400), 100)
		print("Centre de la case river1 :", river1.center_box)
		print("Couleur de la rivière :", river1.background_color)
	
	##### TEST SUR LA CARTE #####
	elif choix == 1:
		map_test = Map()
		print(map_test)

		print('---------------------------------------------------------------------------------------------')
		print('Recherche de la case de coordonnées centrale x=230 et y=90) :', map_test.research_one_box((230, 90)))
		print('---------------------------------------------------------------------------------------------')

		valid = map_test.research_valid_position()
		for v in valid:
			print(v)

		print('---------------------------------------------------------------------------------------------')
		map_test.research_one_box((950, 750)).object = King(True, choice(map_test.boxes), map_test)
		print('---------------------------------------------------------------------------------------------')

		valid = map_test.research_valid_position()
		for v in valid:
			print(v)
		
		print('---------------------------------------------------------------------------------------------')
		print('Case contenant une unité :', map_test.research_one_box((950, 750)))
		print('---------------------------------------------------------------------------------------------')

		print(map_test.number_of_each_type())

		print("Nombre de case du côté gauche (hors rivière) :", len(map_test.left_side_position()))
		print("Nombre de case du côté droit (hors rivière) :", len(map_test.right_side_position()))

from random import choice, uniform
from army import Army
from mapping import Map
from thread_simulation import SimulatorThreaded
from utils import unit_choice, unit_cost, unit_position_choice


def parent1_choice(parent1, points):
	"""
	Permet de choisir des unités aléatoirement dans l'armée du premier parent.

	Paramètres :
		parent1 : objet Army (from army import Army) représentant le premier parent
		points : entier représentant les fonds disponibles pour créer l'armée

	Return :
		(units_chosen, points_choice)
			units_chosen : liste représentant les unités choisies dans l'armée du premier parent
			points_choice : entier représentant les points utilisés
	"""
	points_choice = 0
	units_chosen = []
	i = 0
	while points_choice + parent1.army_base[i][2] < points / 2:  # Choisi seulement dans une limite de points équivaut à la moitié des fonds disponibles
		units_chosen.append(parent1.army_base[i])
		points_choice += units_chosen[i][2]
		i += 1
	return units_chosen, points_choice

def parent2_choice(parent2, points_used, parent1):
	"""
	Permet de choisir des unités dans l'armée du second parent.
	Tester avec incrémentation et décrémentation (actuel).

	Paramètres :
		parent2 : objet Army (from army import Army) représentant l'armée du second parent
		points_used : entier représentant les points déjà utilisés par la fonction 'parent1_choice'
		parent1 : objet Army (from army import Army) représentant l'armée du premier parent

	Return :
		army_parent2 : liste représentant les unités choisies dans l'armée du second parent
	"""
	points = parent1.points - points_used
	position_available = parent1.position_available
	army_parent2 = []
	i = len(parent2.army_base) - 1
	while points >= 10:
		unit_chosen = parent2.army_base[i]
		cost = unit_chosen[2]
		if cost <= points:
			position = unit_position_choice(position_available)
			unit_chosen = (unit_chosen[0], position.center_box, unit_chosen[2])
			position_available.remove(position)
			army_parent2.append(unit_chosen)
			points -= unit_chosen[2]
		i -= 1
		if i == 0:
			break
	return army_parent2

def genetic_algorithm_best_army(population, generations, in_simulation, mapping, points, left_army):
	"""
	Permet de trouver l'armée la plus forte contre un certaine armée et une certaine carte données.

	Paramètres :
		population : entier représentant le nombre d'armée alliée à tester pour une génération
		générations : entier représentant le nombre de fois qu'il faut itérer l'algorithme
		in_simulation : booléen (False si c'est pas une simulation, True si s'en est une)
		mapping : objet Map (from mapping import Map) représentant la carte de combat
		points : entier représentant les fonds disponibles pour créer l'armée
		left_army : objet Army (from army import Army)

	Return :
		armies[0] : objet Army représentant la meilleure armée alliée
	"""
	armies = init_simu(population, in_simulation, mapping, points)
	for generation in range(generations):
		print('Génération :', str(generation + 1))
		armies = fitness(armies, left_army, mapping, points, in_simulation)  # Simulations
		armies = selection(armies)  # Classement des armées
		armies = crossover(armies, points, population, mapping)  # Croisements des armées gardées
		armies = mutation(armies, points)  # Mutation des armées
		if generation == generations - 1:  # Permet d'exécuter une dernière sélection
			print('Dernière sélection ...')
			armies = fitness(armies, left_army, mapping, points, in_simulation)
			armies = selection(armies)
	return armies[0]

def init_simu(population, in_simulation, mapping, points):
	"""
	Permet de créer les premières armées.

	Paramètres :
		population : entier représentant le nombre d'armée alliée à tester pour une génération
		in_simulation : booléen (False si c'est pas une simulation, True si s'en est une)
		mapping : objet Map (from mapping import Map) représentant la carte de combat
		points : entier représentant les fonds disponibles pour créer l'armée
	"""
	return [Army(Map(other_map=mapping), True, points, in_simulation=in_simulation) for _ in range(population)]

def fitness(armies, left_army, mapping, points, in_simulation):
	"""
	Permet de calculer la résistance de l'armée après une simulation.
	Utilisation des simulations parallèles (from thread_simulation import SimulatorThreaded).

	Paramètres :
		armies : liste contenant toutes les objets Army créées
		left_army : objet Army (from army import Army) représentant l'armée ennemie
		mapping : objet Map (from mapping import Map) représentant la carte du combat
		points : entier représentant les fonds disponibles pour créer l'armée
		in_simulation : booléen (False si c'est pas une simulation, True si s'en est une)

	Return :
		armies : liste contenant les objets Army après combat
	"""
	# Thread
	thread_all = [SimulatorThreaded(Map(other_map=armies[i].mapping.for_other_map()), armies[i], left_army.army_base, points, in_simulation=in_simulation) for i in range(len(armies))]
	for thread in thread_all:
		thread.start()
	for i in range(len(thread_all)):
		armies[i].fitness = thread_all[i].join()	
	return armies

def selection(armies):
	"""
	Permet de sélectionner la première moitié des armées (les meilleures, les plus résistantes).

	Paramètres :
		armies : liste contenant tous les objets Army (armées alliées déjà créées)

	Return :
		armies : liste contenant les objets Army après sélection
	"""
	armies = sorted(armies, reverse=True, key=lambda single_army: single_army.fitness)
	armies = armies[:int(len(armies) / 2)]
	return armies

def crossover(armies, points, population, mapping):
	"""
	Permet de croiser 2 parents.

	Paramètres :
		armies : liste contenant tous les objets Army (armées alliées déjà créées)
		points : entier représentant les fonds disponibles pour créer l'armée
		population : entier représentant le nombre d'armée alliée à tester pour une génération
		mapping : objet Map (from mapping import Map) représentant la carte de combat

	Return :
		armies : liste contenant les objets Army après croisement
	"""
	offspring = []
	for _ in range(int(population - len(armies))):
		parent1, parent2 = None, None
		while parent1 == parent2:
			parent1 = choice(armies)
			parent2 = choice(armies)
		army_parent1, points_used_parent1 = parent1_choice(parent1, points)
		army_parent2 = parent2_choice(parent2, points_used_parent1, parent1)
		child1 = army_parent1 + army_parent2
		offspring.append(Army(Map(other_map=mapping), True, points, in_simulation=True, army_base=child1))
	armies.extend(offspring)
	return armies

def mutation(armies, points):
	"""
	Permet de muter les armées.

	Paramètres :
		armies : liste contenant tous les objets Army (armées alliées déjà créées)
		points : entier représentant les fonds disponibles pour créer l'armée

	Return :
		armies : liste contenant les objets Army après mutation
	"""
	for single_army in armies:
		for index, old_unit in enumerate(single_army.army_base):  # Énumération des unités de l'armée qu'on veut muter
			if uniform(0, 1.0) <= 0.05:  # Probabilité de mutation de 5%
				position = unit_position_choice(single_army.position_available)
				new_unit = (old_unit[0], position.center_box, old_unit[2])
				single_army.army_base = single_army.army_base[0:index] + [new_unit] + single_army.army_base[index + 1:]
				break  # Permet de muter seulement une unité dans l'armée
		single_army.create_army_from_base()  # Recréation des armées
	return armies


if __name__ == '__main__':
	from time import time
	

	population = 10
	generations = 25

	debut = time()

	# Création des constantes (listes de positions dispo, quantité de fonds dispo, ...)
	map_test = Map()
	other_map = map_test.for_other_map()
	points = 300
	in_simulation = True

	# Choix ordinateur
	left_army = Army(map_test, False, points)


	best_army = genetic_algorithm_best_army(population, generations, in_simulation, other_map, points, left_army)
	print(best_army.army_base)


	print("Durée totale :", int(time() - debut), 'secondes.')

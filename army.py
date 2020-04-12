from random import choice
from units import Bowman, Horseman, King, Knight, Warrior
from utils import unit_choice, unit_cost, unit_position_choice


class Army:
    """
    Cette classe définit une armée entière.

    Paramètres :
        mapping : objet Map (from mapping import Map) représentant la carte sur laquelle le combat va se passer
        right_side_army : booléen (False si c'est un ennemi qui se trouve à gauche (côté ordinateur) et True s'il se trouve à droite (côté joueur))
        points : entier correspondant à l'argent disponible pour créer l'armée

        Optionnel :
            in_simulation : booléen (False si c'est pas une simulation, True si s'en est une)
                Défaut : False
                Options : True, False
            army_base : liste contenant une armée déjà constituée
                Défaut : None
                Options : n'importe quelle liste
    """
    number_army = 0  # Attribut de classe qui servira à désigner chaque unité par un ID (plus facile à repérer)

    def __init__(self, mapping, right_side_army, points, in_simulation=False, army_base=None):
        Army.number_army += 1
        self.id = self.number_army
        self.mapping = mapping
        self.right_side_army = right_side_army
        if right_side_army:
            self.position_available = self.mapping.right_side_position()
        else:
            self.position_available = self.mapping.left_side_position()
        self.points = points
        self.in_simulation = in_simulation
        self.army_base = army_base
        self.full_army = []
        self.fitness = 0

        if self.army_base is None:  # Si on veut produire une nouvelle armée
            self.army_base = []
            self.create_army_from_scratch(self.points)

        self.create_army_from_base()

    def __repr__(self):
        """
        Représentation de l'objet Army.

        Paramètres :
            -----

        Return :
            chaîne de caractères représentant l'instance de la classe Army
        """
        return f'<Army ID : {self.id}, Fitness : {self.fitness}>'

    def __str__(self):
        """
        Affichage de l'objet.

        Paramètres :
            -----

        Return :
            None
        """
        return f"ID : {self.id} Fitness : {self.fitness} Number of unit : {len(self.full_army)}"

    def position_choice_by_army(self):
        """
        Permet de choisir aléatoirement une position disponible dans la liste 'self.position_available'.

        Paramètres :
            -----
        
        Return :
            position : objet Box représentant la case choisie
        """
        position = None
        if self.right_side_army and not self.in_simulation:  # Joueur non simulé
            x = int(input("Choisissez une valeur de x : "))
            y = int(input("Choisissez une valeur de y : "))
            if self.mapping.research_one_box((x,y)) is not None:
                position = self.mapping.research_one_box((x,y))

        if position is None:
            position = unit_position_choice(self.position_available)

        self.position_available.remove(position)
        return position

    def create_army_from_scratch(self, points):
        """
        Créer une armée à partir des points données lors de l'instanciation.

        Paramètres :
            points : entier correspondant au coût maximal disponible pour créer l'armée

        Return :
            None
        """
        unit_available = ['Warrior', 'Bowman', 'Knight', 'Horseman']
        while points >= 10:
            if not any([True if unit[0] == 'King' else False for unit in self.army_base]):  # S'il n'y a pas de 'King' dans l'armée de base
                unit_chosen = 'King'
            elif self.right_side_army and not self.in_simulation:  # Joueur
                unit_chosen, unit_available = unit_choice(self.right_side_army, points, unit_available=unit_available)
            else:  # Ordinateur (ou Joueur dans la simulation)
                unit_chosen, unit_available = unit_choice(self.right_side_army and not self.in_simulation, points, unit_available=unit_available)

            unit_position = self.position_choice_by_army()

            cost = unit_cost(unit_chosen, self.mapping, unit_position)
            points -= cost

            self.army_base.append((unit_chosen, unit_position.center_box, cost))

    def create_army_from_base(self):
        """
        Créer l'armée par rapport aux unités et leurs positions associées dans 'self.army_base'.

        Paramètres :
            -----

        Return :
            None
        """
        self.full_army = []
        for unit in self.army_base:
            if unit[0] == 'King':
                if self.right_side_army:
                    unit_chosen = King(True, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                else:
                    unit_chosen = King(False, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
            else:
                if unit[0] == 'Knight':
                    if self.right_side_army:
                        unit_chosen = Knight(True, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                    else:
                        unit_chosen = Knight(False, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                elif unit[0] == 'Bowman':
                    if self.right_side_army:
                        unit_chosen = Bowman(True, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                    else:
                        unit_chosen = Bowman(False, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                elif unit[0] == 'Warrior':
                    if self.right_side_army:
                        unit_chosen = Warrior(True, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                    else:
                        unit_chosen = Warrior(False, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                else:
                    if self.right_side_army:
                        unit_chosen = Horseman(True, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                    else:
                        unit_chosen = Horseman(False, self.mapping.research_one_box(unit[1]), self.mapping, create_army_with_points=self.in_simulation)
                self.full_army[0].append_allies(unit_chosen)
            self.full_army.append(unit_chosen)

    def units_type_number(self):
        """
        Permet de donner le nombre d'unité de chaque type qui se trouve dans l'armée.

        Paramètres :
            -----

        Return :
            dico : dictionnaire représentant le nombre d'unité pour chaque type
        """
        dico = {'King': 0,
                'Horseman': 0,
                'Knight': 0,
                'Bowman': 0,
                'Warrior': 0}
        for unit in self.army_base:
            dico[unit[0]] += 1
        return dico


if __name__ == '__main__':
    from mapping import Map


    message = """0 - Armée alliée 1 (en simulation)
1 - Armée alliée 2 (en réel)
2 - Armée ennemie 1 (en simulation)
3 - Armée ennemie 2 (en réel)"""
    print(message)
    choix = int(input('Quel test voulez-vous effectuer ? '))

    map_test = Map(nb_river=200)

    ##### TEST 0 SUR LES ARMÉES #####
    if choix == 0:
        army_test = Army(map_test, True, 300, in_simulation=True)

    ##### TEST 1 SUR LES ARMÉES #####
    elif choix == 1:
        army_test = Army(map_test, True, 300, in_simulation=False)

    ##### TEST 2 SUR LES ARMÉES #####
    elif choix == 2:
        army_test = Army(map_test, False, 300, in_simulation=True)

    ##### TEST 3 SUR LES ARMÉES #####
    elif choix == 3:
        army_test = Army(map_test, False, 300, in_simulation=False)

    else:
        army_test = Army(map_test, True, 300, in_simulation=True)
        army_test.full_army = []
    for unit in army_test.full_army:
        print(unit.box)
    print(army_test)

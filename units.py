from math import sqrt
from time import time


class Unit:
    """
    Permet de définir et de créer une unité.

    Paramètres :
        right_side : booléen (False si c'est un ennemi qui se trouve à gauche et True s'il se trouve à droite)
        box : objet Box (from mapping import Box) représentant la case qui a été choisie pour placer l'unité
        mapping : objet Map (from mapping import Map) représentant la carte sur laquelle le combat va se passer

        Optionnels :
            create_army_with_points : booléen correspondant au fait s'il l'unité est utilisé pour la simulation de l'armée ou dans la création pour combattre ensuite
                Défaut : False (combat)
                Option : True (simulation)
    """
    unit_number = 0  # Attribut de classe qui servira à désigner chaque unité par un ID (plus facile à repérer)

    def __init__(self, right_side, box, mapping, create_army_with_points=False):
        self.type = 'Unit'
        if not create_army_with_points:  # Incrémentation de l'attribut de classe si l'unité combat
            Unit.unit_number += 1
        self.id = self.unit_number
        self.mapping = mapping
        self.hp = 1
        self.damage = 0
        self.movement = 1
        self.attack_range = 4
        self.armor = 10
        self.cost = 0
        self.box = box
        self.x, self.y = box.center_box
        self.right_side = right_side
        self.moral = 100
        self.forces = []
        self.historical = {}

    def __repr__(self):
        """
        Permet de représenter une unité.

        Paramètres :
            -----

        Return :
            chaîne de caractères représentant l'instance de la classe
        """
        return f'<ID : {self.id} Type : {self.type} Ennemi : {not self.right_side}>'

    def enter_in_box(self, box):
        """
        Applique les changements nécessaires pour l'entrée de la case où l'unité arrive.

        Paramètres :
            box : objet Box représentant la case où l'unité arrive

        Return :
            None
        """
        self.box = box  # Lie la case à l'objet Unit
        self.box.object = self  # Lie l'objet Unit à la case
        self.box.malus_bonus_entry_box()  # Activation des malus/bonus associés à la case

    def out_box(self):
        """
        Applique les changements nécessaires pour la sortie de la case où l'unité se trouve.

        Paramètres :
            -----

        Return :
            None
        """
        self.box.malus_bonus_output_box()  # Désactivation des malus/bonus de la case
        self.box.object = None  # Délie l'objet Unit de la case
        self.box = None  # Délie la case de l'objet Unit

    def can_attack(self, enemy_x, enemy_y):
        """
        Méthode qui permet de vérifier si l'ennemi est attaquable ou non.

        Paramètres :
            enemy_x : entier représentant la position de l'ennemi en x
            enemy_y : entier représentant la position de l'ennemi en y

        Return :
            - True si la distance est inférieure ou égale à la distance d'attaque
            - False si la distance est supérieure à la distance d'attaque
        """
        # Utilisation de la formule de distance entre deux points (sur une surface)
        return sqrt((enemy_x - self.x)**2 + (enemy_y - self.y)**2) <= self.attack_range * self.mapping.box_size

    def can_move(self, x, y):
        """
        Vérifie si la position est valide ou non.

        Paramètres :
            x : entier représentant la position de l'unité sur l'axe des abscisses
            y : entier représentant la position de l'unité sur l'axe des ordonnées

        Return :
            - found si une case valide a été trouvée : représente une case (objet Box)
            - None sinon
        """
        found = self.mapping.research_one_valid_box((x, y))
        if found is not None:
            return found

    def attack_boxes_valid(self):
        """
        Permet de chercher toutes les cases que l'unité peut attaquer.

        Paramètres :
            -----

        Return :
            tuple (enemy_unit_in_attack_range, box_in_attack_range)
                enemy_unit_in_attack_range : liste comportant toutes les cases où il y a des ennemis sur celles-ci
                box_in_attack_range : liste comportant toutes les cases qui se trouvent dans la portée d'attaque de l'unité
        """
        distance = self.attack_range * self.mapping.box_size
        enemy_unit_in_attack_range = []
        box_in_attack_range = []
        for x in range(self.x - distance, self.x + distance + 1, self.mapping.box_size):
            for y in range(self.y - distance, self.y + distance + 1, self.mapping.box_size):
                if self.can_attack(x, y):
                    found = self.mapping.research_one_box((x, y))
                    box_in_attack_range.append(found)
                    if found is not None:
                        if found.object is not None and not found.object.right_side:  # Si l'objet est lié à la case et si l'objet de la case est un ennemi
                            enemy_unit_in_attack_range.append(found)
        return enemy_unit_in_attack_range, box_in_attack_range

    def movement_boxes_valid(self):
        """
        Permet de chercher toutes les cases qui se trouve dans la portée de déplacement de l'unité.
        Ne renvoie que les cases disponibles (sans les rivières et les cases où il y a déjà un objet dessus).

        Paramètres :
            -----

        Return :
            box_in_movement_range : liste représentant toutes les cases où l'unité peut se déplacer
        """
        distance = self.movement * self.mapping.box_size
        box_in_movement_range = []
        for x in range(self.x - distance, self.x + distance + 1, self.mapping.box_size):
            for y in range(self.y - distance, self.y + distance + 1, self.mapping.box_size):
                # Formule de distance (2 points)
                dist = sqrt((x - self.x)**2 + (y - self.y)**2)
                if distance >= dist:
                    found = self.can_move(x, y)
                    if found is not None:
                        box_in_movement_range.append(found)
        return box_in_movement_range

    def movement_method(self, enemy_x, enemy_y):
        """
        Méthode de classe permettant de faire déplacer l'unité (utilisation des vecteurs).

        Paramètres :
            enemy_x : entier représentant la position de l'ennemi en x
            enemy_y : entier représentant la position de l'ennemi en y

        Return :
            None
        """
        x, y = int(self.x), int(self.y)

        if self.x <= self.mapping.map_position[0] or self.x >= self.mapping.map_position[0] + self.mapping.map_size[0]:
            if self.x <= self.mapping.map_position[0]:
                x += self.movement*self.mapping.box_size
            else:
                x -= self.movement*self.mapping.box_size
        else:
            if enemy_x < self.x and abs(enemy_x - self.x) > self.attack_range * self.mapping.box_size:
                x -= self.movement*self.mapping.box_size
            elif enemy_x > self.x and abs(enemy_x - self.x) > self.attack_range * self.mapping.box_size:
                x += self.movement*self.mapping.box_size

        if self.y <= self.mapping.map_position[1] or self.y >= self.mapping.map_position[1] + self.mapping.map_size[1]:
            if y <= self.mapping.map_position[1]:
                y += self.movement*self.mapping.box_size
            else:
                y -= self.movement*self.mapping.box_size
        else:
            if enemy_y < self.y and abs(enemy_y - self.y) > self.attack_range * self.mapping.box_size:
                y -= self.movement*self.mapping.box_size
            elif enemy_y > self.y and abs(enemy_y - self.y) > self.attack_range * self.mapping.box_size:
                y += self.movement*self.mapping.box_size

        found = self.can_move(x, y)
        # Si c'est possible
        if found is not None:
            self.out_box()
            self.x, self.y = x, y
            self.logging((self.x, self.y))
            self.enter_in_box(found)
        # Si c'est pas possible
        else:
            aside_boxes = [(self.x - self.mapping.box_size, self.y - self.mapping.box_size),
                           (self.x, self.y - self.mapping.box_size),
                           (self.x + self.mapping.box_size, self.y - self.mapping.box_size),
                           (self.x + self.mapping.box_size, self.y),
                           (self.x + self.mapping.box_size, self.y + self.mapping.box_size),
                           (self.x, self.y + self.mapping.box_size),
                           (self.x - self.mapping.box_size, self.y + self.mapping.box_size),
                           (self.x - self.mapping.box_size, self.y)]
            for box in aside_boxes:
                found = self.can_move(box[0], box[1])
                # Si c'est possible de bouger sur une case adjacente
                if found is not None:
                    self.out_box()
                    self.x, self.y = box[0], box[1]
                    self.logging((self.x, self.y))
                    self.enter_in_box(found)
                    break

    def attack(self, target):
        """
        Permet d'attaquer un ennemi.

        Paramètres :
            target : objet représentant l'ennemi à attaquer

        Return :
            None
        """
        if self.can_attack(target.x, target.y):  # Vérifie que l'ennemi est attaquable
            if target.type in self.forces:
                damage = self.damage * 1.5
            else:
                damage = self.damage
            if target.armor <= 0:
                target.armor = 0
                # Enlève les points d'attaque aux points de vie si la vie de l'armure est nulle ou négative
                target.hp -= damage
            else:
                target.armor -= damage
                if target.armor <= 0:
                    target.hp -= abs(target.armor)
                    target.armor = 0  # Enlève les points d'armure et de vie si l'armure ne peut pas tout absorber
        else:
            # Ennemi pas attaquable => l'objet bouge
            self.movement_method(target.x, target.y)

    def die(self):
        """
        Vérifie si les points de vie de l'objet sont négatifs ou nuls.

        Paramètres :
            -----

        Return :
            - True si les points de vie de l'objet sont négatifs ou nuls
            - None si la condition n'est pas satisfaite
        """
        if self.hp <= 0:
            self.hp = 0
            self.out_box()
            return True

    def logging(self, last_position):
        """
        Permet d'écrire la position de l'unité et de la dernière fois où elle s'y trouvait.

        Paramètres :
            last_position : tuple, chaine de caractère ou objet (Box) représentant la dernière position de l'unité à un temps précis

        Return :
            None
        """
        time_at_last_position = time()
        self.historical[last_position] = time_at_last_position

    def is_surrounded(self):
        """
        Vérifie si l'unité est encerclée ou non et appelle la méthode pour appliquer les malus et bonus en fonction du nombre d'alliés et d'ennemis.

        Paramètres :
            -----

        Return :
            None
        """
        aside_boxes = [(self.x - self.mapping.box_size, self.y - self.mapping.box_size),
                       (self.x, self.y - self.mapping.box_size),
                       (self.x + self.mapping.box_size, self.y - self.mapping.box_size),
                       (self.x + self.mapping.box_size, self.y),
                       (self.x + self.mapping.box_size, self.y + self.mapping.box_size),
                       (self.x, self.y + self.mapping.box_size),
                       (self.x - self.mapping.box_size, self.y + self.mapping.box_size),
                       (self.x - self.mapping.box_size, self.y)]
        box = self.mapping.research_one_box((self.x, self.y))
        ally_unit_in_aside_box = []
        enemy_unit_in_aside_box = []
        for box in aside_boxes:
            new_box = self.mapping.research_one_box(box)
            if new_box is not None and new_box.object is not None:
                if new_box.object.right_side is self.right_side:
                    ally_unit_in_aside_box.append(new_box.object)
                else:
                    enemy_unit_in_aside_box.append(new_box.object)
        # Si il y a autant d'alliées que d'ennemies
        if len(ally_unit_in_aside_box) == len(enemy_unit_in_aside_box):
            pass
        # Si il y a plus d'alliées que d'ennemies
        elif len(ally_unit_in_aside_box) > len(enemy_unit_in_aside_box):
            for unit in ally_unit_in_aside_box:
                unit.surrounded_malus_bonus(True)
            self.surrounded_malus_bonus(True)
            for unit in enemy_unit_in_aside_box:
                unit.surrounded_malus_bonus(False)
        # Si il y a plus d'ennemies que d'alliées
        else:
            for unit in ally_unit_in_aside_box:
                unit.surrounded_malus_bonus(False)
            self.surrounded_malus_bonus(False)
            for unit in enemy_unit_in_aside_box:
                unit.surrounded_malus_bonus(True)

    def surrounded_malus_bonus(self, bonus):
        """
        Applique un malus ou un bonus si l'unité est encerclée.

        Paramètres :
            bonus : booléen représentant l'application du bonus

        Return :
            None
        """
        if bonus:
            self.moral *= 1.1
            self.damage *= 1.02
            self.attack_range *= 1.02
        else:
            self.moral *= 0.9
            if self.moral <= 50:
                self.damage *= 0.95
                self.attack_range *= 0.95


class Bowman(Unit):
    """
    Cette classe définit les archers par :
        - ses points de vie (hp)
        - ses dégâts d'attaque (damage)
        - sa distance maxiamale de déplacement (movement)
        - sa distance minimale d'attaque (attack_range)
        - son coût en points d'armée (cost)

    Paramètres :
        right_side : booléen (False si c'est un ennemi qui se trouve à gauche et True s'il se trouve à droite)
        box : objet Box (from mapping import Box) représentant la case qui a été choisie pour placer l'unité
        mapping : objet Map (from mapping import Map) représentant la carte sur laquelle le combat va se passer

        Optionnel :
            create_army_with_points : booléen correspondant au fait s'il l'unité est utilisé pour la simulation de l'armée ou dans la création pour combattre ensuite
                Défaut : False (combat)
                Option : True (simulation)
    """

    def __init__(self, right_side, box, mapping, create_army_with_points=False):
        Unit.__init__(self, right_side, box, mapping, create_army_with_points)  # Initialisation de la classe parent Unit
        self.type = "Bowman"
        self.hp = 200
        self.damage = 45
        self.movement = 6
        self.attack_range = 12
        self.armor = 75
        self.cost = 20
        self.forces = ['Horseman', 'Bowman']
        self.enter_in_box(box)


class Horseman(Unit):
    """
    Cette classe définit les cavaliers par :
        - ses points de vie (hp)
        - ses dégâts d'attaque (damage)
        - sa distance maxiamale de déplacement (movement)
        - sa distance minimale d'attaque (attack_range)
        - son coût en points d'armée (cost)

    Paramètres :
        right_side : booléen (False si c'est un ennemi qui se trouve à gauche et True s'il se trouve à droite)
        box : objet Box (from mapping import Box) représentant la case qui a été choisie pour placer l'unité
        mapping : objet Map (from mapping import Map) représentant la carte sur laquelle le combat va se passer

        Optionnel :
            create_army_with_points : booléen correspondant au fait s'il l'unité est utilisé pour la simulation de l'armée ou dans la création pour combattre ensuite
                Défaut : False (combat)
                Option : True (simulation)
    """

    def __init__(self, right_side, box, mapping, create_army_with_points=False):
        """Initialisation de la classe Horseman"""
        Unit.__init__(self, right_side, box, mapping, create_army_with_points)  # Initialisation de la classe parent Unit
        self.type = 'Horseman'
        self.hp = 400
        self.damage = 40
        self.movement = 6
        self.attack_range = 7
        self.armor = 75
        self.cost = 40
        self.forces = ['Warrior', 'Bowman', 'Knight']
        self.enter_in_box(box)


class King(Unit):
    """
    Cette classe définit les rois par :
        - ses points de vie (hp)
        - ses dégâts d'attaque (damage)
        - sa distance maxiamale de déplacement (movement)
        - sa distance minimale d'attaque (attack_range)
        - son coût en points d'armée (cost)

    Paramètres :
        right_side : booléen (False si c'est un ennemi qui se trouve à gauche et True s'il se trouve à droite)
        box : objet Box (from mapping import Box) représentant la case qui a été choisie pour placer l'unité
        mapping : objet Map (from mapping import Map) représentant la carte sur laquelle le combat va se passer

        Optionnel :
            create_army_with_points : booléen correspondant au fait s'il l'unité est utilisé pour la simulation de l'armée ou dans la création pour combattre ensuite
                Défaut : False (combat)
                Option : True (simulation)
    """

    def __init__(self, right_side, box, mapping, create_army_with_points=False):
        """Initialisation de la classe King"""
        Unit.__init__(self, right_side, box, mapping, create_army_with_points)  # Initialisation de la classe parent Unit
        self.type = 'King'
        self.hp = 600
        self.damage = 70
        self.movement = 5
        self.attack_range = 10
        self.armor = 100
        self.cost = 70
        self.allies = []
        self.forces = ['Warrior', 'Bowman', 'Knight', 'Horseman']
        self.enter_in_box(box)

    def die(self):
        """
        Vérifie si les points de vie de l'objet sont négatifs ou nuls.

        Paramètres :
            -----

        Return :
            - True si les points de vie de l'objet sont négatifs ou nuls
            - None si la condition n'est pas satisfaite
        """
        if self.hp <= 0:
            self.hp = 0
            self.out_box()
            self.malus_dead_of_king()  # Applique le malus "Mort du Roi"
            return True

    def append_allies(self, ally):
        """
        Ajoute un allié au roi.

        Paramètres :
            ally : objet représentant un allié du roi
                Options : Bowman, Horseman, Knight, Warrior

        Return :
            None
        """
        self.allies.append(ally)

    def malus_dead_of_king(self):
        """
        Ajoute un malus aux alliés du roi (appelé si le roi meurt).

        Paramètres :
            -----

        Return :
            None
        """
        for unit in self.allies:
            if unit.type == "Horseman":
                unit.damage *= 97 / 100
            elif unit.type == "Warrior":
                unit.damage *= 92 / 100
            elif unit.type == "Bowman":
                unit.damage *= 95 / 100
            else:
                unit.damage *= 97 / 100


class Knight(Unit):
    """
    Cette classe définit les chevaliers par :
        - ses points de vie (hp)
        - ses dégâts d'attaque (damage)
        - sa distance maxiamale de déplacement (movement)
        - sa distance minimale d'attaque (attack_range)
        - son coût en points d'armée (cost)

    Paramètres :
        right_side : booléen (False si c'est un ennemi qui se trouve à gauche et True s'il se trouve à droite)
        box : objet Box (from mapping import Box) représentant la case qui a été choisie pour placer l'unité
        mapping : objet Map (from mapping import Map) représentant la carte sur laquelle le combat va se passer

        Optionnel :
            create_army_with_points : booléen correspondant au fait s'il l'unité est utilisé pour la simulation de l'armée ou dans la création pour combattre ensuite
                Défaut : False (combat)
                Option : True (simulation)
    """

    def __init__(self, right_side, box, mapping, create_army_with_points=False):
        """Initialisation de la classe Knight"""
        Unit.__init__(self, right_side, box, mapping, create_army_with_points)  # Initialisation de la classe parent Unit
        self.type = "Knight"
        self.hp = 300
        self.damage = 40
        self.movement = 4
        self.attack_range = 5
        self.armor = 50
        self.cost = 30
        self.forces = ['Warrior', 'Bowman', 'Knight']
        self.enter_in_box(box)


class Warrior(Unit):
    """
    Cette class définit les guerriers par :
        - ses points de vie (hp)
        - ses dégâts d'attaque (damage)
        - sa distance maxiamale de déplacement (movement)
        - sa distance minimale d'attaque (attack_range)
        - son coût en points d'armée (cost)

    Paramètres :
        right_side : booléen (False si c'est un ennemi qui se trouve à gauche et True s'il se trouve à droite)
        box : objet Box (from mapping import Box) représentant la case qui a été choisie pour placer l'unité
        mapping : objet Map (from mapping import Map) représentant la carte sur laquelle le combat va se passer

        Optionnel :
            create_army_with_points : booléen correspondant au fait s'il l'unité est utilisé pour la simulation de l'armée ou dans la création pour combattre ensuite
                Défaut : False (combat)
                Option : True (simulation)
    """

    def __init__(self, right_side, box, mapping, create_army_with_points=False):
        """Initialisation de la classe Warrior"""
        Unit.__init__(self, right_side, box, mapping, create_army_with_points)  # Initialisation de la classe parent Unit
        self.type = "Warrior"
        self.hp = 200
        self.damage = 30
        self.movement = 3
        self.attack_range = 4
        self.armor = 25
        self.cost = 10
        self.enter_in_box(box)


if __name__ == '__main__':
    from mapping import Map


    message = """0 - Test sur les unités (comabt entre 2 unités)
1 - Test des malus/bonus (vérification de l'application des malus et des bonus liées aux cases)"""
    print(message)
    choix = int(input('Quel test voulez-vous effectuer ? '))

    map_test = Map(nb_river=200)

    ##### TEST SUR LES UNITÉS #####
    if choix == 0:
        print("Caractéristiques bowman1 :")
        bowman1 = Bowman(False, map_test.research_one_box((10, 10)), mapping=map_test)  # Unité ennemie
        print("Position bowman1 : x =", bowman1.x, "y =", bowman1.y)
        print("HP bowman1 :", bowman1.hp)
        print("Dégâts bowman1 :", bowman1.damage)
        print("Mouvement bowman1 :", bowman1.movement)

        print("Caractéristiques warrior1 :")
        warrior1 = Warrior(True, map_test.research_one_box((1010, 10)), mapping=map_test)  # Unité alliée
        print("Position warrior1 : x =", warrior1.x, "y =", warrior1.y)
        print("PV warrior1 :", warrior1.hp)
        print("Degats warrior1 :", warrior1.damage)
        print("Mouvement warrior1 :", warrior1.movement)

        while True:
            bowman1.attack(warrior1)
            warrior1.attack(bowman1)
            print(bowman1.hp + bowman1.armor, warrior1.hp + bowman1.armor)
            print('--------------------------------------------------------')
            print(warrior1.box)
            print(bowman1.box)
            print('*****************************************************************')
            print('*****************************************************************')
            print('*****************************************************************')
            if bowman1.hp <= 0 or warrior1.hp <= 0:
                if bowman1.hp <= 0 and warrior1.hp <= 0:
                    print('Égalité')
                elif bowman1.hp <= 0:
                    print('warrior1 a gagné')
                else:
                    print('bowman1 a gagné')
                break
        print(bowman1.box, warrior1.box)

    ##### TEST SUR LES MALUS/BONUS #####
    elif choix == 1:
        town_left1 = (110, 90)
        town_left2 = (110, 110)
        town_left3 = (130, 110)
        h1 = Horseman(True, map_test.research_one_box(town_left1), map_test)
        h2 = Horseman(False, map_test.research_one_box(town_left2), map_test)
        h3 = Horseman(False, map_test.research_one_box(town_left3), map_test)
        print('Horseman ID 1 :', h1.hp, 'VS', 400, h1.attack_range, 'VS', 7, h1.damage, 'VS', 40, h1.movement, 'VS', 6)
        print('Horseman ID 2 :', h2.hp, 'VS', 400, h2.attack_range, 'VS', 7, h2.damage, 'VS', 40, h2.movement, 'VS', 6)
        print('Horseman ID 3 :', h3.hp, 'VS', 400, h3.attack_range, 'VS', 7, h3.damage, 'VS', 40, h3.movement, 'VS', 6)
        print('Moral :', h1.moral, "/", h2.moral, "/", h3.moral)
        h1.is_surrounded()
        print('Moral :', h1.moral, "/", h2.moral, "/", h3.moral)

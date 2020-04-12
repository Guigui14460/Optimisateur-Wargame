from random import choice
from units import Bowman, Horseman, King, Knight, Warrior


def unit_choice(right_side, points, unit_available=['Warrior', 'Bowman', 'Knight', 'Horseman']):
    """
    Permet de choisir une unité en fonction de son coût, de l'appartenance à son armée et des unités qui sont disponibles.

    Paramètres :
        right_side : booléen (False si c'est un ennemi qui se trouve à gauche (côté ordinateur ou simulation (seulement pour cette fonction)) et True s'il se trouve à droite (côté joueur))
        points : entier correspondant à l'argent disponible pour choisir l'unité
            
        Optionnels :
            unit_available : liste qui contient les types des unités qui peuvent encore être choisies
                Défaut : ['Warrior', 'Bowman', 'Knight', 'Horseman']

    Return :
        (unit_chosen, unit_available)
            unit_chosen : chaîne de caractères représentant le type de l'unité chosie
            unit_available : liste des unités encore disponibles
    """

    def choice_by_right():
        """
        Permet le choix de l'unité pour l'armée alliée.
        Réduction des choix possibles en fonction des points disponibles.

        Paramètres :
            -----

        Return :
            unit_available[number] : type de l'unité choisie (=> unit_chosen)
        """
        if points >= 40:
            number = int(input(f"Quelle unité à ajouter à votre armée (0 pour Warrior, 1 pour Bowman, 2 pour Knight, 3 pour Horseman) ? "))
            if not 0 <= number <= 3:
                print("Saisie invalide ! Warrior par défaut")
                number = 0
        elif 10 <= points < 20:
            print("Attention ! Vous ne pouvez plus achetez certaines unités car vous n'avez plus assez de points d'armée !")
            number = int(input(f"Quelle unité à ajouter à votre armée (0 pour Warrior) ? "))
            if number != 0:
                print("Saisie invalide ! Warrior par défaut")
                number = 0
        elif 20 <= points < 30:
            print("Attention ! Vous ne pouvez plus achetez certaines unités car vous n'avez plus assez de points d'armée !")
            number = int(input(f"Quelle unité à ajouter à votre armée (0 pour Warrior, 1 pour Bowman) ? "))
            if not 0 <= number <= 1:
                print("Saisie invalide ! Warrior par défaut")
                number = 0
        elif 30 <= points < 40:
            print("Attention ! Vous ne pouvez plus achetez certaines unités car vous n'avez plus assez de points d'armée !")
            number = int(input(f"Quelle unité à ajouter à votre armée (0 pour Warrior, 1 pour Bowman, 2 pour Knight) ? "))
            if not 0 <= number <= 2:
                print("Saisie invalide ! Warrior par défaut")
                number = 0
        return unit_available[number]

    def choice_by_left():
        """
        Permet le choix de l'unité pour l'armée ennemie (ou en simulation).
        Réduction des choix possibles en fonction des points disponibles.

        Paramètres :
            -----

        Return :
            choice(unit_available) : type de l'unité choisie (=> unit_chosen)
        """
        if points < 40 and 'Horseman' in unit_available:
            unit_available.remove('Horseman')
        if points < 30 and 'Knight' in unit_available:
            unit_available.remove('Knight')
        if points < 20 and 'Bowman' in unit_available:
            unit_available.remove('Bowman')
        return choice(unit_available)

    if right_side:  # Si le choix est pour un joueur
        unit_chosen = choice_by_right()
    else:  # Si le choix est pour l'ordinateur (ou le joueur s'il est en simulation)
        unit_chosen = choice_by_left()

    return unit_chosen, unit_available

def unit_cost(unit, mapping, unit_position):
    """
    Permet de donner le coût d'une unité.

    Paramètres :
        unit : chaîne de caractères correspondant au type de l'unité que l'on veut connaître son coût
        mapping : objet Map (from mapping import Map)
        unit_position : tuple (x, y) représentant la position de l'unité (centre de la case où il va se trouver)

    Return :
        unit.cost : entier représentant le coût de l'unité
    """
    if unit == 'King':
        unit = King(True, unit_position, mapping, create_army_with_points=True)
    elif unit == 'Knight':
        unit = Knight(True, unit_position, mapping, create_army_with_points=True)
    elif unit == 'Bowman':
        unit = Bowman(True, unit_position, mapping, create_army_with_points=True)
    elif unit == 'Warrior':
        unit = Warrior(True, unit_position, mapping, create_army_with_points=True)
    else:
        unit = Horseman(True, unit_position, mapping, create_army_with_points=True)
    return unit.cost

def unit_position_choice(position_available):
    """
    Permet de choisir aléatoirement une position.

    Paramètres :
        position_available : liste d'objet Box (from mapping import Box) représentant toutes les cases disponibles

    Return :
        choice(position_available) : objet Box (from mapping import Box) représentant la case choisie
    """
    return choice(position_available)


if __name__ == '__main__':
    print("Test réalisé avec le fichier : army.py")

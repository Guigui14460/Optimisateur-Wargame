from os import system
from random import choice, randint
from sys import platform
from time import sleep


def nettoyageConsole():
    """
    Permet de nettoyer la console pour éviter le surplus d'information sur celle-ci.

    Paramètres :
            -----

    Return :
            None
    """
    input('Appuyez sur \'Entrée\' pour continuer ')
    if platform == 'win32':
        system("cls")
    else:
        system('clear')


def enemyChoiceByComputer(unit, enemy_list):
    """
    Permet à l'ordinateur de choisir qui attaquer.

    Paramètres :
            unit : objet Unit (from units import Unit) correspondant à l'unité qui va attaquer
            enemy_list : liste des ennemis que l'unité doit attaquer

    Return :
            enemy_list.index(unit2) : entier correspondant à l'indice de l'ennemi dans la liste qu'il va attaquer
    """
    hp_min = 6000
    unit2 = None
    for enemy in enemy_list:
        if enemy.hp + enemy.armor < hp_min:
            unit2 = enemy
            hp_min = enemy.hp + enemy.armor
    if unit2 is None:
        return choice(enemy_list)
    return enemy_list.index(unit2)


def enemyChoiceByPlayer(unit, enemy_list):
    """
    Permet aux joueur de choisir qui attaquer.

    Paramètres :
            unit : objet Unit (from units import Unit) correspondant à l'unité qui va attaquer
            enemy_list : liste des ennemis que l'unité doit attaquer

    Return :
            player_choice : entier correspondant à l'indice de l'ennemi dans la liste qu'il va attaquer
    """
    print('Voici la liste des ennemis :')
    for i in range(len(enemy_list)):
        print(
            i, f"Type : {enemy_list[i].type}, HP + ARMURE : {enemy_list[i].hp + enemy_list[i].armor}, Position : {enemy_list[i].x, enemy_list[i].y}")
    print('Votre unité est forte (x1.5 de dégâts) contre ', unit.forces)
    try:
        player_choice = int(input('Quelle unité voulez-vous attaquer ? '))
    except ValueError:  # Capture de l'erreur disant qu'il n'est pas possible de convertir une chaine de caractère en nombre entier
        player_choice = 0  # Mettre une unité à attaquer par défaut
    # Capture de l'erreur disant qu'il n'y a pas l'indice recherché
    if not 0 <= player_choice < len(enemy_list):
        player_choice = randint(0, len(enemy_list) - 1)
    return player_choice


def left_army_attack(i, left_army, right_army, in_progress):
    """
    Permet à l'armée ennemie d'attaquer.

    Paramètres :
            i : indice de l'unité dans l'armée ennemie
            left_army : objet Army représentant l'armée ennemie
            right_army : objet Army représentant l'armée alliée
            in_progress : booléen représentant la fin du jeu (False si ça continue et True si c'est terminé)

    Return :
            in_progress : booléen représentant la fin du jeu après l'attaque de l'unité (False si ça continue et True si c'est terminé)
    """
    try:
        enemy_index = enemyChoiceByComputer(left_army.full_army[i], right_army.full_army)
        left_army.full_army[i].attack(right_army.full_army[enemy_index])
        # Vérification si l'unité est morte ou non
        if right_army.full_army[enemy_index].die():
            # On l'enlève de l'armée ennemie de l'ordinateur
            right_army.full_army.remove(right_army.full_army[enemy_index])
    except IndexError:  # Capture de l'erreur disant que l'indice recherché n'existe pas
        if right_army.full_army == [] or left_army.full_army == []:  # Si l'une des armée est vide
            in_progress = False
        else:  # Attaque de la dernière unité de la liste ennemie de l'ordinateur par défaut
            left_army.full_army[i].attack(right_army.full_army[-1])
            # Vérification si l'unité est morte ou non
            if right_army.full_army[-1].die():
                # On l'enlève de l'armée ennemie de l'ordinateur
                right_army.full_army.remove(right_army.full_army[-1])
    return in_progress


def simu(left_army, right_army, in_simulation=False):
    """
    Fonction qui simule le combat entre 2 armées données.

    Paramètres :
            left_army : objet Army représentant l'armée ennemie
            right_army : objet Army représentant l'armée alliée

            Optionnel :
                    in_simulation : booléen (True si c'est dans un simulation et False si on est pas dans une simulation)
                            Défaut : False

    Return :
            tuple (right_army.full_army, left_army.full_army)
                    right_army.full_army : liste des alliés restants
                    left_army.full_army : liste des ennemis restants
    """
    in_progress = True
    # Choix aléatoire du côté qui va commencer la partie
    player_turn = choice([True, False])
    while in_progress:
        if not player_turn:  # Ordi
            player_turn = True
            for i in range(len(left_army.full_army)):
                in_progress = left_army_attack(i, left_army, right_army, in_progress)
        else:  # Joueur
            player_turn = False
            for i in range(len(right_army.full_army)):
                try:
                    if not in_simulation:  # Joueur pas simulé
                        enemy_index = enemyChoiceByPlayer(right_army.full_army[i], left_army.full_army)
                    else:  # Joueur simulé
                        enemy_index = enemyChoiceByComputer(right_army.full_army[i], left_army.full_army)
                    right_army.full_army[i].attack(left_army.full_army[enemy_index])
                    # Vérification si l'unité est morte ou non
                    if left_army.full_army[enemy_index].die():
                        # # On l'enlève de l'armée ennemie du joueur
                        left_army.full_army.remove(left_army.full_army[enemy_index])
                except IndexError:  # Capture de l'erreur disant que l'indice recherché n'existe pas
                    if right_army.full_army == [] or left_army.full_army == []:  # Si l'une des armée est vide
                        in_progress = False
                    else:  # Attaque de la dernière unité de la liste ennemie du joueur par défaut
                        right_army.full_army[i].attack(left_army.full_army[-1])
                        # Vérification si l'unité est morte ou non
                        if left_army.full_army[-1].die():
                            # # On l'enlève de l'armée ennemie du joueur
                            left_army.full_army.remove(left_army.full_army[-1])

        if right_army.full_army == [] or left_army.full_army == []:  # Si l'une des armée est vide
            in_progress = False

    if right_army.full_army == [] and left_army.full_army == []:  # Si les deux armées sont vides
        print("Égalité")
    elif left_army.full_army == []:  # Si l'armée ennemie est vide
        print("Vous avez gagné !")
    else:  # Si l'armée du joueur est vide
        print("L'ordinateur a gagné !")
    return right_army.full_army, left_army.full_army


if __name__ == '__main__':
    from time import time
    from mapping import Map
    from army import Army

    message = """0 - Simple simulation (avec choix possible)
1 - Multiples simulations (choix impossible, exécution type algorithme génétique)"""
    print(message)
    choix = int(input("Choix de simulation : "))

    debut_all = time()

    # Création des constantes (listes de positions dispo, quantité de fonds dispo, ...)
    map_test = Map()
    other_map = map_test.for_other_map()
    # print(other_map)
    points = 300

    # Choix ordinateur
    left_army = Army(map_test, False, points)

    ##### SIMPLE SIMULATION #####
    if choix == 0:
        # Choix joueur
        right_army = Army(map_test, True, points)

        nettoyageConsole()

        # Lancement simulation
        simu_ = simu(left_army, right_army)

    ##### MULTIPLES SIMULATIONS #####
    elif choix == 1:
        in_simulation = True

        # Lancement des simulations
        for x in range(8):
            new_map = Map(other_map=other_map)
            right_army = Army(map_test, True, points, in_simulation=in_simulation)
            simu_ = simu(left_army, right_army, in_simulation=in_simulation)
            left_army.create_army_from_base()
            print('-------------------------------------------------------------------------------------------')

    print("Durée totale :", time() - debut_all)

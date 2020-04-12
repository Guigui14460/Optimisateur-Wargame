from threading import Thread, RLock
from army import Army
from simulator import simu


verrou = RLock()  # Permet de synchroniser les threads en les bloquant (si un thread a besoin d'une ressources partagée)


class SimulatorThreaded(Thread):
    """
    Thread chargé de faire la simulation.

    Paramètres :
        mapping : objet Map (from mapping import Map) représentant la carte de combat
        right_army : objet Army (from army import Army) représentant l'armée alliée (from army import Army)
        left_army_base : liste de tuples (unité, case) représentant l'armée ennemie (à créer pour simuler)
        points : entier représentant à l'argent disponible pour créer l'armée

        Optionnels :
            in_simulation : booléen correspondant au fait qu'on se trouve ou non dans une simulation
                Défaut : False
                Options : False, True
    """
    def __init__(self, mapping, right_army, left_army_base, points, in_simulation=False):
        Thread.__init__(self)
        self.right_army = right_army
        self.in_simulation = in_simulation
        self.fitness = 0
        self._return = None
        self.left_army = Army(mapping, False, points, in_simulation, army_base=left_army_base)

    def run(self):
        """
        Code à exécuter pendant l'exécution du thread.

        Paramètres :
            -----

        Return :
            None
        """
        with verrou:  # Verrouillage des threads
            simu_ = simu(self.left_army, self.right_army, self.in_simulation)
            for unit in simu_[0]:
                self.fitness += (unit.hp + unit.armor) * unit.damage  # Calcul d'une valeur pour les unités alliées
            self.fitness *= len(simu_[0])
            fitness2 = 0
            for unit in simu_[1]:
                fitness2 += (unit.hp + unit.armor) * unit.damage  # Calcul d'une valeur pour les unités ennemies
            fitness2 *= len(simu_[1])
            self.fitness -= fitness2

    def join(self):
        """
        Permet de faire attendre les exécutions dans l'ordre de leur lancement.

        Paramètres :
            -----

        Return :
            fitness : entier correspondant à la résistance de l'armée (utilisé pour l'algorithme génétique)
        """
        Thread.join(self)
        return self.fitness


if __name__ == '__main__':
    from time import time
    from mapping import Map


    message = """0 - Test sur l'exécution des simulations en parallèle"""
    print(message)
    choix = int(input('Quel test voulez-vous faire ? '))

    debut_time = time()

    ##### TEST SUR LES SIMULATIONS PARALLELES #####
    if choix == 0:
        population = 8
        in_simulation = True

        # Création des constantes (carte, quantité de fonds dispo, ...)
        map_test = Map()
        other_map = map_test.for_other_map()
        points = 300

        # Choix ordinateur
        left_army = Army(map_test, False, points)


        all_right_armies = [Army(Map(other_map=other_map), True, points, in_simulation=in_simulation) for i in range(population)]

        # Création des threads
        thread_all = [SimulatorThreaded(Map(other_map=other_map), all_right_armies[i], left_army.army_base, points, in_simulation=in_simulation) for i in range(len(all_right_armies))]
        # Lancement des threads
        for thread in thread_all:
            thread.start()

        # Attend que les threads se terminent
        for thread in thread_all:
            thread.join()

    print('***************************************************************')
    print(time() - debut_time)

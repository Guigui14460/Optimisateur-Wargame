import pygame


class GameVictorySound:
	"""
	Cette classe définit les musiques de la victoire qui ne vont être jouée que si le joueur gagne.

	Paramètres :
		-----
	"""

	def __init__(self):
		pass

	def play_victory(self, sound_volume=1):
		"""
		Joue la musique de la victoire.

		Paramètres :
			Optionnels :
				sound_volume : flottant entre 0 et 1 qui permet de gérer le volume de la musique
					Défaut : 1

		Return :
			None
		"""
		pygame.mixer.music.load('victory.wav')
		pygame.mixer.music.play()
		pygame.mixer.music.set_volume(sound_volume)

	def play_clap(self, sound_volume=1):
		"""
		Joue les applaudissements de la victoire.

		Paramètres :
			Optionnels :
				sound_volume : flottant entre 0 et 1 qui permet de gérer le volume de la musique
					Défaut : 1

		Return :
			None
		"""
		pygame.mixer.music.load('clap.wav')
		pygame.mixer.music.play()
		pygame.mixer.music.set_volume(sound_volume)


if __name__ == '__main__':
	message = """0 - Test sur le son joué lors de la victoire du joueur"""
	print(message)

	choix = int(input('Quel test voulez-vous effectuer ? '))

	if choix == 0:
		pygame.init()
		pygame.mixer.init()
		fenetre = pygame.display.set_mode((300,300))
		sound = GameVictorySound()
		run = True
		i = 0
		while run:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False

			if i == 0:
				sound.play_clap()
				i += 1
			elif i == 1 and not pygame.mixer.music.get_busy():
				sound.play_victory()
				i += 1
			elif i == 2 and not pygame.mixer.music.get_busy():
				sound.play_clap()
				i += 1

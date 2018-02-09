"""
Classe servant a faire les stats sur l'univers et les CPUs
A ne pas utiliser pour l'instant (pas fonctionnel)
"""

class Statistiques:
	def __init__(self, U):
		"Chaque instance va etre reliee a un Univers"
		self.univers 	= U
		U.set_statistiques(self)
		self.cpus_crees = [] #Enregistre le nombre de cpus crees a chaque iteration 
		self.cpus_total = [] 

	def mettre_a_jour(self):
		"A appeler apres chaque cycle du CPUs"
		self.recuperer_cpus_crees()
		self.recuperer_cpus_total()

	def recuperer_cpus_crees(self):
		self.cpus_crees.append(self.univers.retourner_cpus_crees())

	def recuperer_cpus_total(self):
		self.cpus_total.append(self.univers.retourner_cpus_total())

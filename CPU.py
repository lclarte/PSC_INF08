from Instructions_Tierra import *

TAILLE_STACK = 10

class CPU:
	TAILLE_STACK = 10

	#ptr stocke l'adresse actuellement pointee par le CPU
	def __init__(self, ptr, univers, ax = 0, bx = 0,cx = 0,dx = 0,stack=[0]*TAILLE_STACK,stack_ptr = 0):
		self.ax = ax
		self.bx = bx
		self.cx = cx
		self.dx = dx
		self.ptr							  = ptr
		self.univers						  = univers
		self.stack 							  = stack
		self.stack_ptr						  = stack_ptr
	
	def execute(self):
		"execute l'instruction actuellement pointee par le CPU puis passe a la suivante\
		Attention, les instructions dans l'univers sont stockees sous forme de chaine de caractere\
		correspondant EXACTEMENT au nom des fonctions"
		
		ins = self.univers.insDict.toString(self.univers.memoire[self.ptr])
		try:
			f = eval(ins)
			f(self)
		except Exception as e:
			print("Instruction ayant echoue : ", ins)
			print(e)
		finally:
			self.incrementer_ptr()

	def enlever_localisation(self):
		"Enleve ce CPU du tableau localisation_cpu"
		try:
			self.univers.localisation_cpus[self.ptr].remove(self)
			if(self.univers.localisation_cpus[self.ptr] == []):
				del self.univers.localisation_cpus[self.ptr]
		except Exception as e:
			print("Le CPU n'est pas la ou il le devrait !")

	def ajouter_localisation(self):
		"Ajoute le CPU dans la case correspondante dans le tableau localisation_cpu de Univers"
		if(self.univers.localisation_cpus.has_key(self.ptr)):
			self.univers.localisation_cpus[self.ptr].append(self)
		else:
			self.univers.localisation_cpus[self.ptr] = [self]


	def incrementer_ptr(self):
		self.ptr = (self.ptr + 1)%(len(self.univers.memoire))

	def incrementer_stack_ptr(self):
		self.stack_ptr = (self.stack_ptr + 1) % (TAILLE_STACK)

	def decrementer_stack_ptr(self):
		self.stack_ptr = (self.stack_ptr - 1) % (TAILLE_STACK)

	def pop_stack(self):
		"Retourne la valeur du stack qui est au dessus i.e en stack_ptr - 1 SANS DECREMENTER\
		le stack pointeur"
		return self.stack[(self.stack_ptr-1)%TAILLE_STACK]

	def push_stack(self, x):
		"Met la valeur de l'argument dans la stack SANS INCREMENTER le stack\
		pointeur"
		self.stack[self.stack_ptr] = x

	def die(self):
		#self.enlever_localisation()
		univers.enlever_cpu(self)

	#FONCTIONS D'AFFICHAGE
	def afficher_etat(self):
		print("valeurs de ax, bx, cx et dx : ")
		print(self.ax, self.bx, self.cx, self.dx)
		print("Etat du pointeur d'instructions")
		print(self.ptr, " sur ", self.univers.memoire[self.ptr])
		print('valeur de la stack : ', self.stack)
		print('pointeur de la stack : ', self.stack_ptr)

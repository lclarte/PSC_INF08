from CPU import *
from Enregistrement import *
from math import *
import InstructionsDict
import random


#TAILLE_MEMOIRE = 50000
#TAUX_MUTATION  = 0
#LARGEUR_CALCUL_DENSITE = 0
#SEUIL_DENSITE		   = 1.5

class Univers:
    "Contient les CPU et le monde i.e les instructions a executer"
    #valeurs non contractuelles.
    b1=2 #nb bytes du nb de CPU et du numero du CPU considere actuellement.(limite leur nombre)
    b2=2 #nb bytes du nb de case memoire.(limite leur nombre)
    n2=6 #nb bit d'une case memoire
    n3=16 #nb de bit d'un registre du CPU
    n1=5*n3+CPU.TAILLE_STACK*n2+ceil(log(CPU.TAILLE_STACK,2)) #nb bit d'un CPU
    #TAILLE_MEMOIRE = 500
    def __init__(s, TAILLE_MEMOIRE=50000, insDict=InstructionsDict.InstructionsDict(), mutation=0, LARGEUR_CALCUL_DENSITE=1, maxCPUs=1):
        #code temporaire
        #eve = charger_genome('eve')
        s.TAILLE_MEMOIRE           = TAILLE_MEMOIRE
        s.memoire                  = [2]*(s.TAILLE_MEMOIRE)
        s.liste_cpus 	           = []     # ne pourrait-on pas gagner de l'efficacite en en faisant une liste chainee ?
        s.insDict                  = insDict
        s.mutation 				   = mutation #definit le taux de mutation de l'univers
        s.indice_cpu_actuel 	   = 0
        s.localisation_cpus        = {} # dictionnaire dont les clefs sont des adresses memoire, qui contient la liste des CPUs
        s.LARGEUR_CALCUL_DENSITE   = LARGEUR_CALCUL_DENSITE
        s.maxCPUs                 = maxCPUs

    def cpu_actuel(s):
        "Renvoie un pointeur vers le CPU actuel"
        if len(s.liste_cpus)==0 :
            return None
        return s.liste_cpus[s.indice_cpu_actuel]

    def ind(self, i):
        """Renvoie l'indice i modulo TAILLE_MEMOIRE"""
        return (i%self.TAILLE_MEMOIRE)

    def cycle(s):
        "Execute les CPUs puit les tue par densite"
        try:
            s.executer_cpus()
            s.tuer_cpus_par_densite()
        except Exception as e:
            print(e)
            raise

    def executer_cpus(s):
        "Cette fonction execute tous les CPU 1 fois\
        PRECISION IMPORTANTE : on parcourt la liste dans l'ordre des indices decroissant"
        if len(s.liste_cpus) == 0:
            raise NoCPUException()
        indice_cpu_depart = (s.indice_cpu_actuel) #Contient le cpu auquel on devra s'arreter
        cpu_actuel 	  = s.cpu_actuel()
        s.executer_cpu_actuel()
        s.next_cpu()
        while s.indice_cpu_actuel != indice_cpu_depart:
            s.executer_cpu_actuel()
            s.next_cpu()

    def executer_cpu_actuel(s):
        "Execute le CPU actuellement pointe SANS PASSER AU SUIVANT\
        i.e sans incrementer cpu_actuel"
        cpu = s.cpu_actuel()
        i = cpu.ptr
        cpu.execute()
        s.supprimer_cpu_localisation(cpu, i)
        s.ajouter_cpu_localisation(cpu)

    def supprimer_cpu_localisation(s, cpu, i=-1):
        """Prend en argument le pointeur vers un cpu et l'enleve de l'adresse i dans le dictionnaire localisation_cpus"""
        # Si i n'est pas precise, i vaut -1 et le cpu est recherche dans toute la memoire a partir de cpu.ptr
        if i == -1 :
            for j in range(0, s.TAILLE_MEMOIRE/2+1) :
                k = s.ind(cpu.ptr + j)
                if (k in s.localisation_cpus) and (cpu in s.localisation_cpus[k]) :
                    s.localisation_cpus[k].remove(cpu)
                    if s.localisation_cpus[k] == []:
                        del s.localisation_cpus[k]
                    return
                k = s.ind(cpu.ptr - j)
                if (k in s.localisation_cpus) and (cpu in s.localisation_cpus[k]) :
                    s.localisation_cpus[k].remove(cpu)
                    if s.localisation_cpus[k] == []:
                        del s.localisation_cpus[k]
                    return
            print("Erreur de suppression de localisation !")
        else :
            try:
                s.localisation_cpus[i].remove(cpu)
                if s.localisation_cpus[i] == []:
                    del s.localisation_cpus[i]
            except Exception as e:
                print("Erreur de suppression de localisation !")
                print(e)

    def ajouter_cpu_localisation(s, cpu):
        if not cpu.ptr in s.localisation_cpus:
            s.localisation_cpus[cpu.ptr] = []
        if not cpu in s.localisation_cpus[cpu.ptr]:
            s.localisation_cpus[cpu.ptr].append(cpu)

    def tuer_cpu(s, cpu, i=-1):
        """Tue cpu qui est situe a l'indice i dans localisation_cpus, ie le supprime de ce dictionnaire et de liste_cpus"""
        s.liste_cpus.remove(cpu)
        s.supprimer_cpu_localisation(cpu, i)

    def tuer_cpu_actuel(s):
        """NE PAS UTILISER SI CPU ACTUEL EN COURS D'EXECUTION"""
        # car risque de pb a la suppression de la localisation
        s.tuer_cpu(s.cpu_actuel())

    def next_cpu(s):
        "Met a jour cpu_actuel pour pointer le suivant a executer"
        s.indice_cpu_actuel = (s.indice_cpu_actuel - 1)%(len(s.liste_cpus))

    def inserer_cpu(s, c):
       "Insere le nouveau CPU c dans la liste juste apres celui actuellement pointe"
       s.liste_cpus.insert(s.indice_cpu_actuel + 1, c)
       s.ajouter_cpu_localisation(c)

    def addIndividual(self, index, indiv) :
        "Ecrit l'individu indiv dans la memoire a partir de l'adresse index. indiv est sous la forme d'un tableau d'entiers"
        for i in range(len(indiv)) :
            self.memoire[self.ind(index + i)] = indiv[i]


    def calculer_densite(s, position):
        "Calcule la densite de CPU a la position donnee"
        nombre = 0
        for i in range(position - s.LARGEUR_CALCUL_DENSITE, position + s.LARGEUR_CALCUL_DENSITE+1):
            if (s.ind(i)) in s.localisation_cpus:
                nombre += len(s.localisation_cpus[s.ind(i)])
        return float(nombre)/float((2*s.LARGEUR_CALCUL_DENSITE+1))

    def nbCPUs_at_i(s, i) :
        """renvoie le nb (eventuellement nul) de CPUs localises a l'adresse i"""
        if i in s.localisation_cpus :
            return len(s.localisation_cpus[i])
        else :
            return 0

    def nbCPUs_around_i(s, i) :
        """renvoie le nb (eventuellement nul) de CPUs localises dans la region centree en l'adresse i"""
        nb = 0
        for j in range(-s.LARGEUR_CALCUL_DENSITE, s.LARGEUR_CALCUL_DENSITE+1) :
            nb += s.nbCPUs_at_i(s.ind(i+j))
        return nb

    def killAround(s, i, n):
        """Tue les CPUs dans la region commencant a l'indice i et contenant au depart n CPUs, jusqu'a atteindre la moitie de la densite limite"""
        # suppose qu'aucun CPU n'est en cours d'execution
        l = 2*s.LARGEUR_CALCUL_DENSITE
        target = max(1, (s.maxCPUs / 2))
        while n > target :
            j = s.ind(random.randint(i, i+l))   # +1 ou pas ?
            if j in s.localisation_cpus :
                k = random.randint(0,len(s.localisation_cpus[j])-1)
                s.tuer_cpu(s.localisation_cpus[j][k])
                n-=1
        # peut-etre le cpu c est-il dans plusieurs localisations ? (et lorsqu'il est supprime de liste_cpus, toute les localisations ne sont pas supprimees...)

    def tuer_cpus_par_densite(s):
        """Fait tuer des CPUs par killAround dans les endroits trop denses"""
        l = 2 * s.LARGEUR_CALCUL_DENSITE  # largeur reelle de l'intervalle de calcul de densite - 1
        start = random.randint(0,
                               len(s.liste_cpus) - 1)  # on commence a un CPU aleatoire pour ne pas introduire de biais d'age
        killZones = []
        for k in range(start, len(s.liste_cpus)) :
            i = s.liste_cpus[k].ptr
            for j in range(-s.LARGEUR_CALCUL_DENSITE, s.LARGEUR_CALCUL_DENSITE+1) :
                n = s.nbCPUs_around_i(s.ind(i+j))
                if n > s.maxCPUs:
                    killZones.append(s.ind(i+j))
        for k in range(0, start) :
            i = s.liste_cpus[k].ptr
            for j in range(-s.LARGEUR_CALCUL_DENSITE, s.LARGEUR_CALCUL_DENSITE+1) :
                n = s.nbCPUs_around_i(s.ind(i+j))
                if n > s.maxCPUs:
                    killZones.append(s.ind(i+j))
        for i in killZones :
            s.killAround(s.ind(i-s.LARGEUR_CALCUL_DENSITE), s.nbCPUs_around_i(i))
        # avec cette methode est qu'apres en avoir deja supprime, on va faire appel a killAround pour des zones potentiellement deja redescendues sous la densite seuil
        # on pourrait optimiser en ne recalculant pas les nbCPUs_around_i(les indices i deja traites par un autre k)


    def afficher(self):
        print("===============")
        print("memoire :", self.memoire)
        print("liste CPU :")
        for cpu in self.liste_cpus:
            cpu.afficher_etat()
        print("indice_cpu_actuel :", self.indice_cpu_actuel)

    def nbCPUsInLocalisation(s):
        d = {}
        for i in s.localisation_cpus.keys():
            for c in s.localisation_cpus[i]:
                if c in d :
                    d[c] += 1
                else :
                    d[c] = 0
        return len(d)
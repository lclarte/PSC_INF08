from CPU import *
from Enregistrement import *
from math import *
import copy
import InstructionsDict
import random
import os
import Exceptions


#TAILLE_MEMOIRE = 50000
#TAUX_MUTATION  = 0
#LARGEUR_CALCUL_DENSITE = 0
#SEUIL_DENSITE		   = 1.5

class Univers:
    "Contient les CPU et le monde i.e les instructions a executer"
    #valeurs non contractuelles.
    b1=2 #nb bytes du nb de CPU et du numero du CPU considere actuellement.(limite leur nombre)
    b2=2 #nb bytes du nb de case memoire.(limite leur nombre)
    n2=8*b2 #nb bit d'une case memoire

    n3=16 #nb de bit d'un registre du CPU
    n1=5*n3+CPU.TAILLE_STACK*n2+ceil(log(CPU.TAILLE_STACK,2)) + 2*b1*8 #nb bit d'un CPU
    #TAILLE_MEMOIRE = 500
    def __init__(s, nextSite, TAILLE_MEMOIRE=50000, insDict=InstructionsDict.InstructionsDict(), mutation=0, LARGEUR_CALCUL_DENSITE=23, maxCPUs=1, lastid=0):
        #code temporaire
        s.statistiques             = None #Pointeur vers l'instance de la classe statistiques 
                                            #qui va recuperer les donnees de l'univers
        s.cpus_crees               = 0 #Contient le nombre de cpus crees lors du cycle termine
        s.TAILLE_MEMOIRE           = TAILLE_MEMOIRE
        s.memoire                  = [2]*(s.TAILLE_MEMOIRE)
        s.liste_cpus 	           = []
        s.insDict                  = insDict
        s.mutation 				   = mutation #definit le taux de mutation de l'univers
        s.indice_cpu_actuel 	   = 0
        s.localisation_cpus        = {} # dictionnaire dont les clefs sont des adresses memoire, qui contient la liste des CPUs
        s.LARGEUR_CALCUL_DENSITE   = LARGEUR_CALCUL_DENSITE
        s.maxCPUs                  = maxCPUs
        s.nextSite                 = nextSite #la classe utilisee lorsqu'un CPU veut savoir ou se recopier (vaut randint en temps normal)
        s.nextSite.setMemSize(s.TAILLE_MEMOIRE)
        s.lastId                   = lastid

    def set_statistiques(s, stats):
        "Initialisation des stats"
        s.statistiques = stats

    def cpu_actuel(s):
        "Renvoie un pointeur vers le CPU actuel"
        if len(s.liste_cpus)==0 :
            return None
        return s.liste_cpus[s.indice_cpu_actuel]

    def ind(self, i):
        """Renvoie l'indice i modulo TAILLE_MEMOIRE"""
        return (i%self.TAILLE_MEMOIRE)

    def nextId(self, c):
        self.lastId += 1
        if c == None :
            return str(self.lastId)
        else :
            l=c.id.split("/")
            return l[-1]+ "/" + str(self.lastId)

    def retourner_copie_memoire(self):
        return copy.copy(s.memoire)

    def incremente_cpus_crees(s):
        s.cpus_crees += 1

    def reinitialise_cpus_crees(s):
        s.cpus_crees = 0

    def retourner_cpus_crees(s):
        return s.cpus_crees

    def retourner_cpus_total(s):
        return len(s.liste_cpus)

    def cycle(s):
        "Execute les CPUs, met a jour les statistiques puis les tue par densite"
        try:
            s.executer_cpus()
            s.tuer_cpus_par_densite()
        except Exception as e:
            print(e)
            raise
        finally:
            if s.statistiques != None:
                s.statistiques.mettre_a_jour()
            s.reinitialise_cpus_crees()
            
    def executer_cpus(s):
        "Cette fonction execute tous les CPU 1 fois\
        PRECISION IMPORTANTE : on parcourt la liste dans l'ordre des indices decroissant"
        nb = len(s.liste_cpus)
        if nb == 0 :
            raise Exceptions.NoCPUException()
        for i in range(nb) :
            s.executer_cpu_actuel()
            s.next_cpu()

    def executer_cpu_actuel(s):
        "Execute le CPU actuellement pointe SANS PASSER AU SUIVANT\
        i.e sans incrementer cpu_actuel"
        s.cpu_actuel().execute()

    def supprimer_cpu_localisation(s, cpu):
        """Prend en argument le pointeur vers un cpu et l'enleve dans le dictionnaire localisation_cpus"""
        i = cpu.ptr
        try:
            s.localisation_cpus[i].remove(cpu)
            if s.localisation_cpus[i] == []:
                del s.localisation_cpus[i]
        except Exception as e:
            print("Erreur de suppression de localisation :", e)


    def ajouter_cpu_localisation(s, cpu):
        if not cpu.ptr in s.localisation_cpus:
            s.localisation_cpus[cpu.ptr] = []
        if not cpu in s.localisation_cpus[cpu.ptr]:
            s.localisation_cpus[cpu.ptr].append(cpu)

    def tuer_cpu(s, cpu):
        """Tue cpu, ie le supprime de ce dictionnaire et de liste_cpus"""
        i = s.liste_cpus.index(cpu)
        s.liste_cpus.pop(i)
        s.supprimer_cpu_localisation(cpu)
        if s.indice_cpu_actuel == i and i!=0:
            s.next_cpu()
        if s.indice_cpu_actuel == len(s.liste_cpus):
            s.indice_cpu_actuel = 0

    def tuer_cpu_actuel(s):
        """NE PAS UTILISER SI CPU ACTUEL EN COURS D'EXECUTION"""
        # car risque de pb a la suppression de la localisation
        s.tuer_cpu(s.cpu_actuel())

    def next_cpu(s):
        "Met a jour cpu_actuel pour pointer le suivant a executer"
        if len(s.liste_cpus) == 0:
            raise NoCPUException()
        s.indice_cpu_actuel = (s.indice_cpu_actuel - 1)%(len(s.liste_cpus))

    def inserer_cpu(s, c):
       "Insere le nouveau CPU c dans la liste juste apres celui actuellement pointe"
       s.liste_cpus.insert(s.indice_cpu_actuel + 1, c)
       s.ajouter_cpu_localisation(c)
       s.incremente_cpus_crees()

    def addIndividual(self, index, indiv) :
        "Ecrit l'individu indiv dans la memoire a partir de l'adresse index. indiv est sous la forme d'un tableau d'entiers"
        for i in range(len(indiv)) :
            self.memoire[self.ind(index + i)] = indiv[i]

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
            summ = i+j
            if summ>=s.TAILLE_MEMOIRE or summ<0:
                summ=s.ind(summ)
            nb += s.nbCPUs_at_i(summ)
        return nb

    def killAround(s, i, n):
        """Tue les CPUs dans la region commencant a l'indice i et contenant au depart n CPUs, jusqu'a atteindre la moitie de la densite limite"""
        # suppose qu'aucun CPU n'est en cours d'execution
        morts=[]
        l = 2*s.LARGEUR_CALCUL_DENSITE
        target = max(1, (s.maxCPUs / 2))
        while n > target :
            j = random.randint(i, i+l)   # +1 ou pas ?
            if j>s.TAILLE_MEMOIRE:
                j = s.ind(j)
            if j in s.localisation_cpus :
                k = random.randint(0,len(s.localisation_cpus[j])-1)
                morts+=[s.localisation_cpus[j][k].id]
                #print(s.localisation_cpus)
                s.tuer_cpu(s.localisation_cpus[j][k])
                n-=1
        # peut-etre le cpu c est-il dans plusieurs localisations ? (et lorsqu'il est supprime de liste_cpus, toute les localisations ne sont pas supprimees...)
        return morts

    def tuer_cpus_par_densite(s):
        """Fait tuer des CPUs par killAround dans les endroits trop denses"""
        l = 2 * s.LARGEUR_CALCUL_DENSITE  # largeur reelle de l'intervalle de calcul de densite - 1
        start = random.randint(0, len(s.liste_cpus) - 1)  # on commence a un CPU aleatoire pour ne pas introduire de biais d'age
        killZones = []
        for k in range(start, len(s.liste_cpus)) :
            i = s.liste_cpus[k].ptr
            for j in range(-s.LARGEUR_CALCUL_DENSITE, s.LARGEUR_CALCUL_DENSITE+1) :
                summ = i+j
                if summ >= s.TAILLE_MEMOIRE or summ < 0:
                    summ = s.ind(summ)
                if s.nbCPUs_around_i(summ) > s.maxCPUs:
                    killZones.append(summ)
        for k in range(0, start) :
            i = s.liste_cpus[k].ptr
            for j in range(-s.LARGEUR_CALCUL_DENSITE, s.LARGEUR_CALCUL_DENSITE+1) :
                summ = i + j
                if summ >= s.TAILLE_MEMOIRE or summ < 0:
                    summ = s.ind(summ)
                n = s.nbCPUs_around_i(summ)
                if n > s.maxCPUs:
                    killZones.append(summ)
        morts=[]
        for i in killZones :
            begin = i-s.LARGEUR_CALCUL_DENSITE
            if begin < 0:
                begin = s.ind(begin)
            morts+=s.killAround(begin, s.nbCPUs_around_i(i))
        # avec cette methode est qu'apres en avoir deja supprime, on va faire appel a killAround pour des zones potentiellement deja redescendues sous la densite seuil
        # on pourrait optimiser en ne recalculant pas les nbCPUs_around_i(les indices i deja traites par un autre k)
        return morts
    def afficher(self):
        print("===============")
        print("memoire :", self.memoire)
        print("liste CPU :")
        for cpu in self.liste_cpus:
            cpu.afficher_etat()
        print("indice_cpu_actuel :", self.indice_cpu_actuel)

    def nbCPUsInLocalisation(s):   #juste pour le debogage
        d = {}
        for i in s.localisation_cpus.keys():
            for c in s.localisation_cpus[i]:
                if c in d :
                    d[c] += 1
                else :
                    d[c] = 0
        return len(d)

    def execute(self, n):
        """Execute les n CPU a venir. Attention, ne tue jamais par densite"""
        for i in range(n):
            self.executer_cpu_actuel()
            self.next_cpu()

    def copy(self):
        autre=Univers(self.nextSite,self.TAILLE_MEMOIRE,self.insDict,self.mutation,self.LARGEUR_CALCUL_DENSITE,self.maxCPUs, self.lastId)
        autre.memoire=self.memoire[:]
        autre.indice_cpu_actuel=self.indice_cpu_actuel
        autre.mutation = self.mutation
        for cpu in self.liste_cpus:
            c = cpu.copy(autre)
            autre.liste_cpus.append(c)
            autre.ajouter_cpu_localisation(c)
        return autre
    def __ne__(self,other):
        return not self.__eq__(other)
    def __eq__(self,other):
        bool = True
        bool *= self.liste_cpus==other.liste_cpus
        bool *= self.indice_cpu_actuel==other.indice_cpu_actuel
        bool *= (len(self.liste_cpus)==len(other.liste_cpus))
        bool *= self.memoire==other.memoire
        return bool




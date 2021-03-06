import unittest
import Univers
import NextSite
from Enregistrement import *
import CPU
import Instructions
import CPU
import Statistiques
import NextSite
import utests.NextSiteTest as NST
import random

class TestEnregistrement(unittest.TestCase):
    def setUp(self):
        self.i = 0
        self.U = Univers.Univers( NST.NextSiteTest())
        self.U.insDict.initialize(Instructions.instructions)
        self.U.addIndividual(0, self.U.insDict.toInts(charger_genome('eve')))
        self.U.inserer_cpu(CPU.CPU(0, self.U))
        self.N=random.randint(100,200)
        self.replay=Replay()
    def test_conversion_CPU(self):
        for i in range(self.N):
            self.U.cycle()

        for cpu in self.U.liste_cpus:
            print(cpu.id, intToCPU(CPUtoInt(cpu),self.U).id)
            self.assertTrue(cpu == intToCPU(CPUtoInt(cpu),self.U))
        self.setUp()
    def test_photo(self):
        fichier = "temp.tierra"
        self.replay.univers=self.U
        self.replay.openWrite(fichier)
        self.replay.univers=self.U.copy()
        self.replay.photo()
        self.replay.openLoad(fichier)
        self.assertTrue(self.replay.loadPhoto()==self.U)
        self.replay.close()
    def test_univers_copy(self):
        for i in range(10):
            for i in range(100):
                self.U.cycle()
            self.assertTrue(self.U == self.U.copy())
        self.setUp()
    def test_save_jump_table(self):
        fichier = "temp.tierra"
        self.replay.univers = self.U.copy()
        self.replay.openWrite(fichier)
        self.N = 420
        memoire = []
        for i in range(self.N):
            self.replay.runAndSave(1)
        memoire=self.replay.positionsPhotos[:]
        self.replay.openLoad(fichier)
        self.assertTrue(self.replay.positionsPhotos==memoire)

    def test_jump(self):
        fichier = "temp.tierra"
        self.replay.univers = self.U.copy()
        self.replay.openWrite(fichier)
        self.N = 701
        memoire = None
        bool=True
        for i in range(self.N):
            self.replay.runAndSave(1)
            if bool and self.replay.tour==204:
                memoire=self.replay.univers.copy()
                bool=False
        self.replay.openLoad(fichier)
        print(self.replay.positionsPhotos)
        self.replay.goto(204)
        self.assertTrue(memoire==self.replay.univers)

    def test_sauvegarde(self):
        fichier = "temp.tierra"
        self.replay.univers=self.U.copy()
        self.replay.openWrite(fichier)
        self.N=1000
        memoire=[]
        for i in range(self.N):
            self.replay.runAndSave(1)
            if i%100==0:
                memoire.append(self.replay.univers.copy())

        print(" ")
        self.V=self.replay.univers.copy()
        self.replay.univers=self.U.copy()
        self.replay.openLoad(fichier)
        for i in range(self.N):
            self.replay.forward(1)
            if i>=1600 and i<1650:
                univ=memoire[i-1600]
                a=5
            if i%100==0:
                bool=self.replay.univers==memoire[int(i/100)]
                if not bool:
                    pass


        self.assertTrue(self.replay.univers==self.V)
        self.replay.close()
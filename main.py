from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
import enum
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.colors

import random


class StatoCella(enum.IntEnum):
    vuoto = 0
    morto = 1
    infetto = 2
    suscettibile = 3
    guarito = 4


class Virus:
    def __init__(self, mortalita, tempo_incubazione, infettivita):
        self.mortalita = mortalita
        self.tempo_incubazione = tempo_incubazione
        self.infettivita = infettivita


class PersonAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.virus = None
        self.isAlive = True
        self.isImmune = False
        self.ttl = 0

    def step(self):
        """processo di infezione, calcolo probabilità di infettare e morire"""
        if self.isAlive:
            if self.virus is not None:
                vittime = self.model.grid.get_neighborhood(pos=self.pos, moore=False)
                for x, y in vittime:
                    probabilita = random.randrange(100)
                    if (probabilita+self.virus.infettivita) >= 100:
                        vittima = self.model.grid[x][y]
                        if vittima is not None and vittima.virus is None:
                            vittima.virus = self.virus
                            vittima.ttl = self.virus.tempo_incubazione
                self.ttl -= 1
                if self.ttl == 0:
                    probabilita = random.randrange(100)
                    if (probabilita + self.virus.mortalita) >= 100:
                        self.isAlive = False
                    else:
                        self.isImmune = True
                        self.ttl = -1

            ...


class MondoModel(Model):
    """Questo è il mondo fatto a griglia"""

    def __init__(self, popolazione, width, height):
        super().__init__()
        self.popolazione = popolazione
        self.grid = SingleGrid(width, height, True)
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.popolazione):
            a = PersonAgent(i, self)
            self.schedule.add(a)
            emptyspace = self.grid.find_empty()
            if emptyspace is not None:
                self.grid.place_agent(a, emptyspace)

        paziente_zero = self.schedule.agents[0]
        paziente_zero.virus = Virus(mortalita=20, tempo_incubazione=3, infettivita=70)
        paziente_zero.ttl = paziente_zero.virus.tempo_incubazione

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()

    def crea_grafico(self):
        global_health_status = np.zeros((self.grid.width, self.grid.height))
        for persona, x, y in self.grid.coord_iter():  # ctrl+click per spiegare meglio

            if persona is None:
                global_health_status[x][y] = StatoCella.vuoto
            elif persona.isAlive is False:
                global_health_status[x][y] = StatoCella.morto
            elif persona.isImmune is True:
                global_health_status[x][y] = StatoCella.guarito
            elif persona.virus is not None:
                global_health_status[x][y] = StatoCella.infetto
            else:
                global_health_status[x][y] = StatoCella.suscettibile

        cmap = matplotlib.colors.ListedColormap([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 0, 1), (0, 1, 0)])
        img = plt.imshow(global_health_status, interpolation='nearest', vmin=0, vmax=4, cmap=cmap)
        plt.colorbar(img, ticks=[0, 1, 2, 3, 4])
        plt.show()


if __name__ == '__main__':
    myMondo = MondoModel(9000, 100, 100)
    for i in range(50):
        myMondo.step()
        myMondo.crea_grafico()

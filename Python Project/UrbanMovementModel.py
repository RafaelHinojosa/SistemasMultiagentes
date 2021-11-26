# Importamos las clases que se requieren para manejar los agentes (Agent) y su entorno (Model).
# Cada modelo puede contener múltiples agentes.
from mesa import Agent, Model 

# Con ''SimultaneousActivation, hacemos que todos los agentes se activen ''al azar''.
from mesa.time import RandomActivation

# Haremos uso de ''DataCollector'' para obtener información de cada paso de la simulación.
from mesa.datacollection import DataCollector

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import numpy as np
import pandas as pd

from random import random

# Importamos la fila de doble fin para guardar a los agentes 
from collections import deque 

import CarAgent

def get_agents(model):
    result = []
    for agent in model.schedule.agents:
        result.append(agent.position)
    result = np.asarray(result)
    return result

class UrbanMovementModel(Model):
    def __init__(self, spawn_cars, w, h, i_dist):
        self.num_agents = 0
        self.spawn_cars = spawn_cars
        self.width = w
        self.height = h
        self.schedule = RandomActivation(self)
        self.i_dist = i_dist
        
        # (carril, semáforo, [carriles destino])
        self.intersection = [(1, 1, [8, 12]), (2, 1, [3, 7]), 
                             (5, 2, [12, 16]), (6, 2, [7, 11]),
                             (9, 3, [4, 16]), (10, 3, [11, 15]), 
                             (13, 4, [4, 8]), (14, 4, [3, 15])]
        
        self.road_pos = [[w / 2 + i_dist / 8, 0], [w / 2 + i_dist / 8 * 3, 0],
                        [w, h / 2 - i_dist / 8 * 3], [w, h / 2 - i_dist / 8],
                        [w, h / 2 + i_dist / 8], [w, h / 2 + i_dist / 8 * 3],
                        [w / 2 + i_dist / 8 * 3, h], [w / 2 + i_dist / 8, h],
                        [w / 2 - i_dist / 8, h], [w / 2 - i_dist / 8 * 3, h],
                        [0, h / 2 + i_dist / 8 * 3], [0, h / 2 + i_dist / 8],
                        [0, h / 2 - i_dist / 8], [0, h / 2 - i_dist / 8 * 3],
                        [w / 2 - i_dist / 8 * 3, 0], [w / 2 - i_dist / 8, 0]]

        self.curve = [  [w / 2 + i_dist / 8, h / 2 - i_dist / 2], [w / 2 + i_dist / 8 * 3, h / 2 - i_dist / 2],
                        [w / 2 + i_dist / 2, h / 2 - i_dist / 8 * 3], [w / 2 + i_dist / 2, h / 2 - i_dist / 8], 
                        [w / 2 + i_dist / 2, h / 2 + i_dist / 8], [w / 2 + i_dist / 2, h / 2 + i_dist / 8 * 3],
                        [w / 2 + i_dist / 8 * 3, h / 2 + i_dist / 2], [w / 2 + i_dist / 8, h / 2 + i_dist / 2], 
                        [w / 2 - i_dist / 8, h / 2 + i_dist / 2], [w / 2 - i_dist / 8 * 3, h / 2 + i_dist / 2],
                        [w / 2 - i_dist / 2, h / 2 + i_dist / 8 * 3], [w / 2 - i_dist / 2, h / 2 + i_dist / 8], 
                        [w / 2 - i_dist / 2, h / 2 - i_dist / 8], [w / 2 - i_dist / 2, h / 2 - i_dist / 8 * 3],
                        [w / 2 - i_dist / 8 * 3, h / 2 - i_dist / 2], [w / 2 - i_dist / 8, h / 2 - i_dist / 2]]

        self.light_pos = [[w / 2 + i_dist / 4, h / 2 - i_dist / 2],
                        [w / 2 + i_dist / 2, h / 2 + i_dist / 4],
                        [w / 2 - i_dist / 4, h / 2 + i_dist / 2],
                        [w / 2 - i_dist / 2, h / 2 - i_dist / 4]]
        
        self.roads_agents = [deque([]), deque([]), deque([]), deque([]), deque([]), deque([]), deque([]), deque([]), 
                            deque([]), deque([]), deque([]), deque([]), deque([]), deque([]), deque([]), deque([])]
       
        
        self.time_for_spawn = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        
        self.createAgents()

        self.datacollector = DataCollector(model_reporters = {"Agents" : get_agents})

    def createAgents(self):
        for i in range(len(self.intersection)):
            if self.time_for_spawn[i] <= 0 and random() <= self.spawn_cars:
                self.time_for_spawn[i] = 3
                self.num_agents += 1
                (road, light, dest) = self.intersection[i]
                j = np.random.randint(len(dest))
                a = CarAgent.CarAgent(self.num_agents, 
                             self, 
                             self.width, 
                             self.height, 
                             self.road_pos[road - 1], 
                             self.road_pos[dest[j] - 1], 
                             self.light_pos[light - 1], 
                             self.i_dist / 4, 
                             len(self.roads_agents[road - 1]), 
                             road - 1,
                             self.curve[road - 1],
                             self.curve[dest[j] - 1],
                             light - 1)
                self.roads_agents[road - 1].append(a)
                self.schedule.add(a)

    def step(self):
        self.createAgents()
        self.time_for_spawn -= 1
        self.datacollector.collect(self)
        self.schedule.step()
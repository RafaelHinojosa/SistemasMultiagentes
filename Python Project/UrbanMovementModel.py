from mesa import Model 
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import numpy as np
from random import random
# Importamos la fila de doble fin para guardar a los agentes 
from collections import deque
from math import ceil

import CarAgent, TrafficLightAgent


def get_agents(model):
    result = []
    for agent in model.schedule.agents:
        result.append(agent.position)
    result = np.asarray(result)
    return result


class UrbanMovementModel(Model):
    def __init__(self, spawn_cars, w, h, i_dist, max_on, max_off):
        self.num_agents = 0
        self.spawn_cars = spawn_cars
        self.width = w
        self.height = h
        self.schedule = RandomActivation(self)
        self.i_dist = i_dist
        self.max_on = max_on
        self.max_off = max_off
        self.actual_light = None
        self.delay_next_light = 0
        
        # (carril, semáforo, [carriles destino], direction)
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
        
        self.light_agents = []

        self.time_for_spawn = np.array([0, 0, 0, 0, 0, 0, 0, 0])

        self.createLights()

        self.createAgents()

        self.datacollector = DataCollector(model_reporters = {"Agents" : get_agents})


    def createLights(self):
        for i in range(len(self.light_pos)):
            self.num_agents += 1
            light = TrafficLightAgent.TrafficLightAgent(self.num_agents, self, self.light_pos[i], self.max_on, self.max_off)
            self.light_agents.append(light)
            self.schedule.add(light)


    def createAgents(self):
        for i in range(len(self.intersection)):
            if self.time_for_spawn[i] <= 0 and random() <= self.spawn_cars:
                self.time_for_spawn[i] = 3
                (road, light, dest) = self.intersection[i]
                j = np.random.randint(len(dest))
                self.num_agents += 1
                car = CarAgent.CarAgent(self.num_agents, 
                            self, 
                            self.width, 
                            self.height,
                            self.road_pos[road - 1], 
                            self.road_pos[dest[j] - 1],
                            self.light_pos[light - 1], 
                            self.i_dist / 4,
                            road - 1,
                            self.curve[road - 1],
                            self.curve[dest[j] - 1],
                            light - 1,
                            self.light_agents[light - 1])
                self.roads_agents[road - 1].append(car)
                self.schedule.add(car)


    def change_light(self):
        if self.actual_light == None and self.delay_next_light <= 0:
            best_light = None
            best_priority = 0
            for i in range(len(self.light_agents)):
                actual_light = self.light_agents[i]
                priority = 0
                if actual_light.wait_off >= actual_light.max_time_off:
                    priority += (actual_light.wait_off * 5)
                if actual_light.crossing_cars > 0:
                    priority += ceil(actual_light.sum_total_wait / actual_light.crossing_cars)
                
                if priority > best_priority:
                    best_priority = priority
                    best_light = i

            if best_light != None:
                self.light_agents[best_light].status = 1
                self.light_agents[best_light].color = 'green'
                self.actual_light = best_light
        elif self.actual_light != None and self.light_agents[self.actual_light].status == 0:
            self.actual_light = None
            self.delay_next_light = 4
        else:
            self.delay_next_light -= 1


    def step(self):
        self.createAgents()
        self.change_light()
        self.time_for_spawn -= 1
        self.datacollector.collect(self)
        self.schedule.step()
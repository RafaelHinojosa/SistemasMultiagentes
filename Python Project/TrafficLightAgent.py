from mesa import Agent
import numpy as np

class TrafficLightAgent(Agent):
    def __init__(self, unique_id, model, pos, max_on, max_off, intelligent):
        super().__init__(unique_id, model)
        
        self.type = "TrafficLight"
        self.color = "red"
        self.status = 0
        self.max_time_on = max_on
        self.max_time_off = max_off
        self.intelligent = intelligent
        self.n_cars = 0
        self.crossing_cars = 0
        self.sum_total_wait = 0
        self.time_on = 0
        self.wait_off = 0
        self.position = np.array((pos[0], pos[1]), dtype = np.float64)
    
    def step(self):
        if self.status == 1:
            self.wait_off = 0
            self.time_on += 1
            if self.intelligent == True and (self.time_on >= self.max_time_on or self.crossing_cars == 0):
                self.status = 0
                self.color = "red"
                self.time_on = 0
            elif not self.intelligent and self.time_on >= self.max_time_on:
                self.status = 0
                self.color = "red"
                self.time_on = 0
            elif not self.intelligent and self.crossing_cars == 0:
                self.model.time_unnecessary_light += 1
        else:
            if self.n_cars > 0:
                self.wait_off += 1
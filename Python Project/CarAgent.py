# Importamos las clases que se requieren para manejar los agentes (Agent) y su entorno (Model).
# Cada modelo puede contener múltiples agentes.
from mesa import Agent

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import numpy as np


class CarAgent(Agent):
    def __init__(self, unique_id, model, width, height, origin, destiny, traffic_light, stop_distance, road_queue_position, road_number, curve_origin, curve_destiny, num_traffic_light):
        super().__init__(unique_id, model)
        
        # Vector que representa la posición en 2D
        self.position = np.array((origin[0], origin[1]), dtype = np.float64)
        self.origin_road = origin
        self.destiny_road = destiny
        self.traffic_light = traffic_light
        self.stop_distance = stop_distance
        self.next_car_max_distance = 50
        self.road_queue_position = road_queue_position
        self.road_number = road_number
        self.curve_origin = curve_origin
        self.curve_destiny = curve_destiny
        self.num_traffic_light = num_traffic_light
    
        # Vector que representa la velocidad
        if origin[0] > width / 2 - stop_distance * 2 and origin[0] < width / 2 + stop_distance * 2:
            if origin[1] < height / 2:
                self.velocity = np.array([0, 10])
                self.acceleration = np.array([0, 10])
            else:
                self.velocity = np.array([0, -10])
                self.acceleration = np.array([0, -10])
        else:
            if origin[0] < width / 2:
                self.velocity = np.array([10, 0])
                self.acceleration = np.array([10, 0])
            else:
                self.velocity = np.array([-10, 0])
                self.acceleration = np.array([-10, 0])
        
        
        # Límite de aceleración
        self.max_acceleration = 10
        
        # Límite de velocidad
        self.max_speed = 60
        
        # Distancia percibida como segura por el agente
        self.perception = 50
        
        self.width = width
        self.height = height
        self.crossed_traffic_light = False
        self.curved_finished = False

    def move(self):        
        # Incluir condicion de semaforo prendido
        isFront = (self.model.roads_agents[self.road_number][0].unique_id == self.unique_id)
        
        if (isFront and self.isFarFromTrafficLight()) or self.isFarFromNextCar(isFront):
            self.position += self.velocity
            self.velocity += self.acceleration
            
            if np.linalg.norm(self.velocity) > self.max_speed:
                self.velocity = self.velocity / np.linalg.norm(self.velocity) * self.max_speed
        else:
            if np.linalg.norm(self.velocity) > 0:
                self.velocity -= self.acceleration
                self.position += self.velocity
            else:
                self.velocity *= 0
    
        if (abs(np.linalg.norm(self.position - self.curve_origin)) <= 50):
            self.crossed_traffic_light = True
            self.model.roads_agents[self.road_number].popleft()
            # Si no es una línea recta
            if (self.position[0] - self.curve_destiny[0]) * (self.position[1] - self.curve_destiny[1]) != 0:
                self.curve_points = self.curve(self.position, self.curve_destiny)
                self.temp = 0
            else:
                self.curved_finished = True

    
    def step(self):
        if not self.crossed_traffic_light:
            self.move()
        elif self.curved_finished == True:
                self.velocity = self.destiny_road - self.position
                if np.linalg.norm(self.velocity) > self.max_speed:
                    self.velocity = self.velocity / np.linalg.norm(self.velocity) * self.max_speed
                
                self.position += self.velocity
        else:
            if self.temp < len(self.curve_points):
                vec = (self.curve_points[self.temp][0] - self.position)
                self.velocity = vec
                self.position += self.velocity
                self.temp += 1
            else:
                    self.curved_finished = True

    def get_car_index(self):
        bot = 0
        top = len(self.model.roads_agents[self.road_number]) - 1
        target_id = self.unique_id
        
        while bot <= top:
            mid = int (bot + (top - bot) / 2)
            current_id = self.model.roads_agents[self.road_number][mid].unique_id
            
            if current_id == target_id:
                return mid
            elif current_id > target_id:
                top = mid - 1
            else:
                bot = mid + 1
            
        return -1

    def isFarFromTrafficLight(self):
        return (abs(np.linalg.norm(self.position + self.velocity - self.traffic_light)) > self.stop_distance * 1.5)
    
    def isFarFromNextCar(self, isFront):
        if isFront:
            return False
        else: 
            queue_position = self.get_car_index()
            next_car = self.model.roads_agents[self.road_number][queue_position - 1]
            self_speed = np.linalg.norm(self.velocity)
            self_acceleration = np.linalg.norm(self.acceleration)
            distance_to_stop = abs(0.5 * self_speed * self_speed / self_acceleration) + 80
            return (abs(np.linalg.norm((self.position + self.velocity) - (next_car.position + next_car.velocity))) > distance_to_stop)

    def curve_points(self, start, end, control, resolution=5):
            
        path = []
        for i in range(resolution+1):
            t = i/resolution
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control[0] + t**2 *end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control[1] + t**2 *end[1]
            path.append((x, y))

        return [(path[i-1], path[i]) for i in range(1, len(path))]

    def curve(self, start, end):
        turn_direction = 0
        resolution = 15
        if (self.num_traffic_light == 0):
            if (end[0] > start[0] and end[1] > start[1]):
                turn_direction = 0
                resolution = 5
            elif(end[0] < start[0] and end[1] > start[1]):
                turn_direction = 1
        elif (self.num_traffic_light == 1):
            if (end[0] < start[0] and end[1] > start[1]):
                turn_direction = 0
                resolution = 5
            elif(end[0] < start[0] and end[1] < start[1]):
                turn_direction = 1
        elif (self.num_traffic_light == 2):
            if (end[0] < start[0] and end[1] < start[1]):
                turn_direction = 0
                resolution = 5
            elif(end[0] > start[0] and end[1] < start[1]):
                turn_direction = 1
        elif (self.num_traffic_light == 3):
            if (end[0] > start[0] and end[1] < start[1]):
                turn_direction = 0
                resolution = 5
            elif(end[0] > start[0] and end[1] > start[1]):
                turn_direction = 1


        CLOCK_WISE = 0
        NON_CLOCK_WISE = 1
        # Get control point
        x = min(start[0], end[0])
        y = min(start[1], end[1])

        if turn_direction == CLOCK_WISE:
            control = (x - y + start[1], y - x + end[0])
        else:
            control = (x - y + end[1], y - x + start[0])
        
        return self.curve_points(start, end, control, resolution=resolution)

from mesa import Agent
import numpy as np


class CarAgent(Agent):
    def __init__(self, unique_id, model, origin, destiny, stop_distance, road_number, curve_origin, curve_destiny, num_traffic_light, light_agent):
        super().__init__(unique_id, model)
        
        # Initial spawn position
        self.type = "Car"
        self.position = np.array((origin[0], origin[1]), dtype = np.float64)
        self.origin_road = np.array((origin[0], origin[1]), dtype = np.float64)
        self.destiny_road = destiny
        self.stop_distance = stop_distance
        self.next_car_min_distance = stop_distance
        self.road_number = road_number
        self.curve_origin = curve_origin
        self.curve_destiny = curve_destiny
        self.num_traffic_light = num_traffic_light
        self.light_agent = light_agent
        self.light_agent.n_cars += 1
        # Speed limit
        self.max_speed = self.stop_distance / 2
        self.crossed_traffic_light = None
        self.total_wait = 0
        self.curved_finished = False

        if (self.num_traffic_light == 0):
            self.speed = np.array([0, (self.stop_distance / 4)])
            self.acceleration = np.array([0, (self.stop_distance / 4)])
        elif (self.num_traffic_light == 1):
            self.speed = np.array([-(self.stop_distance / 4), 0])
            self.acceleration = np.array([-(self.stop_distance / 4), 0])
        elif (self.num_traffic_light == 2):
            self.speed = np.array([0, -(self.stop_distance / 4)])
            self.acceleration = np.array([0, -(self.stop_distance / 4)])
        elif (self.num_traffic_light == 3):
            self.speed = np.array([(self.stop_distance / 4), 0])
            self.acceleration = np.array([(self.stop_distance / 4), 0])


    def move_start(self):
        # Determine if car is the first one of the road
        is_front = (self.model.roads_agents[self.road_number][0].unique_id == self.unique_id)
        
        if (is_front and (self.light_agent.status == 1 or self.is_far_from_traffic_light())) or self.is_far_from_next_car(is_front):
            if(self.has_to_curve() and self.will_cross_traffic_light()):
                self.position += self.acceleration
                self.update_when_crossed()
            else:
                self.position += self.speed
                self.speed += self.acceleration
            
                if np.linalg.norm(self.speed) > self.max_speed:
                    self.speed = self.speed / np.linalg.norm(self.speed) * self.max_speed

                if self.crossed_traffic_light == None and self.is_about_cross_traffic_light():
                    self.crossed_traffic_light = False
                    self.light_agent.crossing_cars += 1
        else:
            if np.linalg.norm(self.speed) > 0:
                self.speed -= self.acceleration
                self.position += self.speed
            elif np.linalg.norm(self.speed) == 0:
                self.model.total_wait_time += 1
                self.light_agent.sum_total_wait += 1
                self.total_wait += 1
            else:
                self.speed *= 0

        if self.has_crossed_traffic_light() and self.crossed_traffic_light != True:
            self.update_when_crossed()


    def update_when_crossed(self):
        if self.crossed_traffic_light == False:
            self.light_agent.crossing_cars -= 1
        self.crossed_traffic_light = True
        self.light_agent.n_cars -= 1
        self.light_agent.sum_total_wait -= self.total_wait
        self.total_wait = 0
        # Deque car from road
        self.model.roads_agents[self.road_number].popleft()
        # If it has to curve to reach destiny
        if self.has_to_curve():
            self.curve_points = self.curve(self.position, self.curve_destiny)
            self.temp = len(self.curve_points) - 1
            self.move_curve()
        # No curve, go forward
        else:
            self.curved_finished = True
            self.move_destination()


    def move_curve(self):
        if self.temp < len(self.curve_points):
            vec = (self.curve_points[self.temp][0] - self.position)
            self.speed = vec
            self.position += self.speed
            self.temp += 2
        else:
            self.curved_finished = True
            self.move_destination()

    def move_destination(self):
        self.speed = self.destiny_road - self.position
        if np.linalg.norm(self.speed) > self.max_speed:
            self.speed = self.speed / np.linalg.norm(self.speed) * self.max_speed
        self.position += self.speed

    def step(self):
        if self.crossed_traffic_light != True:
            self.move_start()
        elif self.curved_finished == True:
            self.move_destination()
        else:
            self.move_curve()

    def get_car_index(self):
        bot = 0
        top = len(self.model.roads_agents[self.road_number]) - 1
        target_id = self.unique_id
        # Binary Search
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


    def is_far_from_traffic_light(self):
        return (abs(np.linalg.norm(self.position + self.speed - self.curve_origin)) > self.stop_distance * 3)


    def is_about_cross_traffic_light(self):
        return (abs(np.linalg.norm(self.position + self.speed - self.curve_origin)) < self.stop_distance * 4.5)


    def is_far_from_next_car(self, is_front):
        if is_front:
            return False
        else:
            queue_position = self.get_car_index()
            next_car = self.model.roads_agents[self.road_number][queue_position - 1]
            self_speed = np.linalg.norm(self.speed)
            self_acceleration = np.linalg.norm(self.acceleration)
            distance_to_stop = abs(0.5 * self_speed * self_speed / self_acceleration) + (self.next_car_min_distance * 3)
            return (abs(np.linalg.norm((self.position + self.speed) - (next_car.position + next_car.speed))) > distance_to_stop)

    def has_crossed_traffic_light(self):
        return (abs(np.linalg.norm(self.position - self.origin_road)) \
                    > abs(np.linalg.norm(self.curve_origin - self.origin_road)))
    
    def will_cross_traffic_light(self):
        return (abs(np.linalg.norm(self.position + self.speed - self.origin_road)) \
                    > abs(np.linalg.norm(self.curve_origin - self.origin_road)))

    def has_to_curve(self):
        return (self.position[0] - self.curve_destiny[0]) * (self.position[1] - self.curve_destiny[1]) != 0


    def curve_points(self, start, end, control, resolution = 5):
        path = []
        for i in range(resolution+1):
            t = i/resolution
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control[0] + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control[1] + t**2 * end[1]
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
        # Get control point
        x = min(start[0], end[0])
        y = min(start[1], end[1])

        if turn_direction == CLOCK_WISE:
            control = (x - y + start[1], y - x + end[0])
        else:
            control = (x - y + end[1], y - x + start[0])
        
        return self.curve_points(start, end, control, resolution=resolution)
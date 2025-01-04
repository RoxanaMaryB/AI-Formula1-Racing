from model.game import *
from car import *

MIN_SPEED = 20
MAX_SPEED = 60

class AICar(Car):
    def __init__(self, game, must_draw=False, sprite=None, size = [100, 50], start_position = [1200, 820]):
        super().__init__(game, must_draw, sprite, size, start_position)
        self.min_speed = MIN_SPEED
        self.max_speed = MAX_SPEED
        self.speed = self.min_speed

    def set_net(self, net):
        self.net = net

    # Overload
    def get_choice(self):
        output = self.net.activate(self.get_data())
        choice = output.index(max(output))
        return choice + 1

    def get_data(self):
        self.radars.clear()
        for d in range(-120, 120 + 1, 30):
            self.check_radar(d)

        return_values = [0] * 9
        for i, radar in enumerate(self.radars):
            return_values[i] = int(radar[1] / 30)
        return return_values
    
    def check_radar(self, degree):
        radar_direction = cis(self.angle + degree)

        # Binary search is much faster
        a, b = 0, 32
        while True:
            point = self.sensors + b * radar_direction
            if self.game.pixel_out_of_bounds(point):
                break
            a, b = b, b + 32

        while a <= b:
            m = (a + b + 1) / 2
            point = self.sensors + m * radar_direction
            if self.game.pixel_out_of_bounds(point):
                b = m - 1
            else:
                a = m
        
        # while not self.game.pixel_out_of_bounds(point):
        #     point = point + radar_direction

        # Calculate Distance To Border And Append To Radars List
        # dist = np.linalg.norm(point - self.sensors)
        point = self.sensors + a * radar_direction
        self.radars.append([point, a])


    def get_reward(self):
        # if self.won:
        #     return MAX_REWARD
        # if self.reward > 0:
        #     return self.reward
        return (self.distance / 50) * (1 + 2 * self.alive)

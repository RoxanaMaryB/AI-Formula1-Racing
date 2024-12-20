import pygame
import math
import numpy as np
from game import *

MIN_SPEED = 30
MAX_SPEED = 60

def cis(angle):
    angle = math.radians(angle)
    return np.array([math.cos(angle), -math.sin(angle)])

class AICar:

    def __init__(self, game, must_draw = False, sprite = None, size = [100, 50], position = [1201, 925]):
        self.game = game
        self.must_draw = False
        self.sprite = sprite

        self.set_size(size)
        self.set_angle(0)
        if must_draw:
            self.start_drawing()
        self.set_position(position)

        self.distance = 0
        self.time = 0
        self.alive = True
        self.radars = []
        self.sensors = np.array([0, 0])
        self.speed = MIN_SPEED

    def start_drawing(self):
        if self.must_draw:
            return
        self.must_draw = True
        self.sprite_resized = pygame.transform.scale(self.sprite, self.size)
        self.rotate_sprite()

    def stop_drawing(self):
        self.must_draw = False

    def set_size(self, size):
        self.size = size
        if self.sprite is not None:
            self.sprite_resized = pygame.transform.scale(self.sprite, self.size)
        if self.must_draw:
            self.rotate_sprite()

    def set_angle(self, angle):
        self.angle = angle
        self.direction = cis(angle)
        self.rotate_sprite()

    def rotate_sprite(self):
        if self.must_draw:
            self.rotated_sprite = pygame.transform.rotate(self.sprite_resized, self.angle)

    def set_position(self, position):
        self.position = np.array(position)
        self.center = self.position + np.array(self.size) / 2
        self.sensors = self.center + self.direction * self.size[0] / 2

    def is_alive(self):
        return self.alive

    def draw(self, screen):
        if self.must_draw:
            screen.blit(self.rotated_sprite, self.position)
            for radar in self.radars:
                RADAR_COLOR = (100, 200, 100)
                position = radar[0]
                pygame.draw.circle(screen, RADAR_COLOR, position, 5)
                pygame.draw.line(screen, RADAR_COLOR, self.sensors, position, 3)

    def check_collision(self):
        self.alive = True
        for point in self.corners:
            if self.game.pixel_out_of_bounds(point):
                self.alive = False
                return

    def check_radar(self, degree):
        radar_direction = cis(self.angle + degree)

        point = self.sensors
        while not self.game.pixel_out_of_bounds(point):
            point = point + radar_direction

        # Calculate Distance To Border And Append To Radars List
        dist = np.linalg.norm(point - self.sensors)
        self.radars.append([point, dist])

    def update(self):
        self.distance += self.speed
        self.set_angle(self.angle)
        self.set_position(self.position + (self.speed * self.size[0]) / 1000 * self.direction)

        length = 0.5 * self.size[0]
        left_top     = self.center + cis(self.angle +  30) * length
        right_top    = self.center + cis(self.angle + 150) * length
        left_bottom  = self.center + cis(self.angle + 210) * length
        right_bottom = self.center + cis(self.angle + 330) * length
        self.corners = [left_top, right_top, left_bottom, right_bottom]
        self.check_collision()

    def update_position(self, choice):
        if choice == 0:
            self.angle += 3 # Left
        elif choice == 1:
            self.angle -= 3 # Right
        elif choice == 2:
            if(self.speed - 2 >= MIN_SPEED):
                self.speed -= 2 # Slow Down
        else:
            if(self.speed + 2 <= MAX_SPEED):
                self.speed += 2 # Speed Up
        self.update()

    def get_data(self):
        self.radars.clear()
        for d in range(-120, 120 + 1, 30):
            self.check_radar(d)

        return_values = [0] * 9
        for i, radar in enumerate(self.radars):
            return_values[i] = int(radar[1] / 30)
        return return_values

    def get_reward(self):
        return self.distance / 50

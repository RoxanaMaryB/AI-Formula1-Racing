import pygame
import math
import numpy as np
from game import *

MIN_SPEED = 30
MAX_SPEED = 75
MAX_REWARD = 1000

def cis(angle):
    angle = math.radians(angle)
    return np.array([math.cos(angle), -math.sin(angle)])

class AICar:

    def __init__(self, game, must_draw = False, sprite = None, size = [100, 50], position = [1200, 925]):
        self.game = game
        self.must_draw = False
        self.sprite = sprite

        self.set_size(size)
        self.set_angle(0)
        self.set_position(position)
        if must_draw:
            self.start_drawing()

        self.distance = 0
        self.time = 0
        self.alive = True
        self.won = False
        self.radars = []
        self.sensors = np.array([0, 0])
        self.speed = MIN_SPEED
        self.reward = 0
        self.total_speed = 0
        self.update_count = 0

    def start_drawing(self):
        if self.must_draw:
            return
        self.must_draw = True
        if self.sprite is not None:
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
        if self.must_draw and hasattr(self, 'sprite_resized'):
            self.rotated_sprite = pygame.transform.rotate(self.sprite_resized, self.angle)
            self.rotated_sprite.set_colorkey((0, 0, 0))
            
    def set_position(self, position):
        self.position = np.array(position)
        self.center = self.position + np.array(self.size) / 2
        self.sensors = self.center + self.direction * self.size[0] / 2

    def draw(self, screen):
        if self.must_draw:
            rotated_rect = self.rotated_sprite.get_rect(center=self.sprite_resized.get_rect(topleft=self.position).center)
            screen.blit(self.rotated_sprite, rotated_rect.topleft)
            # screen.blit(self.rotated_sprite, self.position)

            RADAR_COLOR = (100, 200, 100)
            for radar in self.radars:
                position = radar[0]
                pygame.draw.circle(screen, RADAR_COLOR, position, 5)
                pygame.draw.line(screen, RADAR_COLOR, self.sensors, position, 3)
            # CORNER_COLOR = (150, 50, 50)
            # for corner in self.corners:
            #     pygame.draw.circle(screen, CORNER_COLOR, corner, 10)

    def is_alive(self):
        return self.alive

    def check_collision(self):
        self.alive = True
        for point in self.corners:
            if self.game.pixel_out_of_bounds(point):
                print(f"Collision detected at point: {point}")
                self.alive = False
                return

    def check_radar(self, degree):
        radar_direction = cis(self.angle + degree)

        # Binary search is muuch faster
        a, b = 0, 128
        while True:
            point = self.sensors + b * radar_direction
            if self.game.pixel_out_of_bounds(point):
                break
            a, b = b, b + 128

        while a <= b:
            m = (a + b + 1) / 2
            point = self.sensors + m * radar_direction
            if self.game.pixel_out_of_bounds(point):
                b = m - 1
            else:
                a = m
        point = self.sensors + a * radar_direction

        # while not self.game.pixel_out_of_bounds(point):
        #     point = point + radar_direction

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

        if self.check_green_color():
            self.alive = False
            self.won = True

    def update_position(self, choice):
        if choice == 0:
            self.angle += 3 # Left
        elif choice == 1:
            self.angle -= 3 # Right
        elif choice == 2:
            if(self.speed - 2 >= MIN_SPEED):
                self.speed -= 2 # Slow Down
        else:
            if(self.speed + 1 <= MAX_SPEED):
                self.speed += 1 # Speed Up
        self.update()

    def check_green_color(self):
        GREEN_COLOR = (34, 177, 76, 255)  # Define the green color
        for point in self.corners:
            if self.game.map.get_at((int(point[0]), int(point[1]))) == GREEN_COLOR:
                return True
        return False

    def get_data(self):
        self.radars.clear()
        for d in range(-120, 120 + 1, 30):
            self.check_radar(d)

        return_values = [0] * 9
        for i, radar in enumerate(self.radars):
            return_values[i] = int(radar[1] / 30)
        return return_values

    def get_reward(self):
        standard_reward = self.reward if self.reward > 0 else self.distance / 50
        if self.won:
            standard_reward = MAX_REWARD
        return standard_reward

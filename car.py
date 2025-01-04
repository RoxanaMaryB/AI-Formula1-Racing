import pygame
import math
import numpy as np
from model.game import *

STEERING_ANGLE = 5

def cis(angle):
    angle = math.radians(angle)
    return np.array([math.cos(angle), -math.sin(angle)])

class Car:
    def __init__(self, game, must_draw = False, sprite = None, size = [100, 50], start_position = [1200, 820]):
        self.game = game
        self.sprite = sprite
        self.must_draw = must_draw
        self.start_position = start_position
        self.size = size
        self.start_position = start_position
        self.min_speed = 0
        self.max_speed = 500 # Big number
        self.reset()

    def reset(self):
        self.set_size(self.size)
        self.set_angle(0)
        self.set_position(self.start_position)
        if self.must_draw:
            self.start_drawing()
        self.distance = 0
        self.time = 0
        self.alive = True
        self.won = False
        self.radars = []
        self.sensors = np.array([0, 0])
        self.speed = self.min_speed
        self.reward = 0
        self.total_speed = 0
        self.update_count = 0

    def start_drawing(self):
        self.must_draw = True

    def stop_drawing(self):
        self.must_draw = False

    def set_size(self, size):
        self.size = size

    def set_position(self, position):
        self.center = position
        self.sensors = self.center + self.direction * self.size[0] / 2

    def set_angle(self, angle):
        self.angle = angle
        self.direction = cis(angle)

    def set_position(self, position):
        self.position = np.array(position)
        self.center = self.position + np.array(self.size) / 2
        self.sensors = self.center + self.direction * self.size[0] / 2

    def draw(self, screen):
        if not self.must_draw:
            return
        sprite_rotated = self.game.sprite_cache(self)
        rotated_rect = sprite_rotated.get_rect(center = self.center)
        screen.blit(sprite_rotated, rotated_rect)

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
                # print(f"Collision detected at point: {point}")
                self.alive = False
                return

    def update(self):
        self.update_position_from_choice(self.get_choice())

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
            self.won = True

    def update_position_from_choice(self, choice):
        if choice == 0:
            pass
        elif choice == 1:
            self.angle += 3 # Left
        elif choice == 2:
            self.angle -= 3 # Right
        elif choice == 3:
            if(self.speed - 2 >= self.min_speed):
                self.speed -= 2 # Slow Down
        elif choice == 4:
            if(self.speed + 1 <= self.max_speed):
                self.speed += 1 # Speed Up

    def get_choice(self):
        return 0

    def check_green_color(self):
        # return False
        GREEN_COLOR = (34, 177, 76, 255)  # Define the green color
        for point in self.corners:
            if self.game.map.get_at((int(point[0]), int(point[1]))) == GREEN_COLOR:
                return True
        return False


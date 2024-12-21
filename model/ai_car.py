import pygame
import math
import numpy as np
from game import *

MIN_SPEED = 30
MAX_SPEED = 75
STEERING_ANGLE = 5

def cis(angle):
    angle = math.radians(angle)
    return np.array([math.cos(angle), -math.sin(angle)])

class AICar:

    def __init__(self, game, must_draw = False, sprite = None, size = [100, 50], start_position = [1200, 925]):
        self.game = game
        self.sprite = sprite
        self.must_draw = must_draw
        self.start_position = start_position

        self.set_size(size)
        self.reset()

    def reset(self):
        self.set_angle(0)
        self.set_position(self.start_position)
        self.distance = 0
        self.time = 0
        self.alive = True
        self.radars = []
        self.sensors = np.array([0, 0])
        self.speed = MIN_SPEED

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
                self.alive = False
                return

    def check_radar(self, degree):
        radar_direction = cis(self.angle + degree)

        # Binary search is muuch faster
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

        self.radars.append([point, a])

    def update(self):
        self.distance += self.speed
        self.set_angle(self.angle)
        self.set_position(self.center + (self.speed * self.size[0]) / 1000 * self.direction)

        length = 0.5 * self.size[0]
        left_top     = self.center + cis(self.angle +  30) * length
        right_top    = self.center + cis(self.angle + 150) * length
        left_bottom  = self.center + cis(self.angle + 210) * length
        right_bottom = self.center + cis(self.angle + 330) * length
        self.corners = [left_top, right_top, left_bottom, right_bottom]
        self.check_collision()

    def update_position(self, choice):
        if choice == 0:
            self.angle += STEERING_ANGLE # Left
        elif choice == 1:
            self.angle -= STEERING_ANGLE # Right
        elif choice == 2:
            if(self.speed - 2 >= MIN_SPEED):
                self.speed -= 2 # Slow Down
        else:
            if(self.speed + 1 <= MAX_SPEED):
                self.speed += 1 # Speed Up
        self.update()

    def update_position_from_keyboard(self):
        print("maris")
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                print("marus")
                if event.key == pygame.K_w:
                    self.update_position(3)
                elif event.key == pygame.K_a:
                    self.update_position(0)
                elif event.key == pygame.K_d:
                    self.update_position(1)
                elif event.key == pygame.K_s:
                    self.update_position(2)
            return
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
        return (self.distance / 1000) * (self.alive + 1)

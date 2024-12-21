import pygame
import math
import numpy as np
from game import *

MIN_SPEED = 30
MAX_SPEED = 75
<<<<<<< HEAD
STEERING_ANGLE = 5
=======
MAX_REWARD = 1000
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

def cis(angle):
    angle = math.radians(angle)
    return np.array([math.cos(angle), -math.sin(angle)])

class AICar:

<<<<<<< HEAD
    def __init__(self, game, must_draw = False, sprite = None, size = [100, 50], start_position = [1200, 925]):
=======
    def __init__(self, game, must_draw = False, sprite = None, size = [100, 50], position = [1200, 925]):
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2
        self.game = game
        self.sprite = sprite
<<<<<<< HEAD
        self.must_draw = must_draw
        self.start_position = start_position
=======
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

        self.set_size(size)
        self.reset()

    def reset(self):
        self.set_angle(0)
<<<<<<< HEAD
        self.set_position(self.start_position)
        self.distance = 0
        self.time = 0
        self.alive = True
        self.radars = []
        self.sensors = np.array([0, 0])
        self.speed = MIN_SPEED
=======
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
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

    def start_drawing(self):
        self.must_draw = True
<<<<<<< HEAD
=======
        if self.sprite is not None:
            self.sprite_resized = pygame.transform.scale(self.sprite, self.size)
        self.rotate_sprite()
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

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
<<<<<<< HEAD

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
=======
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
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

    def is_alive(self):
        return self.alive

    def check_collision(self):
        self.alive = True
        for point in self.corners:
            if self.game.pixel_out_of_bounds(point):
<<<<<<< HEAD
=======
                print(f"Collision detected at point: {point}")
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2
                self.alive = False
                return

    def check_radar(self, degree):
        radar_direction = cis(self.angle + degree)

        # Binary search is muuch faster
<<<<<<< HEAD
        a, b = 0, 32
=======
        a, b = 0, 128
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2
        while True:
            point = self.sensors + b * radar_direction
            if self.game.pixel_out_of_bounds(point):
                break
<<<<<<< HEAD
            a, b = b, b + 32
=======
            a, b = b, b + 128
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

        while a <= b:
            m = (a + b + 1) / 2
            point = self.sensors + m * radar_direction
            if self.game.pixel_out_of_bounds(point):
                b = m - 1
            else:
                a = m
<<<<<<< HEAD
=======
        point = self.sensors + a * radar_direction
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

        # while not self.game.pixel_out_of_bounds(point):
        #     point = point + radar_direction

<<<<<<< HEAD
        self.radars.append([point, a])
=======
        # Calculate Distance To Border And Append To Radars List
        dist = np.linalg.norm(point - self.sensors)
        self.radars.append([point, dist])
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

    def update(self):
        self.distance += self.speed
        self.set_angle(self.angle)
<<<<<<< HEAD
        self.set_position(self.center + (self.speed * self.size[0]) / 1000 * self.direction)
=======
        self.set_position(self.position + (self.speed * self.size[0]) / 1000 * self.direction)
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

        length = 0.5 * self.size[0]
        left_top     = self.center + cis(self.angle +  30) * length
        right_top    = self.center + cis(self.angle + 150) * length
        left_bottom  = self.center + cis(self.angle + 210) * length
        right_bottom = self.center + cis(self.angle + 330) * length
        self.corners = [left_top, right_top, left_bottom, right_bottom]
        self.check_collision()
<<<<<<< HEAD

    def update_position(self, choice):
        if choice == 0:
            self.angle += STEERING_ANGLE # Left
        elif choice == 1:
            self.angle -= STEERING_ANGLE # Right
=======

        if self.check_green_color():
            self.alive = False
            self.won = True

    def update_position(self, choice):
        if choice == 0:
            self.angle += 3 # Left
        elif choice == 1:
            self.angle -= 3 # Right
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2
        elif choice == 2:
            if(self.speed - 2 >= MIN_SPEED):
                self.speed -= 2 # Slow Down
        else:
            if(self.speed + 1 <= MAX_SPEED):
                self.speed += 1 # Speed Up
        self.update()
<<<<<<< HEAD
=======

    def check_green_color(self):
        GREEN_COLOR = (34, 177, 76, 255)  # Define the green color
        for point in self.corners:
            if self.game.map.get_at((int(point[0]), int(point[1]))) == GREEN_COLOR:
                return True
        return False
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

    def get_data(self):
        self.radars.clear()
        for d in range(-120, 120 + 1, 30):
            self.check_radar(d)

        return_values = [0] * 9
        for i, radar in enumerate(self.radars):
            return_values[i] = int(radar[1] / 30)
        return return_values

    def get_reward(self):
<<<<<<< HEAD
        return (self.distance / 1000) * (self.alive + 1)
=======
        standard_reward = self.reward if self.reward > 0 else self.distance / 50
        if self.won:
            standard_reward = MAX_REWARD
        return standard_reward
>>>>>>> 8dee5b7b9a4907d03dfb3dbbcfbf5d7b0a5685b2

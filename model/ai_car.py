import pygame
import math
import numpy as np
from game import *

BORDER_COLOR = (255, 255, 255, 255)

class AICar:
    
    def __init__(self, game, must_draw = False, sprite = None, size = [100, 50], position = [1201, 925]):
        self.game = game
        self.must_draw = False
        self.sprite = sprite
        self.set_size(size)
        self.set_angle(0)
        if must_draw:
            self.start_drawing()
        self.position = position
        self.speed = 0
        self.distance = 0
        self.time = 0
        self.alive = True
        self.center = [int(self.position[0]) + self.size[0] / 2, int(self.position[1]) + self.size[1] / 2]
        self.radars = []
        self.speed = 12

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
        angle_rads = math.radians(angle)
        self.direction = [math.cos(angle_rads), -math.sin(angle_rads)]
        self.rotate_sprite()

    def rotate_sprite(self):
        if self.must_draw:
            self.rotated_sprite = pygame.transform.rotate(self.sprite_resized, self.angle)

    def set_position(self, position):
        self.position = position

    def is_alive(self):
        return self.alive

    def draw(self, screen):
        if self.must_draw:
            screen.blit(self.rotated_sprite, self.position)

    def check_collision(self, map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if self.game.map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while length < 300:
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

            # Check if x and y are within the bounds of the map
            if x < 0 or x >= 1920 or y < 0 or y >= 1080:
                break

            if game_map.get_at((x, y)) == BORDER_COLOR:
                break

            length += 1

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self):
        self.set_position(np.add(self.position, np.multiply((self.speed * self.size[0]) / 50, self.direction)))
        self.center = [int(self.position[0]) + self.size[0] / 2, int(self.position[1]) + self.size[1] / 2]
        length = 0.5 * self.size[0]
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]
        self.check_collision(self.game.map)

    def update_position(self, choice):
        if choice == 0:
            self.angle += 10 # Left
        elif choice == 1:
            self.angle -= 10 # Right
        elif choice == 2:
            if(self.speed - 2 >= 12):
                self.speed -= 2 # Slow Down
        else:
            self.speed += 2 # Speed Up

    def get_data(self):
        self.radars.clear()
        for d in range(-120, 121, 30):
            self.check_radar(d, self.game.map)
        radars = self.radars
        return_values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)
        return return_values

    def get_reward(self):
        return self.distance / 50

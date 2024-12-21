import pygame
import math
import numpy as np

class UserCar:
    def __init__(self, sprite_path, size=[100, 50], position=[1220, 820]):
        self.must_draw = False

        self.sprite = pygame.image.load(sprite_path)  # Load the sprite image
        self.position = np.array(position, dtype=float)
        self.set_angle(0)
        self.set_size(size)

        self.speed = 0
        self.distance = 0
        self.time = 0
        self.alive = True

    def set_size(self, size):
        self.size = size
        self.sprite_resized = pygame.transform.scale(self.sprite, self.size)

    def start_drawing(self):
        if self.must_draw:
            return
        self.must_draw = True
        self.sprite_resized = pygame.transform.scale(self.sprite, self.size)
        self.rotate_sprite()

    def set_angle(self, angle):
        self.angle = angle
        self.direction = self.cis(angle)
        self.rotate_sprite()

    def rotate_sprite(self):
        if hasattr(self, 'sprite_resized'):
            self.sprite_resized = pygame.transform.rotate(self.sprite_resized, self.angle)

    def cis(self, angle):
        angle = math.radians(angle)
        return np.array([math.cos(angle), -math.sin(angle)])

    def update(self, player_input):
        if player_input["steering"] == -1:
            self.angle += 3  # Left
        elif player_input["steering"] == 1:
            self.angle -= 3  # Right

        if player_input["acceleration"] == 1:
            self.speed += 1  # Speed Up
        elif player_input["acceleration"] == -1:
            self.speed -= 1  # Slow Down

        self.set_angle(self.angle)
        self.position += self.speed * self.direction

    def draw(self, screen):
        rotated_rect = self.sprite_resized.get_rect(center=self.sprite_resized.get_rect(topleft=self.position).center)
        screen.blit(self.sprite_resized, rotated_rect.topleft)

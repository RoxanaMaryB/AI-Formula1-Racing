import pygame
from car import *

class Game:

    def __init__(self, dimensions, map_file, car_file):
        pygame.init()
        self.screen = pygame.display.set_mode((dimensions[0], dimensions[1]), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.map_file = map_file
        self.map = pygame.image.load(map_file).convert()
        self.car_sprite = pygame.image.load(car_file).convert()
        self.cars = []

    def draw_map(self):
        for car in self.cars:
            car.draw(self.screen)

    def add_car(self, car):
        self.cars.append(car)

    def update_screen(self):
        self.screen.blit(self.map, (0, 0))
        self.draw_map()
        pygame.display.flip()


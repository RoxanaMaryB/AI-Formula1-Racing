import pygame
from ai_car import *

class Game:
    def __init__(self, dimensions, map_file, car_file):
        pygame.init()
        self.screen = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
        self.virtual_screen = pygame.Surface([1920, 1080])
        self.map = pygame.image.load(map_file).convert()

        self.clock = pygame.time.Clock()
        self.car_sprite = pygame.image.load(car_file).convert()
        self.cars = []
        self.update_dimensions(dimensions)

    def draw_map(self):
        for car in self.cars:
            car.draw(self.virtual_screen)

    def add_car(self, car):
        self.cars.append(car)

    def update_screen(self):
        self.virtual_screen.blit(self.map, (0, 0))
        self.draw_map()
        scaled_surface = pygame.transform.scale(self.virtual_screen, self.dimensions)
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def update_dimensions(self, dimensions):
        self.dimensions = dimensions
        self.update_screen()

    def pixel_out_of_bounds(self, v):
        BORDER_COLOR = (255, 255, 255, 255)

        # Check if x and y are within the bounds of the map
        if v[0] < 0 or v[0] >= 1920 or v[1] < 0 or v[1] >= 1080:
            return True
        if self.map.get_at((int(v[0]), int(v[1]))) == BORDER_COLOR:
            return True

        return False

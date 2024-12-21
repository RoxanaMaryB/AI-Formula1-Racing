import sys
import pygame
from ai_car import *

class Game:
    def __init__(self, dimensions, map_file, car_file):
        pygame.init()
        self.screen = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
        self.virtual_screen = pygame.Surface([1920, 1080])
        self.map = pygame.image.load(map_file).convert()
        self.must_update = True

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.car_sprite = pygame.image.load(car_file).convert()
        self.cars = []
        self.update_dimensions(dimensions)

    def draw_map(self):
        for car in self.cars:
            car.draw(self.virtual_screen)

    def add_car(self, car):
        self.cars.append(car)

    def update(self):
        self.get_game_events()
        if not self.must_update:
            return
        self.virtual_screen.blit(self.map, (0, 0))
        self.draw_map()
        scaled_surface = pygame.transform.scale(self.virtual_screen, self.dimensions)
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        self.clock.tick(self.fps)

    def update_dimensions(self, dimensions):
        self.dimensions = dimensions
        self.update()

    def get_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Exit on ESC key press
                    sys.exit(0)
                if event.key == pygame.K_o:
                    self.fps = 60 - self.fps
                if event.key == pygame.K_p:
                    if not self.must_update:
                        self.must_update = True
                        for car in self.cars:
                            car.start_drawing()
                    else:
                        self.must_update = False
                        for car in self.cars:
                            car.stop_drawing()

    def pixel_out_of_bounds(self, v):
        BORDER_COLOR = (255, 255, 255, 255)

        # Check if x and y are within the bounds of the map
        if v[0] < 0 or v[0] >= 1920 or v[1] < 0 or v[1] >= 1080:
            return True
        if self.map.get_at((int(v[0]), int(v[1]))) == BORDER_COLOR:
            return True

        return False

import pygame

class Game:

    def __init__(self, dimensions, map_file, car_sprite):
        pygame.init()
        self.screen = pygame.display.set_mode((dimensions[0], dimensions[1]), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.map = pygame.image.load(map_file).convert()
        self.car_sprite = car_sprite
        self.cars = []

    def draw_map(self):
        pass

    def update_screen(self):
        self.screen.blit(self.map, (0, 0))
        self.draw_map()
        pygame.display.flip()

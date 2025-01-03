import pygame
from ai_car import *

class Game:
    def __init__(self, dimensions, map_file, car_file):
        pygame.init()
        self.screen = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
        self.virtual_screen = pygame.Surface([1920, 1080])
        self.map = pygame.image.load(map_file).convert()
        self.must_update = True

        self.user_car = None

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.car_sprite = pygame.image.load(car_file).convert()
        self.cars = []
        self.update_dimensions(dimensions)

        self.hashtables = [{}, {}]
        self.display_idx = None

    def add_user_car(self, car):
        car.start_drawing()
        car.speed = 1
        self.user_car = car

    def set_display_idx(self, idx):
        self.display_idx = idx

    def must_update_depending_on_idx(self, idx):
        if self.display_idx is None:
            return True
        return idx in self.display_idx

    def sprite_cache(self, car):
        sprite_resized = self.hashtables[0].setdefault(car.sprite, pygame.transform.scale(car.sprite, car.size))
        pair = (sprite_resized, car.angle)
        if pair not in self.hashtables[1]:
            sprite_rotated = pygame.transform.rotate(sprite_resized, car.angle)
            sprite_rotated.set_colorkey((0, 0, 0))
            self.hashtables[1][pair] = sprite_rotated
            return sprite_rotated
        return self.hashtables[1][pair]

    def draw_map(self):
        for car in self.cars:
            car.draw(self.virtual_screen)

    def add_car(self, car):
        self.cars.append(car)

    def update_dimensions(self, dimensions):
        self.dimensions = dimensions
        self.update()

    def update(self):
        self.get_game_events()
        if not self.must_update:
            return
        if self.user_car is not None:
            self.user_car.update()
            if self.user_car.check_collision() or self.user_car.check_green_color():
                print("User car get the finish line")
                self.user_car.reset_user()


        self.virtual_screen.blit(self.map, (0, 0))
        if self.user_car is not None:
            if self.user_car.is_alive():
                self.user_car.must_draw = True
                self.user_car.draw(self.virtual_screen)
            else:
                self.user_car.reset_user()
        if self.must_update:
            self.draw_map()

        scaled_surface = pygame.transform.scale(self.virtual_screen, self.dimensions)
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        self.clock.tick(self.fps)

    def get_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            elif event.type == pygame.VIDEORESIZE:
                # self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.dimensions = (event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Exit on ESC key press
                    exit(0)
                elif event.key == pygame.K_o:
                    self.fps = 60 - self.fps
                elif event.key == pygame.K_p:
                    if not self.must_update:
                        self.must_update = True
                        for car in self.cars:
                            car.start_drawing()
                    else:
                        self.must_update = False
                        for car in self.cars:
                            car.stop_drawing()
        # User Car
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.user_car.update_position(4)
        elif keys[pygame.K_a]:
            self.user_car.update_position(1)
        elif keys[pygame.K_d]:
            self.user_car.update_position(2)
        elif keys[pygame.K_s]:
            self.user_car.update_position(3)

    def pixel_out_of_bounds(self, v):
        BORDER_COLOR = (255, 255, 255)

        # Check if x and y are within the bounds of the map
        if v[0] < 0 or v[0] >= 1920 or v[1] < 0 or v[1] >= 1080:
            return True
        if self.map.get_at((int(v[0]), int(v[1]))) == BORDER_COLOR:
            return True

        return False

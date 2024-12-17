import pygame


class Car:

    def __init__(self, sprite, size, position):
        self.sprite = sprite
        self.position = position
        self.set_size(size)

        self.speed = 0
        self.distance = 0
        self.time = 0
        self.alive = True
    
    def set_size(self, size):
        self.size = size
        self.sprite_resized = pygame.transform.scale(self.sprite, (size[0], size[1]))
        pass

    def set_position(self, position):
        self.position = position

    def is_alive(self):
        return self.alive

    def draw(self, screen):
        screen.blit(self.sprite_resized, self.position)

    def check_collision(self, map):
        pass

    def update(self):
        pass

    def update_position(self, choice):
        match (choice) :
            case 0:
                pass
        pass

    def get_data(self):
        pass

    def get_reward(self):
        return 0

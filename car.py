

class Car:

    def __init__(self, sprite, size, position):
        self.sprite = sprite
        self.position = position
        self.size = size

        self.speed = 0
        self.distance = 0
        self.time = 0
        self.alive = True

    def is_alive(self):
        return self.alive

    def draw(self):
        pass

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

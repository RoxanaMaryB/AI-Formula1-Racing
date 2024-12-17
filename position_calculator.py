from game import *
from car import *


def main():
    dimensions = [1920, 1080]
    game = Game(dimensions, "maps/map1.png", "maps/car.png")
    game.loop()

if __name__ == "__main__":
    main()

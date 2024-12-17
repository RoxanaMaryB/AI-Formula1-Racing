from game import *
from car import *

map_file = "maps/map1.png"
car_file = "maps/car.png"
log_file = "car_position.txt"

def loop(game):
    car_size = [100, 50]
    car_position = [1220, 820]
    car = Car(game.car_sprite, car_size, car_position)
    game.add_car(car)
    with open(log_file, "w") as file:
        file.write(f"map: {map_file}\n")

    while True:
        game.update_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        pygame.quit()

                    case pygame.K_z:
                        car_size = [size * 0.8 for size in car_size]
                        car.set_size(car_size)
                    case pygame.K_x:
                        car_size = [size * 1.25 for size in car_size]
                        car.set_size(car_size)

                    case pygame.K_a:
                        car_position[0] -= car_size[0] / 4
                        car.set_position(car_position)
                    case pygame.K_d:
                        car_position[0] += car_size[0] / 4
                        car.set_position(car_position)
                    case pygame.K_w:
                        car_position[1] -= car_size[1] / 4
                        car.set_position(car_position)
                    case pygame.K_s:
                        car_position[1] += car_size[1] / 4
                        car.set_position(car_position)
                    case pygame.K_l:
                        with open("car_position.txt", "a") as file:
                            file.write(f"size: {car_size}, position: {car_position}\n")

def main():
    dimensions = [1920, 1080]
    game = Game(dimensions, map_file, car_file)
    loop(game)

if __name__ == "__main__":
    main()

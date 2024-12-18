from game import *
from car import *

map_file = "maps/map1.png"
car_file = "maps/car.png"
log_file = "car_position.txt"

def loop(game):
    car_size = [100, 50]
    car_position = [1220, 820]
    car = Car(game.car_sprite, car_size, car_position)
    car.start_drawing()
    game.add_car(car)
    with open(log_file, "w") as file:
        file.write(f"map: {map_file}\n")

    while True:
        game.update_screen()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            car_position[0] -= car_size[0] / 200
            car.set_position(car_position)
        if keys[pygame.K_d]:
            car_position[0] += car_size[0] / 200
            car.set_position(car_position)
        if keys[pygame.K_w]:
            car_position[1] -= car_size[1] / 200
            car.set_position(car_position)
        if keys[pygame.K_s]:
            car_position[1] += car_size[1] / 200
            car.set_position(car_position)

        if keys[pygame.K_z]:
            car_size = [size / 1.01 for size in car_size]
            car.set_size(car_size)
        if keys[pygame.K_x]:
            car_size = [size * 1.01 for size in car_size]
            car.set_size(car_size)

        if keys[pygame.K_q]:
            car.set_angle(car.angle + 0.5)
        if keys[pygame.K_e]:
            car.set_angle(car.angle - 0.5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        pygame.quit()
                    case pygame.K_l:
                        with open("car_position.txt", "a") as file:
                            file.write(f"size: {car_size}, position: {car_position}\n")

def main():
    dimensions = [1920, 1080]
    game = Game(dimensions, map_file, car_file)
    loop(game)

if __name__ == "__main__":
    main()

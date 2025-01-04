from model.game import *
from model.ai_car import *
# from usercar import *

map_file = "maps/map2/map.png"
car_file = "cars/red_car.png"
log_file = "position_calculator/car_position.txt"

def loop(game):
    car_size = [100, 50]
    car_position = [1220, 820]
    car = AICar(game, must_draw=True, size=car_size, start_position=car_position)
    car.start_drawing()
    game.add_car(car)
    with open(log_file, "w") as file:
        file.write(f"map: {map_file}\n")

    while True:
        game.update()
        # car.update_position_from_keyboard()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.VIDEORESIZE:
                game.update_dimensions([event.w, event.h]) 
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        pygame.quit()
                    case pygame.K_l:
                        with open("car_position.txt", "a") as file:
                            file.write(f"size: {car_size}, position: {car_position}\n")


def main():
    dimensions = [900, 500]
    game = Game(dimensions, map_file, car_file)
    loop(game)

if __name__ == "__main__":
    main()

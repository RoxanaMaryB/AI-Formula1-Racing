from model.ai_car import *
from model.game import *
from car import *
import pickle
import neat
import pygame

map_name  = "finish_line"

directory = "maps/" + map_name + "/"
map_file      = directory + "map.png"
best_car_file = directory + 'best_car_100.pkl'

ai_car_file   = "cars/blue_car.png"
user_car_file = "cars/red_car.png"

def load_best_car(file_name):
    try:
        with open(file_name, "rb") as f:
            best_car , config= pickle.load(f)
            return best_car, config
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        return None, None


def init_game():
    global game
    game = Game([1000, 500], map_file, ai_car_file)
    user_car_sprite = pygame.image.load(user_car_file).convert()
    user_car = Car(game, True, user_car_sprite, size = [100, 50], start_position = [1220, 820])
    game.add_user_car(user_car)

def main():
    dimensions = [900, 500]
    screen = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
    game = Game(dimensions, map_file, ai_car_file)
    font = pygame.font.SysFont(None, 55)
    best_car, config = load_best_car(best_car_file)
    if best_car is not None:
        print(f"Loaded best car from {best_car_file}")
    else:
        print(f"Failed to load best car from {best_car_file}")
    net = neat.nn.FeedForwardNetwork.create(best_car, config)
    # initial_position = ([1220, 820], [100, 50])
    player_car = Car(ai_car_file)
    ai_car = AICar(game, must_draw=True, sprite=pygame.image.load(ai_car_file))
    game.add_ai_car(ai_car)

   
    if game.pixel_out_of_bounds(player_car.position):
        print("Player car out of bounds")
        winner = "AI Car Wins!"
        running = False
    elif game.pixel_out_of_bounds(ai_car.position):
        print("AI car out of bounds")
        winner = "User Car Wins!"
        running = False

    screen.fill((0, 0, 0))
    game.update()
    pygame.display.update()

    pygame.time.delay(16)

    if winner:
        screen.fill((0, 0, 0))
        text = font.render(winner, True, (255, 255, 255))
        screen.blit(text, (dimensions[0] // 2 - text.get_width() // 2, dimensions[1] // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(3000)

    pygame.quit()

if __name__ == "__main__":
    main()

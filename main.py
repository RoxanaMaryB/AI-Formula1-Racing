from model.ai_car import *
from model.game import *
from car import *
import pickle
import neat
import pygame

map_name  = "finish_line3"

directory = "maps/" + map_name + "/"
map_file      = directory + "map.png"
best_car_file = directory + 'best_car_100.pkl'

ai_car_file   = "cars/blue_car.png"
user_car_file = "cars/red_car.png"

def load_best_car(file_name):
    try:
        with open(file_name, "rb") as f:
            best_car = pickle.load(f)
            return best_car
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        return None

def init_game():
    global game
    game = Game([1000, 500], map_file, user_car_file)
    user_car_sprite = pygame.image.load(user_car_file).convert()
    user_car = Car(game, True, user_car_sprite, size=[100, 50], start_position=[1220, 820])
    game.add_user_car(user_car)

def run_simulation(best_car, config):
    net = neat.nn.FeedForwardNetwork.create(best_car, config)
    ai_car = AICar(game, must_draw=True, sprite=pygame.image.load("cars/blue_car.png").convert())
    ai_car.set_net(net)
    game.add_car(ai_car)

    running = True
    while running:
        game.update()
        if game.user_car.has_won():
            print("User car has crossed the finish line")
            winner = "User Car Wins!"
            running = False
        elif ai_car.has_won():
            print("AI car has crossed the finish line")
            winner = "AI Car Wins!"
            running = False
        elif not game.user_car.is_alive():
            print("User car is out of bounds")
            winner = "AI Car Wins!"
            running = False
        elif not ai_car.is_alive():
            print("AI car is out of bounds")
            winner = "User Car Wins!"
            running = False
        


    pygame.display.update()
    pygame.time.delay(16)
    dimensions = [1000, 500]
    font = pygame.font.SysFont(None, 55)
    screen = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
    if winner:
        screen.fill((0, 0, 0))
        text = font.render(winner, True, (255, 255, 255))
        screen.blit(text, (dimensions[0] // 2 - text.get_width() // 2, dimensions[1] // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.wait(3000)

    pygame.quit()
            
      

def main():
    config_path = "model/config.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    best_car = load_best_car(best_car_file)
    if best_car is None:
        return
    
    init_game()
    run_simulation(best_car, config)

if __name__ == "__main__":
    main()

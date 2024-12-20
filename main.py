from model.game import *
from usercar import *
from position_calculator import *
import pickle
import neat
import pygame

# clasa Car

def main():
    dimensions = [900, 500]
    game = Game(dimensions, map_file, car_file)
    with open('most_sukar_genome.pfkl', "rb") as f:
        best_genome, config = pickle.load(f)
    net = neat.nn.FeedForwardNetwork.create(best_genome, config)
    initial_position = ([1220, 820], [100, 50])
    player_car = UserCar(initial_position)
    ai_car = AICar(initial_position, net)

    running = True
    while running:
        player_input = {"steering": 0, "acceleration": 0}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_input["steering"] = -1
                elif event.key == pygame.K_RIGHT:
                    player_input["steering"] = 1
                elif event.key == pygame.K_UP:
                    player_input["acceleration"] = 1
                elif event.key == pygame.K_DOWN:
                    player_input["acceleration"] = -1

    ai_inputs = ai_car.get_data()
    player_car.update(player_input)
    ai_car.update(net.activate(ai_inputs))

    game.update_screen()
    player_car.draw()
    ai_car.draw()
    pygame.display.update()

    pygame.time.delay(16)
    loop(game)
    

if __name__ == "__main__":
    main()
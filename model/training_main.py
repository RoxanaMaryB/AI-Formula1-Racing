import neat
import pickle
from model.ai_car import *
from model.game import *

map_name  = "map3"

# Keyboard inputs:
# ESC - stop the population
# O - speedup on/off
# P - display on/off>   (use this for fast generating)

directory = "maps/" + map_name + "/"
map_file      = directory + "map.png"

ai_car_file   = "cars/blue_car.png"
user_car_file = "cars/red_car.png"

game = None

def init_game():
    global game
    game = Game([1000, 500], map_file, ai_car_file)
    return
    user_car_sprite = pygame.image.load(user_car_file).convert()
    user_car = Car(game, True, user_car_sprite, size = [100, 50], start_position = [1220, 820])
    game.add_user_car(user_car)


def init_simulation(genomes, config):
    global game
    game.cars.clear()

    # For All Genomes Passed Create A New Neural Network
    i = 0
    for _, g in genomes:
        car = AICar(game, game.must_update_depending_on_idx(i), game.car_sprite)
        net = neat.nn.FeedForwardNetwork.create(g, config)
        car.set_net(net)
        game.add_car(car)
        i += 1

global best_car

def run_simulation(genomes, config):
    init_simulation(genomes, config)

    for _ in range (0, 2000):
        if game.update() == False:
            break

    # Keep only best N cars for display
    N = 3
    vals = []
    for i, car in enumerate(game.cars):
        reward = car.get_reward()
        genomes[i][1].fitness = reward
        vals.append((i, reward))

    vals.sort(key=lambda x: x[1], reverse=True)
    vals = [val[0] for val in vals]

    global best_car
    best_car = game.cars[vals[0]].net
    game.set_display_idx(vals[:3])


def new_population():
    config_path = "model/config.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    return population


def init_population():
    LOAD_FROM_FILE = True
    load_population_file = directory + "population.pkl"

    if LOAD_FROM_FILE:
        try:
            with open(load_population_file, "rb") as f:
                population = pickle.load(f)
        except FileNotFoundError:
            print(f"{load_population_file} not found. Creating new population.")
            population = new_population()
    else:
        population = new_population()
    return population


def save_best_car(best_car, generation = -1):
    if generation == -1:
        file = directory + "best_car.pkl"
    else:
        file = directory + "best_car_" + str(generation) + ".pkl"        
    with open(file, 'wb') as f:
        pickle.dump(best_car, f)


def save_population(population):
    SAVE_TO_FILE = True
    save_population_file = directory + "population.pkl"

    if SAVE_TO_FILE:
        with open(save_population_file, 'wb') as f:
            pickle.dump(population, f)

def main():
    population = init_population()
    init_game()

    # Run Simulation For A Maximum of 500 Generations
    try:
        for _ in range(500):
            best_car = population.run(run_simulation, 1)
            g = population.generation
            if g > 0 and g % 50 == 0:
                save_best_car(best_car, g)
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
    except SystemExit:
       print("Simulation stopped by user.")
       save_population(population)
    finally:
        save_population(population)


if __name__ == "__main__":
    main()


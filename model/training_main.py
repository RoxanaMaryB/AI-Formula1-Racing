import neat
import pickle
from ai_car import *
from game import *

map_file = "maps/finish_line.png"
car_file = "maps/blue_car.png"
user_car_file = "maps/car.png"
log_file = "car_position.txt"
map_name = map_file.split("/")[-1].split(".")[0]
save_file = "saved/" + map_name + ".pkl"
dimensions = [1000, 500]

game = None

# Keyboard inputs:                   O - speedup on/off
# (use this for fast generating) ->  P - display on/off

def init_game():
    global game
    game = Game(dimensions, map_file, car_file)
    # return
    user_car_sprite = pygame.image.load(user_car_file).convert()
    car = AICar(game, True, user_car_sprite, [100, 50], [1220, 820])
    game.add_user_car(car)

def run_simulation(genomes, config):

    global game
    game.cars.clear()

    # Empty Collections For Nets and Cars
    nets = []

    # For All Genomes Passed Create A New Neural Network
    i = 0
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        car = AICar(game, game.must_update_depending_on_idx(i), game.car_sprite, [100, 50], [1220, 820])
        game.add_car(car)
        i += 1

    for _ in range (0, 2000):

        # For Each Car Get The Acton It Takes
        still_alive = 0
        for i, car in enumerate(game.cars):
            if car.is_alive():
                output = nets[i].activate(car.get_data())
                choice = output.index(max(output))
                car.update_position(choice + 1)
                car.update()
                still_alive += 1
            else:
                car.stop_drawing()

        if still_alive == 0:
            break

        game.update()

    if game.user_car is not None:
        game.user_car.reset()
    vals = []
    for i, car in enumerate(game.cars):
        reward = car.get_reward()
        genomes[i][1].fitness = reward
        vals.append((i, reward))

    vals.sort(key=lambda x: x[1], reverse=True)
    game.set_display_idx([val[0] for val in vals[:5]])

def main():
    config_path = "model/config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                    neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation,
                                    config_path)

    LOAD_FROM_PICKLE = True
    if LOAD_FROM_PICKLE:
        try:
            with open(save_file, "rb") as f:
                population = pickle.load(f)
        except FileNotFoundError:
            print(f"{save_file} not found. Creating new population.")
            population = neat.Population(config)
            population.add_reporter(neat.StdOutReporter(True))
            stats = neat.StatisticsReporter()
            population.add_reporter(stats)

    else:
        # Create Population And Add Reporters
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)

       
    init_game()
    try:
        # Run Simulation For A Maximum of 250 Generations
        population.run(run_simulation, 250)
    except KeyboardInterrupt:
        print("Simulation interrupted by user.")
    except SystemExit:
       with open(save_file, 'wb') as f:
            pickle.dump(population, f)
    finally:
        with open(save_file, 'wb') as f:
            pickle.dump(population, f)


if __name__ == "__main__":
    main()
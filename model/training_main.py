import neat
from ai_car import *
from game import *

map_file = "maps/map2.png"
car_file = "maps/blue_car.png"
user_car_file = "maps/car.png"
log_file = "car_position.txt"
dimensions = [1000, 500]

game = Game(dimensions, map_file, car_file)

# Keyboard inputs:                   O - speedup on/off
# (use this for fast generating) ->  P - display on/off

def init_game():
    global game
    user_car_sprite = pygame.image.load(user_car_file).convert()
    car = AICar(game, True, user_car_sprite, [100, 50], [1220, 820])
    car.start_drawing()
    game.add_user_car(car)

    


def run_simulation(genomes, config):

    global game
    game.cars.clear()

    # Empty Collections For Nets and Cars
    nets = []

    # For All Genomes Passed Create A New Neural Network
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        game.add_car(AICar(game, game.must_update, game.car_sprite, [100, 50], [1220, 820]))

    for _ in range (0, 2000):

        # For Each Car Get The Acton It Takes
        still_alive = 0
        for i, car in enumerate(game.cars):
            if car.is_alive():
                output = nets[i].activate(car.get_data())
                choice = output.index(max(output))
                car.update_position(choice)
                still_alive += 1
            else:
                car.stop_drawing()

        if still_alive == 0:
            break

        game.update()


    for i, car in enumerate(game.cars):
        genomes[i][1].fitness = car.get_reward()
        if car.is_alive():
            pass


def main():
    # Load Config
    config_path = "model/config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    init_game()
    # Run Simulation For A Maximum of 250 Generations
    population.run(run_simulation, 1000)

if __name__ == "__main__":
    main()

import sys
import neat
from ai_car import *
from game import *

map_file = "maps/map2.png"
car_file = "maps/car.png"
log_file = "car_position.txt"
dimensions = [1000, 500]
current_generation = 0

def run_simulation(genomes, config):
    
    # Empty Collections For Nets and Cars
    nets = []

    game = Game(dimensions, map_file, car_file)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        game.add_car(AICar(game, True, game.car_sprite, [100, 50], position=[1220, 820]))

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    for _ in range (0, 50 * 100):

        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(game.cars):
            if car.is_alive():
                output = nets[i].activate(car.get_data())
                choice = output.index(max(output))
                car.update_position(choice)
            else:
                car.stop_drawing()

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(game.cars):
            if car.is_alive():
                still_alive += 1
                # genomes[i][1].fitness += car.get_reward()
        if still_alive == 0:
            break

        game.update_screen()

    for i, car in enumerate(game.cars):
        genomes[i][1].fitness += car.get_reward()


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

    # Run Simulation For A Maximum of 250 Generations
    population.run(run_simulation, 1000)

if __name__ == "__main__":
    main()
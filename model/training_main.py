import neat
from ai_car import *
import sys
import neat
from game import *

map_file = "maps/map.png"
car_file = "maps/car.png"
log_file = "car_position.txt"
dimensions = [1000, 500]
current_generation = 0

def run_simulation(genomes, config):
    
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    game = Game(dimensions, map_file, car_file)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        game.add_car(AICar(game, True, game.car_sprite, [100, 50], [1201, 925]))

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(game.cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            
        
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(game.cars):
            if car.is_alive():
                still_alive += 1
                car.update_position(choice)
                car.update()
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds
            break

        # Update Screen
        game.update_screen()

        # pygame.display.flip()
        game.clock.tick(60) # 60 FPS



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
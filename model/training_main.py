import sys
import neat
from ai_car import *
from game import *

map_file = "maps/map2.png"
car_file = "maps/car.png"
log_file = "car_position.txt"
dimensions = [1000, 500]

game = Game(dimensions, map_file, car_file)
    
display = True
def get_game_events():
    global display
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Exit on ESC key press
                sys.exit(0)
            if event.key == pygame.K_o:
                display = False
            if event.key == pygame.K_p:
                display = True

def run_simulation(genomes, config):

    global game, display
    game.cars.clear()

    # Empty Collections For Nets and Cars
    nets = []
    
    # For All Genomes Passed Create A New Neural Network
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        game.add_car(AICar(game, True, game.car_sprite, [100, 50], position=[1220, 820]))

    for _ in range (0, 50 * 100):
        get_game_events()

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
        
        if display:
            game.update_screen()


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

    # Run Simulation For A Maximum of 250 Generations
    population.run(run_simulation, 1000)

if __name__ == "__main__":
    main()

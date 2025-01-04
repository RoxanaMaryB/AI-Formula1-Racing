from model.ai_car import *
from usercar import *
import pickle
import neat
import pygame

# clasa Car

def main():
    dimensions = [900, 500]
    map_file = "maps/finish_line.png"
    car_file = "maps/blue_car.png"
    screen = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
    game = Game(dimensions, map_file, car_file)
    font = pygame.font.SysFont(None, 55)
    with open('winner.pkl', "rb") as f:
        best_genome, config = pickle.load(f)
    net = neat.nn.FeedForwardNetwork.create(best_genome, config)
    # initial_position = ([1220, 820], [100, 50])
    player_car = UserCar(car_file)
    ai_car = AICar(game, must_draw=True, sprite=pygame.image.load(car_file))

    game.add_user_car(player_car)
    game.add_ai_car(ai_car)

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
        actions = net.activate(ai_inputs)
        choice = actions.index(max(actions))

        player_car.update(player_input)
        ai_car.update_position(choice)

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

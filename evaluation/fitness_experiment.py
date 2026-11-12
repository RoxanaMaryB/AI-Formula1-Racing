"""
Trains NEAT cars with a chosen fitness function, reusing the original training
code unchanged, so fitness functions can be compared under identical settings.

  distance  the original fitness function in model/ai_car.py: distance
            driven, tripled if the car is still driving when time runs
            out. Reaching the finish ends the run early, so it scores less
            than driving slowly.
  finish    distance driven, plus a bonus for reaching the finish line that
            grows the sooner the car gets there.

Commands:
    python3 -m evaluation.fitness_experiment --fitness distance --seed x
    python3 -m evaluation.fitness_experiment --fitness finish --seed x

Each run saves its best car every 50 generations to
evaluation/runs/<map>/<fitness>_seed<seed>/best_car_<generation>.pkl.
The same fitness, seed and settings give the same training run.

--steps sets how many steps each generation is simulated for (2000 in the
original training). A lap of finish_line3 takes about 2500 steps at the
minimum speed, so with 2000 steps only cars that have learned to speed up can
reach the finish line in training. Runs with another value are saved as
<fitness>_steps<steps>_seed<seed>.
"""
import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import argparse
import pickle
import random
import time

import model.training_main as training
from model.ai_car import AICar

TRAINING_STEPS = 2000        # steps per generation in model/training_main.py
FINISH_BONUS = 1000          # one lap's worth of distance reward
MIN_FINISH_DISTANCE = 30000  # the shortest real lap is ~40000, so turning around
                             # to the finish line behind the start doesn't count


class ExperimentCar(AICar):
    fitness_function = "distance"
    time_limit = TRAINING_STEPS

    def update(self):
        super().update()
        self.time += 1  # steps driven; stops counting once the car crashes or finishes

    def reached_finish(self):
        return self.won and self.distance >= MIN_FINISH_DISTANCE

    def get_reward(self):
        if self.fitness_function == "distance":
            return super().get_reward()  # the original formula

        reward = self.distance / 50
        if self.reached_finish():
            reward += FINISH_BONUS + (self.time_limit - self.time) / 2
        return reward


def run_simulation(genomes, config):
    """Same as run_simulation in model/training_main.py, with a configurable
    number of steps and a count of the cars that reached the finish line."""
    training.init_simulation(genomes, config)
    game = training.game

    for _ in range(ExperimentCar.time_limit):
        if game.update() == False:
            break

    vals = []
    for i, car in enumerate(game.cars):
        reward = car.get_reward()
        genomes[i][1].fitness = reward
        vals.append((i, reward))
    vals.sort(key=lambda x: x[1], reverse=True)
    game.set_display_idx([val[0] for val in vals[:3]])

    finished = sum(car.reached_finish() for car in game.cars)
    print(f"Cars that reached the finish line: {finished}/{len(game.cars)}", flush=True)


def main():
    # Claude Opus 5.5 Generated:
    parser = argparse.ArgumentParser(description="Train NEAT cars with a chosen fitness function.")
    parser.add_argument("--fitness", choices=["distance", "finish"], required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--map", default="finish_line3")
    parser.add_argument("--generations", type=int, default=150)
    parser.add_argument("--steps", type=int, default=TRAINING_STEPS, help="steps simulated per generation")
    parser.add_argument("--save-every", type=int, default=50)
    args = parser.parse_args()

    # Point the original training code at this map and at the experiment's car.
    ExperimentCar.fitness_function = args.fitness
    ExperimentCar.time_limit = args.steps
    training.AICar = ExperimentCar
    training.directory = "maps/" + args.map + "/"
    training.map_file = training.directory + "map.png"

    run_name = args.fitness if args.steps == TRAINING_STEPS else f"{args.fitness}_steps{args.steps}"
    out_dir = f"evaluation/runs/{args.map}/{run_name}_seed{args.seed}"
    if os.path.exists(out_dir) and os.listdir(out_dir):
        sys.exit(f"{out_dir} already has results; delete it to train this run again.")
    os.makedirs(out_dir, exist_ok=True)

    random.seed(args.seed)  # NEAT draws all its randomness from this
    population = training.new_population()
    training.init_game()
    training.game.must_update = False  # no drawing and no frame limit

    start = time.time()
    while population.generation < args.generations:
        best = population.run(run_simulation, 1)
        generation = population.generation
        if generation % args.save_every == 0:
            with open(f"{out_dir}/best_car_{generation}.pkl", "wb") as f:
                pickle.dump(best, f)
            print(f"Saved {out_dir}/best_car_{generation}.pkl "
                  f"({(time.time() - start) / 60:.1f} min so far)", flush=True)


if __name__ == "__main__":
    main()

"""
Headless evaluation of the trained NEAT cars.

Measures how often a saved model completes a track, meaning it reaches the
green finish line without crashing.

The simulation is deterministic: the car always starts at the same pose, the
network has no randomness and the radars read fixed map pixels. Running the
same model on the same map twice gives exactly the same result. To get a
meaningful completion rate, each run therefore perturbs:
  * the start position (uniform, +/- POS_JITTER pixels in x and y),
  * the start heading (uniform, +/- ANGLE_JITTER degrees),
  * every radar reading (multiplicative Gaussian noise, SENSOR_NOISE std).

main.py has no time limit, so runs get twice the 2000 steps used per
generation in training. A run still driving after that counts as "out of time"
and is reported separately from crashes.

Models from evaluation/fitness_experiment.py live in their own folders:
    python3 -m evaluation.evaluate --model-dir evaluation/runs/finish_line3/* --model best_car_150.pkl
"""
import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import argparse
import csv
import glob
import math
import pickle
import re

import neat
import numpy as np

# Same import order as main.py
from model.ai_car import *
from model.game import *
from car import *

CONFIG_PATH = "model/config.txt"
AI_CAR_FILE = "cars/blue_car.png"
START_POSITION = [1200, 820]  # AICar default, also used by main.py
FINISH_COLOR = (34, 177, 76)  # Car.check_green_color
TRAINING_STEPS = 2000         # steps per generation in model/training_main.py
MAX_STEPS = 2 * TRAINING_STEPS


class EvalCar(AICar):
    """AICar with a chosen start pose and optional radar noise."""

    def __init__(self, game, start_position, start_angle, sensor_noise, rng):
        self.sensor_noise = sensor_noise
        self.rng = rng
        super().__init__(game, False, game.car_sprite, start_position=start_position)
        # Car.reset() leaves the radar origin at (0, 0) until the first move, so
        # the first decision in the game and in training is made from those
        # readings. Only the heading is changed here, to keep that behaviour.
        self.set_angle(start_angle)
        self.steps = 0
        self.finish_step = None
        self.path = [tuple(self.center)]

    def get_data(self):
        # Same as AICar.get_data, with noise applied before quantization.
        self.radars.clear()
        for d in range(-120, 120 + 1, 30):
            self.check_radar(d)

        values = [0] * 9
        for i, radar in enumerate(self.radars):
            dist = radar[1]
            if self.sensor_noise > 0:
                dist = max(0.0, dist * (1 + self.rng.normal(0, self.sensor_noise)))
            values[i] = int(dist / 30)
        return values

    def update(self):
        super().update()
        self.steps += 1
        self.path.append(tuple(self.center))
        if self.won and self.finish_step is None:
            self.finish_step = self.steps

    def path_length(self):
        # Car.update moves speed * size[0] / 1000 pixels per step.
        return self.distance * self.size[0] / 1000


def corners_at(position, angle, size=(100, 50)):
    """Corner points the car would have at this pose (as in Car.update)."""
    direction = cis(angle)
    center = np.array(position) + np.array(size) / 2
    length = 0.5 * size[0]
    return [center + cis(angle + d) * length for d in (30, 150, 210, 330)], center + direction * size[0] / 2


def valid_start(game, position, angle):
    """The car must start fully on the track and not on the finish line."""
    corners, sensors = corners_at(position, angle)
    for point in corners + [sensors]:
        if game.pixel_out_of_bounds(point):
            return False
        if tuple(game.map.get_at((int(point[0]), int(point[1]))))[:3] == FINISH_COLOR:
            return False
    return True


def sample_start(game, rng, pos_jitter, angle_jitter):
    for _ in range(1000):
        dx, dy = rng.uniform(-pos_jitter, pos_jitter, size=2)
        position = [START_POSITION[0] + dx, START_POSITION[1] + dy]
        angle = rng.uniform(-angle_jitter, angle_jitter)
        if valid_start(game, position, angle):
            return position, angle
    raise RuntimeError("Could not find a valid start pose; lower the jitter.")


def wilson_interval(successes, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def run_cars(game, net, cars, max_steps):
    game.cars.clear()
    for car in cars:
        car.set_net(net)
        game.add_car(car)
    for _ in range(max_steps):
        if not game.update():
            break


def summarize(cars):
    finished = [c for c in cars if c.won]
    crashed = [c for c in cars if not c.won and not c.alive]
    timed_out = [c for c in cars if c.alive]
    return finished, crashed, timed_out


def has_finish_line(map_file):
    surface = pygame.image.load(map_file)
    pixels = pygame.surfarray.array3d(surface)
    return bool(np.all(pixels == FINISH_COLOR, axis=-1).any())


def draw_cross(surface, color, point, size=10, width=4):
    x, y = point
    pygame.draw.line(surface, color, (x - size, y - size), (x + size, y + size), width)
    pygame.draw.line(surface, color, (x - size, y + size), (x + size, y - size), width)


def draw_trajectories(game, cars, out_file, title, note):
    """Save the map with every run's path:
        finished in blue
        failed in orange
        with a cross where the run ended."""
    FINISHED = (57, 135, 229)  # blue
    FAILED = (217, 89, 38)     # orange
    INK = (11, 11, 11)

    track = game.map.copy()
    overlay = pygame.Surface(track.get_size(), pygame.SRCALPHA)
    for car in sorted(cars, key=lambda c: c.won, reverse=True):  # failures on top
        if len(car.path) > 1:
            color = FINISHED + (160,) if car.won else FAILED + (230,)
            pygame.draw.lines(overlay, color, False, car.path, 3)
        if not car.won:
            draw_cross(overlay, FAILED + (255,), car.path[-1])
    track.blit(overlay, (0, 0))

    HEADER = 130
    width, height = track.get_size()
    image = pygame.Surface((width, height + HEADER))
    image.fill((255, 255, 255))
    image.blit(track, (0, HEADER))

    finished = sum(c.won for c in cars)
    font = pygame.font.SysFont(None, 46)
    small = pygame.font.SysFont(None, 34)
    image.blit(font.render(title, True, INK), (24, 16))
    pygame.draw.line(image, FINISHED, (26, 78), (76, 78), 5)
    image.blit(small.render(f"finished ({finished})", True, INK), (88, 66))
    pygame.draw.line(image, FAILED, (420, 78), (470, 78), 5)
    draw_cross(image, FAILED, (445, 78))
    image.blit(small.render(f"crashed or out of time ({len(cars) - finished})", True, INK), (482, 66))
    image.blit(small.render(note, True, (82, 81, 78)), (26, 98))
    pygame.image.save(image, out_file)


def evaluate(map_name, model_path, label, config, args):
    directory = "maps/" + map_name + "/"
    game = Game([192, 108], directory + "map.png", AI_CAR_FILE)
    game.must_update = False

    with open(model_path, "rb") as f:
        genome = pickle.load(f)
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Baseline
    baseline = EvalCar(game, START_POSITION, 0, 0, None)
    run_cars(game, net, [baseline], args.max_steps)

    # Perturbed runs. Each run has its own random stream, so results don't
    # depend on how many runs are simulated at once.
    rngs = [np.random.default_rng([args.seed, i]) for i in range(args.runs)]
    cars = []
    for rng in rngs:
        position, angle = sample_start(game, rng, args.pos_jitter, args.angle_jitter)
        cars.append(EvalCar(game, position, angle, args.sensor_noise, rng))
    run_cars(game, net, cars, args.max_steps)

    finished, crashed, timed_out = summarize(cars)
    low, high = wilson_interval(len(finished), len(cars))
    steps = [c.finish_step for c in finished]
    lengths = [c.path_length() for c in finished]

    if args.plot:
        os.makedirs(args.out_dir, exist_ok=True)
        rate = 100 * len(finished) / len(cars)
        draw_trajectories(game, cars, f"{args.out_dir}/{map_name}_{label.replace('/', '_')}.png",
                          f"{map_name} / {label}: {len(finished)}/{len(cars)} runs finished ({rate:.0f}%)",
                          settings_text(args))

    return {
        "map": map_name,
        "model": label,
        "train_fitness": round(genome.fitness) if genome.fitness is not None else "",
        "baseline": "finished" if baseline.won else ("crashed" if not baseline.alive else "timeout"),
        "baseline_steps": baseline.finish_step if baseline.won else "",
        "runs": len(cars),
        "finished": len(finished),
        "crashed": len(crashed),
        "timeout": len(timed_out),
        "completion_rate": len(finished) / len(cars),
        "ci_low": low,
        "ci_high": high,
        "median_steps": float(np.median(steps)) if steps else "",
        "min_path_px": round(min(lengths)) if lengths else "",
    }


def settings_text(args):
    return (f"{args.runs} runs, seed {args.seed}: start position +/-{args.pos_jitter:g} px, "
            f"heading +/-{args.angle_jitter:g} deg, radar noise {100 * args.sensor_noise:g}%, "
            f"budget {args.max_steps} steps")


def model_sort_key(name):
    digits = "".join(ch for ch in os.path.basename(name) if ch.isdigit())
    return int(digits) if digits else -1


def find_models(args):
    """(map, model path, label) for every model to evaluate."""
    models = []
    if args.model_dir:
        # Experiment runs: evaluation/runs/<map>/<run name>/best_car_<generation>.pkl
        for run_dir in args.model_dir:
            run_dir = run_dir.rstrip("/")
            map_name = args.map or os.path.basename(os.path.dirname(run_dir))
            pattern = args.model or "best_car_*.pkl"
            for path in sorted(glob.glob(f"{run_dir}/{pattern}"), key=model_sort_key):
                label = os.path.basename(run_dir) + "/" + os.path.basename(path).replace(".pkl", "")
                models.append((map_name, path, label))
        return models

    if args.map:
        maps = [args.map]
    else:
        maps = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob("maps/*/map.png")
                      if has_finish_line(p))
    for map_name in maps:
        pattern = args.model or "best_car_*.pkl"
        for path in sorted(glob.glob(f"maps/{map_name}/{pattern}"), key=model_sort_key):
            models.append((map_name, path, os.path.basename(path).replace(".pkl", "")))
    return models


def pooled_groups(rows):
    """Group runs of the same experiment over its training seeds, e.g.
    finish_seed0/best_car_150 + finish_seed1/best_car_150 -> finish/best_car_150.

    The training seed is the unit to compare: the 100 runs of one model share
    the same network, so they are not independent samples of the experiment.
    Each seed is listed separately instead of pooling its runs."""
    groups = {}
    for r in rows:
        name = re.sub(r"_seed\d+/", "/", r["model"])
        if name != r["model"]:
            groups.setdefault((r["map"], name), []).append(r)
    pooled = []
    for (map_name, name), members in sorted(groups.items()):
        members = sorted(members, key=lambda r: int(re.search(r"_seed(\d+)/", r["model"]).group(1)))
        rates = [100 * r["finished"] / r["runs"] for r in members]
        pooled.append({"map": map_name, "model": name, "seeds": len(members),
                       "rates": rates, "mean_rate": float(np.mean(rates)),
                       "medians": [r["median_steps"] for r in members]})
    return pooled


def write_results(rows, pooled, args):
    os.makedirs(args.out_dir, exist_ok=True)
    csv_file = f"{args.out_dir}/{args.name}.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # README-ready tables.
    md_file = f"{args.out_dir}/{args.name}.md"
    baseline_names = {"finished": "finished", "crashed": "crashed", "timeout": "out of time"}
    with open(md_file, "w") as f:
        f.write("| Track | Model | Unperturbed run | Runs completed | 95% CI | Crashed | Out of time "
                "| Median steps to finish |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            steps = f"{r['median_steps']:.0f}" if r["median_steps"] != "" else "–"
            f.write(f"| {r['map']} | {r['model']} | {baseline_names[r['baseline']]} "
                    f"| **{r['finished']}/{r['runs']}** | {100 * r['ci_low']:.0f}–{100 * r['ci_high']:.0f}% "
                    f"| {r['crashed']} | {r['timeout']} | {steps} |\n")
        if pooled:
            f.write("\nBy training seed:\n\n")
            f.write("| Track | Experiment | Seeds | Completion per seed | Mean completion "
                    "| Median steps to finish per seed |\n")
            f.write("|---|---|---|---|---|---|\n")
            for p in pooled:
                rates = ", ".join(f"{rate:.0f}%" for rate in p["rates"])
                medians = ", ".join(f"{m:.0f}" if m != "" else "–" for m in p["medians"])
                f.write(f"| {p['map']} | {p['model']} | {p['seeds']} | {rates} | **{p['mean_rate']:.0f}%** "
                        f"| {medians} |\n")
        f.write(f"\n_{settings_text(args)}._\n")
    return csv_file, md_file


def main():
    # Claude Opus 5.5 Generated:
    parser = argparse.ArgumentParser(description="Measure track completion of trained cars.")
    parser.add_argument("--map", help="map folder name (default: every map with a finish line)")
    parser.add_argument("--model", help="model file name or pattern, e.g. best_car_100.pkl")
    parser.add_argument("--model-dir", nargs="+", help="experiment run folders to evaluate instead of maps/")
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--pos-jitter", type=float, default=10.0, help="pixels")
    parser.add_argument("--angle-jitter", type=float, default=10.0, help="degrees")
    parser.add_argument("--sensor-noise", type=float, default=0.05, help="std of relative radar noise")
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    parser.add_argument("--plot", action="store_true", help="save trajectory images")
    parser.add_argument("--out-dir", default="evaluation/results")
    parser.add_argument("--name", default=None, help="results file name (default: evaluation or experiment)")
    args = parser.parse_args()
    if args.name is None:
        args.name = "experiment" if args.model_dir else "evaluation"

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, CONFIG_PATH)
    pygame.init()
    pygame.display.set_mode([1, 1])

    models = find_models(args)
    if not models:
        sys.exit("No models found.")

    rows = []
    for map_name, path, label in models:
        row = evaluate(map_name, path, label, config, args)
        rows.append(row)
        print(f"{map_name:13s} {label:28s} training fitness={row['train_fitness']!s:>5s} baseline={row['baseline']:8s} "
              f"finished {row['finished']:3d}/{row['runs']} "
              f"({100 * row['completion_rate']:5.1f}%, 95% CI {100 * row['ci_low']:.0f}-{100 * row['ci_high']:.0f}%)  "
              f"crashed {row['crashed']:3d}  timeout {row['timeout']:3d}", flush=True)

    pooled = pooled_groups(rows)
    for p in pooled:
        rates = ", ".join(f"{rate:.0f}%" for rate in p["rates"])
        print(f"by seed  {p['map']:13s} {p['model']:22s} completion {rates} (mean {p['mean_rate']:.0f}%)")

    csv_file, md_file = write_results(rows, pooled, args)
    print(f"\nSettings: {settings_text(args)}")
    print(f"Results written to {csv_file} and {md_file}")


if __name__ == "__main__":
    main()

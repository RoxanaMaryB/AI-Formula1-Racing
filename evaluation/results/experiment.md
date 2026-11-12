| Track | Model | Unperturbed run | Runs completed | 95% CI | Crashed | Out of time | Median steps to finish |
|---|---|---|---|---|---|---|---|
| finish_line3 | distance_seed0/best_car_150 | crashed | **0/100** | 0–4% | 100 | 0 | – |
| finish_line3 | distance_seed1/best_car_150 | finished | **72/100** | 63–80% | 28 | 0 | 2372 |
| finish_line3 | distance_seed2/best_car_150 | finished | **29/100** | 21–39% | 71 | 0 | 2054 |
| finish_line3 | finish_seed0/best_car_150 | crashed | **0/100** | 0–4% | 100 | 0 | – |
| finish_line3 | finish_seed1/best_car_150 | finished | **22/100** | 15–31% | 78 | 0 | 2077 |
| finish_line3 | finish_seed2/best_car_150 | finished | **98/100** | 93–99% | 2 | 0 | 2554 |

By training seed:

| Track | Experiment | Seeds | Completion per seed | Mean completion | Median steps to finish per seed |
|---|---|---|---|---|---|
| finish_line3 | distance/best_car_150 | 3 | 0%, 72%, 29% | **34%** | –, 2372, 2054 |
| finish_line3 | finish/best_car_150 | 3 | 0%, 22%, 98% | **40%** | –, 2077, 2554 |

_100 runs, seed 0: start position +/-10 px, heading +/-10 deg, radar noise 5%, budget 4000 steps._

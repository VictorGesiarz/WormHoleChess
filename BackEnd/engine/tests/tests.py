
""" 
File to run experiments. With arguments we decide which one to run. 
"""

import argparse

from base_board_test_1 import test


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DQN experiments with different parameters.")
    parser.add_argument("--experiment", type=int, choices=[1, 2, 3], required=True,
                        help="Specify which experiment to run (1, 2, or 3).")
    parser.add_argument("--resume", action="store_true",
                        help="Resume the last saved experiment instead of starting over.")

    args = parser.parse_args()

    experiment_settings = {
        1: {"fixed": False, "inverse": False},
        2: {"fixed": True, "inverse": False},
        3: {"fixed": True, "inverse": True}
    }

    run_experiment(args.experiment, **experiment_settings[args.experiment], resume=args.resume)

#   https://github.com/thecookingmethods/projekt_zpo2425
import argparse

from config import Config
from startup import Startup

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--config", required=True, help="Config file", default='./config.json')
    args = arg_parser.parse_args()

    config = Config(args.config)

    startup = Startup(config)
    startup.run()

import datetime

from poker.gui.gui_qt_logic import UIActionAndSignals, QObject
from poker.tests import init_table
import os
from poker.tools.helper import get_dir, multi_threading
import threading
import inspect
import logging
import os
import sys
from unittest.mock import MagicMock, patch
import configparser
import pandas as pd
from PIL import Image
import threading
from poker.tools.mongo_manager import GameLogger
from poker.tools.mongo_manager import StrategyHandler
from poker.tools.mongo_manager import UpdateChecker
import multiprocessing

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from poker import main
from poker.tools.mongo_manager import StrategyHandler, UpdateChecker, GameLogger, MongoManager

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(levelname)s %(message)s',
                    )


class TestmultiThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  daemon=None)
        self.args = args
        self.kwargs = kwargs
        self.target = target
        return

    def run(self):
        logging.info("run this thread")
        h = self.kwargs['h']
        p = self.kwargs['p']
        t = self.kwargs['t']
        n = self.args
        if n == 3:
            self.target(h, p)
        elif n == 2:
            self.target(p)
        elif n == 1:
            self.target(h)
        else:
            self.target()

        if threading.currentThread().getName() == "tableCards":
            t.get_round_number(h)
            t.get_other_player_status(p, h)
            # logging.info(f"{t.other_players[0]['funds']}")
        elif threading.currentThread().getName() == "fund":
            t.get_my_funds(h, p)
            t.get_other_player_funds(p)


def run_test():
    # config = configparser.ConfigParser()
    # file = os.path.join(get_dir('.'), 'config.ini')
    # config.read(file)
    # parallel = config.getboolean('MultiThreading', 'parallel')
    # cores = config.getint('MultiThreading', 'cores')
    #dir = os.path.realpath(__file__)
    # logging.debug('Starting  thread')

    time_funds_start = datetime.datetime.utcnow()
    file = os.path.join(get_dir('tests', 'screenshots'), 'Capture3.png')
    LOG_FILENAME = 'testing.log'
    mongo = MongoManager()
    table_scraper_name = 'GG_TEST'

    table_dict = mongo.get_table(table_scraper_name)
    logger = logging.getLogger('tester')
    gui_signals = MagicMock()
    p = StrategyHandler()
    p.read_strategy(strategy_override='Default1')
    h = main.History()
    h.preflop_sheet = pd.read_excel('C:\\Users\\jinyi\\Desktop\\Poker\\poker\\tools\\preflop.xlsx', sheet_name=None)
    game_logger = GameLogger()

    t = main.TableScreenBased(p, table_dict, gui_signals, game_logger, 0.0)
    t.entireScreenPIL = Image.open(file)
    t.get_top_left_corner(p)
    t.get_dealer_position()
    t.init_get_other_players_info()
    # t.get_players_funds()
    res = multi_threading(t.get_my_funds2, [0, 1, 2, 3, 4, 5], disable_multiprocessing=False, dataframe_mode=False)
    logging.info(f"{t.player_funds}")
    logging.info(f"{res}")
    time_funds_end = datetime.datetime.utcnow()
    logging.info(f"Collapsed time for player funds: {time_funds_end - time_funds_start}")

if __name__ == '__main__':
    run_test()

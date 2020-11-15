import inspect
import logging
import os
import sys
from unittest.mock import MagicMock
import datetime
import pandas as pd
from PIL import Image
import threading
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from poker import main
from poker.tools.mongo_manager import StrategyHandler, GameLogger, MongoManager


# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s (%(threadName)-2s) %(message)s',
#                     )

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


def init_table(file, round_number=0, strategy='Default1'):
    timeout_start = datetime.datetime.utcnow()
    # logging.debug('Starting  thread')
    LOG_FILENAME = 'testing.log'
    mongo = MongoManager()
    table_scraper_name = 'GG_TEST'

    table_dict = mongo.get_table(table_scraper_name)
    logger = logging.getLogger('tester')
    gui_signals = MagicMock()
    p = StrategyHandler()
    p.read_strategy(strategy_override=strategy)
    h = main.History()
    h.preflop_sheet = pd.read_excel('C:\\Users\\jinyi\\Desktop\\Poker\\poker\\tools\\preflop.xlsx', sheet_name=None)
    game_logger = GameLogger()
    t = main.TableScreenBased(p, table_dict, gui_signals, game_logger, 0.0)
    t.entireScreenPIL = Image.open(file)
    t.init_get_other_players_info()
    t.get_top_left_corner(p)
    t.get_dealer_position()
    # t.get_my_funds(h, p)
    # t.get_my_cards(h)
    # t.get_table_cards(h)
    # t.get_round_number(h)
    h.round_number = round_number
    # t.init_get_other_players_info()
    # # t.get_other_player_names(p)
    # t.get_other_player_status(p, h)
    # t.get_other_player_funds(p)
    # t.get_other_player_pots()

    # # # run separate thread to fund and pots.
    t1 = TestmultiThread(group=None, target=t.get_players_funds, name='fund', args=(0),
                         kwargs={'h': h, 'p': p, 't': t})
    t2 = TestmultiThread(group=None, target=t.get_other_player_pots, name='pots', args=(0),
                         kwargs={'h': h, 'p': p, 't': t})
    t3 = TestmultiThread(group=None, target=t.get_my_cards, name='myCards', args=(1),
                         kwargs={'h': h, 'p': p, 't': t})
    t4 = TestmultiThread(group=None, target=t.get_table_cards, name='tableCards', args=(1),
                         kwargs={'h': h, 'p': p, 't': t})
    # t5 = TestmultiThread(group=None, target=t.get_my_funds, name='myFund', args=(3),
    #                      kwargs={'h': h, 'p': p, 't': t})
    # t6 = TestmultiThread(group=None, target=t.get_current_call_value, name='checkbutton', args=(2),
    #                      kwargs={'h': h, 'p': p, 't': t})
    # t7 = TestmultiThread(group=None, target=t.get_current_bet_value, name='checkbutton', args=(2),
    #                      kwargs={'h': h, 'p': p, 't': t})
    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t.check_for_checkbutton()
    t.check_for_call()
    t.check_for_betbutton()
    t.check_for_allincall()
    t.get_current_call_value(p)
    t.get_current_bet_value(p)
    p = MagicMock()
    gui_signals = MagicMock()
    t.totalPotValue = 0.5
    t.equity = 0.5

    t1.join()
    t2.join()
    t3.join()
    t4.join()

    if (not t1.is_alive()) and (not t2.is_alive()) and (not t3.is_alive()) and (not t4.is_alive()):
        timeout_end = datetime.datetime.utcnow()
        logging.info(f"collapsed {timeout_end - timeout_start}")
    return t, p, gui_signals, h, logger

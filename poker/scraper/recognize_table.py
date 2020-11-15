"""Recognize table"""
import datetime
import logging

from poker.scraper.screen_operations import take_screenshot, crop_screenshot_with_topleft_corner, \
    is_template_in_search_area, binary_pil_to_cv2, ocr, pil_to_cv2
from poker.scraper.table_setup import CARD_SUITES, CARD_VALUES
from poker.scraper.board import watchAndDisplayCards
from poker.tools.helper import multi_threading

log = logging.getLogger(__name__)


class TableScraper:
    def __init__(self, table_dict):
        self.table_dict = table_dict
        self.screenshot = None
        self.total_players = 6
        self.my_cards = None
        self.table_cards = None
        self.current_round_pot = None
        self.total_pot = None
        self.dealer_position = [None for _ in range(self.total_players)]
        self.dealer_position1 = None
        self.players_in_game = [None for _ in range(self.total_players)]
        self.player_funds = None
        # self.player_pots = None
        self.call_value = None
        self.raise_value = None
        self.call_button = None
        self.raise_button = None
        self.tlc = None
        self.player_funds = [None for _ in range(self.total_players)]
        self.player_pots = [None for _ in range(self.total_players)]

    def take_screenshot2(self):
        """Take a screenshot"""
        self.screenshot = take_screenshot()

    def crop_from_top_left_corner(self):
        """Crop top left corner based on the current selected table dict and replace self.screnshot with it"""
        self.screenshot, self.tlc = crop_screenshot_with_topleft_corner(self.screenshot,
                                                                        binary_pil_to_cv2(
                                                                            self.table_dict['topleft_corner']))
        return self.screenshot

    def lost_everything(self):
        """Check if lost everything has occurred"""
        return is_template_in_search_area(self.table_dict, self.screenshot,
                                          'lost_everything', 'lost_everything_search_area')

    def im_back(self):
        """Check if I'm back button is visible"""
        return is_template_in_search_area(self.table_dict, self.screenshot,
                                          'im_back', 'buttons_search_area')

    def get_my_cards2(self):
        """Get my cards"""
        self.my_cards = []
        # for value in CARD_VALUES:
        #     for suit in CARD_SUITES:
        #         if is_template_in_search_area(self.table_dict, self.screenshot,
        #                                       value.lower() + suit.lower(), 'my_cards_area'):
        #             self.my_cards.append(value + suit)
        image_area = 'my_cards_area'  # 'my_cards_area'   #

        search_area = self.table_dict[image_area]
        cropped_screenshot = self.screenshot.crop(
            (search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))

        cropped_screenshot = pil_to_cv2(cropped_screenshot)
        cardsFound, allValueMatches = watchAndDisplayCards(cropped_screenshot, image_area)
        self.my_cards = list(cardsFound)

        # if len(self.my_cards) != 2:
        #     if len(self.my_cards) == 1:
        #         self.screenshot.save("pics/ErrMyCardRecognize.png")
        #         assert len(self.my_cards) != 1, "My cards can never be 1"
        #     log.info("My cards are not recognized")
        log.info(f"My cards: {self.my_cards}")
        return True

    def get_table_cards2(self):
        """Get the cards on the table"""
        self.table_cards = []
        # for value in CARD_VALUES:
        #     for suit in CARD_SUITES:
        #         if is_template_in_search_area(self.table_dict, self.screenshot,
        #                                       value.lower() + suit.lower(), 'table_cards_area'):
        #             self.table_cards.append(value + suit)
        image_area = 'table_cards_area'  # 'my_cards_area'   #

        search_area = self.table_dict[image_area]
        cropped_screenshot = self.screenshot.crop(
            (search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))

        cropped_screenshot = pil_to_cv2(cropped_screenshot)
        cardsFound, allValueMatches = watchAndDisplayCards(cropped_screenshot, image_area)
        self.table_cards = list(cardsFound)

        log.info(f"Table cards: {self.table_cards}")
        if len(self.table_cards) == 1 or len(self.table_cards) == 2:
            self.screenshot.save("pics/ErrTableCardRecognize.png")
        # assert len(self.table_cards) != 1, "Table cards can never be 1"
        # assert len(self.table_cards) != 2, "Table cards can never be 2"
        return True

    def get_dealer_position2(self):
        """Determines position of dealer, where 0=myself, continous counter clockwise"""
        for i in range(self.total_players):
            if self.dealer_position[i] == True:
                self.dealer_position1 = i
                log.info(f"Dealer found at position {i}")
                return True
        log.warning("No dealer found.")
        self.dealer_position1 = 0

    def is_template_in_search_area1(self, arg={'name': None, 'player': None}):
        name = arg['name']
        player = arg['player']
        time_cv2_start = datetime.datetime.utcnow()
        if player is not None:
            if name == 'dealer_button':
                self.dealer_position[player] = is_template_in_search_area(self.table_dict, self.screenshot,
                                                                          'dealer_button', 'button_search_area',
                                                                          str(player))
            if name == 'covered_card':
                self.players_in_game[player] = is_template_in_search_area(self.table_dict, self.screenshot,
                                                                          'covered_card', 'covered_card_area',
                                                                          str(player))

        if name == 'raise_button':
            self.raise_button = is_template_in_search_area(self.table_dict, self.screenshot,
                                                           'raise_button', 'buttons_search_area')
        if name == 'call_button':
            self.call_button = is_template_in_search_area(self.table_dict, self.screenshot,
                                                          'call_button', 'buttons_search_area')
        if name == 'all_in_call_button':
            self.all_in_call_button = is_template_in_search_area(self.table_dict, self.screenshot,
                                                                 'all_in_call_button', 'buttons_search_area')
        if name == 'check_button':
            self.check_button = is_template_in_search_area(self.table_dict, self.screenshot,
                                                           'check_button', 'buttons_search_area')

        time_cv2_end = datetime.datetime.utcnow()
        log.info(f"Collapsed time for {name}: {time_cv2_end - time_cv2_start}")
        return True

    def fast_fold(self):
        """Find out if fast fold button is present"""
        return is_template_in_search_area(self.table_dict, self.screenshot,
                                          'fast_fold_button', 'my_turn_search_area')

    def is_my_turn(self):
        """Check if it's my turn"""
        return is_template_in_search_area(self.table_dict, self.screenshot,
                                          'my_turn', 'my_turn_search_area')

    def get_players_in_game(self):
        """
        Get players in the game by checking for covered cards.

        Return: list of ints
        """
        self.players_in_game[0] = True  # assume myself in game
        # for i in range(1, self.total_players):
        #     if is_template_in_search_area(self.table_dict, self.screenshot,
        #                                   'covered_card', 'covered_card_area', str(i)):
        #         self.players_in_game.append(i)
        log.info(f"Players in game: {self.players_in_game}")
        return True

    def get_player_funds(self, i):
        self.get_players_funds(player=i)
        return True

    def get_players_funds2(self):
        # res2 = multi_threading(self.get_player_funds, [0, 1, 2, 3, 4, 5], disable_multiprocessing=False,
        #                        dataframe_mode=False)
        assert res2 == [True, True, True, True, True, True], 'Player Funds are not calculated properly.'
        return True

    def get_players_funds(self, my_funds_only=False, skip=[], player=None):
        """
        Get funds of players

        Returns: list of floats

        """
        self.time_funds_start = datetime.datetime.utcnow()
        if player is not None:
            self.player_funds[player] = ocr(self.screenshot, 'player_funds_area', self.table_dict, str(player))
        else:
            if my_funds_only:
                counter = 1
            else:
                counter = self.total_players

            # self.player_funds = [None for _ in range(self.total_players)]
            for i in range(counter):
                # if i in skip:
                #     funds = 0
                # else:
                #     funds = ocr(self.screenshot, 'player_funds_area', self.table_dict, str(i))
                # self.player_funds.append(funds)
                self.player_funds[i] = ocr(self.screenshot, 'player_funds_area', self.table_dict, str(i))
            log.info(f"Player funds: {self.player_funds}")
        self.time_funds_end = datetime.datetime.utcnow()
        log.info(f"Collapsed time for player funds: {self.time_funds_end - self.time_funds_start}")
        return True

    def other_players_names(self):
        """Read other player names"""
        pass

    def get_pots(self):
        """Get current and total pot"""
        self.current_round_pot = ocr(self.screenshot, 'current_round_pot', self.table_dict)
        log.info(f"Current round pot {self.current_round_pot}")
        self.total_pot = ocr(self.screenshot, 'total_pot_area', self.table_dict)
        log.info(f"Total pot {self.total_pot}")

    def get_pots2(self, name):
        time_pots_start = datetime.datetime.utcnow()
        if name == 'current_round_pot':
            self.current_round_pot = ocr(self.screenshot, 'current_round_pot', self.table_dict)
            log.info(f"Current round pot {self.current_round_pot}")
        if name == 'total_pot_area':
            self.total_pot = ocr(self.screenshot, 'total_pot_area', self.table_dict)
            log.info(f"Total pot {self.total_pot}")
        time_pots_end = datetime.datetime.utcnow()
        log.info(f"Collapsed time for {name}: {time_pots_end - time_pots_start}")

    def get_player_pots(self, skip=[]):
        """Get pots of the players"""
        for i in range(self.total_players):
            if i in skip:
                self.player_pots[i] = 0
            else:
                self.player_pots[i] = ocr(self.screenshot, 'player_pot_area', self.table_dict, str(i))
        log.info(f"Player pots: {self.player_pots}")

        return True

    def get_player_pots_nn(self, i):
        time_pots_start = datetime.datetime.utcnow()
        self.player_pots[i] = ocr(self.screenshot, 'player_pot_area', self.table_dict, str(i))
        time_pots_end = datetime.datetime.utcnow()
        log.info(f"Collapsed time for player {i} pot: {time_pots_end - time_pots_start}")
        return True

    def check_button(self):
        """See if check button is avaialble"""
        return is_template_in_search_area(self.table_dict, self.screenshot,
                                          'check_button', 'buttons_search_area')

    def has_call_button(self):
        """Chek if call button is visible"""
        self.call_button = is_template_in_search_area(self.table_dict, self.screenshot,
                                                      'call_button', 'buttons_search_area')
        log.info(f"Call button found: {self.call_button}")
        return self.call_button

    def has_raise_button(self):
        """Check if raise button is present"""
        self.raise_button = is_template_in_search_area(self.table_dict, self.screenshot,
                                                       'raise_button', 'buttons_search_area')
        log.info(f"Raise button found: {self.raise_button}")
        return self.raise_button

    def has_check_button(self):
        """Check if check button is present"""
        self.check_button = is_template_in_search_area(self.table_dict, self.screenshot,
                                                       'check_button', 'buttons_search_area')
        log.info(f"Check button found: {self.check_button}")
        return self.check_button

    def has_all_in_call_button(self):
        """Check if all in call button is present"""
        return is_template_in_search_area(self.table_dict, self.screenshot,
                                          'all_in_call_button', 'buttons_search_area')

    def get_call_value(self):
        """Read the call value from the call button"""
        self.call_value = ocr(self.screenshot, 'call_value', self.table_dict)
        log.info(f"Call value: {self.call_value}")
        return self.call_value

    def get_raise_value(self):
        """Read the value of the raise button"""
        self.raise_value = ocr(self.screenshot, 'raise_value', self.table_dict)
        log.info(f"Raise value: {self.raise_value}")
        return self.raise_value

    def get_call_raise_value(self, name):
        time_value_start = datetime.datetime.utcnow()
        if name == 'raise_value':
            self.raise_value = ocr(self.screenshot, 'raise_value', self.table_dict)
            log.info(f"Raise value: {self.raise_value}")
        if name == 'call_value':
            self.call_value = ocr(self.screenshot, 'call_value', self.table_dict)
            log.info(f"Call value: {self.call_value}")

        time_value_end = datetime.datetime.utcnow()
        log.info(f"Collapsed time for {name}: {time_value_end - time_value_start}")

    def get_game_number_on_screen2(self):
        """Game number"""
        self.game_number = ocr(self.screenshot, 'game_number', self.table_dict)
        log.info(f"Game number: {self.game_number}")
        return self.game_number

"""Tests for tablbe setup"""
import os
import io
import cv2
import numpy as np
from PIL import Image
from unittest import TestCase
from poker.scraper.recognize_table import TableScraper
from poker.scraper.screen_operations import find_template_on_screen, get_table_template_image, \
    crop_screenshot_with_topleft_corner, binary_pil_to_cv2, ocr, get_ocr_float, is_template_in_search_area, pil_to_cv2
from poker.tools.helper import get_dir
from poker.tools.mongo_manager import MongoManager, UpdateChecker
import matplotlib.pyplot as plt
import logging
import os.path as path
import poker.scraper.screen as screen
from poker.scraper.board import watchAndDisplayCards
import poker.scraper.templateMatching as templateMatching


def test_cropping():
    entire_screen_pil = Image.open(os.path.join(get_dir('tests', 'screenshots'), 'test5.png'))
    top_left_corner = get_table_template_image('GG_TEST1', 'topleft_corner')
    img = cv2.cvtColor(np.array(entire_screen_pil), cv2.COLOR_BGR2RGB)
    count, points, bestfit, minimum_value = find_template_on_screen(top_left_corner, img, 0.01)


def test_crop_func():
    entire_screen_pil = Image.open(os.path.join(get_dir('tests', 'screenshots'), 'test5.png'))
    top_left_corner = get_table_template_image('GG_TEST1', 'topleft_corner')
    # cv2.imshow('image', top_left_corner)
    # cv2.waitKey(0)
    cropped = crop_screenshot_with_topleft_corner(entire_screen_pil, top_left_corner)
    assert cropped


def test_table_scraper():
    log = logging.getLogger(__name__)
    mongo = MongoManager()
    table_dict = mongo.get_table('GG_TEST')
    table_scraper = TableScraper(table_dict)
    table_scraper.screenshot = Image.open(os.path.join(os.environ['test_src'], 'Capture6.PNG'))
    table_scraper.crop_from_top_left_corner()
    log.info(f"Is my turn?{table_scraper.is_my_turn()}")
    table_scraper.lost_everything()
    table_scraper.get_my_cards2()
    table_scraper.get_table_cards2()
    table_scraper.get_dealer_position2()
    table_scraper.get_players_in_game()
    table_scraper.get_pots()
    table_scraper.get_players_funds()
    table_scraper.get_call_value()
    table_scraper.get_raise_value()
    # table_scraper.has_all_in_call_button()
    table_scraper.has_call_button()
    table_scraper.has_raise_button()
    # table_scraper.get_game_number_on_screen2()


def test_card_download():  # ok!
    mongo = MongoManager()
    table_dict = mongo.get_table('GG_TEST1')
    table_scraper = TableScraper(table_dict)
    # table_scraper.screenshot = Image.open(os.path.join(get_dir('tests', 'screenshots'), 'test5.png'))
    # screnshot = table_scraper.crop_from_top_left_corner()
    CARD_VALUES = "23456789TJQKA"
    CARD_SUITES = "CDHS"
    # CARD_VALUES = "9"
    # CARD_SUITES = "H"
    player = None
    for value in CARD_VALUES:
        for suit in CARD_SUITES:
            template_cv2 = binary_pil_to_cv2(table_dict[value.lower() + suit.lower()])
            # if player:
            #     search_area = table_dict[image_area][player]
            # else:
            #     search_area = table_dict[image_area]
            plt.imshow(template_cv2, cmap='gray', interpolation='bicubic')
            plt.show()
def test_excel_download():    # !! ok
    mongo = UpdateChecker()
    preflop_url, preflop_url_backup = mongo.get_preflop_sheet_url()
    print(preflop_url)

def test_card_upload():  # OK!
    mongo = MongoManager()
    table_dict = mongo.get_table('GG_TEST')
    table_scraper = TableScraper(table_dict)
    # table_scraper.screenshot = Image.open(os.path.join(get_dir('tests', 'screenshots'), 'test5.png'))
    # screnshot = table_scraper.crop_from_top_left_corner()
    CARD_VALUES = "23456789TJQKA"
    CARD_SUITES = "CDHS"
    for value in CARD_VALUES:
        for suit in CARD_SUITES:
            fileName = value.upper() + suit.lower() + '.png'
            label = value.lower() + suit.lower()
            pil_image = Image.open(os.path.join('../../../card-detector\\images', fileName))
            mongo.update_table_image(pil_image, label=label, table_name='GG_TEST')


def test_ocr_value():  # ok! for total pot
    log = logging.getLogger(__name__)
    mongo = MongoManager()
    table_dict = mongo.get_table('GG_TEST')
    table_scraper = TableScraper(table_dict)
    test_src = os.environ['test_src']
    table_scraper.screenshot = Image.open(os.path.join(test_src, 'jinyi 0006.PNG'))
    screenshot = table_scraper.crop_from_top_left_corner()

    # plt.imshow(cropped_screenshot, cmap='gray', interpolation='bicubic')   # ok!
    # plt.show()

    # Total pots test   # ok!!!
    search_area = table_dict['total_pot_area']
    cropped_screenshot = screenshot.crop((search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))
    total_pot = get_ocr_float(cropped_screenshot, 'total_pot_area')
    log.info(f"Total pot {total_pot}")

    # Current pot test   # ok !!!
    current_round_pot = 0
    search_area = table_dict['current_round_pot']
    cropped_screenshot = screenshot.crop((search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))
    current_round_pot = get_ocr_float(cropped_screenshot, 'current_round_pot')
    log.info(f"Current round pot {current_round_pot}")

    # plt.imshow(cropped_screenshot, cmap='gray', interpolation='bicubic')   # ok!
    # plt.show()

    # Player funds test
    player_funds = []
    player_pots = []
    for i in range(6):
        search_area = table_dict['player_funds_area'][str(i)]
        cropped_screenshot = screenshot.crop(
            (search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))
        funds = get_ocr_float(cropped_screenshot, 'player_funds_area')
        player_funds.append(funds)
    log.info(f"Player funds: {player_funds}")
    # Player pots test
    for i in range(6):
        search_area = table_dict['player_pot_area'][str(i)]
        cropped_screenshot = screenshot.crop(
            (search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))
        funds = get_ocr_float(cropped_screenshot, 'player_pot_area')
        player_pots.append(funds)
        # plt.imshow(cropped_screenshot, cmap='gray', interpolation='bicubic')
        # plt.show()
    log.info(f"Player pot: {player_pots}")


def test_ocr_value1():  # ok!
    log = logging.getLogger(__name__)
    test_dir = os.environ['test_src1']
    arr = os.listdir(test_dir)
    for testimage in arr:
        image = Image.open(path.join(test_dir, testimage))
        # image = cv2.imread(path.join(test_dir, testimage))
        # image = screen.imageToBw(image)
        final_value = get_ocr_float(image)
        log.info(f"{testimage} : {final_value}")

def test_is_my_turn():  ## ok!!!
    log = logging.getLogger(__name__)
    mongo = MongoManager()
    table_dict = mongo.get_table('GG_TEST')
    test_src = os.environ['test_src']
    table_scraper = TableScraper(table_dict)
    table_scraper.screenshot = Image.open(os.path.join(test_src, 'Capture6.PNG'))
    screenshot = table_scraper.crop_from_top_left_corner()


    print(is_template_in_search_area(table_dict, screenshot,
                               'my_turn', 'my_turn_search_area'))
    #
    search_area = table_dict['my_turn_search_area']
    template = table_dict['my_turn']
    template_cv2 = binary_pil_to_cv2(template)
    cropped_screenshot = screenshot.crop((search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))
    screenshot_cv2 = pil_to_cv2(cropped_screenshot)

    plt.imshow(cropped_screenshot, cmap='gray', interpolation='bicubic')   # ok!
    plt.imshow(template_cv2, cmap='gray', interpolation='bicubic')
    plt.show()


def test_dealer_position():   # ok for 0.85
    log = logging.getLogger(__name__)
    test_dir = os.environ['test_dealer']
    # image = Image.open(path.join(test_dir, 'player5.png'))
    # image = pil_to_cv2(image)
    template = Image.open(path.join(test_dir, 'button.png'))
    template = pil_to_cv2(template)
    for i in range(6, 36):
        image = Image.open(path.join(test_dir, 'player' + str(i) + '.png'))
        image = pil_to_cv2(image)
        count, points, bestfit, minimum_value = find_template_on_screen(template, image, 0.15)
        if count >= 1:
            log.info(f"dealer {i} button found")
            img = cv2.rectangle(image, (bestfit[0], bestfit[1]), (bestfit[0] + 25, bestfit[1] + 25), (0, 255, 0), 2)
            # plt.imshow(img, cmap='gray', interpolation='bicubic')   # ok!
            # plt.show()
            continue
        log.info(f"dealer {i} button not found")


def test_table_and_my_cards():  # ok
    log = logging.getLogger(__name__)
    mongo = MongoManager()
    table_dict = mongo.get_table('GG_TEST')
    table_scraper = TableScraper(table_dict)

    test_src_dir = os.environ['test_src']
    test_mode = 'all'   #'single'
    image_area = 'table_cards_area' # 'my_cards_area'

    if test_mode == 'single':
        arr = ['2020-11-06_17-15-50.png']
    else:
        arr = os.listdir(test_src_dir)
    for testImage in arr:
        table_scraper.screenshot = Image.open(os.path.join(test_src_dir, testImage))

        screenshot = table_scraper.crop_from_top_left_corner()
        # screen.showImage(pil_to_cv2(screenshot))
        # table_cards = []
        # player = None
        search_area = table_dict[image_area]
        cropped_screenshot = screenshot.crop((search_area['x1'], search_area['y1'], search_area['x2'], search_area['y2']))

        cropped_screenshot = pil_to_cv2(cropped_screenshot)
        # screen.showImage(cropped_screenshot)
        # This is ok!!
        # image = cv2.imread(path.join(test_src_dir, testImage))
        # areaToScanTopLeft = (300, 500)   # 300,500 for my hand region   default box size: 800x614
        # areaToScanBottomRight = (650, 700)
        # cropped_screenshot = image[areaToScanTopLeft[1]:areaToScanBottomRight[1], areaToScanTopLeft[0]:areaToScanBottomRight[0]]

        cardsFound, allValueMatches = watchAndDisplayCards(cropped_screenshot, image_area)
        table_cards = list(cardsFound)

        # image = templateMatching.highlightRois(cropped_screenshot, allValueMatches, (30, 50))
        # screen.showImage(image)

        if image_area == 'table_cards_area':
            log.info(f"Table cards:{testImage} : {table_cards}")
            assert len(table_cards) != 1, "Table cards can never be 1"
            assert len(table_cards) != 2, "Table cards can never be 2"
        else:
            log.info(f"My hand cards: {testImage} : {table_cards}")

    # screen.showImage(cropped_screenshot)
    # plt.imshow(cropped_screenshot, cmap='gray', interpolation='bicubic')   # ok!
    # plt.show()


def test_write_table():  # ok!!!
    log = logging.getLogger(__name__)
    mongo = MongoManager()
    table_dict = mongo.get_table('GG_TEST')
    # print(table_dict)
    filename = str(os.getpid()) + '.txt'
    fo = open(filename, "w")
    fo.write(str(table_dict))
    fo.close()


def test_put_table():  # ok!!!
    log = logging.getLogger(__name__)
    mongo = MongoManager()
    COMPUTER_NAME = os.getenv('COMPUTERNAME')
    table_dict = mongo.get_table('GG_TEST')
    fo = open("20824.txt", "r")
    dict_ = eval(fo.read())
    fo.close()
    dic = dict_
    dic['_owner'] = COMPUTER_NAME
    dic['table_name'] = 'GG_TEST_111'
    mongo.db['tables'].insert_one(dic)

import sys
import cv2
import numpy as np
import os.path as path
import poker.scraper.templateMatching as templateMatching
import poker.scraper.screen as screen
from functools import cmp_to_key
from math import sin, cos, pi
import sys, getopt
import os

# in test mode, use a test image as input, otherwise use live screen capture
testMode = True
# testImage = 'jinyi0046.png'

# how good does the match have to be? value between 0 and 1.
# 1 means it has to be a perfect match
matchingThreshold = 0.90
# it's faster to scan a smaller area rather than the whole screen
areaToScanTopLeft = (300, 500)   # 300,500 for my hand region   default box size: 800x614
areaToScanBottomRight = (650, 700)  # 650,700 for my hand region.


# things we're looking for
suits = ['spade', 'heart', 'club', 'diamond']
# values = ['ace', 'king', 'queen', 'jack', 'ten', 'nine', 'eight', 'seven', 'six', 'five', 'four', 'three', 'two']
values = ['2s', '2h', '2d', '2c', '3s', '3h', '3d', '3c', '4s', '4h', '4d', '4c', '5s', '5h', '5d', '5c',
          '6s', '6h', '6d', '6c', '7s', '7h', '7d', '7c', '8s', '8h', '8d', '8c', '9s', '9h', '9d', '9c',
          'Ts', 'Th', 'Td', 'Tc', 'Js', 'Jh', 'Jd', 'Jc', 'Qs', 'Qh', 'Qd', 'Qc', 'Ks', 'Kh', 'Kd', 'Kc',
          'As', 'Ah', 'Ad', 'Ac']

allcardsChecked = set()
# for testing specific cards
# suits = ['spade', 'heart']
# values = ['Qh', 'Qd', 'Qc', 'Jd', 'Tc']

allCards = {v + ' ' + s for s in suits for v in values}

# # cards found so far
# cardsFound = set()

def getImage(name):
    filename = name + '.png';
    image = cv2.imread(path.join(os.environ['image_src'], filename))
    image = screen.imageToBw(image)
    return image

def getRotImage(angle, image):
    (h, w) = image.shape[:2]
    M = np.array([[cos(angle/180*pi), -sin(angle/180*pi), 0],
                      [sin(angle/180*pi), cos(angle/180*pi), 0]], np.float32)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    return rotated

# suitsDict = {}
# for suit in suits:
#     suitsDict[suit] = getImage(suit)
#
# valuesDict = {}
# for value in values:
#     valuesDict[value] = getImage(value)
# suitList = getImage(suit)
# used for sorting a hand of cards
def getCardPosition(cardName):
    cardNameArr = cardName.split(' ')
    value = cardNameArr[0]
    suit = cardNameArr[1]
    valueIndex = values.index(value)
    suitIndex = suits.index(suit)
    return suitIndex * 13 + valueIndex

# used for sorting a hand of cards
def cardComparer(a, b):
    return getCardPosition(a) - getCardPosition(b)

# This is the main function that is executed continuously to watch for new cards and display them
def watchAndDisplayCards(image, image_area):

    image = screen.imageToBw(image)
    cardsFound = set()
    areaToScan = image

    # things we're looking for
    suits = ['spade', 'heart', 'club', 'diamond']
    values = ['2s', '2h', '2d', '2c', '3s', '3h', '3d', '3c', '4s', '4h', '4d', '4c', '5s', '5h', '5d', '5c',
              '6s', '6h', '6d', '6c', '7s', '7h', '7d', '7c', '8s', '8h', '8d', '8c', '9s', '9h', '9d', '9c',
              'Ts', 'Th', 'Td', 'Tc', 'Js', 'Jh', 'Jd', 'Jc', 'Qs', 'Qh', 'Qd', 'Qc', 'Ks', 'Kh', 'Kd', 'Kc',
              'As', 'Ah', 'Ad', 'Ac']
    matchingThreshold = 0.90
    if image_area == 'my_cards_area':
        angleList = [-5, 5]
    else:
        angleList = [0]

    valuesDict = {}
    for value in values:
        valuesDict[value] = getImage(value)
    suitsDict = {}
    for suit in suits:
        suitsDict[suit] = getImage(suit)

    allValueMatches = []
    hand = {}
    for value in values:
        hand[value] = 0
    for angle in angleList:
        for value in valuesDict:     # switch suitsDict and valuesDict for each test.
            valueTemplate = valuesDict[value]
            valueTemplate = valueTemplate[0:30, 0:20]
            valueTemplateRotP5 = getRotImage(angle, valueTemplate)
            valueMatches = templateMatching.getMatches(areaToScan, valueTemplateRotP5, matchingThreshold)
            valueMatches = map(lambda match: {'topLeft': (match[0], match[1]), 'name': value}, valueMatches)

            for valueMatch in valueMatches:
                valueMatchTopLeft = valueMatch['topLeft']
                searchArea = areaToScan[valueMatchTopLeft[1]+25:(valueMatchTopLeft[1]+55),valueMatchTopLeft[0]-5:(valueMatchTopLeft[0]+25)]
                suitRecord = {}
                for suit in suitsDict:
                    suitTemplate = suitsDict[suit]
                    suitTemplateRotP5 = getRotImage(angle, suitTemplate)
                    result = cv2.matchTemplate(searchArea, suitTemplateRotP5, cv2.TM_CCOEFF_NORMED)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
                    suitRecord[suit] = maxVal
                bestSuit = 'spade'
                for suit in suitsDict:
                    if suitRecord[suit] >= suitRecord[bestSuit]:
                        bestSuit = suit
                if bestSuit[0] == value[1]:
                    cardsFound.add(value)
                    hand[value] += 1
                    # print("cardsFound:", bestSuit, value, sep=' ', end='\n')
                    allValueMatches = allValueMatches + [valueMatch]
    if image_area == 'my_cards_area':
        while len(cardsFound) > 2:
            minValue = 10000
            minCard = ''
            for card in cardsFound:
                if hand[card] <= minValue:
                    minValue = hand[card]
                    minCard = card
            # print("remove redundant card", minCard)
            cardsFound.remove(minCard)

    # image = templateMatching.highlightRois(areaToScan, allValueMatches, (30, 50))
    # screen.showImage(image)
    return cardsFound, allValueMatches

def main():

    dir = '../../source\\repos\\Project1\\x64\\Debug\\screenshots\\hand_test'
    arr = os.listdir(dir)
    print(arr)

    for testimage in arr:

        if testMode:
            watchAndDisplayCards(testimage, dir)
        else:
            # keep watching for cards forever
            while True:
                watchAndDisplayCards()

if __name__ == "__main__":
    main()
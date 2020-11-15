import re
import cv2
import pytesseract
from pytesseract import Output
import argparse

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="type of preprocessing to be done")
args = vars(ap.parse_args())

img = cv2.imread(args["image"])
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

if args["preprocess"] == "thresh":
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
# make a check to see if median blurring should be done to remove
# noise
elif args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray, 3)

#### https://medium.com/@jaafarbenabderrazak.info/ocr-with-tesseract-opencv-and-python-d2c4ec097866
# 1. Text template matching ( detect only digits ):
# d = pytesseract.image_to_data(img, output_type=Output.DICT)
# keys = list(d.keys())
#
# date_pattern = '^[0-9]*$'
#
# n_boxes = len(d['text'])
# for i in range(n_boxes):
#     if int(d['conf'][i]) > 60:
#         if re.match(date_pattern, d['text'][i]):
#             (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
#             img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#

# cv2.imshow('img', imageGray)
# cv2.waitKey(0)

# 2. Detect only digits using configuration :
custom_config = r'--oem 3 --psm 6 outputbase digits'
print(pytesseract.image_to_string(gray, config=custom_config))

# 3. Whitelisting/Blacklisting characters :

# custom_config = r'-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz --psm 6'
# print(pytesseract.image_to_string(imageGray, config=custom_config))

# 4. blacklist letters:
# custom_config = r'-c tessedit_char_blacklist=abcdefghijklmnopqrstuvwxyz --psm 6'
# pytesseract.image_to_string(img, config=custom_config)

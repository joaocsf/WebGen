import os
import argparse
import numpy as np
import pprint
import cv2 as cv


def process_image(image):
  img = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
  kernel = 50
  kernel_element = 1
  weight = 30
  typ = 0
  if kernel < 1: 
    kernel = 1
    weight = 1
    kernel_element = 1
    typ = 0
  
  kernel = kernel *2 + 1
  kernel_element = kernel_element + 1

  method = cv.ADAPTIVE_THRESH_GAUSSIAN_C if typ == 0 else cv.ADAPTIVE_THRESH_MEAN_C
  thresh = cv.adaptiveThreshold(img, 256, method, cv.THRESH_BINARY, kernel, weight)
  element = cv.getStructuringElement(cv.MORPH_ELLIPSE, (kernel_element, kernel_element))
  thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, element)
  thresh = cv.morphologyEx(thresh, cv.MORPH_ERODE, element)

  thresh2 = cv.morphologyEx(thresh, cv.MORPH_ERODE, element, iterations=20)

  thresh2 = cv.bitwise_not(thresh2)
  _, contours, _ = cv.findContours(thresh2, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

  sizes = [(cv.contourArea(contour), contour) for contour in contours]

  thresh_color = cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)
  if len(sizes) == 0: 
    return thresh_color
  high = max(sizes, key=lambda c: c[0])[1]

  rect = cv.minAreaRect(high)
  box = cv.boxPoints(rect)
  box = np.int0(box)
  thresh2 = cv.cvtColor(thresh2, cv.COLOR_GRAY2BGR)
  thresh2 = thresh_color.copy()
  cv.drawContours(thresh2, [box], 0, (0,255,0), 2)

  #cv.imshow('Thresh2', thresh2)
  # cv.imshow('Corped', corped)
  return thresh_color

def arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('path')
  parser.add_argument('-o', '--out_path')

  return parser.parse_args()

def main():
  args = arguments()

  for file in os.listdir(args.path):
    file_path = os.path.join(args.path, file)
    out_file_path = os.path.join(args.out_path, file)
    res = process_image(cv.imread(file_path, cv.IMREAD_COLOR))
    cv.imwrite(out_file_path, res)


if __name__ == "__main__": 
  main()
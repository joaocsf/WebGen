import cv2 as cv
import numpy as np
import argparse
import random
import math

def computeLevelStructure(contour, hierarchy):
  data = {}
  maxLevel = 0
  print(hierarchy)
  print(len(contour))
  print(len(hierarchy[0]))
  for id, (a,b,c,d) in enumerate(hierarchy[0]):
    p_area = -1
    currLevel = 0
    parent = None
    if(d == -1):
      currLevel = 0
    else:
      parent = data[str(d)]
      father_level = parent['level']
      p_area= parent['area']
      parent['childs']+=1
      currLevel = father_level + 1

    x,y, w,h = cv.boundingRect(contour[id])
    area = w*h
    data[str(id)]={
      'level': currLevel,
      'area': area,
      'p_area': p_area,
      'childs': 0,
      'parent': parent
    }
    maxLevel = max(maxLevel, currLevel)

  return data, maxLevel

def segment(path):
  print(path)
  image = cv.imread(path, cv.IMREAD_GRAYSCALE)
  _, thresh_img = cv.threshold(image, 128, 256, cv.THRESH_BINARY_INV)

  dst = cv.distanceTransform(thresh_img, cv.DIST_C, 0)
  cv.normalize(dst, dst, 0, 1.0, cv.NORM_MINMAX)

  color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color2 = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color2[::] = (0,0,0)
  color3 = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color3[::] = (0,0,0)

  cv.imshow('Thresh', thresh_img)
  cv.imshow('Dst', dst)

  im2, contours, hierarchy = cv.findContours(thresh_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
  size = len(contours)

  hierarchy_data, maxLevel = computeLevelStructure(contours, hierarchy)

  image_w, image_h= image.shape[:2]
  image_area = image_h*image_w

  for index, contour in enumerate(contours):
    data = hierarchy_data[str(index)]
    level = data['level']
    area = data['area']
    p_area = data['p_area']
    childs = data['childs']

    if not data['parent'] is None and data['parent']['childs'] == 1:
      continue

    area_occupied = 0.0
    if p_area > 0:
      area_occupied = area/float(p_area)

    if level % 2 == 1: continue

    if area_occupied > 0.8: continue

    #if len(contour) > 200: continue
    clr = lerpColor(
      (0, 0, 0), (255, 255, 255),
      level/float(maxLevel+1)
    )

    hull = contour #cv.convexHull(contour, False)
    epsilon = 0.1*cv.arcLength(hull,True)
    hull = cv.approxPolyDP(hull,epsilon,True)

    cv.drawContours(color, [contour], -1, clr, -1)
    point = contour[random.randint(0,len(contour)-1)]
    pt = (point[0][0], point[0][1])
    text = '{0} : {1} {2} {3}'.format(index, int(level), area, childs)
    text2 = '{0} : {1}'.format(index, int(level))
    print(text, flush = True)
    cv.putText(color, text2, pt, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv.LINE_AA)

    clr = (
      random.randint(0,256),
      random.randint(0,256),
      random.randint(0,256)
    )

    i_clr = (256-clr[0], 256-clr[1], 256-clr[2])
    cv.drawContours(color2, [contour], -1, clr, -1)
    #cv.drawContours(color2, [hull], -1, i_clr, 4)
    # for id, point in enumerate(hull):
    #   t = id/float(len(hull)-1)
    #   #Cyan to Yellow
    #   tmp_color = lerpColor((0,255,0), (0,0,255), t)
    #   print(tmp_color)
    #   pt = (point[0][0], point[0][1])
    #   cv.circle(color2, pt, 4, tmp_color, -1)

    x,y,w,h = cv.boundingRect(contour)
    cv.rectangle(color3, (x,y), (x+w, y+h), clr, -1)

  cv.imshow('Hierarchy', color)
  cv.imshow('Elements', color2)
  cv.imshow('Rects', color3)


  while cv.waitKey(1) != 27: continue

def lerpColor(a,b,l):
  r = (
    int(l*b[0] + (1-l)*a[0]),
    int(l*b[1] + (1-l)*a[1]),
    int(l*b[2] + (1-l)*a[2])
  )
  return r


def main():
  parser = argparse.ArgumentParser(description="Segmentation Test")
  parser.add_argument('path')

  args = parser.parse_args()

  segment(args.path)


if __name__ == "__main__":
    main()



from .Detector import Detector
from model.image_classification import Classifier
import os
import sys
from PIL import Image
import cv2 as cv
import numpy as np
import random

WORK_DIR = os.path.dirname(__file__)

class DetectorCNN(Detector):

  def __init__(self, classes_file):
    super().__init__()
    self.classifier = Classifier(None, None, classes_file)
  
  def on_destroy(self):
    pass
  
  def on_detect(self, image):
    
    elements, containers = segment(image)

    boxes = [
      ','.join(
        [str(e['x']),       str(e['y']), 
        str(e['x']+e['w']), str(e['y'] + e['h'])])
      for e in elements
      ]

    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    result = self.classifier.classify(image, boxes)

    for i, c in enumerate(result):
      elements[i]['class']=c
    
    print(len(containers))
    return elements+containers

def get_element(class_name, x,y,w,h):
  return {
    'class': class_name,
    'x': int(x),
    'y': int(y),
    'w': int(w),
    'h': int(h),
    'childs': [],
  }
  
def computeLevelStructure(contour, hierarchy):
  data = {}
  maxLevel = 0
  #print(hierarchy)
  #print(len(contour))
  #print(len(hierarchy[0]))
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
      currLevel = father_level + 1

    x,y, w,h = cv.boundingRect(contour[id])
    area = w*h
    data[str(id)]={
      'level': currLevel,
      'area': area,
      'p_area': p_area,
      'childs': [],
      'parent': parent
    }

    if(parent != None):
      parent['childs'].append(data[str(id)])
    maxLevel = max(maxLevel, currLevel)

  return data, maxLevel

def segment(image):
  image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
  _, thresh_img = cv.threshold(image, 128, 256, cv.THRESH_BINARY_INV)
  #dst = cv.distanceTransform(thresh_img, cv.DIST_C, 0)
  #cv.normalize(dst, dst, 0, 1.0, cv.NORM_MINMAX)

  color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color2 = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color2[::] = (0,0,0)
  color3 = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color3[::] = (0,0,0)

  #cv.imshow('Thresh', thresh_img)
  #cv.imshow('Dst', dst)

  im2, contours, hierarchy = cv.findContours(thresh_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
  size = len(contours)

  hierarchy_data, maxLevel = computeLevelStructure(contours, hierarchy)

  image_w, image_h= image.shape[:2]
  image_area = image_h*image_w

  elements = []
  containers = []

  for index, contour in enumerate(contours):
    data = hierarchy_data[str(index)]
    level = data['level']
    area = data['area']
    p_area = data['p_area']
    n_childs = len(data['childs'])
    childs = data['childs']

    if not data['parent'] is None and len(data['parent']['childs']) == 1:
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

    x,y,w,h = cv.boundingRect(contour)
    print('Size', (x,y,w,h))
    #childs_of_childs = len(childs[0]['childs']) if n_childs
    is_container = False
    if n_childs >= 1:
      for c in childs:
        if len(c['childs']) > 1:
          containers.append(get_element('Container',x,y,w,h))
          is_container = True
          break

    if not is_container:
      elements.append(get_element('',x,y,w,h))

    hull = contour #cv.convexHull(contour, False)
    epsilon = 0.1*cv.arcLength(hull,True)
    hull = cv.approxPolyDP(hull,epsilon,True)

    cv.drawContours(color, [contour], -1, clr, -1)
    point = contour[random.randint(0,len(contour)-1)]
    pt = (point[0][0], point[0][1])
    text = '{0} : {1} {2} {3}'.format(index, int(level), area, n_childs)
    text2 = '{0} : {1}'.format(index, int(level))
    #print(text, flush = True)
    cv.putText(color, text2, pt, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv.LINE_AA)

    clr = (
      random.randint(0,256),
      random.randint(0,256),
      random.randint(0,256)
    )

    i_clr = (256-clr[0], 256-clr[1], 256-clr[2])
    cv.drawContours(color2, [contour], -1, clr, -1)

    
    x,y,w,h = cv.boundingRect(contour)
    cv.rectangle(color3, (x,y), (x+w, y+h), clr, -1)

  cv.imshow('Color', color)
  cv.imshow('Color2', color2)
  cv.imshow('Color3', color3)
  return elements, containers

def lerpColor(a,b,l):
  r = (
    int(l*b[0] + (1-l)*a[0]),
    int(l*b[1] + (1-l)*a[1]),
    int(l*b[2] + (1-l)*a[2])
  )
  return r
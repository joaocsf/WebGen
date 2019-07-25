import os
#logging.getLogger('tensorflow').setLevel(logging.NOTSET)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import sys
import importlib
from PIL import Image
from model import merge
import argparse
import time
import cv2 as cv
from pipeline import pipeline as PipeLine
import json
import numpy as np

BANNER="""

-----------------=========================================-----------------

{0}'|| '||'  '|'         '||     {1}     ..|'''.|                   
{0} '|. '|.  .'    ....   || ... {1}    .|'     '    ....  .. ...   {2}
{0}  ||  ||  |   .|...||  ||'  ||{1}    ||    .... .|...||  ||  ||  {2}
{0}   ||| |||    ||       ||    |{1}    '|.    ||  ||       ||  ||  {2}
{0}    |   |      '|...'  '|...' {1}     ''|...'|   '|...' .||. ||. {2}

-----------------=========================================-----------------
""".format('\033[93m', '\033[92m', '\033[0m')

PROCESSING_IMAGE = """
\033[92m Processing Image...
\033[0m
"""

SETUP ="""
\033[92m Initializing
\033[0m
"""

Processing ="""
\033[92m Processing
\033[0m
"""

class MockCode:
  def __init__(self, pipeline):
    self.pipeline=pipeline
    cv.namedWindow('Image', cv.WINDOW_NORMAL)
    cv.createTrackbar('type', 'Image', 0, 1, nothing) 
    cv.createTrackbar('kernel', 'Image', 11, 50, nothing) 
    cv.createTrackbar('weight', 'Image', 10, 50, nothing) 
    cv.createTrackbar('kernel_e', 'Image', 1, 3, nothing) 
  
  def video(self, camera):
    print('Processing Video')
    cam = cv.VideoCapture(camera)
    cv.setWindowProperty('Image', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    cv.setWindowProperty('Image', cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
    cv.waitKey(1)

    while True:
      _, img = cam.read()
      key = cv.waitKey(1)
      img = self.adapt_image(img)
      #cv.imshow('Image', img)
      if key == 114:
        print('Restarting Video Stream')
        cam.release()
        cam = cv.VideoCapture(camera)
      if key == 27:
        break
      elif key == 32:
        #cv.imshow('ScreenShot', img)
        cv.waitKey(1)
        print(Processing)
        self.__run_pipeline__(img)
        cv.setWindowProperty('Image', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        cv.setWindowProperty('Image', cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        cv.waitKey(1)
  
  def test(self, file_path, eval_obj):

    with open(file_path, 'r') as file:
      for line in file.readlines():
        eval_obj['current'] = line
        image = line.split(' ')[0]
        image = cv.imread(image, cv.IMREAD_COLOR)
        if(image is None):
          print('Error Files Missing')
          return
        self.__run_pipeline__(image)

  def interactive(self, folder_path):
    i = ''
    files = os.listdir(folder_path)
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f) or -1)))
    add1 = int(''.join(filter(str.isdigit,files[0])))
    while True:
      try:
        i = input('Image_ID {0}:'.format(len(files)))
        if i == 'exit': 
          return
        id = int(i) - add1
        path = os.path.join(folder_path, files[id])
        print(path)
        self.image(path)
      except:
        print('Wrong Value')
        i = 'exit'

  def image(self, image_path):
    print(PROCESSING_IMAGE, flush=True)
    image = cv.imread(image_path)
    #cv.imshow('Input', image)
    cv.waitKey(1)
    image = self.adapt_image(image)
    print(Processing)
    self.__run_pipeline__(image)
  
  def __run_pipeline__(self, image):
    self.pipeline.execute(image)
    self.pipeline.show_generator_results()

  def corp_image(self, img, rect):
    center, size, angle = rect[0], rect[1], rect[2]
    center, size = tuple(map(int, center)), tuple(map(int, size))
    if angle < -45:
      angle += 90
      size = (size[1], size[0])
    height, width = img.shape[0], img.shape[1]

    M = cv.getRotationMatrix2D(center, angle, 1)
    img_rot = cv.warpAffine(img, M, (width, height))

    img_crop = cv.getRectSubPix(img_rot, size, center)

    return img_crop, img_rot

  def adapt_image(self, img):
    cv.namedWindow('Image', cv.WINDOW_NORMAL)

    original_img = img
    img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    kernel = cv.getTrackbarPos('kernel', 'Image')
    kernel_element = cv.getTrackbarPos('kernel_e', 'Image')
    weight = cv.getTrackbarPos('weight', 'Image')
    typ = cv.getTrackbarPos('type', 'Image')
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
    element2 = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, element)
    thresh = cv.morphologyEx(thresh, cv.MORPH_ERODE, element2, iterations=1)

    thresh2 = cv.morphologyEx(thresh, cv.MORPH_ERODE, element2, iterations=10)

    thresh2 = cv.bitwise_not(thresh2)
    _, contours, _ = cv.findContours(thresh2, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    sizes = [(cv.contourArea(contour), contour) for contour in contours]

    thresh_color = cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)
    cv.imshow('Image', original_img)
    return thresh_color

    if len(sizes) == 0: 
      cv.imshow('Image', original_img)
      return thresh_color
    high = max(sizes, key=lambda c: c[0])[1]

    rect = cv.minAreaRect(high)
    box = cv.boxPoints(rect)
    box = np.int0(box)
    thresh2 = cv.cvtColor(thresh2, cv.COLOR_GRAY2BGR)
    thresh2 = thresh_color.copy()
    cv.drawContours(original_img, [box], 0, (0,255,0), 2)

    corped, rot = self.corp_image(thresh, rect)
    cv.imshow('Image', original_img)
    if corped is None or np.sum(corped.shape) == 0:
      return thresh_color

    corped = cv.cvtColor(corped, cv.COLOR_GRAY2BGR)
    cv.imshow('Corped', corped)
    return thresh_color

def arg_parse():
  parser = argparse.ArgumentParser('')
  parser.add_argument('-i', '--image')
  parser.add_argument('-o', '--out', default='generated/')
  parser.add_argument('-a', '--alternative')
  parser.add_argument('-dg', '--debuggen')
  parser.add_argument('-c', '--camera', default=0)
  parser.add_argument('--interactive')

  parser.add_argument('--testing', dest='testing')
  parser.add_argument('--testing-yolo', dest='testing_yolo', action='store_true')
  parser.add_argument('--testing-p2p', dest='testing_pix2pix', action='store_true')
  parser.add_argument('--testing-classes', dest='testing_classes', default="./model/classes.txt")
  parser.add_argument('--testing-p2p-weights', dest='testing_pix2pix_weights')
  parser.add_argument('--testing-p2p-yolo-weights', dest='testing_pix2pix_yolo_weights')
  parser.add_argument('--testing-yolo-weights', dest='testing_yolo_weights')

  parser.add_argument('--measure_time', dest='measure_time')

  return parser.parse_args()

def nothing(x):
  pass

def setup_dnn_pipeline(pipeline):
  yolo = PipeLine.detection.DetectorYOLO()
  pix2pix = PipeLine.detection.DetectorPix2Pix()
  pipeline.add_detection(yolo)
  pipeline.add_detection(pix2pix)

  merger = PipeLine.result_processing.ProcessorMerger()
  component = PipeLine.result_processing.ProcessorComponents()
  selector = PipeLine.result_processing.ProcessorSelector()
  vLists = PipeLine.result_processing.ProcessorLists('v')
  hLists = PipeLine.result_processing.ProcessorLists('h')

  hierarchy = PipeLine.result_processing.ProcessorHierarchy('h')

  pipeline.add_processing(merger)
  pipeline.add_processing(component)
  pipeline.add_processing(selector)
  pipeline.add_processing(vLists)
  pipeline.add_processing(hLists)

  pipeline.add_processing(hierarchy)

  html_generator = PipeLine.code_generation.GeneratorHTMLGRIDV2()
  pipeline.add_generator(html_generator)

def setup_cnn_pipeline(pipeline, classes_path):
  cnn = PipeLine.detection.DetectorCNN(classes_path)
  pipeline.add_detection(cnn)

  merger = PipeLine.result_processing.ProcessorMerger()
  component = PipeLine.result_processing.ProcessorComponents()
  selector = PipeLine.result_processing.ProcessorSelector()
  vLists = PipeLine.result_processing.ProcessorLists('v')
  hLists = PipeLine.result_processing.ProcessorLists('h')
  pipeline.add_processing(merger)
  pipeline.add_processing(component)
  pipeline.add_processing(selector)
  pipeline.add_processing(vLists)
  pipeline.add_processing(hLists)  
  
  html_generator = PipeLine.code_generation.GeneratorHTMLGRIDV2()
  pipeline.add_generator(html_generator)

def setup_debug_gen_pipeline(pipeline, annotation_file):

  objs = {}
  with open(annotation_file, 'r') as file:
    objs = json.load(file)
  pipeline.ommit_process('detection', objs)

  merger = PipeLine.result_processing.ProcessorMerger()
  component = PipeLine.result_processing.ProcessorComponents()
  selector = PipeLine.result_processing.ProcessorSelector()
  vLists = PipeLine.result_processing.ProcessorLists('v')
  hLists = PipeLine.result_processing.ProcessorLists('h')

  hierarchy = PipeLine.result_processing.ProcessorHierarchy('h')

  pipeline.add_processing(merger)
  pipeline.add_processing(component)
  pipeline.add_processing(selector)
  pipeline.add_processing(vLists)
  pipeline.add_processing(hLists)
  pipeline.add_processing(hierarchy)

  html_generator = PipeLine.code_generation.GeneratorHTMLLists()
  html_generator = PipeLine.code_generation.GeneratorHTMLGRIDV2()
  pipeline.add_generator(html_generator)

def test_all(pipeline, add_pix2pix, add_yolo, pix2pix_data, yolo_data, eval_obj, classes_path):

  objs = {}

  if(add_yolo):
    yolo = PipeLine.detection.DetectorYOLO(
      model_path=yolo_data['model'])
    pipeline.add_detection(yolo)

  if(add_pix2pix):
    pix2pix = PipeLine.detection.DetectorPix2Pix(
      p2p_weights=pix2pix_data['p2p_weights'],
      yolo_weights=pix2pix_data['yolo_weights'])
    pipeline.add_detection(pix2pix)


  html_generator = PipeLine.code_generation.GeneratorTest(eval_obj, classes_path)
  pipeline.add_generator(html_generator)

def main():
  args = arg_parse()
  eval_obj = {'current': 0}

  print(BANNER, flush=True)
  print(SETUP, flush=True)

  pipeline = PipeLine.Pipeline(args.out)

  if not args.debuggen is None:
    setup_debug_gen_pipeline(pipeline, args.debuggen)

  elif not args.alternative is None:
    setup_cnn_pipeline(pipeline, args.alternative)

  elif not args.testing is None:
    yolo_data = {
      "model": args.testing_yolo_weights
    }
    p2p_data = { 
      "p2p_weights": args.testing_pix2pix_weights,
      "yolo_weights": args.testing_pix2pix_yolo_weights
    }
    test_all(pipeline, args.testing_pix2pix, args.testing_yolo, p2p_data, yolo_data, eval_obj, args.testing_classes)
  else:
    setup_dnn_pipeline(pipeline)

  mockcode = MockCode(pipeline)

  if not args.interactive is None:
    mockcode.interactive(args.interactive)

  elif not args.measure_time is None:
    mockcode.test(args.measure_time, eval_obj)

  elif not args.testing is None:
    mockcode.test(args.testing, eval_obj)

  elif args.image == None:
    mockcode.video(args.camera)

  else:
    mockcode.image(args.image)
    cv.waitKey(0)


if __name__ == "__main__":
  main()
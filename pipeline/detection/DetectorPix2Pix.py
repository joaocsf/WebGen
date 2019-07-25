from .Detector import Detector
from model.pix2pix import Pix2Pix
import os
import sys
from PIL import Image
import cv2 as cv
import numpy as np
import importlib

WORK_DIR = os.path.dirname(__file__)

DEFAULT_PIX2PIX_WEIGHTS = os.path.join(WORK_DIR, '../../model/pix2pix/out/transfer_learning/')
DEFAULT_YOLO_MODEL = os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/containers_transferlearning.h5')
DEFAULT_YOLO_CLASSES = os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/container_classes.txt')

DEFAULT_PIX2PIX_WEIGHTS = os.path.join(WORK_DIR, '../../model/pix2pix/out/only_drawings/')
DEFAULT_YOLO_MODEL = os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/containers_hand_original_weights.h5')
DEFAULT_YOLO_CLASSES = os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/container_classes.txt')


class DetectorPix2Pix(Detector):
  def __init__(self, p2p_weights=DEFAULT_PIX2PIX_WEIGHTS, yolo_weights=DEFAULT_YOLO_MODEL):
    self.default_pix2pix_weights = p2p_weights
    print(p2p_weights)
    self.default_yolo_weights = yolo_weights
    super().__init__()

  def on_create(self):
    self.pix2pix = Pix2Pix(None, None, weights_path=self.default_pix2pix_weights)
    yolo = importlib.import_module('model.keras-yolo3.yolo')

    yolo_config = {
        "model_path": self.default_yolo_weights,
        "classes_path": DEFAULT_YOLO_CLASSES
      }
    self.YOLO = yolo.YOLO(**yolo_config)
  
  def on_destroy(self):
    pass
  
  def result_to_image(self, result):
    result = np.uint8(result*127 + 127)
    image = Image.fromarray(result)
    return image

  def on_detect(self, image):
    img_original_h, img_original_w = image.shape[:2]
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = Image.fromarray(image)

    result = self.pix2pix.predict_image(image)
    image = self.result_to_image(result)
    #image.show('Pix2Pix')
    image_h, image_w = result.shape[:2]
    result = self.YOLO.detect_boxes(image)

    fx = img_original_w/float(image_w)
    fy = img_original_h/float(image_h)
    return self.to_json(result, fx, fy)
  
  def to_json(self, boxes, fx, fy):
    result = []
    for box in boxes:
      x,y,mx,my,id,c,s = box
      x  *= fx
      y  *= fy
      mx *= fx
      my *= fy
      result.append(
        {
          'class': c,
          'class_id': id,
          'x': x,
          'y': y,
          'w': mx-x,
          'h': my-y,
          'score': s
        }
      )
    return result
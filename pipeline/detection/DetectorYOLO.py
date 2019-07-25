from .Detector import Detector
import os
import sys
import importlib
from PIL import Image
import cv2 as cv

WORK_DIR = os.path.dirname(__file__)

DEFAULT_MODEL_DATA = os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/elements_transferlearning.h5')
DEFAULT_CLASS_DATA = os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/element_classes.txt')

class DetectorYOLO(Detector):
  def __init__(self, model_path=DEFAULT_MODEL_DATA, classes_path=DEFAULT_CLASS_DATA):
    self.model_path = model_path
    self.classes_path = classes_path
    super().__init__()

  def on_create(self):
    #self.work_path = os.getcwd()
    #self.yolo_path = os.path.join(WORK_DIR, '../../model/keras-yolo3/')

    #sys.path.append(self.yolo_path)
    yolo = importlib.import_module('model.keras-yolo3.yolo')
    yolo_config = {
        "model_path": self.model_path,
        "classes_path": self.classes_path
      }

    #os.chdir(self.yolo_path)
    self.YOLO = yolo.YOLO(**yolo_config)
    #os.chdir(self.work_path)
  
  def __del__(self):
    self.on_destroy()
  
  def on_destroy(self):
    #os.chdir(self.yolo_path)

    self.YOLO.close_session()

    #os.chdir(self.work_path)
  
  def on_detect(self, image):
    #os.chdir(self.yolo_path)

    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = Image.fromarray(image)

    result = self.YOLO.detect_boxes(image)
    #os.chdir(self.work_path)
    res = self.to_json(result)
    res = [r for r in res if not r['class'] == 'Container']
    return res
  
  def to_json(self, boxes):
    result = []
    for box in boxes:
      x,y,mx,my,id,c,s = box
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
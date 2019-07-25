import argparse
import yolo
import os
from PIL import Image
import multiprocessing.dummy as mp

WORK_DIR = os.path.dirname(__file__)

default_model_name = os.path.join(WORK_DIR, './model_data/yolo_weights.h5')
default_classes = os.path.join(WORK_DIR, './model_data/classes.txt')

class Evaluator:

  def __init__(self, out_dir, model_path, classes):
    self.yolo = yolo.YOLO(
      **{
        "model_path": model_path,
        "classes_path": classes,
      }
    )
    self.classes = get_classes(classes)
    self.out_dir = out_dir
    self.out_tr = os.path.join(out_dir, 'detection-results')
    self.out_gt = os.path.join(out_dir, 'ground-truth')
    make_dir(self.out_gt)
    make_dir(self.out_tr)
    self.finishedFiles = 0


  def process_image(self, data):
    data = data.split(' ')
    image_path = data[0]
    boxes = data[1::]
    image = Image.open(image_path)
    p_boxes = self.yolo.detect_boxes(image)

    boxes = [x.split(',') for x in boxes]
    self.store_data(image_path, boxes)
    self.store_data(image_path, p_boxes, True)

    self.finishedFiles+=1

    print_progressbar(self.finishedFiles/self.totalLines, suffix='{0}/{1}'.format(self.finishedFiles, self.totalLines))
  
  def store_data(self, image, boxes, prediction=False):
    _, name = os.path.split(image)
    name = name.replace('.png', '.txt')
    path = os.path.join(self.out_gt, name)
    if prediction:
      path = os.path.join(self.out_tr, name)

    lines = [] 
    for box in boxes:
      box_data = box
      class_name = self.classes[int(box_data[4])]

      left = box_data[0]
      top = box_data[1]
      right = box_data[2]
      bottom = box_data[3]
      text = ''
      if prediction:
        confidence = box_data[-1]
        text = '{0} {1} {2} {3} {4} {5}\n'.format(class_name, confidence, left, top, right, bottom)
      else:
        text = '{0} {1} {2} {3} {4}\n'.format(class_name, left, top, right, bottom)

      lines.append(text)
    
    with open(path, 'w') as file:
      file.writelines(lines)


  def create_files(self, file):

    self.finishedFiles = 0

    with open(file, 'r') as f:
      lines = f.readlines()
      self.totalLines = len(lines)
      for line in lines:
        self.process_image(line)

def get_classes(file):
  with open(os.path.join(WORK_DIR,file), 'r') as f:
    lines = f.readlines()
    return [line.replace('\n','') for line in lines]

def make_dir(dir):
  if not os.path.exists(dir):
    os.makedirs(dir)

def print_progressbar(percentage, width=50, prefix='>', suffix='...'):
  filled = int(width*percentage)
  toFill = width-filled
  bar = '='*filled + '-'*toFill
  suffix += ' '*(20-len(suffix))
  print('\r{0} [{2}] {3:0.2f}% {1}'.format(prefix, suffix, bar, percentage), end='\r')

def args():
  parser = argparse.ArgumentParser()
  parser.add_argument('file')
  parser.add_argument('-o', dest='out')
  parser.add_argument('-m', '--model', dest='model', default=default_model_name)
  parser.add_argument('-c', '--classes', dest='classes', default=default_classes)
  return parser.parse_args()

def main():
  parser = args()

  evaluator = Evaluator(parser.out, parser.model, parser.classes)
  evaluator.create_files(parser.file)

if __name__ == "__main__":
  main()
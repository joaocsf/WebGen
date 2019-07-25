from .Generator import Generator
import os
import webbrowser
from shutil import copyfile

WORK_DIR = os.path.dirname(__file__)

class GeneratorTest(Generator):
  def __init__(self, eval_obj, classes, evaluation_path="Evaluation"):
    
    super().__init__()
    self.evaluation_folder = evaluation_path
    self.eval_obj = eval_obj
    self.classes = get_classes(classes)

  def on_process(self, elements, out_folder):
    out_folder = os.path.join(out_folder, self.evaluation_folder)
    os.makedirs(os.path.dirname(out_folder), exist_ok=True)
    self.ground_truth = os.path.join(out_folder, './ground-truth/')
    self.detection_results = os.path.join(out_folder, './detection-results/')
    os.makedirs(self.ground_truth, exist_ok=True)
    os.makedirs(self.detection_results, exist_ok=True)
    #print('#######ELEMENTS', elements)
    print('\n\nCurrent', self.eval_obj['current'], flush=True)
    self.evaluate(elements, self.eval_obj['current'])

  def show(self):
    pass

  def evaluate(self, prediction, original_boxes):
    original_boxes = original_boxes.replace('\n','').strip()
    data = original_boxes.split(' ')
    print(data)
    image_path = data[0]
    boxes = data[1::]
    p_boxes = [
                [x['x']      , x['y'], 
                x['x']+x['w'], x['y'] + x['h'],
                x['class_id'], x['score']] for x in prediction]

    boxes = [x.split(',') for x in boxes]
    self.store_data(image_path, boxes)
    self.store_data(image_path, p_boxes, True)

  def store_data(self, image, boxes, prediction=False):
    _, name = os.path.split(image)
    name = name.replace('.png', '.txt')
    path = os.path.join(self.ground_truth, name)
    if prediction:
      path = os.path.join(self.detection_results, name)

    print(boxes, prediction, self.classes, flush=True)
    lines = [] 
    for box in boxes:
      box_data = box
      print(int(box_data[4]), prediction, self.classes, flush=True)
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


def get_classes(file):
  with open(file, 'r') as f:
    lines = f.readlines()
    return [line.replace('\n','') for line in lines]


def print_progressbar(percentage, width=50, prefix='>', suffix='...'):
  filled = int(width*percentage)
  toFill = width-filled
  bar = '='*filled + '-'*toFill
  suffix += ' '*(20-len(suffix))
  print('\r{0} [{2}] {3:0.2f}% {1}'.format(prefix, suffix, bar, percentage), end='\r')
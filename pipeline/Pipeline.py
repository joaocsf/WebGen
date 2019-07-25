from .detection import Detector
from .result_processing import Processor
from .code_generation import Generator
import os
import cv2 as cv
import time
import pickle


WORK_DIR = os.path.dirname(__file__)
DEFAULT_STATISTICS_DIR = os.path.join(WORK_DIR,'stats/')

class Pipeline():

  def __init__(self, out_folder, statistics=DEFAULT_STATISTICS_DIR):
    self.out_folder =out_folder
    self.statistics_dir = statistics

    self.detectors = []
    self.processors = []
    self.generators = []
    self.detection_results = []
    self.ommit = {}

    os.makedirs(self.statistics_dir, exist_ok=True)
  def add_detection(self, detection):
    assert isinstance(detection, Detector)
    self.detectors.append(detection)
  
  def add_processing(self, processor):
    assert isinstance(processor, Processor)
    self.processors.append(processor)
  
  def add_generator(self, generator):
    assert isinstance(generator, Generator)
    self.generators.append(generator)

  def execute_detection(self, image):
    results = []
    total = len(self.detectors)
    for i, detector in enumerate(self.detectors):
      results += detector.detect(image)
      progress((i+1)/float(total), prefix='Detection', suffix='{0}/{1}'.format(i+1,total))
    return results
  
  def execute_processors(self, elements):
    total = len(self.processors)    

    for i, processor in enumerate(self.processors):
      elements = processor.process(elements)
      progress((i+1)/float(total), prefix='Processing', suffix='{0}/{1}'.format(i+1,total))

    return elements

  def execute_code_generators(self, elements):
    total = len(self.generators)    

    for i, generator in enumerate(self.generators):
      generator.process(elements, self.out_folder)
      progress((i+1)/float(total), prefix='Generating', suffix='{0}/{1}'.format(i+1,total))
  
  def show_generator_results(self):
    for generator in self.generators:
      generator.show()
  
  def ommit_process(self, process, objects):
    self.ommit[process] = objects

  def debug_aux(self, image, elements, deep=0):
    for element in elements:
      pt1 = (int(element['x']), int(element['y']))
      pt2 = (int(element['w'] + pt1[0]), int(element['h'] + pt1[1]))
      color = (0,0,255)

      if element['class'] == 'Container':
        color = (255*(1-deep/5.0),255*deep/5.0,0)
        if element.__contains__('childs'):
          self.debug_aux(image, element['childs'], deep+1)

      cv.rectangle(image, pt1, pt2, color, 5)

  def debug(self,tag, image, elements):
    image2 = image.copy()
    self.debug_aux(image2, elements)
    cv.namedWindow(tag,cv.WINDOW_NORMAL)
    cv.imshow(tag, image2)
    cv.waitKey(1)

  def log_substats(self, lst, label):
    sub_stats_str = ''
    total_time = 0

    for item in lst:
      times = item.get_times()
      times_mean = sum(times)/len(times)
      name = type(item).__name__
      sub_stats_str += ('\t\t{0:>19}: {1:<12}\n'.format(name, self.colored_number(times_mean)))
      total_time += times_mean
    print('\t{0}: \t{1}\n{2}'.format(label, self.colored_number(total_time), sub_stats_str))
    return total_time
  
  def statsObject(self, lst, label):
    obj = {
      'name': label,
      'childs': [],
      'average': 0
    }

    total_time = 0

    for item in lst:
      times = item.get_times()
      times_mean = sum(times)/len(times)
      name = type(item).__name__
      total_time += times_mean
      obj['childs'].append(
        {
          'name': name,
          'times': times,
          'average': times_mean
        }
      )
    
    obj['average']=total_time
    return obj
  
  def colored_number(self, content):
    return '\033[92m{0:.4f}s\033[0m'.format(content)

  def log_stats(self):
    print('Statistics:', flush=True)
    total = 0

    total += self.log_substats(self.detectors, 'Detection')
    total += self.log_substats(self.processors, 'Processing')
    total += self.log_substats(self.generators, 'Generation')

    print('Total: {0}'.format(self.colored_number(total)), flush=True)
    self.store_statistics()

  def store_statistics(self):
    print('Storing Statistics')
    objs = []
    objs.append(self.statsObject(self.detectors, 'Detection'))
    objs.append(self.statsObject(self.processors, 'Processing'))
    objs.append(self.statsObject(self.generators, 'Generating'))

    store_path = os.path.join(self.statistics_dir, 'stats.pkl')
    with open(store_path, 'wb') as file:
      pickle.dump(objs, file)

  def execute(self, image):
    res = []

    if self.ommit.__contains__('detection'):
      res = self.ommit['detection']
    else:
      res = self.execute_detection(image)
    self.debug('Before', image, res)
    print('')
    #print(res)
    res = self.execute_processors(res)
    self.debug('After', image, res)
    cv.waitKey(1)
    print('')

    #print(res)
    self.execute_code_generators(res)
    print('\nFinished Processing Pipeline')

    self.log_stats()

def progress(percentage, width=50, prefix='', suffix='', fill='\033[92m#\033[0m', empty='-'):
  n_fill = int(width*percentage)
  t_fill = width-n_fill
  p = fill*n_fill + empty*t_fill

  print('\r{0} |{1}| {2}'.format(prefix, p, suffix), end='', flush=True)

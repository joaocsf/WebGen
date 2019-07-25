from .Processor import Processor
import os
import json

class ProcessorComponents(Processor):
  def __init__(self, orientation='v'):
    super().__init__()
    self.orientation = orientation
    self.components = [
      'Component', 'Expand'
    ]

  def on_process(self, root):
    container = root[0]
    self.orientation
    self.process_container(container)

    return [container]

  def process_container(self, container):
    if not container.__contains__('childs'):
      container['childs'] = []

    childs = container['childs']
    container['components'] = []
    end = False
    components = container['components']

    for child in childs[:]:
      if self.components.__contains__(child['class']):
        childs.remove(child)
        components.append(child)
      elif child['class'] == 'Container':
        self.process_container(child)

  def something_between(self, a, b, objs):
    minX = min(a['x'], b['x'])
    minY = min(a['y'], b['y'])
    maxX = max(a['x'] + a['w'], b['x'] + b['w'])
    maxY = max(a['y'] + a['h'], b['y'] + b['h'])

    a_shape = (minX, minY, maxX, maxY)

    for obj in objs:
      b_shape = (obj['x'], obj['y'], obj['x'] + obj['w'], obj['y'] + obj['h'])
      if obj == a or obj == b:
        continue
      if self.inside(a_shape, b_shape) > 0:
        return True
    
    return False

  def create_container(self, _type, objs, orientation='v'):
    minX = min(objs, key=lambda o: o['x'])
    minX = minX['x']
    minY = min(objs, key=lambda o: o['y'])
    minY = minY['y']
    maxW = max(objs, key=lambda o: o['x']+o['w'])
    maxW = maxW['x']+maxW['w']
    maxH = max(objs, key=lambda o: o['y']+o['h'])
    maxH = maxH['y']+maxH['h']

    root = {
        'class': 'Container',
        'type': _type,
        'orientation': orientation,
        'x':minX,
        'y':minY,
        'w': maxW - minX,
        'h': maxH - minY,
        'childs': objs
      }
    return root
  
  def get_mult_factor(self, width, thresh, divisor):
    v = thresh-width

    v/=divisor

    if v < 0:
      v = 0
    elif v > 1.0:
      v = 1.0
    return v

  def next_to_object(self, a, b):
    (a_w, a_h) = (a['w'], a['h'])
    (a_x,a_y) = (a['x'], a['y'])
    (a_xM, a_yM) = (a_x + a_w, a_y + a_h)


    if self.orientation == 'h':
      m = 1.0 #self.get_mult_factor(a_w, 50, 30)
      a_x -= a_w*m*2.5
      a_xM += a_w*m*2.5
      a_y += a_h*0.25
      a_yM -= a_h*0.25
      if a_x < 0: 
        a_x = 0

    else:
      m = 1.0 #self.get_mult_factor(a_h, 50, 30)
      a_x += a_w*0.2
      a_xM -= a_w*0.2
      a_y -= a_h*m*2.5
      a_yM += a_h*m*2.5
      if a_y < 0: 
        a_y = 0

    (b_x,b_y) = (b['x'], b['y'])
    (b_w, b_h) = (b['w'], b['h'])
    (b_xM, b_yM) = (b_x + b_w, b_y + b_h)

    a_shape = (a_x, a_y, a_xM, a_yM)
    b_shape = (b_x, b_y, b_xM, b_yM)

    inside = self.inside(a_shape, b_shape) > 0

    return inside

  def inside(self, a, b):
      x1m, y1m, x1M, y1M = a

      x2m, y2m, x2M, y2M = b

      x1 = max(x1m, x2m)
      y1 = max(y1m, y2m)
      x2 = min(x1M, x2M)
      y2 = min(y1M, y2M)

      width = (x2-x1)
      height = (y2-y1)
      if width < 0 or height < 0:
        return 0

      overlap = width*height
      area = (x1M - x1m) * (y1M - y1m)

      return overlap/area
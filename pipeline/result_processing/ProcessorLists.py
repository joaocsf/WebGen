from .Processor import Processor
import os
import json

class ProcessorLists(Processor):
  def __init__(self, orientation='v'):
    super().__init__()
    self.orientation = orientation

  def on_process(self, root):
    container = root[0]
    self.orientation
    self.process_container(container)

    return [container]

  def process_elements(self, element, others):
    elements = []
    elements.append(element)
    to_remove = []

    element_type = 'none' if not element.__contains__('type') else element['type']

    if self.orientation == 'v':
      others = sorted(others, key=lambda obj: (obj['y']))
    else:
      others = sorted(others, key=lambda obj: (obj['x']))

    for other in others[:]:
      if elements.__contains__(other) or other['class'] != element['class']:
        continue
      other_type = 'none' if not other.__contains__('type') else other['type']

      if element['class'] == 'Container' and other_type == 'none':
        continue

      if element['class'] == 'Container' and other_type != element_type:
        continue

      for e in elements:
        if self.next_to_object(e, other):
          if self.something_between(e, other, others):
            continue
          others.remove(other)
          elements.append(other)
          #to_remove.append(other)
          break

    #for r in to_remove:
      #others.remove(r)
    
    if self.orientation == 'v':
      elements = sorted(elements, key=lambda e: e['y'])
    else:
      elements = sorted(elements, key=lambda e: e['x'])
    
    result = [element]
    if len(elements) > 1:
      container = self.create_container(element['class'], elements, self.orientation)
      result = [container]
    
    return result, others

  def process_container(self, container):
    childs = container['childs']
    end = False
    childs2 = []

    for child in container['childs']:
      if child['class'] == 'Container':
        self.process_container(child)
    
    while childs: 
      child = childs[0]
      childs.pop(0)
      result, remaining = self.process_elements(child, childs)
      childs = remaining
      childs2 += result

    container['childs'] = childs2

  def something_between(self, a, b, objs):
    minX = min(a['x'], b['x'])
    minY = min(a['y'], b['y'])
    maxX = max(a['x'] + a['w'], b['x'] + b['w'])
    maxY = max(a['y'] + a['h'], b['y'] + b['h'])
    wX = (maxX - minX) * 0.1
    wY = (maxY - minY) * 0.1

    minX += wX 
    maxX -= wX
    minY += wY
    maxY -= wY

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
  
  def helper_bounds(self, a,b, w):
    return abs(a-b)/w

  def next_to_object(self, a, b):
    (a_w, a_h) = (a['w'], a['h'])
    (a_x,a_y) = (a['x'], a['y'])
    (a_xM, a_yM) = (a_x + a_w, a_y + a_h)

    (b_x,b_y) = (b['x'], b['y'])
    (b_w, b_h) = (b['w'], b['h'])
    (b_xM, b_yM) = (b_x + b_w, b_y + b_h)

    f_e = 2.5
    f_d = 0.25
      #Horizontal
    if self.orientation == 'h':

      if(self.helper_bounds(a_y, b_y, a_h) > 0.5
        or 
         self.helper_bounds(a_yM, b_yM, a_h) > 0.5):
        return False

      m = 2.0 #self.get_mult_factor(a_w, 50, 30)
      a_x -= a_w*m*f_e
      a_xM += a_w*m*f_e
      a_y += a_h*f_d
      a_yM -= a_h*f_d
      if a_x < 0: 
        a_x = 0

      #Vertical
    else:

      if(self.helper_bounds(a_x, b_x, a_w) > 0.5
        or 
         self.helper_bounds(a_xM, b_xM, a_w) > 0.5):
        return False

      m = 1.0 #self.get_mult_factor(a_h, 50, 30)
      a_x += a_w*f_d
      a_xM -= a_w*f_d
      a_y -= a_h*m*f_e
      a_yM += a_h*m*f_e
      if a_y < 0: 
        a_y = 0

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
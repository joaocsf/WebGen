from .Processor import Processor
import os
import json

class ProcessorSelector(Processor):
  

  def on_process(self, root):
    container = root[0]

    self.process_container(container)
    
    return [container]

  def process_container(self, container):
    selectors = []
    textblocks = []
    to_remove=[]

    childs = container['childs']
    childs = sorted(childs, key= lambda x: (x['x']))

    for index, child in enumerate(childs):
      if child['class'] == 'Container':
        self.process_container(child)

      elif child['class'] == 'RadioButton':
        selectors.append(index)

      elif child['class'] == 'Checkbox':
        selectors.append(index)
      
      elif child['class'] == 'TextBlock':
        textblocks.append(index)
      
    while selectors:
      selector = selectors[0]
      selectors.pop(0)
      for textblock in textblocks:
        a = childs[selector]
        b = childs[textblock]
        texts = [childs[i] for i in textblocks]
        if self.next_to_object(a, b) and not self.something_between(a,b, childs):
          textblocks.remove(textblock)

          objs = [a, b]
          if a['x'] > b['x']:
            objs = [b, a]

          h_container = self.create_horizontal_container(objs)
          container['childs'].append(h_container)
          to_remove.append(a)
          to_remove.append(b)
          break
    
    for r in to_remove:
      container['childs'].remove(r)

  def create_horizontal_container(self, objs):
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
        'type': 'Selector',
        'orientation': 'h',
        'x':minX,
        'y':minY,
        'w': maxW - minX,
        'h': maxH - minY,
        'childs': objs
      }
    return root

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
  
  def m_mult(self, value, minimum, maximum):
    delta = maximum-minimum
    v = value-minimum

    res = v/float(delta)
    if res < 0:
      res = 0
    elif res >= 1:
      res = 0
    res = 0

    return 1.0 - res

  def next_to_object(self, a, b):
    (a_w, a_h) = (a['w'], a['h'])
    (a_x,a_y) = (a['x'], a['y'])
    (a_xM, a_yM) = (a['x'] + a_w, a_y + a_h)

    a_x -= a_w * self.m_mult(a_w, 15, 70) * 8
    a_xM += a_w * self.m_mult(a_w, 15, 70) * 8

    (b_x,b_y) = (b['x'], b['y'])
    (b_w, b_h) = (b['w'], b['h'])
    (b_xM, b_yM) = (b_x + b_w, b_y + b_h)

    a_shape = (a_w, a_y, a_xM, a_yM)
    b_shape = (b_w, b_y, b_xM, b_yM)

    return self.inside(a_shape, b_shape) > 0

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
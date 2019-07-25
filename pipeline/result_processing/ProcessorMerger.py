from .Processor import Processor
import os
import json

class ProcessorMerger(Processor):
  def on_process(self, result):
    document = []
    containers = [x for x in result if x['class'] == 'Container']
    objects = [x for x in result if not x['class'] == 'Container']

    for container in containers:
      container['user'] = True

    for obj in objects:
      added = False 
      for container in containers[::]:
        percentage = self.inside(obj, container)

        if percentage > 0.5:

          if obj['w']*obj['h'] > container['w']*container['h']:
            containers.remove(container)
            continue

          else:
            container['childs'] = [] if not container.__contains__('childs') else container['childs']
            container['childs'].append(obj)
            added = True
            break
      
      if not added:
        document.append(obj)

    for c in containers:
      if not c.__contains__('childs') or len(c['childs']) == 0:
        continue
      document.append(c)
    
    return [self.get_root_object(document)]

  def get_root_object(self, objs):

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
        'x':minX,
        'y':minY,
        'w': maxW - minX,
        'h': maxH - minY,
        'childs': objs
      }
    return root

  def inside(self, obj, container):
    x1m = obj['x']
    y1m = obj['y']
    x1M = obj['x'] + obj['w']
    y1M = obj['y'] + obj['h']
    

    x2m = container['x']
    y2m = container['y']
    x2M = container['x'] + container['w']
    y2M = container['y'] + container['h']

    x1 = max(x1m, x2m)
    y1 = max(y1m, y2m)
    x2 = min(x1M, x2M)
    y2 = min(y1M, y2M)

    width = (x2-x1)
    height = (y2-y1)
    if width < 0 or height < 0:
      return 0

    overlap = width*height
    area = obj['w'] * obj['h']

    return overlap/area
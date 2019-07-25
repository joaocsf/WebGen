from .Processor import Processor
import os
import json

class ProcessorHierarchy(Processor):
  def __init__(self, orientation='v'):
    super().__init__()
    self.orientation = orientation
    self.box_offset = 10

  def on_process(self, root):
    container = root[0]
    self.containerTests = {}
    self.process_container(container, self.orientation)
    return [container]



  def process_container(self, container, orientation):
    # Ver filhos
    # Expandir em determinada seccao
    # Adicionar objetos que nao colidam a lista separada
    # Em caso de colisao, voltar a adicionar os elementos removidos/testa-los
    # Acaba quando nao existir mais elementos na lista original/copia
    # Se acabar com um grande grupo, adicionar 1 e testar noutra orientacao
    # Caso na outra orientacao continue, então marcar como GRID (Caso especial).
    # Caso apenas exista um objeto na lista não criar grupo, apenas adicionar-lo como está.

    current_orientation = orientation

    res = self.process_container_direction(container, current_orientation)

    final_orientation = current_orientation

    if len(res) == 1:
      current_orientation = self.get_oposite_direction(current_orientation)
      res = self.process_container_direction(container, current_orientation)
      final_orientation = current_orientation

      if len(res) == 1:
        final_orientation = 'grid'
        res = container['childs']

    oposite_orientation = self.get_oposite_direction(current_orientation)

    container['orientation'] = final_orientation
    container['childs'] = res
    for child in container['childs']:
      if not child['class'] == 'Container': 
        continue
      if child.__contains__('type') and child['type'] != '_h_':
        continue

      self.process_container(child, oposite_orientation)
  
  def process_container_direction(self, container, orientation):
    childs_to_test = container['childs'].copy()
    childs_to_test = self.sort_by_direction(childs_to_test, orientation)
    oposite_orientation = self.get_oposite_direction(orientation)

    final_list = []

    while len(childs_to_test) > 0:
      first = childs_to_test[0]
      childs_to_test.pop(0)
      elems = [first]
      box = self.get_bounding_box(first, container, oposite_orientation)

      for child in childs_to_test[:]:
        if not self.obj_inside_box(box, child):
          break
        elems.append(child)
        childs_to_test.remove(child)
        box = self.update_box(box, child, orientation)

      obj_to_list = elems[0]

      if (len(elems) > 1):
        obj_to_list = self.create_container('_h_', elems, oposite_orientation)
      
      final_list.append(obj_to_list)

    return final_list

  def sort_by_direction(self, lst, direction):
    if direction == 'h':
      return sorted(lst, key=lambda x: (x['x']))
    elif direction == 'v':
      return sorted(lst, key=lambda x: (x['y']))

  def get_oposite_direction(self, direction):
    return 'v' if direction == 'h' else 'h'

  def obj_inside_box(self, box, obj):
    obj_box = self.obj_bounds(obj)
    return self.inside(box, obj_box) > 0

  def update_box(self, box, new_obj, orientation):
    new_obj_box = self.obj_bounds(new_obj)  

    if orientation == 'h':
      box[0] = min(new_obj_box[0]+self.box_offset, box[0])
      box[2] = max(new_obj_box[2]-self.box_offset, box[2])
    else: 
      box[1] = min(new_obj_box[1]+self.box_offset, box[1])
      box[3] = max(new_obj_box[3]-self.box_offset, box[3])

    return box

  def get_bounding_box(self, obj, parent, orientation):
    obj_box = self.obj_bounds(obj)
    parent_box = self.obj_bounds(parent)

    obj_box[0] += self.box_offset
    obj_box[1] += self.box_offset
    obj_box[2] -= self.box_offset
    obj_box[3] -= self.box_offset

    if orientation == 'h':
      obj_box[0] = parent_box[0]
      obj_box[2] = parent_box[2]
    else: 
      obj_box[1] = parent_box[1]
      obj_box[3] = parent_box[3]

    return obj_box

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

  def obj_bounds(self, o):
    minX = o['x']
    minY = o['y']
    maxX = o['x'] + o['w']
    maxY = o['y'] + o['h']
    return [minX, minY, maxX, maxY]

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
    elements_inside = []
    elements_outside = []
    for obj in objs:
      b_shape = (obj['x'], obj['y'], obj['x'] + obj['w'], obj['y'] + obj['h'])
      if obj == a or obj == b:
        continue
      if self.inside(a_shape, b_shape) > 0:
        elements_inside.append(obj)
      else:
        elements_outside.append(obj)
    
    return len(elements_inside) > 0, elements_inside, elements_outside

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

      m = 2.0 #self.get_mult_factor(a_w, 50, 30)
      a_x -= a_w*m*f_e
      a_xM += a_w*m*f_e
      a_y += a_h*f_d
      a_yM -= a_h*f_d
      if a_x < 0: 
        a_x = 0

      #Vertical
    else:

      m = 2.0 #self.get_mult_factor(a_h, 50, 30)
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
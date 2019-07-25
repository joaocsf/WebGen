import os
import json
import argparse

def inside(obj, container):
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

def merge_obj(j):
  document = []

  containers = [x for x in j if x['class'] == 'Container']
  objects = [x for x in j if not x['class'] == 'Container']
  print(containers)

  for obj in objects:
    added = False 
    for container in containers:
      if inside(obj, container) > 0.8:
        container['childs'] = [] if not container.__contains__('childs') else container['childs']
        container['childs'].append(obj)
        added = True
        break
    
    if not added:
      document.append(obj)

  for c in containers:
    document.append(c)
  
  return document

def main():

  parser = argparse.ArgumentParser(description='Joins Elements from an JSON file')

  parser.add_argument('file')
  parser.add_argument('-o', dest='out', required=True)

  args = parser.parse_args()

  file = args.file
  outfile = args.out
  print('File' + file)

  with open(file) as f:
    j = json.load(f)

    document = merge_obj(j)
    
    with open(outfile, 'w') as f:
      f.write(json.dumps(document))


if __name__ == "__main__":
   main() 
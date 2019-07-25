import os
import sys
import numpy as np
import argparse
import cv2 as cv
import json
from pprint import pprint
import multiprocessing.dummy as mp

splitImages = False
store_everything = False
mustSplit = False
datasetDir = ''
outputDir = ''
relative2Output = False
classes = []
totalfiles = 0
currfile = 0
entries = []
prefix = "Parsing"
saveMask = False

def box2string(boxes):
  strboxes = []
  for box in boxes:
    value = "{0:0.0f},{1:0.0f},{2:0.0f},{3:0.0f},{4:0.0f}".format(
      box['xMin'],box['yMin'],box['xMax'],box['yMax'],box['classID'])
    strboxes.append(value)

  return strboxes

def lerpPX(a,b,px):
  x = b[0]-a[0]
  y = b[1]-a[1]
  return (px/x, px/y)


def lerp(a,b,t):
  x = a[0] + (b[0]-a[0])*t[0]
  y = a[1] + (b[1]-a[1])*t[1]
  return (int(x),int(y))


def remove_boxes(img, boxes, classes):

  # img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
  # img = ~img
  # img = cv.Canny(img,200,250)
  # img = ~img
  # img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
  # kernel = np.ones((5,5), np.uint8)
  # img = cv.erode(img, kernel, iterations=2) 

  for box in boxes:
    if(classes[box['classID']] == 'Container'):
      continue
    pt1 = (int(box['xMin']), int(box['yMin']))
    pt2 = (int(box['xMax']), int(box['yMax']))

    lerpValue = lerpPX(pt1, pt2, 5)
    p1 = lerp(pt1, pt2, lerpValue)
    p2 = lerp(pt1, pt2, (1-lerpValue[0], 1-lerpValue[1]))
    
    cv.rectangle(img, p1, p2, (255,255,255), thickness=-1)

  return img

def processFile(file):
  global mustSplit, datasetDir, outputDir, relative2Output, classes, totalfiles, currfile, entries, prefix, saveMask, store_everything

  currfile+=1
  print_progressbar(currfile/totalfiles, prefix=prefix, suffix=file )

  fileName = file.replace(".json","")
  imagePath =      os.path.join(datasetDir, "image/"  + fileName +".png")
  imageBoxesPath = os.path.join(datasetDir, "mask/"   + fileName +".png")
  jsonPath =       os.path.join(datasetDir, "annotation/" + file)

  if not os.path.isfile(imagePath) or not os.path.isfile(imageBoxesPath):
    print('\nFILE NOT FOUND' + imagePath)
    return

  annotationName = file

  boxes = []
  with open(jsonPath, 'r') as f:
    data = json.load(f)
    for elem in data:
      c = elem['class']
      x = elem['x']
      y = elem['y']
      w = elem['w']
      h = elem['h']
      classID = classes.index(c)
      xMax = float(x)+float(w)
      yMax = float(y)+float(h)

      if(x < 0): x = 0
      if(y < 0): y = 0
      
      boxes.append(
        {
          'xMin': x,
          'xMax': xMax,
          'yMin': y,
          'yMax': yMax,
          'classID': classID
        }
      )

  if not mustSplit:
    normalBoxes     = box2string( [ x for x in boxes if not classes[x['classID']] == 'Container'  ]  )
    containerBoxes  = box2string( [ x for x in boxes if     classes[x['classID']] == 'Container'  ]  )
    toImage = imagePath
    toImageBoxes = imageBoxesPath
    if(relative2Output):
      toImage = os.path.relpath(imagePath, outputDir)
      toImageBoxes = os.path.relpath(imageBoxesPath, outputDir)

    if not saveMask or store_everything:
      if store_everything:
        normalBoxes += containerBoxes
      entries.append(toImage + " " + ' '.join(normalBoxes))
    else:
      entries.append(toImageBoxes + " " + ' '.join(containerBoxes))

  else:
    toImage = imagePath
    toImageBoxes = imageBoxesPath
    if(relative2Output):
      toImage = os.path.relpath(imagePath, outputDir)
      toImageBoxes = os.path.relpath(imageBoxesPath, outputDir)

    entries.append(toImage + " " + toImageBoxes)
  # if mustSplit is None:
  #   t_path = imagePath
  #   if(relative2Output):
  #     t_path = os.path.relpath(imagePath, outputDir)

  #   entry = t_path + " " + ' '.join(box2string(boxes))
  #   entries.append(entry)
  # else:
  #   normal_dir     = os.path.join(splitDir, 'normal/')
  #   containers_dir = os.path.join(splitDir, 'containers/')

  #   img_normal_dir      = os.path.join(normal_dir     , fileName + ".png")
  #   img_containers_dir  = os.path.join(containers_dir , fileName + ".png")

  #   image = cv.imread(imagePath, cv.IMREAD_COLOR)

  #   cv.imwrite(img_normal_dir     , image)

  #   image = remove_boxes(image, boxes, classes)

  #   cv.imwrite(img_containers_dir , image)

  #   normalBoxes     = box2string( [ x for x in boxes if not classes[x['classID']] == 'Container'  ]  )
  #   containerBoxes  = box2string( [ x for x in boxes if     classes[x['classID']] == 'Container'  ]  )

  #   if(relative2Output):
  #     img_normal_dir = os.path.relpath(img_normal_dir, outputDir)
  #     img_containers_dir = os.path.relpath(img_containers_dir, outputDir)

  #   entries.append(img_normal_dir     + " " + ' '.join(normalBoxes))
  #   entries.append(img_containers_dir + " " + ' '.join(containerBoxes))


def parseFiles(_datasetDir, _outputDir, _relative2Output, _classes):
  global datasetDir, outputDir, relative2Output, classes, currfile, totalfiles, entries, mustSplit
  datasetDir = _datasetDir
  outputDir = _outputDir
  relative2Output = _relative2Output
  classes = _classes
  jsonDir = os.path.join(datasetDir, 'annotation/')
  print('JSON Directory:', jsonDir)
  print('Dataset Directory:', datasetDir)
  print('Output Directory:', outputDir)
  print('Relative to Output?', relative2Output)

  nfiles = int(len(os.listdir(jsonDir))/2)
  index = 1
  jsonfiles = []
  for file in os.listdir(jsonDir):
    if not file.endswith(".json"):
      continue
    jsonfiles.append(file)

    print_progressbar(index/nfiles, prefix='FindingJSON', suffix=file)
    index+=1


  totalfiles = len(jsonfiles)
  currfile = 0
  print('\n')
  
  prefix = "Parsing" if not mustSplit else 'Splitting'
  outfile = 'trainset' if not mustSplit else 'maskset'

  with open(os.path.join(outputDir, outfile), 'w') as fOut:
    p = mp.Pool(8)
    p.map(processFile, jsonfiles)
    p.close()
    p.join()
    fOut.write('\n'.join(entries)+'\n')

def print_progressbar(percentage, width=50, prefix='>', suffix='...'):
  filled = int(width*percentage)
  toFill = width-filled
  bar = '='*filled + '-'*toFill
  suffix += ' '*(20-len(suffix))
  
  print('\r{0} [{2}] {3:0.2f}% {1}'.format(prefix, suffix, bar, percentage), end='\r')

def createParser():
  parser = argparse.ArgumentParser(description='Generate Dataset Trainning Files')
  parser.add_argument(
    'input',
    help='Input folder',
  )
  parser.add_argument(
    '-o',
    dest='out',
    help='Output folder',
  )
  parser.add_argument(
    '-c',
    dest='classes',
    help='Classes',
  )
  parser.add_argument(
    '-s',
    dest='split',
    action='count',
    help='Split To Image-Mask',
  )
  parser.add_argument(
    '-m',
    dest='mask',
    action='count',
    help='Label Mask Only',
  )
  parser.add_argument(
    '-r',
    action='count',
    help="Relative To Output?"
  )
  parser.add_argument(
    '-e',
    dest='everything',
    action='store_true',
    help="Store Every Element Found"
  )

  return parser

def read_classes(classfile):
  print('Classes File:', classfile)
  classes = []

  with open(classfile, 'r') as f:
    classes = f.readlines()

  classes = [ x.replace('\n','') for x in classes]
  return classes

def execute():
  global mustSplit, saveMask, store_everything
  parser = createParser()
  args = parser.parse_args()

  relative_path = (not args.r is None) and args.r > 0
    
  if args.classes is None:
    print('-c is required')
    return
  
  out_path = './' if args.out is None else args.out

  classes = read_classes(args.classes)

  mustSplit = (not args.split is None) and args.split > 0
  saveMask = (not args.mask is None) and args.mask > 0
  store_everything = args.everything

  if len(classes) == 0:
    print('Classes Missing')
    return

  print('Classes:', classes)

  parseFiles(args.input, out_path, relative_path, classes)

if __name__ == "__main__":
  execute()
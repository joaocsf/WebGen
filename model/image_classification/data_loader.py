import os
import numpy as np
from PIL import Image

class DataLoader():

  def __init__(self, trainfile, validationfile, classes):
    self.trainlines = load_lines(trainfile)
    self.validationlines = load_lines(validationfile)
    self.classes = classes
  
  def load_batch(self, batch_size=1, image_shape=(128,128), validation_phase=False):
    lines = self.trainlines if not validation_phase else self.validationlines
    np.random.shuffle(lines)

    images = []
    labels = []
    for i in range(batch_size):
      line = lines[i]
      i = (i+1)%len(lines)

      imgs, lbls = self.image_data(line, image_shape)
      images += imgs
      labels += lbls

    return np.array(images), np.array(labels)
  
  def yield_batch2(self, batch_size=1, image_shape=(128,128), validation_phase=False):
    lines = self.trainlines if not validation_phase else self.validationlines
    np.random.shuffle(lines)

    self.n_batches = int(len(lines)/batch_size)

    index = 0

    for i in range(self.n_batches-1):
      images = []
      labels = []
      for b in range(batch_size):
        index = (index+1)%len(lines)
        line = lines[index]
        imgs, lbls = self.image_data(line, image_shape)
        images += imgs
        labels += lbls
      yield np.array(images), np.array(labels)

  def yield_batch(self, batch_size=1, image_shape=(128,128), validation_phase=False):
    lines = self.trainlines if not validation_phase else self.validationlines
    np.random.shuffle(lines)

    self.n_batches = int(len(lines)/batch_size)

    index = 0

    while True:

      for i in range(self.n_batches-1):
        images = []
        labels = []
        for b in range(batch_size):
          index = (index+1)%len(lines)
          line = lines[index]
          imgs, lbls = self.image_data(line, image_shape)
          images += imgs
          labels += lbls
        yield np.array(images), np.array(labels)

  def image_data(self, line, image_shape=(128,128)):
    data = line.split(' ')
    img_path = data[0]
    boxes = data[1::]
    images = []
    labels = []

    image = Image.open(img_path)
    image = image.convert('RGB')
    for box in boxes:
      data = box.split(',')
      data = [int(d) for d in data]
      x,y,xMax,yMax,class_id = data
      w = xMax-x
      h = yMax-y

      croped = image.crop((x,y,xMax,yMax))
      croped = croped.resize((image_shape[0], image_shape[1]), Image.ANTIALIAS)
      croped = np.array(croped, dtype='float32')
      croped /= 255.0
      #croped = np.expand_dims(croped, 0)

      images.append(croped)
      labels.append(self.get_classification(class_id))
    return images, labels



  def from_image(self, image, boxes, image_shape=(128,128)):
    images = []

    image = image.convert('RGB')
    image_width, image_height = image.size
    for box in boxes:
      data = box.split(',')
      data = [int(d) for d in data]
      x,y,xMax,yMax = data
      w = xMax-x
      h = yMax-y
      x = clamp(x-10, 0, image_width)
      y = clamp(y-10, 0, image_height)
      xMax = clamp(xMax + 10, 0, image_width)
      yMax = clamp(yMax + 10, 0, image_height)

      croped = image.crop((x,y,xMax,yMax))
      croped = croped.resize((image_shape[0], image_shape[1]), Image.ANTIALIAS)
      croped = np.array(croped, dtype='float32')
      croped /= 255.0

      images.append(croped)
    return np.array(images)

  def get_classification(self, class_id):
    res = [0]*len(self.classes)
    res[class_id] = 1.0
    return np.array(res)

def load_lines(file):
  if file is None: return []
  lines = []
  with open(file, 'r') as f:
    lines = f.readlines()
  return [line.replace('\n', '') for line in lines]

def clamp(value, min_val, max_val):
  return max(min(value, max_val), min_val)
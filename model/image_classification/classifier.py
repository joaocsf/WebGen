from keras.models import Sequential, Model
from keras.layers import Input, Dense, Reshape, Flatten, Dropout, Concatenate, Conv2D, MaxPooling2D, BatchNormalization
from keras.optimizers import Adam
from .data_loader import DataLoader
import os
import datetime
import numpy as np
import argparse
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import pickle

WORKING_DIR = os.path.dirname(__file__)

class Classifier():

  def __init__(self, trainfile, testfile, classesfile, image_shape=(128,128,3)):
    self.classes = load_classes(classesfile) 
    self.image_shape = image_shape

    self.output_history=os.path.join(WORKING_DIR, './results/history/')
    os.makedirs(self.output_history, exist_ok=True)

    self.data = DataLoader(trainfile, testfile, self.classes)

    self.model = self.get_model(self.image_shape, self.classes)
    self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    self.history = {}
    self.history['loss'] = []
    self.history['acc'] = []
    self.history['val_loss'] = []
    self.history['val_acc'] = []

    self.weights_path = os.path.join(WORKING_DIR, 'weights/')
    os.makedirs(self.weights_path, exist_ok=True)
    self.load()


  def get_model(self, image_shape, classes):
    model = Sequential()

    model.add(Conv2D(32, kernel_size=(3,3), activation='relu', input_shape=image_shape))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(BatchNormalization())

    model.add(Conv2D(64, kernel_size=(3,3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(BatchNormalization())

    model.add(Conv2D(64, kernel_size=(3,3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(BatchNormalization())

    model.add(Conv2D(96, kernel_size=(3,3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(BatchNormalization())

    model.add(Conv2D(32, kernel_size=(3,3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(BatchNormalization())
    model.add(Dropout(0.2))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(len(classes), activation='softmax'))
    return model

  def train(self, epochs=50, batch_size=10, save_freq=1000):
    
    start_time = datetime.datetime.now()
    for epoch in range(epochs):
      d_loss = []
      d_v_loss = []
      d_acc = []
      d_v_acc = []
      for batch, (images, labels) in enumerate(self.data.yield_batch2(batch_size, self.image_shape)):

        train_data = self.model.train_on_batch(images, labels)
        d_loss += [train_data[0]]
        d_acc += [train_data[1]]

        (t_images, t_labels) = self.data.load_batch(10, self.image_shape, validation_phase=True)
        test_data = self.model.test_on_batch(t_images, t_labels)
        d_v_loss += [test_data[0]]
        d_v_acc += [test_data[1]]

        acc = np.mean(d_acc)
        val_acc = np.mean(d_v_acc)
        loss = np.mean(d_loss)
        val_loss = np.mean(d_v_loss)
        _curr_batch = batch/float(self.data.n_batches)
        _curr_epoch = epoch/float(epochs)
        _curr = _curr_epoch + _curr_batch * 1.0/epochs
        
        
        remain_time = remaining_time(start_time, datetime.datetime.now(), _curr)
        print_progressbar(_curr, 
          prefix='[Epoch {0}/{1}][Batch {2}/{3}]'.format(epoch, epochs, batch, self.data.n_batches), 
          suffix='[Accuracy: {1:0.2f} | Val: {2:0.2f}] [Loss:{3:.3f} | Val: {4:.3f}] {0}'.format(remain_time, acc*100, val_acc*100, loss, val_loss))

        self.history['loss'] += [np.mean(d_loss)]
        self.history['val_loss'] += [np.mean(d_v_loss)]
        self.history['acc'] += [np.mean(d_acc)]
        self.history['val_acc'] += [np.mean(d_v_acc)]


        
        #if batch % save_freq == 0:
          #self.save(epoch, batch, acc, val_acc, loss, val_loss)

      # self.history['loss'] += [np.mean(d_loss)]
      # self.history['val_loss'] += [np.mean(d_v_loss)]
      # self.history['acc'] += [np.mean(d_acc)]
      # self.history['val_acc'] += [np.mean(d_v_acc)]


    
    self.store_history()
    plot_history_charts('Loss', self.history['loss'], self.history['val_loss'])
    plot_history_charts('Accuracy', self.history['acc'], self.history['val_acc'])
  
  def store_history(self):
    history_file = os.path.join(self.output_history, 'history.pkl')
    with open(history_file, 'wb') as f: 
      pickle.dump(self.history, f)

  def load_history(self):
    history_file = os.path.join(self.output_history, 'history.pkl')
    with open(history_file, 'rb') as f: 
      self.history = pickle.load(f)

  def label_to_class(self, label):
    mx = np.argmax(label)
    return self.classes[mx]

  def classify(self, image, boxes):
    images = self.data.from_image(image, boxes, self.image_shape)
    predictions = self.model.predict_on_batch(images)

    result = []
    for index, prediction in enumerate(predictions):
      label = self.label_to_class(prediction)
      result.append(label)
    return result

  def evaluate(self, batch_size=10):
    start_time = datetime.datetime.now()
    validation_labels = []
    predicted_labels = []
    for batch, (images, labels) in enumerate(self.data.yield_batch2(batch_size, self.image_shape, validation_phase=True)):
      _curr = batch/float(self.data.n_batches)

      predictions = self.model.predict_on_batch(images)

      for index, prediction in enumerate(predictions):
        validation_label = self.label_to_class(labels[index])
        predicted_label = self.label_to_class(prediction)
        validation_labels.append(validation_label)
        predicted_labels.append(predicted_label)

      remain_time = remaining_time(start_time, datetime.datetime.now(), _curr)
      print_progressbar(_curr, 
      prefix='[Batch {0}/{1}]'.format(batch, self.data.n_batches), suffix='{0}'.format(remain_time))
    
    plot_confusion_matrix(validation_labels, predicted_labels, self.classes)

  def save(self, epoch, batch, acc, val_acc, loss, val_loss):
    path = os.path.join(self.weights_path, 'ep{0}_{1}_weights_acc{2:.2f}-{3:.2f}_loss{4:.3f}-{5:.3f}.h5'.format(epoch, batch,acc*100,val_acc*100, loss, val_loss))
    self.model.save_weights(path)
    path = os.path.join(self.weights_path, 'weights.h5')
    self.model.save_weights(path)
  
  def load(self):
    path = os.path.join(self.weights_path, 'weights.h5')
    if os.path.isfile(path):
      self.model.load_weights(path)


def remaining_time(start, now, percentage):
  if percentage == 0:
    return now-start
  left_p = 1.0-percentage
  left = now-start
  left = left*left_p/percentage
  return left

def print_progressbar(percentage, width=50, prefix='>', suffix='...'):
  filled = int(width*percentage)
  toFill = width-filled
  bar = '='*filled + '-'*toFill
  suffix += ' '*(50-len(suffix))
  print('\r{0} [{2}] {3:0.2f}% {1}'.format(prefix, suffix, bar, percentage), end='', flush=True)

def load_classes(file):
  lines = []
  with open(file, 'r') as file:
    lines = file.readlines()
  
  lines = [line.replace('\n','') for line in lines]
  return lines

def arguments():
  parser =argparse.ArgumentParser('')
  parser.add_argument('-t', '--train')
  parser.add_argument('-v', '--validation')
  parser.add_argument('-c', '--classes')
  parser.add_argument('-e', '--evaluate', default=0, action='count')

  return parser.parse_args()

def plot_history_charts(title, data, val_data):
  l1, = plt.plot(data, label='Train')
  l2, = plt.plot(val_data, label="Validation")
  plt.ylabel(title)
  plt.legend(handles=[l1, l2])
  plt.show()

def plot_confusion_matrix(labels, predicted, classes, normalized=True):
  cm = confusion_matrix(labels, predicted, classes)
  fig, ax = plt.subplots()
  im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
  ax.figure.colorbar(im, ax=ax)
  ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes, yticklabels=classes,
        title='Confusion Matrix',
        xlabel='True',
        ylabel='Predicted')
  
  if normalized:
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

  plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
  fmt = '.2f' if normalized else 'd'
  thresh = cm.max()/2
  for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
      ax.text(j, i, format(cm[i, j], fmt),
              ha='center', va='center',
              color='white' if cm[i,j] > thresh else 'black')
  
  fig.tight_layout()
  plt.show()
  return ax

if __name__ == "__main__":
  args = arguments()
  classifier = Classifier(args.train, args.validation, args.classes)
  if args.evaluate < 1:
    classifier.train(1,1, save_freq=10)
  else:
    classifier.evaluate()
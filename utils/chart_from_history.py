import pickle
import argparse
import matplotlib.pyplot as plt
import numpy as np

selected = None
title = None

def read_file(file_path):
  history = load_history(file_path)  

  keys = []
  val_keys = []

  for key in history.keys():
    if 'val' in key:
      val_keys.append(key)
    else:
      keys.append(key)

  while True:
    if openDialog((keys, val_keys), history) == False:
      break

def selectFromList(lst, id=None):
  error = True

  if(id != None):
    return lst[id]

  for i, key in enumerate(lst): 
    print('\t{} {}'.format(i,key))
  
  while error:
    try:

      index = int(input('\tIndex:'))
      if(index < 0): return None
      return lst[index]
    except:
      pass
def openDialog(keys, history):
  global selected, title
  print('TrainData:')
  train = selectFromList(keys[0], selected)
  if train == None:
    return False
  
  print('ValidationData:')
  validation = selectFromList(keys[1], selected)
  if validation == None:
    return False

  title_1 = title if title != None else input('Title: ')
  print(title_1)
  plot_history_charts(title_1, history[train], history[validation])

  if(selected or title):
    return False

  return True

def moving_average(data, window):
  avg_mask = np.ones(window) / window
  return np.convolve(data, avg_mask, 'valid')

def plot_history_charts(title, data, val_data):
  l1, = plt.plot(data, label='Train', zorder=0, alpha=0.3)
  l2, = plt.plot(val_data, label="Validation", zorder=0, alpha=0.3)

  minimumY = np.min(data)
  minimumX = np.argmin(data)

  l3 = plt.scatter([minimumX], [minimumY], zorder=20, marker='x', c='tab:blue', label='Minimum {0:.2f}'.format(minimumY))

  minimumY = np.min(val_data)
  minimumX = np.argmin(val_data)
  l4 = plt.scatter([minimumX], [minimumY], zorder=20, marker='x', c='tab:orange', label='Minimum Val {0:.2f}'.format(minimumY))

  xx = range(0,len(data))
  window = 5
  ma = moving_average(data, window)
  l1, = plt.plot(xx[window-1:],ma[:], 'tab:blue', label='Train')
  ma = moving_average(val_data, window)
  l2, = plt.plot(xx[window-1:], ma[:], 'tab:orange', label='Validation')

  plt.ylabel('Loss')
  plt.yscale('log')
  plt.title(title)
  plt.legend(handles=[l3, l4, l1, l2])
  plt.savefig(title.replace(' ','') +'.pdf')
  #plt.show()

def load_history(file_path):
  obj = None
  with open(file_path, 'rb') as file:
    obj = pickle.load(file)

  return obj

def arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('file')
  parser.add_argument('-i', dest='index', default=None, type=int)
  parser.add_argument('-t', dest='title', default=None)

  return parser.parse_args()

def main():
  global selected, title
  args = arguments()
  selected = args.index
  title = args.title
  read_file(args.file)


if __name__ == "__main__":
    main()
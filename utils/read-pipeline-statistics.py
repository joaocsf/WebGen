import pickle
import argparse
import matplotlib.pyplot as plt
import os
out_path = './results'
import json
import numpy as np

def read_file(file_path):
  objs = load_history(file_path)  
  os.makedirs(out_path, exist_ok=True)

  total = []
  for obj in objs:
    tmp = makeChart(obj)
    print(len(tmp), flush=True)
    if len(total) == 0:
      total = tmp
    else:
      for i, t in enumerate(tmp):
        total[i] += t
  
  plot_history_charts('Time', [['',total, np.average(total)]], 'Total')


def makeChart(obj):
  chart_title = '{0} (Average: {1:.3f}s)'.format(obj['name'], obj['average'])

  data = []
  commulative = []
  for item in obj['childs']:
    name = item['name']
    times = item['times']
    average = item['average']
    if(len(commulative) == 0):
      commulative = times.copy()
    else:
      for index, time in enumerate(times):
        commulative[index] += time

    data.append([name,times, average])

  if len(obj['childs']) > 1:
    obj = ['Total', commulative, obj['average']]
    data = [obj] + data
  
  res = data[0][1]
  #data.append(['Total', commulative, obj['average']])

  plot_history_charts('Time', data, chart_title)

  store_string(chart_title, data)
  return res

def store_string(title, data):
  title = title.replace('(','').replace(')','').replace('_','').replace(':','').replace('.','-')
  path = os.path.join(out_path, '{0}.txt'.format(title))
  print(path)
  with open(path, 'w') as file:
    file.write(json.dumps(data))

def plot_history_charts(yLabel, data, title):

  handles = []
  for name, items, _ in data:
    l, = plt.plot(items, label=name)
    handles.append(l)

  plt.ylabel(yLabel)
  plt.legend(handles=handles)
  plt.title(title)
  #plt.xscale('log',basex=2)

  title = title.replace('(','').replace(')','').replace('_','').replace(':','').replace('.','-')
  path = os.path.join(out_path, '{0}.pdf'.format(title))
  plt.savefig(path)
  plt.show()

def load_history(file_path):
  obj = None
  with open(file_path, 'rb') as file:
    obj = pickle.load(file)

  return obj

def arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('file')
  parser.add_argument('-o', '--out', default='./results')

  return parser.parse_args()

def main():
  global out_path
  args = arguments()
  out_path = args.out
  read_file(args.file)

if __name__ == "__main__":
    main()
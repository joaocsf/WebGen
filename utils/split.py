import os
import argparse
import numpy as np
import pprint

def arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', dest='percentage', metavar='N', default=70)
  parser.add_argument('file')
  parser.add_argument('-t', '--train', default='train')
  parser.add_argument('-v', '--validation', default='validation')
  parser.add_argument('-r', '--randomize', action='count', default=0)

  return parser.parse_args()

def main():
  args = arguments()
  lines = []
  percentage = args.percentage/100.0
  with open(args.file, 'r') as file:
    lines = file.readlines()

  if args.randomize > 0:
    np.random.shuffle(lines)

  line_count = len(lines) 
  print('Total Lines', line_count)
  train_lines = int(line_count*percentage)
  print('Train Size', train_lines)
  print('Validation Size', line_count - train_lines)

  train = lines[:train_lines]
  validation = lines[train_lines:]
  print('Train Size', len(train))
  print('Validation Size', len(validation))

  write(args.train, train) 
  write(args.validation, validation) 

def write(name, lines):
  with open(name, 'w') as file:
    file.writelines(lines)

if __name__ == "__main__": 
  main()
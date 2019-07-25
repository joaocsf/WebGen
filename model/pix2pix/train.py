
import numpy as np
from pix2pix import Pix2Pix
import argparse
import os

WORKING_DIR = os.path.dirname(__file__)

DEFAULT_MODEL_PATH = os.path.join(WORKING_DIR, './weights')
DEFAULT_MODEL_PATH_OUT = os.path.join(WORKING_DIR, './out')

def arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', dest='validation')
  parser.add_argument('-t', dest='train')
  parser.add_argument('-history', dest='history', action='count', default=0)
  parser.add_argument('-m', dest='model', default=DEFAULT_MODEL_PATH, help="Folder to the weight files")
  parser.add_argument('-out', dest='out_model', default=DEFAULT_MODEL_PATH_OUT, help="Folder to store the output weight files")

  return parser.parse_args()

if __name__ == '__main__':
  args = arguments()
  gan = Pix2Pix(args.train, args.validation, args.model, args.out_model)

  if(args.history > 0):
    gan.load_history()
    gan.plot_history()
  gan.train(epochs=50, batch_size=2, sample_interval=25)
import time

class Generator:
  def __init__(self):
    self.times = []

  def process(self, elements, out_folder):
    start = time.time()
    res = self.on_process(elements, out_folder)
    end = time.time()
    self.times.append(end-start)
    return res

  def on_process(self, elements, out_folder):
    return 0
  
  def get_times(self):
    return self.times

  def show(self):
    pass
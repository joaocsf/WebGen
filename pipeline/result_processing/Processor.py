import time
class Processor():
  def __init__(self):
    self.times = []

  def process(self, result):
    start = time.time()
    res = self.on_process(result)
    end = time.time()
    self.times.append(end-start)
    return res
  
  def on_process(self, result):
    return 0

  def get_times(self):
    return self.times
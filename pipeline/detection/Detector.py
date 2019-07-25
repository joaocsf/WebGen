import time

class Detector:
  def __init__(self):
    self.on_create()
    self.times = []
  
  def on_create(self):
    pass
  
  def on_destroy(self):
    pass
  
  def detect(self, image):
    start = time.time()
    res = self.on_detect(image)
    end = time.time()
    self.times.append(end-start)
    return res
  
  def on_detect(self, image):
    return 0

  def get_times(self):
    return self.times
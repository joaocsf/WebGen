from .Generator import Generator
import os
import webbrowser

class GeneratorHTMLLists(Generator):
  def __init__(self):
    super().__init__()
    self.ignoreList = [
      'Component', 'Expand'
    ]

  def on_process(self, elements, out_folder):
    self.out_file = os.path.join(out_folder, 'html_generator_out/index.html')
    os.makedirs(os.path.dirname(self.out_file), exist_ok=True)
    #print('#######ELEMENTS', elements)
    generate_code(elements, self.out_file)
  
  def show(self):
    webbrowser.get('firefox').open(self.out_file)

main_grid_size = (8,12)
main_grid_subsize = 8
grid={}

randomID = 0
containerStack = []
ignoreList = [
  'Component', 'Expand'
]

def getHeader():
  return """
  <!doctype html>
  <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <!-- 
      <link rel="stylesheet" href="https://unpkg.com/picnic">
      -->
      <title>Hello, world!</title>
      <style>body > div.container{border: 2px none #000;} </style>
      <style>.container{ 
        display: flex;
        }
        .border{
          border: 2px dotted #000;
        }
        .user.border{
          border: 2px solid #F00;
        }
        .fixed-size {
          width: 100px;
          height: 100px;
        }
        button{
          height: 50px;
        }
        .column{
          flex-direction: column;
        }
        .row{
          flex-direction: row;
        }
        .img {
          background-image: url('https://picsum.photos/300/200?random=1');
          background-position: center;
          background-size: cover;
          display: block;
          max-width: 100%;
          max-height: 100%;
        }
      </style>
    </head>
    <body>
      <div class="container">
    """

def getElement(tag, attributes="", clss="", style="", content="", obj=None):
  attributes = " ".join(attributes)
  return '<{0} {1} class="{4}" style="{3}" > {2}</{0}>'.format(tag,attributes, content, style, clss)

def clamp(value, a, b):
  if value < a:
    return a
  elif value > b:
    return b
  return value

def getSpan(xMin, xMax, Value, span_width):
  b = xMax-xMin
  a = Value-xMin
  a = clamp(a, 0, b)
  span_width1 = span_width-1
  return clamp(int(a/b*span_width),1,99999)

def getElementSpanString(obj):
  return 'class="col-md-{0}"'.format(getElementSpan(obj))

def getElementSpan(obj):
  if obj == None: return ''
  container = containerStack[-1]
  xMin = container['x']
  xMax = xMin + container['w']

  span_width = container['grid-size']

  oXMin = obj['x']
  oXMax = oXMin + obj['w']
  s1 = getSpan(xMin,xMax, oXMin, span_width)
  s2 = getSpan(xMin,xMax, oXMax, span_width)

  span = s2-s1 + 1
  wC = container['w']
  wO = obj['w']
  
  print(span_width)
  return clamp( int(wO/wC * (span_width-1))+1, 1, span_width) 
  #return span

def closeBody():
  return '</div></body></html>\n'

def wIMG(o):
  global randomID
  randomID+=1
  #return getElement('div', clss="fixed-size", style='background-color: red;', obj=o)
  return getElement('div', ['class="img"'], style='background-image:url(https://picsum.photos/200/300?random={});'.format(randomID), obj=o)

def wTF(o):
  #return getElement('div', clss="fixed-size", style='background-color: cyan;', obj=o)
  return getElement('input', ['type="text"'], obj=o)

def wTB(o):
  #return getElement('div', clss="fixed-size", style='background-color: black;', obj=o)
  return getElement('p', content="Some Text.....", obj=o)

def wB(o):
  #return getElement('div', clss="fixed-size", style='background-color: blue;', obj=o)
  return getElement('Button', content="Button", obj=o)

def wCB(o):
  #return getElement('div', clss="fixed-size", style='background-color: green;', obj=o)
  return getElement('input', ['type="checkbox"'], obj=o)

def wE(o):
  #return getElement('div', clss="fixed-size", style='background-color: pink;', obj=o)
  return getElement('b', content='UNKNOWN {0}'.format(o['class']), obj=o)

def select_content(count):
  template = '<option value="{0}">{1} </option>'
  text = ''
  for i in range(count):
    text += template.format(i, 'Option {0}'.format(i))
  return text

def wD(o):
  #return getElement('div', clss="fixed-size", style='background-color: orange;', obj=o)
  return getElement('select', ['type="select"'], content=select_content(5), obj=o)

def wRB(o):
  #return getElement('div', clss="fixed-size", style='background-color: yellow;', obj=o)
  return getElement('input', ['type="radio"'], obj=o)

def beginContainer(o):
  vertical = o.__contains__('orientation') and o['orientation'] == 'v'
  user = 'user' if o.__contains__('user') else ''
  return """
    <div class="border container {0} {1}"
      style=" 
      ">
      """.format('column' if vertical else 'row', user)

def endContainer(o):
  return """
    </div>"""

def writeObj(file, obj):
  switch = {
    'Textfield': wTF,
    'Picture': wIMG,
    'Button': wB,
    'TextBlock': wTB,
    'Checkbox': wCB,
    'RadioButton': wRB,
    'Dropdown': wD,
  }
  #if(ignoreList.__contains__(obj['class'])):
  #  return

  option = wE
  if switch.__contains__(obj['class']):
    option = switch[obj['class']]

  file.write(option(obj))

def snap(value, base):
  return int(value/base)

def snapToGrid(objs, size=1):
  for obj in objs:
    x = obj['x']
    y = obj['y']
    xMax = x + obj['w']
    yMax = y + obj['h']
    x = snap(x, size)
    y = snap(y, size)
    xMax = snap(xMax, size)
    yMax = snap(yMax, size)
    obj['x'] = x
    obj['y'] = y
    obj['w'] = xMax - x
    obj['h'] = yMax - y


def parseContainer(file, objs):
  parent = containerStack[-1]
  snapToGrid(objs)
  #objs = sorted(objs, key=lambda obj: (obj['y'], obj['x']))
  #print([ [x['class'], x['x'], x['w']] for x in objs])
  for obj in objs:
    if obj['class'] == 'Container':
      file.write(beginContainer(obj))

      if obj.__contains__('childs'):

        containerStack.append(obj)
        parseContainer(file, obj['childs'])
        containerStack.pop()
        file.write(endContainer(obj))

    else:
      writeObj(file, obj)

def generate_code(objects, out_file):
  with open(out_file, 'w') as indexFile:
    indexFile.write(getHeader())
    containerStack.append(objects[0])
    objs = objects[0]['childs']
    # #print(objs)

    # maxW = max(objs, key=lambda o: o['x']+o['w'])
    # maxW = maxW['x']+maxW['w']
    # maxH = max(objs, key=lambda o: o['y']+o['h'])
    # maxH = maxH['y']+maxH['h']
    # containerStack.append(
    #   {
    #     'x':0,
    #     'y':0,
    #     'w': maxW,
    #     'h': maxH,
    #     'grid-size': main_grid_size
    #   }
    # )
    #snapToGrid(containerStack)
    parseContainer(indexFile, objs)
    indexFile.write(closeBody())
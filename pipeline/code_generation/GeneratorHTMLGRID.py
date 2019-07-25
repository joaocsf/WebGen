from .Generator import Generator
import os
import webbrowser
from shutil import copyfile

WORK_DIR = os.path.dirname(__file__)

class GeneratorHTMLGRID(Generator):
  def __init__(self, inputjs = None, inputcss = None, templatehtml = None):
    
    super().__init__()
    self.js_file = inputjs if not inputjs is None else os.path.join(WORK_DIR, './template/main.js')
    self.css_file = inputcss if not inputcss is None else os.path.join(WORK_DIR, './template/style.css')
    self.html_file = templatehtml if not templatehtml is None else os.path.join(WORK_DIR, './template/template.html')

    self.ignoreList = [
      'Component', 'Expand'
    ]

  def on_process(self, elements, out_folder):
    out_folder = os.path.join(out_folder, 'html_generator_out/')
    os.makedirs(os.path.dirname(out_folder), exist_ok=True)
    #print('#######ELEMENTS', elements)
    generate_code(elements, out_folder, self.html_file, self.css_file, self.js_file)
    self.out_file = os.path.join(out_folder, 'index.html')
  
  def show(self):
    webbrowser.get('firefox').open(self.out_file)

main_grid_size = (12,12)
main_grid_subsize = 8
grid={}

Lorem = "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"

randomID = 0
containerStack = []
ignoreList = [
  'Component', 'Expand'
]

def get_html(file):
  text = ""
  with open(file, 'r') as file:
    text = ''.join(file.readlines())
  return text

def getElement(tag, attributes="", clss="", style="", content="", obj=None):
  attributes = " ".join(attributes)
  return '<{0} {1} class="{4}" style="{3}" > {2}</{0}>'.format(tag,attributes, content, getElementSpanGridString(obj) + style, clss)

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

def getElementSpanGridString(obj):
  parent = containerStack[-1]
  if obj is None:
    return ''

  if (parent.__contains__('orientation')):
    if not parent['orientation'] is None:
      return ''
  grid = getElementGridPosition(obj)
  return """
      grid-column: {0}/{1} ;
      grid-row: {2}/{3} ;
  """.format(grid[0], grid[1], grid[2], grid[3])

def getElementGridPosition(obj):
  if obj == None: return [0,0,0,0]
  container = containerStack[-1]
  xMin = container['x']
  xMax = xMin + container['w']
  yMin = container['y']
  yMax = yMin + container['h']

  oXMin = obj['x']
  oXMax = oXMin + obj['w']
  oYMin = obj['y']
  oYMax = oYMin + obj['h']

  span_width, span_height = container['grid-size']

  xm = getSpan(xMin,xMax, oXMin, span_width)
  xM = getSpan(xMin,xMax, oXMax, span_width)
  ym = getSpan(yMin,yMax, oYMin, span_height)
  yM = getSpan(yMin,yMax, oYMax, span_height)

  return [xm, xM, ym, yM]

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

def wIMG(o):
  global randomID
  randomID+=1
  return getElement('div', clss='img z-depth-2', style='background-image:url(https://picsum.photos/{1}/{2}?random={0});'.format(randomID, o['w']*3, o['h']*3), obj=o)

def wTF(o):
  return getElement('input', ['placeholder="Inputfield"','type="text"'], obj=o)

def wTB(o):
  return getElement('p', content='...Text block...', obj=o)

def wB(o):
  return getElement('Button', content="Button", clss="btn", obj=o)

def wCB(o):
  checkbox = getElement('p', 
    content=
      getElement('label', 
      content=
        getElement('input', ['type="checkbox"'])
        +
        getElement('span')
    )
    ,
    obj=o)
  return checkbox

def wE(o):
  return getElement('b', content='UNKNOWN {0}'.format(o['class']), obj=o)

def select_content(count):
  template = '<option value="{0}">{1} </option>'
  text = ''
  for i in range(count):
    text += template.format(i, 'Option {0}'.format(i))
  return text

def wD(o):
  select = getElement('select', content=select_content(5))
  div = getElement('div', clss='input-field', content=select, obj=o)
  return div

def wRB(o):
  radio = getElement('p', 
    content=
      getElement('label', 
      content=
        getElement('input', ['type="radio"'])
        +
        getElement('span')
    )
    ,
    obj=o)
  return radio

def get_container_components(o):
  if not o.__contains__('components'): return []
  return [c['class'] for c in o['components']]

def get_container_string(o):
  span = getElementGridPosition(o)
  orientation = '' if not o.__contains__('orientation') else o['orientation']
  if orientation != '':
    orientation = 'row' if orientation == 'h' else 'column'

  components = get_container_components(o)
  dark_theme = 'blue-grey darken-1 dark' if components.__contains__('Component') else ''
  alt_css = 'alt-css' if components.__contains__('Expand') else ''

  is_card = 'card z-depth-2' if o.__contains__('user') else ''
  is_grid = 'grid' if orientation == '' else ''
  #style = 'grid-column: {0}/{1}; grid-row: {2}/{3};'.format(span[0], span[1], span[2], span[3])
  classes = 'container {0} {1} {2} {3} {4}'.format(is_grid, is_card, orientation, dark_theme, alt_css)
  return getElement('div', clss=classes, content='{0}', obj=o)

def get_obj_string(obj):
  switch = {
    'Textfield': wTF,
    'Picture': wIMG,
    'Button': wB,
    'TextBlock': wTB,
    'Checkbox': wCB,
    'RadioButton': wRB,
    'Dropdown': wD,
  }
  if(ignoreList.__contains__(obj['class'])):
    return

  option = wE
  if switch.__contains__(obj['class']):
    option = switch[obj['class']]

  return (option(obj))
  #file.write(option(obj))

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

def new_size(parent, obj):
  #w,h = (obj['w'], obj['h'])
  #pw,ph = (parent['w'], parent['h'])
  #gw,gh = parent['grid-size']
  return parent['grid-size']
  return (int(w/pw*gw), int(h/ph*gh))


def parseContainer(objs):
  parent = containerStack[-1]
  snapToGrid(objs)
  content = ""
  #objs = sorted(objs, key=lambda obj: (obj['y'], obj['x']))
  #print([ [x['class'], x['x'], x['w']] for x in objs])
  for obj in objs:
    if obj['class'] == 'Container':

      container_str = get_container_string(obj)
      container_content = ''

      if obj.__contains__('childs'):
        obj['grid-size'] = new_size(parent,obj)
        print(obj['grid-size'])
        containerStack.append(obj)
        container_content = parseContainer(obj['childs'])
        containerStack.pop()

      content += container_str.format(container_content)

    else:
      content += get_obj_string(obj)
  
  return content

def generate_code(objects, out_folder, html_file, css_file, js_file):
  objs = objects
  #print(objs)
  maxW = max(objs, key=lambda o: o['x']+o['w'])
  maxW = maxW['x']+maxW['w']
  maxH = max(objs, key=lambda o: o['y']+o['h'])
  maxH = maxH['y']+maxH['h']
  containerStack.append(
    {
      'x':0,
      'y':0,
      'w': maxW,
      'h': maxH,
      'grid-size': main_grid_size
    }
  )
  #snapToGrid(containerStack)
  content = parseContainer(objs)

  html_source = get_html(html_file).format(content)
  
  with open(os.path.join(out_folder, 'index.html'), 'w') as htmlFile:
    htmlFile.write(html_source)
  copyfile(css_file, os.path.join(out_folder, 'style.css'))
  copyfile(js_file, os.path.join(out_folder, 'main.js'))
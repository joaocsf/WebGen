from .Generator import Generator
import os
import webbrowser
from shutil import copyfile

WORK_DIR = os.path.dirname(__file__)

class GeneratorHTMLGRIDV2(Generator):
  def __init__(self, inputjs = None, inputcss = None, templatehtml = None):
    
    super().__init__()
    self.js_file = inputjs if not inputjs is None else os.path.join(WORK_DIR, './template/main.js')
    self.css_file = inputcss if not inputcss is None else os.path.join(WORK_DIR, './template/style.css')
    self.html_file = templatehtml if not templatehtml is None else os.path.join(WORK_DIR, './template/template.html')

    self.ignoreList = [
      'Component', 'Expand'
    ]

  def on_process(self, elements, out_folder):
    print(elements)
    out_folder = os.path.join(out_folder, 'html_generator_out/')
    os.makedirs(os.path.dirname(out_folder), exist_ok=True)
    #print('#######ELEMENTS', elements)
    generate_code(elements, out_folder, self.html_file, self.css_file, self.js_file)
    self.out_file = os.path.join(out_folder, 'index.html')
  
  def show(self):
    #webbrowser.get('firefox').open(self.out_file)
    pass

main_grid_size = (12,12)
grid_h_div = (12)
main_grid_subsize = 8
grid={}

size_w = 800

canvas_size = (0,0)
default_canvas_size=(800,900)

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

def get_flex_size(obj, parent):
  dimension = 'width: auto'
  s = int(obj['w']/parent['w'])*grid_h_div
  if parent['orientation'] == 'v':
    dimension = 'height: auto'
    s = int(obj['h']/parent['h'])*grid_h_div
  
  return 'flex-grow: {0}; {1};'.format(s, dimension)


def getElementSpanGridString(obj):
  parent = containerStack[-1]
  if obj is None:
    return ''

  if (parent.__contains__('orientation')):
    if not parent['orientation'] is None and not parent['orientation'] == 'grid':
      return ''
  grid = getElementGridPosition(obj)
  return """
      grid-column: {0}/{1} ;
      grid-row: {2}/{3} ;
  """.format(grid[0], grid[1], grid[2], grid[3])

def getElementGridPosition(obj):
  if obj == None: return [0,0,0,0]
  container = containerStack[-1]
  xMin = obj['sX']
  xMax = xMin + obj['sW']
  yMin = obj['sY']
  yMax = yMin + obj['sH']

  return [xMin, xMax, yMin, yMax]

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
  
  return clamp( int(wO/wC * (span_width-1))+1, 1, span_width) 
  #return span

def wIMG(o):
  global randomID, canvas_size, default_canvas_size
  randomID+=1
  
  xx = o['w']/canvas_size[0]
  xx = xx * default_canvas_size[0]
  xx = int(xx)

  yy = o['h']/canvas_size[1]
  yy = yy * default_canvas_size[1]
  yy = int(yy)

  return getElement('div', clss='img z-depth-2', style='background-image:url(https://picsum.photos/{1}/{2}?random={0}); min-height:{3}px;'.format(randomID, xx, yy, yy/2), obj=o)

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
  if orientation == 'h':
    orientation = 'row'
  elif orientation == 'v':
    orientation = 'column'

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

def snap2(value, width, divisions):
  value /= width
  value = clamp(value, 0, 1)
  value *= divisions
  return int(round(value))

def snapToGrid(objs, container, grid_size=1):
  container_x = container['x']
  container_y = container['y']
  container_w = container['w']
  container_h = container['h']

  grid_h_subdiv = grid_size
  size = container_w/grid_size
  grid_v_subdiv = container_h/size

  for obj in objs:
    x = obj['x'] - container_x
    y = obj['y'] - container_y
    xMax = x + obj['w']
    yMax = y + obj['h']
    x = snap2(x, container_w, grid_h_subdiv) + 1
    y = snap2(y, container_h, grid_v_subdiv) + 1
    xMax = snap2(xMax, container_w, grid_h_subdiv)
    yMax = snap2(yMax, container_h, grid_v_subdiv)

    obj['sX'] = x
    obj['sY'] = y
    obj['sW'] = xMax - x
    obj['sH'] = yMax - y
    #if obj['class'] == 'Container':
      #print('x', x, 'y', y, 'sW', xMax-x, 'sH', yMax - y)

def new_size(parent, obj):
  #w,h = (obj['w'], obj['h'])
  #pw,ph = (parent['w'], parent['h'])
  #gw,gh = parent['grid-size']
  return parent['grid-size']
  return (int(w/pw*gw), int(h/ph*gh))


def parseContainer(objs):
  parent = containerStack[-1]
  snapToGrid(objs, parent, grid_h_div)
  content = ""
  w = parent['w']
  h = parent['h']
  #objs = sorted(objs, key=lambda obj: (obj['y'], obj['x']))
  #print([ [x['class'], x['x'], x['w']] for x in objs])
  for obj in objs:
    if obj['class'] == 'Container':

      container_str = get_container_string(obj)
      container_content = ''

      if obj.__contains__('childs'):
        containerStack.append(obj)
        container_content = parseContainer(obj['childs'])
        containerStack.pop()

      content += container_str.format(container_content)

    else:
      content += get_obj_string(obj)
  
  return content

def generate_code(objects, out_folder, html_file, css_file, js_file):
  global canvas_size
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
  canvas_size = (objs[0]['w'], objs[0]['h'])
  #snapToGrid(containerStack)
  content = parseContainer(objs)

  html_source = get_html(html_file).format(content)
  
  with open(os.path.join(out_folder, 'index.html'), 'w') as htmlFile:
    htmlFile.write(html_source)
  copyfile(css_file, os.path.join(out_folder, 'style.css'))
  copyfile(js_file, os.path.join(out_folder, 'main.js'))
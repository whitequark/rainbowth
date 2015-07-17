import sublime, sublime_plugin, re, json, os

class Rainbowth(sublime_plugin.EventListener):
  def update_colors(self, view):
    cache_file_path = os.path.join(sublime.cache_path(), 'Rainbowth', 'Rainbowth' + '.cache')
    base_dir = sublime.packages_path()
    scheme_path = base_dir[:-8] + view.settings().get('color_scheme')
    scheme_name = scheme_path.split('/')[-1].split('.')[0]

    try:
      with open(cache_file_path, 'r') as cache_file:
        cache = json.load(cache_file)
    except (EnvironmentError, ValueError):
      cache = {}

    settings = sublime.load_settings('Rainbowth.sublime-settings')
    palettes = settings.get('palettes')
    self.colors = palettes.get(scheme_name, palettes['default'])
    if self.colors == cache.get(scheme_name, None):
      return

    with open(scheme_path, 'r') as scheme_file:
      scheme_xml = scheme_file.read()#.decode('utf-8')

    bg = re.search('background.+?g>(.+?)<', scheme_xml, re.DOTALL).group(1)
    bg = '#%06x' % max(1, (int(bg[1:], 16) - 1))
    fragment = '<dict><key>scope</key><string>rainbowth%d</string><key>settings</key><dict><key>background</key><string>' + bg + '</string><key>foreground</key><string>%s</string></dict></dict>'
    scheme_xml = re.sub('\t+<!-- rainbowth -->.+\n', '', scheme_xml)

    rainbowth = '\t<!-- rainbowth -->'
    for i, c in enumerate(self.colors):
      rainbowth += fragment % (i, c)

    scheme_xml = re.sub('</array>', rainbowth + '<!---->\n\t</array>', scheme_xml)
    with open(scheme_path, 'w') as scheme_file:
      scheme_file.write(scheme_xml)#.encode('utf-8'))
    cache[scheme_name] = self.colors

    cache_file_folder = os.path.split(cache_file_path)[0]
    if not os.path.exists(cache_file_folder):
      # ensure folder exists for cache file
      os.makedirs(cache_file_folder)

    with open(cache_file_path, 'w') as cache_file:
      json.dump(cache, cache_file)

  # plugins are not loaded properly after a hot exit
  # this causes problems with files opened automatically at boot
  def on_activated(self, view):
    if not view.settings().get('rainbowthed'):
      file_scope = view.scope_name(0)
      view.settings().set('lispy',
          file_scope.split('.')[1].split(' ')[0] in ['lisp', 'scheme', 'clojure', 'clojurescript'])
      if view.settings().get('lispy'):
        self.update_colors(view)
        self.on_modified(view, True)
        view.settings().set('rainbowthed', True)

  def on_modified(self, view, load = False):
    if not view.settings().get('lispy'):
      return

    source = view.substr(sublime.Region(0, view.size()))

    parens = [(sublime.Region(idx, idx + 1), char)
      for idx, char in enumerate(source[0:view.size()])
      if char in '()[]']

    level, depths = 0, [[sublime.Region(-1, 0)] for i in range(len(self.colors))]
    for region, char in parens:
      level += (char in '([') and -1 or 0
      depths[level % len(self.colors)].append(region)
      level += (char in ')]') and 1 or 0

    for i, regions in enumerate(depths):
      view.erase_regions('rainbowth%d' % i)
      view.add_regions('rainbowth%d' % i, regions, 'rainbowth%d' % i)

import sublime, sublime_plugin, re, json, os

class Rainbowth(sublime_plugin.EventListener):
    lispy_languages = ['lisp', 'scheme', 'clojure', 'clojurescript']

    cache_file_path = os.path.join(sublime.cache_path(), 'Rainbowth', 'Rainbowth.cache')
    if not os.path.exists(os.path.dirname(cache_file_path)):
        os.makedirs(os.path.dirname(cache_file_path))

    def __init__(self):
        self.cache = None

    def read_cache(self):
        if self.cache is None:
            if os.path.exists(self.cache_file_path):
                with open(self.cache_file_path, 'r') as cache_file:
                    self.cache = json.load(cache_file)
            else:
                self.cache = {}

    def write_cache(self):
        with open(self.cache_file_path, 'w') as cache_file:
            json.dump(self.cache, cache_file)

    def current_color_scheme(self, view):
        """Returns (absolute color scheme path, scheme name)."""
        scheme_relative_path = view.settings().get('color_scheme')
        scheme_name, _ = os.path.splitext(os.path.basename(scheme_relative_path))
        sublime_base_path = os.path.dirname(sublime.packages_path())
        scheme_path = os.path.join(sublime_base_path, scheme_relative_path)
        return scheme_path, scheme_name

    def colors_to_xml(self, colors):
        xml = []

        # bg = re.search('background.+?g>(.+?)<', scheme_xml, re.DOTALL).group(1)
        # bg = '#%06x' % max(1, (int(bg[1:], 16) - 1))

        for index, color in enumerate(colors):
            xml.append(
                '<dict>'
                    '<key>name</key><string>Rainbowth #{index}</string>'
                    '<key>scope</key><string>rainbowth{index}</string>'
                    '<key>settings</key><dict>'
                        '<key>foreground</key><string>{color}</string>'
                    '</dict>'
                '</dict>'.format(index=index, color=color))

        return "".join(xml)

    def update_color_scheme(self, view):
        scheme_path, scheme_name = self.current_color_scheme(view)

        settings = sublime.load_settings('Rainbowth.sublime-settings')
        palettes = settings.get('palettes')
        colors = palettes.get(scheme_name, palettes['default'])

        self.read_cache()
        if colors == self.cache.get(scheme_name, None):
            # Already updated.
            return colors

        # Not updated; do it!
        with open(scheme_path, 'r') as scheme_file:
            scheme_xml = scheme_file.read()

        # Cut out our old colors, if any.
        scheme_xml = re.sub('[ \t]+<!-- rainbowth -->.+\n', '', scheme_xml)

        # Insert our updated colors.
        rainbowth = '\t<!-- rainbowth -->{}<!-- /rainbowth -->'. \
                    format(self.colors_to_xml(colors))
        scheme_xml = re.sub('</array>', rainbowth + '\n\t</array>', scheme_xml)

        with open(scheme_path, 'w') as scheme_file:
            scheme_file.write(scheme_xml)

        self.cache[scheme_name] = colors
        self.write_cache()

        return colors

    def is_written_in(self, view, languages):
        scope_names = view.scope_name(0).split(' ')
        for language in ["source.{}".format(lang) for lang in languages]:
            if language in scope_names:
                return True
        return False

    def on_activated(self, view):
        view.settings().set('rainbowth.lispy', self.is_written_in(view, self.lispy_languages))
        if view.settings().get('rainbowth.lispy'):
            colors = self.update_color_scheme(view)
            view.settings().set('rainbowth.colors', colors)
            self.on_modified(view)

    def on_modified(self, view):
        if not view.settings().get('rainbowth.lispy'):
            return
        colors = view.settings().get('rainbowth.colors')

        level = -1
        depths = [[] for _ in range(len(colors))]
        for region in view.find_all('[\[\]()]'):
            char = view.substr(region)
            if char in '([': level += 1
            depths[level % len(colors)].append(region)
            if char in ')]': level -= 1

        for index, regions in enumerate(depths):
            key = 'rainbowth{}'.format(index)
            view.erase_regions(key)
            view.add_regions(key, regions, scope='rainbowth{}'.format(index))

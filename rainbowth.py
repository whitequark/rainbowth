import sublime, sublime_plugin, re, json, os, codecs
from collections import defaultdict

class ViewInfo:
    def __init__(self, color_count, per_line_depths):
        self.keys = ['rainbowth{}'.format(index) for index in range(color_count)]
        self.keys_lineHighlight = [scope + '-lineHighlight' for scope in self.keys]
        self.per_line_depths = per_line_depths

        self.prepared_regions = {}
        for key in self.keys + self.keys_lineHighlight:
            self.prepared_regions[key] = []

        for line in self.per_line_depths:
            depths = self.per_line_depths[line]
            for depth, regions in enumerate(depths):
                self.prepared_regions[self.keys[depth]] += regions

    def update(self, old_highlighted_line, new_highlighted_line):
        # Sublime does not permit us to set foreground color of a region
        # without simultaneously filling its background, so we do this
        # gross workaround: paint the background to the color it would have
        # been otherwise. Since selection erases foreground colors of regions
        # as well, we do this only for regular and current line backgrounds.

        if old_highlighted_line is not None:
            depths = self.per_line_depths[old_highlighted_line]
            for depth, regions in enumerate(depths):
                visible_regions = self.prepared_regions[self.keys_lineHighlight[depth]]
                for region in regions:
                    visible_regions.remove(region)
                self.prepared_regions[self.keys[depth]] += regions

        if new_highlighted_line is not None:
            depths = self.per_line_depths[new_highlighted_line]
            for depth, regions in enumerate(depths):
                visible_regions = self.prepared_regions[self.keys[depth]]
                for region in regions:
                    if region in visible_regions: # FIXME: should be always true
                        visible_regions.remove(region)
                self.prepared_regions[self.keys_lineHighlight[depth]] += regions

    def highlight(self, view):
        for key in self.prepared_regions:
            view.erase_regions(key)
            view.add_regions(key, self.prepared_regions[key],
                             scope=key, flags=sublime.DRAW_NO_OUTLINE)

class Rainbowth(sublime_plugin.EventListener):
    @staticmethod
    def cache_file_path():
        result = os.path.join(sublime.cache_path(), 'Rainbowth', 'Rainbowth.cache')
        if not os.path.exists(os.path.dirname(result)):
            os.makedirs(os.path.dirname(result))
        return result

    def __init__(self):
        self.cache = None
        self.view_infos = {}

    def read_cache(self):
        if self.cache is None:
            if os.path.exists(self.cache_file_path()):
                with codecs.open(self.cache_file_path(), 'r', 'utf-8') as cache_file:
                    self.cache = json.load(cache_file)
            else:
                self.cache = {}

    def write_cache(self):
        with codecs.open(self.cache_file_path(), 'w', 'utf-8') as cache_file:
            json.dump(self.cache, cache_file)

    def current_color_scheme(self, view):
        """Returns (absolute color scheme path, scheme name)."""
        scheme_relative_path = view.settings().get('color_scheme')
        scheme_name, _ = os.path.splitext(os.path.basename(scheme_relative_path))
        sublime_base_path = os.path.dirname(sublime.packages_path())
        scheme_path = os.path.join(sublime_base_path, scheme_relative_path)
        return scheme_path, scheme_name

    def perturb_color(self, color):
        """
        Apply a minimal change to `color`, which must be in CSS hex format,
        and return the modified color.
        """
        if color[0] == '#' and len(color) in (4, 7, 9):
            # Normalize to 8-digit hex.
            color = re.sub('^#(.)(.)(.)$', r'#\1\1\2\2\3\3', color)
            color = re.sub('^#(......)$',  r'#\1ff', color)

            # Perturb.
            color_value = int(color[1:], base=16)
            if color_value & 0xff00 == 0xff00:
                color_value -= 0x100
            else:
                color_value += 0x100
            color = "#{:08x}".format(color_value)

        return color

    def get_setting(self, scheme_xml, setting):
        # This is an awful hack, but even with a full-blown XML parser,
        # parsing .tmTheme files is painful. Feel free to send a PR.
        settings = re.search('<key>settings</key>\s*<dict>(.+?)</dict>',
                             scheme_xml, flags=re.DOTALL).group(1)
        value    = re.search('<key>{}</key>\s*<string>(.+?)</string>'.format(setting),
                             settings, flags=re.DOTALL).group(1)
        return value

    def colors_to_xml(self, colors, background, lineHighlight):
        xml = []

        # If we don't perturb the background color, ST treats it as absent
        # and refuses to change foreground color of the letters either.
        # Instead, it uses the foreground color to draw the outline and fill.
        background = self.perturb_color(background)

        for index, color in enumerate(colors):
            xml.append(
                '<dict>'
                    '<key>scope</key><string>rainbowth{index}</string>'
                    '<key>settings</key><dict>'
                        '<key>foreground</key><string>{foreground}</string>'
                        '<key>background</key><string>{background}</string>'
                    '</dict>'
                '</dict>'
                '<dict>'
                    '<key>scope</key><string>rainbowth{index}-lineHighlight</string>'
                    '<key>settings</key><dict>'
                        '<key>foreground</key><string>{foreground}</string>'
                        '<key>background</key><string>{lineHighlight}</string>'
                    '</dict>'
                '</dict>'
                .format(index=index, foreground=color,
                        background=background, lineHighlight=lineHighlight))

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

        print("Rainbowth: color scheme needs updating")

        # Not updated; do it!
        with codecs.open(scheme_path, 'r', 'utf-8') as scheme_file:
            scheme_xml = scheme_file.read()

        background = self.get_setting(scheme_xml, 'background')
        lineHighlight = self.get_setting(scheme_xml, 'lineHighlight')

        # Cut out our old colors, if any.
        scheme_xml = re.sub('[ \t]+<!-- rainbowth -->.+\n', '', scheme_xml)

        # Insert our updated colors.
        rainbowth = '\t<!-- rainbowth -->{}<!-- /rainbowth -->'. \
                    format(self.colors_to_xml(colors, background, lineHighlight))
        scheme_xml = re.sub('</array>', rainbowth + '\n\t</array>', scheme_xml)

        with codecs.open(scheme_path, 'w', 'utf-8') as scheme_file:
            scheme_file.write(scheme_xml)

        self.cache[scheme_name] = colors
        self.write_cache()

        return colors

    def is_written_in(self, view, languages):
        scope_names = view.scope_name(0).split(' ')
        for language in [scope.format(lang) for lang in languages 
                         for scope in ["source.{}", "text.{}", "text.tex.{}"]]:
            if language in scope_names:
                return True
        return False

    def on_activated_async(self, view):
        settings = sublime.load_settings('Rainbowth.sublime-settings')
        languages = settings.get('languages')
        lispy = self.is_written_in(view, languages)
        if settings.get('exclude_languages'):
            lispy = not lispy
        view.settings().set('rainbowth.lispy', lispy)
        if view.settings().get('rainbowth.lispy'):
            colors = self.update_color_scheme(view)
            view.settings().set('rainbowth.colors', colors)
            self.on_modified_async(view)

    def on_modified_async(self, view):
        if not view.settings().get('rainbowth.lispy'):
            return
        colors = view.settings().get('rainbowth.colors')

        settings = sublime.load_settings('Rainbowth.sublime-settings')
        customSigns = settings.get('custom_signs')

        if customSigns['enabled']:
          prefix = customSigns['prefix'] 
          suffix = customSigns['suffix']
        else:
          prefix = '(['
          suffix = ')]'

        disableString = settings.get('disable_inside_string')
        disableComment = settings.get('disable_inside_comment')
        regex = '['+re.escape(prefix) + re.escape(suffix)+']'

        badRegions = []
        if(disableComment):
            badRegions.extend(view.find_by_selector("comment"))
        if(disableString):
            badRegions.extend(view.find_by_selector("string"))

        level = -1
        per_line_depths = defaultdict(lambda: [[] for _ in range(len(colors))])
        for region in view.find_all(regex):
            skip = False
            for badRegion in badRegions:
                if badRegion.contains(region):
                    skip = True
                if badRegion.contains(region):
                    skip = True

            if not skip:
                char = view.substr(region)
                line, _ = view.rowcol(region.a)
                if char in prefix: level += 1
                per_line_depths[line][level % len(colors)].append(region)
                if char in suffix: level -= 1

        self.view_infos[view.id()] = ViewInfo(len(colors), per_line_depths)
        view.settings().set('rainbowth.line', None)
        self.on_selection_modified(view)

    def on_close(self, view):
        if not view.settings().get('rainbowth.lispy'):
            return

        del self.view_infos[view.id()]

    def on_selection_modified(self, view):
        if not view.settings().get('rainbowth.lispy'):
            return
        colors = view.settings().get('rainbowth.colors')

        if not view.id() in self.view_infos:
            return

        if len(view.sel()) == 1 and view.sel()[0].a == view.sel()[0].b:
            highlighted_line, _ = view.rowcol(view.sel()[0].a)
        else:
            highlighted_line = None

        old_highlighted_line = int(view.settings().get('rainbowth.line') or "-1")
        if old_highlighted_line == highlighted_line:
            return
        view.settings().set('rainbowth.line', highlighted_line)

        view_info = self.view_infos[view.id()]
        view_info.update(old_highlighted_line, highlighted_line)
        view_info.highlight(view)

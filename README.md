Rainbowth
=========

### What is this?

Rainbowth is a Sublime Text 3 plugin that automagically highlights matching parentheses, brackets, and curly braces in source code. While the name does imply a certain sequence of colors, the palette used to paint them is entirely configurable; nonetheless, the effect is perhaps best demonstrated when viewed with a theme like [Tomorrow Night](https://github.com/chriskempson/tomorrow-theme/tree/master/textmate):

![img](http://i.imgur.com/ja50Z.png)

### Why?

It took about three hours for Racket to grow on me. I know with a fair amount of certainty that I'd like to master it, but the structure is going to take some getting used to. This plugin attempts to overcome one of the primary barriers to entry, that of not being able to tell what's related beyond the matching of a single parenthetical pair.

### Installation

Install Rainbowth via [Package Control](https://packagecontrol.io/packages/Rainbowth), or clone this repository directly into your Packages directory.

### Setup

The color scheme must be unpacked in the user's `Packages` folder and writable for Rainbowth to be able to automatically insert its palette.

The default themes can be located in the `Color Scheme - Default.sublime-package` (or `Color Scheme - Legacy.sublime-package` on newer Sublime Text installations) file in the Sublime Text installation folder. Use a zip archive manager to extract the `.tmTheme` file corresponding to the theme you like. There is currently no support for the new `.sublime-color-scheme` file format.

* [Step-by-step setup instructions](Setup-Instructions.md)

### Configuration

Rainbowth's default configuration can be customized by creating a `Rainbowth.sublime-settings` file in `Packages/User`. 

The `palettes` setting is a mapping of theme names to the list of colors to use for painting parentheses while using that theme, outermost first. When using a theme not specified, the default ROYGBIV sequence will be used.

```
{
  "palettes": {
    "default": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
  }
}
```

Highlighting for a given language can be enabled (or disabled) by updating the `languages` setting.

```
{
  "languages": ["lisp", "scheme", "clojure", "clojurescript", "hylang"]
}
```

### Contributing

Comments, criticisms, and code are all eagerly welcomed.

# Adjustkeys

![An example adjustcaps layout in blender](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/slanted-layout-60.png)
![An example adjustglyphs layout in blender](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/100-layout.png)

This is a [python][python] script which generates layouts of keycaps and glyphs for (automatic) import into [Blender!][blender]
Gone will be the days of manually placing caps into the correct locations and spending hours fixing alignment problems of glyphs on individual keys—simply specify the layout you want using the JSON output of [KLE][kle] to have the computer guide the caps into the mathematically-correct locations.

This script can be used to create a _single source of truth_ for glyph alignment on caps and—as an added bonus—colourway-config, so later changes and fixes can be more easily propagated.

Please note that for the steps below, default configuration files are provided (and obtained through the zip on the [releases page][releases]), so the annoying in-the-dark stage of getting the thing working for the first time should be largely avoided.
Configuration can optionally be saved and read from a file.

The [python][python] API of `adjustkeys` also allows a coder to be notified of the objects it creates, thereby allowing it to form part of a larger keyboard-render build-system, should the user be that-way inclined.

## Table of Contents

<!-- vim-markdown-toc GFM -->

* [Why Bother?](#why-bother)
* [Usage](#usage)
	* [Usage Through a Blender Addon (Regular difficulty)](#usage-through-a-blender-addon-regular-difficulty)
	* [Usage Through Other Scripts (Masochist difficulty)](#usage-through-other-scripts-masochist-difficulty)
	* [Uninstalling](#uninstalling)
* [Custom Setup](#custom-setup)
	* [Using a custom layout](#using-a-custom-layout)
	* [Changing keycap profiles](#changing-keycap-profiles)
	* [Using custom glyphs / fonts](#using-custom-glyphs--fonts)
	* [Setting colours (via KLE or name-matching)](#setting-colours-via-kle-or-name-matching)
* [Pitfalls](#pitfalls)
	* [Missing keycap models due to incorrect key profile](#missing-keycap-models-due-to-incorrect-key-profile)
	* [Deactivation colours](#deactivation-colours)
* [Building from Source](#building-from-source)
* [Contributing](#contributing)
* [Gripes](#gripes)
* [Author and Acknowledgements](#author-and-acknowledgements)

<!-- vim-markdown-toc -->

## Why Bother?

Alignment is important.
Whereas good alignment can lend your set a kind of refined perfection, bad alignment can unnecessarily draw the eye and distract from the rest of your hard work.
The only problem is that to perfect alignment requires a non-negligable amount of effort to be spent on each key—it’s not as simple as just putting the glyph in the centre by how the computer sees it:

![An explanation for why computers aren’t natively good at aligning characters](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/alignment-reasoning.png)

Without an in-depth study into emulation of the human eye, the best way to align glyphs is to use your own, but to do this for each time a glyph and keycap appears in every layout/kit would be extremely time-consuming, especially if one were to find something later which would require fixing very early-on in the process.
Therefore, `adjustkeys` exists—to help banish the duplication of tedious alignment work from the task of preparing renders for ICs and GBs, allowing its’ users to focus on the more fun bits of rendering, like watching your set come to life.

## Usage

You’ll need a working installation of [Blender][blender] (v2.82+ or v2.90+ work) and a little familiarity with the [yaml][yaml-intro] syntax (although this can be picked up as it’s designed to be relatively human-friendly).
There’s two ways of interacting with `adjustkeys`, either through the Blender extension or through Python, both are explained here.

**Important**: currently, you need to be able to view the console output for certain features of `adjustkeys`, which can be done as follows depending on your operating system.

- Windows:
	1. Open blender as usual
	2. Go to _Window > Toggle System Console_
- Linux:
	1. Open up a terminal
	2. Enter `blender`
- MacOS:
	1. Read and do [Blender’s very quick guide on how to get `blender` into your path][blender-path-guide] if step 2 doesn’t work.
	2. Enter `blender` at the terminal

Regardless of how you choose to use `adjustkeys`, you’ll need a text editor to edit the configuration files.
Notepad or Blender’s editor work okay, but they don’t have syntax highlighting (which makes things _much_ easier).
If you’re new around text-editors, I’d recommend [VSCodium][codium], a minimalistic editor which is just Microsoft’s excellent VSCode compiled from the source and hence without the snooping nonsense present in the canonical closed-source binary.

### Usage Through a Blender Addon (Regular difficulty)

You’ll need a working installation of Blender.

1. Go to the [releases page][releases] and download `adjust-keys-blender-addon.zip`
2. Install the addon by going to _Edit > Preferences > Add-ons > Install,_ and install the zip you just downloaded and activate the plugin (tick the tick-box)
	- (Optional) If it doesn’t already appear, you may need to search the preferences window for `Adjustkeys`.
3. Go to _Properties > Scene Properties > Adjustkeys_ to see the menu
4. Press _place caps and glyphs_
5. Wait a moment, et voilà!

See the [custom setup section](#custom-setup) for how to change the stock settings into your own keycap set.

### Usage Through Other Scripts (Masochist difficulty)

If you want to use `adjustkeys` through another python script for the purpose of automating something a script:

1. Go to the [releases page][releases], download `adjust-keys.zip` and unzip it so that the `adjustkeys-bin` binary somewhere you won’t accidentally delete it
	- If you want to automate the process (e.g. through `git submodule`), running `make -C /path/to/adjust-keys/ devel` will make a binary and necessary data files
2. Copy the path where `adjustkeys` now is (I have mine in `/home/kcza/Documents/keys/adjustkeys-bin`)
3. In your existing Python script add the following lines, appropriately substituting the path from the previous step:

```python
from sys import path
path.append('/path/to/adjustkeys-bin')
from adjustkeys import main as adjustkeys
```

4. Now, you can call `adjustkeys` as necessary from your script.
   The function takes input of either an (arbitrarily-nested) list of strings corresponding to command-line arguments, or a dictionary corresponding to the yaml arguments.
   Both are equally expressive but dictionaries are the more standard way of passing data of the two.
   The function returns a dictionary containing the names of the objects created during that run, and the number of warnings triggered.

A complete python example is below.

```python
from sys import path
path.append('./adjustkeys-bin')
from adjustkeys import main as adjustkeys

adjustkeys_args:dict = {
		'glyph_dir': './my-super-cool-glyphs/',
		'layout_row_profiles_file': 'examples/layout_row_profiles-60.yml',
		'layout_file': './my-exotic-layout.json'
	}
inf:dict = adjustkeys(adjustkeys_args)
```

Assuming that the `my-super-cool-glyphs` folder is full of (super cool) glyphs, that the `adjustkeys.zip` has been extracted into the same folder as the script above (hence `examples/` is next to it) and that `my-exotic-layout.json` exists and contains a valid [KLE][kle] layout.

### Uninstalling

You should be able to uninstall through the usual Blender UI, that is, _Edit > Preferences > Add-ons > Adjustkeys > Remove,_ but in some cases this may not work some python binary files can get marked as read-only during the installation process, and Blender’s delete function doesn’t force-delete to override this condition.
As a result, if the ‘remove’ button doesn’t work you may need to do the following:

1. Close Blender
2. Go to the directory where extensions are installed, for a standard setup, this will probably be of the form:
	- **Windows**: `C:\\Users\\<username>\\AppData\\Roaming\\Blender Foundation\\Blender\\2.XX\\scripts\\addons\\`
	- **macOS**: `/Users/<username>/Library/Application Support/Blender/2.XX/scripts/addons/`
	- **Linux**: `~/.config/blender/2.XX/scripts/addons/`
3. Delete the `adjust_keys_blender_addon` folder

There are no configuration files or python dependencies located outside of this folder, so after step 3, your Blender installation will be completely free of any `adjustkeys` related material.

## Custom Setup

It’s a fair assumption that the user will not be contented with just re-making the examples all day—they should probably want to do something cool themselves.
There are a few important files which are combined to make the layout you see before you; it’s important that the user has some notion of what each does and what they should look like as otherwise `adjustkeys` won’t be able to work.
There’s not too much to each, but some understanding should help avoid errors.

They’ll be explained in this section, but as an overview, `adjustkeys` takes:

- A directory containing `.obj` files each containing an individual keycap
- A directory containing the glyphs to be placed, each in a separate `.svg` file
- A `yaml` (or equivalently `json`) file containing the layout exported from [KLE][kle]
- A `yaml` file which specifies the location of the centre of a key in a particular profile
- A `yaml` file which specifies a mapping from key names to glyph names

### Using a custom layout

This is probably the easy bit—just head on over to [KLE,][kle] configure a layout (a grid-like one like a standard 104 key ANSI layout will do, angling isn’t explicitly supported just yet) then click the _Download > Download JSON._
It’s important to note that [KLE][kle] interactive editor **doesn’t use JSON, it’s just JSON-like**, so simply copy-pasting might not work.

Here’s the first few lines of a valid file as an example:

```json
[
  [
    "Esc",
    {
      "x": 1
    },
    "F1",
    "F2",
    "F3",
    "F4",
```

### Changing keycap profiles

To change keycap profiles, you need a few things.
(Please note that in the `profiles/kat/` folder everything is supplied for KAT-profiles keycaps.

If a profile you want isn’t in the repo, you’ll need two things:

1. A folder containing one `obj` file for each keycap width and row combination, named as `row-width.obj`, e.g. the model `R5-1_0u.obj` would be used for a 100%-layout escape key. Note how the radix/decimal point in `1.0` is replaced with an underscore.
	- If a homing bump is present, the `-homing` suffix is added, for example `R2-1.0u-homing.obj`
	- Special keys have special names: `iso-enter.obj`, `num-plus.obj`, `num-enter.obj`, `stepped-caps.obj`
	- The only vertices present in each of these files belong to the keycap model it holds, and the bottom of the cap is parallel to the x-y plane.
	- If a uniform profile (e.g. KAM/DSA) is used, all keycap models should be considered to have profile `R2` (as this is the default `adjustkeys` uses).
2. A `yaml` file containing information on the location of the centre of a keycap as a fraction of a unit from the top left of the space it occupies (i.e. including margins)

Then to point `adjustkeys` to these through the relevant for keycap models and centres file.

### Using custom glyphs / fonts

To change the glyphs/images on top of the keycaps, you’ll firstly need a folder full of svgs (each containing exactly one image to be applied) and a mapping from the names of the keys in your layout to the name of the file (without the svg extension) which you wish to apply to that key.

An example folder of glyphs is seen in `glyphs/red-hat-display/` which contains an svg for each legend in some keycap set design which uses the [Red Hat Display][red-hat-display] font.
(As an aside, I chose Red Hat Display as an example font specifically for the reason that I _haven’t_ seen it on a keycap set before—given the freedom of dye-sublimation, I believe that designers should be able to respect the desires of the others, but, when the occasion permits, to surprise them.)

You’ll need to tell `adjustkeys` where in your layout you want each legend to be placed.
For this you need a mapping such as that in `examples/ansi-example-map.yml`, where some of the lines are below:

```yaml
'@-2': 2-at
'A': a
'Alt': alt
'B': b
'Backspace': backspace
'C': c
'Caps Lock': caps-lock
'Ctrl': ctrl
'D': d
'Delete': delete
'E': e
'End': end
```

Each line is like an instruction which tells `adjustkeys` that keycap named to the _left_ of the colon is to have the svg named to the _right_ of the colon applied to it.
The keycap names are derived from the [KLE][kle] input JSON; taken as either the text of the key or, if there is more than one symbol on it, the name of each from the top with new-lines `\n` replaced by dashes (such as `@-2` above).
The glyph names are just the final part of the svg path without the extension—for an svg in `C:/Users/kcza/Downloads/some-glyph.svg` can be referred to simply as `some-glyph` (assuming `adjustkeys` has been told to look for glyphs in `C:/Users/kcza/Downloads/` in the first place).
The lines don’t need to be alphabetical order; they are here just for cleanliness.

If you want, you can keep a guide to represent the keycap in the svg which you can have automatically removed when adjustment is performed (this is designed to help with the trial-and-error process of getting things the right size).
If a curve in your svg has the id `cap-guide` (by default, although the id to exclude can be different), then it will be automatically discarded when combining the svg data.

For the most logical results, ensure that the value provided to the ‘unit-length’ option is the same as the height and width of a 1u-size input svg.
(By default the unit length is 292, which is the same as the height of every svg in `glyphs/red-hat-display`.)

### Setting colours (via KLE or name-matching)

There are two ways of colouring keycaps and glyphs: either from raw [KLE][kle] input or from a colour map file.
The first way is always active and is just a matter of adjusting RGB colours through the website; the second way can be deactivated but is on by default.

A colour map file is a list of objects, each of which possibly specifies a keycap colour and/or a glyph style, the name to give the corresponding material in Blender, and a list of keycaps to apply it to.
The file is scanned from top to bottom, so if there are two places a keycap can be matched from, then only one nearest the top of the file will be used.
The `cap-colour` field is always a 6-digit hex number, available from any reputable colour picker.
The `glyph-style` field is a little more interesting—it can either be a 6-digit hex colour like `cap-colour`, _or,_ it can be a section of CSS code which is applied directly to the svg data.

Here’s an example of the first ten lines of the [example colour-map file](https://github.com/TheSignPainter98/adjust-keys/blob/master/examples/colour-map.yml) in the repo:

```yaml
- name: green
  cap-colour: '32a852'
  glyph-style: 'fill:#ad1aad;'
  keys:
  - .-.+
  - '[^+/*-]'
  - ''
  - F[1-49][0-2]?
- name: purple
  cap-colour: 'ad1aad'
```

Note firstly the indentation and how it discerns the list of objects (each containing a `name`, `colour` and `keys` field) from the `keys` list stored inside each.

Secondly, note the quote marks—these are used to force the yaml parser to consider what’s inside them as a string of letters as otherwise, the hex code `001100` would be considered a number and have the preceding zeros stripped away (leaving `1100`, which isn’t good).

Finally, observe how you can also use [Python regular expressions][regex-help] to specify keycap names in more general terms.
If you aren’t too comfortable using regular expressions, `adjustkeys` takes a list of keys, so you can more simply copy the names of the keycaps you wish to colour into the appropriate `keys` list, whilst being mindful of indentation and putting the `-` character at the start of each key-name as above.
These are little filters for patterns in text, for example on the final line of the above, the `.*` is as follows: `.` means match any _single_ character (e.g. a-z), and `*` means match zero or more of the expression to the left, hence here means zero or more of ‘any character,’ so `.*` is just a concise way of telling `adjustkeys` to match _anything._
It’s not essential to know regular expressions, but a few basics can make things a little more streamlined.
The cheatsheet and playground on [regexr][regex-playground] may be helpful.

## Pitfalls

Although adjustkeys is designed to be reasonably lenient, there are a few places an unsuspecting user can be caught out, so here’s a few things to keep in mind.

### Missing keycap models due to incorrect key profile

If you’re finding that some keys are missing, it may be because adjustkeys is looking for keycap models of widths and heights which do not exist.
Make sure that the [KLE][kle] layout file is referencing the right profile (in JSON this is the `p` key).

### Deactivation colours

Currently, adjustkeys combines colour information from a KLE input and through a colour-map but as KLE does not have an explicit ‘default’ colouring mode which would indicate when to fall-back on the colour-map, there is no perfect way of deciding when to do so.
The heuristic used by adjustkeys is as follows:

- If a colour-map is enabled then:
	- If the keycap being parsed has a glyph colour of `#000000`, this is taken as an indication to fall back on the user’s colour-map rules
	- Otherwise the given glyph colour is specified as the intended colour
	- If the keycap being parsed has a cap colour of `#cccccc`, this is taken as an indication to fall back on the user’s colour-map rules
	- Otherwise the given cap colour is specified as the intended colour
- Otherwise, KLE colours are taken as an exact specification of the user’s desired colourway

Therefore, if the user wishes to use a colour of `#cccccc` for caps, or `#000000` for glyphs in their design, it may be better to tell adjustkeys not to use the colour-map file through the appropriate option.

## Building from Source

This section is only useful for contributors; if you want to use the script, looking at the [releases][releases] page and the [usage](#usage) section should suffice.

Assuming `git` is installed, then in a suitable directory, run the following from the command-line.
For an easier experience, install [`cython3`][cython] first—it’s used here as a static checker and can find some bugs without needing to explicitly run all code-paths.
It’s optional, if you don’t want to install it, just pass the `NO_CYTHON=y` option on the `make` line.

```bash
git clone https://github.com/TheSignPainter98/adjust-keys
cd adjust-keys
make
```

Non-essential parts of the process which require programs which might not easily be found on all platforms can be removed from the build process by defining the appropriate `NO_x` variable.
See [`Makefile`][makefile] for more information.

## Contributing

Contributions are welcome!
Please see the [contribution note,][contrib-note] abide by the [code of conduct][code-of-conduct] and the note following:

- To add glyphs for a font _x,_ please place the related `svg`s in `glyphs/x/`, relative to the project root (the `x` should be lower-case)
- To add keycap models and metadata for a profile _y,_
	1. Place the related `obj` files in `profiles/y/` relative to the project root (the `y` should be lower-case and spaces should be replaced by dashes)
	2. Measure the margin between the space occupied by the keycap and the model itself (see [1u keycap size example diagram][keycap-info]) and enter the value into `profiles/y/keycap_data.yml`
	3. (The annoying one) measure the location of the centre of the face of the keycap model and the uppermost and leftmost extremes of the keycap model and enter the values into `profiles/y/centres.csv`
- When adding code, please use include type-annotations—they make it much easier to interface with the Python code written before!

Above all, please abide by the licenses of the relevant works!
For example, the license for Gotham, a common type family in KAT and KAM sets, would prohibit it’s inclusion in this repo.
In particular, some licenses state that the format of the contained glyphs may not be changed.
For example, at the time of writing, the licence for Comic Sans MS would prohibit its use through adjustkeys... although one might argue this is a good thing as there are plenty of better families which do what Comic Sans tries to but better.

The [licensing section](#author-and-acknowledgements) section below should be updated to acknowledge the original source of the material.

## Gripes

I wrote this in Python for two reasons:

1. There exists a large, well-documented Python API for Blender
2. ~~So that anyone learning to program could have an example of some reasonably complicated code and some reasonably clean methods to deal with challenges~~ Python is a popular but bad programming language.

Some languages like C are beautifully simple, others like [Haskell][haskell] are beautifully complex, but alas Python is neither.
It’s type system (“duck typing”), it’s lack of native support for type annotations is bad, its import system caching when it can’t find packages is bad and that imported modules are allowed to have side-effects is bad.
Although Python isn’t the only language to suffer these ailments, it’s the only one I’ve seen which lies at the intersection of all these problems and is also popular.

## Author and Acknowledgements

This [code][github] was written by Ed Jones (Discord `@kcza#4691`).

Thanks to Swishy for user-testing in the early stages and for suggesting that `adjustkeys` would benefit from being a Blender extension.

All files written by contributors to this project are covered under the [GNU Lesser General Public License v3.0][lgpl3], **with the following exceptions:**

- KAT keycap models present in the repo were derived from a model kindly provided by [zFrontier][zfrontier] which was found on the [Keycap Designers’][keycap-designers-discord] Discord.
  If there are any artifacts not present in the originals, please blame AutoCAD’s `obj` conversion
- The typeface used in svgs the `glyphs/red-hat-display/` folder is [Red Hat Display][red-hat-display] which uses the [Open Font License][ofl]
- The keycap representation used in `glyphs/red-hat-display` is derived from a 2D model by Alex Lin of [zFrontier][zfrontier], which was also found on the [Keycap Designers’][keycap-designers-discord] Discord
- The layout `examples/layout.yml` is derived from the [ANSI 104][kle-ansi-104] layout example on [KLE.][kle]

Please ensure that credit is given where it is due.

[blender]: https://www.blender.org
[blender-path-guide]: https://docs.blender.org/manual/en/latest/advanced/command_line/launch/macos.html
[contrib-note]: https://github.com/TheSignPainter98/adjust-keys/blob/master/.github/CONTRIBUTING.md
[code-of-conduct]: https://github.com/TheSignPainter98/adjust-keys/blob/master/.github/CODE_OF_CONDUCT.md
[codium]: https://github.com/VSCodium/vscodium
[cython]: https://cython.org
[github]: https://www.github.com/TheSignPainter98/adjust-keys
[lgpl3]: https://choosealicense.com/licenses/lgpl-3.0/
[haskell]: https://wiki.haskell.org/Introduction
[keycap-designers-discord]: https://discord.gg/93WN2uF
[keycap-info]: https://matt3o.com/anatomy-of-a-keyboard/
[kle]: http://www.keyboard-layout-editor.com "Keyboard layout editor"
[kle-ansi-104]: https://github.com/ijprest/keyboard-layout-editor/blob/master/layouts.json
[makefile]: https://github.com/TheSignPainter98/adjust-keys/blob/master/Makefile
[ofl]: https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL
[pip]: https://pip.pypa.io/en/stable/
[python]: https://www.python.org
[red-hat-display]: https://fonts.google.com/specimen/Red+Hat+Display
[regex-help]: https://docs.python.org/3/howto/regex.html
[regex-playground]: https://regexr.com
[releases]: https://www.github.com/TheSignPainter98/adjust-keys/releases
[yaml-intro]: https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html
[zfrontier]: https://en.zfrontier.com

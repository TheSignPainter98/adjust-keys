# Adjustcaps and Adjustglyphs

![An example adjustcaps layout in blender](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/placed-caps.png)
![An example adjustglyphs layout in blender](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/menacing-glyphs.png)

This is a [python][python] script which generates layouts of glyphs and keycaps for (automatic) import into [Blender!][blender]
Gone will be the days of manually placing caps into the correct locations and spending hours fixing alignment problems of glyphs on individual keys—simply use the layout you want using the JSON output of the [KLE][kle] to guide the caps into the mathematically-correct location using the perfection of a computer.

This script can also be used to create a _single source of truth_ for glyph alignment on caps, so changes and fixes can be easily propagated.

Please note that for many of the steps below, default configuration files are provided (obtained through the zip on the [releases page][releases]).
Also, command-line options can be saved and automatically read from the file `(cap|glyph)-opts.yml` for later use.

## Usage

You’ll need an installation of [`python3`][python] and its package manager, [`pip3`][pip].

1. Go to the [releases page][releases], download and unzip the code where you’ll have your `.blend` file
2. Check everything is working, in a terminal `cd` into the directory above then run `python3 ./adjust(caps|glyphs) -h` (or for macOS &amp; Linux, `./adjust(caps|glyphs) -h` is equivalent and shorter)
	- If python complains of a missing module, install missing dependencies with `pip3 install -r pkgs.txt`
3. Adjust command-line arguments (where the `-h` is from step 2); adjust data files appropriately (see [custom setup](#custom-setup))
4. Run the code—replace `ARGS` with the command-line parameters from above and `adjust(caps|glyphs)` as appropriate in either of the following
	- Run direct from the command-line _with_ Blender by pasting `blender --python-expr "import bpy; import os.path; import sys; sys.path.append(os.path.join(os.path.basename(bpy.data.filepath), 'adjust(caps|glyphs)')); import adjust(caps|glyphs); adjust(caps|glyphs).main('ARGS')"`
	- Run from GUI _within_ Blender by opening a Python console and pasting `import bpy; import os.path; import sys; sys.path.append(os.path.join(os.path.basename(bpy.data.filepath), 'adjust(caps|glyphs)')); import adjust(caps|glyphs); adjust(caps|glyphs).main('ARGS')`
	- Run from the command-line _without_ blender as in step 2 before manually importing the file left on disk
5. _Wait_ (it takes me about 15 seconds on my laptop to place all keycaps for a TKL layout, glyph placement is faster.)
6. (Possibly shrink-wrap glyphs onto caps if required)
7. Enjoy free time

## Example

In the zip on the [releases page][releases], some example data files are present and generate the layouts in the images above.
Assuming the zip is in `Downloads`, to generate a standard exposé of keycap models, run the following, and be prepared to wait a little while—there’s a lot of data to process.

```bash
cd Downloads
unzip adjust-keycaps.zip
blender --python-expr "import bpy; import os.path; import sys; sys.path.append(os.path.join(os.path.basename(bpy.data.filepath), 'adjustcaps')); import adjustcaps; adjustcaps.main('-v3') sys.path.append(os.path.join(os.path.basename(bpy.data.filepath), 'adjustglyphs')); import adjustglyphs; adjustglyphs.main('-v3')"
```

**Notice how the gray construction lines around the glyph are automatically removed!**
This is because they have the id `cap-guide` in the `svg`, which is detected and discarded by `adjustglyphs`.
As such, you can keep a guide to help with the glyph alignment without affecting the output layout.

## Custom Setup

Although they share some code, `adjustcaps` and `adjustglyphs` operate independently.
They are setup as below.

### Setting up `adjustcaps`

This script takes input of:

- A directory containing `.obj` files each with an individual keycap in an arbitrary location (_but consistent orientation_), named as `profile-size.obj` (e.g. `r1-1_0u.obj`)
- A `yaml` (or equivalently `json`) file containing the layout exported from [KLE][kle]
- A `yaml` file which lists the profiles of each row in order top to bottom

If called from blender, the arranged keycaps are imported, otherwise, the generated `.obj` files (one for each cap) are left on disk.

It’s important to note that _no other vertices should be present in the object files!_
Some cleaned KAT profile models are provided, but for other models, please make sure that only the vertices of the keycap are present in the file as otherwise this can mess up alignment when the script translates models to be adjacent to the origin.

### Setting up `adjustglyphs`

This is a little more complicated, but the results should speak for themselves.

This script takes input of:

- A folder containing the glyphs to be placed, each in a separate `.svg` file
- A `yaml` file which specifies the location of the centre of a key in a particular profile
- A `yaml` (or equivalently `json`) file containing the layout exported from [KLE][kle]
- A `yaml` file which specifies a mapping from key names to glyph names

If called from blender, the arranged glyphs are imported, otherwise, the generated `.svg` file is left on disk.

For the best results, all `.svg` files should be of an identical height and width which is then specified as the `--unit-length` parameter.

## Building from Source

This section is only useful for contributors; if you want to use the script, see the [releases][releases] page and the [usage](#usage) section above.

Assuming `git` is installed, then in a suitable directory, run the following from the command-line.
For an easier experience, install [`cython3`][cython] first—it’s used here as a static checker and can find some bugs without needing to explicitly run all code-paths.
It’s optional, if you don’t want to install it, just pass the `NO_CYTHON=y` option on the `make` line.

```bash
git clone https://github.com/TheSignPainter98/adjust-keys
cd adjust-keys
make
```

## Gripes

I wrote this in Python so that anyone learning to program could have an example of some reasonably complicated code and some reasonably clean methods to deal with challenges.
Of course, using Python was an absolutely terrible idea due to it’s basically useless type system and its failure to report errors ahead of time which made development a pain as usual.
[Haskell][haskell] would have been a _far_ better option for my sanity.
Everyone has their regrets, eh?

## Author and Acknowledgements

This [code][github] was written by Ed Jones (Discord `@kcza#4691`).
I’m not particularly proud of it, but it gets the job done.

KAT keycap models present in the repo were derived from a model kindly provided by [zFrontier][zfrontier] which I found on the [Keycap Designers’][keycap-designers-discord] Discord.

[blender]: https://www.blender.org
[cython]: https://cython.org
[github]: https://www.github.com/TheSignPainter98/adjust-keys
[haskell]: https://wiki.haskell.org/Introduction
[keycap-designers-discord]: https://discord.gg/93WN2uF
[kle]: http://www.keyboard-layout-editor.com "keyboard layout editor"
[pip]: https://pip.pypa.io/en/stable/
[python]: https://www.python.org
[releases]: https://www.github.com/TheSignPainter98/adjust-keys/releases
[zfrontier]: https://en.zfrontier.com

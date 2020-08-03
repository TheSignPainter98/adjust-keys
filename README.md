# Adjustkeys

![An example adjustcaps layout in blender](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/menacing-60.png)
![An example adjustglyphs layout in blender](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/menacing-layout.png)

This is a [python][python] script which generates layouts of keycaps and glyphs for (automatic) import into [Blender!][blender]
Gone will be the days of manually placing caps into the correct locations and spending hours fixing alignment problems of glyphs on individual keys—simply specify the layout you want using the JSON output of [KLE][kle] to have the computer guide the caps into the mathematically-correct locations.

This script can be used to create a _single source of truth_ for glyph alignment on caps, so later changes and fixes can be more easily propagated.

Please note that for many of the steps below, default configuration files are provided (obtained through the zip on the [releases page][releases]).
Also, command-line options can be saved and automatically read from the file `opts.yml` for later use.

## Why Bother?

Alignment is important.
Whereas good alignment can lend your set a kind of refined perfection, bad alignment can unnecessarily draw the eye and distract from the rest of your hard work.
The only problem is that to perfect alignment requires a non-negligable amount of effort to be spent on each key—it’s not as simple as just putting the glyph in the centre by how the computer sees it:

![An explanation for why computers aren’t natively good at aligning characters](https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/img/alignment-reasoning.png)

Without an in-depth study into emulation of the human eye, the best way to align glyphs is to use your own, but to do this for each time a glyph and keycap appears in every layout/kit would be extremely time-consuming, especially if one were to find something later which would require fixing very early-on in the process.
Therefore, `adjustkeys` exists—to help banish the duplication of tedious alignment work from the task of preparing renders for ICs and GBs, allowing its’ users to focus on the more fun bits of rendering, like watching your set come to life.

## Usage

You’ll need a working installation of [`python3`][python] and its package manager, [`pip3`][pip].

1. Go to the [releases page][releases], download and unzip the code so the `adjustkeys` binary is next to where you’ll have your `.blend` file
2. Check everything is working—in a terminal, `cd` into the directory above then run `python3 ./adjustkeys -h` (or for macOS &amp; Linux, `./adjustkeys -h` is both equivalent and shorter)
	- If python complains of a missing module, install missing dependencies by calling `pip3 install -r requirements.txt`
3. Configure the command-line arguments (see output with `-h` from step 2) and adjust data files appropriately (see [custom setup](#custom-setup))
4. Run the code—replace `ARGS` with what you found in step 3 in one of the following methods of running the script:
	- Run direct from the command-line _with_ Blender by pasting `blender --python-expr "import bpy; import os.path; import sys; sys.path.append(os.path.join(os.path.basename(bpy.data.filepath), 'adjustkeys')); import adjustkeys; adjustkeys.main('ARGS')"`
	- Run from GUI _within_ Blender by opening a Python console and pasting `import bpy; import os.path; import sys; sys.path.append(os.path.join(os.path.basename(bpy.data.filepath), 'adjustkeys')); import adjustkeys; adjustkeys.main('ARGS')`
	- Run from the command-line _without_ blender as in step 2 before manually importing the files left on disk
5. _Wait_ (it takes me about 15 seconds on my laptop to place all keycaps for a complete layout)
6. Enjoy free time

## Example

In the zip on the [releases page][releases], some example data files are present and generate the layouts in the images above.
Assuming the zip is in `Downloads`, to generate a standard exposé of keycap models, run the following, and be prepared to wait a little while—there’s a lot of data to process.

```bash
cd Downloads
unzip adjust-keycaps.zip
blender --python-expr "import bpy; import os.path; import sys; sys.path.append(os.path.join(os.path.basename(bpy.data.filepath), 'adjustcaps')); import adjustcaps; adjustcaps.main('-v3')"
```

Perhaps while it’s running, take a look at the [`./examples/menacing.svg`][menacing] file which will appear in the output.
Notice how the gray construction lines around the glyph are automatically removed!
This is because they have the id `cap-guide` in the `svg`, which is automatically detected and discarded by `adjustcaps`.
As such, you can keep a guide to help with the glyph alignment without affecting the output.

## Custom Setup

This script takes input of:

- A directory containing `.obj` files each with an individual keycap in an arbitrary location (_but consistent orientation_), named as `profile-size.obj` (e.g. `r1-1_0u.obj`)
- A `yaml` (or equivalently `json`) file containing the layout exported from [KLE][kle]
- A `yaml` file which lists the profiles of each row in order top to bottom
- A folder containing the glyphs to be placed, each in a separate `.svg` file
- A `yaml` file which specifies the location of the centre of a key in a particular profile
- A `yaml` (or equivalently `json`) file containing the layout exported from [KLE][kle]
- A `yaml` file which specifies a mapping from key names to glyph names

If called from blender, the arranged keycaps are imported, otherwise, the generated `.svg` and `.obj` files (one for each cap) are left on disk.

It’s important to note that _no other vertices should be present in the object files!_
Some cleaned KAT profile models are provided, but for other models, please make sure that only the vertices of the keycap are present in the file as otherwise this can mess up alignment when the script translates models to be adjacent to the origin.

Although non-essential, results may be improved by ensuring that all input `.svg` files are be of an identical height and width which is then specified as the `--unit-length` parameter.

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

- To add glyphs for a font _x,_ please place the related `svg`s in `./glyphs/x/`, relative to the project root
- To add keycap models for a profile _y,_
	1. Place the related `obj` files in `./profiles/y/` relative to the project root
	2. List the order of row profiles in a file `./profiles/y/layout_row_profiles.yml`
	3. (The annoying one) Compute the centres of the faces of the each keycap in units relative to the top left corner of the area occupied by the keycap, see [standard 1u keycap size diagram][keycap-info] for reference, and place the result in `./profiles/y/centres.yml`
- When adding code, please use include type-annotations—they make it much easier to interface with the Python code you’ve written!

Above all, please abide by the licenses of the relevant works!
For example, the license for Gotham, a de-facto standard type family for KAT and KAM sets, would prohibit it’s inclusion in this repo.

The [licensing section](#author-and-acknowledgements) section below should be updated to acknowledge the original source of the material.

## Gripes

I wrote this in Python for two reasons:

1. There exists a large, well-documented Python API for Blender
2. So that anyone learning to program could have an example of some reasonably complicated code and some reasonably clean methods to deal with challenges

Of course, using Python was really annoying due to it’s basically useless type system and its failure to report errors ahead of time which made development a pain as usual.
My sanity would have been better-off had I instead done this in [Haskell][haskell], but I guess everyone has their regrets, eh?

## Author and Acknowledgements

This [code][github] was written by Ed Jones (Discord `@kcza#4691`).
All files written by contributors to this project are covered under the [GNU Lesser General Public License v3.0][lgpl3], **with the following exceptions:**

- KAT keycap models present in the repo were derived from a model kindly provided by [zFrontier][zfrontier] which was found on the [Keycap Designers’][keycap-designers-discord] Discord
  If there are any artifacts not present in the originals, please blame AutoCAD’s `obj` conversion
- The typeface used in `examples/menacing.svg` is [Noto Serif JP][noto-serif-jp] which uses the [Open Font License][ofl]
- The keycap representation used in `examples/menacing.svg` is derived from a 2D model by Alex Lin of [zFrontier][zfrontier], which was also found on the [Keycap Designers’][keycap-designers-discord] Discord
- The example layouts, `examples/layout.yml` is derived from the [ANSI 104][kle-ansi-104] layout example on [KLE][kle]

Please ensure that credit is given where it is due.

[blender]: https://www.blender.org
[contrib-note]: https://github.com/TheSignPainter98/adjust-keys/blob/master/.github/CONTRIBUTING.md
[code-of-conduct]: https://github.com/TheSignPainter98/adjust-keys/blob/master/.github/CODE_OF_CONDUCT.md
[cython]: https://cython.org
[github]: https://www.github.com/TheSignPainter98/adjust-keys
[lgpl3]: https://choosealicense.com/licenses/lgpl-3.0/
[haskell]: https://wiki.haskell.org/Introduction
[keycap-designers-discord]: https://discord.gg/93WN2uF
[keycap-info]: https://matt3o.com/anatomy-of-a-keyboard/
[kle]: http://www.keyboard-layout-editor.com "Keyboard layout editor"
[kle-ansi-104]: https://github.com/ijprest/keyboard-layout-editor/blob/master/layouts.json
[makefile]: https://github.com/TheSignPainter98/adjust-keys/blob/master/Makefile
[menacing]: https://raw.githubusercontent.com/TheSignPainter98/adjust-keys/master/examples/menacing.svg
[noto-serif-jp]: https://fonts.google.com/specimen/Noto+Serif+JP
[ofl]: https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL
[pip]: https://pip.pypa.io/en/stable/
[python]: https://www.python.org
[releases]: https://www.github.com/TheSignPainter98/adjust-keys/releases
[zfrontier]: https://en.zfrontier.com

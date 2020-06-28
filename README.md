# AdjustKeys

A python script to provide a single source of truth for glyph alignment over arbitrary profiles and layouts.
Takes input of:

- A `yaml` file which specifies the location of the centre of a key in a particular profile
- A `yaml` file which specifies the offset from the centre of an arbitrary key of a particular glyph
- A `yaml` file which specifies a layout to use (this can be taken directly from KLE!)
- A `yaml` file which specifies a mapping from key names to glyph names
- Command-line arguments (which can be given in a `yaml` file) which detail the length of a single unit, the distance between consecutive rows without extra padding (such as a 0.5u space between the top two rows), and the margin between consecutive keycaps on the same row where extra padding is omitted

Outputs the locations where the centres of glyphs should be placed for optimal alignment.
This will eventually be extended to be represented as a single `svg` which can then be shrink-wrapped onto keycap models.

I wrote this in Python so that anyone learning to code could have an example of some reasonably complicated code and some reasonably clean methods to deal with this.
Of course, using Python was an absolutely terrible idea due to it's basically useless type system and its failure to report errors ahead of time which made development a pain as usual.
Haskell would have been a _far_ better option.
Everyone has their regrets, eh?

## How to obtain &amp; use

Assuming `git` is installed, you can build the code with the following commands.

```bash
git clone https://github.com/TheSignPainter98/adjust-keys
cd adjust-keys
make # Optional
```

I've only tested this on Linux, so the build system might require the installation of a few dependencies.
The binaries produced should be cross-platform---they're just zips of Python scripts.

The last step is optional and only used to obtain single binaries which are a little easier to distribute.
If you have run it, to test the binary you can replace `python3 ./glyphinf_main.py` with `./glyphinf` and `python3 ./adjustkeys_main.py` with `./adjustkeys` in the following commands.

Once you're in the `adjust-keys` directory, you can obtain positioning information about your glyphs by calling `glyphinf` on them.

```bash
python3 ./glyphinf_main.py /path/to/glyphs/*.svg > glyphs.yml
```

The `> glyphs.yml` just copies the output of the script into the `glyphs.yml` file for later use.
To see what goes in there, just omit that last part and the script will print its output to the console.

To obtain a single `svg` image which positions your glyphs onto a given keycap layout of a given profile (with some appropriate parameters), call:

```bash
python3 ./adjustkeys_main.py -u unit_length -x x-margin-between-caps -y same-for-y -P profile_file.yml -G glyphs.yml -L layout_file.yml -Q profile_rows.yml -M glyph_map_file.yml
```
A subset of the above options should be sufficient---each of the above has a default value so you can clean things up a little by making use of those.

Further usage information about usage can be found using

```bash
python3 ./adjustkeys_main.py -h
python3 ./glyphinf_main.py -h
```

I don't plan to release this on any package managers---unless requested.

# AdjustKeys

A python script to provide a single source of truth for glyph alignment over arbitrary profiles and layouts.
Takes input of:

- A folder containing a bunch of `svg`s where each file contains a single centred glyph
- A `yaml` file which specifies the location of the centre of a key in a particular profile
- A `yaml` file which specifies a layout to use (this can be taken directly from KLE!)
- A `yaml` file which specifies a mapping from key names to glyph names
- Command-line arguments (which can be given in a `yaml` file) which detail the length of a single unit, the distance between consecutive rows without extra padding (such as a 0.5u space between the top two rows), and the margin between consecutive keycaps on the same row where extra padding is omitted

The script then outputs an `svg` containing all the glyphs centred in each key in the layout according to the mapping used.

I wrote this in Python so that anyone learning to code could have an example of some reasonably complicated code and some reasonably clean methods to deal with this.
Of course, using Python was an absolutely terrible idea due to it's basically useless type system and its failure to report errors ahead of time which made development a pain as usual.
Haskell would have been a _far_ better option.
Everyone has their regrets, eh?

## How to obtain &amp; use

Assuming `git` is installed, you can build the code with the following commands.

```bash
git clone https://github.com/TheSignPainter98/adjust-keys
cd adjust-keys
make # (This step is optional to lint and collect into a single binary, so don't worry if it doesn't work, see below)
```

To run generate a laid-out `svg` of the glyphs present in the current folder, use:

```bash
python3 ./adjustkeys_main.py
```

For example, `python3 ./adjustkeys_main.py -G /path/to/glyph/dir/ -o glyphs.svg`

Find usage information with:

```bash
python3 ./adjustkeys_main.py -h
```

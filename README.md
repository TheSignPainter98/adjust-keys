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

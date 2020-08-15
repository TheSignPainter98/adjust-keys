# Copyright (C) Edward Jones

class AdjustKeysException(Exception):
    pass

class AdjustGlyphsException(AdjustKeysException):
    pass

class AdjustCapsException(AdjustKeysException):
    pass

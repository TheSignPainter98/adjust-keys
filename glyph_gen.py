from freetype import Face, FT_Vector
from svgpathtools import wsvg, CubicBezier, Line, QuadraticBezier, Path

def gen_svg(text:str, opath:str) -> str:
    face:Face = Face('ftemp/static/PlayfairDisplay-ExtraBoldItalic.ttf')
    char_size:float = 48 * 64
    face.set_char_size(char_size)
    prevChar:str = None
    off:complex = 0 + 0j
    paths:[Path] = []
    face.load_char(text[0])
    for char in text:
        face.load_char(char)
        outline = face.glyph.outline
        outline_points = [(p[0], char_size - p[1]) for p in outline.points]
        start:int = 0
        end:int = 0
        for i in range(len(outline.contours)):
            end = outline.contours[i]
            points:[Point] = outline_points[start:end + 1] + [outline_points[start]]
            tags:[Tag] = outline.tags[start:end + 1] + [outline.tags[start]]
            segments:[[Point]] = [[points[0]]]
            for j in range(1, len(points)):
                segments[-1] += [points[j]]
                if tags[j] and j < (len(points) - 1):
                    segments += [[points[j]]]
            segments = list(map(lambda segment: list(map(tuple_to_complex, segment)), segments))
            segments = list(map(lambda segment: list(map(lambda p: p + off, segment)), segments))
            for segment in segments:
                if len(segment) == 2:
                    paths.append(Line(start=segment[0], end=segment[1]))
                elif len(segment) == 3:
                    paths.append(QuadraticBezier(start=segment[0], control=segment[1], end=segment[2]))
                elif len(segment) == 4:
                    paths.append(CubicBezier(start=segment[0], control1=segment[1], control2=segment[2], end=segment[3]))
            start = end + 1
        off += face.glyph.metrics.horiAdvance + (vector_to_complex(face.get_kerning(char, prevChar)) if prevChar is not None else 0)
        prevChar = char
    path = Path(*paths)
    wsvg(path, filename=opath)

def tuple_to_complex(t:tuple) -> complex:
    return t[0] + t[1] * 1j

def vector_to_complex(t:FT_Vector) -> complex:
    return t.x + t.y * 1j

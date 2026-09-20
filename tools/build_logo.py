"""Localize the Japanese subtitle while retaining the Japanese English logo."""
import numpy as np
from PIL import Image
import paths


def localize_logo(original):
    assert original.shape == (184, 568, 4), original.shape
    subtitle = Image.open(paths.TOOLS / 'assets' / 'title_subtitle_ko.png').convert('RGBA')
    # Ignore nearly transparent generation noise when measuring visible padding.
    bounds = subtitle.getchannel('A').point(lambda a: 255 if a > 16 else 0).getbbox()
    assert bounds is not None, 'Empty Korean subtitle asset'
    subtitle = subtitle.crop(bounds)
    height = 37
    width = round(subtitle.width * height / subtitle.height)
    assert width <= 474, 'Subtitle is too wide'
    subtitle = subtitle.resize((width, height), Image.Resampling.LANCZOS)
    result = original.copy()
    # Japanese reading line. The English lettering above row 145 is untouched.
    result[145:184, 38:512] = 0
    canvas = Image.fromarray(result)
    canvas.alpha_composite(subtitle, ((568 - width) // 2, 147))
    return np.array(canvas)

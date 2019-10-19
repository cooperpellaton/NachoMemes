# pylint: skip-file

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from sys import maxsize
from typing import IO, Callable, Iterable, List, Optional
from urllib.request import Request, urlopen

from dacite import Config
from PIL import Image, ImageFont

# Monkeypatch Request to show the url in repr
Request.__repr__ = lambda self: f"Request(<{self.full_url}>)"


class TemplateError(Exception):
    pass


class Color(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


class Justify(Enum):
    """Horizontal text position; lambda function calculates left offset from
    enclosing box"""

    LEFT = (lambda w1, w2: 0,)
    CENTER = (lambda w1, w2: (w1 - w2) // 2,)
    RIGHT = (lambda w1, w2: w1 - w2,)

    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)


class Font(Enum):
    IMPACT = Path("fonts/impact.ttf")
    XKCD = Path("fonts/xkcd-script.ttf")
    COMIC_SANS = Path("fonts/comic.ttf")

    def load(self, font_size: int) -> ImageFont:
        return ImageFont.truetype(str(self.value), font_size)


@dataclass
class TextBox:
    """ Definition for text that will be placed in a template."""

    # left, right, top and bottom are offsets from the top left corner as a
    # percentage of the target image
    left: float
    right: float
    top: float
    bottom: float

    face: Font

    # in pixels
    max_font_size: Optional[int]

    color: Color = Color.BLACK
    outline: Optional[Color] = None

    # text alignment
    justify: Justify = Justify.CENTER

    # in degrees
    rotation: Optional[int] = 0

    # if this textbox is sized independently of the other boxes
    ind_size: Optional[bool] = False


@dataclass
class MemeTemplate:
    """Anatomy of a Meme"""

    name: str

    # URL to load the image
    source_image_url: Request

    # Where to put the text
    textboxes: List[TextBox]

    # name of the layout
    layout: str
    description: str
    docs: str

    # times used
    usage: int

    def read_source_image(self, buffer) -> Image:
        with urlopen(self.source_image_url) as s:
            buffer.write(s.read())
            buffer.flush
            buffer.seek(0)
            return Image.open(buffer)

    def render(self, message: Iterable[str], output: IO):
        from render import render_template

        render_template(self, message, output)


# additional deserializers for dacite
da_config = Config(
    {
        Font: Font.__getitem__,
        Color: Color.__getitem__,
        Justify: Justify.__getitem__,
        Request: Request,
        float: float,
        int: int,
    }
)


class Store(ABC):
    @abstractmethod
    def refresh_memes(self, guild: str, hard: bool = False) -> str:
        pass

    @abstractmethod
    def read_meme(
        self, guild: str, id: str, increment_use: bool = False
    ) -> MemeTemplate:
        pass

    @abstractmethod
    def list_memes(self, guild: str, fields: List[str] = None) -> Iterable[dict]:
        pass

    @abstractmethod
    def guild_config(self, guild: str) -> dict:
        pass
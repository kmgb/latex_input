from dataclasses import dataclass
from enum import IntFlag, auto


class FontVariantType(IntFlag):
    BOLD = auto()
    DOUBLE_STRUCK = auto()
    FRAKTUR = auto()
    ITALIC = auto()
    MATHEMATICAL = auto()
    MONOSPACE = auto()
    SANS_SERIF = auto()
    SCRIPT = auto()


@dataclass
class CharacterFontVariant:
    text: str
    kind: FontVariantType

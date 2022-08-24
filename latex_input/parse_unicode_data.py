from dataclasses import dataclass
import typing


@dataclass
class CharacterFontVariant:
    text: str
    is_bold: bool
    is_double_struck: bool
    is_fraktur: bool
    is_italic: bool
    is_mathematical: bool
    is_monospace: bool
    is_sans_serif: bool
    is_script: bool


subscript_mapping = dict[str, str]()
superscript_mapping = dict[str, str]()

character_font_variants = dict[str, list[CharacterFontVariant]]()


with open("./UnicodeData.txt", encoding="utf-8") as f:
    for line in f:
        fields = line.split(";")
        assert len(fields) == 15

        codepoint = fields[0]
        name = fields[1]
        decomposition = fields[5]

        char = chr(int(codepoint, 16))

        if decomposition:
            # Help out mypy with redefinitions
            map_type: typing.Any
            basechars: typing.Any

            # print(f"{name} has decomposition {decomposition}")
            *map_type, basechars = decomposition.split(maxsplit=1)

            # We aren't looking for 2 -> 1 mappings, skip any that decompose to
            # multiple characters.
            basechars = basechars.split()
            if len(basechars) > 1:
                continue

            basechar = chr(int(basechars[0], 16))

            assert len(map_type) < 2
            map_type = "".join(map_type)

            if map_type == "<super>":
                # Intentionally overwrite if there's multiple
                # Later unicode values tend to work look more consistent with one another
                superscript_mapping[basechar] = char

            elif map_type == "<sub>":
                # Intentionally overwrite if there's multiple
                subscript_mapping[basechar] = char

            elif map_type == "<font>":
                variant = CharacterFontVariant(
                    char,
                    is_mathematical="MATHEMATICAL" in name,
                    is_bold="BOLD" in name,
                    is_double_struck="DOUBLE-STRUCK" in name,
                    is_fraktur=any(x in name for x in ["FRAKTUR", "BLACK-LETTER"]),
                    is_italic="ITALIC" in name,
                    is_monospace="MONOSPACE" in name,
                    is_sans_serif="SANS-SERIF" in name,
                    is_script="SCRIPT" in name,
                )

                character_font_variants.setdefault(basechar, []).append(variant)

if __name__ == "__main__":
    print(str(character_font_variants).encode("utf-8"))

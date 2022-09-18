import typing

from unicode_structs import CharacterFontVariant, FontVariantType


def main():
    subscript_mapping = dict[str, str]()
    superscript_mapping = dict[str, str]()
    character_font_variants = dict[str, list[CharacterFontVariant]]()

    read_datafile(subscript_mapping, superscript_mapping, character_font_variants)

    print(str(subscript_mapping).encode("utf-8"))
    print("\n\n")
    print(str(superscript_mapping).encode("utf-8"))
    print("\n\n")
    print(str(character_font_variants).encode("utf-8"))


def read_datafile(subscript_mapping, superscript_mapping, character_font_variants):
    # TODO: Fix finding superscript alpha, iota, epsilon
    # Their fallbacks are listed as the "Latin" variants, meaning they aren't found
    # when looking for ^{\alpha} as it looks for the Greek variants
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
                    # Later unicode values tend to look more consistent with one another
                    superscript_mapping[basechar] = char

                elif map_type == "<sub>":
                    # Intentionally overwrite if there's multiple
                    subscript_mapping[basechar] = char

                elif map_type == "<font>":
                    variant = CharacterFontVariant(
                        char,
                        FontVariantType.MATHEMATICAL * ("MATHEMATICAL" in name)
                        | FontVariantType.BOLD * ("BOLD" in name)
                        | FontVariantType.DOUBLE_STRUCK * ("DOUBLE-STRUCK" in name)
                        | FontVariantType.FRAKTUR * (any(x in name for x in ["FRAKTUR", "BLACK-LETTER"]))
                        | FontVariantType.ITALIC * ("ITALIC" in name)
                        | FontVariantType.MONOSPACE * ("MONOSPACE" in name)
                        | FontVariantType.SANS_SERIF * ("SANS-SERIF" in name)
                        | FontVariantType.SCRIPT * ("SCRIPT" in name)
                    )

                    character_font_variants.setdefault(basechar, []).append(variant)


if __name__ == "__main__":
    main()

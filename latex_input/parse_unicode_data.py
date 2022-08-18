import typing

mathbb_mapping = dict[str, list[str]]()
mathcal_mapping = dict[str, list[str]]()
mathfrak_mapping = dict[str, list[str]]()
subscript_mapping = dict[str, list[str]]()
superscript_mapping = dict[str, list[str]]()

with open("./UnicodeData.txt") as f:
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
                superscript_mapping.setdefault(basechar, []).append(char)

            elif map_type == "<sub>":
                subscript_mapping.setdefault(basechar, []).append(char)

            # TODO: Add support for preferring one type (mathematical) over the other
            elif map_type == "<font>":
                # Skip italic and bold variants for now, maybe we can use them in the future
                if any(x in name for x in ["ITALIC", "BOLD"]):
                    continue

                if name.startswith(("DOUBLE-STRUCK ", "MATHEMATICAL DOUBLE-STRUCK ")):
                    mathbb_mapping.setdefault(basechar, []).append(char)

                elif name.startswith(("SCRIPT ", "MATHEMATICAL SCRIPT ")):
                    mathcal_mapping.setdefault(basechar, []).append(char)

                elif name.startswith(("MATHEMATICAL FRAKTUR ", "BLACK-LETTER ")):
                    mathfrak_mapping.setdefault(basechar, []).append(char)

from collections import defaultdict
import typing

# A -> 𝒜
mathbb_mapping = dict[str, str]()
mathcal_mapping = dict[str, str]()
mathfrak_mapping = dict[str, str]()
subscript_mapping = dict[str, str]()
superscript_mapping = dict[str, str]()

with open("./UnicodeData.txt") as f:
    # A -> [(𝒜, MATHEMATICAL SCRIPT CAPITAL A), ...]
    # Temporary mappings that store all found values
    mathbb_data = defaultdict[str, list[tuple[str, str]]](list)
    mathcal_data = defaultdict[str, list[tuple[str, str]]](list)
    mathfrak_data = defaultdict[str, list[tuple[str, str]]](list)

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

            # TODO: Add support for preferring one type (mathematical) over the other
            elif map_type == "<font>":
                # Skip italic and bold variants for now, maybe we can use them in the future
                if any(x in name for x in ["ITALIC", "BOLD"]):
                    continue

                if name.startswith(("DOUBLE-STRUCK ", "MATHEMATICAL DOUBLE-STRUCK ")):
                    mathbb_data[basechar].append((char, name))

                elif name.startswith(("SCRIPT ", "MATHEMATICAL SCRIPT ")):
                    mathcal_data[basechar].append((char, name))

                elif name.startswith(("MATHEMATICAL FRAKTUR ", "BLACK-LETTER ")):
                    mathfrak_data[basechar].append((char, name))

    # Find all mappings with multiple characters, and prefer the mathematical variant
    # for consistency. Generally, if there's more than one match for these sets, one is
    # guaranteed the mathematical variant.
    for intermediate, resultant in [
            (mathbb_data, mathbb_mapping),
            (mathcal_data, mathcal_mapping),
            (mathfrak_data, mathfrak_mapping)
    ]:

        for k, v in intermediate.items():
            value = ""

            if len(v) == 1:
                value = v[0][0]
            else:
                value = next(x[0] for x in v if x[1].startswith("MATHEMATICAL "))

            resultant[k] = value

superscript_mapping = dict[str, list[str]]()
subscript_mapping = dict[str, list[str]]()

with open("./UnicodeData.txt") as f:
    for line in f:
        fields = line.split(";")
        assert len(fields) == 15

        codepoint = fields[0]
        decomposition = fields[5]

        char = chr(int(codepoint, 16))

        if decomposition:
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
